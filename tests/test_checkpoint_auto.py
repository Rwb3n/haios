"""
Tests for checkpoint_auto.py (WORK-170).

8 tests covering: happy path, graceful degradation for missing files,
null work_id, no plan file, non-checkpoint path, and missing file.
"""
import json
from pathlib import Path

import pytest


def _get_checkpoint_auto():
    """Import checkpoint_auto from lib (adds to sys.path)."""
    import sys
    lib_dir = Path(__file__).parent.parent / ".claude" / "haios" / "lib"
    if str(lib_dir) not in sys.path:
        sys.path.insert(0, str(lib_dir))
    from checkpoint_auto import populate_checkpoint_fields
    return populate_checkpoint_fields


def _make_checkpoint_file(tmp_path: Path) -> Path:
    """Create a checkpoint file with standard placeholders in a checkpoints/ subdir."""
    checkpoints_dir = tmp_path / "docs" / "checkpoints"
    checkpoints_dir.mkdir(parents=True)
    cp = checkpoints_dir / "CHECKPOINT-409.md"
    cp.write_text(
        "---\n"
        "template: checkpoint\n"
        "session: {{SESSION}}\n"
        "prior_session: {{PREV_SESSION}}\n"
        "date: {{DATE}}\n"
        "work_id: {{WORK_ID}}\n"
        "plan_ref: {{PLAN_REF}}\n"
        "---\n",
        encoding="utf-8",
    )
    return cp


def _make_session_file(tmp_path: Path, session_num: int) -> Path:
    """Create a .claude/session file with the given session number."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    session_file = claude_dir / "session"
    session_file.write_text(f"# session number\n{session_num}\n", encoding="utf-8")
    return session_file


def _make_slim_json(tmp_path: Path, work_id) -> Path:
    """Create haios-status-slim.json with session_state.work_id."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    slim_file = claude_dir / "haios-status-slim.json"
    data = {
        "session_state": {
            "work_id": work_id,
        }
    }
    slim_file.write_text(json.dumps(data), encoding="utf-8")
    return slim_file


def _make_plan_file(tmp_path: Path, work_id: str) -> Path:
    """Create a PLAN.md file for the given work_id."""
    plan_dir = tmp_path / "docs" / "work" / "active" / work_id / "plans"
    plan_dir.mkdir(parents=True)
    plan_file = plan_dir / "PLAN.md"
    plan_file.write_text("---\ntemplate: implementation_plan\n---\n", encoding="utf-8")
    return plan_file


# ── Test 1: All fields populated (happy path) ─────────────────────────────────

def test_populate_all_fields(tmp_path):
    """All 5 fields populated when all sources available."""
    populate = _get_checkpoint_auto()

    cp = _make_checkpoint_file(tmp_path)
    _make_session_file(tmp_path, 409)
    _make_slim_json(tmp_path, "WORK-170")
    _make_plan_file(tmp_path, "WORK-170")

    result = populate(cp, project_root=tmp_path)

    content = cp.read_text(encoding="utf-8")

    assert "{{SESSION}}" not in content
    assert "{{PREV_SESSION}}" not in content
    assert "{{DATE}}" not in content
    assert "{{WORK_ID}}" not in content
    assert "{{PLAN_REF}}" not in content

    assert "session: 409" in content
    assert "prior_session: 408" in content
    assert "work_id: WORK-170" in content
    assert "plan_ref: docs/work/active/WORK-170/plans/PLAN.md" in content
    assert result is not None


# ── Test 2: Missing session file → session + prior_session stay as placeholders ──

def test_missing_session_file(tmp_path):
    """No session file → session and prior_session remain as placeholders."""
    populate = _get_checkpoint_auto()

    cp = _make_checkpoint_file(tmp_path)
    # No session file created
    _make_slim_json(tmp_path, "WORK-170")

    result = populate(cp, project_root=tmp_path)

    content = cp.read_text(encoding="utf-8")

    assert "{{SESSION}}" in content
    assert "{{PREV_SESSION}}" in content
    # Date and work_id should still be populated
    assert "{{DATE}}" not in content
    assert "{{WORK_ID}}" not in content


# ── Test 3: Missing slim JSON → work_id stays as placeholder ─────────────────

def test_missing_slim_json(tmp_path):
    """No slim JSON → work_id remains as placeholder."""
    populate = _get_checkpoint_auto()

    cp = _make_checkpoint_file(tmp_path)
    _make_session_file(tmp_path, 409)
    # No slim JSON created

    result = populate(cp, project_root=tmp_path)

    content = cp.read_text(encoding="utf-8")

    assert "{{WORK_ID}}" in content
    assert "{{PLAN_REF}}" in content  # No work_id → no plan lookup → placeholder
    assert "{{SESSION}}" not in content
    assert "{{DATE}}" not in content


# ── Test 4: Null work_id in slim JSON → work_id stays as placeholder ─────────

def test_null_work_id_in_slim(tmp_path):
    """session_state.work_id is null → work_id remains as placeholder."""
    populate = _get_checkpoint_auto()

    cp = _make_checkpoint_file(tmp_path)
    _make_session_file(tmp_path, 409)
    _make_slim_json(tmp_path, None)  # null work_id

    result = populate(cp, project_root=tmp_path)

    content = cp.read_text(encoding="utf-8")

    assert "{{WORK_ID}}" in content
    assert "{{PLAN_REF}}" in content  # No work_id → no plan lookup
    assert "{{SESSION}}" not in content


# ── Test 5: No plan file → plan_ref placeholder preserved ────────────────────

def test_no_plan_file(tmp_path):
    """No plan file for work_id → plan_ref remains as placeholder."""
    populate = _get_checkpoint_auto()

    cp = _make_checkpoint_file(tmp_path)
    _make_session_file(tmp_path, 409)
    _make_slim_json(tmp_path, "WORK-170")
    # No plan file created

    result = populate(cp, project_root=tmp_path)

    content = cp.read_text(encoding="utf-8")

    assert "{{PLAN_REF}}" in content  # No plan file → placeholder preserved
    assert "{{WORK_ID}}" not in content  # work_id IS populated
    assert "{{SESSION}}" not in content


# ── Test 6: Plan file exists → plan_ref populated ────────────────────────────

def test_plan_file_exists(tmp_path):
    """Plan file found → plan_ref populated with relative path."""
    populate = _get_checkpoint_auto()

    cp = _make_checkpoint_file(tmp_path)
    _make_session_file(tmp_path, 409)
    _make_slim_json(tmp_path, "WORK-170")
    _make_plan_file(tmp_path, "WORK-170")

    result = populate(cp, project_root=tmp_path)

    content = cp.read_text(encoding="utf-8")

    assert "plan_ref: docs/work/active/WORK-170/plans/PLAN.md" in content
    assert "{{PLAN_REF}}" not in content


# ── Test 7: Non-checkpoint path returns early (no modification) ───────────────

def test_file_without_placeholders_noop(tmp_path):
    """File without {{}} placeholders → no modification, returns None."""
    populate = _get_checkpoint_auto()

    # Create file with no placeholders (already populated)
    cp_dir = tmp_path / "docs" / "checkpoints"
    cp_dir.mkdir(parents=True)
    cp = cp_dir / "checkpoint-409.md"
    original_content = "---\ntemplate: checkpoint\nsession: 409\ndate: 2026-02-20\n---\n"
    cp.write_text(original_content, encoding="utf-8")

    _make_session_file(tmp_path, 409)
    _make_slim_json(tmp_path, "WORK-170")

    result = populate(cp, project_root=tmp_path)

    content = cp.read_text(encoding="utf-8")
    assert content == original_content
    assert result is None


# ── Test 8: Missing checkpoint file → returns None without raising ────────────

def test_missing_checkpoint_file(tmp_path):
    """Non-existent path → returns None without raising."""
    populate = _get_checkpoint_auto()

    # Path that does not exist, but is in checkpoints/
    nonexistent = tmp_path / "docs" / "checkpoints" / "CHECKPOINT-999.md"

    result = populate(nonexistent, project_root=tmp_path)

    assert result is None
