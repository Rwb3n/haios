# generated: 2025-12-22
# System Auto: last updated on: 2026-01-21T22:18:35
# DEPRECATED: E2-251 migrated this functionality to WorkEngine
# Use: python .claude/haios/modules/cli.py cascade <id> <status>
# This file remains for reference only - will be removed in E2-255
"""DEPRECATED: Cascade module - migrated to WorkEngine.cascade() in E2-251.

Cascade module - propagates status changes through dependency graph.

Heartbeat mechanism that runs when work items complete.

CASCADE TYPES:
1. UNBLOCK - Items blocked by completed item, check if now ready
2. RELATED - Items related to completed item, may need review
3. MILESTONE - Recalculate milestone progress
4. SUBSTANTIVE - CLAUDE.md/README references need update
5. REVIEW_PROMPT - Stale unblocked plans need review

TRIGGERS:
- Plan status: complete/completed/done
- ADR status: accepted
- Investigation status: complete

Usage:
    from cascade import run_cascade
    result = run_cascade("E2-110", "complete")
    print(result["message"])

Migrated from CascadeHook.ps1 (E2-076e) in Session 97.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

# Project root detection (4 levels up from .claude/haios/lib/)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DOCS_PATH = PROJECT_ROOT / "docs"
PLANS_PATH = DOCS_PATH / "plans"
BACKLOG_PATH = DOCS_PATH / "pm" / "backlog.md"
STATUS_FILE = PROJECT_ROOT / ".claude" / "haios-status.json"
EVENTS_FILE = PROJECT_ROOT / ".claude" / "haios-events.jsonl"

# Trigger statuses
TRIGGER_STATUSES = {"complete", "completed", "done", "closed", "accepted"}

# Stale threshold (sessions since last update = extra urgency)
STALE_THRESHOLD = 3


def parse_yaml_frontmatter(content: str) -> dict[str, Any]:
    """Extract YAML frontmatter from markdown content.

    Args:
        content: Full markdown file content

    Returns:
        Dict of frontmatter fields, or empty dict if no frontmatter
    """
    match = re.match(r'^---\s*\n([\s\S]*?)\n---', content)
    if not match:
        return {}

    yaml_str = match.group(1)
    result = {}

    # Parse simple YAML fields
    for line in yaml_str.split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip()

            # Handle arrays [item1, item2]
            if value.startswith('[') and value.endswith(']'):
                items = value[1:-1].split(',')
                result[key] = [item.strip().strip('"\'') for item in items if item.strip()]
            else:
                result[key] = value.strip('"\'')

    return result


def is_item_complete(item_id: str) -> bool:
    """Check if a backlog item is complete.

    Args:
        item_id: Backlog ID like "E2-110"

    Returns:
        True if item is complete/closed
    """
    # Check plan files
    for plan_file in PLANS_PATH.glob(f"PLAN-{item_id}*.md"):
        try:
            content = plan_file.read_text(encoding='utf-8')
            if re.search(r'status:\s*(complete|completed|done|closed)', content, re.IGNORECASE):
                return True
        except Exception:
            continue

    # Check backlog for CLOSED/COMPLETE
    if BACKLOG_PATH.exists():
        try:
            backlog = BACKLOG_PATH.read_text(encoding='utf-8')
            if re.search(rf'\[CLOSED\].*{item_id}|{item_id}.*\[CLOSED\]|\[COMPLETE\].*{item_id}', backlog):
                return True
        except Exception:
            pass

    return False


def get_unblocked_items(completed_id: str) -> list[dict]:
    """Find items that were blocked by completed item.

    CASCADE 1: UNBLOCK

    Args:
        completed_id: ID of the item that just completed

    Returns:
        List of dicts with id, status (READY/STILL_BLOCKED), message, remaining blockers
    """
    results = []

    if not PLANS_PATH.exists():
        return results

    for plan_file in PLANS_PATH.glob("*.md"):
        try:
            content = plan_file.read_text(encoding='utf-8')
        except Exception:
            continue

        fm = parse_yaml_frontmatter(content)
        blocked_by = fm.get('blocked_by', [])

        if not blocked_by:
            continue

        # Ensure it's a list
        if isinstance(blocked_by, str):
            blocked_by = [blocked_by]

        # Only process if this item was blocked by our completed item
        if completed_id not in blocked_by:
            continue

        item_id = fm.get('backlog_id')
        item_status = fm.get('status', 'unknown')

        if not item_id:
            continue

        # Skip if already complete
        if item_status.lower() in TRIGGER_STATUSES:
            continue

        # Check if ALL blockers are now complete
        remaining_blockers = []
        for blocker in blocked_by:
            if blocker == completed_id:
                continue  # This one is now complete
            if not is_item_complete(blocker):
                remaining_blockers.append(blocker)

        last_session = int(fm.get('session', 0)) if fm.get('session', '').isdigit() else 0

        if len(remaining_blockers) == 0:
            results.append({
                'id': item_id,
                'status': 'READY',
                'message': f"{item_id} is now READY (was blocked_by: {completed_id})",
                'last_session': last_session,
                'remaining': []
            })
        else:
            results.append({
                'id': item_id,
                'status': 'STILL_BLOCKED',
                'message': f"{item_id} still blocked by [{', '.join(remaining_blockers)}]",
                'last_session': last_session,
                'remaining': remaining_blockers
            })

    return results


def get_related_items(completed_id: str) -> list[dict]:
    """Find items with bidirectional related relationship.

    CASCADE 2: RELATED
    Checks BOTH directions:
    - Items that list completed_id in THEIR related array (inbound)
    - Items that completed_id lists in ITS related array (outbound)

    Args:
        completed_id: ID of the item that just completed

    Returns:
        List of dicts with id, direction, reason
    """
    results = []
    seen_ids = set()

    if not PLANS_PATH.exists():
        return results

    # DIRECTION 1: Find items that list completed_id in THEIR related array
    for plan_file in PLANS_PATH.glob("*.md"):
        try:
            content = plan_file.read_text(encoding='utf-8')
        except Exception:
            continue

        fm = parse_yaml_frontmatter(content)
        related = fm.get('related', [])

        if isinstance(related, str):
            related = [related]

        if completed_id in related:
            item_id = fm.get('backlog_id')
            item_status = fm.get('status', 'unknown')

            if item_id and item_id != completed_id and item_status.lower() not in TRIGGER_STATUSES:
                if item_id not in seen_ids:
                    seen_ids.add(item_id)
                    results.append({
                        'id': item_id,
                        'direction': 'inbound',
                        'reason': f"lists {completed_id} in its related array"
                    })

    # DIRECTION 2: Find items that completed_id lists in ITS related array
    for completed_plan in PLANS_PATH.glob(f"PLAN-{completed_id}*.md"):
        try:
            content = completed_plan.read_text(encoding='utf-8')
        except Exception:
            continue

        fm = parse_yaml_frontmatter(content)
        related = fm.get('related', [])

        if isinstance(related, str):
            related = [related]

        for related_id in related:
            if not related_id or related_id == completed_id:
                continue
            if related_id in seen_ids:
                continue

            # Check if this related item exists and is active
            for related_plan in PLANS_PATH.glob(f"PLAN-{related_id}*.md"):
                try:
                    related_content = related_plan.read_text(encoding='utf-8')
                except Exception:
                    continue

                related_fm = parse_yaml_frontmatter(related_content)
                related_status = related_fm.get('status', 'unknown')

                if related_status.lower() not in TRIGGER_STATUSES:
                    seen_ids.add(related_id)
                    results.append({
                        'id': related_id,
                        'direction': 'outbound',
                        'reason': f"{completed_id} listed it in related array"
                    })

    return results


def get_milestone_delta(completed_id: str) -> dict | None:
    """Calculate milestone progress delta.

    CASCADE 3: MILESTONE

    Args:
        completed_id: ID of the item that just completed

    Returns:
        Dict with milestone, name, old, new, delta - or None if no milestone affected
    """
    if not STATUS_FILE.exists():
        return None

    try:
        status = json.loads(STATUS_FILE.read_text(encoding='utf-8'))
    except Exception:
        return None

    milestones = status.get('milestones', {})

    for milestone_id, milestone in milestones.items():
        items = milestone.get('items', [])

        if completed_id in items:
            prior_progress = milestone.get('prior_progress', 0)
            current_progress = milestone.get('progress', 0)

            # Calculate new progress
            complete_items = list(milestone.get('complete', []))
            if completed_id not in complete_items:
                complete_items.append(completed_id)

            total_items = len(items)
            new_progress = round((len(complete_items) / total_items) * 100) if total_items > 0 else 0

            return {
                'milestone': milestone_id,
                'name': milestone.get('name', milestone_id),
                'old': current_progress,
                'new': new_progress,
                'delta': new_progress - current_progress
            }

    return None


def get_substantive_references(completed_id: str) -> list[dict]:
    """Check CLAUDE.md and READMEs for references.

    CASCADE 4: SUBSTANTIVE

    Args:
        completed_id: ID of the item that just completed

    Returns:
        List of dicts with file, type, message
    """
    results = []

    check_files = [
        PROJECT_ROOT / "CLAUDE.md",
        PROJECT_ROOT / "README.md",
        DOCS_PATH / "README.md"
    ]

    for file_path in check_files:
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                if completed_id in content:
                    relative_path = str(file_path.relative_to(PROJECT_ROOT))
                    results.append({
                        'file': relative_path,
                        'type': 'substantive',
                        'message': f"{relative_path} references {completed_id} -> Consider update"
                    })
            except Exception:
                continue

    return results


def get_review_prompts(unblocked_items: list[dict], current_session: int) -> list[dict]:
    """Identify stale unblocked plans needing review.

    CASCADE 5: REVIEW_PROMPT

    Args:
        unblocked_items: List of items that are now unblocked
        current_session: Current session number

    Returns:
        List of dicts with id, last_session, sessions_ago, message
    """
    results = []

    for item in unblocked_items:
        if item['status'] == 'READY':
            last_session = item.get('last_session', 0)
            sessions_ago = current_session - last_session if last_session > 0 else 0

            urgency = ""
            if sessions_ago >= STALE_THRESHOLD:
                urgency = f" (STALE: {sessions_ago} sessions ago)"

            results.append({
                'id': item['id'],
                'last_session': last_session,
                'sessions_ago': sessions_ago,
                'message': f"SHOULD review {item['id']} before implementation - blocker work may affect plan{urgency}"
            })

    return results


def format_cascade_message(
    completed_id: str,
    new_status: str,
    unblocked_items: list[dict],
    related_items: list[dict],
    milestone_delta: dict | None,
    substantive_refs: list[dict],
    review_prompts: list[dict]
) -> dict:
    """Build cascade message and effects list.

    Args:
        completed_id: ID of completed item
        new_status: New status value
        unblocked_items: From get_unblocked_items
        related_items: From get_related_items
        milestone_delta: From get_milestone_delta
        substantive_refs: From get_substantive_references
        review_prompts: From get_review_prompts

    Returns:
        Dict with 'message' (str) and 'effects' (list)
    """
    lines = []
    lines.append("--- Cascade (Heartbeat) ---")
    lines.append(f"{completed_id} status: {new_status}")
    lines.append("")

    effects = []

    # UNBLOCK section
    ready_items = [i for i in unblocked_items if i['status'] == 'READY']
    still_blocked = [i for i in unblocked_items if i['status'] == 'STILL_BLOCKED']

    if ready_items or still_blocked:
        lines.append("[UNBLOCK]")
        for item in ready_items:
            lines.append(f"  - {item['message']}")
            effects.append(f"unblock:{item['id']}")
        for item in still_blocked:
            lines.append(f"  - {item['message']}")
        lines.append("")

    # REVIEW PROMPT section
    if review_prompts:
        lines.append("[REVIEW PROMPT]")
        for item in review_prompts:
            lines.append(f"  - {item['message']}")
        lines.append("")

    # RELATED section
    if related_items:
        lines.append("[RELATED - REVIEW REQUIRED]")
        lines.append("  Implementation may have drifted from plan. MUST review for:")
        lines.append("    - Scope overlap (did completed work partially fulfill this?)")
        lines.append("    - Changed assumptions (does completed work affect approach?)")
        lines.append("    - New patterns (should this follow patterns established?)")
        lines.append("")
        for item in related_items:
            direction_label = "outbound" if item['direction'] == "outbound" else "inbound"
            lines.append(f"  [{direction_label}] {item['id']}")
            lines.append(f"    Reason: {item['reason']}")
        lines.append("")
        effects.append(f"related:{len(related_items)}")

    # MILESTONE section
    if milestone_delta and milestone_delta.get('delta', 0) > 0:
        lines.append("[MILESTONE]")
        lines.append(f"  - {milestone_delta['name']}: {milestone_delta['old']}% -> {milestone_delta['new']}% (+{milestone_delta['delta']}%)")
        effects.append(f"milestone:+{milestone_delta['delta']}")
        lines.append("")

    # SUBSTANTIVE section
    if substantive_refs:
        lines.append("[SUBSTANTIVE]")
        for ref in substantive_refs:
            lines.append(f"  - {ref['message']}")
        lines.append("")

    # Next action
    if ready_items:
        next_item = ready_items[0]['id']
        lines.append(f"Action: {next_item} is next in sequence.")
    elif not unblocked_items and not related_items:
        lines.append("No dependents affected.")

    lines.append("--- End Cascade ---")

    return {
        'message': '\n'.join(lines),
        'effects': effects
    }


def write_cascade_event(source_id: str, effects: list[str]) -> None:
    """Write cascade event to haios-events.jsonl.

    Args:
        source_id: ID of the source item
        effects: List of effect strings
    """
    event = {
        'ts': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        'type': 'cascade',
        'source': source_id,
        'effects': effects
    }

    with open(EVENTS_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event) + '\n')


def get_current_session() -> int:
    """Get current session number from status file.

    Returns:
        Session number, defaults to 97
    """
    if STATUS_FILE.exists():
        try:
            status = json.loads(STATUS_FILE.read_text(encoding='utf-8'))
            # Try multiple paths for session number
            if 'pm' in status and 'last_session' in status['pm']:
                return status['pm']['last_session']
            if 'session_delta' in status and status['session_delta']:
                return status['session_delta'].get('current_session', 97)
        except Exception:
            pass
    return 97


def run_cascade(backlog_id: str, new_status: str, dry_run: bool = False) -> dict:
    """Run full cascade for a completed item.

    Main entry point for cascade processing.

    Args:
        backlog_id: ID of the item that just completed (e.g., "E2-110")
        new_status: New status value (e.g., "complete")
        dry_run: If True, don't write events or refresh status

    Returns:
        Dict with 'message', 'effects', 'triggered' (bool)
    """
    # Only trigger on completion statuses
    if new_status.lower() not in TRIGGER_STATUSES:
        return {
            'message': f"Status '{new_status}' does not trigger cascade",
            'effects': [],
            'triggered': False
        }

    current_session = get_current_session()

    # Run all cascade checks
    unblocked_items = get_unblocked_items(backlog_id)
    related_items = get_related_items(backlog_id)
    milestone_delta = get_milestone_delta(backlog_id)
    substantive_refs = get_substantive_references(backlog_id)
    review_prompts = get_review_prompts(unblocked_items, current_session)

    # Format message
    result = format_cascade_message(
        completed_id=backlog_id,
        new_status=new_status,
        unblocked_items=unblocked_items,
        related_items=related_items,
        milestone_delta=milestone_delta,
        substantive_refs=substantive_refs,
        review_prompts=review_prompts
    )

    # Write event log
    if result['effects'] and not dry_run:
        write_cascade_event(backlog_id, result['effects'])

    # Refresh status (import here to avoid circular import)
    if not dry_run:
        try:
            from status import generate_slim_status, write_slim_status
            slim = generate_slim_status()
            write_slim_status(slim, str(PROJECT_ROOT / ".claude" / "haios-status-slim.json"))
        except Exception:
            pass  # Status refresh is best-effort

    result['triggered'] = True
    return result


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python cascade.py <backlog_id> <new_status> [--dry-run]")
        print("Example: python cascade.py E2-110 complete")
        sys.exit(1)

    backlog_id = sys.argv[1]
    new_status = sys.argv[2]
    dry_run = "--dry-run" in sys.argv

    result = run_cascade(backlog_id, new_status, dry_run=dry_run)
    print(result['message'])

    if dry_run:
        print("\n[DRY RUN - No changes made]")
