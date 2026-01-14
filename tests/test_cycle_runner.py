# generated: 2026-01-04
# System Auto: last updated on: 2026-01-04T20:52:33
"""Tests for CycleRunner module (E2-255).

Tests phase gate validation and cycle phase lookup functionality.
"""
import pytest
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path

# Add modules to path
_modules_path = Path(__file__).parent.parent / ".claude" / "haios" / "modules"
if str(_modules_path) not in sys.path:
    sys.path.insert(0, str(_modules_path))

_lib_path = Path(__file__).parent.parent / ".claude" / "lib"
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))


class TestCycleRunnerInstantiation:
    """Test CycleRunner initialization."""

    def test_cycle_runner_requires_governance_and_work_engine(self):
        """Test that CycleRunner stores governance and work_engine."""
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer

        governance = GovernanceLayer()
        runner = CycleRunner(governance=governance, work_engine=None)
        assert runner._governance is governance
        assert runner._work_engine is None


class TestGetCyclePhases:
    """Test get_cycle_phases method."""

    def test_get_cycle_phases_implementation_cycle(self):
        """Test phases for implementation-cycle."""
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer

        runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
        phases = runner.get_cycle_phases("implementation-cycle")
        assert phases == ["PLAN", "DO", "CHECK", "DONE", "CHAIN"]

    def test_get_cycle_phases_unknown_returns_empty(self):
        """Test unknown cycle returns empty list."""
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer

        runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
        phases = runner.get_cycle_phases("nonexistent-cycle")
        assert phases == []


class TestCheckPhaseEntry:
    """Test check_phase_entry method."""

    def test_check_phase_entry_allowed(self):
        """Test that phase entry returns allowed GateResult."""
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer, GateResult

        runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
        result = runner.check_phase_entry("implementation-cycle", "PLAN", "E2-255")
        assert result.allowed is True
        assert isinstance(result, GateResult)


class TestCheckPhaseExit:
    """Test check_phase_exit method."""

    def test_check_phase_exit_with_criteria(self):
        """Test that phase exit returns GateResult (may be blocked or allowed)."""
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer, GateResult

        runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
        result = runner.check_phase_exit("investigation-cycle", "CONCLUDE", "INV-001")
        assert isinstance(result, GateResult)


class TestCycleResult:
    """Test CycleResult dataclass."""

    def test_cycle_result_dataclass(self):
        """Test CycleResult fields."""
        from cycle_runner import CycleResult

        result = CycleResult(
            cycle_id="implementation-cycle",
            final_phase="DONE",
            outcome="completed",
            gate_results=[],
            next_cycle=None,
        )
        assert result.cycle_id == "implementation-cycle"
        assert result.outcome == "completed"
        assert result.final_phase == "DONE"
        assert result.gate_results == []
        assert result.next_cycle is None


class TestLoadCycleDefinitions:
    """Test _load_cycle_definitions method."""

    def test_load_cycle_definitions(self):
        """Test that cycle definitions load from config."""
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer

        runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
        cycles = runner._load_cycle_definitions()
        # cycles.yaml should have nodes section
        assert "nodes" in cycles
        assert "discovery" in cycles["nodes"]


class TestEventEmission:
    """Test event emission."""

    def test_emit_phase_entered_event(self):
        """Test that phase entry emits event via log_phase_transition."""
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer

        with patch("cycle_runner.log_phase_transition") as mock_log:
            runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
            runner._emit_phase_entered("implementation-cycle", "DO", "E2-255")
            mock_log.assert_called_once_with("DO", "E2-255", "Hephaestus")


# =============================================================================
# E2-263: Scaffold Command Tests
# =============================================================================


class TestScaffoldCommand:
    """Tests for scaffold command method (E2-263)."""

    def test_build_scaffold_command_replaces_placeholders(self):
        """build_scaffold_command replaces {id} and {title} placeholders."""
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer

        runner = CycleRunner(governance=GovernanceLayer())
        result = runner.build_scaffold_command(
            template="/new-plan {id} {title}",
            work_id="E2-263",
            title="Test Title"
        )
        assert result == "/new-plan E2-263 Test Title"

    def test_build_scaffold_command_passthrough(self):
        """build_scaffold_command passes through template without placeholders."""
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer

        runner = CycleRunner(governance=GovernanceLayer())
        result = runner.build_scaffold_command(
            template="just validate",
            work_id="E2-263",
            title="Test"
        )
        assert result == "just validate"
