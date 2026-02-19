"""
Retro-cycle scale assessment (WORK-171).

Computable predicate for retro-cycle Phase 0: determines if a work item
is 'trivial' or 'substantial' based on 4 machine-checkable conditions.

Follows session_end_actions.py pattern:
- Pure functions in lib/
- Fail-permissive (never raises)
- _default_project_root() for path derivation
- Testable without hook infrastructure
"""
import json
import subprocess
from pathlib import Path
from typing import Optional


def _default_project_root() -> Path:
    """Derive project root from this file's location.

    lib/ -> haios/ -> .claude/ -> project root.
    NOT Path.cwd() — hook subprocess cwd is not guaranteed.
    """
    return Path(__file__).parent.parent.parent.parent


def _get_changed_files(project_root: Path) -> list[str]:
    """Get list of changed files via git diff (fail-safe: empty list).

    Uses HEAD~5 as a reasonable approximation of session-scoped changes.

    Args:
        project_root: Project root for git commands.

    Returns:
        List of changed file paths, or empty list on error.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~5"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(project_root),
        )
        if result.returncode != 0:
            return []
        return [f for f in result.stdout.splitlines() if f.strip()]
    except Exception:
        return []


def assess_scale(
    work_id: str,
    project_root: Optional[Path] = None,
) -> str:
    """Assess work item scale for retro-cycle Phase 0.

    Computable predicate: trivial if ALL of:
    1. files_changed <= 2
    2. no plan exists in docs/work/active/{work_id}/plans/
    3. no test files in changed files
    4. no CyclePhaseEntered governance events for work_id

    Args:
        work_id: Work item ID (e.g., "WORK-171")
        project_root: Project root. Defaults to derived path.

    Returns:
        "trivial" or "substantial". Defaults to "substantial" on error.
    """
    try:
        root = project_root or _default_project_root()

        # Condition 1: files_changed <= 2
        changed = _get_changed_files(root)
        if len(changed) > 2:
            return "substantial"

        # Condition 2: no plan exists
        plan_path = root / "docs" / "work" / "active" / work_id / "plans" / "PLAN.md"
        if plan_path.exists():
            return "substantial"

        # Condition 3: no test files changed
        if any(f.startswith("tests/") or f.startswith("tests\\") for f in changed):
            return "substantial"

        # Condition 4: no CyclePhaseEntered events for work_id
        events_file = root / ".claude" / "haios" / "governance-events.jsonl"
        if events_file.exists():
            for line in events_file.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                    if (
                        event.get("type") == "CyclePhaseEntered"
                        and event.get("work_id") == work_id
                    ):
                        return "substantial"
                except json.JSONDecodeError:
                    continue

        return "trivial"
    except Exception:
        return "substantial"  # Fail-safe: assume substantial
