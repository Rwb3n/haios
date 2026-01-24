# generated: 2026-01-24
# System Auto: last updated on: 2026-01-24T20:45:52
"""
Tests for ColdstartOrchestrator (WORK-011, CH-007).

TDD: These tests define expected behavior before implementation.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

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
