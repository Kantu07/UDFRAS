from __future__ import annotations

from pathlib import Path

from packages.adapters.base import VendorAdapter
from packages.adapters.dahua import DahuaAdapter
from packages.adapters.demosecure import DemoSecureAdapter
from packages.adapters.detector import VendorDetectionResult, VendorDetector
from packages.adapters.generic import GenericFallbackAdapter
from packages.adapters.hikvision import HikvisionAdapter


class AdapterRegistry:
    """
    Registry responsible for selecting the appropriate
    vendor adapter for an evidence source.
    """

    def __init__(self) -> None:
        self.adapters: list[VendorAdapter] = [
            DemoSecureAdapter(),
            DahuaAdapter(),
            HikvisionAdapter(),
        ]
        self._fallback = GenericFallbackAdapter()
        self._detector = VendorDetector()

    def register(self, adapter: VendorAdapter) -> None:
        self.adapters.append(adapter)

    def detect(self, evidence_path: Path) -> VendorAdapter | None:
        for adapter in self.adapters:
            if adapter.detect(evidence_path):
                return adapter

        return None

    def detect_vendor(self, evidence_path: Path) -> VendorDetectionResult:
        """Runs the low-level magic byte scanner and returns structured vendor detection."""
        return self._detector.detect(evidence_path)

    def get_adapter_or_fallback(self, evidence_path: Path) -> VendorAdapter:
        adapter = self.detect(evidence_path)
        return adapter if adapter is not None else self._fallback