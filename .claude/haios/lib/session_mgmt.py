"""
Session start management (WORK-219).

Extracted from justfile session-start inline Python. Encapsulates:
- Writing session number to .claude/session (preserving # comment headers)
- Writing session_delta to haios-status.json
- Logging session start governance event
- Resetting session event log

Explicit params, fail-permissive, no global module-level state.
"""
import json
import sys
from pathlib import Path
from typing import Optional


def _default_project_root() -> Path:
    """Derive project root from this file's location.

    lib/ -> haios/ -> .claude/ -> project root.
    NOT Path.cwd() — hook subprocess cwd is not guaranteed.
    """
    return Path(__file__).parent.parent.parent.parent


def start_session(
    session_number: int,
    agent: str = "Hephaestus",
    project_root: Optional[Path] = None,
) -> bool:
    """Encapsulate justfile session-start recipe logic.

    Actions performed (in order, all fail-permissive):
    1. Write session_number to .claude/session (preserving # comment headers)
    2. Write session_delta to .claude/haios-status.json
    3. Log SessionStarted governance event via log_session_start()
    4. Truncate session event log via reset_log()

    Args:
        session_number: New session number (e.g., 451)
        agent: Agent name for governance event (default: "Hephaestus")
        project_root: Project root. Defaults to derived path.

    Returns:
        True if all 4 actions completed without error, False if any failed.
    """
    try:
        root = project_root or _default_project_root()
        lib_dir = Path(__file__).parent
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))

        all_ok = True

        # 1. Write session number to .claude/session
        try:
            session_file = root / ".claude" / "session"
            lines = (
                session_file.read_text(encoding="utf-8").splitlines(keepends=True)
                if session_file.exists()
                else []
            )
            headers = [line for line in lines if line.startswith("#")]
            session_file.write_text(
                "".join(headers) + str(session_number) + "\n", encoding="utf-8"
            )
        except Exception:
            all_ok = False

        # 2. Write session_delta to haios-status.json
        try:
            status_file = root / ".claude" / "haios-status.json"
            status = (
                json.loads(status_file.read_text(encoding="utf-8"))
                if status_file.exists()
                else {}
            )
            status["session_delta"] = {
                "current_session": session_number,
                "prior_session": session_number - 1,
            }
            status_file.write_text(json.dumps(status, indent=2), encoding="utf-8")
        except Exception:
            all_ok = False

        # 3. Log governance event
        try:
            from governance_events import log_session_start

            log_session_start(session_number, agent)
        except Exception:
            all_ok = False

        # 4. Reset session event log
        try:
            from session_event_log import reset_log

            reset_log()
        except Exception:
            all_ok = False

        return all_ok

    except Exception:
        return False
