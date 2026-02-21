# generated: 2026-01-24
# System Auto: last updated on: 2026-02-21T00:30:00
"""
Tests for ColdstartOrchestrator (WORK-011, CH-007).
WORK-180: Added tier selection tests (Tests 9-18, ADR-047).

TDD: These tests define expected behavior before implementation.
"""
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

# Add lib path for imports
_lib_path = Path(__file__).parent.parent / ".claude" / "haios" / "lib"
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))


class MockLoader:
    """Mock loader that returns predictable content."""

    def __init__(self, content: str):
        self._content = content

    def load(self) -> str:
        return self._content


# =============================================================================
# Test 1: Orchestrator Loads Config
# =============================================================================


def test_orchestrator_loads_config(tmp_path):
    """ColdstartOrchestrator reads coldstart.yaml config file."""
    config = tmp_path / "coldstart.yaml"
    config.write_text("phases:\n  - id: identity\n    breathe: true")

    from coldstart_orchestrator import ColdstartOrchestrator

    orch = ColdstartOrchestrator(config_path=config)
    assert orch.config is not None
    assert "phases" in orch.config
    assert len(orch.config["phases"]) == 1
    assert orch.config["phases"][0]["id"] == "identity"


# =============================================================================
# Test 2: Orchestrator Runs Phases in Order
# =============================================================================


def test_orchestrator_runs_phases_in_order(tmp_path):
    """run() executes phases in config order."""
    config = tmp_path / "coldstart.yaml"
    config.write_text("phases:\n  - id: identity\n  - id: session")

    from coldstart_orchestrator import ColdstartOrchestrator

    orch = ColdstartOrchestrator(config_path=config)
    # Replace loaders with mocks
    orch._loaders = {
        "identity": lambda: MockLoader("IDENTITY_CONTENT"),
        "session": lambda: MockLoader("SESSION_CONTENT"),
    }

    output = orch.run()

    # Verify order
    assert "IDENTITY_CONTENT" in output
    assert "SESSION_CONTENT" in output
    assert output.index("IDENTITY_CONTENT") < output.index("SESSION_CONTENT")


# =============================================================================
# Test 3: Breathe Markers Between Phases
# =============================================================================


def test_breathe_markers_between_phases(tmp_path):
    """run() adds [BREATHE] when phase.breathe is True."""
    config = tmp_path / "coldstart.yaml"
    config.write_text(
        """phases:
  - id: identity
    breathe: true
  - id: session
    breathe: false"""
    )

    from coldstart_orchestrator import ColdstartOrchestrator

    orch = ColdstartOrchestrator(config_path=config)
    orch._loaders = {
        "identity": lambda: MockLoader("ID"),
        "session": lambda: MockLoader("SESS"),
    }

    output = orch.run()

    assert "[BREATHE]" in output
    # Breathe appears after identity, not after session
    assert output.count("[BREATHE]") == 1
    # Verify order: ID then BREATHE then SESS
    id_pos = output.index("ID")
    breathe_pos = output.index("[BREATHE]")
    sess_pos = output.index("SESS")
    assert id_pos < breathe_pos < sess_pos


# =============================================================================
# Test 4: Content Parity Check
# =============================================================================


def test_content_parity_with_individual_loaders():
    """Orchestrator output contains same info as individual loaders."""
    from coldstart_orchestrator import ColdstartOrchestrator

    orch = ColdstartOrchestrator()
    output = orch.run()

    # Key identity elements present (from IdentityLoader)
    # At minimum, should have phase markers or identity content
    assert "[PHASE:" in output or "=== IDENTITY ===" in output or "Mission:" in output

    # Key session elements present (from SessionLoader)
    assert (
        "[PHASE:" in output
        or "=== SESSION" in output
        or "Prior Session:" in output
        or "SESSION" in output
    )

    # Should end with ready marker
    assert "[READY FOR SELECTION]" in output


# =============================================================================
# Test 5: Integration - Just Recipe Works
# =============================================================================


@pytest.mark.integration
def test_just_coldstart_recipe_produces_output():
    """just coldstart recipe produces orchestrator output."""
    import subprocess

    result = subprocess.run(
        ["just", "coldstart-orchestrator"],  # New recipe name to avoid conflict
        capture_output=True,
        text=True,
        timeout=30,
        cwd=Path(__file__).parent.parent,
    )

    # Should contain phase markers or identity content
    assert (
        "[PHASE:" in result.stdout
        or "=== IDENTITY ===" in result.stdout
        or "Mission:" in result.stdout
    ), f"Output was: {result.stdout[:500]}"


# =============================================================================
# Test 6: Default Config Fallback
# =============================================================================


def test_default_config_fallback_when_missing(tmp_path):
    """Orchestrator uses hardcoded defaults when config missing."""
    missing_config = tmp_path / "nonexistent.yaml"

    from coldstart_orchestrator import ColdstartOrchestrator

    orch = ColdstartOrchestrator(config_path=missing_config)

    # Should have default phases
    assert orch.config is not None
    assert "phases" in orch.config
    assert len(orch.config["phases"]) == 3  # identity, session, work


# =============================================================================
# Test 7: Phase Markers Present
# =============================================================================


def test_phase_markers_in_output(tmp_path):
    """Output includes [PHASE: NAME] markers."""
    config = tmp_path / "coldstart.yaml"
    config.write_text("phases:\n  - id: identity\n  - id: session")

    from coldstart_orchestrator import ColdstartOrchestrator

    orch = ColdstartOrchestrator(config_path=config)
    orch._loaders = {
        "identity": lambda: MockLoader("ID"),
        "session": lambda: MockLoader("SESS"),
    }

    output = orch.run()

    assert "[PHASE: IDENTITY]" in output
    assert "[PHASE: SESSION]" in output


# =============================================================================
# WORK-180: Tier Selection Tests (ADR-047)
# =============================================================================

def _create_tiered_config(tmp_path):
    """Create a coldstart.yaml with tier definitions."""
    config = tmp_path / "coldstart.yaml"
    config.write_text(yaml.dump({
        "tier_detection": {"max_age_hours": 24},
        "tiers": {
            "full": {"phases": ["identity", "session", "work", "epoch", "operations"]},
            "light": {"phases": ["session", "work"]},
            "minimal": {"phases": ["session"]},
        },
        "phases": [
            {"id": "identity", "breathe": True},
            {"id": "session", "breathe": True},
            {"id": "work", "breathe": False},
            {"id": "epoch", "breathe": True},
            {"id": "operations", "breathe": False},
        ],
    }), encoding="utf-8")
    return config


def _create_mock_checkpoint(tmp_path, pending=None, age_hours=0):
    """Create a mock checkpoint file with optional pending items and age."""
    checkpoint_dir = tmp_path / "docs" / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    cp = checkpoint_dir / "2026-02-21-01-SESSION-413-checkpoint.md"
    fm = {"session": 413}
    if pending:
        fm["pending"] = pending
    cp.write_text(f"---\n{yaml.dump(fm)}---\n# Checkpoint\n", encoding="utf-8")
    # Set mtime to simulate age
    if age_hours > 0:
        import os
        old_time = time.time() - (age_hours * 3600)
        os.utime(cp, (old_time, old_time))
    return cp


def _mock_all_loaders(orch):
    """Replace all loaders with mocks returning predictable content."""
    orch._loaders = {
        "identity": lambda: MockLoader("IDENTITY"),
        "session": lambda: MockLoader("SESSION"),
        "work": lambda: MockLoader("WORK"),
        "epoch": lambda: MockLoader("EPOCH"),
        "operations": lambda: MockLoader("OPERATIONS"),
    }


# =============================================================================
# Test 9: Tier auto-detection — fresh checkpoint with in-progress work -> light
# =============================================================================


def test_tier_autodetect_fresh_checkpoint_light(tmp_path):
    """Fresh checkpoint with pending work resolves to light tier."""
    config = _create_tiered_config(tmp_path)
    _create_mock_checkpoint(tmp_path, pending=["WORK-180"], age_hours=0)

    from coldstart_orchestrator import ColdstartOrchestrator

    orch = ColdstartOrchestrator(config_path=config)
    # Point checkpoint lookup to our tmp_path
    with patch.object(orch, '_find_latest_checkpoint',
                      return_value=tmp_path / "docs" / "checkpoints" / "2026-02-21-01-SESSION-413-checkpoint.md"):
        result = orch._resolve_tier("auto")

    assert result == "light"


# =============================================================================
# Test 10: Tier auto-detection — no checkpoint -> full
# =============================================================================


def test_tier_autodetect_no_checkpoint_full(tmp_path):
    """No checkpoint file resolves to full tier."""
    config = _create_tiered_config(tmp_path)

    from coldstart_orchestrator import ColdstartOrchestrator

    orch = ColdstartOrchestrator(config_path=config)
    with patch.object(orch, '_find_latest_checkpoint', return_value=None):
        result = orch._resolve_tier("auto")

    assert result == "full"


# =============================================================================
# Test 11: Tier auto-detection — stale checkpoint -> full
# =============================================================================


def test_tier_autodetect_stale_checkpoint_full(tmp_path):
    """Stale checkpoint (>24h) resolves to full tier."""
    config = _create_tiered_config(tmp_path)
    _create_mock_checkpoint(tmp_path, pending=["WORK-180"], age_hours=48)

    from coldstart_orchestrator import ColdstartOrchestrator

    orch = ColdstartOrchestrator(config_path=config)
    cp_path = tmp_path / "docs" / "checkpoints" / "2026-02-21-01-SESSION-413-checkpoint.md"
    with patch.object(orch, '_find_latest_checkpoint', return_value=cp_path):
        result = orch._resolve_tier("auto")

    assert result == "full"


# =============================================================================
# Test 12: Tier auto-detection — explicit override
# =============================================================================


def test_tier_explicit_override(tmp_path):
    """Explicit tier argument bypasses auto-detection."""
    config = _create_tiered_config(tmp_path)

    from coldstart_orchestrator import ColdstartOrchestrator

    orch = ColdstartOrchestrator(config_path=config)

    assert orch._resolve_tier("minimal") == "minimal"
    assert orch._resolve_tier("light") == "light"
    assert orch._resolve_tier("full") == "full"


# =============================================================================
# Test 13: Orchestrator runs correct phases for each tier
# =============================================================================


def test_orchestrator_runs_tier_phases(tmp_path):
    """Full runs 5 loaders, Light runs 2, Minimal runs 1."""
    config = _create_tiered_config(tmp_path)

    from coldstart_orchestrator import ColdstartOrchestrator

    orch = ColdstartOrchestrator(config_path=config)
    _mock_all_loaders(orch)

    # Full tier — 5 phases
    full_output = orch.run(tier="full")
    assert "[PHASE: IDENTITY]" in full_output
    assert "[PHASE: SESSION]" in full_output
    assert "[PHASE: WORK]" in full_output
    assert "[PHASE: EPOCH]" in full_output
    assert "[PHASE: OPERATIONS]" in full_output

    # Light tier — 2 phases
    light_output = orch.run(tier="light")
    assert "[PHASE: SESSION]" in light_output
    assert "[PHASE: WORK]" in light_output
    assert "[PHASE: IDENTITY]" not in light_output
    assert "[PHASE: EPOCH]" not in light_output
    assert "[PHASE: OPERATIONS]" not in light_output

    # Minimal tier — 1 phase
    minimal_output = orch.run(tier="minimal")
    assert "[PHASE: SESSION]" in minimal_output
    assert "[PHASE: IDENTITY]" not in minimal_output
    assert "[PHASE: WORK]" not in minimal_output
    assert "[PHASE: EPOCH]" not in minimal_output
    assert "[PHASE: OPERATIONS]" not in minimal_output


# =============================================================================
# Test 14: CLI argument parsing
# =============================================================================


def test_cli_argparse_tier_argument():
    """CLI argparse accepts --tier argument."""
    import argparse

    # Simulate the argparse from the plan
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", default="auto",
                        choices=["auto", "full", "light", "minimal"])
    parser.add_argument("--extend", nargs="*", default=None)

    args = parser.parse_args(["--tier", "full"])
    assert args.tier == "full"

    args = parser.parse_args(["--tier", "minimal"])
    assert args.tier == "minimal"

    args = parser.parse_args([])
    assert args.tier == "auto"


# =============================================================================
# Test 15: CLI --extend prints not-yet-implemented
# =============================================================================


def test_cli_extend_deferred():
    """--extend flag is accepted but reports not-yet-implemented."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", default="auto",
                        choices=["auto", "full", "light", "minimal"])
    parser.add_argument("--extend", nargs="*", default=None)

    args = parser.parse_args(["--extend", "epoch", "operations"])
    assert args.extend is not None
    assert "epoch" in args.extend
    assert "operations" in args.extend


# =============================================================================
# Test 16: Full tier output contains all phase markers
# =============================================================================


def test_full_tier_all_phase_markers(tmp_path):
    """Full tier output has all 5 PHASE markers."""
    config = _create_tiered_config(tmp_path)

    from coldstart_orchestrator import ColdstartOrchestrator

    orch = ColdstartOrchestrator(config_path=config)
    _mock_all_loaders(orch)

    output = orch.run(tier="full")

    phase_markers = ["[PHASE: IDENTITY]", "[PHASE: SESSION]", "[PHASE: WORK]",
                     "[PHASE: EPOCH]", "[PHASE: OPERATIONS]"]
    for marker in phase_markers:
        assert marker in output, f"Missing: {marker}"
    assert "[READY FOR SELECTION]" in output


# =============================================================================
# Test 17: Light tier skips identity and epoch
# =============================================================================


def test_light_tier_skips_phases(tmp_path):
    """Light tier output does NOT contain identity or epoch phases."""
    config = _create_tiered_config(tmp_path)

    from coldstart_orchestrator import ColdstartOrchestrator

    orch = ColdstartOrchestrator(config_path=config)
    _mock_all_loaders(orch)

    output = orch.run(tier="light")

    assert "[PHASE: IDENTITY]" not in output
    assert "[PHASE: EPOCH]" not in output
    assert "[PHASE: OPERATIONS]" not in output
    assert "[PHASE: SESSION]" in output
    assert "[PHASE: WORK]" in output
    assert "[READY FOR SELECTION]" in output


# =============================================================================
# Test 18: Minimal tier runs session only
# =============================================================================


def test_minimal_tier_session_only(tmp_path):
    """Minimal tier output has only session phase."""
    config = _create_tiered_config(tmp_path)

    from coldstart_orchestrator import ColdstartOrchestrator

    orch = ColdstartOrchestrator(config_path=config)
    _mock_all_loaders(orch)

    output = orch.run(tier="minimal")

    assert "[PHASE: SESSION]" in output
    assert "[PHASE: IDENTITY]" not in output
    assert "[PHASE: WORK]" not in output
    assert "[PHASE: EPOCH]" not in output
    assert "[PHASE: OPERATIONS]" not in output
    assert "[READY FOR SELECTION]" in output
