# generated: 2026-03-07
# WORK-244: CHAPTER.md YAML Frontmatter Migration
"""
CHAPTER.md frontmatter parser and writer (WORK-244).

Provides read/write access to YAML frontmatter in CHAPTER.md files.
Backward-compatible: falls back to regex parsing if frontmatter absent.

Schema:
  id: CH-067
  name: File Format Migration
  arc: infrastructure
  epoch: E2.8
  status: Active
  work_items:
    - id: WORK-244
      title: "CHAPTER.md YAML Frontmatter Migration"
      status: Active
      type: implementation
  exit_criteria:
    - text: "criterion text"
      checked: false
  dependencies: []
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

import yaml


def parse_chapter_frontmatter(path: Path) -> Optional[dict]:
    """Parse YAML frontmatter from CHAPTER.md file.

    Returns the frontmatter dict if --- delimiters found, else None.
    None signals callers to fall back to regex parsing (backward compat).

    Args:
        path: Path to CHAPTER.md file.

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


def get_exit_criteria(path: Path) -> Optional[Dict]:
    """Return exit criteria from frontmatter or fall back to regex parsing.

    Frontmatter format (preferred):
      exit_criteria:
        - text: "criterion text"
          checked: true

    Fallback (legacy markdown):
      - [x] criterion text
      - [ ] criterion text

    Args:
        path: Path to CHAPTER.md file.

    Returns:
        {"all_checked": bool, "total": int, "checked": int, "unchecked_items": list[str]}
        or None if no exit criteria found by either method.
    """
    fm = parse_chapter_frontmatter(path)

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

    # Fallback: regex parse markdown body
    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")
    in_section = False
    criteria_list: List[tuple] = []
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


def get_chapter_status(path: Path) -> Optional[str]:
    """Return status field from frontmatter or fall back to bold-markdown parsing.

    Args:
        path: Path to CHAPTER.md file.

    Returns:
        Status string (e.g. "Active", "Complete"), or None if not found.
    """
    fm = parse_chapter_frontmatter(path)
    if fm is not None:
        return fm.get("status")

    # Fallback: regex parse **Status:** Value
    content = path.read_text(encoding="utf-8")
    pattern = r"\*\*Status:\*\*\s*(.+)"
    match = re.search(pattern, content)
    return match.group(1).strip() if match else None


def get_work_items(path: Path) -> List[dict]:
    """Return work_items list from frontmatter or fall back to table parsing.

    Frontmatter format (preferred):
      work_items:
        - id: WORK-244
          title: "..."
          status: Active
          type: implementation

    Fallback: parses | ID | Title | Status | Type | markdown table.

    Args:
        path: Path to CHAPTER.md file.

    Returns:
        List of dicts with keys: id, title, status, type.
        Empty list if no work items found.
    """
    fm = parse_chapter_frontmatter(path)
    if fm is not None:
        return fm.get("work_items", []) or []

    # Fallback: parse markdown table in ## Work Items section
    content = path.read_text(encoding="utf-8")
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
            # Skip header and separator rows
            if len(cells) == 4 and not cells[0].startswith("-"):
                id_, title, status, type_ = cells
                if id_ != "ID":  # skip header row
                    items.append({"id": id_, "title": title, "status": status, "type": type_})
    return items


def update_work_item_in_frontmatter(
    path: Path,
    work_id: str,
    new_status: str,
) -> bool:
    """Update a work item's status in CHAPTER.md frontmatter.

    Does NOT fall back -- only operates on files with frontmatter.
    Callers must handle False return for legacy files.

    Args:
        path: Path to CHAPTER.md file.
        work_id: Work item ID to update (e.g. "WORK-244").
        new_status: New status string (e.g. "Complete").

    Returns:
        True if updated, False if frontmatter absent or work_id not found.
    """
    fm = parse_chapter_frontmatter(path)
    if fm is None:
        return False

    work_items = fm.get("work_items", []) or []
    updated = False
    for item in work_items:
        if item.get("id") == work_id:
            item["status"] = new_status
            updated = True
            break
    if not updated:
        return False

    _write_frontmatter(path, fm)
    return True


def add_work_item_to_frontmatter(
    path: Path,
    work_id: str,
    title: str,
    status: str = "Backlog",
    work_type: str = "implementation",
) -> bool:
    """Append a work item to the frontmatter work_items list.

    Does NOT fall back -- only operates on files with frontmatter.

    Args:
        path: Path to CHAPTER.md file.
        work_id: New work item ID.
        title: Work item title.
        status: Initial status (default: "Backlog").
        work_type: Work type (default: "implementation").

    Returns:
        True if added, False if frontmatter absent or work_id already present.
    """
    fm = parse_chapter_frontmatter(path)
    if fm is None:
        return False

    work_items = fm.get("work_items", []) or []
    if any(item.get("id") == work_id for item in work_items):
        return False  # already present

    work_items.append({"id": work_id, "title": title, "status": status, "type": work_type})
    fm["work_items"] = work_items
    _write_frontmatter(path, fm)
    return True


def _write_frontmatter(path: Path, fm: dict) -> None:
    """Rewrite CHAPTER.md with updated frontmatter, preserving markdown body.

    Args:
        path: Path to CHAPTER.md file.
        fm: Updated frontmatter dict.
    """
    content = path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Cannot write frontmatter to {path}: no --- delimiters found")

    new_yaml = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
    new_content = f"---\n{new_yaml}---{parts[2]}"
    path.write_text(new_content, encoding="utf-8")
