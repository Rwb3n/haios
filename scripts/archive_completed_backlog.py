# generated: 2025-12-22
# System Auto: last updated on: 2025-12-22T09:37:11
#!/usr/bin/env python3
"""
Archive completed backlog items to reduce file size.

Moves [COMPLETE], [CLOSED], [ABSORBED] items to backlog_archive.md

Session 96 Note: Keep this script for future backlog redesign reference.
- Shows pattern for parsing markdown-based backlog items
- Could inform migration to DB-backed backlog (Epoch 3 scaling concern)
- Related: INV-021 (Work Item Taxonomy), E2-069 (Roadmap Structure)
"""
import re
from pathlib import Path
from datetime import datetime

def main():
    backlog_path = Path("docs/pm/backlog.md")
    archive_path = Path("docs/pm/backlog_archive.md")

    content = backlog_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Pattern to match completed items
    completed_pattern = re.compile(r"^### \[(COMPLETE|CLOSED|ABSORBED)\]")

    # Find all item boundaries (### headers)
    item_starts = []
    for i, line in enumerate(lines):
        if line.startswith("### ["):
            item_starts.append(i)

    # Add end marker
    item_starts.append(len(lines))

    # Separate completed from active
    completed_items = []
    active_lines = []

    i = 0
    for idx, start in enumerate(item_starts[:-1]):
        end = item_starts[idx + 1]
        item_lines = lines[start:end]
        header = item_lines[0]

        # Add lines before first item
        if idx == 0:
            active_lines.extend(lines[:start])

        if completed_pattern.match(header):
            completed_items.append("\n".join(item_lines))
        else:
            active_lines.extend(item_lines)

    # Create archive file
    archive_header = f"""# generated: {datetime.now().strftime('%Y-%m-%d')}
# HAIOS Backlog Archive

> **Purpose:** Completed, closed, and absorbed work items moved from main backlog.
> **Note:** These items are preserved for historical reference and memory linkage.

---

## Archived Items ({len(completed_items)} items)

"""

    archive_content = archive_header + "\n\n".join(completed_items) + "\n"

    # Write archive
    archive_path.write_text(archive_content, encoding="utf-8")
    print(f"Archived {len(completed_items)} items to {archive_path}")

    # Write updated backlog
    new_backlog = "\n".join(active_lines)
    backlog_path.write_text(new_backlog, encoding="utf-8")

    # Stats
    old_lines = len(lines)
    new_lines = len(active_lines)
    print(f"Backlog: {old_lines} -> {new_lines} lines (saved {old_lines - new_lines})")

if __name__ == "__main__":
    main()
