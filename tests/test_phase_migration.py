"""Tests for phase migration — sync_work_md_phase and integration (WORK-171)."""
import json
import sys
from pathlib import Path

import pytest

# Ensure lib/ is on path
lib_dir = Path(__file__).parent.parent / ".claude" / "haios" / "lib"
if str(lib_dir) not in sys.path:
    sys.path.insert(0, str(lib_dir))

# Ensure modules/ is on path (for cycle_runner import in monkeypatch)
modules_dir = Path(__file__).parent.parent / ".claude" / "haios" / "modules"
if str(modules_dir) not in sys.path:
    sys.path.insert(0, str(modules_dir))

from cycle_state import sync_work_md_phase, advance_cycle_phase
import cycle_runner  # Required for monkeypatch target


class TestSyncWorkMdPhase:
    """Tests for sync_work_md_phase() — targeted WORK.md cycle_phase writes."""

    def test_updates_cycle_phase_field(self, tmp_path):
        """Writes cycle_phase field to WORK.md frontmatter."""
        work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
        work_dir.mkdir(parents=True)
        work_file = work_dir / "WORK.md"
        work_file.write_text(
            "---\nid: WORK-999\ncycle_phase: PLAN\nstatus: active\n---\n# Content\n"
        )
        result = sync_work_md_phase("WORK-999", "DO", project_root=tmp_path)
        assert result is True
        content = work_file.read_text()
        assert "cycle_phase: DO" in content
        assert "cycle_phase: PLAN" not in content

    def test_preserves_other_frontmatter(self, tmp_path):
        """Does not corrupt other frontmatter fields or body content."""
        work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
        work_dir.mkdir(parents=True)
        work_file = work_dir / "WORK.md"
        original = (
            '---\nid: WORK-999\ntitle: "Test Item"\n'
            "cycle_phase: PLAN\nstatus: active\n---\n"
            "# Content\nBody text here.\n"
        )
        work_file.write_text(original)
        sync_work_md_phase("WORK-999", "DO", project_root=tmp_path)
        content = work_file.read_text()
        assert 'title: "Test Item"' in content
        assert "status: active" in content
        assert "Body text here." in content
        assert "cycle_phase: DO" in content

    def test_updates_current_node_field(self, tmp_path):
        """WORK-198: Also syncs current_node for backward compat."""
        work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
        work_dir.mkdir(parents=True)
        work_file = work_dir / "WORK.md"
        work_file.write_text(
            "---\nid: WORK-999\ncycle_phase: PLAN\ncurrent_node: PLAN\nstatus: active\n---\n# Content\n"
        )
        result = sync_work_md_phase("WORK-999", "DO", project_root=tmp_path)
        assert result is True
        content = work_file.read_text()
        assert "cycle_phase: DO" in content
        assert "current_node: DO" in content
        assert "current_node: PLAN" not in content

    def test_skips_current_node_if_missing(self, tmp_path):
        """WORK-198: If no current_node field, only cycle_phase is updated."""
        work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
        work_dir.mkdir(parents=True)
        work_file = work_dir / "WORK.md"
        work_file.write_text(
            "---\nid: WORK-999\ncycle_phase: PLAN\nstatus: active\n---\n# Content\n"
        )
        result = sync_work_md_phase("WORK-999", "DO", project_root=tmp_path)
        assert result is True
        content = work_file.read_text()
        assert "cycle_phase: DO" in content
        assert "current_node" not in content

    def test_returns_false_missing_file(self, tmp_path):
        """Returns False when WORK.md does not exist (fail-permissive)."""
        result = sync_work_md_phase("WORK-999", "DO", project_root=tmp_path)
        assert result is False

    def test_returns_false_no_cycle_phase_field(self, tmp_path):
        """Returns False when WORK.md has no cycle_phase field."""
        work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
        work_dir.mkdir(parents=True)
        work_file = work_dir / "WORK.md"
        work_file.write_text("---\nid: WORK-999\nstatus: active\n---\n")
        result = sync_work_md_phase("WORK-999", "DO", project_root=tmp_path)
        assert result is False


class TestAdvanceCyclePhaseWithSync:
    """Integration tests — advance_cycle_phase calls sync_work_md_phase."""

    def test_syncs_work_md_on_advance(self, tmp_path, monkeypatch):
        """advance_cycle_phase calls sync_work_md_phase after advancing."""
        slim_file = tmp_path / ".claude" / "haios-status-slim.json"
        slim_file.parent.mkdir(parents=True)
        slim_file.write_text(json.dumps({
            "session_state": {
                "active_cycle": "implementation-cycle",
                "current_phase": "PLAN",
                "work_id": "WORK-999",
                "entered_at": "2026-01-01T00:00:00",
                "active_queue": None,
                "phase_history": [],
            }
        }))
        # Setup WORK.md
        work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
        work_dir.mkdir(parents=True)
        (work_dir / "WORK.md").write_text(
            "---\nid: WORK-999\ncycle_phase: PLAN\n---\n"
        )
        # Patch CYCLE_PHASES at the source module (cycle_runner)
        monkeypatch.setattr(
            cycle_runner, "CYCLE_PHASES",
            {"implementation-cycle": ["PLAN", "DO", "CHECK", "DONE"]},
        )
        result = advance_cycle_phase("implementation-cycle", project_root=tmp_path)
        assert result is True
        content = (work_dir / "WORK.md").read_text()
        assert "cycle_phase: DO" in content

    def test_advance_succeeds_without_work_md(self, tmp_path, monkeypatch):
        """Phase still advances in slim JSON even if WORK.md sync fails."""
        slim_file = tmp_path / ".claude" / "haios-status-slim.json"
        slim_file.parent.mkdir(parents=True)
        slim_file.write_text(json.dumps({
            "session_state": {
                "active_cycle": "implementation-cycle",
                "current_phase": "PLAN",
                "work_id": "WORK-999",
                "entered_at": "2026-01-01T00:00:00",
                "active_queue": None,
                "phase_history": [],
            }
        }))
        # Patch CYCLE_PHASES at the source module (cycle_runner)
        monkeypatch.setattr(
            cycle_runner, "CYCLE_PHASES",
            {"implementation-cycle": ["PLAN", "DO", "CHECK", "DONE"]},
        )
        # No WORK.md exists — sync will fail but advance should still succeed
        result = advance_cycle_phase("implementation-cycle", project_root=tmp_path)
        assert result is True
        data = json.loads(slim_file.read_text())
        assert data["session_state"]["current_phase"] == "DO"

    def test_handles_missing_session_state(self, tmp_path):
        """Returns False cleanly when slim JSON has no session_state key."""
        slim_file = tmp_path / ".claude" / "haios-status-slim.json"
        slim_file.parent.mkdir(parents=True)
        slim_file.write_text(json.dumps({"version": "1.0"}))
        result = advance_cycle_phase("implementation-cycle", project_root=tmp_path)
        assert result is False
