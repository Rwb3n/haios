# generated: 2026-01-03
# System Auto: last updated on: 2026-01-21T22:21:39
"""
Unified configuration loader for HAIOS modules.

E2-246: Consolidate Config Files MVP

Provides single access point for all config files:
- haios.yaml: toggles, thresholds, manifest
- cycles.yaml: node bindings, cycle definitions
- components.yaml: skill/agent/hook registries

Usage:
    from config import ConfigLoader
    config = ConfigLoader.get()
    if config.toggles.get("block_powershell"):
        # handle blocked
"""
from pathlib import Path
from typing import Any, Dict, Optional
import yaml

# Config directory relative to this file (.claude/haios/lib/ -> .claude/haios/config/)
CONFIG_DIR = Path(__file__).parent.parent / "config"


class ConfigLoader:
    """Unified config access for HAIOS modules."""

    _instance: Optional["ConfigLoader"] = None

    @classmethod
    def get(cls) -> "ConfigLoader":
        """Get singleton config instance. Creates on first call."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton (for testing)."""
        cls._instance = None

    def __init__(self):
        """Load all config files on init."""
        self._haios = self._load("haios.yaml")
        self._cycles = self._load("cycles.yaml")
        self._components = self._load("components.yaml")

    def _load(self, filename: str) -> Dict[str, Any]:
        """Load a YAML config file, returning empty dict on failure."""
        path = CONFIG_DIR / filename
        if not path.exists():
            return {}
        try:
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    @property
    def haios(self) -> Dict[str, Any]:
        """Full haios.yaml content."""
        return self._haios

    @property
    def cycles(self) -> Dict[str, Any]:
        """Full cycles.yaml content."""
        return self._cycles

    @property
    def components(self) -> Dict[str, Any]:
        """Full components.yaml content."""
        return self._components

    # Backward compatibility accessors
    @property
    def toggles(self) -> Dict[str, Any]:
        """Governance toggles (backward compat for governance-toggles.yaml)."""
        return self._haios.get("toggles", {})

    @property
    def thresholds(self) -> Dict[str, Any]:
        """Routing thresholds (backward compat for routing-thresholds.yaml)."""
        return self._haios.get("thresholds", {})

    @property
    def node_bindings(self) -> Dict[str, Any]:
        """Node-cycle bindings (backward compat for node-cycle-bindings.yaml)."""
        return self._cycles.get("nodes", {})
