from __future__ import annotations

import os
from pathlib import Path
from typing import BinaryIO, Generator


class ForensicIntegrityViolationError(Exception):
    """Raised when an attempt is made to modify read-only forensic evidence."""
    pass


class ReadOnlyEvidence:
    """
    Forensic read-only evidence file handler.
    
    Guarantees strict read-only access (rb mode) to forensic disk images
    in compliance with ISO/IEC 27037 standards. Enforces that no write handles
    can ever be opened on the source evidence.
    """

    def __init__(self, file_path: str | Path) -> None:
        self.path = Path(file_path).resolve()
        if not self.path.exists():
            raise FileNotFoundError(f"Forensic evidence not found: {self.path}")
        if not self.path.is_file():
            raise ValueError(f"Path is not a regular file: {self.path}")

        self._file_handle: BinaryIO | None = None
        self._initial_size = self.path.stat().st_size
        self._initial_mtime = self.path.stat().st_mtime

    @property
    def size_bytes(self) -> int:
        return self._initial_size

    def __enter__(self) -> ReadOnlyEvidence:
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def open(self) -> BinaryIO:
        if self._file_handle is None or self._file_handle.closed:
            # Strictly open with 'rb' mode only
            self._file_handle = open(self.path, "rb")
        return self._file_handle

    def close(self) -> None:
        if self._file_handle is not None and not self._file_handle.closed:
            self._file_handle.close()
            self._file_handle = None
        self._verify_unaltered()

    def read(self, size: int = -1) -> bytes:
        if self._file_handle is None or self._file_handle.closed:
            self.open()
        return self._file_handle.read(size)

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        if self._file_handle is None or self._file_handle.closed:
            self.open()
        return self._file_handle.seek(offset, whence)

    def tell(self) -> int:
        if self._file_handle is None or self._file_handle.closed:
            self.open()
        return self._file_handle.tell()

    def read_chunks(self, chunk_size: int = 65536) -> Generator[bytes, None, None]:
        """Iterates over the evidence in chunked blocks (default: 64 KB)."""
        if self._file_handle is None or self._file_handle.closed:
            self.open()
        self.seek(0)
        while True:
            chunk = self._file_handle.read(chunk_size)
            if not chunk:
                break
            yield chunk

    def _verify_unaltered(self) -> None:
        """Verifies file size and modification time have not changed."""
        current_stat = self.path.stat()
        if current_stat.st_size != self._initial_size:
            raise ForensicIntegrityViolationError(
                f"Evidence file size modified! Initial: {self._initial_size}, Current: {current_stat.st_size}"
            )
        if current_stat.st_mtime != self._initial_mtime:
            raise ForensicIntegrityViolationError(
                f"Evidence file timestamp modified! Initial: {self._initial_mtime}, Current: {current_stat.st_mtime}"
            )
