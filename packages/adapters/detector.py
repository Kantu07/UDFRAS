from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from packages.adapters.signatures import VENDOR_SIGNATURES, SignatureDefinition
from packages.forensics.io.readonly import ReadOnlyEvidence


@dataclass(frozen=True)
class VendorDetectionResult:
    vendor: str
    detected_family: str
    matched_signature: str | None
    signature_offset: int | None
    confidence: str
    is_supported: bool
    evidence_path: str


class VendorDetector:
    """
    Automated DVR/NVR vendor and model identification engine.
    
    Inspects low-level disk sector headers via strict read-only handles
    and compares magic bytes against known vendor specifications without
    altering source evidence bytes.
    """

    def __init__(self, signatures: List[SignatureDefinition] | None = None) -> None:
        self.signatures = signatures or VENDOR_SIGNATURES

    def detect(self, evidence_path: str | Path) -> VendorDetectionResult:
        path = Path(evidence_path)
        if not path.is_file():
            raise FileNotFoundError(f"Evidence file not found: {path}")

        with ReadOnlyEvidence(path) as evidence:
            # Read first 8192 bytes (first 16 standard sectors)
            header_sample = evidence.read(8192)

        # Check CP Plus OEM specific marker in header if DHFS matched
        is_cpplus_custom = b"CP PLUS" in header_sample or b"CPPLUS" in header_sample

        for sig in self.signatures:
            offset = sig.offset
            magic = sig.magic_bytes
            magic_len = len(magic)

            if len(header_sample) >= offset + magic_len:
                candidate = header_sample[offset : offset + magic_len]
                if candidate == magic:
                    if sig.vendor == "DAHUA" and is_cpplus_custom:
                        return VendorDetectionResult(
                            vendor="CP_PLUS",
                            detected_family="CP Plus (Dahua OEM Structure)",
                            matched_signature=magic.hex().upper(),
                            signature_offset=offset,
                            confidence="HIGH",
                            is_supported=True,
                            evidence_path=str(path),
                        )

                    return VendorDetectionResult(
                        vendor=sig.vendor,
                        detected_family=sig.family,
                        matched_signature=magic.hex().upper(),
                        signature_offset=offset,
                        confidence=sig.confidence_level,
                        is_supported=True,
                        evidence_path=str(path),
                    )

        # Fallback when no known signatures match
        return VendorDetectionResult(
            vendor="UNKNOWN",
            detected_family="Unrecognized / Non-Proprietary Format",
            matched_signature=None,
            signature_offset=None,
            confidence="UNRECOGNIZED",
            is_supported=False,
            evidence_path=str(path),
        )
