from pathlib import Path
import pytest

from packages.forensics.io.readonly import (
    ReadOnlyEvidence,
    ForensicIntegrityViolationError,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = PROJECT_ROOT / "fixtures" / "demo_dvr" / "demo_dvr.img"


def test_readonly_evidence_reads_bytes_correctly():
    with ReadOnlyEvidence(FIXTURE_PATH) as evidence:
        assert evidence.size_bytes == 922
        first_chunk = evidence.read(16)
        assert len(first_chunk) == 16
        assert b"DEMOSECURE" in evidence.read(128)


def test_readonly_evidence_chunk_iteration():
    with ReadOnlyEvidence(FIXTURE_PATH) as evidence:
        chunks = list(evidence.read_chunks(chunk_size=256))
        assert len(chunks) == 4  # 922 bytes in 256B chunks: 256, 256, 256, 154
        total_read = sum(len(c) for c in chunks)
        assert total_read == 922


def test_readonly_evidence_seek_and_tell():
    with ReadOnlyEvidence(FIXTURE_PATH) as evidence:
        evidence.seek(10)
        assert evidence.tell() == 10
        chunk = evidence.read(5)
        assert len(chunk) == 5
        assert evidence.tell() == 15


def test_readonly_evidence_file_not_found():
    with pytest.raises(FileNotFoundError):
        ReadOnlyEvidence("non_existent_disk_image.dd")
