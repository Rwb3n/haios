# generated: 2026-02-16
# WORK-154: Epoch Transition Validation and Queue Config Sync
"""
Tests for epoch_validator.py (WORK-154).

Validates:
- Queue config vs active_arcs consistency
- EPOCH.md status vs WORK.md status drift detection
- Coldstart integration
- Multi-item cells (Critique A1)
- Completed section exclusion (Critique A6)
- Disk-loading path (Critique A10)
"""
import sys
from pathlib import Path
import pytest

# Ensure lib/ is importable
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))


# ---------------------------------------------------------------------------
# Test 1: Queue config validates against active arcs — no drift
# ---------------------------------------------------------------------------
def test_validate_queue_config_no_drift():
    """Queue names that match active_arcs produce no warnings."""
    from epoch_validator import EpochValidator

    haios = {"epoch": {"active_arcs": ["engine-functions", "composability", "infrastructure"]}}
    queues = {
        "queues": {
            "engine-functions": {"type": "fifo", "items": []},
            "composability": {"type": "priority", "items": []},
            "infrastructure": {"type": "batch", "items": []},
        }
    }
    validator = EpochValidator(haios_config=haios, queue_config=queues)
    result = validator.validate_queue_config()
    assert result["warnings"] == []


# ---------------------------------------------------------------------------
# Test 2: Queue config references stale arc
# ---------------------------------------------------------------------------
def test_validate_queue_config_stale_arc():
    """Queue referencing arc not in active_arcs produces warning."""
    from epoch_validator import EpochValidator

    haios = {"epoch": {"active_arcs": ["infrastructure"]}}
    queues = {"queues": {"old-arc": {"type": "fifo", "items": ["WORK-001"]}}}
    validator = EpochValidator(haios_config=haios, queue_config=queues)
    result = validator.validate_queue_config()
    assert len(result["warnings"]) == 1
    assert "old-arc" in result["warnings"][0]


# ---------------------------------------------------------------------------
# Test 3: EPOCH.md status drift detection
# ---------------------------------------------------------------------------
def test_validate_epoch_status_drift():
    """Work item marked complete in WORK.md but shown as Planning in EPOCH.md."""
    from epoch_validator import EpochValidator

    epoch_content = (
        "### Arc 3: infrastructure\n"
        "\n"
        "| CH-ID | Title | Work Items | Status |\n"
        "|-------|-------|------------|--------|\n"
        "| CH-049 | BugBatch | WORK-153 | Planning |\n"
    )
    work_statuses = {"WORK-153": "complete"}
    validator = EpochValidator(epoch_content=epoch_content, work_statuses=work_statuses)
    result = validator.validate_epoch_status()
    assert len(result["drift"]) == 1
    # WORK-272: message now uses chapter-level format
    assert "CH-049" in result["drift"][0]
    assert "WORK-153" in result["drift"][0]


# ---------------------------------------------------------------------------
# Test 4: EPOCH.md status no drift
# ---------------------------------------------------------------------------
def test_validate_epoch_status_no_drift():
    """Work items with active status and Planning in EPOCH.md produce no drift."""
    from epoch_validator import EpochValidator

    epoch_content = (
        "### Arc 3: infrastructure\n"
        "\n"
        "| CH-ID | Title | Work Items | Status |\n"
        "|-------|-------|------------|--------|\n"
        "| CH-050 | EpochTransition | WORK-154 | Planning |\n"
    )
    work_statuses = {"WORK-154": "active"}
    validator = EpochValidator(epoch_content=epoch_content, work_statuses=work_statuses)
    result = validator.validate_epoch_status()
    assert result["drift"] == []


# ---------------------------------------------------------------------------
# Test 5: Missing active arc in queue config
# ---------------------------------------------------------------------------
def test_validate_queue_config_missing_arc():
    """Active arc with no matching queue produces info (not warning)."""
    from epoch_validator import EpochValidator

    haios = {"epoch": {"active_arcs": ["engine-functions", "composability"]}}
    queues = {"queues": {"engine-functions": {"type": "fifo", "items": []}}}
    validator = EpochValidator(haios_config=haios, queue_config=queues)
    result = validator.validate_queue_config()
    assert len(result["info"]) == 1
    assert "composability" in result["info"][0]


# ---------------------------------------------------------------------------
# Test 6: Coldstart integration — validation phase runs
# ---------------------------------------------------------------------------
def test_coldstart_runs_epoch_validation(monkeypatch):
    """ColdstartOrchestrator includes epoch validation output when drift exists."""
    sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
    from coldstart_orchestrator import ColdstartOrchestrator

    # Mock all loaders to return minimal content
    class MockLoader:
        def load(self):
            return "(mock)"

    # Mock EpochValidator to return a warning
    class MockEpochValidator:
        def __init__(self, **kwargs):
            pass

        def validate(self):
            return "DRIFT: WORK-999 is 'complete' but shown as 'Planning'"

    # Monkeypatch the loaders and validator
    orch = ColdstartOrchestrator.__new__(ColdstartOrchestrator)
    orch.config = {"phases": []}  # Skip loader phases
    orch._loaders = {}

    # Monkeypatch the epoch_validator import inside _run_epoch_validation
    import epoch_validator as ev_mod

    monkeypatch.setattr(ev_mod, "EpochValidator", MockEpochValidator)

    from unittest.mock import patch
    with patch.object(orch, '_check_for_orphans', return_value=None):
        output = orch.run(tier="full")  # Explicit full tier to ensure validation runs
    assert "[PHASE: VALIDATION]" in output
    assert "WORK-999" in output


# ---------------------------------------------------------------------------
# Test 7: Default queue excluded from stale arc check
# ---------------------------------------------------------------------------
def test_default_queue_excluded_from_arc_check():
    """'default' queue is not matched against active_arcs (structural queue)."""
    from epoch_validator import EpochValidator

    haios = {"epoch": {"active_arcs": ["infrastructure"]}}
    queues = {
        "queues": {
            "default": {"type": "priority", "items": "auto"},
            "infrastructure": {"type": "batch", "items": []},
        }
    }
    validator = EpochValidator(haios_config=haios, queue_config=queues)
    result = validator.validate_queue_config()
    assert result["warnings"] == []


# ---------------------------------------------------------------------------
# Test 8: Multi-work-item cell in EPOCH.md (Critique A1)
# ---------------------------------------------------------------------------
def test_validate_epoch_status_multi_item_cell():
    """EPOCH.md cell with 'WORK-152, WORK-155' extracts both items."""
    from epoch_validator import EpochValidator

    epoch_content = (
        "### Arc 2: composability\n"
        "\n"
        "| CH-ID | Title | Work Items | Status |\n"
        "|-------|-------|------------|--------|\n"
        "| CH-047 | TemplateComposability | WORK-152, WORK-155 | Planning |\n"
    )
    work_statuses = {"WORK-152": "complete", "WORK-155": "active"}
    validator = EpochValidator(epoch_content=epoch_content, work_statuses=work_statuses)
    result = validator.validate_epoch_status()
    # WORK-272 fix: chapter-level drift — not all items complete, so NO drift
    # (WORK-155 is still active, chapter is correctly "Planning")
    assert result["drift"] == []


# ---------------------------------------------------------------------------
# Test 9: Completed section excluded from drift check (Critique A6)
# ---------------------------------------------------------------------------
def test_validate_epoch_status_completed_section_excluded():
    """Work items in 'Completed' section of EPOCH.md are not flagged as drift."""
    from epoch_validator import EpochValidator

    epoch_content = (
        "### Arc 3: infrastructure\n"
        "\n"
        "| CH-ID | Title | Work Items | Status |\n"
        "|-------|-------|------------|--------|\n"
        "| CH-049 | BugBatch | WORK-153 | Planning |\n"
        "\n"
        "### Completed (carry-forward satisfied)\n"
        "\n"
        "| ID | Title | Notes |\n"
        "|----|----|-------|\n"
        "| WORK-093 | Lifecycle Asset Types | Closed |\n"
    )
    work_statuses = {"WORK-153": "complete", "WORK-093": "complete"}
    validator = EpochValidator(epoch_content=epoch_content, work_statuses=work_statuses)
    result = validator.validate_epoch_status()
    # WORK-153 should drift (in active arc table, status mismatch)
    assert any("WORK-153" in d for d in result["drift"])
    # WORK-093 should NOT drift (in Completed section)
    assert not any("WORK-093" in d for d in result["drift"])


# ---------------------------------------------------------------------------
# Test 10: Disk-loading path works (Critique A10)
# ---------------------------------------------------------------------------
def test_validate_disk_loading_path(tmp_path):
    """EpochValidator loads config from disk when no injection provided."""
    from epoch_validator import EpochValidator

    # Create minimal haios.yaml
    config_dir = tmp_path / ".claude" / "haios" / "config"
    config_dir.mkdir(parents=True)
    haios_yaml = config_dir / "haios.yaml"
    haios_yaml.write_text(
        "epoch:\n"
        "  current: E2.7\n"
        "  active_arcs:\n"
        "    - infra\n"
        "  epoch_file: .claude/haios/epochs/E2_7/EPOCH.md\n",
        encoding="utf-8",
    )
    queues_yaml = config_dir / "work_queues.yaml"
    queues_yaml.write_text(
        "queues:\n"
        "  infra:\n"
        "    type: fifo\n"
        "    items: []\n",
        encoding="utf-8",
    )
    # Create minimal EPOCH.md
    epoch_dir = tmp_path / ".claude" / "haios" / "epochs" / "E2_7"
    epoch_dir.mkdir(parents=True)
    (epoch_dir / "EPOCH.md").write_text(
        "### Arc 1: infra\n"
        "\n"
        "| CH-ID | Title | Work Items | Status |\n"
        "|-------|-------|------------|--------|\n"
        "| CH-001 | Test | WORK-001 | Planning |\n",
        encoding="utf-8",
    )
    # Create work item
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-001"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text(
        "---\nid: WORK-001\nstatus: active\n---\n# WORK-001\n",
        encoding="utf-8",
    )

    validator = EpochValidator(base_path=tmp_path)
    result = validator.validate()
    assert isinstance(result, str)
    # No drift expected (WORK-001 is active, EPOCH.md says Planning)
    assert "DRIFT" not in result


# ---------------------------------------------------------------------------
# Test 11: Mixed chapter — some complete, some active — no drift (WORK-272)
# ---------------------------------------------------------------------------
def test_validate_epoch_status_no_drift_mixed_chapter():
    """Chapter with mix of complete and active work items produces no drift."""
    from epoch_validator import EpochValidator

    epoch_content = (
        "### Arc 1: call\n"
        "\n"
        "| CH-ID | Title | Work Items | Status |\n"
        "|-------|-------|------------|--------|\n"
        "| CH-059 | CeremonyAutomation | WORK-160, WORK-167, WORK-170 | In Progress |\n"
    )
    work_statuses = {
        "WORK-160": "complete",
        "WORK-167": "complete",
        "WORK-170": "active",
    }
    validator = EpochValidator(epoch_content=epoch_content, work_statuses=work_statuses)
    result = validator.validate_epoch_status()
    # Chapter correctly "In Progress" — not all items complete
    assert result["drift"] == []


# ---------------------------------------------------------------------------
# Test 12: All chapter items complete but chapter not promoted — drift (WORK-272)
# ---------------------------------------------------------------------------
def test_validate_epoch_status_drift_all_complete():
    """Chapter where ALL work items are complete but status is not produces drift."""
    from epoch_validator import EpochValidator

    epoch_content = (
        "### Arc 1: infrastructure\n"
        "\n"
        "| CH-ID | Title | Work Items | Status |\n"
        "|-------|-------|------------|--------|\n"
        "| CH-065 | BugBatch | WORK-200, WORK-201 | Active |\n"
    )
    work_statuses = {"WORK-200": "complete", "WORK-201": "complete"}
    validator = EpochValidator(epoch_content=epoch_content, work_statuses=work_statuses)
    result = validator.validate_epoch_status()
    assert len(result["drift"]) == 1
    assert "CH-065" in result["drift"][0]
    assert "WORK-200" in result["drift"][0]
    assert "WORK-201" in result["drift"][0]


# ---------------------------------------------------------------------------
# Test 13: Chapter already complete — no drift (WORK-272)
# ---------------------------------------------------------------------------
def test_validate_epoch_status_no_drift_chapter_complete():
    """Chapter marked Complete with all complete items produces no drift."""
    from epoch_validator import EpochValidator

    epoch_content = (
        "### Arc 1: infrastructure\n"
        "\n"
        "| CH-ID | Title | Work Items | Status |\n"
        "|-------|-------|------------|--------|\n"
        "| CH-065 | BugBatch | WORK-200, WORK-201 | Complete |\n"
    )
    work_statuses = {"WORK-200": "complete", "WORK-201": "complete"}
    validator = EpochValidator(epoch_content=epoch_content, work_statuses=work_statuses)
    result = validator.validate_epoch_status()
    assert result["drift"] == []


# ---------------------------------------------------------------------------
# Test 14: Legacy fallback — all complete, chapter stale — drift (WORK-272)
# ---------------------------------------------------------------------------
def test_validate_epoch_status_drift_legacy_all_complete():
    """Legacy EPOCH.md path: all work items complete but chapter stale produces drift."""
    from epoch_validator import EpochValidator

    epoch_content = (
        "### Arc 2: composability\n"
        "\n"
        "| CH-ID | Title | Work Items | Status |\n"
        "|-------|-------|------------|--------|\n"
        "| CH-047 | Templates | WORK-152, WORK-155 | Planning |\n"
    )
    work_statuses = {"WORK-152": "complete", "WORK-155": "complete"}
    validator = EpochValidator(epoch_content=epoch_content, work_statuses=work_statuses)
    result = validator.validate_epoch_status()
    assert len(result["drift"]) == 1
    assert "CH-047" in result["drift"][0]
