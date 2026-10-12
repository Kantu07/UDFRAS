from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SignatureDefinition:
    vendor: str
    family: str
    magic_bytes: bytes
    offset: int
    description: str
    confidence_level: str  # HIGH, MEDIUM, LOW


# Canonical vendor signature database for multi-vendor DVR/NVR detection
VENDOR_SIGNATURES: List[SignatureDefinition] = [
    # Dahua DHFS File System (Sector 0 or Sector 1)
    SignatureDefinition(
        vendor="DAHUA",
        family="Dahua DHFS 4.1",
        magic_bytes=b"DHFS",
        offset=0,
        description="Dahua DHFS Master Sector at offset 0",
        confidence_level="HIGH",
    ),
    SignatureDefinition(
        vendor="DAHUA",
        family="Dahua DHFS Sector 1",
        magic_bytes=b"DHFS",
        offset=512,
        description="Dahua DHFS Master Sector at Sector 1 (512 bytes)",
        confidence_level="HIGH",
    ),

    # Hikvision Surveillance Storage Layouts
    SignatureDefinition(
        vendor="HIKVISION",
        family="Hikvision Master Sector",
        magic_bytes=b"HIKG",
        offset=0,
        description="Hikvision Master Disk Identifier (HIKG)",
        confidence_level="HIGH",
    ),
    SignatureDefinition(
        vendor="HIKVISION",
        family="Hikvision File System",
        magic_bytes=b"HKCS",
        offset=0,
        description="Hikvision File System Track Header (HKCS)",
        confidence_level="HIGH",
    ),
    SignatureDefinition(
        vendor="HIKVISION",
        family="Hikvision Extended Header",
        magic_bytes=b"HIKVISION",
        offset=0,
        description="Hikvision ASCII disk identifier",
        confidence_level="HIGH",
    ),

    # CP Plus (Dahua OEM variant with customized metadata)
    SignatureDefinition(
        vendor="CP_PLUS",
        family="CP Plus (Dahua OEM)",
        magic_bytes=b"DHFS",
        offset=0,
        description="CP Plus CCTV disk layout based on DHFS",
        confidence_level="MEDIUM",
    ),

    # DemoSecure Test Environment
    SignatureDefinition(
        vendor="DemoSecure",
        family="DemoSecure Synthetic Fixture",
        magic_bytes=b"=== DEMOSECURE FORENSIC FIXTURE ===",
        offset=0,
        description="Deterministic test fixture for validation",
        confidence_level="HIGH",
    ),
]
