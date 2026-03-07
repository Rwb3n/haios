# generated: 2026-03-07
# WORK-244: CHAPTER.md YAML Frontmatter Migration — Tests
"""Tests for chapter_frontmatter.py and migrate_chapter_frontmatter.py.

TDD RED phase: All 19 tests written before implementation.
Tests cover:
  - Frontmatter parsing (Tests 1-2)
  - Exit criteria read with fallback (Tests 3-5)
  - Migration (Tests 6-8, 17)
  - Work item operations (Tests 9-11)
  - Consumer integration (Tests 12-16)
  - Critique fixes (Tests 18-19)
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

CH060_LEGACY_CONTENT = """\
# generated: 2026-02-19
# System Auto: last updated on: 2026-02-19T08:30:00
# Chapter: SessionBoundaryFix

## Chapter Definition

**Chapter ID:** CH-060
**Arc:** call
**Epoch:** E2.8
**Name:** Session Boundary Fix
**Status:** Complete

---

## Purpose

Govern the session boundary gap.

---

## Work Items

| ID | Title | Status | Type |
|----|-------|--------|------|
| WORK-161 | Session Boundary Fix | Complete | implementation |

---

## Exit Criteria

- [x] Post-closure ceremonies run reliably (S396)
- [x] Session-end ceremony triggered automatically (S396)
- [x] Governance events logged (S396)
- [x] No orphan sessions (S396)

---

## Dependencies

| Direction | Target | Reason |
|-----------|--------|--------|
| None | - | No inbound or outbound dependencies |

---

## References

- Memory: 85609
"""


def _write_frontmatter_chapter(tmp_path, fm_dict, body="# Chapter body\n"):
    """Helper: write CHAPTER.md with YAML frontmatter + body."""
    path = tmp_path / "CHAPTER.md"
    fm_yaml = yaml.dump(fm_dict, default_flow_style=False, allow_unicode=True, sort_keys=False)
    path.write_text(f"---\n{fm_yaml}---\n{body}", encoding="utf-8")
    return path


def _write_legacy_chapter(tmp_path, content=None):
    """Helper: write CHAPTER.md in legacy bold-markdown format."""
    path = tmp_path / "CHAPTER.md"
    path.write_text(content or CH060_LEGACY_CONTENT, encoding="utf-8")
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


def _create_chapter_in_structure(tmp_path, chapter_id, arc_name, content,
                                  epoch_dir=".claude/haios/epochs/E2_8"):
    """Helper: create CHAPTER.md in the standard directory structure."""
    # Derive chapter dir name from content or use generic
    chapter_dir = tmp_path / epoch_dir / "arcs" / arc_name / "chapters" / f"{chapter_id}-Test"
    chapter_dir.mkdir(parents=True, exist_ok=True)
    chapter_file = chapter_dir / "CHAPTER.md"
    chapter_file.write_text(content, encoding="utf-8")
    return chapter_file


def _create_work_item(tmp_path, work_id, chapter_id="", status="active"):
    """Helper: create a minimal WORK.md for a work item."""
    work_dir = tmp_path / "docs" / "work" / "active" / work_id
    work_dir.mkdir(parents=True, exist_ok=True)
    work_file = work_dir / "WORK.md"
    fm = {
        "id": work_id,
        "title": f"Test {work_id}",
        "status": status,
        "type": "implementation",
        "chapter": chapter_id,
        "arc": "call",
        "traces_to": ["REQ-TRACE-004"],
        "closed": "2026-03-07" if status == "complete" else None,
    }
    fm_yaml = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
    work_file.write_text(f"---\n{fm_yaml}---\n# {work_id}\n", encoding="utf-8")
    return work_file


# =========================================================================
# Test 1: parse_chapter_frontmatter — returns dict when frontmatter present
# =========================================================================
class TestParseChapterFrontmatter:
    def test_parse_chapter_frontmatter_returns_dict(self, tmp_path):
        fm = {"id": "CH-067", "name": "Test", "status": "Active"}
        path = _write_frontmatter_chapter(tmp_path, fm)

        from chapter_frontmatter import parse_chapter_frontmatter
        result = parse_chapter_frontmatter(path)

        assert result is not None
        assert result["id"] == "CH-067"
        assert result["name"] == "Test"
        assert result["status"] == "Active"

    # Test 2: returns None when no frontmatter
    def test_parse_chapter_frontmatter_returns_none_for_legacy(self, tmp_path):
        path = _write_legacy_chapter(tmp_path)

        from chapter_frontmatter import parse_chapter_frontmatter
        result = parse_chapter_frontmatter(path)

        assert result is None


# =========================================================================
# Tests 3-5: get_exit_criteria
# =========================================================================
class TestGetExitCriteria:
    # Test 3: reads from frontmatter when present
    def test_get_exit_criteria_from_frontmatter(self, tmp_path):
        fm = {
            "id": "CH-067",
            "exit_criteria": [
                {"text": "done", "checked": True},
                {"text": "pending", "checked": False},
            ],
        }
        path = _write_frontmatter_chapter(tmp_path, fm)

        from chapter_frontmatter import get_exit_criteria
        result = get_exit_criteria(path)

        assert result is not None
        assert result["all_checked"] is False
        assert result["total"] == 2
        assert result["checked"] == 1
        assert result["unchecked_items"] == ["pending"]

    # Test 4: falls back to regex when no frontmatter
    def test_get_exit_criteria_fallback_to_regex(self, tmp_path):
        content = """\
# Chapter

## Chapter Definition

**Chapter ID:** CH-060
**Status:** Active

## Exit Criteria

- [x] Done
- [ ] Not done

## References
"""
        path = _write_legacy_chapter(tmp_path, content)

        from chapter_frontmatter import get_exit_criteria
        result = get_exit_criteria(path)

        assert result is not None
        assert result["all_checked"] is False
        assert result["total"] == 2
        assert result["checked"] == 1
        assert result["unchecked_items"] == ["Not done"]

    # Test 5: returns None when no exit criteria section
    def test_get_exit_criteria_returns_none_when_absent(self, tmp_path):
        fm = {"id": "CH-067", "status": "Active"}  # no exit_criteria key
        path = _write_frontmatter_chapter(tmp_path, fm)

        from chapter_frontmatter import get_exit_criteria
        result = get_exit_criteria(path)

        assert result is None


# =========================================================================
# Tests 6-8: Migration
# =========================================================================
class TestMigration:
    # Test 6: migrate_file injects frontmatter into legacy file
    def test_migrate_file_injects_frontmatter(self, tmp_path):
        content = """\
# Chapter: TestChapter

## Chapter Definition

**Chapter ID:** CH-060
**Arc:** call
**Epoch:** E2.8
**Name:** TestChapter
**Status:** Active

---

## Work Items

| ID | Title | Status | Type |
|----|-------|--------|------|
| WORK-100 | Test Item | Active | implementation |

---

## Exit Criteria

- [x] Criterion one
- [ ] Criterion two

---

## Dependencies

| Direction | Target | Reason |
|-----------|--------|--------|
| None | - | No dependencies |
"""
        path = _write_legacy_chapter(tmp_path, content)

        from migrate_chapter_frontmatter import migrate_file
        result = migrate_file(path)

        assert result.get("skipped") is not True
        assert result.get("migrated") is True

        from chapter_frontmatter import parse_chapter_frontmatter
        fm = parse_chapter_frontmatter(path)
        assert fm is not None
        assert fm["id"] == "CH-060"
        assert fm["arc"] == "call"
        assert fm["epoch"] == "E2.8"
        assert fm["name"] == "TestChapter"
        assert fm["status"] == "Active"
        assert len(fm["work_items"]) == 1
        assert fm["work_items"][0]["id"] == "WORK-100"
        assert len(fm["exit_criteria"]) == 2
        assert fm["exit_criteria"][0]["checked"] is True
        assert fm["exit_criteria"][1]["checked"] is False

        # Verify markdown body is preserved
        file_content = path.read_text(encoding="utf-8")
        assert "## Purpose" in file_content or "## Chapter Definition" in file_content

    # Test 7: migrate_file skips file already having frontmatter
    def test_migrate_file_skips_existing_frontmatter(self, tmp_path):
        fm = {"id": "CH-060", "status": "Active"}
        path = _write_frontmatter_chapter(tmp_path, fm)
        original_content = path.read_text(encoding="utf-8")

        from migrate_chapter_frontmatter import migrate_file
        result = migrate_file(path)

        assert result.get("skipped") is True
        assert path.read_text(encoding="utf-8") == original_content

    # Test 8: migrate_all in dry_run mode
    def test_migrate_all_dry_run(self, tmp_path, monkeypatch):
        # Create two minimal CHAPTER.md files
        ch1_dir = tmp_path / "chapters" / "CH-001-Test"
        ch1_dir.mkdir(parents=True)
        ch1 = ch1_dir / "CHAPTER.md"
        ch1.write_text("**Chapter ID:** CH-001\n**Name:** T1\n**Arc:** a\n**Epoch:** E2\n**Status:** Active\n", encoding="utf-8")

        ch2_dir = tmp_path / "chapters" / "CH-002-Test"
        ch2_dir.mkdir(parents=True)
        ch2 = ch2_dir / "CHAPTER.md"
        ch2.write_text("**Chapter ID:** CH-002\n**Name:** T2\n**Arc:** a\n**Epoch:** E2\n**Status:** Active\n", encoding="utf-8")

        original1 = ch1.read_text(encoding="utf-8")
        original2 = ch2.read_text(encoding="utf-8")

        from migrate_chapter_frontmatter import migrate_file
        r1 = migrate_file(ch1, dry_run=True)
        r2 = migrate_file(ch2, dry_run=True)

        # In dry_run, files should not be written
        assert r1.get("migrated") is True or r1.get("dry_run") is True
        assert ch1.read_text(encoding="utf-8") == original1
        assert ch2.read_text(encoding="utf-8") == original2


# =========================================================================
# Tests 9-11: Work item operations
# =========================================================================
class TestWorkItemOperations:
    # Test 9: add_work_item_to_frontmatter
    def test_add_work_item_to_frontmatter(self, tmp_path):
        fm = {
            "id": "CH-067",
            "work_items": [
                {"id": "WORK-001", "title": "Old", "status": "Active", "type": "implementation"},
            ],
        }
        path = _write_frontmatter_chapter(tmp_path, fm)

        from chapter_frontmatter import add_work_item_to_frontmatter
        result = add_work_item_to_frontmatter(path, "WORK-002", "New", "Backlog", "investigation")

        assert result is True

        from chapter_frontmatter import parse_chapter_frontmatter
        updated_fm = parse_chapter_frontmatter(path)
        assert len(updated_fm["work_items"]) == 2
        new_item = next(i for i in updated_fm["work_items"] if i["id"] == "WORK-002")
        assert new_item["title"] == "New"
        assert new_item["status"] == "Backlog"
        assert new_item["type"] == "investigation"

    # Test 10: add_work_item returns False for duplicate
    def test_add_work_item_duplicate_returns_false(self, tmp_path):
        fm = {
            "id": "CH-067",
            "work_items": [
                {"id": "WORK-001", "title": "Old", "status": "Active", "type": "implementation"},
            ],
        }
        path = _write_frontmatter_chapter(tmp_path, fm)

        from chapter_frontmatter import add_work_item_to_frontmatter
        result = add_work_item_to_frontmatter(path, "WORK-001", "Old Again")

        assert result is False

        from chapter_frontmatter import parse_chapter_frontmatter
        updated_fm = parse_chapter_frontmatter(path)
        assert len(updated_fm["work_items"]) == 1

    # Test 11: update_work_item_in_frontmatter
    def test_update_work_item_status_in_frontmatter(self, tmp_path):
        fm = {
            "id": "CH-067",
            "work_items": [
                {"id": "WORK-001", "title": "Item", "status": "Active", "type": "implementation"},
            ],
        }
        path = _write_frontmatter_chapter(tmp_path, fm)

        from chapter_frontmatter import update_work_item_in_frontmatter
        result = update_work_item_in_frontmatter(path, "WORK-001", "Complete")

        assert result is True

        from chapter_frontmatter import parse_chapter_frontmatter
        updated_fm = parse_chapter_frontmatter(path)
        assert updated_fm["work_items"][0]["status"] == "Complete"


# =========================================================================
# Tests 12-14: Consumer integration (status_propagator, dod_validation)
# =========================================================================
class TestConsumerIntegration:
    # Test 12: status_propagator._check_exit_criteria uses frontmatter
    def test_status_propagator_uses_frontmatter_exit_criteria(self, tmp_path):
        # Create haios.yaml
        arcs_dir = ".claude/haios/epochs/E2_8/arcs"
        _create_haios_config(tmp_path, arcs_dir)

        # Create CHAPTER.md with frontmatter
        fm = {
            "id": "CH-060",
            "exit_criteria": [
                {"text": "Done criterion", "checked": True},
                {"text": "Pending criterion", "checked": False},
            ],
        }
        fm_yaml = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
        chapter_dir = (
            tmp_path / arcs_dir / "call" / "chapters" / "CH-060-Test"
        )
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_file = chapter_dir / "CHAPTER.md"
        chapter_file.write_text(f"---\n{fm_yaml}---\n# Chapter\n", encoding="utf-8")

        # Create work item for the chapter
        _create_work_item(tmp_path, "WORK-161", "CH-060", "complete")

        from status_propagator import StatusPropagator
        propagator = StatusPropagator(base_path=tmp_path)
        result = propagator._check_exit_criteria("CH-060", "call")

        assert result is not None
        assert result["all_checked"] is False
        assert result["total"] == 2
        assert result["checked"] == 1
        assert "Pending criterion" in result["unchecked_items"]

    # Test 13: dod_validation.validate_chapter_dod with frontmatter
    def test_validate_chapter_dod_with_frontmatter(self, tmp_path):
        # Create CHAPTER.md with all criteria checked
        fm = {
            "id": "CH-015",
            "status": "Complete",
            "exit_criteria": [
                {"text": "Criterion 1", "checked": True},
                {"text": "Criterion 2", "checked": True},
            ],
        }
        fm_yaml = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
        epoch_dir = ".claude/haios/epochs/E2_5"
        chapter_dir = tmp_path / epoch_dir / "arcs" / "ceremonies" / "chapters" / "CH-015-Test"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_file = chapter_dir / "CHAPTER.md"
        chapter_file.write_text(f"---\n{fm_yaml}---\n# Chapter\n", encoding="utf-8")

        # Create complete work item
        _create_work_item(tmp_path, "WORK-100", "CH-015", "complete")

        from dod_validation import validate_chapter_dod
        result = validate_chapter_dod("CH-015", "ceremonies", base_path=tmp_path, epoch_dir=epoch_dir)

        assert result.passed is True

    # Test 14: dod_validation falls back to regex for legacy format
    def test_validate_chapter_dod_legacy_fallback(self, tmp_path):
        epoch_dir = ".claude/haios/epochs/E2_5"
        # Create legacy CHAPTER.md (flat file, no frontmatter)
        arc_dir = tmp_path / epoch_dir / "arcs" / "ceremonies"
        arc_dir.mkdir(parents=True, exist_ok=True)
        chapter_file = arc_dir / "CH-015-ClosureCeremonies.md"
        chapter_file.write_text(
            "**Status:** Active\n\n## Exit Criteria\n\n- [x] Done\n- [ ] Not done\n",
            encoding="utf-8",
        )

        # Create complete work item
        _create_work_item(tmp_path, "WORK-100", "CH-015", "complete")

        from dod_validation import validate_chapter_dod
        result = validate_chapter_dod("CH-015", "ceremonies", base_path=tmp_path, epoch_dir=epoch_dir)

        assert result.passed is False
        assert any("Exit criteria" in f or "exit criteria" in f for f in result.failures)


# =========================================================================
# Tests 15-16: Scaffold consumer integration
# =========================================================================
class TestScaffoldIntegration:
    # Test 15: update_chapter_manifest uses frontmatter
    def test_update_chapter_manifest_uses_frontmatter(self, tmp_path):
        fm = {
            "id": "CH-060",
            "work_items": [],
        }
        fm_yaml = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
        chapter_dir = (
            tmp_path / ".claude" / "haios" / "epochs" / "E2_8" / "arcs" / "call"
            / "chapters" / "CH-060-Test"
        )
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_file = chapter_dir / "CHAPTER.md"
        chapter_file.write_text(f"---\n{fm_yaml}---\n# Chapter\n\n## Work Items\n\n| ID | Title | Status | Type |\n|----|-------|--------|------|\n", encoding="utf-8")

        from scaffold import update_chapter_manifest
        result = update_chapter_manifest("WORK-NEW", "Title", "CH-060", base_path=tmp_path)

        assert result["updated"] is True

        from chapter_frontmatter import parse_chapter_frontmatter
        updated_fm = parse_chapter_frontmatter(chapter_file)
        assert any(i["id"] == "WORK-NEW" for i in updated_fm["work_items"])

    # Test 16: update_chapter_manifest falls back to line insertion
    def test_update_chapter_manifest_legacy_fallback(self, tmp_path):
        # Create legacy CHAPTER.md (no frontmatter)
        chapter_dir = (
            tmp_path / ".claude" / "haios" / "epochs" / "E2_8" / "arcs" / "call"
            / "chapters" / "CH-060-Test"
        )
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_file = chapter_dir / "CHAPTER.md"
        chapter_file.write_text(
            "# Chapter\n\n## Work Items\n\n| ID | Title | Status | Type |\n|----|-------|--------|------|\n| WORK-001 | Old | Active | implementation |\n\n---\n",
            encoding="utf-8",
        )

        from scaffold import update_chapter_manifest
        result = update_chapter_manifest("WORK-NEW", "Title", "CH-060", base_path=tmp_path)

        assert result["updated"] is True
        assert result["reason"] == "row_added"

        content = chapter_file.read_text(encoding="utf-8")
        assert "| WORK-NEW |" in content


# =========================================================================
# Test 17: build_frontmatter parses all fields from realistic CHAPTER.md
# =========================================================================
class TestBuildFrontmatter:
    def test_build_frontmatter_parses_all_fields(self):
        from migrate_chapter_frontmatter import build_frontmatter

        result = build_frontmatter(CH060_LEGACY_CONTENT)

        assert result["id"] == "CH-060"
        assert result["arc"] == "call"
        assert result["epoch"] == "E2.8"
        assert result["name"] == "Session Boundary Fix"
        assert result["status"] == "Complete"
        assert len(result["exit_criteria"]) == 4
        assert all(c["checked"] for c in result["exit_criteria"])
        assert len(result["work_items"]) == 1
        assert result["work_items"][0]["id"] == "WORK-161"
        assert result["dependencies"] == []


# =========================================================================
# Test 18: _write_frontmatter preserves body with multiple --- separators
# =========================================================================
class TestWriteFrontmatterRoundTrip:
    def test_write_frontmatter_preserves_body_separators(self, tmp_path):
        path = tmp_path / "CHAPTER.md"
        content = """\
---
id: CH-067
status: Active
work_items:
- id: WORK-NEW
  title: New
  status: Active
  type: implementation
---
# Chapter

---

## Section

Some content here.

---

## Another

More content.
"""
        path.write_text(content, encoding="utf-8")

        from chapter_frontmatter import update_work_item_in_frontmatter, parse_chapter_frontmatter
        result = update_work_item_in_frontmatter(path, "WORK-NEW", "Complete")

        assert result is True

        # Verify frontmatter updated
        fm = parse_chapter_frontmatter(path)
        assert fm["work_items"][0]["status"] == "Complete"

        # Verify body preserved
        file_content = path.read_text(encoding="utf-8")
        assert "## Section" in file_content
        assert "Some content here." in file_content
        assert "## Another" in file_content
        assert "More content." in file_content
        # Count --- in file: should have at least 4 (2 frontmatter + 2 body)
        assert file_content.count("---") >= 4


# =========================================================================
# Test 19: update_chapter_manifest_status finds frontmatter-only work item
# =========================================================================
class TestFrontmatterOnlyWorkItem:
    def test_update_chapter_manifest_status_frontmatter_only_item(self, tmp_path):
        """Work item exists in frontmatter but NOT in markdown table body.
        After A6 fix, update_chapter_manifest_status should find it via frontmatter."""
        fm = {
            "id": "CH-067",
            "work_items": [
                {"id": "WORK-NEW", "title": "New", "status": "Active", "type": "implementation"},
            ],
        }
        fm_yaml = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
        chapter_dir = (
            tmp_path / ".claude" / "haios" / "epochs" / "E2_8" / "arcs" / "infrastructure"
            / "chapters" / "CH-067-Test"
        )
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_file = chapter_dir / "CHAPTER.md"
        # Note: NO | WORK-NEW | row in the markdown table
        chapter_file.write_text(
            f"---\n{fm_yaml}---\n# Chapter\n\n## Work Items\n\n| ID | Title | Status | Type |\n|----|-------|--------|------|\n\n---\n",
            encoding="utf-8",
        )

        from scaffold import update_chapter_manifest_status
        result = update_chapter_manifest_status("WORK-NEW", "CH-067", "Complete", base_path=tmp_path)

        assert result["updated"] is True

        # Verify frontmatter was updated
        from chapter_frontmatter import parse_chapter_frontmatter
        updated_fm = parse_chapter_frontmatter(chapter_file)
        assert updated_fm["work_items"][0]["status"] == "Complete"
