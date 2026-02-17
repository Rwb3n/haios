# generated: 2026-02-17
# WORK-158: ConfigLoader Path Migration
"""
Tests for ConfigLoader path resolution and migration verification.

Validates:
- New path keys resolve correctly
- Existing path keys unchanged
- Placeholder substitution works
- Unknown keys raise KeyError
- Zero hardcoded PROJECT_ROOT / path construction in migrated files
"""
import sys
from pathlib import Path

import pytest

# Load lib module
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
from config import ConfigLoader


# =========================================================================
# Fixtures
# =========================================================================


@pytest.fixture(autouse=True)
def reset_configloader():
    """Reset ConfigLoader singleton between tests."""
    ConfigLoader.reset()
    yield
    ConfigLoader.reset()


# =========================================================================
# Test 1: New path keys resolve correctly
# =========================================================================


class TestNewPathKeys:
    def test_new_keys_exist(self):
        """All path keys added in WORK-158 resolve without error."""
        config = ConfigLoader.get()
        new_keys = [
            "work_blocked",
            "plans",
            "investigations",
            "backlog",
            "session",
            "memory_db",
        ]
        for key in new_keys:
            path = config.get_path(key)
            assert path is not None
            assert "{" not in str(path), f"Unresolved placeholder in {key}: {path}"


# =========================================================================
# Test 2: Existing path keys unchanged
# =========================================================================


class TestExistingPathKeys:
    def test_existing_keys_still_work(self):
        """Existing keys from haios.yaml still resolve correctly."""
        config = ConfigLoader.get()
        # Compare as Path objects for platform safety (Memory: 85073)
        assert config.get_path("work_active") == Path("docs/work/active")
        assert config.get_path("checkpoints") == Path("docs/checkpoints")
        assert config.get_path("templates") == Path(".claude/templates")
        assert config.get_path("adr") == Path("docs/ADR")


# =========================================================================
# Test 3: Placeholder substitution
# =========================================================================


class TestPlaceholderSubstitution:
    def test_work_item_placeholder(self):
        """work_item key resolves with id placeholder."""
        config = ConfigLoader.get()
        path = config.get_path("work_item", id="WORK-158")
        assert "WORK-158" in str(path)

    def test_unresolved_placeholder_raises(self):
        """Calling get_path with template key but no kwargs raises ValueError."""
        config = ConfigLoader.get()
        with pytest.raises(ValueError, match="Unresolved placeholder"):
            config.get_path("work_item")  # needs id= kwarg


# =========================================================================
# Test 4: Unknown key raises KeyError
# =========================================================================


class TestUnknownKey:
    def test_unknown_key_raises(self):
        """Missing key raises KeyError."""
        config = ConfigLoader.get()
        with pytest.raises(KeyError):
            config.get_path("nonexistent_key_xyz")


# =========================================================================
# Tests 5-8: Per-file migration verification (grep-based)
# These verify zero hardcoded PROJECT_ROOT / path construction remains.
# =========================================================================

LIB_DIR = Path(__file__).parent.parent / ".claude" / "haios" / "lib"


def _count_hardcoded_paths(filepath: Path) -> list:
    """Count lines with PROJECT_ROOT / path construction (excluding definition)."""
    content = filepath.read_text(encoding="utf-8")
    violations = []
    for i, line in enumerate(content.split("\n"), 1):
        stripped = line.strip()
        # Skip comments and docstrings
        if stripped.startswith("#"):
            continue
        # Skip the PROJECT_ROOT definition line
        if "PROJECT_ROOT = " in line or "PROJECT_ROOT=" in line:
            continue
        # Check for hardcoded path construction
        # Allow: PROJECT_ROOT / ConfigLoader.get().get_path(...)
        # Allow: PROJECT_ROOT / variable (dynamic path, no string literal)
        if "PROJECT_ROOT /" in line and "get_path" not in line:
            # Check if the path after / is a string literal (hardcoded)
            after_slash = line.split("PROJECT_ROOT /", 1)[1].strip()
            if not after_slash.startswith('"') and not after_slash.startswith("'"):
                continue  # Variable-based path, not hardcoded
            violations.append(f"  Line {i}: {stripped}")
    return violations


class TestStatusMigration:
    def test_status_no_hardcoded_paths(self):
        """status.py has zero hardcoded PROJECT_ROOT / path construction."""
        violations = _count_hardcoded_paths(LIB_DIR / "status.py")
        assert violations == [], f"Found hardcoded paths in status.py:\n" + "\n".join(violations)


class TestScaffoldMigration:
    def test_scaffold_no_hardcoded_paths(self):
        """scaffold.py has zero hardcoded PROJECT_ROOT / path construction."""
        violations = _count_hardcoded_paths(LIB_DIR / "scaffold.py")
        assert violations == [], f"Found hardcoded paths in scaffold.py:\n" + "\n".join(violations)


class TestObservationsMigration:
    def test_observations_no_hardcoded_paths(self):
        """observations.py has zero hardcoded PROJECT_ROOT / path construction."""
        violations = _count_hardcoded_paths(LIB_DIR / "observations.py")
        assert violations == [], f"Found hardcoded paths in observations.py:\n" + "\n".join(violations)


class TestLoadersMigration:
    def test_work_loader_no_hardcoded_paths(self):
        """work_loader.py has zero hardcoded PROJECT_ROOT / path construction."""
        violations = _count_hardcoded_paths(LIB_DIR / "work_loader.py")
        assert violations == [], f"Found hardcoded paths in work_loader.py:\n" + "\n".join(violations)

    def test_session_loader_no_hardcoded_paths(self):
        """session_loader.py has zero hardcoded PROJECT_ROOT / path construction."""
        violations = _count_hardcoded_paths(LIB_DIR / "session_loader.py")
        assert violations == [], f"Found hardcoded paths in session_loader.py:\n" + "\n".join(violations)

    def test_loader_no_hardcoded_paths(self):
        """loader.py has zero hardcoded PROJECT_ROOT / path construction."""
        violations = _count_hardcoded_paths(LIB_DIR / "loader.py")
        assert violations == [], f"Found hardcoded paths in loader.py:\n" + "\n".join(violations)
