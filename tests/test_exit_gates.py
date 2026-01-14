# generated: 2025-12-23
# System Auto: last updated on: 2025-12-28T11:07:11
"""Tests for node exit gates (E2-155)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "lib"))


class TestGetExitCriteria:
    """Test loading exit criteria from config."""

    def test_load_exit_criteria_returns_list(self):
        """Config file has exit_criteria for discovery node."""
        from node_cycle import get_exit_criteria

        criteria = get_exit_criteria("discovery")
        assert isinstance(criteria, list)
        assert len(criteria) > 0

    def test_get_exit_criteria_returns_empty_for_backlog(self):
        """Backlog node has no exit criteria."""
        from node_cycle import get_exit_criteria

        criteria = get_exit_criteria("backlog")
        assert criteria == []


class TestDetectNodeExitAttempt:
    """Test detecting node transition attempts."""

    def test_detect_node_exit_from_edit(self):
        """Detects when Edit changes current_node field."""
        from node_cycle import detect_node_exit_attempt

        old_string = "current_node: discovery"
        new_string = "current_node: plan"
        result = detect_node_exit_attempt(old_string, new_string)
        assert result == ("discovery", "plan")

    def test_detect_node_exit_returns_none_for_other_edits(self):
        """Returns None if edit doesn't touch current_node."""
        from node_cycle import detect_node_exit_attempt

        old_string = "title: Old Title"
        new_string = "title: New Title"
        result = detect_node_exit_attempt(old_string, new_string)
        assert result is None

    def test_detect_node_exit_returns_none_for_same_node(self):
        """Returns None if node is unchanged."""
        from node_cycle import detect_node_exit_attempt

        old_string = "current_node: plan"
        new_string = "current_node: plan"
        result = detect_node_exit_attempt(old_string, new_string)
        assert result is None

    def test_detect_node_exit_partial_match(self):
        """Returns None if only one side has current_node."""
        from node_cycle import detect_node_exit_attempt

        old_string = "title: Test"
        new_string = "current_node: plan"
        result = detect_node_exit_attempt(old_string, new_string)
        assert result is None


class TestCheckExitCriteria:
    """Test checking exit criteria for a node."""

    def test_check_exit_criteria_passes_when_all_met(self, tmp_path):
        """Returns empty list when all criteria met."""
        from node_cycle import check_exit_criteria

        # Setup: Create investigation file with complete content
        inv_dir = tmp_path / "docs" / "investigations"
        inv_dir.mkdir(parents=True)
        inv_file = inv_dir / "INVESTIGATION-E2-999-test.md"
        inv_file.write_text(
            "---\nstatus: complete\n---\n\n## Findings\n\n"
            "This is real content that exceeds 50 characters to pass the min_length check."
        )

        failures = check_exit_criteria("discovery", "E2-999", tmp_path)
        assert failures == []

    def test_check_exit_criteria_returns_failures(self, tmp_path):
        """Returns list of unmet criteria when file not found."""
        from node_cycle import check_exit_criteria

        # Setup: No investigation file exists
        failures = check_exit_criteria("discovery", "E2-999", tmp_path)
        assert len(failures) > 0
        assert any("not found" in f.lower() for f in failures)

    def test_check_exit_criteria_status_not_complete(self, tmp_path):
        """Returns failure when status is not complete."""
        from node_cycle import check_exit_criteria

        # Setup: Create investigation file with draft status
        inv_dir = tmp_path / "docs" / "investigations"
        inv_dir.mkdir(parents=True)
        inv_file = inv_dir / "INVESTIGATION-E2-999-test.md"
        inv_file.write_text(
            "---\nstatus: active\n---\n\n## Findings\n\n"
            "This is real content that exceeds 50 characters to pass the min_length check."
        )

        failures = check_exit_criteria("discovery", "E2-999", tmp_path)
        assert len(failures) > 0
        assert any("status" in f.lower() for f in failures)


class TestPlanExitCriteria:
    """Test exit criteria for plan node."""

    def test_plan_exit_criteria_checks_status(self, tmp_path):
        """Plan node checks for approved status."""
        from node_cycle import check_exit_criteria

        # Setup: Create plan file with draft status (new directory structure)
        plan_dir = tmp_path / "docs" / "work" / "active" / "E2-999" / "plans"
        plan_dir.mkdir(parents=True)
        plan_file = plan_dir / "PLAN.md"
        plan_file.write_text("---\nstatus: draft\n---\n## Tests First\ntest content here")

        failures = check_exit_criteria("plan", "E2-999", tmp_path)
        assert any("approved" in f.lower() for f in failures)

    def test_plan_exit_passes_when_approved(self, tmp_path):
        """Plan node passes when status is approved."""
        from node_cycle import check_exit_criteria

        # Setup: Create plan file with approved status (new directory structure)
        plan_dir = tmp_path / "docs" / "work" / "active" / "E2-999" / "plans"
        plan_dir.mkdir(parents=True)
        plan_file = plan_dir / "PLAN.md"
        plan_file.write_text("---\nstatus: approved\n---\n## Tests First\ntest content here")

        failures = check_exit_criteria("plan", "E2-999", tmp_path)
        assert failures == []


class TestBuildExitGateWarning:
    """Test building user-friendly warning messages."""

    def test_build_exit_gate_warning(self):
        """Builds user-friendly warning message."""
        from node_cycle import build_exit_gate_warning

        failures = ["Investigation status not complete", "Findings section empty"]
        warning = build_exit_gate_warning("discovery", "plan", failures)

        assert "discovery" in warning
        assert "plan" in warning
        assert "Investigation status" in warning
        assert "Findings section" in warning

    def test_build_exit_gate_warning_single_failure(self):
        """Handles single failure message."""
        from node_cycle import build_exit_gate_warning

        failures = ["Plan status not approved"]
        warning = build_exit_gate_warning("plan", "implement", failures)

        assert "plan" in warning
        assert "implement" in warning
        assert "Plan status" in warning


class TestBacklogExitCriteria:
    """Test that backlog node has no exit criteria."""

    def test_backlog_has_no_exit_criteria(self):
        """Backlog node should allow free transition."""
        from node_cycle import get_exit_criteria

        criteria = get_exit_criteria("backlog")
        assert criteria == []

    def test_implement_has_no_exit_criteria(self):
        """Implement node has no exit criteria (DoD via /close)."""
        from node_cycle import get_exit_criteria

        criteria = get_exit_criteria("implement")
        assert criteria == []
