from __future__ import annotations

import struct
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional

from packages.forensics.io.readonly import ReadOnlyEvidence


@dataclass(frozen=True)
class HIKGTrack:
    track_id: int
    channel: int
    start_time: datetime
    end_time: datetime
    start_sector: int
    sector_count: int
    data_type: int

    @property
    def is_alarm(self) -> bool:
        return bool(self.data_type & 0x06)

    def to_dict(self) -> dict[str, Any]:
        return {
            "track_id": self.track_id,
            "channel": self.channel,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "start_sector": self.start_sector,
            "sector_count": self.sector_count,
            "data_type": self.data_type,
            "is_alarm": self.is_alarm,
        }


@dataclass(frozen=True)
class HIKGHeader:
    magic: bytes
    sub_magic: bytes
    version: int
    sector_size: int
    total_tracks: int
    tracks_offset: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "magic": self.magic.decode("ascii", errors="replace"),
            "sub_magic": self.sub_magic.decode("ascii", errors="replace"),
            "version": self.version,
            "sector_size": self.sector_size,
            "total_tracks": self.total_tracks,
            "tracks_offset": self.tracks_offset,
        }


class HIKGParser:
    HIKG_MAGIC = b"HIKG"
    HKCS_MAGIC = b"HKCS"

    def __init__(self, evidence_path: Path):
        self.evidence_path = Path(evidence_path)
        self.header: Optional[HIKGHeader] = None
        self.tracks: List[HIKGTrack] = []

    def parse(self) -> HIKGHeader:
        with ReadOnlyEvidence(self.evidence_path) as evidence:
            header_bytes = evidence.read(1024)

            if header_bytes[:4] != self.HIKG_MAGIC:
                raise ValueError(f"Invalid Hikvision evidence: missing 'HIKG' magic signature at {self.evidence_path}")

            magic = header_bytes[0:4]
            sub_magic = header_bytes[8:12] if len(header_bytes) >= 12 else b""
            version = struct.unpack("<I", header_bytes[4:8])[0] if len(header_bytes) >= 8 else 1
            sector_size = struct.unpack("<I", header_bytes[12:16])[0] if len(header_bytes) >= 16 and struct.unpack("<I", header_bytes[12:16])[0] > 0 else 512
            total_tracks = struct.unpack("<I", header_bytes[16:20])[0] if len(header_bytes) >= 20 else 0
            tracks_offset = struct.unpack("<Q", header_bytes[20:28])[0] if len(header_bytes) >= 28 and struct.unpack("<Q", header_bytes[20:28])[0] > 0 else 4096

            self.header = HIKGHeader(
                magic=magic,
                sub_magic=sub_magic,
                version=version,
                sector_size=sector_size,
                total_tracks=total_tracks,
                tracks_offset=tracks_offset,
            )

            self.tracks = self._parse_tracks(evidence)
            return self.header

    def _parse_tracks(self, evidence: ReadOnlyEvidence) -> List[HIKGTrack]:
        tracks: List[HIKGTrack] = []
        if not self.header or self.header.tracks_offset >= evidence.size_bytes:
            return tracks

        evidence.seek(self.header.tracks_offset)
        table_size = min(65536, evidence.size_bytes - self.header.tracks_offset)
        if table_size < 32:
            return tracks

        data = evidence.read(table_size)
        entry_size = 32

        for i in range(0, len(data) - entry_size + 1, entry_size):
            entry = data[i:i + entry_size]
            if entry == b"\x00" * entry_size or entry == b"\xff" * entry_size:
                continue

            # Standard 32-byte track record format:
            # <IIIIQII = 4 + 4 + 4 + 4 + 8 + 4 + 4 = 32 bytes
            track_id, channel, data_type, start_epoch, start_sec, sec_count, duration = struct.unpack(
                "<IIIIQII", entry
            )

            if channel == 0 or channel > 128 or start_epoch == 0:
                continue

            end_epoch = start_epoch + (duration if duration > 0 else 900)

            try:
                start_dt = datetime.fromtimestamp(start_epoch, tz=timezone.utc)
                end_dt = datetime.fromtimestamp(end_epoch, tz=timezone.utc)
            except (ValueError, OverflowError, OSError):
                continue

            track = HIKGTrack(
                track_id=track_id,
                channel=channel,
                start_time=start_dt,
                end_time=end_dt,
                start_sector=start_sec,
                sector_count=sec_count,
                data_type=data_type,
            )
            tracks.append(track)

        return tracks

    def get_recordings(self) -> List[dict[str, Any]]:
        if not self.header:
            self.parse()

        recordings = []
        for track in self.tracks:
            recordings.append({
                "id": f"REC-HIK-CH{track.channel:02d}-{track.track_id:04d}",
                "camera": f"CAM-{track.channel:02d}",
                "channel": track.channel,
                "start_time": track.start_time.isoformat(),
                "end_time": track.end_time.isoformat(),
                "start_sector": track.start_sector,
                "sector_count": track.sector_count,
                "status": "alarm" if track.is_alarm else "normal",
                "format": "H.264",
            })
        return recordings
