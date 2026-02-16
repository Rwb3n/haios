# generated: 2026-02-16
# WORK-034: Upstream Status Propagation on Work Closure
"""
Tests for StatusPropagator (lib/status_propagator.py).

Validates:
- Hierarchy context extraction from work item frontmatter
- Chapter completion detection
- ARC.md chapter status row update
- Arc completion detection
- Full propagation flow
- Event logging
"""
import json
import sys
from pathlib import Path

import pytest

# Load lib module
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
from status_propagator import StatusPropagator


# =========================================================================
# Fixtures
# =========================================================================


def _create_work_item(base: Path, work_id: str, chapter: str = None, arc: str = None, status: str = "active"):
    """Helper: create a minimal WORK.md with optional chapter/arc fields."""
    work_dir = base / "docs" / "work" / "active" / work_id
    work_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        f"id: {work_id}",
        f"title: Test work item {work_id}",
        f"status: {status}",
    ]
    if chapter:
        lines.append(f"chapter: {chapter}")
    if arc:
        lines.append(f"arc: {arc}")
    lines.append("---")
    lines.append(f"# {work_id}")
    (work_dir / "WORK.md").write_text("\n".join(lines), encoding="utf-8")


def _create_arc_md(base: Path, arc_name: str, chapters: list[tuple[str, str, str]]):
    """Helper: create an ARC.md with chapter table.

    chapters: list of (chapter_id, title, status) tuples.
    """
    haios_dir = base / ".claude" / "haios"
    config_dir = haios_dir / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    arcs_dir = haios_dir / "epochs" / "E2_7" / "arcs"

    # Write haios.yaml with arcs_dir
    haios_yaml = config_dir / "haios.yaml"
    haios_yaml.write_text(
        f"epoch:\n  arcs_dir: .claude/haios/epochs/E2_7/arcs\n",
        encoding="utf-8",
    )

    # Write ARC.md
    arc_dir = arcs_dir / arc_name
    arc_dir.mkdir(parents=True, exist_ok=True)
    table_rows = []
    for ch_id, title, status in chapters:
        table_rows.append(f"| {ch_id} | {title} | WORK-XXX | REQ-XXX | None | {status} |")

    content = f"""# Arc: {arc_name}

## Chapters

| CH-ID | Title | Work Items | Requirements | Dependencies | Status |
|-------|-------|------------|--------------|--------------|--------|
{chr(10).join(table_rows)}
"""
    (arc_dir / "ARC.md").write_text(content, encoding="utf-8")


# =========================================================================
# Test 1: Extract chapter and arc from work item frontmatter
# =========================================================================


class TestGetHierarchyContext:
    def test_reads_chapter_arc_from_frontmatter(self, tmp_path):
        """StatusPropagator reads chapter/arc from raw WORK.md frontmatter."""
        _create_work_item(tmp_path, "WORK-034", chapter="CH-045", arc="engine-functions")
        propagator = StatusPropagator(base_path=tmp_path)
        ctx = propagator.get_hierarchy_context("WORK-034")
        assert ctx is not None
        assert ctx["chapter"] == "CH-045"
        assert ctx["arc"] == "engine-functions"

    def test_returns_none_when_no_chapter_arc(self, tmp_path):
        """Returns None when work item lacks chapter/arc fields."""
        _create_work_item(tmp_path, "WORK-999")
        propagator = StatusPropagator(base_path=tmp_path)
        ctx = propagator.get_hierarchy_context("WORK-999")
        assert ctx is None

    def test_returns_none_when_work_not_found(self, tmp_path):
        """Returns None when work item doesn't exist."""
        propagator = StatusPropagator(base_path=tmp_path)
        ctx = propagator.get_hierarchy_context("WORK-NONEXISTENT")
        assert ctx is None


# =========================================================================
# Test 2-3: Chapter completion detection
# =========================================================================


class TestIsChapterComplete:
    def test_all_complete(self, tmp_path):
        """Returns True when all work items for a chapter have complete status."""
        _create_work_item(tmp_path, "WORK-153", chapter="CH-049", arc="infrastructure", status="complete")
        _create_work_item(tmp_path, "WORK-160", chapter="CH-049", arc="infrastructure", status="complete")
        propagator = StatusPropagator(base_path=tmp_path)
        assert propagator.is_chapter_complete("CH-049") is True

    def test_partial_complete(self, tmp_path):
        """Returns False when some work items for a chapter are still active."""
        _create_work_item(tmp_path, "WORK-152", chapter="CH-047", arc="composability", status="complete")
        _create_work_item(tmp_path, "WORK-155", chapter="CH-047", arc="composability", status="active")
        propagator = StatusPropagator(base_path=tmp_path)
        assert propagator.is_chapter_complete("CH-047") is False

    def test_no_items_returns_false(self, tmp_path):
        """Returns False when no work items exist for the chapter (unfunded)."""
        # Create active dir but no items for CH-999
        (tmp_path / "docs" / "work" / "active").mkdir(parents=True)
        propagator = StatusPropagator(base_path=tmp_path)
        assert propagator.is_chapter_complete("CH-999") is False


# =========================================================================
# Test 4: Update ARC.md chapter status row
# =========================================================================


class TestUpdateArcChapterStatus:
    def test_updates_chapter_row(self, tmp_path):
        """Updates the chapter row status in ARC.md from Planning to Complete."""
        _create_arc_md(tmp_path, "engine-functions", [
            ("CH-044", "HierarchyQueryEngine", "Planning"),
            ("CH-045", "StatusCascade", "Planning"),
        ])
        propagator = StatusPropagator(base_path=tmp_path)
        result = propagator.update_arc_chapter_status("engine-functions", "CH-045", "Complete")
        assert result["updated"] is True
        # Verify content changed
        arc_file = tmp_path / ".claude" / "haios" / "epochs" / "E2_7" / "arcs" / "engine-functions" / "ARC.md"
        content = arc_file.read_text(encoding="utf-8")
        # CH-045 should be Complete, CH-044 should still be Planning
        assert "| CH-045 |" in content
        assert "| CH-044 |" in content
        # Check that CH-045 row has Complete
        for line in content.split("\n"):
            if "CH-045" in line:
                assert "Complete" in line
            if "CH-044" in line:
                assert "Planning" in line

    def test_returns_false_when_arc_not_found(self, tmp_path):
        """Returns updated=False when arc file doesn't exist."""
        _create_arc_md(tmp_path, "infrastructure", [("CH-049", "BugBatch", "Planning")])
        propagator = StatusPropagator(base_path=tmp_path)
        result = propagator.update_arc_chapter_status("nonexistent-arc", "CH-049", "Complete")
        assert result["updated"] is False
        assert result["reason"] == "arc_file_not_found"


# =========================================================================
# Test 5: No-op when chapter/arc fields missing
# =========================================================================


class TestPropagateNoHierarchy:
    def test_noop_when_no_hierarchy(self, tmp_path):
        """Returns early with no_hierarchy result when work item lacks chapter/arc."""
        _create_work_item(tmp_path, "WORK-999", status="complete")
        _create_arc_md(tmp_path, "infrastructure", [("CH-049", "BugBatch", "Planning")])
        propagator = StatusPropagator(base_path=tmp_path)
        result = propagator.propagate("WORK-999")
        assert result["action"] == "no_hierarchy"


# =========================================================================
# Test 6: Full propagation flow (chapter completes)
# =========================================================================


class TestPropagateFullFlow:
    def test_chapter_completes(self, tmp_path):
        """Full propagation: work closes, chapter detected complete, ARC.md updated."""
        _create_work_item(tmp_path, "WORK-153", chapter="CH-049", arc="infrastructure", status="complete")
        _create_arc_md(tmp_path, "infrastructure", [
            ("CH-049", "BugBatch", "Planning"),
            ("CH-050", "EpochTransition", "Planning"),
            ("CH-051", "StalenessDetection", "Planning"),
        ])
        propagator = StatusPropagator(base_path=tmp_path)
        result = propagator.propagate("WORK-153")
        assert result["action"] == "chapter_completed"
        assert result["chapter"] == "CH-049"
        assert result["arc_updated"] is True
        assert result["arc_complete"] is False  # Other chapters still Planning

    def test_chapter_incomplete(self, tmp_path):
        """Returns chapter_incomplete when not all chapter items are done."""
        _create_work_item(tmp_path, "WORK-152", chapter="CH-047", arc="composability", status="complete")
        _create_work_item(tmp_path, "WORK-155", chapter="CH-047", arc="composability", status="active")
        _create_arc_md(tmp_path, "composability", [("CH-047", "TemplateComposability", "Planning")])
        propagator = StatusPropagator(base_path=tmp_path)
        result = propagator.propagate("WORK-152")
        assert result["action"] == "chapter_incomplete"
        assert result["chapter"] == "CH-047"


# =========================================================================
# Test 7: Event logging on propagation
# =========================================================================


class TestEventLogging:
    def test_logs_status_propagation_event(self, tmp_path):
        """StatusPropagation event logged to governance-events.jsonl."""
        events_file = tmp_path / "events.jsonl"
        _create_work_item(tmp_path, "WORK-153", chapter="CH-049", arc="infrastructure", status="complete")
        _create_arc_md(tmp_path, "infrastructure", [("CH-049", "BugBatch", "Planning")])
        propagator = StatusPropagator(base_path=tmp_path, events_file=events_file)
        propagator.propagate("WORK-153")

        assert events_file.exists()
        events = events_file.read_text(encoding="utf-8").strip().split("\n")
        event = json.loads(events[-1])
        assert event["type"] == "StatusPropagation"
        assert event["work_id"] == "WORK-153"
        assert event["chapter"] == "CH-049"
        assert event["arc"] == "infrastructure"
        assert "timestamp" in event


# =========================================================================
# Test 8: Arc completion detection
# =========================================================================


class TestIsArcComplete:
    def test_all_chapters_complete(self, tmp_path):
        """Returns True when all chapter rows in ARC.md have Complete status."""
        _create_arc_md(tmp_path, "infrastructure", [
            ("CH-049", "BugBatch", "Complete"),
            ("CH-050", "EpochTransition", "Complete"),
            ("CH-051", "StalenessDetection", "Complete"),
        ])
        propagator = StatusPropagator(base_path=tmp_path)
        assert propagator.is_arc_complete("infrastructure") is True

    def test_some_chapters_not_complete(self, tmp_path):
        """Returns False when some chapter rows still show Planning."""
        _create_arc_md(tmp_path, "infrastructure", [
            ("CH-049", "BugBatch", "Complete"),
            ("CH-050", "EpochTransition", "Planning"),
        ])
        propagator = StatusPropagator(base_path=tmp_path)
        assert propagator.is_arc_complete("infrastructure") is False
