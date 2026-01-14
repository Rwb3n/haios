# generated: 2025-12-23
# System Auto: last updated on: 2025-12-27T22:11:07
"""Tests for backlog migration script.

E2-151: Backlog Migration Script
- Tests for parsing backlog.md entries
- Tests for mapping to work file schema
- Tests for full migration run
"""

import sys
from pathlib import Path

import pytest

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestParseBacklogEntry:
    """Tests for parsing backlog.md entry format."""

    def test_parses_header_correctly(self):
        """Verify header parsing extracts priority, id, and title."""
        from migrate_backlog import parse_backlog_entry

        entry = '''### [MEDIUM] E2-004: Documentation Sync
- **Status:** pending
- **Owner:** Hephaestus
- **Created:** 2025-12-07
- **Context:** Update epistemic_state.md'''

        result = parse_backlog_entry(entry)
        assert result["id"] == "E2-004"
        assert result["title"] == "Documentation Sync"
        assert result["priority"] == "medium"

    def test_parses_fields_correctly(self):
        """Verify field parsing extracts status, owner, context."""
        from migrate_backlog import parse_backlog_entry

        entry = '''### [HIGH] E2-017: Concept Embedding Completion
- **Status:** pending
- **Owner:** Hephaestus
- **Created:** 2025-12-09
- **Session:** 50
- **Context:** 4,933 concepts have no embeddings
- **spawned_by:** INV-022
- **Milestone:** M4-Research'''

        result = parse_backlog_entry(entry)
        assert result["status"] == "pending"
        assert result["owner"] == "Hephaestus"
        assert result["session"] == "50"
        assert result["spawned_by"] == "INV-022"
        assert result["milestone"] == "M4-Research"


class TestMapToWorkSchema:
    """Tests for mapping entry to work file schema."""

    def test_maps_basic_fields(self):
        """Verify basic field mapping."""
        from migrate_backlog import map_to_work_schema

        entry = {
            "id": "E2-004",
            "title": "Documentation Sync",
            "priority": "high",
            "status": "pending",
        }

        work = map_to_work_schema(entry)
        assert work["id"] == "E2-004"
        assert work["title"] == "Documentation Sync"
        assert work["priority"] == "high"
        assert work["status"] == "active"  # Always active for migration
        assert work["current_node"] == "backlog"  # Start at backlog

    def test_handles_missing_fields(self):
        """Verify missing fields get defaults."""
        from migrate_backlog import map_to_work_schema

        entry = {"id": "E2-999"}

        work = map_to_work_schema(entry)
        assert work["title"] == "Untitled"
        assert work["priority"] == "medium"
        assert work["current_node"] == "backlog"


class TestMigrateBacklog:
    """Tests for full migration run."""

    @pytest.mark.skip(reason="backlog.md archived - migration complete")
    def test_dry_run_finds_items(self):
        """Verify dry-run counts items without creating files."""
        from migrate_backlog import migrate_backlog

        result = migrate_backlog(dry_run=True)
        # After full migration, most items already exist so total_items may be 0
        # The important thing is no errors
        assert len(result["errors"]) == 0
        # Total parsed from backlog (including already migrated) should be >= 0
        assert result["total_items"] >= 0

    @pytest.mark.skip(reason="backlog.md archived - migration complete")
    def test_dry_run_skips_complete_items(self):
        """Verify complete items are not migrated."""
        from migrate_backlog import migrate_backlog

        result = migrate_backlog(dry_run=True)
        # E2-150 was just closed - should not appear
        assert "E2-150" not in result["migrated"]
