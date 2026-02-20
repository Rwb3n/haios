"""
Checkpoint field auto-population (WORK-170).

Pure function to populate checkpoint frontmatter fields from infrastructure.
Pattern: session_end_actions.py (fail-permissive, _default_project_root).
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


def _default_project_root() -> Path:
    """Derive project root. lib/ -> haios/ -> .claude/ -> project root."""
    return Path(__file__).parent.parent.parent.parent


def populate_checkpoint_fields(
    checkpoint_path: Path,
    project_root: Optional[Path] = None,
) -> Optional[str]:
    """Populate placeholder fields in a checkpoint file.

    Reads session file, haios-status-slim.json, and work directory
    to fill: session, prior_session, date, work_id, plan_ref.

    Fields that cannot be resolved are left as placeholders (no errors).

    Args:
        checkpoint_path: Path to the checkpoint .md file.
        project_root: Project root. Defaults to derived path.

    Returns:
        Status message, or None on error. Never raises.
    """
    try:
        root = project_root or _default_project_root()
        content = checkpoint_path.read_text(encoding="utf-8")

        # Only process files with frontmatter placeholders
        if "{{" not in content:
            return None

        # Resolve fields
        session_num = _read_session_number(root)
        work_id = _read_work_id(root)
        plan_ref = _resolve_plan_ref(root, work_id) if work_id else None
        today = datetime.now().strftime("%Y-%m-%d")

        # Replace placeholders (only if value resolved)
        if session_num is not None:
            content = content.replace("{{SESSION}}", str(session_num))
            content = content.replace("{{PREV_SESSION}}", str(max(0, session_num - 1)))
        if work_id:
            content = content.replace("{{WORK_ID}}", work_id)
        if plan_ref:
            content = content.replace("{{PLAN_REF}}", plan_ref)
        content = content.replace("{{DATE}}", today)

        checkpoint_path.write_text(content, encoding="utf-8")
        return f"[CHECKPOINT] Auto-populated fields in {checkpoint_path.name}"

    except Exception:
        return None  # Fail-permissive


def _read_session_number(root: Path) -> Optional[int]:
    """Read session number from .claude/session. Reuses pattern from session_end_actions."""
    try:
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


def _read_work_id(root: Path) -> Optional[str]:
    """Read work_id from haios-status-slim.json session_state."""
    try:
        slim_file = root / ".claude" / "haios-status-slim.json"
        if not slim_file.exists():
            return None
        data = json.loads(slim_file.read_text(encoding="utf-8"))
        work_id = data.get("session_state", {}).get("work_id")
        return work_id if work_id else None
    except Exception:
        return None


def _resolve_plan_ref(root: Path, work_id: str) -> Optional[str]:
    """Resolve plan file path for work_id. Check docs/work/active/{work_id}/plans/PLAN.md."""
    try:
        plan_path = root / "docs" / "work" / "active" / work_id / "plans" / "PLAN.md"
        if plan_path.exists():
            return f"docs/work/active/{work_id}/plans/PLAN.md"
        return None
    except Exception:
        return None
