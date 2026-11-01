from __future__ import annotations

from pathlib import Path
import pytest

from packages.forensics.carving.h264_carver import H264Carver, NALUnit


@pytest.fixture
def h264_stream_fixture(tmp_path: Path) -> Path:
    """
    Creates a synthetic raw disk block containing H.264 NAL units:
    - Offset 0: Non-zero dummy padding (so preceding bytes are not zero)
    - Offset 64: SPS (0x00000001 0x67)
    - Offset 128: PPS (0x00000001 0x68)
    - Offset 256: IDR Slice Keyframe (0x00000001 0x65)
    - Offset 512: Non-IDR P-frame (3-byte start code 0x000001 0x61)
    """
    disk = tmp_path / "raw_h264_disk.raw"
    data = bytearray([0xFF] * 4096)  # Fill with non-zero dummy background

    # SPS (NAL type 7)
    data[64:68] = b"\x00\x00\x00\x01"
    data[68] = 0x67  # 0x67 & 0x1F = 7

    # PPS (NAL type 8)
    data[128:132] = b"\x00\x00\x00\x01"
    data[132] = 0x68  # 0x68 & 0x1F = 8

    # IDR Keyframe (NAL type 5)
    data[256:260] = b"\x00\x00\x00\x01"
    data[260] = 0x65  # 0x65 & 0x1F = 5

    # P-frame (3-byte start code, NAL type 1)
    data[512:515] = b"\x00\x00\x01"
    data[515] = 0x61  # 0x61 & 0x1F = 1

    disk.write_bytes(bytes(data))
    return disk


def test_h264_carver_detects_nal_units(h264_stream_fixture: Path):
    carver = H264Carver(h264_stream_fixture)
    nal_units = carver.scan_nal_units()

    assert len(nal_units) == 4

    # 1. SPS
    assert nal_units[0].nal_type == 7
    assert nal_units[0].nal_unit_type == "SPS"
    assert nal_units[0].is_keyframe is True
    assert nal_units[0].start_offset == 64

    # 2. PPS
    assert nal_units[1].nal_type == 8
    assert nal_units[1].nal_unit_type == "PPS"
    assert nal_units[1].start_offset == 128

    # 3. IDR Keyframe
    assert nal_units[2].nal_type == 5
    assert nal_units[2].nal_unit_type == "IDR_SLICE"
    assert nal_units[2].is_keyframe is True
    assert nal_units[2].start_offset == 256

    # 4. P-frame
    assert nal_units[3].nal_type == 1
    assert nal_units[3].nal_unit_type == "NON_IDR_SLICE"
    assert nal_units[3].start_offset == 512


def test_h264_carver_carve_to_file(h264_stream_fixture: Path, tmp_path: Path):
    carver = H264Carver(h264_stream_fixture)
    output = tmp_path / "recovered" / "carved_clip.h264"

    # Carve sectors 0 to 4 (2048 bytes)
    carved_len = carver.carve_to_file(output, start_sector=0, sector_count=4, sector_size=512)

    assert carved_len == 2048
    assert output.exists()
    assert output.stat().st_size == 2048

    # Verify carved content preserved the SPS
    recovered_bytes = output.read_bytes()
    assert recovered_bytes[64:68] == b"\x00\x00\x00\x01"
    assert recovered_bytes[68] == 0x67
