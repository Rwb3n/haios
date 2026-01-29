# generated: 2025-12-16
# System Auto: last updated on: 2026-01-25T21:59:20
#!/usr/bin/env python3
"""
Plan Tree Viewer - Shows milestone progress and dependency status.

DEPRECATION NOTICE (Session 241):
    This script duplicates WorkEngine.get_ready() logic.
    Prefer: just queue  (uses WorkEngine)
    This script will be removed after E2.3.

Usage:
    python scripts/plan_tree.py          # Show full tree
    python scripts/plan_tree.py --ready  # Show only ready (unblocked) items
"""

import json
import glob
import re
import sys
from pathlib import Path

def load_status():
    """Load haios-status.json"""
    status_path = Path(".claude/haios-status.json")
    if not status_path.exists():
        print("Error: .claude/haios-status.json not found")
        sys.exit(1)
    # Use utf-8-sig to handle BOM from PowerShell
    with open(status_path, encoding='utf-8-sig') as f:
        return json.load(f)

def get_work_info(work_path: str) -> dict:
    """Extract frontmatter info from a work file."""
    with open(work_path, encoding='utf-8-sig') as f:
        content = f.read()

    info = {
        "path": work_path,
        "backlog_id": None,
        "status": None,
        "blocked_by": [],
        "title": None
    }

    # Parse frontmatter - work files use 'id:' not 'backlog_id:'
    if match := re.search(r'^id:\s*(\S+)', content, re.MULTILINE):
        info["backlog_id"] = match.group(1)
    if match := re.search(r'^status:\s*(\S+)', content, re.MULTILINE):
        info["status"] = match.group(1)
    if match := re.search(r'blocked_by:\s*\[([^\]]*)\]', content):
        blockers = match.group(1)
        info["blocked_by"] = [b.strip() for b in blockers.split(',') if b.strip()]
    if match := re.search(r'^title:\s*["\']?([^"\'\n]+)', content, re.MULTILINE):
        info["title"] = match.group(1).strip('"\'')

    return info

def main():
    ready_only = "--ready" in sys.argv
    filter_milestone = None
    if "--milestone" in sys.argv:
        idx = sys.argv.index("--milestone")
        if idx + 1 < len(sys.argv):
            filter_milestone = sys.argv[idx + 1]

    status = load_status()
    milestones = status.get("milestones", {})

    # Filter to single milestone if specified
    if filter_milestone:
        milestones = {k: v for k, v in milestones.items() if k == filter_milestone}

    # Load all work files (canonical source per ADR-039)
    # Only read from active/ directory - archive/ contains closed items
    # E2-212: Support both directory structure and flat files
    plans = {}
    active_dir = Path("docs/work/active")
    if active_dir.exists():
        # Check for directory structure first
        for subdir in active_dir.iterdir():
            if subdir.is_dir():
                work_md = subdir / "WORK.md"
                if work_md.exists():
                    info = get_work_info(str(work_md))
                    if info["backlog_id"]:
                        plans[info["backlog_id"]] = info
        # Fall back to flat file pattern
        for work_path in glob.glob("docs/work/active/WORK-*.md"):
            info = get_work_info(work_path)
            if info["backlog_id"] and info["backlog_id"] not in plans:
                plans[info["backlog_id"]] = info

    # Global complete set for cross-milestone dependency checking
    all_complete = set()
    for ms in milestones.values():
        all_complete.update(ms.get("complete", []))

    if ready_only:
        print("READY (unblocked across all milestones):")
        # Scan ALL work files in active/, not just milestone-registered items
        # Session 187: Milestones deprecated, chapters are the new taxonomy
        # Session 241: Match WorkEngine terminal statuses (was only filtering 'complete')
        terminal_statuses = {"complete", "archived", "dismissed", "invalid", "deferred"}
        for item_id, plan in plans.items():
            status = plan.get("status", "")
            if status in terminal_statuses:
                continue
            blockers = plan.get("blocked_by", [])
            if not blockers or all(b in all_complete for b in blockers):
                title = plan.get("title", "")
                print(f"  {item_id}: {title[:50]}")
        return

    # Full tree view - iterate all milestones
    for ms_name, milestone in milestones.items():
        items = milestone.get("items", [])
        complete = milestone.get("complete", [])
        progress = milestone.get("progress", 0)

        print(f"{ms_name}: {progress}% ({len(complete)}/{len(items)} complete)")
        print()

        print("COMPLETE:")
        for item_id in complete:
            plan = plans.get(item_id, {})
            title = plan.get("title", "")[:40]
            print(f"  [x] {item_id}: {title}")
        print()

        print("REMAINING:")
        for item_id in items:
            if item_id in complete:
                continue
            plan = plans.get(item_id, {})
            title = plan.get("title", "")[:40]
            blockers = plan.get("blocked_by", [])

            # Check if ready (blockers can be from any milestone)
            is_ready = not blockers or all(b in all_complete for b in blockers)
            status_marker = "READY" if is_ready else f"blocked by {blockers}"

            print(f"  [ ] {item_id}: {title}")
            print(f"      -> {status_marker}")
        print()

if __name__ == "__main__":
    main()
