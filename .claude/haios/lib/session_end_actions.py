# generated: 2026-02-18
"""
Session-end actions for Stop hook (WORK-161: Session Boundary Fix).

Four fail-permissive functions that run unconditionally from the Stop hook,
ensuring session-end housekeeping happens even when the agent exhausts context.

Functions:
    read_session_number  — Read current session number from .claude/session
    log_session_ended    — Write SessionEnded event to governance-events.jsonl
    clear_cycle_state    — Zero out session_state in haios-status-slim.json
    detect_uncommitted_changes — Check for uncommitted git changes
"""
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional


def _default_project_root() -> Path:
    """Derive project root from this file's location.

    lib/ -> haios/ -> .claude/ -> project root.
    NOT Path.cwd() — hook subprocess cwd is not guaranteed.
    """
    return Path(__file__).parent.parent.parent.parent


def read_session_number(project_root: Optional[Path] = None) -> Optional[int]:
    """Read session number from .claude/session file.

    Skips lines starting with '#' (comment headers).

    Args:
        project_root: Project root path. Defaults to derived path.

    Returns:
        Session number as int, or None if file missing/unparseable.
    """
    try:
        root = project_root or _default_project_root()
        session_file = root / ".claude" / "session"
        if not session_file.exists():
            return None

        for line in session_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                return int(line)
            except ValueError:
                continue

        return None
    except Exception:
        return None


def log_session_ended(session_number: int, agent: str) -> Optional[dict]:
    """Log SessionEnded event to governance-events.jsonl.

    Args:
        session_number: Current session number (required).
        agent: Agent name (required).

    Returns:
        The logged event dict, or None on error.
    """
    try:
        from governance_events import log_session_end

        return log_session_end(session_number, agent)
    except Exception:
        return None


def clear_cycle_state(project_root: Optional[Path] = None) -> bool:
    """Zero out session_state in haios-status-slim.json.

    Delegates to cycle_state.clear_cycle_state (canonical impl moved to
    cycle_state.py by WORK-219).

    Args:
        project_root: Project root path. Defaults to derived path.

    Returns:
        True if cleared successfully, False on error/missing file.
    """
    try:
        _lib_dir = Path(__file__).parent
        if str(_lib_dir) not in sys.path:
            sys.path.insert(0, str(_lib_dir))
        from cycle_state import clear_cycle_state as _clear
        return _clear(project_root=project_root)
    except Exception:
        return False


def detect_uncommitted_changes(project_root: Optional[Path] = None) -> Optional[list[str]]:
    """Detect uncommitted changes via git status.

    Args:
        project_root: Project root path. Defaults to derived path.

    Returns:
        List of changed file strings (empty if clean),
        or None on error/timeout.
    """
    try:
        root = project_root or _default_project_root()
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(root),
        )
        if result.returncode != 0:
            return None

        lines = [line for line in result.stdout.splitlines() if line.strip()]
        return lines
    except (subprocess.TimeoutExpired, OSError, Exception):
        return None
