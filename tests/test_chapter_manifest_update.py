# generated: 2026-02-19
# WORK-177: Chapter Manifest Auto-Update on Work Creation
"""Tests for update_chapter_manifest() in scaffold.py.

Verifies that chapter CHAPTER.md work items tables are auto-updated
when work items are created with a CHAPTER variable.

TDD: These tests are written BEFORE the implementation.
"""

import sys
from pathlib import Path
import pytest

# Add .claude/haios/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))


def _create_chapter_file(tmp_path, chapter_id, chapter_name, work_items=None):
    """Helper: create a minimal CHAPTER.md with work items table."""
    work_items = work_items or []
    rows = "\n".join(
        f"| {wid} | {wtitle} | {wstatus} | {wtype} |"
        for wid, wtitle, wstatus, wtype in work_items
    )
    content = f"""# Chapter: {chapter_name}

## Chapter Definition

**Chapter ID:** {chapter_id}

---

## Work Items

| ID | Title | Status | Type |
|----|-------|--------|------|
{rows}

---

## Exit Criteria

- [ ] Placeholder
"""
    # Create epoch/arc/chapter directory structure
    chapter_dir = (
        tmp_path / ".claude" / "haios" / "epochs" / "E2_8" / "arcs" / "call"
        / "chapters" / f"{chapter_id}-{chapter_name}"
    )
    chapter_dir.mkdir(parents=True, exist_ok=True)
    chapter_file = chapter_dir / "CHAPTER.md"
    chapter_file.write_text(content, encoding="utf-8")
    return chapter_file


class TestUpdateChapterManifest:
    """Tests for the standalone update_chapter_manifest() function."""

    def test_chapter_manifest_updated_on_scaffold(self, tmp_path):
        """Test 1: When scaffold_template creates a work_item with CHAPTER variable,
        the chapter's CHAPTER.md work items table gets a new row."""
        import scaffold

        _create_chapter_file(
            tmp_path, "CH-059", "CeremonyAutomation",
            work_items=[("WORK-160", "Ceremony Automation", "Active", "implementation")],
        )

        result = scaffold.update_chapter_manifest(
            work_id="WORK-180",
            title="New Work Item",
            chapter_id="CH-059",
            work_type="implementation",
            base_path=tmp_path,
        )

        assert result["updated"] is True
        assert result["reason"] == "row_added"

        # Verify the row is in the file
        chapter_file = result["chapter_file"]
        content = Path(chapter_file).read_text(encoding="utf-8")
        assert "| WORK-180 |" in content
        assert "| New Work Item |" in content
        assert "| Backlog |" in content

    def test_chapter_manifest_missing_file_no_error(self, tmp_path):
        """Test 2: When CHAPTER.md doesn't exist, returns not-found without error."""
        import scaffold

        result = scaffold.update_chapter_manifest(
            work_id="WORK-180",
            title="New Work Item",
            chapter_id="CH-999",
            work_type="implementation",
            base_path=tmp_path,
        )

        assert result["updated"] is False
        assert result["reason"] == "chapter_file_not_found"
        assert result["chapter_file"] is None

    def test_no_chapter_update_without_variable(self, tmp_path):
        """Test 3: When no CHAPTER variable, chapter manifest is not modified."""
        import scaffold

        chapter_file = _create_chapter_file(
            tmp_path, "CH-059", "CeremonyAutomation",
            work_items=[("WORK-160", "Ceremony Automation", "Active", "implementation")],
        )

        original_content = chapter_file.read_text(encoding="utf-8")

        # Call scaffold_template WITHOUT CHAPTER variable — mock the file write parts
        # The key assertion is that update_chapter_manifest is NOT called by
        # scaffold_template when CHAPTER is absent. We verify by checking the file.
        # Since scaffold_template only calls the update when variables.get("CHAPTER"),
        # we verify the function's conditional logic by checking the chapter file unchanged.

        # Direct test: calling update_chapter_manifest with empty chapter_id
        # should return chapter_file_not_found (no glob match for empty string)
        result = scaffold.update_chapter_manifest(
            work_id="WORK-180",
            title="New Work Item",
            chapter_id="",
            work_type="implementation",
            base_path=tmp_path,
        )

        assert result["updated"] is False
        # File unchanged
        assert chapter_file.read_text(encoding="utf-8") == original_content

    def test_update_chapter_manifest_standalone(self, tmp_path):
        """Test 4: update_chapter_manifest() can be called independently
        and correctly appends a row to the work items table."""
        import scaffold

        chapter_file = _create_chapter_file(
            tmp_path, "CH-062", "ProgressiveContracts",
            work_items=[
                ("WORK-163", "Progressive Contracts", "Backlog", "implementation"),
            ],
        )

        result = scaffold.update_chapter_manifest(
            work_id="WORK-190",
            title="Contract Validation",
            chapter_id="CH-062",
            work_type="investigation",
            base_path=tmp_path,
        )

        assert result["updated"] is True
        assert result["reason"] == "row_added"

        content = chapter_file.read_text(encoding="utf-8")
        # Both original and new row present
        assert "| WORK-163 |" in content
        assert "| WORK-190 | Contract Validation | Backlog | investigation |" in content

    def test_no_duplicate_row_on_second_call(self, tmp_path):
        """Test 5: Calling update_chapter_manifest twice for same work ID
        doesn't duplicate the row."""
        import scaffold

        _create_chapter_file(
            tmp_path, "CH-059", "CeremonyAutomation",
            work_items=[("WORK-160", "Ceremony Automation", "Active", "implementation")],
        )

        # First call
        result1 = scaffold.update_chapter_manifest(
            work_id="WORK-180",
            title="New Work Item",
            chapter_id="CH-059",
            work_type="implementation",
            base_path=tmp_path,
        )
        assert result1["updated"] is True

        # Second call — same work ID
        result2 = scaffold.update_chapter_manifest(
            work_id="WORK-180",
            title="New Work Item",
            chapter_id="CH-059",
            work_type="implementation",
            base_path=tmp_path,
        )
        assert result2["updated"] is False
        assert result2["reason"] == "already_present"

        # Verify only one row
        content = Path(result1["chapter_file"]).read_text(encoding="utf-8")
        assert content.count("| WORK-180 |") == 1

    def test_table_not_found_in_chapter_file(self, tmp_path):
        """Test 6: When CHAPTER.md exists but has no '## Work Items' section,
        returns table_not_found."""
        import scaffold

        # Create a CHAPTER.md WITHOUT a Work Items table
        chapter_dir = (
            tmp_path / ".claude" / "haios" / "epochs" / "E2_8" / "arcs" / "call"
            / "chapters" / "CH-099-NoTable"
        )
        chapter_dir.mkdir(parents=True, exist_ok=True)
        chapter_file = chapter_dir / "CHAPTER.md"
        chapter_file.write_text(
            "# Chapter: NoTable\n\n## Purpose\n\nSome purpose.\n\n---\n",
            encoding="utf-8",
        )

        result = scaffold.update_chapter_manifest(
            work_id="WORK-180",
            title="New Work Item",
            chapter_id="CH-099",
            work_type="implementation",
            base_path=tmp_path,
        )

        assert result["updated"] is False
        assert result["reason"] == "table_not_found"
        assert result["chapter_file"] is not None  # File exists, just no table


class TestUpdateChapterManifestStatus:
    """Tests for update_chapter_manifest_status() — WORK-204 closure-side."""

    def test_chapter_manifest_status_updated_on_close(self, tmp_path):
        """Test 1: When closing a work item, the chapter's CHAPTER.md
        work items table row status is updated to 'Complete'."""
        import scaffold

        _create_chapter_file(
            tmp_path, "CH-059", "CeremonyAutomation",
            work_items=[
                ("WORK-160", "Ceremony Automation", "Complete", "implementation"),
                ("WORK-204", "Chapter Manifest Auto-Update", "Active", "implementation"),
            ],
        )

        result = scaffold.update_chapter_manifest_status(
            work_id="WORK-204",
            chapter_id="CH-059",
            base_path=tmp_path,
        )

        assert result["updated"] is True
        assert result["reason"] == "status_updated"

        # Verify the status column changed
        content = Path(result["chapter_file"]).read_text(encoding="utf-8")
        assert "| WORK-204 | Chapter Manifest Auto-Update | Complete | implementation |" in content
        # Other rows unchanged
        assert "| WORK-160 | Ceremony Automation | Complete | implementation |" in content

    def test_chapter_manifest_status_missing_file_no_error(self, tmp_path):
        """Test 2: When CHAPTER.md doesn't exist, returns graceful failure."""
        import scaffold

        result = scaffold.update_chapter_manifest_status(
            work_id="WORK-204",
            chapter_id="CH-999",
            base_path=tmp_path,
        )

        assert result["updated"] is False
        assert result["reason"] == "chapter_file_not_found"
        assert result["chapter_file"] is None

    def test_chapter_manifest_status_work_not_in_table(self, tmp_path):
        """Test 3: When work ID is not in the chapter table, returns graceful result."""
        import scaffold

        chapter_file = _create_chapter_file(
            tmp_path, "CH-059", "CeremonyAutomation",
            work_items=[
                ("WORK-160", "Ceremony Automation", "Active", "implementation"),
            ],
        )

        original_content = chapter_file.read_text(encoding="utf-8")

        result = scaffold.update_chapter_manifest_status(
            work_id="WORK-999",
            chapter_id="CH-059",
            base_path=tmp_path,
        )

        assert result["updated"] is False
        assert result["reason"] == "work_id_not_found"
        # File unchanged
        assert chapter_file.read_text(encoding="utf-8") == original_content
