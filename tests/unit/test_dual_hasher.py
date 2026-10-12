import hashlib
from pathlib import Path

from packages.forensics.hashing.hasher import DualHasher


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = PROJECT_ROOT / "fixtures" / "demo_dvr" / "demo_dvr.img"


def test_dual_hasher_matches_standard_hashlib():
    raw_data = FIXTURE_PATH.read_bytes()
    expected_md5 = hashlib.md5(raw_data).hexdigest()
    expected_sha256 = hashlib.sha256(raw_data).hexdigest()

    hasher = DualHasher(chunk_size=128)
    manifest = hasher.hash_evidence(FIXTURE_PATH)

    assert manifest.md5 == expected_md5
    assert manifest.sha256 == expected_sha256
    assert manifest.size_bytes == len(raw_data)
    assert manifest.duration_seconds >= 0


def test_dual_hasher_progress_callback():
    progress_records = []

    def on_progress(bytes_read: int, total_bytes: int):
        progress_records.append((bytes_read, total_bytes))

    hasher = DualHasher(chunk_size=256)
    manifest = hasher.hash_evidence(FIXTURE_PATH, on_progress=on_progress)

    assert len(progress_records) > 0
    # Final progress callback should reflect the full file size
    assert progress_records[-1][0] == manifest.size_bytes
    assert progress_records[-1][1] == manifest.size_bytes


def test_dual_hasher_memory_bytes():
    data = b"FORENSIC-TEST-STREAM-0123456789"
    hasher = DualHasher()
    manifest = hasher.hash_bytes(data)

    assert manifest.sha256 == hashlib.sha256(data).hexdigest()
    assert manifest.md5 == hashlib.md5(data).hexdigest()
    assert manifest.size_bytes == len(data)
