# generated: 2026-02-19
"""
Tests for plan_tree.py --ready blocked_by filter (WORK-175).

Verifies that plan_tree.py --ready output matches WorkEngine.get_ready() semantics:
- Items with unclosed blocked_by entries are excluded
- Items with terminal-status blockers are included (unblocked)
- Items with empty blocked_by are included
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add scripts directory to path for import
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


class TestPlanTreeReadyFilter:
    """WORK-175: plan_tree.py --ready must filter blocked_by."""

    def _create_work_item(self, tmp_path, work_id, status="active",
                          blocked_by=None, title="Test Item",
                          queue_position="backlog"):
        """Helper to create a work item directory with WORK.md."""
        work_dir = tmp_path / "docs" / "work" / "active" / work_id
        work_dir.mkdir(parents=True, exist_ok=True)
        blocked_by = blocked_by or []

        # Use YAML list format (the format that plan_tree.py must handle)
        blocked_list = "\n".join(f"  - {b}" for b in blocked_by) if blocked_by else ""
        blocked_yaml = f"blocked_by:\n{blocked_list}" if blocked_by else "blocked_by: []"

        content = f"""---
id: {work_id}
title: "{title}"
status: {status}
queue_position: {queue_position}
{blocked_yaml}
---
# {work_id}: {title}
"""
        (work_dir / "WORK.md").write_text(content)
        return work_dir

    def test_blocked_items_excluded_from_ready(self, tmp_path, monkeypatch):
        """Items with unclosed blockers must NOT appear in --ready output."""
        # Create blocker (active, not closed)
        self._create_work_item(tmp_path, "WORK-100", status="active",
                               title="Active Blocker")
        # Create blocked item
        self._create_work_item(tmp_path, "WORK-101", status="active",
                               blocked_by=["WORK-100"],
                               title="Blocked Item")
        # Create unblocked item
        self._create_work_item(tmp_path, "WORK-102", status="active",
                               title="Unblocked Item")

        monkeypatch.chdir(tmp_path)

        # Capture output
        import plan_tree
        import importlib
        importlib.reload(plan_tree)

        from io import StringIO
        captured = StringIO()
        monkeypatch.setattr(sys, "argv", ["plan_tree.py", "--ready"])
        monkeypatch.setattr(sys, "stdout", captured)

        # Mock load_status to return empty milestones (deprecated)
        with patch.object(plan_tree, "load_status", return_value={"milestones": {}}):
            plan_tree.main()

        output = captured.getvalue()
        assert "WORK-102" in output, "Unblocked item should appear"
        assert "WORK-101" not in output, "Blocked item should NOT appear"

    def test_items_with_closed_blockers_are_ready(self, tmp_path, monkeypatch):
        """Items whose blockers are all complete should appear as ready."""
        # Create completed blocker
        self._create_work_item(tmp_path, "WORK-200", status="complete",
                               title="Completed Blocker")
        # Create item blocked by completed blocker
        self._create_work_item(tmp_path, "WORK-201", status="active",
                               blocked_by=["WORK-200"],
                               title="Was Blocked Now Ready")

        monkeypatch.chdir(tmp_path)

        import plan_tree
        import importlib
        importlib.reload(plan_tree)

        from io import StringIO
        captured = StringIO()
        monkeypatch.setattr(sys, "argv", ["plan_tree.py", "--ready"])
        monkeypatch.setattr(sys, "stdout", captured)

        with patch.object(plan_tree, "load_status", return_value={"milestones": {}}):
            plan_tree.main()

        output = captured.getvalue()
        assert "WORK-201" in output, "Item with completed blocker should appear as ready"

    def test_terminal_statuses_excluded(self, tmp_path, monkeypatch):
        """Items with terminal statuses should not appear in ready list."""
        self._create_work_item(tmp_path, "WORK-300", status="complete",
                               title="Complete Item")
        self._create_work_item(tmp_path, "WORK-301", status="active",
                               title="Active Item")

        monkeypatch.chdir(tmp_path)

        import plan_tree
        import importlib
        importlib.reload(plan_tree)

        from io import StringIO
        captured = StringIO()
        monkeypatch.setattr(sys, "argv", ["plan_tree.py", "--ready"])
        monkeypatch.setattr(sys, "stdout", captured)

        with patch.object(plan_tree, "load_status", return_value={"milestones": {}}):
            plan_tree.main()

        output = captured.getvalue()
        assert "WORK-300" not in output, "Complete item should NOT appear"
        assert "WORK-301" in output, "Active item should appear"

    def test_yaml_list_blocked_by_parsed(self, tmp_path, monkeypatch):
        """blocked_by in YAML list format (not inline) must be parsed correctly."""
        # Create blocker
        self._create_work_item(tmp_path, "WORK-400", status="active",
                               title="Blocker")
        # Create blocked item with YAML list format blocked_by
        work_dir = tmp_path / "docs" / "work" / "active" / "WORK-401"
        work_dir.mkdir(parents=True, exist_ok=True)
        content = """---
id: WORK-401
title: "Blocked via YAML list"
status: active
blocked_by:
- WORK-400
---
# WORK-401
"""
        (work_dir / "WORK.md").write_text(content)

        monkeypatch.chdir(tmp_path)

        import plan_tree
        import importlib
        importlib.reload(plan_tree)

        from io import StringIO
        captured = StringIO()
        monkeypatch.setattr(sys, "argv", ["plan_tree.py", "--ready"])
        monkeypatch.setattr(sys, "stdout", captured)

        with patch.object(plan_tree, "load_status", return_value={"milestones": {}}):
            plan_tree.main()

        output = captured.getvalue()
        assert "WORK-401" not in output, "YAML-list blocked item should NOT appear"
