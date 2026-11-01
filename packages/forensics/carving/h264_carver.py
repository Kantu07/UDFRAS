from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from packages.forensics.io.readonly import ReadOnlyEvidence


@dataclass(frozen=True)
class NALUnit:
    start_offset: int
    nal_type: int
    nal_unit_type: str
    length: int

    @property
    def is_keyframe(self) -> bool:
        return self.nal_type == 5 or self.nal_type == 7


class H264Carver:
    NAL_NAMES = {
        1: "NON_IDR_SLICE",  # P-frame / B-frame
        5: "IDR_SLICE",      # I-frame Keyframe
        6: "SEI",            # Supplemental enhancement info
        7: "SPS",            # Sequence Parameter Set
        8: "PPS",            # Picture Parameter Set
        9: "AUD",            # Access unit delimiter
    }

    def __init__(self, evidence_path: Path):
        self.evidence_path = Path(evidence_path)

    def scan_nal_units(self, max_bytes: Optional[int] = None) -> List[NALUnit]:
        nal_units: List[NALUnit] = []

        with ReadOnlyEvidence(self.evidence_path) as evidence:
            scan_limit = min(evidence.size_bytes, max_bytes) if max_bytes else evidence.size_bytes
            buffer_size = 65536
            file_offset = 0
            carryover = b""

            while file_offset < scan_limit:
                read_len = min(buffer_size, scan_limit - file_offset)
                raw_chunk = evidence.read(read_len)
                if not raw_chunk:
                    break

                chunk = carryover + raw_chunk
                chunk_base_offset = file_offset - len(carryover)

                i = 0
                while i <= len(chunk) - 4:
                    start_code_len = 0
                    if chunk[i:i + 4] == b"\x00\x00\x00\x01":
                        start_code_len = 4
                    elif i > 0 and chunk[i - 1] == 0:
                        # Preceded by a 0, handled as part of 4-byte check
                        pass
                    elif chunk[i:i + 3] == b"\x00\x00\x01":
                        start_code_len = 3

                    if start_code_len > 0:
                        header_byte = chunk[i + start_code_len]
                        nal_type = header_byte & 0x1F
                        nal_name = self.NAL_NAMES.get(nal_type, f"NAL_TYPE_{nal_type}")

                        global_offset = chunk_base_offset + i
                        nal_units.append(NALUnit(
                            start_offset=global_offset,
                            nal_type=nal_type,
                            nal_unit_type=nal_name,
                            length=0,
                        ))
                        i += start_code_len

                    i += 1

                carryover = chunk[-4:]
                file_offset += len(raw_chunk)

        return nal_units

    def carve_to_file(self, output_path: Path, start_sector: int, sector_count: int, sector_size: int = 512) -> int:
        start_byte = start_sector * sector_size
        total_bytes = sector_count * sector_size

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        carved_bytes = 0
        with ReadOnlyEvidence(self.evidence_path) as evidence:
            if start_byte >= evidence.size_bytes:
                return 0

            evidence.seek(start_byte)
            bytes_to_read = min(total_bytes, evidence.size_bytes - start_byte)

            with open(output_path, "wb") as out_f:
                chunk_size = 65536
                while bytes_to_read > 0:
                    read_size = min(chunk_size, bytes_to_read)
                    block = evidence.read(read_size)
                    if not block:
                        break
                    out_f.write(block)
                    carved_bytes += len(block)
                    bytes_to_read -= len(block)

        return carved_bytes
