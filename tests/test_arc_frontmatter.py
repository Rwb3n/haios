# generated: 2026-03-07
# WORK-245: ARC.md YAML Frontmatter Migration — Tests
"""Tests for arc_frontmatter.py and migrate_arc_frontmatter.py.

TDD RED phase: All 22 tests written before implementation.
Tests cover:
  - Frontmatter parsing (Tests 1-2)
  - Arc status and metadata read with fallback (Tests 3-5)
  - Chapters read with multi-column fallback (Tests 6-7, 7a, 7b)
  - Exit criteria with section heading variants (Tests 7c, 8-9)
  - Chapter update operations (Tests 10-12)
  - Migration (Tests 13-15)
  - build_arc_frontmatter full parse (Test 16)
  - Consumer integration (Tests 17-19)
"""

import sys
from pathlib import Path

import pytest
import yaml

# Add .claude/haios/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))


# =========================================================================
# Fixtures
# =========================================================================

ARC_INFRA_LEGACY_CONTENT = """\
# generated: 2026-02-17
# System Auto: last updated on: 2026-02-17T21:00:00
# Arc: Infrastructure

## Definition

**Arc ID:** infrastructure
**Epoch:** E2.8
**Theme:** Fix what's broken
**Status:** Planning
**Started:** 2026-02-17 (Session 393)

---

## Purpose

Bug fixes and deferred items from E2.7 triage. Clean foundation for the UX arcs. The batch bug pattern (mem:84963) is validated — grouping 4+ small fixes in one session is efficient.

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-CEREMONY-001 | Ceremonies are side-effect boundaries |

---

## Chapters

| CH-ID | Title | Work Items | Requirements | Dependencies | Status |
|-------|-------|------------|--------------|--------------|--------|
| CH-065 | BugBatch-E28 | New | REQ-CEREMONY-001 | None | Complete |
| CH-067 | FileFormatMigration | WORK-244, WORK-245 | REQ-TRACE-004 | None | Active |

---

## Exit Criteria

- [x] All confirmed bugs from E2.7 triage resolved (WORK-166, S395)

---

## Known Bugs

From E2.7 triage (memory IDs) and S393 operator report:

| Bug | Source | Description |
|-----|--------|-------------|
| Checkpoint same-session sort | S393 operator | session_loader.py:120 |

---

## Notes

- Batch pattern validated (mem:84963): grouping small fixes is efficient
- Memory-referenced bugs need verification

---

## References

- @.claude/haios/epochs/E2_8/EPOCH.md (parent epoch)
- Memory: 84963 (batch pattern)
"""


def _write_frontmatter_arc(tmp_path, fm_dict, body="# Arc body\n"):
    """Helper: write ARC.md with YAML frontmatter + body."""
    path = tmp_path / "ARC.md"
    fm_yaml = yaml.dump(fm_dict, default_flow_style=False, allow_unicode=True, sort_keys=False)
    path.write_text(f"---\n{fm_yaml}---\n{body}", encoding="utf-8")
    return path


def _write_legacy_arc(tmp_path, content=None):
    """Helper: write ARC.md in legacy bold-markdown format."""
    path = tmp_path / "ARC.md"
    path.write_text(content or ARC_INFRA_LEGACY_CONTENT, encoding="utf-8")
    return path


def _create_haios_config(tmp_path, arcs_dir_rel):
    """Helper: create haios.yaml with epoch.arcs_dir pointing to arcs_dir_rel."""
    config_dir = tmp_path / ".claude" / "haios" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "haios.yaml"
    config_file.write_text(
        yaml.dump({"epoch": {"arcs_dir": arcs_dir_rel, "current": "E2.8"}},
                  default_flow_style=False),
        encoding="utf-8",
    )
    return config_file


# =========================================================================
# Test 1: parse_arc_frontmatter — returns dict when frontmatter present
# =========================================================================
class TestParseArcFrontmatter:
    def test_parse_arc_frontmatter_returns_dict(self, tmp_path):
        fm = {"id": "infrastructure", "epoch": "E2.8", "status": "Planning"}
        path = _write_frontmatter_arc(tmp_path, fm)

        from arc_frontmatter import parse_arc_frontmatter
        result = parse_arc_frontmatter(path)

        assert result is not None
        assert result["id"] == "infrastructure"
        assert result["epoch"] == "E2.8"
        assert result["status"] == "Planning"

    # Test 2: returns None when no frontmatter
    def test_parse_arc_frontmatter_returns_none_for_legacy(self, tmp_path):
        path = _write_legacy_arc(tmp_path)

        from arc_frontmatter import parse_arc_frontmatter
        result = parse_arc_frontmatter(path)

        assert result is None


# =========================================================================
# Tests 3-4: get_arc_status
# =========================================================================
class TestGetArcStatus:
    # Test 3: reads from frontmatter when present
    def test_get_arc_status_from_frontmatter(self, tmp_path):
        fm = {"id": "infrastructure", "epoch": "E2.8", "status": "Active"}
        path = _write_frontmatter_arc(tmp_path, fm)

        from arc_frontmatter import get_arc_status
        result = get_arc_status(path)

        assert result == "Active"

    # Test 4: falls back to bold-markdown when no frontmatter
    def test_get_arc_status_fallback(self, tmp_path):
        content = "**Arc ID:** infrastructure\n**Status:** Planning\n"
        path = _write_legacy_arc(tmp_path, content)

        from arc_frontmatter import get_arc_status
        result = get_arc_status(path)

        assert result == "Planning"


# =========================================================================
# Test 5: get_arc_metadata
# =========================================================================
class TestGetArcMetadata:
    def test_get_arc_metadata_from_frontmatter(self, tmp_path):
        fm = {
            "id": "infrastructure",
            "epoch": "E2.8",
            "theme": "Fix what's broken",
            "status": "Planning",
            "started": "2026-02-17 (Session 393)",
        }
        path = _write_frontmatter_arc(tmp_path, fm)

        from arc_frontmatter import get_arc_metadata
        result = get_arc_metadata(path)

        assert result["theme"] == "Fix what's broken"
        assert result["status"] == "Planning"


# =========================================================================
# Tests 6-7, 7a, 7b: get_chapters
# =========================================================================
class TestGetChapters:
    # Test 6: reads chapter list from frontmatter
    def test_get_chapters_from_frontmatter(self, tmp_path):
        fm = {
            "id": "infrastructure",
            "chapters": [
                {"id": "CH-065", "title": "BugBatch-E28", "work_items": ["New"],
                 "requirements": ["REQ-CEREMONY-001"], "dependencies": [], "status": "Complete"},
                {"id": "CH-067", "title": "FileFormatMigration", "work_items": ["WORK-244", "WORK-245"],
                 "requirements": ["REQ-TRACE-004"], "dependencies": [], "status": "Active"},
            ],
        }
        path = _write_frontmatter_arc(tmp_path, fm)

        from arc_frontmatter import get_chapters
        result = get_chapters(path)

        assert len(result) == 2
        assert result[0]["id"] == "CH-065"
        assert result[0]["status"] == "Complete"

    # Test 7: falls back to 6-column table parsing when no frontmatter
    def test_get_chapters_fallback_6col_table(self, tmp_path):
        content = """\
# Arc

## Chapters

| CH-ID | Title | Work Items | Requirements | Dependencies | Status |
|-------|-------|------------|--------------|--------------|--------|
| CH-065 | BugBatch-E28 | New | REQ-CEREMONY-001 | None | Complete |
"""
        path = _write_legacy_arc(tmp_path, content)

        from arc_frontmatter import get_chapters
        result = get_chapters(path)

        assert len(result) == 1
        assert result[0]["id"] == "CH-065"
        assert result[0]["title"] == "BugBatch-E28"
        assert result[0]["status"] == "Complete"

    # Test 7a: falls back to 4-column table parsing (A1/A7 critique)
    def test_get_chapters_fallback_4col_table(self, tmp_path):
        content = """\
# Arc

## Chapters

| Chapter | Name | Status | Purpose |
|---------|------|--------|---------|
| CH-001 | GroundCycle | Complete | Core grounding |
"""
        path = _write_legacy_arc(tmp_path, content)

        from arc_frontmatter import get_chapters
        result = get_chapters(path)

        assert len(result) == 1
        assert result[0]["id"] == "CH-001"
        assert result[0]["title"] == "GroundCycle"
        assert result[0]["status"] == "Complete"
        assert result[0]["work_items"] == []
        assert result[0]["requirements"] == []
        assert result[0]["dependencies"] == []

    # Test 7b: falls back to 5-column table parsing (A7 critique)
    def test_get_chapters_fallback_5col_table(self, tmp_path):
        content = """\
# Arc

## Chapters

| CH-ID | Title | Requirements | Dependencies | Status |
|-------|-------|--------------|--------------|--------|
| CH-018 | ChapterReview | REQ-FEEDBACK-001 | None | Complete |
"""
        path = _write_legacy_arc(tmp_path, content)

        from arc_frontmatter import get_chapters
        result = get_chapters(path)

        assert len(result) == 1
        assert result[0]["id"] == "CH-018"
        assert result[0]["title"] == "ChapterReview"
        assert result[0]["status"] == "Complete"
        assert result[0]["work_items"] == []
        assert result[0]["requirements"] == ["REQ-FEEDBACK-001"]
        assert result[0]["dependencies"] == []


# =========================================================================
# Tests 7c, 8-9: get_exit_criteria
# =========================================================================
class TestGetExitCriteria:
    # Test 7c: falls back to Arc Completion Criteria heading (A3 critique)
    def test_get_exit_criteria_fallback_arc_completion_heading(self, tmp_path):
        content = """\
# Arc

## Arc Completion Criteria

- [x] done
- [ ] pending
"""
        path = _write_legacy_arc(tmp_path, content)

        from arc_frontmatter import get_exit_criteria
        result = get_exit_criteria(path)

        assert result is not None
        assert result["all_checked"] is False
        assert result["total"] == 2
        assert result["checked"] == 1
        assert result["unchecked_items"] == ["pending"]

    # Test 8: reads from frontmatter when present
    def test_get_exit_criteria_from_frontmatter(self, tmp_path):
        fm = {
            "id": "infrastructure",
            "exit_criteria": [
                {"text": "bugs resolved", "checked": True},
            ],
        }
        path = _write_frontmatter_arc(tmp_path, fm)

        from arc_frontmatter import get_exit_criteria
        result = get_exit_criteria(path)

        assert result is not None
        assert result["all_checked"] is True
        assert result["total"] == 1
        assert result["checked"] == 1
        assert result["unchecked_items"] == []

    # Test 9: falls back to checkbox parsing when no frontmatter
    def test_get_exit_criteria_fallback(self, tmp_path):
        content = """\
# Arc

## Exit Criteria

- [x] done
- [ ] pending
"""
        path = _write_legacy_arc(tmp_path, content)

        from arc_frontmatter import get_exit_criteria
        result = get_exit_criteria(path)

        assert result is not None
        assert result["all_checked"] is False
        assert result["total"] == 2
        assert result["checked"] == 1
        assert result["unchecked_items"] == ["pending"]


# =========================================================================
# Tests 10-12: update_chapter_in_frontmatter
# =========================================================================
class TestUpdateChapterInFrontmatter:
    # Test 10: updates chapter status in frontmatter
    def test_update_chapter_in_frontmatter(self, tmp_path):
        fm = {
            "id": "infrastructure",
            "chapters": [
                {"id": "CH-067", "title": "FileFormatMigration", "work_items": [],
                 "requirements": [], "dependencies": [], "status": "Active"},
            ],
        }
        path = _write_frontmatter_arc(tmp_path, fm)

        from arc_frontmatter import update_chapter_in_frontmatter, parse_arc_frontmatter
        result = update_chapter_in_frontmatter(path, "CH-067", "Complete")

        assert result is True

        updated_fm = parse_arc_frontmatter(path)
        assert updated_fm["chapters"][0]["status"] == "Complete"

    # Test 11: returns False when chapter not found
    def test_update_chapter_not_found(self, tmp_path):
        fm = {
            "id": "infrastructure",
            "chapters": [
                {"id": "CH-065", "title": "BugBatch", "work_items": [],
                 "requirements": [], "dependencies": [], "status": "Complete"},
            ],
        }
        path = _write_frontmatter_arc(tmp_path, fm)

        from arc_frontmatter import update_chapter_in_frontmatter
        result = update_chapter_in_frontmatter(path, "CH-999", "Complete")

        assert result is False

    # Test 12: returns False when no frontmatter
    def test_update_chapter_no_frontmatter(self, tmp_path):
        path = _write_legacy_arc(tmp_path)

        from arc_frontmatter import update_chapter_in_frontmatter
        result = update_chapter_in_frontmatter(path, "CH-067", "Complete")

        assert result is False


# =========================================================================
# Tests 13-15: Migration
# =========================================================================
class TestMigration:
    # Test 13: migrate_file injects frontmatter into legacy ARC.md
    def test_migrate_arc_file_injects_frontmatter(self, tmp_path):
        path = _write_legacy_arc(tmp_path, ARC_INFRA_LEGACY_CONTENT)

        from migrate_arc_frontmatter import migrate_file
        result = migrate_file(path)

        assert result.get("skipped") is not True
        assert result.get("migrated") is True

        from arc_frontmatter import parse_arc_frontmatter
        fm = parse_arc_frontmatter(path)
        assert fm is not None
        assert fm["id"] == "infrastructure"
        assert len(fm["chapters"]) == 2
        assert any(c.get("checked") is True for c in fm["exit_criteria"])

        # Verify markdown body is preserved
        file_content = path.read_text(encoding="utf-8")
        assert "## Definition" in file_content or "## Purpose" in file_content

    # Test 14: migrate_file skips file already having frontmatter
    def test_migrate_arc_file_skips_existing(self, tmp_path):
        fm = {"id": "infrastructure", "status": "Planning"}
        path = _write_frontmatter_arc(tmp_path, fm)
        original_content = path.read_text(encoding="utf-8")

        from migrate_arc_frontmatter import migrate_file
        result = migrate_file(path)

        assert result.get("skipped") is True
        assert path.read_text(encoding="utf-8") == original_content

    # Test 15: migrate_file dry_run does not write
    def test_migrate_arc_file_dry_run(self, tmp_path):
        path = _write_legacy_arc(tmp_path, ARC_INFRA_LEGACY_CONTENT)
        original_content = path.read_text(encoding="utf-8")

        from migrate_arc_frontmatter import migrate_file
        result = migrate_file(path, dry_run=True)

        assert result.get("migrated") is True
        assert path.read_text(encoding="utf-8") == original_content


# =========================================================================
# Test 16: build_arc_frontmatter — parses all fields from realistic ARC.md
# =========================================================================
class TestBuildArcFrontmatter:
    def test_build_arc_frontmatter_parses_all_fields(self):
        from migrate_arc_frontmatter import build_arc_frontmatter

        result = build_arc_frontmatter(ARC_INFRA_LEGACY_CONTENT)

        assert result["id"] == "infrastructure"
        assert result["epoch"] == "E2.8"
        assert result["theme"] == "Fix what's broken"
        assert result["status"] == "Planning"
        assert result["started"] == "2026-02-17 (Session 393)"
        assert len(result["chapters"]) == 2
        assert result["chapters"][0]["id"] == "CH-065"
        assert result["chapters"][0]["status"] == "Complete"
        assert len(result["exit_criteria"]) == 1
        assert result["exit_criteria"][0]["checked"] is True


# =========================================================================
# Tests 17-19: Consumer integration
# =========================================================================
class TestConsumerIntegration:
    # Test 17: hierarchy_engine uses arc_frontmatter for chapters
    def test_hierarchy_engine_uses_arc_frontmatter(self, tmp_path):
        arcs_dir = ".claude/haios/epochs/E2_8/arcs"
        _create_haios_config(tmp_path, arcs_dir)

        # Create ARC.md with frontmatter chapters
        arc_dir = tmp_path / arcs_dir / "infrastructure"
        arc_dir.mkdir(parents=True, exist_ok=True)
        fm = {
            "id": "infrastructure",
            "chapters": [
                {"id": "CH-065", "title": "BugBatch-E28", "work_items": ["New"],
                 "requirements": ["REQ-CEREMONY-001"], "dependencies": [], "status": "Complete"},
                {"id": "CH-067", "title": "FileFormatMigration",
                 "work_items": ["WORK-244", "WORK-245"],
                 "requirements": ["REQ-TRACE-004"], "dependencies": [], "status": "Active"},
            ],
        }
        fm_yaml = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
        arc_file = arc_dir / "ARC.md"
        arc_file.write_text(f"---\n{fm_yaml}---\n# Arc\n", encoding="utf-8")

        from hierarchy_engine import HierarchyQueryEngine
        engine = HierarchyQueryEngine(base_path=tmp_path)
        chapters = engine.get_chapters("infrastructure")

        assert chapters is not None
        assert len(chapters) >= 1
        ch_ids = [ch.id for ch in chapters]
        assert "CH-065" in ch_ids
        ch065 = next(ch for ch in chapters if ch.id == "CH-065")
        assert ch065.status == "Complete"

    # Test 18: status_propagator uses arc_frontmatter for chapter update
    def test_status_propagator_uses_arc_frontmatter(self, tmp_path):
        arcs_dir = ".claude/haios/epochs/E2_8/arcs"
        _create_haios_config(tmp_path, arcs_dir)

        # Create ARC.md with frontmatter chapters
        arc_dir = tmp_path / arcs_dir / "infrastructure"
        arc_dir.mkdir(parents=True, exist_ok=True)
        fm = {
            "id": "infrastructure",
            "chapters": [
                {"id": "CH-067", "title": "FileFormatMigration",
                 "work_items": ["WORK-244", "WORK-245"],
                 "requirements": ["REQ-TRACE-004"], "dependencies": [], "status": "Active"},
            ],
        }
        fm_yaml = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
        arc_file = arc_dir / "ARC.md"
        arc_file.write_text(f"---\n{fm_yaml}---\n# Arc\n", encoding="utf-8")

        from status_propagator import StatusPropagator
        propagator = StatusPropagator(base_path=tmp_path)
        result = propagator.update_arc_chapter_status("infrastructure", "CH-067", "Complete")

        assert result["updated"] is True

        from arc_frontmatter import parse_arc_frontmatter
        updated_fm = parse_arc_frontmatter(arc_file)
        ch067 = next(ch for ch in updated_fm["chapters"] if ch["id"] == "CH-067")
        assert ch067["status"] == "Complete"

    # Test 19: dod_validation.validate_epoch_dod uses arc_frontmatter
    def test_epoch_dod_uses_arc_frontmatter(self, tmp_path):
        epoch_dir = ".claude/haios/epochs/E2_8"
        arcs_dir = f"{epoch_dir}/arcs"
        _create_haios_config(tmp_path, arcs_dir)

        # Create EPOCH.md
        epoch_path = tmp_path / epoch_dir
        epoch_path.mkdir(parents=True, exist_ok=True)
        (epoch_path / "EPOCH.md").write_text(
            "---\nid: E2.8\nstatus: Complete\n---\n# Epoch\n",
            encoding="utf-8",
        )

        # Create ARC.md with frontmatter status: Complete
        arc_dir = tmp_path / arcs_dir / "infrastructure"
        arc_dir.mkdir(parents=True, exist_ok=True)
        fm = {
            "id": "infrastructure",
            "status": "Complete",
            "chapters": [],
            "exit_criteria": [],
        }
        fm_yaml = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
        arc_file = arc_dir / "ARC.md"
        arc_file.write_text(f"---\n{fm_yaml}---\n# Arc\n", encoding="utf-8")

        from dod_validation import validate_epoch_dod
        result = validate_epoch_dod("E2_8", base_path=tmp_path)

        # Result should pass (arc status Complete, no incomplete items)
        assert result.passed is True
