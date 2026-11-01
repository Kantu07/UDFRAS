from __future__ import annotations

import struct
from datetime import datetime, timezone
from pathlib import Path
import pytest

from packages.parsers.dhfs import DHFSParser, DHFSSuperblock, DHFSInode


@pytest.fixture
def dhfs_disk_image(tmp_path: Path) -> Path:
    disk = tmp_path / "dahua_test.img"
    data = bytearray(131072)

    data[0:4] = b"DHFS"
    data[4:8] = struct.pack("<I", 4)
    data[8:12] = struct.pack("<I", 512)
    data[12:16] = struct.pack("<I", 64)
    data[16:24] = struct.pack("<Q", 256)
    data[24:26] = struct.pack("<H", 8)
    data[26:34] = struct.pack("<Q", 4096)
    data[34:38] = struct.pack("<I", 2)

    inode1 = struct.pack("<HHIIQII", 1, 0x01, 1700000000, 1700000900, 64, 32, 16384) + (b"\x00" * 4)
    data[4096:4096 + 32] = inode1

    inode2 = struct.pack("<HHIIQII", 2, 0x80, 1700001000, 1700001600, 96, 16, 8192) + (b"\x00" * 4)
    data[4096 + 32:4096 + 64] = inode2

    disk.write_bytes(bytes(data))
    return disk


def test_dhfs_parser_superblock(dhfs_disk_image: Path):
    parser = DHFSParser(dhfs_disk_image)
    sb = parser.parse()

    assert isinstance(sb, DHFSSuperblock)
    assert sb.magic == b"DHFS"
    assert sb.version == 4
    assert sb.sector_size == 512
    assert sb.cluster_size == 64
    assert sb.total_sectors == 256
    assert sb.channel_count == 8
    assert sb.inodes_offset == 4096


def test_dhfs_parser_inodes(dhfs_disk_image: Path):
    parser = DHFSParser(dhfs_disk_image)
    parser.parse()

    assert len(parser.inodes) == 2

    in1 = parser.inodes[0]
    assert in1.channel == 1
    assert in1.is_deleted is False
    assert in1.start_sector == 64
    assert in1.sector_count == 32
    assert in1.length_bytes == 16384
    assert in1.start_time == datetime.fromtimestamp(1700000000, tz=timezone.utc)

    in2 = parser.inodes[1]
    assert in2.channel == 2
    assert in2.is_deleted is True
    assert in2.start_sector == 96
    assert in2.length_bytes == 8192


def test_dhfs_get_recordings(dhfs_disk_image: Path):
    parser = DHFSParser(dhfs_disk_image)
    recordings = parser.get_recordings()

    assert len(recordings) == 2
    assert recordings[0]["id"] == "REC-DH-CH01-0001"
    assert recordings[0]["camera"] == "CAM-01"
    assert recordings[0]["status"] == "normal"

    assert recordings[1]["id"] == "REC-DH-CH02-0002"
    assert recordings[1]["camera"] == "CAM-02"
    assert recordings[1]["status"] == "deleted"


def test_dhfs_invalid_magic_raises_error(tmp_path: Path):
    invalid = tmp_path / "not_dhfs.img"
    invalid.write_bytes(b"INVALID_HEADER_DATA_12345678")

    parser = DHFSParser(invalid)
    with pytest.raises(ValueError, match="missing 'DHFS' magic signature"):
        parser.parse()
