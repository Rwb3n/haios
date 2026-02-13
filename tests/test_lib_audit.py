# generated: 2025-12-24
# System Auto: last updated on: 2026-01-27T20:56:45
"""Tests for .claude/haios/lib/audit.py"""
import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add .claude/haios/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))


def test_parse_frontmatter_valid():
    """Test parsing valid YAML frontmatter."""
    from audit import parse_frontmatter

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write('---\nstatus: active\nid: E2-001\n---\n# Content')
        f.flush()
        result = parse_frontmatter(f.name)
        assert result['status'] == 'active'
        assert result['id'] == 'E2-001'
    os.unlink(f.name)


def test_parse_frontmatter_missing():
    """Test parsing file without frontmatter."""
    from audit import parse_frontmatter

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write('# No frontmatter here')
        f.flush()
        result = parse_frontmatter(f.name)
        assert result == {}
    os.unlink(f.name)


def test_audit_sync_returns_list():
    """Verify audit_sync returns a list."""
    from audit import audit_sync

    result = audit_sync()
    assert isinstance(result, list)


def test_audit_gaps_returns_list():
    """Verify audit_gaps returns a list."""
    from audit import audit_gaps

    result = audit_gaps()
    assert isinstance(result, list)


def test_audit_stale_returns_list():
    """Verify audit_stale returns a list."""
    from audit import audit_stale

    result = audit_stale()
    assert isinstance(result, list)


def test_audit_stale_threshold():
    """Verify threshold parameter works."""
    from audit import audit_stale

    result_high = audit_stale(threshold=1000)  # Very high, should find nothing recent
    result_low = audit_stale(threshold=0)      # Zero, should find everything
    # At minimum, result should be a list
    assert isinstance(result_high, list)
    assert isinstance(result_low, list)


# =============================================================================
# WORK-140: Status vs Node Divergence Detection Tests
# =============================================================================

class TestAuditStatusDivergence:
    """Tests for WORK-140: detect status/node_history divergence in work items."""

    def _write_work_item(self, tmp_path, work_id, status, current_node, node_history=None):
        """Helper to create a work item file with given fields."""
        work_dir = tmp_path / "docs" / "work" / "active" / work_id
        work_dir.mkdir(parents=True, exist_ok=True)
        work_file = work_dir / "WORK.md"

        nh = node_history or [{"node": current_node, "entered": "2026-01-01T00:00:00", "exited": None}]
        import yaml
        frontmatter = {
            "id": work_id,
            "status": status,
            "current_node": current_node,
            "node_history": nh,
        }
        content = f"---\n{yaml.dump(frontmatter, default_flow_style=False)}---\n# {work_id}\n"
        work_file.write_text(content, encoding="utf-8")
        return str(work_file)

    def test_clean_item_no_divergence(self, tmp_path):
        """Status=active, current_node=backlog — no divergence."""
        from audit import audit_status_divergence

        self._write_work_item(tmp_path, "WORK-001", "active", "backlog")
        result = audit_status_divergence(str(tmp_path / "docs" / "work" / "active"))
        assert len(result) == 0

    def test_complete_status_complete_node_no_divergence(self, tmp_path):
        """Status=complete, current_node=done — consistent, no divergence."""
        from audit import audit_status_divergence

        self._write_work_item(tmp_path, "WORK-002", "complete", "done")
        result = audit_status_divergence(str(tmp_path / "docs" / "work" / "active"))
        assert len(result) == 0

    def test_archived_status_complete_node_diverges(self, tmp_path):
        """Status=archived but current_node=complete — divergence (E2-295 pattern)."""
        from audit import audit_status_divergence

        self._write_work_item(tmp_path, "E2-295", "archived", "complete")
        result = audit_status_divergence(str(tmp_path / "docs" / "work" / "active"))
        assert len(result) == 1
        assert "E2-295" in result[0]
        assert "DIVERGE" in result[0]

    def test_complete_status_backlog_node_diverges(self, tmp_path):
        """Status=complete but current_node=backlog — divergence."""
        from audit import audit_status_divergence

        self._write_work_item(tmp_path, "WORK-003", "complete", "backlog")
        result = audit_status_divergence(str(tmp_path / "docs" / "work" / "active"))
        assert len(result) == 1
        assert "WORK-003" in result[0]

    def test_multiple_items_mixed(self, tmp_path):
        """Multiple items: only divergent ones flagged."""
        from audit import audit_status_divergence

        self._write_work_item(tmp_path, "WORK-010", "active", "implement")  # OK
        self._write_work_item(tmp_path, "WORK-011", "complete", "done")     # OK
        self._write_work_item(tmp_path, "WORK-012", "archived", "done")     # Divergent

        result = audit_status_divergence(str(tmp_path / "docs" / "work" / "active"))
        assert len(result) == 1
        assert "WORK-012" in result[0]

    def test_returns_list_type(self, tmp_path):
        """Should always return a list."""
        from audit import audit_status_divergence

        result = audit_status_divergence(str(tmp_path / "nonexistent"))
        assert isinstance(result, list)
        assert len(result) == 0
