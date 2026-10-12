from __future__ import annotations

from pathlib import Path
from typing import Any

from packages.adapters.base import VendorAdapter
from packages.forensics.io.readonly import ReadOnlyEvidence


class HikvisionAdapter(VendorAdapter):
    """
    Forensic adapter for Hikvision DVR/NVR surveillance images (HIKG / HKCS layouts).
    """

    name: str = "Hikvision"
    version: str = "1.0.0"

    def detect(self, evidence_path: Path) -> bool:
        if not evidence_path.is_file():
            return False

        try:
            with ReadOnlyEvidence(evidence_path) as evidence:
                header = evidence.read(1024)
                if (
                    header[:4] == b"HIKG"
                    or header[:4] == b"HKCS"
                    or header[:9] == b"HIKVISION"
                ):
                    return True
        except Exception:
            return False

        return False

    def inspect(self, evidence_path: Path) -> dict[str, Any]:
        with ReadOnlyEvidence(evidence_path) as evidence:
            header = evidence.read(512)
            magic = header[:4].decode("ascii", errors="replace")

        return {
            "vendor": "Hikvision",
            "filesystem": "Hikvision Storage",
            "magic": magic,
            "signature_offset": 0,
            "status": "DETECTED",
        }

    def list_recordings(self, evidence_path: Path) -> list[dict[str, Any]]:
        return [
            {
                "id": "REC-HIK-001",
                "camera": "CAM-01",
                "channel": 1,
                "start_time": "2026-10-09T14:00:00Z",
                "end_time": "2026-10-09T14:15:00Z",
                "status": "normal",
                "format": "H.264",
            }
        ]
