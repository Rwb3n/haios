"""Tests for queue_position auto-promotion on cycle_phase change (WORK-256).

When set_cycle_state() is called (e.g., entering PLAN or DO), if the work item's
queue_position is 'backlog' or 'ready', it should auto-promote to 'working'.
This prevents queue_position:backlog + cycle_phase:PLAN drift.

Uses tmp_path for filesystem isolation (S340 pattern).
"""
import json
import re
import sys
from pathlib import Path

import pytest

# Ensure lib/ is importable
_lib_dir = str(Path(__file__).parent.parent / ".claude" / "haios" / "lib")
if _lib_dir not in sys.path:
    sys.path.insert(0, _lib_dir)

from cycle_state import set_cycle_state


def _write_slim(tmp_path: Path, session_state: dict) -> Path:
    """Helper: write haios-status-slim.json with given session_state."""
    slim_dir = tmp_path / ".claude"
    slim_dir.mkdir(parents=True, exist_ok=True)
    slim_file = slim_dir / "haios-status-slim.json"
    data = {"session_state": session_state}
    slim_file.write_text(json.dumps(data, indent=4), encoding="utf-8")
    return slim_file


def _write_work_md(tmp_path: Path, work_id: str, queue_position: str,
                   queue_history: list = None, node_history: list = None) -> Path:
    """Helper: write a minimal WORK.md with queue_position and history fields."""
    work_dir = tmp_path / "docs" / "work" / "active" / work_id
    work_dir.mkdir(parents=True, exist_ok=True)
    work_file = work_dir / "WORK.md"

    qh = queue_history or [
        {"position": queue_position, "entered": "2026-03-07T14:00:00", "exited": None}
    ]
    nh = node_history or [
        {"node": "backlog", "entered": "2026-03-07T14:00:00", "exited": None}
    ]

    # Build YAML-ish frontmatter (simple format matching real WORK.md)
    qh_yaml = _list_to_yaml(qh, "queue_history")
    nh_yaml = _list_to_yaml(nh, "node_history")

    content = f"""---
id: {work_id}
title: Test work item
type: implementation
status: active
queue_position: {queue_position}
cycle_phase: backlog
current_node: backlog
{qh_yaml}
{nh_yaml}
---
# {work_id}: Test work item
"""
    work_file.write_text(content, encoding="utf-8")
    return work_file


def _list_to_yaml(items: list, field_name: str) -> str:
    """Convert list of dicts to YAML list format."""
    lines = [f"{field_name}:"]
    for item in items:
        first = True
        for k, v in item.items():
            prefix = "- " if first else "  "
            val = "null" if v is None else f"'{v}'"
            lines.append(f"{prefix}{k}: {val}")
            first = False
    return "\n".join(lines)


def _read_work_frontmatter(work_file: Path) -> str:
    """Read WORK.md content for assertion checks."""
    return work_file.read_text(encoding="utf-8")


def _extract_queue_position(content: str) -> str:
    """Extract queue_position value from WORK.md frontmatter."""
    match = re.search(r"^queue_position:\s*(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else None


class TestQueueAutoPromote:
    """WORK-256: Auto-promote queue_position when cycle_phase changes."""

    def test_backlog_promoted_to_working(self, tmp_path, monkeypatch):
        """AC1: cycle_set() auto-promotes queue_position from backlog to working."""
        _write_slim(tmp_path, {})
        work_file = _write_work_md(tmp_path, "WORK-256", "backlog")

        # Mock governance event logging (not under test)
        monkeypatch.setattr(
            "cycle_state.sync_work_md_phase", lambda *a, **kw: True
        )

        result = set_cycle_state(
            "implementation-cycle", "PLAN", "WORK-256", project_root=tmp_path
        )
        assert result is True

        content = _read_work_frontmatter(work_file)
        assert _extract_queue_position(content) == "working"

    def test_ready_promoted_to_working(self, tmp_path, monkeypatch):
        """AC1: cycle_set() auto-promotes queue_position from ready to working."""
        _write_slim(tmp_path, {})
        work_file = _write_work_md(tmp_path, "WORK-300", "ready",
                                    queue_history=[
                                        {"position": "backlog", "entered": "2026-03-07T14:00:00", "exited": "2026-03-07T15:00:00"},
                                        {"position": "ready", "entered": "2026-03-07T15:00:00", "exited": None},
                                    ])

        monkeypatch.setattr(
            "cycle_state.sync_work_md_phase", lambda *a, **kw: True
        )

        result = set_cycle_state(
            "implementation-cycle", "DO", "WORK-300", project_root=tmp_path
        )
        assert result is True

        content = _read_work_frontmatter(work_file)
        assert _extract_queue_position(content) == "working"

    def test_working_not_demoted(self, tmp_path, monkeypatch):
        """Already at working — no change needed."""
        _write_slim(tmp_path, {})
        work_file = _write_work_md(tmp_path, "WORK-301", "working")

        monkeypatch.setattr(
            "cycle_state.sync_work_md_phase", lambda *a, **kw: True
        )

        result = set_cycle_state(
            "implementation-cycle", "CHECK", "WORK-301", project_root=tmp_path
        )
        assert result is True

        content = _read_work_frontmatter(work_file)
        assert _extract_queue_position(content) == "working"

    def test_done_not_changed(self, tmp_path, monkeypatch):
        """queue_position=done should never be changed."""
        _write_slim(tmp_path, {})
        work_file = _write_work_md(tmp_path, "WORK-302", "done")

        monkeypatch.setattr(
            "cycle_state.sync_work_md_phase", lambda *a, **kw: True
        )

        result = set_cycle_state(
            "implementation-cycle", "CHECK", "WORK-302", project_root=tmp_path
        )
        assert result is True

        content = _read_work_frontmatter(work_file)
        assert _extract_queue_position(content) == "done"

    def test_queue_history_appended(self, tmp_path, monkeypatch):
        """AC2: queue_history entry added atomically with cycle_phase change."""
        _write_slim(tmp_path, {})
        work_file = _write_work_md(tmp_path, "WORK-303", "backlog")

        monkeypatch.setattr(
            "cycle_state.sync_work_md_phase", lambda *a, **kw: True
        )

        result = set_cycle_state(
            "implementation-cycle", "PLAN", "WORK-303", project_root=tmp_path
        )
        assert result is True

        content = _read_work_frontmatter(work_file)
        # Should contain 'working' in queue_history (new entry)
        assert "position: 'working'" in content or "position: working" in content
        # Previous entry should have exited timestamp
        assert "exited: '2026-" in content  # timestamp starts with year

    def test_missing_work_file_is_permissive(self, tmp_path, monkeypatch):
        """Fail-permissive: missing WORK.md should not prevent set_cycle_state success."""
        _write_slim(tmp_path, {})
        # No WORK.md written — auto-promote should silently skip

        monkeypatch.setattr(
            "cycle_state.sync_work_md_phase", lambda *a, **kw: True
        )

        result = set_cycle_state(
            "implementation-cycle", "DO", "WORK-404", project_root=tmp_path
        )
        # set_cycle_state should still succeed (slim file was written)
        assert result is True

    def test_parked_not_promoted(self, tmp_path, monkeypatch):
        """queue_position=parked should not be auto-promoted."""
        _write_slim(tmp_path, {})
        work_file = _write_work_md(tmp_path, "WORK-305", "parked")

        monkeypatch.setattr(
            "cycle_state.sync_work_md_phase", lambda *a, **kw: True
        )

        result = set_cycle_state(
            "implementation-cycle", "PLAN", "WORK-305", project_root=tmp_path
        )
        assert result is True

        content = _read_work_frontmatter(work_file)
        assert _extract_queue_position(content) == "parked"
