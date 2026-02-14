# generated: 2026-01-03
# System Auto: last updated on: 2026-02-02T17:46:47
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
        self._schemas = self._load_schemas()

    def _load_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load all YAML schema files from schemas directory.

        Scans both core/ and project/ subdirectories.
        Schema key = "{tier}/{filename_without_ext}" (e.g., "core/work_item").

        Returns:
            Dict mapping schema keys to loaded YAML content.
        """
        schemas_path = self._haios.get("paths", {}).get("schemas")
        if not schemas_path:
            return {}

        # Resolve relative to project root (CONFIG_DIR parent is .claude/haios/)
        schemas_dir = CONFIG_DIR.parent.parent.parent / schemas_path
        if not schemas_dir.exists():
            return {}

        result = {}
        for tier_dir in schemas_dir.iterdir():
            if not tier_dir.is_dir() or tier_dir.name.startswith("."):
                continue
            for schema_file in tier_dir.glob("*.yaml"):
                key = f"{tier_dir.name}/{schema_file.stem}"
                try:
                    with open(schema_file, encoding="utf-8") as f:
                        data = yaml.safe_load(f) or {}
                    # A4 mitigation: validate schema format
                    if not isinstance(data, dict):
                        continue  # Skip non-dict files
                    if "enums" not in data and "transitions" not in data:
                        continue  # Skip files without expected sections
                    result[key] = data
                except Exception:
                    pass  # Skip malformed files silently (graceful degradation)
        return result

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

    # Path constants (WORK-080: Single source of truth)
    @property
    def paths(self) -> Dict[str, str]:
        """Path constants from haios.yaml (single source of truth - WORK-080)."""
        return self._haios.get("paths", {})

    def get_path(self, key: str, **kwargs) -> Path:
        """
        Get path with placeholder substitution.

        Args:
            key: Path key from haios.yaml paths section (e.g., "work_item")
            **kwargs: Placeholder values (e.g., id="WORK-080")

        Returns:
            Path object with placeholders resolved

        Raises:
            KeyError: If key not found in paths section
            ValueError: If unresolved placeholders remain after substitution

        Examples:
            config.get_path("work_dir")  # Returns Path("docs/work")
            config.get_path("work_item", id="WORK-080")  # Returns Path("docs/work/active/WORK-080/WORK.md")
        """
        template = self.paths.get(key)
        if template is None:
            raise KeyError(f"Path key '{key}' not found in haios.yaml paths section")
        resolved = template.format(**kwargs) if kwargs else template
        # Check for unresolved placeholders (A4 mitigation from critique)
        if '{' in resolved:
            raise ValueError(f"Unresolved placeholder in path: {resolved}")
        return Path(resolved)

    # Schema registry (WORK-147: central schema location)
    @property
    def schemas(self) -> Dict[str, Dict[str, Any]]:
        """Schema registry content (core/ and project/ tiers)."""
        return self._schemas

    def get_schema(self, domain: str, key: str) -> Any:
        """Get schema enum or section by domain and key.

        Searches all tiers (core/ first, then project/) for the domain file,
        then returns the value at the key path within 'enums' section.

        Args:
            domain: Schema file name without extension (e.g., "work_item")
            key: Key within the enums section (e.g., "status", "type")

        Returns:
            Schema entry dict (typically has 'values', 'default' keys)

        Raises:
            KeyError: If domain or key not found in any tier
        """
        # Search tiers in order: core first, then project
        for tier in ("core", "project"):
            schema_key = f"{tier}/{domain}"
            if schema_key in self._schemas:
                schema = self._schemas[schema_key]
                enums = schema.get("enums", {})
                if key in enums:
                    return enums[key]
                # Also check top-level keys (for transitions, etc.)
                if key in schema:
                    return schema[key]

        raise KeyError(
            f"Schema '{domain}.{key}' not found. "
            f"Available domains: {[k.split('/')[1] for k in self._schemas.keys()]}"
        )
