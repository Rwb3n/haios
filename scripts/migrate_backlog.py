# generated: 2025-12-23
# System Auto: last updated on: 2025-12-23T19:05:45
#!/usr/bin/env python3
# generated: 2025-12-23
"""Migrate backlog.md entries to WORK-{id}.md files.

E2-151: Phase A.2 of M6-WorkCycle migration.

Usage:
    python scripts/migrate_backlog.py --dry-run  # Preview without creating files
    python scripts/migrate_backlog.py            # Execute full migration
"""

import argparse
import re
import sys
from pathlib import Path

# Add .claude/lib to path for scaffold imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "lib"))
from scaffold import scaffold_template

PROJECT_ROOT = Path(__file__).parent.parent


def parse_backlog_entry(text: str) -> dict:
    """Parse a single backlog entry from markdown.

    Args:
        text: Markdown text of a single backlog entry (### [...] ID: Title)

    Returns:
        Dict with extracted fields: id, title, priority, status, owner, etc.
    """
    result = {}

    # Header: ### [PRIORITY] ID: Title
    header_match = re.match(r"### \[(\w+)\] ([\w-]+): (.+)", text.strip())
    if header_match:
        result["priority"] = header_match.group(1).lower()
        result["id"] = header_match.group(2)
        result["title"] = header_match.group(3).strip()

    # Fields: - **Field:** value
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("- **"):
            match = re.match(r"- \*\*(\w+):\*\* (.+)", line)
            if match:
                field = match.group(1).lower()
                value = match.group(2).strip()
                result[field] = value

    return result


def map_to_work_schema(entry: dict) -> dict:
    """Map backlog entry to work file schema.

    Args:
        entry: Dict from parse_backlog_entry

    Returns:
        Dict with work file schema fields.
    """
    return {
        "id": entry.get("id"),
        "title": entry.get("title", "Untitled"),
        "status": "active",  # All migrated items start active
        "priority": entry.get("priority", "medium"),
        "current_node": "backlog",  # Start in backlog node
        "spawned_by": entry.get("spawned_by"),
        "milestone": entry.get("milestone"),
        "context": entry.get("context", ""),
    }


def migrate_backlog(dry_run: bool = False) -> dict:
    """Run migration from backlog.md to work files.

    Args:
        dry_run: If True, only count items without creating files.

    Returns:
        Dict with migration results: migrated, skipped, errors, total_items.
    """
    backlog_path = PROJECT_ROOT / "docs" / "pm" / "backlog.md"
    content = backlog_path.read_text(encoding="utf-8-sig")

    # Find existing work files to avoid duplicates
    work_dirs = [
        PROJECT_ROOT / "docs" / "work" / "active",
        PROJECT_ROOT / "docs" / "work" / "blocked",
        PROJECT_ROOT / "docs" / "work" / "archive",
    ]
    existing_ids = set()
    for dir_path in work_dirs:
        if dir_path.exists():
            for f in dir_path.glob("WORK-*.md"):
                # Extract ID from filename (WORK-E2-123-title.md or WORK-E2-143.md)
                # ID is the first E2-XXX or INV-XXX pattern after WORK-
                stem = f.stem  # Remove .md
                match = re.search(r"WORK-((?:E2|INV|TD|V)-\d+)", stem)
                if match:
                    existing_ids.add(match.group(1))

    # Split into entries at ### [
    entries = re.split(r"(?=### \[\w+\])", content)

    results = {"migrated": [], "skipped": [], "errors": [], "total_items": 0}

    for entry_text in entries:
        entry_text = entry_text.strip()
        if not entry_text.startswith("### ["):
            continue

        # Skip complete/closed items
        if "status:** complete" in entry_text.lower():
            results["skipped"].append("complete item")
            continue

        entry = parse_backlog_entry(entry_text)
        if not entry.get("id"):
            continue

        # Skip items that already have work files
        if entry["id"] in existing_ids:
            results["skipped"].append(f"{entry['id']} (already exists)")
            continue

        results["total_items"] += 1
        work = map_to_work_schema(entry)

        if dry_run:
            results["migrated"].append(work["id"])
            continue

        try:
            # Use scaffold to create work file
            output_path = scaffold_template(
                "work_item",
                backlog_id=work["id"],
                title=work["title"],
            )
            results["migrated"].append(work["id"])
            print(f"  Created: {output_path}")
        except Exception as e:
            results["errors"].append(f"{work['id']}: {e}")
            print(f"  ERROR: {work['id']}: {e}")

    return results


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Migrate backlog.md entries to WORK-{id}.md files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview migration without creating files",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("E2-151: Backlog Migration Script")
    print("=" * 60)

    if args.dry_run:
        print("MODE: Dry run (no files will be created)")
    else:
        print("MODE: Full migration (files will be created)")

    print()
    results = migrate_backlog(dry_run=args.dry_run)

    print()
    print("-" * 60)
    print(f"Total items found: {results['total_items']}")
    print(f"Migrated: {len(results['migrated'])}")
    print(f"Skipped: {len(results['skipped'])}")
    print(f"Errors: {len(results['errors'])}")

    if results["errors"]:
        print("\nErrors:")
        for error in results["errors"]:
            print(f"  - {error}")

    if args.dry_run:
        print("\nItems to migrate:")
        for item_id in sorted(results["migrated"]):
            print(f"  - {item_id}")

    print()
    return 0 if not results["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
