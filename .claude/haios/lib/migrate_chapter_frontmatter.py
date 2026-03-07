# generated: 2026-03-07
# WORK-244: CHAPTER.md YAML Frontmatter Migration
"""
Migration script: convert CHAPTER.md files from bold-markdown to YAML frontmatter.

Usage (standalone):
    python .claude/haios/lib/migrate_chapter_frontmatter.py
    python .claude/haios/lib/migrate_chapter_frontmatter.py --dry-run

Idempotent: files that already have frontmatter are skipped.

Parses these bold-markdown fields:
  **Chapter ID:** CH-067
  **Arc:** infrastructure
  **Epoch:** E2.8
  **Name:** File Format Migration
  **Status:** Active

Parses Work Items table (| ID | Title | Status | Type |).
Parses Exit Criteria checkboxes (- [x] / - [ ]).
Parses Dependencies table (| Direction | Target | Reason |).
"""

import re
import sys
from pathlib import Path
from typing import List, Optional

import yaml


# Project root is 4 levels up from .claude/haios/lib/
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# All CHAPTER.md files to migrate (relative to PROJECT_ROOT)
CHAPTER_FILES = [
    ".claude/haios/epochs/E2_8/arcs/call/chapters/CH-058-ProportionalGovernanceDesign/CHAPTER.md",
    ".claude/haios/epochs/E2_8/arcs/call/chapters/CH-059-CeremonyAutomation/CHAPTER.md",
    ".claude/haios/epochs/E2_8/arcs/call/chapters/CH-060-SessionBoundaryFix/CHAPTER.md",
    ".claude/haios/epochs/E2_8/arcs/call/chapters/CH-061-ColdstartContextInjection/CHAPTER.md",
    ".claude/haios/epochs/E2_8/arcs/call/chapters/CH-066-MCPOperationsServer/CHAPTER.md",
    ".claude/haios/epochs/E2_8/arcs/infrastructure/chapters/CH-065-BugBatch-E28/CHAPTER.md",
    ".claude/haios/epochs/E2_8/arcs/infrastructure/chapters/CH-067-FileFormatMigration/CHAPTER.md",
    ".claude/haios/epochs/E2_8/arcs/query/chapters/CH-062-ProgressiveContracts/CHAPTER.md",
    ".claude/haios/epochs/E2_8/arcs/discover/chapters/CH-063-AgentCards/CHAPTER.md",
    ".claude/haios/epochs/E2_8/arcs/discover/chapters/CH-064-InfrastructureCeremonies/CHAPTER.md",
]


def _parse_bold_field(content: str, field_name: str) -> Optional[str]:
    """Extract value from **Field:** Value pattern."""
    pattern = rf"\*\*{re.escape(field_name)}:\*\*\s*(.+)"
    match = re.search(pattern, content)
    return match.group(1).strip() if match else None


def _parse_work_items_table(content: str) -> List[dict]:
    """Parse | ID | Title | Status | Type | table from ## Work Items section."""
    lines = content.split("\n")
    in_section = False
    items = []
    for line in lines:
        if re.match(r"^##\s+Work Items", line):
            in_section = True
            continue
        if in_section and re.match(r"^##\s+", line):
            break
        if in_section and line.strip().startswith("|"):
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) == 4 and not cells[0].startswith("-") and cells[0] != "ID":
                id_, title, status, type_ = cells
                # Handle strikethrough IDs (e.g., ~~WORK-218~~)
                id_ = id_.strip("~")
                items.append({"id": id_, "title": title, "status": status, "type": type_})
    return items


def _parse_exit_criteria(content: str) -> List[dict]:
    """Parse - [x] / - [ ] checkboxes from ## Exit Criteria section."""
    lines = content.split("\n")
    in_section = False
    criteria = []
    for line in lines:
        if re.match(r"^##\s+Exit Criteria", line):
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


def _parse_dependencies_table(content: str) -> List[dict]:
    """Parse | Direction | Target | Reason | table from ## Dependencies section.

    Returns empty list if no dependencies row (only None/- rows present).
    """
    lines = content.split("\n")
    in_section = False
    deps = []
    for line in lines:
        if re.match(r"^##\s+Dependencies", line):
            in_section = True
            continue
        if in_section and re.match(r"^##\s+", line):
            break
        if in_section and line.strip().startswith("|"):
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) >= 3 and not cells[0].startswith("-"):
                direction, target, reason = cells[0], cells[1], cells[2]
                # Skip header and "None" placeholder rows
                if direction not in ("Direction", "None") and target != "-":
                    deps.append({"direction": direction, "target": target, "reason": reason})
    return deps


def build_frontmatter(content: str) -> dict:
    """Parse bold-markdown CHAPTER.md content into frontmatter dict.

    Args:
        content: Full text of CHAPTER.md file.

    Returns:
        Dict suitable for YAML frontmatter serialization.
    """
    fm = {
        "id": _parse_bold_field(content, "Chapter ID"),
        "name": _parse_bold_field(content, "Name"),
        "arc": _parse_bold_field(content, "Arc"),
        "epoch": _parse_bold_field(content, "Epoch"),
        "status": _parse_bold_field(content, "Status"),
        "work_items": _parse_work_items_table(content),
        "exit_criteria": _parse_exit_criteria(content),
        "dependencies": _parse_dependencies_table(content),
    }
    return fm


def _has_frontmatter(content: str) -> bool:
    """Return True if file already has YAML frontmatter (--- delimiter)."""
    stripped = "\n".join(
        line for line in content.split("\n") if not line.startswith("# ")
    )
    return stripped.lstrip().startswith("---")


def migrate_file(path: Path, dry_run: bool = False) -> dict:
    """Inject YAML frontmatter into a single CHAPTER.md file.

    Idempotent: returns {"skipped": True} if frontmatter already present.
    Preserves the full markdown body after the --- markers.

    Args:
        path: Path to CHAPTER.md file.
        dry_run: If True, return result without writing.

    Returns:
        {"migrated": bool, "skipped": bool, "path": str, "frontmatter": dict}
    """
    if not path.exists():
        return {"migrated": False, "skipped": False, "path": str(path), "error": "not_found"}

    content = path.read_text(encoding="utf-8")

    if _has_frontmatter(content):
        return {"migrated": False, "skipped": True, "path": str(path)}

    fm = build_frontmatter(content)
    yaml_block = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
    new_content = f"---\n{yaml_block}---\n{content}"

    if not dry_run:
        path.write_text(new_content, encoding="utf-8")

    return {"migrated": True, "skipped": False, "path": str(path), "frontmatter": fm}


def migrate_all(base_path: Optional[Path] = None, dry_run: bool = False) -> List[dict]:
    """Migrate all CHAPTER.md files listed in CHAPTER_FILES.

    Args:
        base_path: Project root override (for testing).
        dry_run: If True, do not write files.

    Returns:
        List of result dicts from migrate_file().
    """
    root = base_path or PROJECT_ROOT
    results = []
    for rel_path in CHAPTER_FILES:
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
