from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from packages.forensics.io.readonly import ReadOnlyEvidence


@dataclass(frozen=True)
class HashManifest:
    """Immutable manifest containing dual cryptographic verification hashes."""
    md5: str
    sha256: str
    size_bytes: int
    duration_seconds: float


class DualHasher:
    """
    Streaming cryptographic dual-hasher engine.
    
    Computes both SHA-256 (court-admissible cryptographic standard) and MD5
    (legacy fast match) simultaneously in a single linear pass over evidence blocks.
    Memory footprint is strictly O(1) regardless of image size.
    """

    def __init__(self, chunk_size: int = 65536) -> None:
        self.chunk_size = chunk_size

    def hash_evidence(
        self,
        evidence_path: str | Path,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> HashManifest:
        start_time = time.perf_counter()
        
        md5_ctx = hashlib.md5()
        sha256_ctx = hashlib.sha256()
        bytes_read = 0

        with ReadOnlyEvidence(evidence_path) as evidence:
            total_bytes = evidence.size_bytes

            for chunk in evidence.read_chunks(self.chunk_size):
                md5_ctx.update(chunk)
                sha256_ctx.update(chunk)
                bytes_read += len(chunk)

                if on_progress:
                    on_progress(bytes_read, total_bytes)

        elapsed = time.perf_counter() - start_time

        return HashManifest(
            md5=md5_ctx.hexdigest(),
            sha256=sha256_ctx.hexdigest(),
            size_bytes=bytes_read,
            duration_seconds=round(elapsed, 4),
        )

    def hash_bytes(self, data: bytes) -> HashManifest:
        """Helper to hash an in-memory byte sequence (used for headers or synthetic tests)."""
        start_time = time.perf_counter()
        md5_ctx = hashlib.md5(data)
        sha256_ctx = hashlib.sha256(data)
        elapsed = time.perf_counter() - start_time

        return HashManifest(
            md5=md5_ctx.hexdigest(),
            sha256=sha256_ctx.hexdigest(),
            size_bytes=len(data),
            duration_seconds=round(elapsed, 6),
        )
