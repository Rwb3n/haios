# generated: 2026-02-17
# WORK-157: Hierarchy Query Engine
"""
Tests for HierarchyQueryEngine (.claude/haios/lib/hierarchy_engine.py).

Validates:
- get_arcs() returns arc metadata from haios.yaml + ARC.md files
- get_chapters() returns chapter list from ARC.md table
- get_work() returns work items filtered by chapter
- get_hierarchy() returns full chain: work -> chapter -> arc -> epoch
- Edge cases: missing files, malformed YAML, epoch from extensions
- Integration: StatusPropagator delegates to HierarchyQueryEngine
"""
import sys
from pathlib import Path

import pytest

# Load lib module
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
from hierarchy_engine import (
    ArcInfo,
    ChapterInfo,
    HierarchyChain,
    HierarchyQueryEngine,
    WorkInfo,
)


# =========================================================================
# Fixtures
# =========================================================================


def _setup_hierarchy(base: Path):
    """Create a representative hierarchy: haios.yaml + 2 ARC.md + 3 WORK.md files.

    Structure:
    - Arc: engine-functions (2 chapters: CH-044, CH-045)
    - Arc: composability (1 chapter: CH-047)
    - WORK-157: CH-044, engine-functions, active
    - WORK-034: CH-045, engine-functions, complete
    - WORK-152: CH-047, composability, complete
    """
    # haios.yaml
    config_dir = base / ".claude" / "haios" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "haios.yaml").write_text(
        "epoch:\n"
        '  current: "E2.7"\n'
        "  arcs_dir: .claude/haios/epochs/E2_7/arcs\n"
        "  active_arcs:\n"
        "    - engine-functions\n"
        "    - composability\n",
        encoding="utf-8",
    )

    # ARC.md: engine-functions
    ef_dir = base / ".claude" / "haios" / "epochs" / "E2_7" / "arcs" / "engine-functions"
    ef_dir.mkdir(parents=True, exist_ok=True)
    (ef_dir / "ARC.md").write_text(
        "# Arc: engine-functions\n\n"
        "## Definition\n\n"
        "**Arc ID:** engine-functions\n"
        "**Epoch:** E2.7\n"
        "**Theme:** Functions over file reads -- engine query functions and status cascade\n"
        "**Status:** Active\n\n"
        "---\n\n"
        "## Chapters\n\n"
        "| CH-ID | Title | Work Items | Requirements | Dependencies | Status |\n"
        "|-------|-------|------------|--------------|--------------|--------|\n"
        "| CH-044 | HierarchyQueryEngine | WORK-157 | REQ-TRACE-005 | None | Planning |\n"
        "| CH-045 | StatusCascade | WORK-034 | REQ-QUEUE-001 | CH-044 | Complete |\n",
        encoding="utf-8",
    )

    # ARC.md: composability
    comp_dir = base / ".claude" / "haios" / "epochs" / "E2_7" / "arcs" / "composability"
    comp_dir.mkdir(parents=True, exist_ok=True)
    (comp_dir / "ARC.md").write_text(
        "# Arc: composability\n\n"
        "## Definition\n\n"
        "**Arc ID:** composability\n"
        "**Epoch:** E2.7\n"
        "**Theme:** Compose, don't concatenate -- flat metadata\n"
        "**Status:** Active\n\n"
        "---\n\n"
        "## Chapters\n\n"
        "| CH-ID | Title | Work Items | Requirements | Dependencies | Status |\n"
        "|-------|-------|------------|--------------|--------------|--------|\n"
        "| CH-047 | TemplateComposability | WORK-152, WORK-155 | REQ-COMPOSE-001 | None | Complete |\n",
        encoding="utf-8",
    )

    # Work items
    active_dir = base / "docs" / "work" / "active"

    # WORK-157: active, CH-044, engine-functions
    w157_dir = active_dir / "WORK-157"
    w157_dir.mkdir(parents=True, exist_ok=True)
    (w157_dir / "WORK.md").write_text(
        "---\n"
        "id: WORK-157\n"
        'title: "Hierarchy Query Engine"\n'
        "status: active\n"
        "type: feature\n"
        "chapter: CH-044\n"
        "arc: engine-functions\n"
        "extensions:\n"
        "  epoch: E2.7\n"
        "---\n"
        "# WORK-157\n",
        encoding="utf-8",
    )

    # WORK-034: complete, CH-045, engine-functions
    w034_dir = active_dir / "WORK-034"
    w034_dir.mkdir(parents=True, exist_ok=True)
    (w034_dir / "WORK.md").write_text(
        "---\n"
        "id: WORK-034\n"
        'title: "Upstream Status Propagation"\n'
        "status: complete\n"
        "type: feature\n"
        "chapter: CH-045\n"
        "arc: engine-functions\n"
        "extensions:\n"
        "  epoch: E2.7\n"
        "---\n"
        "# WORK-034\n",
        encoding="utf-8",
    )

    # WORK-152: complete, CH-047, composability
    w152_dir = active_dir / "WORK-152"
    w152_dir.mkdir(parents=True, exist_ok=True)
    (w152_dir / "WORK.md").write_text(
        "---\n"
        "id: WORK-152\n"
        'title: "Plan Template Fracturing"\n'
        "status: complete\n"
        "type: feature\n"
        "chapter: CH-047\n"
        "arc: composability\n"
        "extensions:\n"
        "  epoch: E2.7\n"
        "---\n"
        "# WORK-152\n",
        encoding="utf-8",
    )


def _setup_minimal_config(base: Path):
    """Create haios.yaml with epoch section but no arcs directory on disk."""
    config_dir = base / ".claude" / "haios" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "haios.yaml").write_text(
        "epoch:\n"
        '  current: "E2.7"\n'
        "  arcs_dir: .claude/haios/epochs/E2_7/arcs\n"
        "  active_arcs:\n"
        "    - nonexistent-arc\n",
        encoding="utf-8",
    )


# =========================================================================
# Test 1: get_arcs returns arc metadata
# =========================================================================


class TestGetArcs:
    def test_returns_arc_list(self, tmp_path):
        """get_arcs() returns list of ArcInfo from haios.yaml + ARC.md files."""
        _setup_hierarchy(tmp_path)
        engine = HierarchyQueryEngine(base_path=tmp_path)
        arcs = engine.get_arcs()
        assert len(arcs) == 2
        # Sorted by name
        names = [a.name for a in arcs]
        assert "composability" in names
        assert "engine-functions" in names
        # Verify ArcInfo fields populated
        ef = next(a for a in arcs if a.name == "engine-functions")
        assert ef.status == "Active"
        assert "Functions over file reads" in ef.theme
        assert isinstance(ef.chapters, list)
        assert "CH-044" in ef.chapters
        assert "CH-045" in ef.chapters

    def test_no_arcs_dir_returns_empty(self, tmp_path):
        """get_arcs() returns empty list when arcs directory doesn't exist."""
        _setup_minimal_config(tmp_path)
        engine = HierarchyQueryEngine(base_path=tmp_path)
        arcs = engine.get_arcs()
        assert arcs == []


# =========================================================================
# Test 2-3: get_chapters
# =========================================================================


class TestGetChapters:
    def test_returns_chapter_list(self, tmp_path):
        """get_chapters() returns chapters from ARC.md table."""
        _setup_hierarchy(tmp_path)
        engine = HierarchyQueryEngine(base_path=tmp_path)
        chapters = engine.get_chapters("engine-functions")
        assert len(chapters) == 2
        ch044 = next(c for c in chapters if c.id == "CH-044")
        assert ch044.title == "HierarchyQueryEngine"
        assert ch044.work_items == ["WORK-157"]
        assert ch044.status == "Planning"
        assert ch044.arc == "engine-functions"

    def test_unknown_arc_returns_empty(self, tmp_path):
        """get_chapters() returns empty list for unknown arc."""
        _setup_hierarchy(tmp_path)
        engine = HierarchyQueryEngine(base_path=tmp_path)
        chapters = engine.get_chapters("nonexistent")
        assert chapters == []

    def test_multiple_work_items_in_chapter(self, tmp_path):
        """get_chapters() parses comma-separated work item IDs."""
        _setup_hierarchy(tmp_path)
        engine = HierarchyQueryEngine(base_path=tmp_path)
        chapters = engine.get_chapters("composability")
        ch047 = next(c for c in chapters if c.id == "CH-047")
        assert "WORK-152" in ch047.work_items
        assert "WORK-155" in ch047.work_items


# =========================================================================
# Test 4-5: get_work
# =========================================================================


class TestGetWork:
    def test_returns_work_items_for_chapter(self, tmp_path):
        """get_work() returns WorkInfo list filtered by chapter."""
        _setup_hierarchy(tmp_path)
        engine = HierarchyQueryEngine(base_path=tmp_path)
        items = engine.get_work("CH-044")
        assert len(items) == 1
        assert items[0].id == "WORK-157"
        assert items[0].status == "active"
        assert items[0].type == "feature"

    def test_empty_chapter_returns_empty(self, tmp_path):
        """get_work() returns empty list for chapter with no items."""
        _setup_hierarchy(tmp_path)
        engine = HierarchyQueryEngine(base_path=tmp_path)
        items = engine.get_work("CH-999")
        assert items == []

    def test_includes_completed_items(self, tmp_path):
        """get_work() includes items with complete status."""
        _setup_hierarchy(tmp_path)
        engine = HierarchyQueryEngine(base_path=tmp_path)
        items = engine.get_work("CH-045")
        assert len(items) == 1
        assert items[0].id == "WORK-034"
        assert items[0].status == "complete"


# =========================================================================
# Test 6-7: get_hierarchy
# =========================================================================


class TestGetHierarchy:
    def test_returns_full_chain(self, tmp_path):
        """get_hierarchy() returns HierarchyChain with all levels."""
        _setup_hierarchy(tmp_path)
        engine = HierarchyQueryEngine(base_path=tmp_path)
        chain = engine.get_hierarchy("WORK-157")
        assert chain is not None
        assert chain.work_id == "WORK-157"
        assert chain.chapter == "CH-044"
        assert chain.arc == "engine-functions"
        assert chain.epoch == "E2.7"

    def test_unknown_work_returns_none(self, tmp_path):
        """get_hierarchy() returns None for unknown work item."""
        _setup_hierarchy(tmp_path)
        engine = HierarchyQueryEngine(base_path=tmp_path)
        chain = engine.get_hierarchy("WORK-999")
        assert chain is None


# =========================================================================
# Test 8: get_arcs with no arcs directory
# =========================================================================


class TestGetArcsNoDir:
    def test_no_arcs_dir(self, tmp_path):
        """get_arcs() returns empty list when arcs_dir path doesn't exist on disk."""
        _setup_minimal_config(tmp_path)
        engine = HierarchyQueryEngine(base_path=tmp_path)
        arcs = engine.get_arcs()
        assert arcs == []


# =========================================================================
# Test 10: Malformed YAML tolerance (A9 critique)
# =========================================================================


class TestMalformedYaml:
    def test_skips_malformed_work_item(self, tmp_path):
        """get_work() skips malformed WORK.md files gracefully."""
        _setup_hierarchy(tmp_path)
        # Create a malformed WORK.md in active dir
        bad_dir = tmp_path / "docs" / "work" / "active" / "WORK-BAD"
        bad_dir.mkdir(parents=True)
        (bad_dir / "WORK.md").write_text(
            "---\n: invalid: yaml: {{{\n---\n", encoding="utf-8"
        )
        engine = HierarchyQueryEngine(base_path=tmp_path)
        items = engine.get_work("CH-044")
        assert len(items) == 1
        assert items[0].id == "WORK-157"


# =========================================================================
# Test 11: Epoch from work item extensions (A10 critique)
# =========================================================================


class TestEpochFromExtensions:
    def test_uses_work_item_epoch(self, tmp_path):
        """get_hierarchy() reads epoch from extensions.epoch, not just config."""
        _setup_hierarchy(tmp_path)
        engine = HierarchyQueryEngine(base_path=tmp_path)
        chain = engine.get_hierarchy("WORK-157")
        assert chain.epoch == "E2.7"

    def test_fallback_to_config_epoch(self, tmp_path):
        """get_hierarchy() falls back to config epoch when extensions.epoch missing."""
        _setup_hierarchy(tmp_path)
        # Create work item WITHOUT extensions.epoch
        no_epoch_dir = tmp_path / "docs" / "work" / "active" / "WORK-NOEPOCH"
        no_epoch_dir.mkdir(parents=True, exist_ok=True)
        (no_epoch_dir / "WORK.md").write_text(
            "---\n"
            "id: WORK-NOEPOCH\n"
            'title: "No Epoch Field"\n'
            "status: active\n"
            "type: feature\n"
            "chapter: CH-044\n"
            "arc: engine-functions\n"
            "---\n"
            "# WORK-NOEPOCH\n",
            encoding="utf-8",
        )
        engine = HierarchyQueryEngine(base_path=tmp_path)
        chain = engine.get_hierarchy("WORK-NOEPOCH")
        assert chain is not None
        assert chain.epoch == "E2.7"  # From config fallback


# =========================================================================
# Test 12: Integration - StatusPropagator uses HierarchyQueryEngine
# =========================================================================


class TestStatusPropagatorIntegration:
    def test_status_propagator_hierarchy_context(self, tmp_path):
        """StatusPropagator.get_hierarchy_context() still works after refactor."""
        _setup_hierarchy(tmp_path)
        # Also need ARC.md for StatusPropagator's arc operations
        from status_propagator import StatusPropagator

        propagator = StatusPropagator(base_path=tmp_path)
        ctx = propagator.get_hierarchy_context("WORK-034")
        assert ctx is not None
        assert ctx["chapter"] == "CH-045"
        assert ctx["arc"] == "engine-functions"
