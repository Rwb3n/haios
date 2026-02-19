"""Tests for retro_scale.py — retro-cycle Phase 0 scale assessment (WORK-171)."""
import json
import sys
from pathlib import Path

import pytest

# Ensure lib/ is on path
lib_dir = Path(__file__).parent.parent / ".claude" / "haios" / "lib"
if str(lib_dir) not in sys.path:
    sys.path.insert(0, str(lib_dir))

import retro_scale  # Required for monkeypatch target "retro_scale._get_changed_files"
from retro_scale import assess_scale


class TestAssessScaleTrivial:
    """Work items meeting all 4 trivial conditions."""

    def test_trivial_small_work(self, tmp_path):
        """Work with <=2 files changed, no plan, no tests, no events -> trivial."""
        work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
        work_dir.mkdir(parents=True)
        (work_dir / "WORK.md").write_text("---\nid: WORK-999\n---\n")
        # No plans dir, no governance events
        events_dir = tmp_path / ".claude" / "haios"
        events_dir.mkdir(parents=True)
        (events_dir / "governance-events.jsonl").write_text("")
        result = assess_scale("WORK-999", project_root=tmp_path)
        assert result == "trivial"


class TestAssessScaleSubstantial:
    """Work items failing at least one trivial condition."""

    def test_substantial_with_plan(self, tmp_path):
        """Work with a plan file -> substantial."""
        work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
        plans_dir = work_dir / "plans"
        plans_dir.mkdir(parents=True)
        (plans_dir / "PLAN.md").write_text("---\nstatus: approved\n---\n")
        events_dir = tmp_path / ".claude" / "haios"
        events_dir.mkdir(parents=True)
        (events_dir / "governance-events.jsonl").write_text("")
        result = assess_scale("WORK-999", project_root=tmp_path)
        assert result == "substantial"

    def test_substantial_with_governance_events(self, tmp_path):
        """Work with CyclePhaseEntered events for work_id -> substantial."""
        work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
        work_dir.mkdir(parents=True)
        (work_dir / "WORK.md").write_text("---\nid: WORK-999\n---\n")
        events_dir = tmp_path / ".claude" / "haios"
        events_dir.mkdir(parents=True)
        event = {"type": "CyclePhaseEntered", "work_id": "WORK-999", "phase": "PLAN"}
        (events_dir / "governance-events.jsonl").write_text(json.dumps(event) + "\n")
        result = assess_scale("WORK-999", project_root=tmp_path)
        assert result == "substantial"

    def test_substantial_with_test_changes(self, tmp_path, monkeypatch):
        """Git diff showing test file changes -> substantial."""
        work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
        work_dir.mkdir(parents=True)
        (work_dir / "WORK.md").write_text("---\nid: WORK-999\n---\n")
        events_dir = tmp_path / ".claude" / "haios"
        events_dir.mkdir(parents=True)
        (events_dir / "governance-events.jsonl").write_text("")
        monkeypatch.setattr(
            retro_scale, "_get_changed_files",
            lambda root: ["tests/test_foo.py", "lib/foo.py"],
        )
        result = assess_scale("WORK-999", project_root=tmp_path)
        assert result == "substantial"

    def test_substantial_many_files(self, tmp_path, monkeypatch):
        """Git diff showing >2 files -> substantial."""
        work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
        work_dir.mkdir(parents=True)
        (work_dir / "WORK.md").write_text("---\nid: WORK-999\n---\n")
        events_dir = tmp_path / ".claude" / "haios"
        events_dir.mkdir(parents=True)
        (events_dir / "governance-events.jsonl").write_text("")
        monkeypatch.setattr(
            retro_scale, "_get_changed_files",
            lambda root: ["a.py", "b.py", "c.py"],
        )
        result = assess_scale("WORK-999", project_root=tmp_path)
        assert result == "substantial"


class TestAssessScaleGracefulDegradation:
    """Error handling and fail-safe behavior."""

    def test_missing_work_dir_still_evaluates_predicate(self, tmp_path):
        """Missing work dir with no plan/events/tests -> trivial (predicate passes).

        The function evaluates the 4 conditions, not the existence of the
        work directory. A nonexistent dir means no plan exists (condition 2
        passes), so this correctly returns trivial when all other conditions
        are also met.
        """
        events_dir = tmp_path / ".claude" / "haios"
        events_dir.mkdir(parents=True)
        (events_dir / "governance-events.jsonl").write_text("")
        result = assess_scale("WORK-999", project_root=tmp_path)
        assert result == "trivial"
