from __future__ import annotations

from pathlib import Path


FIXTURE_DIR = Path(__file__).resolve().parent


def generate_all_signatures() -> None:
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Dahua DHFS Sector 0 Image (4 KB)
    dahua_img = FIXTURE_DIR / "dahua_dhfs.img"
    dahua_header = bytearray(4096)
    dahua_header[0:4] = b"DHFS"
    dahua_header[4:8] = (4).to_bytes(4, "little")  # Version 4
    dahua_header[8:24] = b"DAHUA-SURVEILLANCE"
    dahua_img.write_bytes(bytes(dahua_header))

    # 2. Hikvision Master Sector Image (4 KB)
    hik_img = FIXTURE_DIR / "hikvision_hikg.img"
    hik_header = bytearray(4096)
    hik_header[0:4] = b"HIKG"
    hik_header[8:12] = b"HKCS"
    hik_header[12:28] = b"HIKVISION-MASTER"
    hik_img.write_bytes(bytes(hik_header))

    # 3. CP Plus OEM Image (4 KB)
    cpplus_img = FIXTURE_DIR / "cpplus_oem.img"
    cpplus_header = bytearray(4096)
    cpplus_header[0:4] = b"DHFS"
    cpplus_header[8:24] = b"CP PLUS-SECURITY"
    cpplus_img.write_bytes(bytes(cpplus_header))

    # 4. Generic / Unknown Disk (4 KB)
    generic_img = FIXTURE_DIR / "generic_unknown.img"
    generic_header = bytearray(4096)
    generic_header[0:3] = b"\xeb\x58\x90"  # standard FAT/NTFS jump
    generic_header[3:11] = b"MSDOS5.0"
    generic_img.write_bytes(bytes(generic_header))

    print(f"Generated 4 signature fixtures in {FIXTURE_DIR}")


if __name__ == "__main__":
    generate_all_signatures()
