# generated: 2025-12-23
# System Auto: last updated on: 2025-12-23T11:36:07
"""
Tests for Investigation Status Sync Hook (E2-140).

Tests the synchronization of investigation file status when INV-* items
are archived to backlog-complete.md.
"""
import sys
from pathlib import Path

import pytest

# Add hook handlers to path for importing
hooks_dir = Path(__file__).parent.parent / ".claude" / "hooks" / "hooks"
if str(hooks_dir) not in sys.path:
    sys.path.insert(0, str(hooks_dir))


class TestExtractInvIds:
    """Test extraction of INV-* IDs from backlog archive."""

    def test_sync_detects_inv_in_backlog_archive(self, tmp_path):
        """When backlog-complete.md contains INV-* completion, detect the ID."""
        from post_tool_use import _extract_inv_ids_from_archive

        archive_file = tmp_path / "backlog-complete.md"
        archive_file.write_text("""### [COMPLETE] INV-022: Work-Cycle-DAG
- **Status:** complete
""")

        # Should detect INV-022 needs sync
        result = _extract_inv_ids_from_archive(archive_file)
        assert "INV-022" in result

    def test_sync_detects_multiple_inv_ids(self, tmp_path):
        """Multiple INV-* items should all be detected."""
        from post_tool_use import _extract_inv_ids_from_archive

        archive_file = tmp_path / "backlog-complete.md"
        archive_file.write_text("""### [COMPLETE] INV-008: Status Optimization
- **Status:** complete

### [COMPLETE] INV-022: Work-Cycle-DAG
- **Status:** complete

### [COMPLETE] INV-1234: Future Investigation
- **Status:** complete
""")

        result = _extract_inv_ids_from_archive(archive_file)
        assert "INV-008" in result
        assert "INV-022" in result
        assert "INV-1234" in result

    def test_sync_skips_non_inv_items(self, tmp_path):
        """E2-* items should not trigger investigation sync."""
        from post_tool_use import _extract_inv_ids_from_archive

        archive_file = tmp_path / "backlog-complete.md"
        archive_file.write_text("""### [COMPLETE] E2-140: Investigation Status Sync
- **Status:** complete
""")

        # Should NOT detect any INV IDs
        result = _extract_inv_ids_from_archive(archive_file)
        assert len(result) == 0


class TestSyncInvestigationStatus:
    """Test updating investigation file status."""

    def test_sync_updates_investigation_file_status(self, tmp_path):
        """When INV-* is archived, update corresponding investigation file."""
        from post_tool_use import _sync_investigation_status_for_id

        # Setup investigation file with status: active
        inv_dir = tmp_path / "docs" / "investigations"
        inv_dir.mkdir(parents=True)
        inv_file = inv_dir / "INVESTIGATION-INV-022-work-cycle-dag.md"
        inv_file.write_text("""---
template: investigation
status: active
backlog_id: INV-022
---
# Content
""")

        # Call sync function
        _sync_investigation_status_for_id("INV-022", tmp_path)

        # Verify status changed
        content = inv_file.read_text()
        assert "status: complete" in content
        assert "status: active" not in content

    def test_sync_handles_missing_investigation_file(self, tmp_path):
        """If investigation file not found, should not crash."""
        from post_tool_use import _sync_investigation_status_for_id

        # No investigation file exists
        result = _sync_investigation_status_for_id("INV-999", tmp_path)

        # Should return None gracefully
        assert result is None

    def test_sync_preserves_other_frontmatter_fields(self, tmp_path):
        """Sync should only change status, preserving other fields."""
        from post_tool_use import _sync_investigation_status_for_id

        inv_dir = tmp_path / "docs" / "investigations"
        inv_dir.mkdir(parents=True)
        inv_file = inv_dir / "INVESTIGATION-INV-010-test.md"
        inv_file.write_text("""---
template: investigation
status: active
backlog_id: INV-010
date: 2025-12-23
author: Hephaestus
memory_refs: [12345, 67890]
---
# Content here
Some markdown content.
""")

        _sync_investigation_status_for_id("INV-010", tmp_path)

        content = inv_file.read_text()
        # Status changed
        assert "status: complete" in content
        # Other fields preserved
        assert "template: investigation" in content
        assert "backlog_id: INV-010" in content
        assert "date: 2025-12-23" in content
        assert "author: Hephaestus" in content
        assert "memory_refs: [12345, 67890]" in content
        assert "# Content here" in content
        assert "Some markdown content." in content

    def test_sync_skips_already_complete(self, tmp_path):
        """Should skip files that already have status: complete."""
        from post_tool_use import _sync_investigation_status_for_id

        inv_dir = tmp_path / "docs" / "investigations"
        inv_dir.mkdir(parents=True)
        inv_file = inv_dir / "INVESTIGATION-INV-005-already-done.md"
        original_content = """---
template: investigation
status: complete
backlog_id: INV-005
---
# Content
"""
        inv_file.write_text(original_content)

        result = _sync_investigation_status_for_id("INV-005", tmp_path)

        # Should skip (return None) and not modify file
        assert result is None
        assert inv_file.read_text() == original_content
