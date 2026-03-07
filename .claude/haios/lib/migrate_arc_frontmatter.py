# generated: 2026-03-07
# WORK-245: ARC.md YAML Frontmatter Migration
"""
Migration script: convert ARC.md files from bold-markdown to YAML frontmatter.

Usage (standalone):
    python .claude/haios/lib/migrate_arc_frontmatter.py
    python .claude/haios/lib/migrate_arc_frontmatter.py --dry-run

Idempotent: files that already have frontmatter are skipped.

Parses these bold-markdown fields:
  **Arc ID:** infrastructure
  **Epoch:** E2.8
  **Theme:** Fix what's broken
  **Status:** Planning
  **Started:** 2026-02-17 (Session 393)

Parses Chapters table (| CH-ID | Title | Work Items | Requirements | Dependencies | Status |).
Parses Exit Criteria checkboxes (- [x] / - [ ]).
"""

import re
import sys
from pathlib import Path
from typing import List, Optional

import yaml


# Project root is 4 levels up from .claude/haios/lib/
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# All ARC.md files to migrate (relative to PROJECT_ROOT)
ARC_FILES = [
    ".claude/haios/epochs/E2/arcs/breath/ARC.md",
    ".claude/haios/epochs/E2/arcs/chariot/ARC.md",
    ".claude/haios/epochs/E2/arcs/form/ARC.md",
    ".claude/haios/epochs/E2/arcs/ground/ARC.md",
    ".claude/haios/epochs/E2/arcs/tongue/ARC.md",
    ".claude/haios/epochs/E2/arcs/workinfra/ARC.md",
    ".claude/haios/epochs/E2_3/arcs/configuration/ARC.md",
    ".claude/haios/epochs/E2_3/arcs/migration/ARC.md",
    ".claude/haios/epochs/E2_3/arcs/observations/ARC.md",
    ".claude/haios/epochs/E2_3/arcs/pipeline/ARC.md",
    ".claude/haios/epochs/E2_3/arcs/provenance/ARC.md",
    ".claude/haios/epochs/E2_3/arcs/workuniversal/ARC.md",
    ".claude/haios/epochs/E2_4/arcs/activities/ARC.md",
    ".claude/haios/epochs/E2_4/arcs/configuration/ARC.md",
    ".claude/haios/epochs/E2_4/arcs/flow/ARC.md",
    ".claude/haios/epochs/E2_4/arcs/templates/ARC.md",
    ".claude/haios/epochs/E2_4/arcs/workuniversal/ARC.md",
    ".claude/haios/epochs/E2_5/arcs/assets/ARC.md",
    ".claude/haios/epochs/E2_5/arcs/ceremonies/ARC.md",
    ".claude/haios/epochs/E2_5/arcs/feedback/ARC.md",
    ".claude/haios/epochs/E2_5/arcs/lifecycles/ARC.md",
    ".claude/haios/epochs/E2_5/arcs/portability/ARC.md",
    ".claude/haios/epochs/E2_5/arcs/queue/ARC.md",
    ".claude/haios/epochs/E2_6/arcs/discoverability/ARC.md",
    ".claude/haios/epochs/E2_6/arcs/observability/ARC.md",
    ".claude/haios/epochs/E2_6/arcs/referenceability/ARC.md",
    ".claude/haios/epochs/E2_6/arcs/traceability/ARC.md",
    ".claude/haios/epochs/E2_7/arcs/composability/ARC.md",
    ".claude/haios/epochs/E2_7/arcs/engine-functions/ARC.md",
    ".claude/haios/epochs/E2_7/arcs/infrastructure/ARC.md",
    ".claude/haios/epochs/E2_8/arcs/call/ARC.md",
    ".claude/haios/epochs/E2_8/arcs/discover/ARC.md",
    ".claude/haios/epochs/E2_8/arcs/infrastructure/ARC.md",
    ".claude/haios/epochs/E2_8/arcs/query/ARC.md",
]


def _parse_bold_field(content: str, field_name: str) -> Optional[str]:
    """Extract value from **Field:** Value pattern."""
    pattern = rf"\*\*{re.escape(field_name)}:\*\*\s*(.+)"
    match = re.search(pattern, content)
    return match.group(1).strip() if match else None


def _clean_status(raw: str) -> str:
    """Strip bold-markdown formatting and session annotations from status values.

    B2 critique fix: Real ARC.md files contain status like '**Complete** (S335)'.
    Without cleaning, is_arc_complete silently fails because '**complete** (s335)'
    is not in ARC_COMPLETE_STATUSES.

    Examples:
        '**Complete** (S335)' -> 'Complete'
        '**Active**' -> 'Active'
        'Planning' -> 'Planning'
    """
    cleaned = raw.replace("**", "").strip()
    cleaned = re.sub(r"\s*\(S\d+.*?\)\s*$", "", cleaned)
    return cleaned


def _parse_chapters_table(content: str) -> List[dict]:
    """Parse chapter table with variable column counts (4, 5, or 6 columns).

    Handles three table formats across epochs:
      4-col (E2-E2.4): | Chapter | Name | Status | Purpose |
      5-col (E2.5 var): | CH-ID | Title | Requirements | Dependencies | Status |
      6-col (E2.6+):    | CH-ID | Title | Work Items | Requirements | Dependencies | Status |

    A1/A7 critique fix: column-count branching instead of >= 6 guard.
    """
    chapters = []
    for line in content.split("\n"):
        if re.match(r"\s*\|\s*CH-\d+", line):
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) >= 6:
                # 6-column: CH-ID | Title | Work Items | Requirements | Dependencies | Status
                ch_id = cells[0]
                title = cells[1]
                work_str = cells[2]
                req_str = cells[3]
                dep_str = cells[4]
                status = _clean_status(cells[5])
                if work_str in ("", "None"):
                    work_items = []
                elif work_str == "New":
                    work_items = ["New"]
                else:
                    work_items = [w.strip() for w in work_str.split(",") if w.strip()]
                requirements = [r.strip() for r in req_str.split(",") if r.strip() and r.strip() != "None"]
                dependencies = [d.strip() for d in dep_str.split(",") if d.strip() and d.strip() != "None"]
                chapters.append({
                    "id": ch_id, "title": title, "work_items": work_items,
                    "requirements": requirements, "dependencies": dependencies, "status": status,
                })
            elif len(cells) == 5:
                # 5-column: CH-ID | Title | Requirements | Dependencies | Status
                ch_id = cells[0]
                title = cells[1]
                req_str = cells[2]
                dep_str = cells[3]
                status = _clean_status(cells[4])
                requirements = [r.strip() for r in req_str.split(",") if r.strip() and r.strip() != "None"]
                dependencies = [d.strip() for d in dep_str.split(",") if d.strip() and d.strip() != "None"]
                chapters.append({
                    "id": ch_id, "title": title, "work_items": [],
                    "requirements": requirements, "dependencies": dependencies, "status": status,
                })
            elif len(cells) == 4:
                # 4-column: Chapter | Name | Status | Purpose
                ch_id = cells[0]
                title = cells[1]
                status = _clean_status(cells[2])
                chapters.append({
                    "id": ch_id, "title": title, "work_items": [],
                    "requirements": [], "dependencies": [], "status": status,
                })
    return chapters


def _parse_exit_criteria(content: str) -> List[dict]:
    """Parse - [x] / - [ ] checkboxes from exit criteria section.

    A3 critique fix: handles multiple section heading variants:
      ## Exit Criteria (E2.5+)
      ## Arc Completion Criteria (E2)
      ## Chapter Completion Criteria (E2 variant)
      ## Completion Criteria (generic)
    """
    lines = content.split("\n")
    in_section = False
    criteria = []
    for line in lines:
        if re.match(r"^##\s+(Exit Criteria|Arc Completion Criteria|Chapter Completion Criteria|Completion Criteria)", line):
            in_section = True
            continue
        if in_section and re.match(r"^##\s+", line):
            break
        if in_section:
            m = re.match(r"^- \[([ x])\] (.+)$", line)
            if m:
                checked = m.group(1) == "x"
                criteria.append({"text": m.group(2).strip(), "checked": checked})
    return criteria


def build_arc_frontmatter(content: str) -> dict:
    """Parse bold-markdown ARC.md content into frontmatter dict.

    A2 critique fix: handles field name variants across epochs:
      - **Name:** (E2-E2.4, separate from Theme)
      - **Theme:** (E2.5+, replaces Name for purpose description)
      - **Pressure:** (E2-E2.4 only, preserved but optional)
      - **Started:** (E2.7+ only)
      - **Completed:** (when status=Complete, E2.5+)

    Args:
        content: Full text of ARC.md file.

    Returns:
        Dict suitable for YAML frontmatter serialization.
    """
    fm = {
        "id": _parse_bold_field(content, "Arc ID"),
        "name": _parse_bold_field(content, "Name"),
        "epoch": _parse_bold_field(content, "Epoch"),
        "theme": _parse_bold_field(content, "Theme"),
        "status": _parse_bold_field(content, "Status"),
        "started": _parse_bold_field(content, "Started"),
        "completed": _parse_bold_field(content, "Completed"),
        "chapters": _parse_chapters_table(content),
        "exit_criteria": _parse_exit_criteria(content),
    }
    # Remove None fields to keep frontmatter clean
    return {k: v for k, v in fm.items() if v is not None}


def _has_frontmatter(content: str) -> bool:
    """Return True if file already has YAML frontmatter (--- delimiter)."""
    stripped = "\n".join(
        line for line in content.split("\n") if not line.startswith("# ")
    )
    return stripped.lstrip().startswith("---")


def migrate_file(path: Path, dry_run: bool = False) -> dict:
    """Inject YAML frontmatter into a single ARC.md file.

    Idempotent: returns {"skipped": True} if frontmatter already present.
    Preserves the full markdown body after the --- markers.

    Args:
        path: Path to ARC.md file.
        dry_run: If True, return result without writing.

    Returns:
        {"migrated": bool, "skipped": bool, "path": str, "frontmatter": dict}
    """
    if not path.exists():
        return {"migrated": False, "skipped": False, "path": str(path), "error": "not_found"}

    content = path.read_text(encoding="utf-8")

    if _has_frontmatter(content):
        return {"migrated": False, "skipped": True, "path": str(path)}

    fm = build_arc_frontmatter(content)
    yaml_block = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
    new_content = f"---\n{yaml_block}---\n{content}"

    if not dry_run:
        path.write_text(new_content, encoding="utf-8")

    return {"migrated": True, "skipped": False, "path": str(path), "frontmatter": fm}


def migrate_all(base_path: Optional[Path] = None, dry_run: bool = False) -> List[dict]:
    """Migrate all ARC.md files listed in ARC_FILES.

    Args:
        base_path: Project root override (for testing).
        dry_run: If True, do not write files.

    Returns:
        List of result dicts from migrate_file().
    """
    root = base_path or PROJECT_ROOT
    results = []
    for rel_path in ARC_FILES:
        path = root / rel_path
        result = migrate_file(path, dry_run=dry_run)
        results.append(result)
    return results


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    results = migrate_all(dry_run=dry_run)
    migrated = sum(1 for r in results if r.get("migrated"))
    skipped = sum(1 for r in results if r.get("skipped"))
    errors = sum(1 for r in results if r.get("error"))
    print(f"Migration complete: {migrated} migrated, {skipped} skipped, {errors} errors")
    for r in results:
        status = "MIGRATED" if r.get("migrated") else ("SKIPPED" if r.get("skipped") else "ERROR")
        print(f"  [{status}] {r['path']}")
