# generated: 2026-03-07
# WORK-245: ARC.md YAML Frontmatter Migration
"""
ARC.md frontmatter parser and writer (WORK-245).

Provides read/write access to YAML frontmatter in ARC.md files.
Backward-compatible: falls back to regex/table parsing if frontmatter absent.

Schema:
  id: infrastructure
  epoch: "E2.8"
  theme: "Fix what's broken"
  status: Planning
  started: "2026-02-17 (Session 393)"
  chapters:
    - id: CH-065
      title: BugBatch-E28
      work_items: ["New"]
      requirements: ["REQ-CEREMONY-001"]
      dependencies: []
      status: Complete
    - id: CH-067
      title: FileFormatMigration
      work_items: ["WORK-244", "WORK-245"]
      requirements: ["REQ-TRACE-004"]
      dependencies: []
      status: Active
  exit_criteria:
    - text: "All confirmed bugs from E2.7 triage resolved"
      checked: true
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

import yaml


def parse_arc_frontmatter(path: Path) -> Optional[dict]:
    """Parse YAML frontmatter from ARC.md file.

    Returns the frontmatter dict if --- delimiters found, else None.
    None signals callers to fall back to regex parsing (backward compat).

    Args:
        path: Path to ARC.md file.

    Returns:
        dict of frontmatter fields, or None if no frontmatter present.
    """
    content = path.read_text(encoding="utf-8")
    # Strip comment lines (# generated: ...) before checking for ---
    stripped = "\n".join(
        line for line in content.split("\n") if not line.startswith("# ")
    )
    if not stripped.lstrip().startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return None


def get_arc_status(path: Path) -> Optional[str]:
    """Return status field from frontmatter or fall back to bold-markdown parsing.

    Args:
        path: Path to ARC.md file.

    Returns:
        Status string (e.g. "Planning", "Active", "Complete"), or None if not found.
    """
    fm = parse_arc_frontmatter(path)
    if fm is not None:
        return fm.get("status")

    # Fallback: regex parse **Status:** Value
    content = path.read_text(encoding="utf-8")
    pattern = r"\*\*Status:\*\*\s*(.+)"
    match = re.search(pattern, content)
    return match.group(1).strip() if match else None


def get_arc_metadata(path: Path) -> Dict[str, str]:
    """Return theme and status from frontmatter or fall back to bold-markdown.

    Returns dict with 'theme' and 'status' keys (same interface as
    hierarchy_engine._parse_arc_metadata).

    Args:
        path: Path to ARC.md file.

    Returns:
        {"theme": str, "status": str} — empty strings if not found.
    """
    fm = parse_arc_frontmatter(path)
    if fm is not None:
        return {
            "theme": fm.get("theme", "") or "",
            "status": fm.get("status", "") or "",
        }

    # Fallback: bold-markdown parsing
    content = path.read_text(encoding="utf-8")
    theme = ""
    status = ""
    for line in content.split("\n"):
        if line.startswith("**Theme:**"):
            theme = line.split("**Theme:**", 1)[1].strip()
        elif line.startswith("**Status:**"):
            status = line.split("**Status:**", 1)[1].strip()
    return {"theme": theme, "status": status}


def get_chapters(path: Path) -> List[dict]:
    """Return chapters list from frontmatter or fall back to table parsing.

    Frontmatter format (preferred):
      chapters:
        - id: CH-065
          title: BugBatch-E28
          work_items: ["New"]
          requirements: ["REQ-CEREMONY-001"]
          dependencies: []
          status: Complete

    Fallback: parses | CH-ID | Title | Work Items | Requirements | Dependencies | Status |
    markdown table (>= 6 columns).

    Args:
        path: Path to ARC.md file.

    Returns:
        List of dicts with keys: id, title, work_items, requirements, dependencies, status.
        Empty list if no chapters found.
    """
    fm = parse_arc_frontmatter(path)
    if fm is not None:
        return fm.get("chapters", []) or []

    # Fallback: parse markdown table in ## Chapters section
    # B1 critique fix: handle 4, 5, and 6 column table variants (same as migration script)
    content = path.read_text(encoding="utf-8")
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
                status = cells[5]
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
                status = cells[4]
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
                status = cells[2]
                chapters.append({
                    "id": ch_id, "title": title, "work_items": [],
                    "requirements": [], "dependencies": [], "status": status,
                })
    return chapters


def get_exit_criteria(path: Path) -> Optional[Dict]:
    """Return exit criteria from frontmatter or fall back to checkbox parsing.

    Frontmatter format (preferred):
      exit_criteria:
        - text: "criterion text"
          checked: true

    Fallback (legacy markdown):
      - [x] criterion text
      - [ ] criterion text

    Args:
        path: Path to ARC.md file.

    Returns:
        {"all_checked": bool, "total": int, "checked": int, "unchecked_items": list[str]}
        or None if no exit criteria found by either method.
    """
    fm = parse_arc_frontmatter(path)

    if fm is not None:
        # Frontmatter path
        criteria = fm.get("exit_criteria", [])
        if not criteria:
            return None
        total = len(criteria)
        checked_count = sum(1 for c in criteria if c.get("checked", False))
        unchecked_items = [
            c.get("text", "") for c in criteria if not c.get("checked", False)
        ]
        return {
            "all_checked": checked_count == total,
            "total": total,
            "checked": checked_count,
            "unchecked_items": unchecked_items,
        }

    # Fallback: regex parse checkbox lines
    # A3 critique fix: handle multiple section heading variants
    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")
    in_section = False
    criteria_list: List[tuple] = []
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
                criteria_list.append((checked, m.group(2).strip()))
    if not criteria_list:
        return None
    checked_count = sum(1 for c, _ in criteria_list if c)
    unchecked_items = [desc for c, desc in criteria_list if not c]
    return {
        "all_checked": checked_count == len(criteria_list),
        "total": len(criteria_list),
        "checked": checked_count,
        "unchecked_items": unchecked_items,
    }


def update_chapter_in_frontmatter(
    path: Path,
    chapter_id: str,
    new_status: str,
) -> bool:
    """Update a chapter's status in ARC.md frontmatter.

    Does NOT fall back -- only operates on files with frontmatter.
    Callers must handle False return for legacy files.

    Args:
        path: Path to ARC.md file.
        chapter_id: Chapter ID to update (e.g. "CH-067").
        new_status: New status string (e.g. "Complete").

    Returns:
        True if updated, False if frontmatter absent or chapter_id not found.
    """
    fm = parse_arc_frontmatter(path)
    if fm is None:
        return False

    chapters = fm.get("chapters", []) or []
    updated = False
    for ch in chapters:
        if ch.get("id") == chapter_id:
            ch["status"] = new_status
            updated = True
            break
    if not updated:
        return False

    _write_frontmatter(path, fm)
    return True


def _write_frontmatter(path: Path, fm: dict) -> None:
    """Rewrite ARC.md with updated frontmatter, preserving markdown body.

    Args:
        path: Path to ARC.md file.
        fm: Updated frontmatter dict.
    """
    content = path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Cannot write frontmatter to {path}: no --- delimiters found")

    new_yaml = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
    new_content = f"---\n{new_yaml}---{parts[2]}"
    path.write_text(new_content, encoding="utf-8")
