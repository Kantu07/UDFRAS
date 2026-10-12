from __future__ import annotations

from pathlib import Path
from typing import Any

from packages.adapters.base import VendorAdapter
from packages.forensics.io.readonly import ReadOnlyEvidence


class DahuaAdapter(VendorAdapter):
    """
    Forensic adapter for Dahua DVR/NVR surveillance images (DHFS filesystem).
    """

    name: str = "Dahua"
    version: str = "1.0.0"

    def detect(self, evidence_path: Path) -> bool:
        if not evidence_path.is_file():
            return False

        try:
            with ReadOnlyEvidence(evidence_path) as evidence:
                header = evidence.read(1024)
                # Check sector 0 and sector 1 for DHFS magic bytes
                if header[:4] == b"DHFS" or (len(header) >= 516 and header[512:516] == b"DHFS"):
                    return True
        except Exception:
            return False

        return False

    def inspect(self, evidence_path: Path) -> dict[str, Any]:
        with ReadOnlyEvidence(evidence_path) as evidence:
            header = evidence.read(512)
            magic = header[:4].decode("ascii", errors="replace")

        return {
            "vendor": "Dahua",
            "filesystem": "DHFS 4.1",
            "magic": magic,
            "signature_offset": 0,
            "status": "DETECTED",
        }

    def list_recordings(self, evidence_path: Path) -> list[dict[str, Any]]:
        # Initial parser structure for Phase 1 / Phase 2
        return [
            {
                "id": "REC-DH-001",
                "camera": "CAM-01",
                "channel": 1,
                "start_time": "2026-10-09T14:00:00Z",
                "end_time": "2026-10-09T14:15:00Z",
                "status": "normal",
                "format": "H.264",
            }
        ]
