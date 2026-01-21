# generated: 2026-01-21
# System Auto: last updated on: 2026-01-21T20:14:16
"""
Tests for lib migration from .claude/lib/ to .claude/haios/lib/

These tests verify:
1. All lib modules are importable from new location
2. Compatibility shims work from old location
3. Consumer modules function after migration

WORK-006: Migrate .claude/lib to portable plugin directory
"""
import sys
from pathlib import Path
import pytest

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent


class TestLibModulesImportable:
    """Test 1: All lib modules importable from new location."""

    def test_haios_lib_directory_exists(self):
        """Verify .claude/haios/lib/ directory exists."""
        haios_lib = PROJECT_ROOT / ".claude" / "haios" / "lib"
        assert haios_lib.exists(), f"Directory {haios_lib} does not exist"
        assert haios_lib.is_dir(), f"{haios_lib} is not a directory"

    def test_haios_lib_init_exists(self):
        """Verify __init__.py exists in new location."""
        init_file = PROJECT_ROOT / ".claude" / "haios" / "lib" / "__init__.py"
        assert init_file.exists(), f"File {init_file} does not exist"

    def test_all_modules_importable_from_haios_lib(self):
        """Verify all 23 modules can be imported from .claude/haios/lib/."""
        haios_lib = PROJECT_ROOT / ".claude" / "haios" / "lib"

        # Add to path for import
        sys.path.insert(0, str(haios_lib))

        try:
            # Core modules used by consumers (governance_layer, hooks)
            # These MUST import cleanly from new location
            core_modules = [
                "database",
                "scaffold",
                "work_item",
                "config",
                "status",
                "validate",
                "observations",
                "cascade",
                "spawn",
                "backfill",
                "node_cycle",
                "governance_events",
                "routing",
                "dependencies",
                "error_capture",
                "audit",
                "errors",
            ]

            # Modules with haios_etl dependencies (pre-existing external deps)
            # Just verify files exist, don't test import
            etl_dependent_modules = [
                "retrieval",
                "synthesis",
                "extraction",
                "cli",
                "mcp_server",
            ]

            imported = []
            failed = []

            for mod in core_modules:
                try:
                    __import__(mod)
                    imported.append(mod)
                except ImportError as e:
                    failed.append((mod, str(e)))

            assert len(failed) == 0, f"Failed to import core modules: {failed}"
            assert len(imported) >= 17, f"Expected at least 17 core modules, got {len(imported)}"

            # Verify ETL-dependent module files exist (structural check only)
            for mod in etl_dependent_modules:
                mod_file = haios_lib / f"{mod}.py"
                assert mod_file.exists(), f"Module file {mod_file} should exist"
        finally:
            # Clean up path
            sys.path.remove(str(haios_lib))


class TestCompatibilityShims:
    """Test 2: Compatibility shims work from old location."""

    def test_old_location_has_deprecation_init(self):
        """Verify old .claude/lib/ has deprecation notice."""
        old_lib = PROJECT_ROOT / ".claude" / "lib"
        init_file = old_lib / "__init__.py"

        assert init_file.exists(), f"Shim file {init_file} does not exist"

        content = init_file.read_text()
        assert "deprecated" in content.lower() or "DEPRECATED" in content, \
            "Old __init__.py should contain deprecation notice"

    def test_shim_reexports_database(self):
        """Verify database module can still be imported via shim."""
        old_lib = PROJECT_ROOT / ".claude" / "lib"
        sys.path.insert(0, str(old_lib))

        try:
            # This should work via re-export from new location
            from database import DatabaseManager
            assert DatabaseManager is not None, "DatabaseManager should be importable"
        finally:
            sys.path.remove(str(old_lib))


class TestConsumerModulesFunction:
    """Test 3: Consumer modules still function after migration."""

    def test_governance_layer_imports(self):
        """Verify governance_layer.py imports work after migration."""
        modules_dir = PROJECT_ROOT / ".claude" / "haios" / "modules"
        sys.path.insert(0, str(modules_dir))

        # Also add haios/lib to path for the import chain
        haios_lib = PROJECT_ROOT / ".claude" / "haios" / "lib"
        sys.path.insert(0, str(haios_lib))

        try:
            from governance_layer import GovernanceLayer, GateResult
            layer = GovernanceLayer()
            assert layer is not None, "GovernanceLayer should instantiate"
        finally:
            sys.path.remove(str(modules_dir))
            if str(haios_lib) in sys.path:
                sys.path.remove(str(haios_lib))

    def test_hooks_can_import_validate(self):
        """Verify hooks can import validate module from new location."""
        haios_lib = PROJECT_ROOT / ".claude" / "haios" / "lib"
        sys.path.insert(0, str(haios_lib))

        try:
            from validate import validate_template
            assert callable(validate_template), "validate_template should be callable"
        finally:
            sys.path.remove(str(haios_lib))

    def test_hooks_can_import_node_cycle(self):
        """Verify hooks can import node_cycle module from new location."""
        haios_lib = PROJECT_ROOT / ".claude" / "haios" / "lib"
        sys.path.insert(0, str(haios_lib))

        try:
            from node_cycle import get_node_binding, detect_node_exit_attempt
            assert callable(get_node_binding), "get_node_binding should be callable"
            assert callable(detect_node_exit_attempt), "detect_node_exit_attempt should be callable"
        finally:
            sys.path.remove(str(haios_lib))
