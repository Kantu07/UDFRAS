from pathlib import Path

from packages.adapters.dahua import DahuaAdapter
from packages.adapters.demosecure import DemoSecureAdapter
from packages.adapters.generic import GenericFallbackAdapter
from packages.adapters.hikvision import HikvisionAdapter
from packages.adapters.registry import AdapterRegistry


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = PROJECT_ROOT / "fixtures" / "signatures"
DEMO_PATH = PROJECT_ROOT / "fixtures" / "demo_dvr" / "demo_dvr.img"


def test_registry_selects_dahua_adapter():
    registry = AdapterRegistry()
    adapter = registry.detect(FIXTURES_DIR / "dahua_dhfs.img")

    assert adapter is not None
    assert isinstance(adapter, DahuaAdapter)
    assert adapter.name == "Dahua"


def test_registry_selects_hikvision_adapter():
    registry = AdapterRegistry()
    adapter = registry.detect(FIXTURES_DIR / "hikvision_hikg.img")

    assert adapter is not None
    assert isinstance(adapter, HikvisionAdapter)
    assert adapter.name == "Hikvision"


def test_registry_selects_demosecure_adapter():
    registry = AdapterRegistry()
    adapter = registry.detect(DEMO_PATH)

    assert adapter is not None
    assert isinstance(adapter, DemoSecureAdapter)
    assert adapter.name == "DemoSecure"


def test_registry_fallback_for_unknown_evidence():
    registry = AdapterRegistry()
    adapter = registry.detect(FIXTURES_DIR / "generic_unknown.img")
    assert adapter is None

    fallback = registry.get_adapter_or_fallback(FIXTURES_DIR / "generic_unknown.img")
    assert isinstance(fallback, GenericFallbackAdapter)
    assert fallback.name == "Generic / Unrecognized"


def test_registry_detect_vendor_structured():
    registry = AdapterRegistry()
    detection = registry.detect_vendor(FIXTURES_DIR / "dahua_dhfs.img")

    assert detection.vendor == "DAHUA"
    assert detection.confidence == "HIGH"
