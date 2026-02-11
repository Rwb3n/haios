# generated: 2026-02-11
"""Tests for DoD validation functions (CH-015, WORK-122).

Tests programmatic DoD validation at each hierarchy level:
- validate_work_dod: Work item status checks
- validate_chapter_dod: All chapter work items complete + exit criteria
- validate_arc_dod: All arc chapters Complete (bold markdown)
- validate_epoch_dod: All epoch arcs Complete (bold markdown)
"""

import sys
from pathlib import Path

import pytest

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))

from dod_validation import (
    DoDCheck,
    DoDResult,
    validate_arc_dod,
    validate_chapter_dod,
    validate_epoch_dod,
    validate_work_dod,
)


class TestValidateWorkDod:
    """Tests for validate_work_dod."""

    def test_returns_dod_result_on_complete(self, tmp_path):
        """validate_work_dod returns DoDResult with passed=True for complete work."""
        work_dir = tmp_path / "docs" / "work" / "active" / "WORK-001"
        work_dir.mkdir(parents=True)
        (work_dir / "WORK.md").write_text(
            "---\nid: WORK-001\nstatus: complete\nclosed: 2026-02-11\n"
            "traces_to: [REQ-TEST-001]\n---\n# WORK-001\n",
            encoding="utf-8",
        )
        result = validate_work_dod("WORK-001", base_path=tmp_path)
        assert isinstance(result, DoDResult)
        assert result.passed is True
        assert result.level == "work"
        assert result.entity_id == "WORK-001"
        assert len(result.failures) == 0

    def test_fails_on_incomplete_work(self, tmp_path):
        """validate_work_dod fails when status is not complete."""
        work_dir = tmp_path / "docs" / "work" / "active" / "WORK-001"
        work_dir.mkdir(parents=True)
        (work_dir / "WORK.md").write_text(
            "---\nid: WORK-001\nstatus: active\nclosed: null\n"
            "traces_to: []\n---\n# WORK-001\n",
            encoding="utf-8",
        )
        result = validate_work_dod("WORK-001", base_path=tmp_path)
        assert result.passed is False
        assert len(result.failures) > 0

    def test_fails_when_not_found(self, tmp_path):
        """validate_work_dod fails gracefully when work item doesn't exist."""
        result = validate_work_dod("WORK-999", base_path=tmp_path)
        assert result.passed is False
        assert any("not found" in f.lower() for f in result.failures)


class TestValidateChapterDod:
    """Tests for validate_chapter_dod (bold markdown format)."""

    def _setup_chapter(self, tmp_path, status="Complete", exit_criteria="- [x] Done\n"):
        """Helper: create chapter file in bold markdown format."""
        ch_dir = (
            tmp_path / ".claude" / "haios" / "epochs" / "E2_5" / "arcs" / "ceremonies"
        )
        ch_dir.mkdir(parents=True, exist_ok=True)
        (ch_dir / "CH-015-ClosureCeremonies.md").write_text(
            f"# Chapter: Closure Ceremonies\n\n"
            f"**Chapter ID:** CH-015\n**Arc:** ceremonies\n**Status:** {status}\n\n"
            f"## Exit Criteria\n\n{exit_criteria}",
            encoding="utf-8",
        )
        return ch_dir

    def _setup_work_item(self, tmp_path, work_id, chapter, status="complete"):
        """Helper: create work item with chapter field."""
        wd = tmp_path / "docs" / "work" / "active" / work_id
        wd.mkdir(parents=True, exist_ok=True)
        (wd / "WORK.md").write_text(
            f"---\nid: {work_id}\nstatus: {status}\nchapter: {chapter}\n"
            f"closed: 2026-02-11\n---\n# {work_id}\n",
            encoding="utf-8",
        )

    def test_passes_when_all_work_complete(self, tmp_path):
        """validate_chapter_dod passes when all chapter work items are complete."""
        self._setup_chapter(tmp_path)
        self._setup_work_item(tmp_path, "WORK-111", "CH-015")
        self._setup_work_item(tmp_path, "WORK-112", "CH-015")
        result = validate_chapter_dod("CH-015", "ceremonies", base_path=tmp_path)
        assert result.passed is True
        assert result.level == "chapter"

    def test_fails_with_incomplete_work(self, tmp_path):
        """validate_chapter_dod fails when any work item is not complete."""
        self._setup_chapter(tmp_path, status="Planned", exit_criteria="- [ ] Not done\n")
        self._setup_work_item(tmp_path, "WORK-111", "CH-015", status="complete")
        self._setup_work_item(tmp_path, "WORK-122", "CH-015", status="active")
        result = validate_chapter_dod("CH-015", "ceremonies", base_path=tmp_path)
        assert result.passed is False
        assert any("WORK-122" in f for f in result.failures)

    def test_fails_with_unchecked_exit_criteria(self, tmp_path):
        """validate_chapter_dod fails when exit criteria checkboxes are not all checked."""
        self._setup_chapter(
            tmp_path,
            exit_criteria="- [x] Done item\n- [ ] Not done item\n",
        )
        self._setup_work_item(tmp_path, "WORK-111", "CH-015")
        result = validate_chapter_dod("CH-015", "ceremonies", base_path=tmp_path)
        assert result.passed is False
        assert any("exit criteria" in f.lower() for f in result.failures)

    def test_passes_with_no_work_items(self, tmp_path):
        """validate_chapter_dod passes if chapter has no work items assigned."""
        self._setup_chapter(tmp_path)
        result = validate_chapter_dod("CH-015", "ceremonies", base_path=tmp_path)
        assert result.passed is True


class TestValidateArcDod:
    """Tests for validate_arc_dod (bold markdown format)."""

    def test_passes_when_all_chapters_complete(self, tmp_path):
        """validate_arc_dod passes when all arc chapters are Complete."""
        arc_dir = (
            tmp_path / ".claude" / "haios" / "epochs" / "E2_5" / "arcs" / "ceremonies"
        )
        arc_dir.mkdir(parents=True)
        (arc_dir / "ARC.md").write_text("**Status:** In Progress\n", encoding="utf-8")
        (arc_dir / "CH-011-CeremonyContracts.md").write_text(
            "**Status:** Complete\n", encoding="utf-8"
        )
        (arc_dir / "CH-012-SideEffectBoundaries.md").write_text(
            "**Status:** Complete\n", encoding="utf-8"
        )
        result = validate_arc_dod("ceremonies", base_path=tmp_path)
        assert result.passed is True
        assert result.level == "arc"

    def test_fails_with_incomplete_chapter(self, tmp_path):
        """validate_arc_dod fails when any chapter is not Complete."""
        arc_dir = (
            tmp_path / ".claude" / "haios" / "epochs" / "E2_5" / "arcs" / "ceremonies"
        )
        arc_dir.mkdir(parents=True)
        (arc_dir / "ARC.md").write_text("**Status:** In Progress\n", encoding="utf-8")
        (arc_dir / "CH-011-CeremonyContracts.md").write_text(
            "**Status:** Complete\n", encoding="utf-8"
        )
        (arc_dir / "CH-015-ClosureCeremonies.md").write_text(
            "**Status:** Planned\n", encoding="utf-8"
        )
        result = validate_arc_dod("ceremonies", base_path=tmp_path)
        assert result.passed is False
        assert any("CH-015" in f for f in result.failures)

    def test_skips_deferred_chapters(self, tmp_path):
        """validate_arc_dod skips chapters with Deferred status."""
        arc_dir = (
            tmp_path / ".claude" / "haios" / "epochs" / "E2_5" / "arcs" / "feedback"
        )
        arc_dir.mkdir(parents=True)
        (arc_dir / "ARC.md").write_text("**Status:** In Progress\n", encoding="utf-8")
        (arc_dir / "CH-018-ChapterReview.md").write_text(
            "**Status:** Deferred to E2.6\n", encoding="utf-8"
        )
        result = validate_arc_dod("feedback", base_path=tmp_path)
        assert result.passed is True


class TestValidateEpochDod:
    """Tests for validate_epoch_dod (bold markdown format)."""

    def test_passes_when_all_arcs_complete(self, tmp_path):
        """validate_epoch_dod passes when all arcs are Complete."""
        epoch_dir = tmp_path / ".claude" / "haios" / "epochs" / "E2_5"
        epoch_dir.mkdir(parents=True)
        (epoch_dir / "EPOCH.md").write_text("**Status:** Active\n", encoding="utf-8")
        arcs_dir = epoch_dir / "arcs"
        for arc in ["lifecycles", "ceremonies"]:
            (arcs_dir / arc).mkdir(parents=True)
            (arcs_dir / arc / "ARC.md").write_text(
                "**Status:** Complete\n", encoding="utf-8"
            )
        result = validate_epoch_dod("E2_5", base_path=tmp_path)
        assert result.passed is True
        assert result.level == "epoch"

    def test_fails_with_incomplete_arc(self, tmp_path):
        """validate_epoch_dod fails when any non-deferred arc is not Complete."""
        epoch_dir = tmp_path / ".claude" / "haios" / "epochs" / "E2_5"
        epoch_dir.mkdir(parents=True)
        (epoch_dir / "EPOCH.md").write_text("**Status:** Active\n", encoding="utf-8")
        arcs_dir = epoch_dir / "arcs"
        (arcs_dir / "lifecycles").mkdir(parents=True)
        (arcs_dir / "lifecycles" / "ARC.md").write_text(
            "**Status:** Complete\n", encoding="utf-8"
        )
        (arcs_dir / "ceremonies").mkdir(parents=True)
        (arcs_dir / "ceremonies" / "ARC.md").write_text(
            "**Status:** In Progress\n", encoding="utf-8"
        )
        result = validate_epoch_dod("E2_5", base_path=tmp_path)
        assert result.passed is False
        assert any("ceremonies" in f for f in result.failures)

    def test_skips_deferred_arcs(self, tmp_path):
        """validate_epoch_dod skips arcs with Deferred status."""
        epoch_dir = tmp_path / ".claude" / "haios" / "epochs" / "E2_5"
        epoch_dir.mkdir(parents=True)
        (epoch_dir / "EPOCH.md").write_text("**Status:** Active\n", encoding="utf-8")
        arcs_dir = epoch_dir / "arcs"
        (arcs_dir / "lifecycles").mkdir(parents=True)
        (arcs_dir / "lifecycles" / "ARC.md").write_text(
            "**Status:** Complete\n", encoding="utf-8"
        )
        (arcs_dir / "feedback").mkdir(parents=True)
        (arcs_dir / "feedback" / "ARC.md").write_text(
            "**Status:** Deferred to E2.6\n", encoding="utf-8"
        )
        result = validate_epoch_dod("E2_5", base_path=tmp_path)
        assert result.passed is True
