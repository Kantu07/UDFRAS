from __future__ import annotations

import struct
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional

from packages.forensics.io.readonly import ReadOnlyEvidence


@dataclass(frozen=True)
class DHFSInode:
    channel: int
    start_time: datetime
    end_time: datetime
    start_sector: int
    sector_count: int
    length_bytes: int
    flags: int

    @property
    def is_deleted(self) -> bool:
        return bool(self.flags & 0x80)

    @property
    def is_alarm(self) -> bool:
        return bool(self.flags & 0x02)

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel": self.channel,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "start_sector": self.start_sector,
            "sector_count": self.sector_count,
            "length_bytes": self.length_bytes,
            "flags": self.flags,
            "is_deleted": self.is_deleted,
            "is_alarm": self.is_alarm,
        }


@dataclass(frozen=True)
class DHFSSuperblock:
    magic: bytes
    version: int
    sector_size: int
    cluster_size: int
    total_sectors: int
    channel_count: int
    inodes_offset: int
    inodes_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "magic": self.magic.decode("ascii", errors="replace"),
            "version": self.version,
            "sector_size": self.sector_size,
            "cluster_size": self.cluster_size,
            "total_sectors": self.total_sectors,
            "channel_count": self.channel_count,
            "inodes_offset": self.inodes_offset,
            "inodes_count": self.inodes_count,
        }


class DHFSParser:
    SECTOR_SIZE_DEFAULT = 512
    DHFS_MAGIC = b"DHFS"

    def __init__(self, evidence_path: Path):
        self.evidence_path = Path(evidence_path)
        self.superblock: Optional[DHFSSuperblock] = None
        self.inodes: List[DHFSInode] = []

    def parse(self) -> DHFSSuperblock:
        with ReadOnlyEvidence(self.evidence_path) as evidence:
            header = evidence.read(1024)

            offset = 0
            if header[:4] != self.DHFS_MAGIC:
                if len(header) >= 516 and header[512:516] == self.DHFS_MAGIC:
                    offset = 512
                else:
                    raise ValueError(f"Invalid DHFS evidence: missing 'DHFS' magic signature at {self.evidence_path}")

            sb_bytes = header[offset:offset + 512]
            magic = sb_bytes[0:4]
            version = struct.unpack("<I", sb_bytes[4:8])[0] if len(sb_bytes) >= 8 else 4

            sector_size = struct.unpack("<I", sb_bytes[8:12])[0] if len(sb_bytes) >= 12 and struct.unpack("<I", sb_bytes[8:12])[0] > 0 else 512
            cluster_size = struct.unpack("<I", sb_bytes[12:16])[0] if len(sb_bytes) >= 16 and struct.unpack("<I", sb_bytes[12:16])[0] > 0 else 64
            total_sectors = struct.unpack("<Q", sb_bytes[16:24])[0] if len(sb_bytes) >= 24 and struct.unpack("<Q", sb_bytes[16:24])[0] > 0 else (evidence.size_bytes // sector_size)
            channel_count = struct.unpack("<H", sb_bytes[24:26])[0] if len(sb_bytes) >= 26 and struct.unpack("<H", sb_bytes[24:26])[0] > 0 else 16
            inodes_offset = struct.unpack("<Q", sb_bytes[26:34])[0] if len(sb_bytes) >= 34 and struct.unpack("<Q", sb_bytes[26:34])[0] > 0 else 4096
            inodes_count = struct.unpack("<I", sb_bytes[34:38])[0] if len(sb_bytes) >= 38 and struct.unpack("<I", sb_bytes[34:38])[0] > 0 else 0

            self.superblock = DHFSSuperblock(
                magic=magic,
                version=version,
                sector_size=sector_size,
                cluster_size=cluster_size,
                total_sectors=total_sectors,
                channel_count=channel_count,
                inodes_offset=inodes_offset,
                inodes_count=inodes_count,
            )

            self.inodes = self._parse_inodes(evidence)
            return self.superblock

    def _parse_inodes(self, evidence: ReadOnlyEvidence) -> List[DHFSInode]:
        inodes: List[DHFSInode] = []
        if not self.superblock or self.superblock.inodes_offset >= evidence.size_bytes:
            return inodes

        evidence.seek(self.superblock.inodes_offset)
        table_size = min(65536, evidence.size_bytes - self.superblock.inodes_offset)
        if table_size < 32:
            return inodes

        data = evidence.read(table_size)
        entry_size = 32

        for i in range(0, len(data) - entry_size + 1, entry_size):
            entry = data[i:i + entry_size]
            if entry == b"\x00" * entry_size or entry == b"\xff" * entry_size:
                continue

            channel, flags, start_epoch, end_epoch, start_sec, sec_count, length_bytes = struct.unpack(
                "<HHIIQII", entry[:28]
            )

            if channel == 0 or channel > 128 or start_epoch == 0:
                continue

            try:
                start_dt = datetime.fromtimestamp(start_epoch, tz=timezone.utc)
                end_dt = datetime.fromtimestamp(end_epoch, tz=timezone.utc)
            except (ValueError, OverflowError, OSError):
                continue

            inode = DHFSInode(
                channel=channel,
                start_time=start_dt,
                end_time=end_dt,
                start_sector=start_sec,
                sector_count=sec_count,
                length_bytes=length_bytes,
                flags=flags,
            )
            inodes.append(inode)

        return inodes

    def get_recordings(self) -> List[dict[str, Any]]:
        if not self.superblock:
            self.parse()

        recordings = []
        for idx, inode in enumerate(self.inodes, 1):
            status = "deleted" if inode.is_deleted else ("alarm" if inode.is_alarm else "normal")
            recordings.append({
                "id": f"REC-DH-CH{inode.channel:02d}-{idx:04d}",
                "camera": f"CAM-{inode.channel:02d}",
                "channel": inode.channel,
                "start_time": inode.start_time.isoformat(),
                "end_time": inode.end_time.isoformat(),
                "start_sector": inode.start_sector,
                "sector_count": inode.sector_count,
                "length_bytes": inode.length_bytes,
                "status": status,
                "format": "H.264",
            })
        return recordings
