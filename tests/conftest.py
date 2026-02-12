# generated: 2025-10-19
# System Auto: last updated on: 2026-02-11
"""
pytest Configuration and Shared Fixtures

This module contains pytest configuration and shared fixtures used across
all test modules.

WORK-117 (Session 351): Unified module loading to prevent ContextVar divergence.
Module-level loading ensures governance_layer, work_engine, queue_ceremonies, and
cycle_runner are loaded ONCE into sys.modules BEFORE test file collection. This
prevents the _load_module() unconditional overwrite bug discovered in Session 338
(WORK-116) where each test file created its own module instance with its own
ContextVars.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

# Project root (parent of tests/)
_root = Path(__file__).parent.parent

# Add module paths once — these directories contain standalone modules
# (not packages) that test files import via `from X import Y`
sys.path.insert(0, str(_root / ".claude" / "haios" / "modules"))
sys.path.insert(0, str(_root / ".claude" / "haios" / "lib"))
# Add tests/ so shared helpers (helpers.py) are importable
sys.path.insert(0, str(Path(__file__).parent))


def _load_module_once(name: str, path: Path):
    """Load a module once into sys.modules. Reuse if already loaded.

    Unlike the old _load_module() pattern which unconditionally created new
    module instances (causing ContextVar divergence), this function checks
    sys.modules first and reuses existing entries.

    Args:
        name: Module name for sys.modules registration.
        path: Absolute path to the .py file.

    Returns:
        The loaded module.
    """
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# =============================================================================
# Module-level loading (runs before test file collection)
# =============================================================================
# Load in dependency order: governance_layer first (imported by work_engine),
# then work_engine (imported by queue_ceremonies), then queue_ceremonies,
# then cycle_runner.

_load_module_once(
    "governance_layer",
    _root / ".claude" / "haios" / "modules" / "governance_layer.py",
)
_load_module_once(
    "work_engine",
    _root / ".claude" / "haios" / "modules" / "work_engine.py",
)
_load_module_once(
    "queue_ceremonies",
    _root / ".claude" / "haios" / "lib" / "queue_ceremonies.py",
)
_load_module_once(
    "cycle_runner",
    _root / ".claude" / "haios" / "modules" / "cycle_runner.py",
)


# =============================================================================
# Shared Fixtures (TODO: populate as needed)
# =============================================================================

# TODO: Implement temp database fixture
# TODO: Implement temp directory fixture
# TODO: Implement sample schema fixture
# TODO: Implement mock langextract fixture
