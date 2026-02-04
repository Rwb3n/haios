# generated: 2026-01-04
# System Auto: last updated on: 2026-02-04T22:28:13
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


# =============================================================================
# WORK-084: Lifecycle Signatures (REQ-LIFECYCLE-001)
# =============================================================================


class TestLifecycleOutputDataclasses:
    """Tests for LifecycleOutput type hierarchy (WORK-084)."""

    def test_lifecycle_output_base_dataclass(self):
        """LifecycleOutput has required fields."""
        from cycle_runner import LifecycleOutput
        from datetime import datetime

        output = LifecycleOutput(
            lifecycle="investigation",
            work_id="INV-001",
            timestamp=datetime.now(),
            status="success"
        )
        assert output.lifecycle == "investigation"
        assert output.work_id == "INV-001"
        assert output.status == "success"

    def test_findings_output_type(self):
        """Findings extends LifecycleOutput with investigation-specific fields."""
        from cycle_runner import Findings
        from datetime import datetime

        findings = Findings(
            lifecycle="investigation",
            work_id="INV-001",
            timestamp=datetime.now(),
            status="success",
            question="What causes the bug?",
            conclusions=["Root cause is X"],
            evidence=["Log file shows Y"],
            open_questions=[]
        )
        assert findings.question == "What causes the bug?"
        assert len(findings.conclusions) == 1

    def test_specification_output_type(self):
        """Specification extends LifecycleOutput with design-specific fields."""
        from cycle_runner import Specification
        from datetime import datetime

        spec = Specification(
            lifecycle="design",
            work_id="WORK-084",
            timestamp=datetime.now(),
            status="success",
            requirements=["REQ-LIFECYCLE-001"],
            design_decisions=["Use dataclasses"],
            interfaces={"run": "work_id, lifecycle -> LifecycleOutput"}
        )
        assert "REQ-LIFECYCLE-001" in spec.requirements
        assert "run" in spec.interfaces


class TestCycleRunnerRun:
    """Tests for CycleRunner.run() method (WORK-084)."""

    def test_run_returns_lifecycle_output(self):
        """CycleRunner.run() returns LifecycleOutput subclass."""
        from cycle_runner import CycleRunner, LifecycleOutput
        from governance_layer import GovernanceLayer

        runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
        output = runner.run(work_id="WORK-084", lifecycle="design")
        assert isinstance(output, LifecycleOutput)
        assert output.work_id == "WORK-084"
        assert output.lifecycle == "design"

    def test_run_does_not_auto_chain(self):
        """CycleRunner.run() returns output, does NOT trigger next lifecycle."""
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer

        runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)

        # Mock any chaining mechanism
        with patch.object(runner, '_emit_phase_entered') as mock_emit:
            output = runner.run(work_id="WORK-084", lifecycle="design")
            # Should emit for current lifecycle phases only, not next lifecycle
            # Specifically, should NOT emit for "implementation" phases
            for call in mock_emit.call_args_list:
                assert "implementation" not in str(call)

    def test_existing_get_cycle_phases_unchanged(self):
        """Existing get_cycle_phases behavior unchanged after adding run()."""
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer

        runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
        phases = runner.get_cycle_phases("implementation-cycle")
        assert phases == ["PLAN", "DO", "CHECK", "DONE", "CHAIN"]


# =============================================================================
# WORK-085: Pause Semantics (REQ-LIFECYCLE-002, S27 Breath Model)
# =============================================================================


class TestPauseSemantics:
    """Tests for PAUSE_PHASES constant (WORK-085)."""

    def test_pause_phases_constant_exists(self):
        """PAUSE_PHASES constant defines pause phases for all 5 lifecycles."""
        from cycle_runner import PAUSE_PHASES

        assert "investigation" in PAUSE_PHASES
        assert "design" in PAUSE_PHASES
        assert "implementation" in PAUSE_PHASES
        assert "validation" in PAUSE_PHASES
        assert "triage" in PAUSE_PHASES

    def test_pause_phases_maps_to_exhale_phases(self):
        """Pause phases match S27 exhale phases (CONCLUDE, COMPLETE, DONE, REPORT, COMMIT)."""
        from cycle_runner import PAUSE_PHASES

        assert "CONCLUDE" in PAUSE_PHASES["investigation"]
        assert "COMPLETE" in PAUSE_PHASES["design"]
        assert "DONE" in PAUSE_PHASES["implementation"]
        assert "REPORT" in PAUSE_PHASES["validation"]
        assert "COMMIT" in PAUSE_PHASES["triage"]

    def test_all_lifecycles_have_defined_pause_points(self):
        """Every lifecycle in PAUSE_PHASES has at least one pause phase defined."""
        from cycle_runner import PAUSE_PHASES

        for lifecycle, phases in PAUSE_PHASES.items():
            assert len(phases) > 0, f"Lifecycle {lifecycle} has no pause phases"

    def test_existing_cycle_phases_unchanged(self):
        """CYCLE_PHASES constant unchanged after adding PAUSE_PHASES."""
        from cycle_runner import CYCLE_PHASES

        # Verify existing cycles still have same phases
        assert CYCLE_PHASES["implementation-cycle"] == ["PLAN", "DO", "CHECK", "DONE", "CHAIN"]
        # WORK-098: Updated to match L4 REQ-FLOW-002 (Session 304)
        assert CYCLE_PHASES["investigation-cycle"] == ["EXPLORE", "HYPOTHESIZE", "VALIDATE", "CONCLUDE", "CHAIN"]


# =============================================================================
# WORK-088: Phase Template Contracts (REQ-TEMPLATE-001)
# =============================================================================


class TestLoadPhaseTemplate:
    """Tests for _load_phase_template method (WORK-088)."""

    def test_explore_template_has_input_contract(self):
        """EXPLORE template frontmatter includes input_contract field."""
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer

        runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
        template = runner._load_phase_template("EXPLORE")
        assert "input_contract" in template
        assert len(template["input_contract"]) > 0

    def test_explore_template_has_output_contract(self):
        """EXPLORE template frontmatter includes output_contract field."""
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer

        runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
        template = runner._load_phase_template("EXPLORE")
        assert "output_contract" in template
        assert len(template["output_contract"]) > 0


class TestValidatePhaseInput:
    """Tests for validate_phase_input method (WORK-088)."""

    def test_validate_phase_input_success(self):
        """validate_phase_input returns allowed when contract satisfied."""
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer, GateResult

        runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
        result = runner.validate_phase_input("EXPLORE", "WORK-088")
        assert result.allowed is True
        assert isinstance(result, GateResult)

    def test_validate_phase_input_missing_field_blocks(self):
        """validate_phase_input returns blocked when required field missing."""
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer

        runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)

        # Mock _check_work_has_field to return False for specific field
        with patch.object(runner, '_check_work_has_field', return_value=False):
            result = runner.validate_phase_input("EXPLORE", "WORK-EMPTY")
            assert result.allowed is False
            assert "Missing required input:" in result.reason


class TestValidatePhaseOutput:
    """Tests for validate_phase_output method (WORK-088)."""

    def test_validate_phase_output_returns_gate_result(self):
        """validate_phase_output returns GateResult."""
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer, GateResult

        runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
        result = runner.validate_phase_output("EXPLORE", "WORK-088")
        assert isinstance(result, GateResult)


class TestBackwardCompatibility:
    """Tests for backward compatibility (WORK-088)."""

    def test_check_phase_entry_unchanged_for_cycles_without_templates(self):
        """Existing check_phase_entry behavior unchanged for cycles without templates."""
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer

        runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
        # implementation-cycle doesn't have templates yet
        result = runner.check_phase_entry("implementation-cycle", "PLAN", "WORK-088")
        assert result.allowed is True  # MVP behavior preserved
