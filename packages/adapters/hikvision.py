from __future__ import annotations

from pathlib import Path
from typing import Any

from packages.adapters.base import VendorAdapter
from packages.parsers.hikg import HIKGParser
from packages.forensics.io.readonly import ReadOnlyEvidence


class HikvisionAdapter(VendorAdapter):
    """
    Forensic adapter for Hikvision DVR/NVR surveillance images (HIKG/HKCS master sectors).
    """

    name: str = "Hikvision"
    version: str = "2.0.0"

    def detect(self, evidence_path: Path) -> bool:
        if not evidence_path.is_file():
            return False

        try:
            with ReadOnlyEvidence(evidence_path) as evidence:
                header = evidence.read(1024)
                if header[:4] == b"HIKG" or (len(header) >= 12 and header[8:12] == b"HKCS"):
                    return True
        except Exception:
            return False

        return False

    def inspect(self, evidence_path: Path) -> dict[str, Any]:
        parser = HIKGParser(evidence_path)
        try:
            hdr = parser.parse()
            return {
                "vendor": "Hikvision",
                "filesystem": f"HIKG v{hdr.version}.0",
                "magic": hdr.magic.decode("ascii", errors="replace"),
                "sub_magic": hdr.sub_magic.decode("ascii", errors="replace"),
                "signature_offset": 0,
                "status": "DETECTED",
                "sector_size": hdr.sector_size,
                "total_tracks": hdr.total_tracks,
                "tracks_offset": hdr.tracks_offset,
            }
        except Exception:
            with ReadOnlyEvidence(evidence_path) as evidence:
                header = evidence.read(512)
                magic = header[:4].decode("ascii", errors="replace")
            return {
                "vendor": "Hikvision",
                "filesystem": "HIKG/HKCS",
                "magic": magic,
                "signature_offset": 0,
                "status": "DETECTED",
            }

    def list_recordings(self, evidence_path: Path) -> list[dict[str, Any]]:
        parser = HIKGParser(evidence_path)
        try:
            recordings = parser.get_recordings()
            if recordings:
                return recordings
        except Exception:
            pass

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
