# generated: 2025-12-21
# System Auto: last updated on: 2025-12-21 11:48:12
"""
Phase 0 Tests: Plugin Structure Verification

These tests verify the foundational plugin structure exists per PLAN-E2-120.
Tests written FIRST per TDD methodology (implementation-cycle skill).
"""
from pathlib import Path
import json


class TestPluginStructure:
    """Tests for plugin foundation (Phase 0)."""

    def test_lib_directory_exists(self):
        """Library directory must exist."""
        lib_dir = Path('.claude/lib')
        assert lib_dir.is_dir(), "Missing .claude/lib/ directory"

    def test_lib_has_init(self):
        """Library must be a proper Python package."""
        init = Path('.claude/lib/__init__.py')
        assert init.exists(), "Missing .claude/lib/__init__.py"

    def test_plugin_manifest_exists(self):
        """Plugin manifest must exist."""
        manifest = Path('.claude/.claude-plugin/plugin.json')
        assert manifest.exists(), "Missing .claude/.claude-plugin/plugin.json"

    def test_plugin_manifest_valid_json(self):
        """Plugin manifest must be valid JSON."""
        manifest = Path('.claude/.claude-plugin/plugin.json')
        if manifest.exists():
            with open(manifest) as f:
                data = json.load(f)
            assert 'name' in data, "Manifest missing 'name' field"
            assert 'description' in data, "Manifest missing 'description' field"
            assert 'version' in data, "Manifest missing 'version' field"

    def test_plugin_manifest_has_haios_name(self):
        """Plugin manifest should identify as haios."""
        manifest = Path('.claude/.claude-plugin/plugin.json')
        if manifest.exists():
            with open(manifest) as f:
                data = json.load(f)
            assert data.get('name') == 'haios', f"Expected name 'haios', got '{data.get('name')}'"

    def test_lib_readme_exists(self):
        """Library should have README for module documentation."""
        readme = Path('.claude/lib/README.md')
        assert readme.exists(), "Missing .claude/lib/README.md"
