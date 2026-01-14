# generated: 2025-12-27
# System Auto: last updated on: 2025-12-27T21:52:45
#!/usr/bin/env python3
"""Work directory structure migration script (E2-212).

Migrates work files from flat structure to directory structure:
- WORK-E2-123-title.md -> E2-123/WORK.md

Also moves associated plans into work directories:
- docs/plans/PLAN-E2-123-*.md -> docs/work/active/E2-123/plans/PLAN.md

Usage:
    python scripts/migrate_work_dirs.py --dry-run  # Preview changes
    python scripts/migrate_work_dirs.py            # Execute migration
"""

import argparse
import glob
import re
import shutil
from pathlib import Path


def extract_backlog_id(filename: str) -> str | None:
    """Extract backlog ID from work filename.

    Args:
        filename: Work filename like 'WORK-E2-123-title.md'

    Returns:
        Backlog ID like 'E2-123' or None if not parseable.
    """
    match = re.match(r'WORK-((?:E2|INV|TD|V)-\d+)', filename)
    return match.group(1) if match else None


def migrate_work_file(work_path: Path, dry_run: bool = True) -> dict:
    """Migrate a single work file to directory structure.

    Args:
        work_path: Path to work file (e.g., docs/work/active/WORK-E2-123-title.md)
        dry_run: If True, only preview changes without executing

    Returns:
        Dict with migration details.
    """
    backlog_id = extract_backlog_id(work_path.name)
    if not backlog_id:
        return {"status": "skipped", "reason": "Could not extract ID", "path": str(work_path)}

    # Target directory structure
    target_dir = work_path.parent / backlog_id
    target_file = target_dir / "WORK.md"

    # Check if already migrated
    if target_file.exists():
        return {"status": "skipped", "reason": "Already migrated", "path": str(work_path)}

    result = {
        "status": "migrated" if not dry_run else "would_migrate",
        "source": str(work_path),
        "target": str(target_file),
        "backlog_id": backlog_id,
        "subdirs_created": [],
        "plans_moved": [],
    }

    if not dry_run:
        # Create directory structure
        target_dir.mkdir(parents=True, exist_ok=True)
        for subdir in ["plans", "investigations", "reports"]:
            (target_dir / subdir).mkdir(exist_ok=True)
            result["subdirs_created"].append(subdir)

        # Move work file
        shutil.move(str(work_path), str(target_file))
    else:
        result["subdirs_created"] = ["plans", "investigations", "reports"]

    # Find and move associated plans
    plans_dir = work_path.parent.parent.parent / "plans"
    plan_files = list(plans_dir.glob(f"PLAN-{backlog_id}*.md"))
    for i, plan_path in enumerate(sorted(plan_files)):
        if len(plan_files) == 1:
            # Single plan -> PLAN.md
            plan_target = target_dir / "plans" / "PLAN.md"
        else:
            # Multiple plans -> keep original filename
            plan_target = target_dir / "plans" / plan_path.name
        if not dry_run:
            shutil.move(str(plan_path), str(plan_target))
        result["plans_moved"].append({
            "source": str(plan_path),
            "target": str(plan_target)
        })

    return result


def migrate_all_active(dry_run: bool = True) -> list[dict]:
    """Migrate all active work files to directory structure.

    Args:
        dry_run: If True, only preview changes without executing

    Returns:
        List of migration results.
    """
    results = []
    active_dir = Path("docs/work/active")

    if not active_dir.exists():
        print("No docs/work/active/ directory found")
        return results

    # Find all flat work files
    work_files = list(active_dir.glob("WORK-*.md"))

    print(f"{'DRY RUN: ' if dry_run else ''}Found {len(work_files)} flat work files to migrate")
    print("-" * 60)

    for work_path in sorted(work_files):
        result = migrate_work_file(work_path, dry_run=dry_run)
        results.append(result)

        status = result["status"]
        if status == "skipped":
            print(f"SKIP: {work_path.name} - {result['reason']}")
        else:
            print(f"{'WOULD ' if dry_run else ''}MIGRATE: {result['backlog_id']}")
            print(f"  {result['source']}")
            print(f"  -> {result['target']}")
            if result["plans_moved"]:
                for plan in result["plans_moved"]:
                    print(f"  PLAN: {plan['source']} -> {plan['target']}")

    print("-" * 60)
    migrated = sum(1 for r in results if "migrate" in r["status"])
    skipped = sum(1 for r in results if r["status"] == "skipped")
    print(f"Summary: {migrated} {'would be ' if dry_run else ''}migrated, {skipped} skipped")

    return results


def main():
    parser = argparse.ArgumentParser(description="Migrate work files to directory structure")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    args = parser.parse_args()

    migrate_all_active(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
