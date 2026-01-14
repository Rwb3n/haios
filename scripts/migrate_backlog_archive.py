# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 23:40:25
#!/usr/bin/env python3
"""
E2-043: One-time backlog archival migration.
Moves non-active items from backlog.md to archive/backlog-complete.md.
Normalizes status values per ADR-033.
"""
import re
from pathlib import Path
from datetime import datetime

BACKLOG_PATH = Path("docs/pm/backlog.md")
ARCHIVE_PATH = Path("docs/pm/archive/backlog-complete.md")

# Status values that indicate non-active items
NON_ACTIVE_STATUSES = {"complete", "completed", "closed", "subsumed", "done", "cancelled"}

# Status normalization map (per ADR-033)
STATUS_NORMALIZE = {
    "completed": "complete",
    "done": "complete",
}

def parse_sections(content: str) -> list[dict]:
    """Parse backlog into sections."""
    sections = []
    lines = content.split('\n')

    current_section = None
    header_pattern = re.compile(r'^### \[([^\]]+)\] ([^:]+): (.+)$')
    status_pattern = re.compile(r'^- \*\*Status:\*\* (.+)$')

    for i, line in enumerate(lines):
        header_match = header_pattern.match(line)
        if header_match:
            # Save previous section
            if current_section:
                sections.append(current_section)

            current_section = {
                'start_line': i,
                'header_priority': header_match.group(1),
                'item_id': header_match.group(2),
                'title': header_match.group(3),
                'status': None,
                'lines': [line],
            }
        elif current_section:
            current_section['lines'].append(line)

            # Check for status field
            status_match = status_pattern.match(line)
            if status_match:
                current_section['status'] = status_match.group(1).strip().lower()

    # Don't forget last section
    if current_section:
        sections.append(current_section)

    return sections

def normalize_section(section: dict) -> str:
    """Normalize a section's status and header for archive."""
    lines = section['lines'].copy()

    # Normalize status in content
    old_status = section['status']
    new_status = STATUS_NORMALIZE.get(old_status, old_status)

    # Update header to [COMPLETE]
    header_pattern = re.compile(r'^### \[([^\]]+)\]')
    if lines:
        lines[0] = header_pattern.sub('### [COMPLETE]', lines[0])

    # Update status line
    for i, line in enumerate(lines):
        if line.startswith('- **Status:**'):
            lines[i] = f'- **Status:** {new_status}'
            break

    return '\n'.join(lines)

def main():
    print("E2-043: Backlog Archival Migration")
    print("=" * 50)

    # Read backlog
    content = BACKLOG_PATH.read_text(encoding='utf-8')

    # Split into header (before first ###) and sections
    first_section_idx = content.find('\n### ')
    if first_section_idx == -1:
        print("ERROR: No sections found in backlog")
        return

    header = content[:first_section_idx]
    sections_content = content[first_section_idx:]

    # Find archive reference section
    archive_ref_idx = sections_content.find('\n## Archive Reference')
    if archive_ref_idx != -1:
        footer = sections_content[archive_ref_idx:]
        sections_content = sections_content[:archive_ref_idx]
    else:
        footer = "\n---\n\n## Archive Reference\nCompleted items moved to `docs/pm/archive/backlog-complete.md` with completion date.\n"

    # Parse sections
    sections = parse_sections(sections_content)
    print(f"Found {len(sections)} total sections")

    # Categorize
    active = []
    archived = []

    for section in sections:
        if section['status'] and section['status'] in NON_ACTIVE_STATUSES:
            archived.append(section)
        else:
            active.append(section)

    print(f"Active items: {len(active)}")
    print(f"Items to archive: {len(archived)}")

    # Build archive content
    archive_header = f"""# HAIOS Backlog Archive - Completed Items

> **Migration Date:** {datetime.now().strftime('%Y-%m-%d')} (Session 70)
> **Source:** docs/pm/backlog.md
> **Reason:** ADR-036 PM Data Architecture - reduce active backlog bloat
> **Items Migrated:** {len(archived)}

This archive contains completed, closed, and subsumed work items.
Items preserve their original content for historical reference.
Status values normalized to `complete` per ADR-033.

---

## Epoch 2: Governance Suite (Archived)

"""

    archive_items = []
    for section in archived:
        normalized = normalize_section(section)
        archive_items.append(normalized)

    archive_content = archive_header + '\n'.join(archive_items)

    # Build reduced backlog
    active_items = []
    for section in active:
        active_items.append('\n'.join(section['lines']))

    new_backlog = header + '\n' + '\n'.join(active_items) + footer

    # Report
    print("\nItems being archived:")
    for section in archived:
        print(f"  - {section['item_id']}: {section['title']} (status: {section['status']})")

    print("\nItems remaining active:")
    for section in active:
        print(f"  - {section['item_id']}: {section['title']} (status: {section['status']})")

    # Write files
    print("\n" + "=" * 50)
    print(f"Writing archive to: {ARCHIVE_PATH}")
    ARCHIVE_PATH.write_text(archive_content, encoding='utf-8')

    print(f"Writing reduced backlog to: {BACKLOG_PATH}")
    BACKLOG_PATH.write_text(new_backlog, encoding='utf-8')

    # Stats
    original_lines = len(content.split('\n'))
    new_lines = len(new_backlog.split('\n'))
    archive_lines = len(archive_content.split('\n'))

    print(f"\nStats:")
    print(f"  Original backlog: {original_lines} lines")
    print(f"  New backlog: {new_lines} lines ({original_lines - new_lines} removed)")
    print(f"  Archive: {archive_lines} lines")
    print(f"  Reduction: {((original_lines - new_lines) / original_lines * 100):.1f}%")

if __name__ == "__main__":
    main()
