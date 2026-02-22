"""Tests for phase contract auto-injection (WORK-188, ADR-048).

Tests read_phase_contract() in cycle_state.py, PostToolUse injection in
post_tool_use.py, and UserPromptSubmit injection in user_prompt_submit.py.
"""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LIB_DIR = Path(__file__).parent.parent / ".claude" / "haios" / "lib"
HOOKS_DIR = Path(__file__).parent.parent / ".claude" / "hooks" / "hooks"


def _import_cycle_state():
    """Import cycle_state from lib."""
    if str(LIB_DIR) not in sys.path:
        sys.path.insert(0, str(LIB_DIR))
    import cycle_state
    return cycle_state


def _import_post_tool_use():
    """Import post_tool_use hook handler."""
    if str(HOOKS_DIR) not in sys.path:
        sys.path.insert(0, str(HOOKS_DIR))
    import post_tool_use
    return post_tool_use


def _import_user_prompt_submit():
    """Import user_prompt_submit hook handler."""
    if str(HOOKS_DIR) not in sys.path:
        sys.path.insert(0, str(HOOKS_DIR))
    import user_prompt_submit
    return user_prompt_submit


def _create_phase_file(tmp_path, cycle_name, phase_name, content):
    """Create a phase file in the expected directory structure."""
    phase_dir = tmp_path / ".claude" / "skills" / cycle_name / "phases"
    phase_dir.mkdir(parents=True, exist_ok=True)
    phase_file = phase_dir / f"{phase_name}.md"
    phase_file.write_text(content, encoding="utf-8")
    return phase_file


def _create_slim_json(tmp_path, active_cycle=None, current_phase=None, work_id=None):
    """Create haios-status-slim.json with session_state."""
    slim_dir = tmp_path / ".claude"
    slim_dir.mkdir(parents=True, exist_ok=True)
    slim_data = {
        "session_state": {
            "active_cycle": active_cycle,
            "current_phase": current_phase,
            "work_id": work_id,
            "entered_at": "2026-02-22T11:00:00",
            "phase_history": [],
            "active_queue": None,
        }
    }
    slim_file = slim_dir / "haios-status-slim.json"
    slim_file.write_text(json.dumps(slim_data, indent=4), encoding="utf-8")
    return slim_file


# ---------------------------------------------------------------------------
# Tests 1-3: read_phase_contract (cycle_state.py)
# ---------------------------------------------------------------------------

class TestReadPhaseContract:
    """Tests for the read_phase_contract function in cycle_state.py."""

    def test_read_phase_contract_returns_content(self, tmp_path):
        """Test 1: Existing phase file returns its content."""
        cs = _import_cycle_state()
        content = "# DO Phase\nDo stuff"
        _create_phase_file(tmp_path, "implementation-cycle", "DO", content)

        result = cs.read_phase_contract(
            "implementation-cycle", "DO", project_root=tmp_path
        )
        assert result == content

    def test_read_phase_contract_missing_file_returns_none(self, tmp_path):
        """Test 2: Missing phase file returns None (fall-permissive)."""
        cs = _import_cycle_state()
        # Create the phases directory but no PLAN.md file
        phases_dir = tmp_path / ".claude" / "skills" / "implementation-cycle" / "phases"
        phases_dir.mkdir(parents=True, exist_ok=True)

        result = cs.read_phase_contract(
            "implementation-cycle", "PLAN", project_root=tmp_path
        )
        assert result is None

    def test_read_phase_contract_missing_cycle_dir_returns_none(self, tmp_path):
        """Test 3: Missing cycle directory returns None (no exception)."""
        cs = _import_cycle_state()
        # No .claude/skills/ directory at all

        result = cs.read_phase_contract(
            "nonexistent-cycle", "DO", project_root=tmp_path
        )
        assert result is None


# ---------------------------------------------------------------------------
# Tests 4-5: PostToolUse injection (post_tool_use.py)
# ---------------------------------------------------------------------------

class TestPostToolUseInjection:
    """Tests for phase contract injection in PostToolUse Skill handler.

    The PostToolUse handler imports advance_cycle_phase and read_phase_contract
    locally inside handle() via `from cycle_state import ...`. Monkeypatching
    must target the cycle_state module, and we must also handle the slim file
    path (derived from Path(__file__).parent x4).
    """

    def test_posttooluse_injects_phase_contract_after_advance(self, tmp_path, monkeypatch):
        """Test 4: After advance, PostToolUse injects phase contract content."""
        ptu = _import_post_tool_use()
        cs = _import_cycle_state()

        # Create slim with DO phase active
        slim_file = _create_slim_json(
            tmp_path,
            active_cycle="implementation-cycle",
            current_phase="DO",
            work_id="WORK-188",
        )

        # Create the phase file
        phase_content = "# DO Phase\nExecute the plan."
        _create_phase_file(tmp_path, "implementation-cycle", "DO", phase_content)

        # Monkeypatch advance_cycle_phase on the cycle_state module
        monkeypatch.setattr(cs, "advance_cycle_phase", lambda skill_name, **kw: True)

        # Monkeypatch read_phase_contract to use tmp_path as project root
        monkeypatch.setattr(
            cs, "read_phase_contract",
            lambda cycle_key, new_phase, **kw: cs.read_phase_contract.__wrapped__(
                cycle_key, new_phase, project_root=tmp_path
            ) if hasattr(cs.read_phase_contract, "__wrapped__") else
            phase_content  # Direct return for simplicity
        )

        # The slim file path in PostToolUse is derived from Path(__file__).parent x4.
        # We can't easily redirect that, so instead we patch the slim file read
        # by making the real slim path point to our test data.
        # Approach: write our slim data to the REAL slim location temporarily,
        # or patch json.loads to intercept.
        import post_tool_use as ptu_mod
        original_json_loads = json.loads
        slim_data = json.loads(slim_file.read_text(encoding="utf-8"))

        def mock_json_loads(s, *args, **kwargs):
            parsed = original_json_loads(s, *args, **kwargs)
            if isinstance(parsed, dict) and "session_state" in parsed:
                return slim_data
            return parsed

        monkeypatch.setattr(json, "loads", mock_json_loads)

        # Monkeypatch read_phase_contract simply to return the phase content
        monkeypatch.setattr(cs, "read_phase_contract", lambda ck, np, **kw: phase_content)

        hook_data = {
            "tool_name": "Skill",
            "tool_input": {"skill": "implementation-cycle"},
            "tool_response": {},
        }
        result = ptu.handle(hook_data)

        assert result is not None
        assert "Phase Contract: implementation-cycle/DO" in result
        assert "# DO Phase" in result

    def test_posttooluse_missing_phase_file_no_crash(self, tmp_path, monkeypatch):
        """Test 5: Missing phase file does not crash; advance message still present."""
        ptu = _import_post_tool_use()
        cs = _import_cycle_state()

        # Create slim with DO phase active but NO phase file
        slim_file = _create_slim_json(
            tmp_path,
            active_cycle="implementation-cycle",
            current_phase="DO",
            work_id="WORK-188",
        )

        # Monkeypatch advance to return True
        monkeypatch.setattr(cs, "advance_cycle_phase", lambda skill_name, **kw: True)

        # Monkeypatch read_phase_contract to return None (no phase file)
        monkeypatch.setattr(cs, "read_phase_contract", lambda ck, np, **kw: None)

        # Mock slim read
        slim_data = json.loads(slim_file.read_text(encoding="utf-8"))
        original_json_loads = json.loads

        def mock_json_loads(s, *args, **kwargs):
            parsed = original_json_loads(s, *args, **kwargs)
            if isinstance(parsed, dict) and "session_state" in parsed:
                return slim_data
            return parsed

        monkeypatch.setattr(json, "loads", mock_json_loads)

        hook_data = {
            "tool_name": "Skill",
            "tool_input": {"skill": "implementation-cycle"},
            "tool_response": {},
        }
        result = ptu.handle(hook_data)

        assert result is not None
        assert "[CYCLE] Auto-advanced" in result
        assert "Phase Contract" not in result


# ---------------------------------------------------------------------------
# Tests 6-8: UserPromptSubmit injection (user_prompt_submit.py)
# ---------------------------------------------------------------------------

class TestUserPromptSubmitInjection:
    """Tests for phase contract injection in UserPromptSubmit."""

    def test_user_prompt_submit_injects_phase_contract(self, tmp_path):
        """Test 6: Active cycle with existing phase file returns contract."""
        ups = _import_user_prompt_submit()

        # Create slim and phase file
        _create_slim_json(
            tmp_path,
            active_cycle="implementation-cycle",
            current_phase="DO",
        )
        phase_content = "# DO Phase\nExecute the plan."
        _create_phase_file(tmp_path, "implementation-cycle", "DO", phase_content)

        result = ups._get_phase_contract(str(tmp_path))

        assert result is not None
        assert "Phase Contract: implementation-cycle/DO" in result
        assert "# DO Phase" in result

    def test_user_prompt_submit_no_active_cycle_returns_none(self, tmp_path):
        """Test 7: No active cycle returns None."""
        ups = _import_user_prompt_submit()

        _create_slim_json(tmp_path, active_cycle=None, current_phase=None)

        result = ups._get_phase_contract(str(tmp_path))
        assert result is None

    def test_user_prompt_submit_missing_phase_file_returns_none(self, tmp_path):
        """Test 8: Active cycle but missing phase file returns None."""
        ups = _import_user_prompt_submit()

        _create_slim_json(
            tmp_path,
            active_cycle="implementation-cycle",
            current_phase="DO",
        )
        # No phase file created

        result = ups._get_phase_contract(str(tmp_path))
        assert result is None
