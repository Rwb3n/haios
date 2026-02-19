# generated: 2026-02-19
# WORK-173: Blocked-by cascade on work closure
"""
Blocked-by cascade on work closure (WORK-173).

When a work item closes, removes its ID from all active WORK.md
blocked_by fields. Fail-permissive: errors log warnings but never
block closure.

Note: This lib function writes directly to WORK.md files, following
the precedent set by cycle_state.py:sync_work_md_phase(). Targeted
field replacement (not full YAML re-serialization) minimizes mutation.
If WorkEngine's L4 invariant is ever code-enforced, this is a known
deviation to address.

Usage:
    from blocked_by_cascade import clear_blocked_by
    result = clear_blocked_by("WORK-101", base_path=Path("."))
    # result = {"cleared": ["WORK-160"], "errors": [], "skipped": []}

Integration: close-work recipe (justfile) calls clear-blocked-by after cascade.
"""
import json
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def _format_blocked_by(items: List[str]) -> str:
    """Format blocked_by list as YAML flow sequence.

    Uses manual formatting (not str() which produces Python syntax).
    YAML flow: [WORK-A, WORK-B] — no quotes needed for bare scalars.
    Python str(): ['WORK-A', 'WORK-B'] — single quotes break YAML parsing.

    Args:
        items: List of work item IDs.

    Returns:
        YAML flow sequence string (e.g., "[WORK-A, WORK-B]" or "[]").
    """
    if not items:
        return "[]"
    return "[" + ", ".join(items) + "]"


def _replace_blocked_by_block(content: str, new_value: str) -> str:
    """Replace the entire blocked_by field in WORK.md content.

    Handles both YAML formats found in production files:
      Flow:  blocked_by: [WORK-A, WORK-B]      (single line)
      Block: blocked_by:\\n- WORK-A\\n- WORK-B  (multi-line)

    Uses line-scanning to find the block boundary, then replaces
    the entire range with a single flow-style line.

    Args:
        content: Full WORK.md file content (with --- delimiters).
        new_value: YAML flow-style value (e.g., "[WORK-B]" or "[]").

    Returns:
        Updated content with blocked_by replaced.
    """
    lines = content.split("\n")
    start_idx = None
    end_idx = None

    for i, line in enumerate(lines):
        if start_idx is None:
            # Find the blocked_by field
            if re.match(r"^blocked_by:", line):
                start_idx = i
                # Check if it's flow style (value on same line with [)
                if re.match(r"^blocked_by:\s*\[", line):
                    end_idx = i + 1  # Flow style: single line
                    break
                # Block style: header line, items follow
                continue
        else:
            # We're inside a block-style blocked_by
            # Block items are "- VALUE" lines (with optional leading spaces)
            if re.match(r"^[\s]*-\s", line):
                end_idx = i + 1  # Extend block through list items
            else:
                # First non-list line = end of block
                if end_idx is None:
                    end_idx = start_idx + 1  # Empty block header only
                break

    if start_idx is None:
        return content  # No blocked_by field found

    # Handle case where block extends to end of content
    if end_idx is None:
        end_idx = start_idx + 1

    # Replace the entire block with a single flow-style line
    lines[start_idx:end_idx] = [f"blocked_by: {new_value}"]
    return "\n".join(lines)


def clear_blocked_by(
    closed_id: str,
    base_path: Optional[Path] = None,
    events_file: Optional[Path] = None,
) -> dict:
    """Remove closed_id from blocked_by in all active WORK.md files.

    Reads blocked_by via yaml.safe_load (reliable for both flow and block
    styles), then writes back using targeted line replacement (avoids full
    YAML re-serialization which corrupts multiline strings and quoting).

    Args:
        closed_id: The work item ID being closed (e.g., "WORK-101").
        base_path: Project root. Defaults to 4 levels up from __file__.
        events_file: Governance events file. Defaults to standard location.

    Returns:
        dict with keys:
        - cleared: List of work item IDs whose blocked_by was updated
        - errors: List of work item IDs where update failed
        - skipped: List of directory names with unparseable WORK.md
    """
    root = base_path or Path(__file__).parent.parent.parent.parent
    events = events_file or (root / ".claude" / "haios" / "governance-events.jsonl")
    active_dir = root / "docs" / "work" / "active"

    cleared = []
    errors = []
    skipped = []

    if not active_dir.exists():
        return {"cleared": cleared, "errors": errors, "skipped": skipped}

    for work_dir in sorted(active_dir.iterdir()):
        if not work_dir.is_dir():
            continue
        work_file = work_dir / "WORK.md"
        if not work_file.exists():
            continue

        try:
            content = work_file.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) < 3:
                skipped.append(work_dir.name)
                continue

            fm = yaml.safe_load(parts[1]) or {}
            blocked_by = fm.get("blocked_by", []) or []

            if closed_id not in blocked_by:
                continue

            # Remove closed_id, format as YAML flow sequence
            new_blocked = [b for b in blocked_by if b != closed_id]
            new_value = _format_blocked_by(new_blocked)

            # Replace entire blocked_by block (handles flow + block style)
            updated = _replace_blocked_by_block(content, new_value)
            work_file.write_text(updated, encoding="utf-8")

            cleared.append(fm.get("id", work_dir.name))

        except Exception as exc:
            item_id = work_dir.name
            errors.append(item_id)
            _log_warning(events, closed_id, item_id, str(exc))

    return {"cleared": cleared, "errors": errors, "skipped": skipped}


def _log_warning(events_file: Path, closed_id: str, failed_id: str, error: str) -> None:
    """Log a warning event for cascade failure (fail-permissive observability).

    Args:
        events_file: Path to governance-events.jsonl.
        closed_id: The work item ID that was being closed.
        failed_id: The downstream work item ID that failed to update.
        error: Error description.
    """
    try:
        event = {
            "type": "BlockedByCascadeWarning",
            "closed_id": closed_id,
            "failed_id": failed_id,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        }
        events_file.parent.mkdir(parents=True, exist_ok=True)
        with open(events_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception:
        pass  # Even logging failure is fail-permissive
