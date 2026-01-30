# generated: 2026-01-30
# System Auto: last updated on: 2026-01-30T17:43:06
"""
Tests for PipelineOrchestrator Module (WORK-033, CH-006)

TDD tests per plan - written BEFORE implementation.
All tests should FAIL initially (RED phase).
"""
import pytest
import sys
from pathlib import Path

# Add modules path for imports
modules_path = Path(__file__).parent.parent / ".claude" / "haios" / "modules"
if str(modules_path) not in sys.path:
    sys.path.insert(0, str(modules_path))


# =============================================================================
# Test 1: State Machine Initial State
# =============================================================================

def test_orchestrator_starts_in_idle_state(tmp_path):
    """Orchestrator initializes in IDLE state."""
    from pipeline_orchestrator import PipelineOrchestrator, PipelineState

    config = {"corpus": {"sources": [{"path": "docs"}]}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)
    assert orchestrator.state == PipelineState.IDLE


# =============================================================================
# Test 2: Ingest Stage Transitions State
# =============================================================================

def test_ingest_transitions_to_planning(tmp_path):
    """ingest() moves state from IDLE to PLANNING."""
    from pipeline_orchestrator import PipelineOrchestrator, PipelineState

    # Setup: Create test corpus with TRD-style requirement
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "TRD-test.md").write_text("| R0 | Test requirement | MUST |")

    config = {"corpus": {"sources": [{"path": "docs"}]}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)

    req_set = orchestrator.ingest()

    assert orchestrator.state == PipelineState.PLANNING
    assert len(req_set.requirements) >= 1


# =============================================================================
# Test 3: Plan Stage Transitions State
# =============================================================================

def test_plan_transitions_to_complete(tmp_path):
    """plan() moves state from PLANNING to COMPLETE."""
    from pipeline_orchestrator import PipelineOrchestrator, PipelineState

    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "TRD-test.md").write_text("| R0 | Test requirement | MUST |")

    config = {"corpus": {"sources": [{"path": "docs"}]}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)
    orchestrator.ingest()  # Move to PLANNING

    work_plan = orchestrator.plan()

    assert orchestrator.state == PipelineState.COMPLETE
    assert work_plan is not None


# =============================================================================
# Test 4: Invalid State Transition Raises
# =============================================================================

def test_plan_before_ingest_raises(tmp_path):
    """plan() raises if called before ingest()."""
    from pipeline_orchestrator import PipelineOrchestrator, InvalidStateError

    config = {"corpus": {"sources": []}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)

    with pytest.raises(InvalidStateError):
        orchestrator.plan()  # Can't plan from IDLE


# =============================================================================
# Test 5: Run Executes Full Pipeline
# =============================================================================

def test_run_executes_full_pipeline(tmp_path):
    """run() executes INGEST -> PLAN and returns PipelineResult."""
    from pipeline_orchestrator import PipelineOrchestrator, PipelineState

    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "TRD-test.md").write_text("| R0 | Test requirement | MUST |")

    config = {"corpus": {"sources": [{"path": "docs"}]}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)

    result = orchestrator.run()

    assert orchestrator.state == PipelineState.COMPLETE
    assert result.work_plan is not None
    assert result.requirement_set is not None


# =============================================================================
# Test 6: Empty Corpus Handled Gracefully
# =============================================================================

def test_empty_corpus_returns_empty_results(tmp_path):
    """Empty corpus produces empty RequirementSet and WorkPlan."""
    from pipeline_orchestrator import PipelineOrchestrator

    (tmp_path / "docs").mkdir()  # Empty directory

    config = {"corpus": {"sources": [{"path": "docs"}]}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)

    result = orchestrator.run()

    assert len(result.requirement_set.requirements) == 0
    assert len(result.work_plan.work_items) == 0


# =============================================================================
# Test 7: Config From YAML File
# =============================================================================

def test_orchestrator_accepts_yaml_path(tmp_path):
    """Orchestrator accepts path to YAML config file."""
    from pipeline_orchestrator import PipelineOrchestrator, PipelineState

    (tmp_path / "docs").mkdir()
    config_file = tmp_path / "corpus.yaml"
    config_file.write_text("corpus:\n  sources:\n    - path: docs")

    orchestrator = PipelineOrchestrator(config_file, base_path=tmp_path)

    assert orchestrator.state == PipelineState.IDLE


# =============================================================================
# Test 8: State History Tracked
# =============================================================================

def test_state_history_recorded(tmp_path):
    """State transitions are recorded in history."""
    from pipeline_orchestrator import PipelineOrchestrator, PipelineState

    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "test.md").write_text("| R0 | Test | MUST |")

    config = {"corpus": {"sources": [{"path": "docs"}]}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)
    orchestrator.run()

    assert PipelineState.IDLE in orchestrator.state_history
    assert PipelineState.INGESTING in orchestrator.state_history
    assert PipelineState.PLANNING in orchestrator.state_history
    assert PipelineState.COMPLETE in orchestrator.state_history


# =============================================================================
# Test 9: Requirements Stored After Ingest
# =============================================================================

def test_requirements_accessible_after_ingest(tmp_path):
    """RequirementSet is accessible via property after ingest."""
    from pipeline_orchestrator import PipelineOrchestrator

    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "TRD-test.md").write_text("| R0 | Test | MUST |")

    config = {"corpus": {"sources": [{"path": "docs"}]}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)
    orchestrator.ingest()

    assert orchestrator.requirement_set is not None
    assert len(orchestrator.requirement_set.requirements) >= 1


# =============================================================================
# Test 10: WorkPlan Stored After Plan
# =============================================================================

def test_work_plan_accessible_after_plan(tmp_path):
    """WorkPlan is accessible via property after plan."""
    from pipeline_orchestrator import PipelineOrchestrator

    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "TRD-test.md").write_text("| R0 | Test | MUST |")

    config = {"corpus": {"sources": [{"path": "docs"}]}}
    orchestrator = PipelineOrchestrator(config, base_path=tmp_path)
    orchestrator.run()

    assert orchestrator.work_plan is not None
