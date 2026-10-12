from pathlib import Path

from packages.adapters.detector import VendorDetector


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = PROJECT_ROOT / "fixtures" / "signatures"
DEMO_PATH = PROJECT_ROOT / "fixtures" / "demo_dvr" / "demo_dvr.img"


def test_detect_dahua_dhfs_signature():
    detector = VendorDetector()
    result = detector.detect(FIXTURES_DIR / "dahua_dhfs.img")

    assert result.vendor == "DAHUA"
    assert "DHFS" in result.detected_family
    assert result.matched_signature == "44484653"  # Hex for DHFS
    assert result.confidence == "HIGH"
    assert result.is_supported is True


def test_detect_hikvision_signature():
    detector = VendorDetector()
    result = detector.detect(FIXTURES_DIR / "hikvision_hikg.img")

    assert result.vendor == "HIKVISION"
    assert result.matched_signature == "48494B47"  # Hex for HIKG
    assert result.confidence == "HIGH"
    assert result.is_supported is True


def test_detect_cpplus_signature():
    detector = VendorDetector()
    result = detector.detect(FIXTURES_DIR / "cpplus_oem.img")

    assert result.vendor == "CP_PLUS"
    assert "CP Plus" in result.detected_family
    assert result.confidence == "HIGH"
    assert result.is_supported is True


def test_detect_generic_unknown_signature():
    detector = VendorDetector()
    result = detector.detect(FIXTURES_DIR / "generic_unknown.img")

    assert result.vendor == "UNKNOWN"
    assert result.confidence == "UNRECOGNIZED"
    assert result.is_supported is False
    assert result.matched_signature is None


def test_detect_demosecure_signature():
    detector = VendorDetector()
    result = detector.detect(DEMO_PATH)

    assert result.vendor == "DemoSecure"
    assert result.confidence == "HIGH"
    assert result.is_supported is True
