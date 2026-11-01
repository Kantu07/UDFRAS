from __future__ import annotations

import struct
from datetime import datetime, timezone
from pathlib import Path
import pytest

from packages.parsers.hikg import HIKGParser, HIKGHeader, HIKGTrack


@pytest.fixture
def hikg_disk_image(tmp_path: Path) -> Path:
    disk = tmp_path / "hikvision_test.img"
    data = bytearray(131072)

    # 1. Sector 0: Master Header
    data[0:4] = b"HIKG"
    data[4:8] = struct.pack("<I", 1)  # Version 1
    data[8:12] = b"HKCS"
    data[12:16] = struct.pack("<I", 512)  # Sector size
    data[16:20] = struct.pack("<I", 2)  # 2 tracks
    data[20:28] = struct.pack("<Q", 4096)  # Tracks offset: 4096

    # 2. Track Allocation Table at offset 4096
    # 32-byte layout: <IIIIQII = track_id, channel, data_type, start_epoch, start_sec, sec_count, duration
    # Track 1: ID 1, Channel 1, normal (0x01), time 1700000000, sector 64, count 32, duration 900
    track1 = struct.pack("<IIIIQII", 1, 1, 0x01, 1700000000, 64, 32, 900)
    data[4096:4096 + 32] = track1

    # Track 2: ID 2, Channel 2, motion alarm (0x02), time 1700001000, sector 96, count 16, duration 600
    track2 = struct.pack("<IIIIQII", 2, 2, 0x02, 1700001000, 96, 16, 600)
    data[4096 + 32:4096 + 64] = track2

    disk.write_bytes(bytes(data))
    return disk


def test_hikg_parser_header(hikg_disk_image: Path):
    parser = HIKGParser(hikg_disk_image)
    hdr = parser.parse()

    assert isinstance(hdr, HIKGHeader)
    assert hdr.magic == b"HIKG"
    assert hdr.sub_magic == b"HKCS"
    assert hdr.version == 1
    assert hdr.sector_size == 512
    assert hdr.total_tracks == 2
    assert hdr.tracks_offset == 4096


def test_hikg_parser_tracks(hikg_disk_image: Path):
    parser = HIKGParser(hikg_disk_image)
    parser.parse()

    assert len(parser.tracks) == 2

    t1 = parser.tracks[0]
    assert t1.track_id == 1
    assert t1.channel == 1
    assert t1.is_alarm is False
    assert t1.start_sector == 64
    assert t1.sector_count == 32
    assert t1.start_time == datetime.fromtimestamp(1700000000, tz=timezone.utc)

    t2 = parser.tracks[1]
    assert t2.track_id == 2
    assert t2.channel == 2
    assert t2.is_alarm is True
    assert t2.start_sector == 96
    assert t2.sector_count == 16


def test_hikg_get_recordings(hikg_disk_image: Path):
    parser = HIKGParser(hikg_disk_image)
    recordings = parser.get_recordings()

    assert len(recordings) == 2
    assert recordings[0]["id"] == "REC-HIK-CH01-0001"
    assert recordings[0]["camera"] == "CAM-01"
    assert recordings[0]["status"] == "normal"

    assert recordings[1]["id"] == "REC-HIK-CH02-0002"
    assert recordings[1]["camera"] == "CAM-02"
    assert recordings[1]["status"] == "alarm"


def test_hikg_invalid_magic_raises_error(tmp_path: Path):
    invalid = tmp_path / "not_hik.img"
    invalid.write_bytes(b"INVALID_HEADER_DATA_12345678")

    parser = HIKGParser(invalid)
    with pytest.raises(ValueError, match="missing 'HIKG' magic signature"):
        parser.parse()
