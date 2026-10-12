from __future__ import annotations

from pathlib import Path
from typing import Any

from packages.adapters.base import VendorAdapter
from packages.forensics.io.readonly import ReadOnlyEvidence


class GenericFallbackAdapter(VendorAdapter):
    """
    Fallback adapter for unrecognized or raw disk images.
    Reports strictly verified facts without fabricating false recordings.
    """

    name: str = "Generic / Unrecognized"
    version: str = "1.0.0"

    def detect(self, evidence_path: Path) -> bool:
        # Generic adapter accepts any valid file as fallback
        return evidence_path.is_file()

    def inspect(self, evidence_path: Path) -> dict[str, Any]:
        with ReadOnlyEvidence(evidence_path) as evidence:
            size = evidence.size_bytes

        return {
            "vendor": "Generic / Unrecognized",
            "filesystem": "Unknown Raw Storage",
            "size_bytes": size,
            "status": "UNRECOGNIZED",
        }

    def list_recordings(self, evidence_path: Path) -> list[dict[str, Any]]:
        # Does not fabricate false recordings
        return []
