# generated: 2025-12-24
# System Auto: last updated on: 2026-01-21T22:18:57
# DEPRECATED: E2-251 migrated this functionality to WorkEngine
# Use: python .claude/haios/modules/cli.py backfill <id>
# This file remains for reference only - will be removed in E2-255
"""DEPRECATED: Backfill - migrated to WorkEngine.backfill() in E2-251.

Backfill work files from backlog entries.

E2-170: Work items created by E2-151 migration have placeholder content.
This module parses backlog.md/backlog_archive.md and updates work files
with actual Context, Deliverables, Milestone, and spawned_by data.

Usage:
    from backfill import backfill_work_item, backfill_all
    backfill_work_item("E2-021")  # Single item
    backfill_all()  # All active work items
"""

import re
from pathlib import Path
from typing import Any

# Project root is 4 levels up from .claude/haios/lib/
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def parse_backlog_entry(backlog_id: str, content: str) -> dict[str, Any] | None:
    """Parse a backlog entry and extract key fields.

    Args:
        backlog_id: ID like "E2-021", "INV-015"
        content: Full backlog.md or backlog_archive.md content

    Returns:
        Dict with: context, deliverables, milestone, session, spawned_by, related,
                   status, closed_date
        or None if not found.
    """
    # Find entry by pattern: ### [STATUS] {backlog_id}:
    # Note: [^\]]* ensures status doesn't span lines (vs .*? with DOTALL)
    pattern = rf"^### \[[^\]]*\] {re.escape(backlog_id)}:.*?(?=^### |\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if not match:
        return None

    entry_text = match.group(0)
    result: dict[str, Any] = {
        "context": "",
        "deliverables": [],
        "milestone": None,
        "session": None,
        "spawned_by": None,
        "related": [],
        "status": None,
        "closed_date": None,
    }

    # Extract fields using regex
    # Context comes from **Context:** line
    ctx_match = re.search(
        r"\*\*Context:\*\*\s*(.+?)(?=\n- \*\*|\n\n|\n- \*\*Vision|\Z)",
        entry_text,
        re.DOTALL,
    )
    if ctx_match:
        result["context"] = ctx_match.group(1).strip()

    # Milestone
    mile_match = re.search(r"\*\*Milestone:\*\*\s*(\S+)", entry_text)
    if mile_match:
        result["milestone"] = mile_match.group(1)

    # Session
    sess_match = re.search(r"\*\*Session:\*\*\s*(.+?)(?=\n|$)", entry_text)
    if sess_match:
        result["session"] = sess_match.group(1).strip()

    # Spawned By
    spawn_match = re.search(r"\*\*Spawned By:\*\*\s*(.+?)(?=\n|$)", entry_text)
    if spawn_match:
        result["spawned_by"] = spawn_match.group(1).strip()

    # Related
    related_match = re.search(r"\*\*Related:\*\*\s*(.+?)(?=\n|$)", entry_text)
    if related_match:
        result["related"] = related_match.group(1).strip()

    # Deliverables - find checklist items (indented with - [ ])
    deliverables = re.findall(r"^\s*-\s*\[[ x]\]\s*(.+)$", entry_text, re.MULTILINE)
    result["deliverables"] = deliverables

    # Status from header
    status_match = re.search(r"^### \[(\w+)\]", entry_text)
    if status_match:
        result["status"] = status_match.group(1).lower()

    # Closed date (for archive)
    closed_match = re.search(r"\*\*Closed:\*\*\s*(.+?)(?=\n|$)", entry_text)
    if closed_match:
        result["closed_date"] = closed_match.group(1).strip()

    # Memory refs - parse various formats:
    # "Concepts 64641-64652" -> [64641, 64642, ..., 64652]
    # "Concept 62539" -> [62539]
    # "50372, 50388, 71375" -> [50372, 50388, 71375]
    memory_match = re.search(r"\*\*Memory:\*\*\s*(.+?)(?=\n|$)", entry_text)
    if memory_match:
        memory_str = memory_match.group(1).strip()
        memory_ids: list[int] = []

        # Range format: "Concepts 64641-64652"
        range_match = re.search(r"(\d+)-(\d+)", memory_str)
        if range_match:
            start, end = int(range_match.group(1)), int(range_match.group(2))
            memory_ids.extend(range(start, end + 1))
        else:
            # Single or comma-separated: "Concept 62539" or "50372, 50388"
            id_matches = re.findall(r"\d+", memory_str)
            memory_ids.extend(int(x) for x in id_matches)

        result["memory_refs"] = memory_ids

    return result


def update_work_file(work_path: Path, parsed: dict[str, Any], force: bool = False) -> str:
    """Update work file with parsed backlog content.

    Updates:
    - Context section with parsed context
    - Deliverables section with checklist items
    - Frontmatter: milestone, spawned_by

    Args:
        work_path: Path to work file
        parsed: Dict from parse_backlog_entry()
        force: If True, replace context even if placeholder not found

    Returns:
        Updated file content (does NOT write to disk)
    """
    content = work_path.read_text(encoding="utf-8")

    # Update Context section
    if parsed["context"]:
        if "[Problem and root cause]" in content:
            content = content.replace(
                "[Problem and root cause]", f"**Problem:** {parsed['context']}"
            )
        elif force:
            # Force mode: replace existing **Problem:** line
            content = re.sub(
                r"\*\*Problem:\*\*.*?(?=\n---|\n\n##)",
                f"**Problem:** {parsed['context']}",
                content,
                count=1,
                flags=re.DOTALL,
            )

    # Update Deliverables section
    if parsed["deliverables"]:
        old_deliverables = "- [ ] [Deliverable 1]\n- [ ] [Deliverable 2]"
        new_deliverables = "\n".join(f"- [ ] {d}" for d in parsed["deliverables"])
        content = content.replace(old_deliverables, new_deliverables)

    # Update frontmatter - milestone
    if parsed["milestone"]:
        content = re.sub(r"milestone: null", f"milestone: {parsed['milestone']}", content)

    # Update frontmatter - spawned_by
    if parsed["spawned_by"]:
        content = re.sub(
            r"spawned_by: null", f'spawned_by: "{parsed["spawned_by"]}"', content
        )

    # Update frontmatter - memory_refs
    if parsed.get("memory_refs"):
        refs_str = str(parsed["memory_refs"])
        if "memory_refs: []" in content:
            content = re.sub(r"memory_refs: \[\]", f"memory_refs: {refs_str}", content)
        elif force:
            content = re.sub(r"memory_refs: \[.*?\]", f"memory_refs: {refs_str}", content)

    return content


def backfill_work_item(backlog_id: str, force: bool = False) -> bool:
    """Backfill a single work item from backlog sources.

    Args:
        backlog_id: ID like "E2-021"
        force: If True, re-process even if placeholder not found

    Returns:
        True if successfully backfilled, False if not found or no changes
    """
    # Find work file
    work_dir = PROJECT_ROOT / "docs" / "work" / "active"
    matches = list(work_dir.glob(f"WORK-{backlog_id}-*.md"))
    if not matches:
        return False

    work_path = matches[0]

    # Try backlog.md first, then archive
    backlog_path = PROJECT_ROOT / "docs" / "pm" / "backlog.md"
    archive_path = PROJECT_ROOT / "docs" / "pm" / "backlog_archive.md"

    parsed = None
    for source in [backlog_path, archive_path]:
        if source.exists():
            source_content = source.read_text(encoding="utf-8")
            parsed = parse_backlog_entry(backlog_id, source_content)
            if parsed:
                break

    if not parsed:
        return False

    # Update work file
    new_content = update_work_file(work_path, parsed, force=force)
    work_path.write_text(new_content, encoding="utf-8")
    return True


def backfill_all(force: bool = False) -> dict[str, list[str]]:
    """Backfill all active work items.

    Args:
        force: If True, re-process all files even if already filled

    Returns:
        Dict with 'success', 'not_found', 'no_changes' lists of IDs
    """
    work_dir = PROJECT_ROOT / "docs" / "work" / "active"
    results: dict[str, list[str]] = {"success": [], "not_found": [], "no_changes": []}

    for work_file in work_dir.glob("WORK-*.md"):
        # Extract ID from filename: WORK-E2-021-title.md -> E2-021
        match = re.match(r"WORK-([A-Z0-9]+-\d+)[-.]", work_file.name)
        if not match:
            continue

        backlog_id = match.group(1)

        # Check if already has content (not placeholder)
        content = work_file.read_text(encoding="utf-8")
        if "[Problem and root cause]" not in content and not force:
            results["no_changes"].append(backlog_id)
            continue

        if backfill_work_item(backlog_id, force=force):
            results["success"].append(backlog_id)
        else:
            results["not_found"].append(backlog_id)

    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        backlog_id = sys.argv[1].upper()
        if backfill_work_item(backlog_id):
            print(f"Backfilled {backlog_id}")
        else:
            print(f"Not found or no changes: {backlog_id}")
    else:
        results = backfill_all()
        print(f"Success: {len(results['success'])} items")
        print(f"Not found in backlog: {len(results['not_found'])} items")
        print(f"Already has content: {len(results['no_changes'])} items")
        if results["not_found"]:
            print(f"  Not found: {', '.join(results['not_found'][:10])}...")
