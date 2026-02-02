# generated: 2026-01-03
# System Auto: last updated on: 2026-02-02T17:45:44
"""
Tests for HAIOS unified configuration loader.

E2-246: Consolidate Config Files MVP
"""
import pytest
import sys
from pathlib import Path

# Add .claude/haios/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))


class TestConfigLoaderSingleton:
    """Test ConfigLoader singleton pattern."""

    def test_config_loader_singleton(self):
        """ConfigLoader.get() returns same instance."""
        from config import ConfigLoader

        # Reset to ensure clean state
        ConfigLoader.reset()

        loader1 = ConfigLoader.get()
        loader2 = ConfigLoader.get()
        assert loader1 is loader2

    def test_config_loader_reset(self):
        """ConfigLoader.reset() creates new instance on next get()."""
        from config import ConfigLoader

        loader1 = ConfigLoader.get()
        ConfigLoader.reset()
        loader2 = ConfigLoader.get()

        # After reset, should be different instance
        assert loader1 is not loader2


class TestHaiosConfig:
    """Test haios.yaml loading."""

    def test_load_haios_config(self):
        """haios.yaml loads with toggles and thresholds."""
        from config import ConfigLoader
        ConfigLoader.reset()

        loader = ConfigLoader.get()
        assert "toggles" in loader.haios
        assert "thresholds" in loader.haios
        assert loader.toggles.get("block_powershell") is True

    def test_haios_manifest(self):
        """haios.yaml contains manifest section."""
        from config import ConfigLoader
        ConfigLoader.reset()

        loader = ConfigLoader.get()
        assert "manifest" in loader.haios
        assert loader.haios["manifest"]["name"] == "haios"


class TestCyclesConfig:
    """Test cycles.yaml loading."""

    def test_load_cycles_config(self):
        """cycles.yaml loads with node bindings."""
        from config import ConfigLoader
        ConfigLoader.reset()

        loader = ConfigLoader.get()
        assert "nodes" in loader.cycles
        assert "backlog" in loader.node_bindings
        assert "discovery" in loader.node_bindings


class TestBackwardCompatibility:
    """Test backward compatibility with old config accessors."""

    def test_backward_compat_toggles(self):
        """loader.toggles matches old governance-toggles.yaml content."""
        from config import ConfigLoader
        ConfigLoader.reset()

        loader = ConfigLoader.get()
        # Old behavior: block_powershell from governance-toggles.yaml
        assert loader.toggles.get("block_powershell") is True

    def test_backward_compat_thresholds(self):
        """loader.thresholds matches old routing-thresholds.yaml content."""
        from config import ConfigLoader
        ConfigLoader.reset()

        loader = ConfigLoader.get()
        thresholds = loader.thresholds
        assert "observation_pending" in thresholds
        assert thresholds["observation_pending"]["max_count"] == 10

    def test_backward_compat_node_bindings(self):
        """loader.node_bindings matches old node-cycle-bindings.yaml content."""
        from config import ConfigLoader
        ConfigLoader.reset()

        loader = ConfigLoader.get()
        bindings = loader.node_bindings
        assert "discovery" in bindings
        assert bindings["discovery"]["cycle"] == "investigation-cycle"


class TestGracefulDegradation:
    """Test graceful degradation on missing/invalid config."""

    def test_missing_config_returns_empty(self):
        """Missing config file returns empty dict (graceful degradation)."""
        from config import ConfigLoader
        ConfigLoader.reset()

        loader = ConfigLoader.get()
        # components.yaml starts as placeholder with empty dicts
        assert isinstance(loader.components, dict)


class TestPathsConfig:
    """Test ConfigLoader.paths functionality (WORK-080)."""

    def test_config_loader_paths_property(self):
        """ConfigLoader.paths returns paths dict from haios.yaml."""
        from config import ConfigLoader
        ConfigLoader.reset()

        config = ConfigLoader.get()
        paths = config.paths
        assert isinstance(paths, dict)
        assert "work_dir" in paths
        assert paths["work_dir"] == "docs/work"

    def test_config_loader_get_path_simple(self):
        """get_path returns Path for simple keys."""
        from config import ConfigLoader
        ConfigLoader.reset()

        config = ConfigLoader.get()
        path = config.get_path("work_dir")
        assert isinstance(path, Path)
        # Use Path comparison for platform independence
        assert path == Path("docs/work")

    def test_config_loader_get_path_interpolated(self):
        """get_path substitutes placeholders."""
        from config import ConfigLoader
        ConfigLoader.reset()

        config = ConfigLoader.get()
        path = config.get_path("work_item", id="WORK-080")
        # Use Path comparison for platform independence
        assert path == Path("docs/work/active/WORK-080/WORK.md")

    def test_config_loader_get_path_missing_key(self):
        """get_path raises KeyError for unknown keys."""
        from config import ConfigLoader
        ConfigLoader.reset()

        config = ConfigLoader.get()
        with pytest.raises(KeyError) as exc_info:
            config.get_path("nonexistent_key")
        assert "nonexistent_key" in str(exc_info.value)

    def test_config_loader_get_path_unresolved_placeholder(self):
        """get_path raises ValueError for unresolved placeholders."""
        from config import ConfigLoader
        ConfigLoader.reset()

        config = ConfigLoader.get()
        # work_item has {id} placeholder - calling without id= should raise
        with pytest.raises(ValueError) as exc_info:
            config.get_path("work_item")  # Missing id= kwarg
        assert "Unresolved placeholder" in str(exc_info.value)
