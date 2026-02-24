# generated: 2026-02-23
"""
Session Event Log module (WORK-206).

Thin utility for the session-scoped compact event log at
.claude/haios/session-log.jsonl.

Public API:
    reset_log()       — truncate at session-start (called from justfile)
    append_event()    — append compact JSONL event (called from PostToolUse hook)
    read_events()     — read all events for SessionLoader summary

All functions are fail-permissive: they never raise exceptions.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

# Default path — overridden by haios.yaml paths.session_log
SESSION_LOG_DEFAULT = Path(".claude/haios/session-log.jsonl")


def get_log_path() -> Path:
    """Return session log path from ConfigLoader, fallback to default."""
    try:
        lib_dir = Path(__file__).parent
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))
        from config import ConfigLoader
        raw = ConfigLoader.get().get_path("session_log")
        return Path(raw) if raw else SESSION_LOG_DEFAULT
    except Exception:
        return SESSION_LOG_DEFAULT


def reset_log() -> None:
    """Truncate session log file. Called by session-start recipe in justfile."""
    try:
        path = get_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    except Exception:
        pass  # Fail-permissive


def append_event(event_type: str, value: str, work_id: str = "") -> None:
    """Append one compact JSONL event line.

    Format: {"t": "phase", "v": "PLAN->DO", "w": "WORK-206", "ts": "15:03"}

    Args:
        event_type: Short event type key — "phase", "commit", "test", "spawn", "close"
        value:      Human-readable value for the event
        work_id:    Associated work item ID (empty string if unknown)
    """
    try:
        path = get_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "t": event_type,
            "v": value,
            "w": work_id,
            "ts": datetime.now().strftime("%H:%M"),
        }
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception:
        pass  # Fail-permissive


def read_events() -> list:
    """Read all events from session log. Returns [] on missing or corrupt file."""
    try:
        path = get_log_path()
        if not path.exists():
            return []
        events = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass  # Skip malformed lines
        return events
    except Exception:
        return []
