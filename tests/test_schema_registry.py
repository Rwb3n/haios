"""
Tests for HAIOS Schema Registry and ConfigLoader Extension.

WORK-147: Implements schema registry at .claude/haios/schemas/
with ConfigLoader.get_schema() and substitute_variables() schema resolution.

TDD: Tests written BEFORE implementation (Session 369).
"""
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

# Add .claude/haios/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))


# --- Fixtures ---


@pytest.fixture
def schema_dir(tmp_path):
    """Create a temporary schema directory with core/ and project/ tiers."""
    core_dir = tmp_path / "schemas" / "core"
    core_dir.mkdir(parents=True)
    project_dir = tmp_path / "schemas" / "project"
    project_dir.mkdir(parents=True)

    # Write a core schema file
    work_item_schema = {
        "version": "2.0",
        "source": "TRD-WORK-ITEM-UNIVERSAL",
        "enums": {
            "status": {
                "values": ["active", "blocked", "complete", "archived"],
                "default": "active",
            },
            "type": {
                "values": ["feature", "investigation", "bug", "chore", "spike"],
                "default": "feature",
            },
            "priority": {
                "values": ["critical", "high", "medium", "low"],
                "default": "medium",
            },
            "effort": {
                "values": ["small", "medium", "large", "unknown"],
                "default": "medium",
            },
        },
    }
    (core_dir / "work_item.yaml").write_text(
        yaml.dump(work_item_schema, default_flow_style=False), encoding="utf-8"
    )

    return tmp_path / "schemas"


@pytest.fixture
def config_with_schemas(tmp_path, schema_dir):
    """Create a ConfigLoader instance with schemas loaded from tmp_path."""
    from config import ConfigLoader

    ConfigLoader.reset()

    # Patch CONFIG_DIR and haios.yaml to point to our tmp schemas
    haios_data = {
        "paths": {"schemas": str(schema_dir)},
        "toggles": {},
        "thresholds": {},
    }

    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "haios.yaml").write_text(
        yaml.dump(haios_data, default_flow_style=False), encoding="utf-8"
    )
    (config_dir / "cycles.yaml").write_text("{}", encoding="utf-8")
    (config_dir / "components.yaml").write_text("{}", encoding="utf-8")

    with patch("config.CONFIG_DIR", config_dir):
        ConfigLoader.reset()
        loader = ConfigLoader.get()
        yield loader

    ConfigLoader.reset()


# --- Test 1: Schema directory loading ---


class TestSchemaLoading:
    """Tests for ConfigLoader schema loading (Tests 1, 5)."""

    def test_config_loader_schemas_property(self, config_with_schemas):
        """Test 1: ConfigLoader.schemas returns loaded schema dict."""
        schemas = config_with_schemas.schemas
        assert isinstance(schemas, dict)
        assert "core/work_item" in schemas
        assert "enums" in schemas["core/work_item"]
        assert "status" in schemas["core/work_item"]["enums"]
        values = schemas["core/work_item"]["enums"]["status"]["values"]
        assert len(values) == 4
        assert "active" in values

    def test_schemas_empty_project_dir(self, config_with_schemas):
        """Test 5: Empty project/ dir doesn't cause errors."""
        schemas = config_with_schemas.schemas
        # project/ is empty, so no project schemas loaded
        project_keys = [k for k in schemas if k.startswith("project/")]
        assert len(project_keys) == 0
        # But core schemas still load fine
        assert "core/work_item" in schemas


# --- Test 2-4: get_schema resolution ---


class TestGetSchema:
    """Tests for ConfigLoader.get_schema() (Tests 2, 3, 4)."""

    def test_get_schema_resolves_domain_key(self, config_with_schemas):
        """Test 2: get_schema('work_item', 'status') returns enum entry."""
        result = config_with_schemas.get_schema("work_item", "status")
        assert isinstance(result, dict)
        assert "values" in result
        assert result["values"] == ["active", "blocked", "complete", "archived"]
        assert result["default"] == "active"

    def test_get_schema_missing_domain_raises(self, config_with_schemas):
        """Test 3: get_schema with unknown domain raises KeyError."""
        with pytest.raises(KeyError) as exc_info:
            config_with_schemas.get_schema("nonexistent_domain", "status")
        assert "nonexistent_domain" in str(exc_info.value)

    def test_get_schema_missing_key_raises(self, config_with_schemas):
        """Test 4: get_schema with unknown key raises KeyError."""
        with pytest.raises(KeyError) as exc_info:
            config_with_schemas.get_schema("work_item", "nonexistent_key")
        assert "nonexistent_key" not in str(exc_info.value) or "not found" in str(
            exc_info.value
        )


# --- Tests 6-9: substitute_variables schema resolution ---


class TestSubstituteVariablesSchema:
    """Tests for substitute_variables() schema ref resolution (Tests 6-9)."""

    def test_substitute_schema_ref(self, config_with_schemas):
        """Test 6: {{schema:work_item.type}} resolves to pipe-delimited values."""
        from scaffold import substitute_variables

        content = "type: {{schema:work_item.type}}"
        result = substitute_variables(content, {})
        assert result == "type: feature|investigation|bug|chore|spike"

    def test_substitute_unknown_schema_ref_raises(self, config_with_schemas):
        """Test 7: {{schema:nonexistent.key}} raises ValueError."""
        from scaffold import substitute_variables

        content = "type: {{schema:nonexistent.key}}"
        with pytest.raises(ValueError) as exc_info:
            substitute_variables(content, {})
        assert "Schema reference resolution failed" in str(exc_info.value)

    def test_substitute_mixed_refs(self, config_with_schemas):
        """Test 8: Content with both {{VAR}} and {{schema:X.Y}} resolves both."""
        from scaffold import substitute_variables

        content = "title: {{TITLE}}\ntype: {{schema:work_item.type}}"
        result = substitute_variables(content, {"TITLE": "My Title"})
        assert result == "title: My Title\ntype: feature|investigation|bug|chore|spike"

    def test_substitute_no_schema_refs_unchanged(self):
        """Test 9: Content without {{schema:}} works exactly as before."""
        from scaffold import substitute_variables

        content = "title: {{TITLE}}"
        result = substitute_variables(content, {"TITLE": "Test"})
        assert result == "title: Test"


# --- Test 10: Integration — haios.yaml schemas path ---


class TestIntegration:
    """Integration tests (Test 10)."""

    def test_haios_yaml_has_schemas_path(self):
        """Test 10: haios.yaml paths section includes schemas entry."""
        from config import ConfigLoader

        ConfigLoader.reset()
        config = ConfigLoader.get()
        assert "schemas" in config.paths
