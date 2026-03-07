---
template: implementation_plan
plan_version: "2.0"
status: approved
date: 2026-03-07
backlog_id: WORK-244
title: "CHAPTER.md YAML Frontmatter Migration"
author: Hephaestus
lifecycle_phase: plan
session: 467
generated: 2026-03-07
last_updated: 2026-03-07T02:00:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-244/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete code blocks, not pseudocode"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: CHAPTER.md YAML Frontmatter Migration

---

## Goal

Add YAML frontmatter to all 10 existing CHAPTER.md files and migrate the 3 consumer modules (status_propagator, dod_validation, scaffold) to read structured frontmatter instead of regex-parsing bold-markdown, while preserving backward-compatible fallback for any file missing frontmatter.

---

## Open Decisions

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| No unresolved operator decisions | — | — | operator_decisions field empty in WORK.md |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/lib/chapter_frontmatter.py` | CREATE | 2 |
| `.claude/haios/lib/migrate_chapter_frontmatter.py` | CREATE | 2 |
| `.claude/haios/lib/status_propagator.py` | MODIFY | 2 |
| `.claude/haios/lib/dod_validation.py` | MODIFY | 2 |
| `.claude/haios/lib/scaffold.py` | MODIFY | 2 |

### Consumer Files

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `tests/test_chapter_manifest_update.py` | imports scaffold; calls update_chapter_manifest / update_chapter_manifest_status | 70, 147, 174, 184, 215, 244, 263, 286 | UPDATE — add frontmatter-format CHAPTER.md fixture helper |
| `tests/test_dod_validation.py` | imports dod_validation; calls validate_chapter_dod | 100, 109, 119, 127 | UPDATE — existing markdown-format tests remain; add frontmatter-format tests |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_chapter_frontmatter.py` | CREATE | Primary tests for chapter_frontmatter.py parser and migration script |
| `tests/test_dod_validation.py` | UPDATE | Add `TestValidateChapterDodFrontmatter` class for frontmatter-format tests |
| `tests/test_chapter_manifest_update.py` | UPDATE | Add frontmatter-format test class `TestUpdateChapterManifestFrontmatter` |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 3 | `chapter_frontmatter.py`, `migrate_chapter_frontmatter.py`, `tests/test_chapter_frontmatter.py` |
| Files to modify | 5 | `status_propagator.py`, `dod_validation.py`, `scaffold.py`, `test_dod_validation.py`, `test_chapter_manifest_update.py` |
| CHAPTER.md files to migrate | 10 | All listed in WORK.md |
| Total blast radius | 18 | 3 new + 5 modified + 10 CHAPTER.md files |

---

## Layer 1: Specification

### Current State

**status_propagator.py — `_check_exit_criteria()` (lines 190-240):**
```python
# .claude/haios/lib/status_propagator.py:210-240
content = chapter_file.read_text(encoding="utf-8")
lines = content.split("\n")
in_section = False
criteria: List[tuple] = []

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
            criteria.append((checked, m.group(2).strip()))
```

**dod_validation.py — `_parse_markdown_field()` (lines 68-76) and `_count_exit_criteria()` (lines 79-93):**
```python
# .claude/haios/lib/dod_validation.py:68-76
def _parse_markdown_field(content: str, field_name: str) -> Optional[str]:
    pattern = rf"\*\*{re.escape(field_name)}:\*\*\s*(.+)"
    match = re.search(pattern, content)
    return match.group(1).strip() if match else None

# .claude/haios/lib/dod_validation.py:79-93
def _count_exit_criteria(content: str) -> Tuple[int, int]:
    ec_match = re.search(r"## Exit Criteria\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if not ec_match:
        return 0, 0
    ec_section = ec_match.group(1)
    total = len(re.findall(r"- \[[ x]\]", ec_section))
    checked = len(re.findall(r"- \[x\]", ec_section))
    return checked, total
```

**scaffold.py — `update_chapter_manifest()` (lines 647-714):**
```python
# .claude/haios/lib/scaffold.py:695-714
lines = content.split("\n")
insert_idx = None
in_work_items = False
for i, line in enumerate(lines):
    if line.strip().startswith("## Work Items"):
        in_work_items = True
        continue
    if in_work_items:
        if line.strip().startswith("|"):
            insert_idx = i
        elif line.strip() == "---" or line.strip().startswith("##"):
            break
if insert_idx is None:
    return {"updated": False, "reason": "table_not_found", ...}
lines.insert(insert_idx + 1, new_row)
chapter_file.write_text("\n".join(lines), encoding="utf-8")
```

**Behavior:** All three consumers independently regex-parse the markdown body of CHAPTER.md. Each implements its own parser for the same fields, with no shared utility.

**Problem:** Fragile — any whitespace or formatting change in CHAPTER.md breaks 3 independent parsers. No single source of truth for field names. Work items table manipulation via line insertion is accident-prone.

---

### Desired State

**New module: `.claude/haios/lib/chapter_frontmatter.py`**

```python
# .claude/haios/lib/chapter_frontmatter.py — complete implementation

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
from typing import Dict, List, Optional, Tuple

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
    criteria: List[tuple] = []
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
                criteria.append((checked, m.group(2).strip()))
    if not criteria:
        return None
    checked_count = sum(1 for c, _ in criteria if c)
    unchecked_items = [desc for c, desc in criteria if not c]
    return {
        "all_checked": checked_count == len(criteria),
        "total": len(criteria),
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

    Does NOT fall back — only operates on files with frontmatter.
    Callers must call has_frontmatter() first or handle False return.

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

    Does NOT fall back — only operates on files with frontmatter.

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
```

**New module: `.claude/haios/lib/migrate_chapter_frontmatter.py`**

```python
# .claude/haios/lib/migrate_chapter_frontmatter.py — complete implementation

"""
Migration script: convert CHAPTER.md files from bold-markdown to YAML frontmatter.

Usage (standalone):
    python .claude/haios/lib/migrate_chapter_frontmatter.py

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
from typing import Dict, List, Optional, Tuple

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
```

**Modified: `.claude/haios/lib/status_propagator.py` — `_check_exit_criteria()`**

Location: Lines 190-240 in `_check_exit_criteria()`

**Current Code:**
```python
# status_propagator.py:206-240
chapter_file = self._find_chapter_file(chapter_id, arc_name)
if chapter_file is None:
    return None

content = chapter_file.read_text(encoding="utf-8")

# Find ## Exit Criteria section
lines = content.split("\n")
in_section = False
criteria: List[tuple] = []

for line in lines:
    if re.match(r"^##\s+Exit Criteria", line):
        in_section = True
        continue
    if in_section and re.match(r"^##\s+", line):
        break  # Next section starts
    if in_section:
        m = re.match(r"^- \[([ x])\] (.+)$", line)
        if m:
            checked = m.group(1) == "x"
            criteria.append((checked, m.group(2).strip()))

if not criteria:
    return None  # No exit criteria found

checked_count = sum(1 for c, _ in criteria if c)
unchecked_items = [desc for c, desc in criteria if not c]

return {
    "all_checked": checked_count == len(criteria),
    "total": len(criteria),
    "checked": checked_count,
    "unchecked_items": unchecked_items,
}
```

**Target Code:**
```python
# status_propagator.py:206-215 (replacement — delegates to chapter_frontmatter)
chapter_file = self._find_chapter_file(chapter_id, arc_name)
if chapter_file is None:
    return None

from chapter_frontmatter import get_exit_criteria
return get_exit_criteria(chapter_file)
```

**Diff:**
```diff
-        content = chapter_file.read_text(encoding="utf-8")
-
-        # Find ## Exit Criteria section
-        lines = content.split("\n")
-        in_section = False
-        criteria: List[tuple] = []
-
-        for line in lines:
-            if re.match(r"^##\s+Exit Criteria", line):
-                in_section = True
-                continue
-            if in_section and re.match(r"^##\s+", line):
-                break  # Next section starts
-            if in_section:
-                m = re.match(r"^- \[([ x])\] (.+)$", line)
-                if m:
-                    checked = m.group(1) == "x"
-                    criteria.append((checked, m.group(2).strip()))
-
-        if not criteria:
-            return None  # No exit criteria found
-
-        checked_count = sum(1 for c, _ in criteria if c)
-        unchecked_items = [desc for c, desc in criteria if not c]
-
-        return {
-            "all_checked": checked_count == len(criteria),
-            "total": len(criteria),
-            "checked": checked_count,
-            "unchecked_items": unchecked_items,
-        }
+        from chapter_frontmatter import get_exit_criteria
+        return get_exit_criteria(chapter_file)
```

**Modified: `.claude/haios/lib/dod_validation.py` — `validate_chapter_dod()`**

Location: Lines 266-283 in `validate_chapter_dod()`

**Current Code:**
```python
# dod_validation.py:266-283
# Check 2: Exit criteria all checked
checked, total = _count_exit_criteria(content)
if total > 0:
    ec_ok = checked == total
    checks.append(
        DoDCheck(
            "exit_criteria_checked",
            ec_ok,
            f"{checked}/{total} checked",
        )
    )
    if not ec_ok:
        failures.append(
            f"Exit criteria incomplete: {checked}/{total} checked"
        )
else:
    checks.append(
        DoDCheck("exit_criteria_checked", True, "No exit criteria found")
    )
```

**Target Code:**
```python
# dod_validation.py:266-290 (replacement — delegates to chapter_frontmatter)
# Check 2: Exit criteria all checked
# chapter_file is: arc_dir / f"{chapter_id}-*.md" match
# For validate_chapter_dod the chapter_file variable comes from the glob
# We detect if it's a CHAPTER.md directory-style or flat file
from chapter_frontmatter import get_exit_criteria as _get_chapter_exit_criteria

# chapter_file from glob may be a flat .md file (old style) or CHAPTER.md
# Try to find companion CHAPTER.md in parent directory if this is a flat file
_chapter_md_path = chapter_file if chapter_file.name == "CHAPTER.md" else None
if _chapter_md_path is None:
    # Try: same dir, look for CHAPTER.md
    candidate = chapter_file.parent / "CHAPTER.md"
    if candidate.exists():
        _chapter_md_path = candidate

if _chapter_md_path is not None:
    criteria = _get_chapter_exit_criteria(_chapter_md_path)
else:
    criteria = None

if criteria is None:
    # Fallback: count from markdown body of chapter_file itself
    checked, total = _count_exit_criteria(content)
    criteria = {"checked": checked, "total": total, "all_checked": checked == total} if total > 0 else None

if criteria is not None and criteria["total"] > 0:
    ec_ok = criteria["all_checked"]
    checks.append(
        DoDCheck(
            "exit_criteria_checked",
            ec_ok,
            f"{criteria['checked']}/{criteria['total']} checked",
        )
    )
    if not ec_ok:
        failures.append(
            f"Exit criteria incomplete: {criteria['checked']}/{criteria['total']} checked"
        )
else:
    checks.append(
        DoDCheck("exit_criteria_checked", True, "No exit criteria found")
    )
```

Note: `validate_arc_dod()` and `validate_epoch_dod()` also call `_parse_markdown_field()` but for ARC.md/EPOCH.md files — those are Phase 2/3 scope (WORK-245) and are NOT modified here.

**Modified: `.claude/haios/lib/scaffold.py` — `update_chapter_manifest()` and `update_chapter_manifest_status()`**

**update_chapter_manifest() target:**

Location: Lines 683-714

**Current Code (core logic):**
```python
# scaffold.py:684-714
content = chapter_file.read_text(encoding="utf-8")

# Check for duplicate
if f"| {work_id} |" in content:
    return {"updated": False, "reason": "already_present", ...}

# Find the work items table and append row before the next section
new_row = f"| {work_id} | {title} | Backlog | {work_type} |"
lines = content.split("\n")
insert_idx = None
in_work_items = False
for i, line in enumerate(lines):
    if line.strip().startswith("## Work Items"):
        in_work_items = True
        continue
    if in_work_items:
        if line.strip().startswith("|"):
            insert_idx = i
        elif line.strip() == "---" or line.strip().startswith("##"):
            break
if insert_idx is None:
    return {"updated": False, "reason": "table_not_found", ...}
lines.insert(insert_idx + 1, new_row)
chapter_file.write_text("\n".join(lines), encoding="utf-8")
```

**Target Code:**
```python
# scaffold.py:683-720 (replacement)
content = chapter_file.read_text(encoding="utf-8")

# Try frontmatter path first
from chapter_frontmatter import (
    parse_chapter_frontmatter,
    add_work_item_to_frontmatter,
)
fm = parse_chapter_frontmatter(chapter_file)
if fm is not None:
    # Frontmatter path: check duplicate then add
    work_items = fm.get("work_items", []) or []
    if any(item.get("id") == work_id for item in work_items):
        return {"updated": False, "reason": "already_present", "chapter_file": str(chapter_file)}
    added = add_work_item_to_frontmatter(chapter_file, work_id, title, "Backlog", work_type)
    if added:
        return {"updated": True, "reason": "row_added", "chapter_file": str(chapter_file)}
    return {"updated": False, "reason": "frontmatter_write_error", "chapter_file": str(chapter_file)}

# Fallback: legacy line-by-line table insertion
if f"| {work_id} |" in content:
    return {"updated": False, "reason": "already_present", "chapter_file": str(chapter_file)}
new_row = f"| {work_id} | {title} | Backlog | {work_type} |"
lines = content.split("\n")
insert_idx = None
in_work_items = False
for i, line in enumerate(lines):
    if line.strip().startswith("## Work Items"):
        in_work_items = True
        continue
    if in_work_items:
        if line.strip().startswith("|"):
            insert_idx = i
        elif line.strip() == "---" or line.strip().startswith("##"):
            break
if insert_idx is None:
    return {"updated": False, "reason": "table_not_found", "chapter_file": str(chapter_file)}
lines.insert(insert_idx + 1, new_row)
chapter_file.write_text("\n".join(lines), encoding="utf-8")
return {"updated": True, "reason": "row_added", "chapter_file": str(chapter_file)}
```

**update_chapter_manifest_status() target:**

Location: Lines 770-794

**Current Code (core logic):**
```python
# scaffold.py:779-794
lines = content.split("\n")
updated = False
for i, line in enumerate(lines):
    if f"| {work_id} |" in line:
        parts = line.split("|")
        if len(parts) >= 5:
            parts[3] = f" {new_status} "
            lines[i] = "|".join(parts)
            updated = True
        break
if not updated:
    return {"updated": False, "reason": "parse_error", ...}
chapter_file.write_text("\n".join(lines), encoding="utf-8")
```

**Target Code:**
```python
# scaffold.py:770-800 (replacement)
# A6 fix: try frontmatter path FIRST, without markdown substring guard
content = chapter_file.read_text(encoding="utf-8")

# Try frontmatter path first (no markdown substring guard — work items
# added via add_work_item_to_frontmatter exist only in YAML, not table)
from chapter_frontmatter import parse_chapter_frontmatter, update_work_item_in_frontmatter
fm = parse_chapter_frontmatter(chapter_file)
if fm is not None:
    updated = update_work_item_in_frontmatter(chapter_file, work_id, new_status)
    if updated:
        return {"updated": True, "reason": "status_updated", "chapter_file": str(chapter_file)}
    return {"updated": False, "reason": "work_id_not_found", "chapter_file": str(chapter_file)}

# Fallback: legacy line-by-line table surgery (substring guard here only)
if f"| {work_id} |" not in content:
    return {"updated": False, "reason": "work_id_not_found", "chapter_file": str(chapter_file)}

lines = content.split("\n")
updated = False
for i, line in enumerate(lines):
    if f"| {work_id} |" in line:
        parts = line.split("|")
        if len(parts) >= 5:
            parts[3] = f" {new_status} "
            lines[i] = "|".join(parts)
            updated = True
        break
if not updated:
    return {"updated": False, "reason": "parse_error", "chapter_file": str(chapter_file)}
chapter_file.write_text("\n".join(lines), encoding="utf-8")
return {"updated": True, "reason": "status_updated", "chapter_file": str(chapter_file)}
```

---

### Tests

#### Test 1: parse_chapter_frontmatter — returns dict when frontmatter present
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_parse_chapter_frontmatter_returns_dict(tmp_path)`
- **setup:** Write a CHAPTER.md with `---\nid: CH-067\nname: Test\nstatus: Active\n---\n# Chapter body`
- **assertion:** `parse_chapter_frontmatter(path)` returns `{"id": "CH-067", "name": "Test", "status": "Active"}`

#### Test 2: parse_chapter_frontmatter — returns None when no frontmatter
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_parse_chapter_frontmatter_returns_none_for_legacy(tmp_path)`
- **setup:** Write a CHAPTER.md with bold-markdown format only (no `---` delimiters)
- **assertion:** `parse_chapter_frontmatter(path)` returns `None`

#### Test 3: get_exit_criteria — reads from frontmatter when present
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_get_exit_criteria_from_frontmatter(tmp_path)`
- **setup:** Write CHAPTER.md with frontmatter `exit_criteria: [{text: "done", checked: true}, {text: "pending", checked: false}]`
- **assertion:** Returns `{"all_checked": False, "total": 2, "checked": 1, "unchecked_items": ["pending"]}`

#### Test 4: get_exit_criteria — falls back to regex when no frontmatter
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_get_exit_criteria_fallback_to_regex(tmp_path)`
- **setup:** Write CHAPTER.md with bold-markdown format and `## Exit Criteria\n- [x] Done\n- [ ] Not done`
- **assertion:** Returns `{"all_checked": False, "total": 2, "checked": 1, "unchecked_items": ["Not done"]}`

#### Test 5: get_exit_criteria — returns None when no exit criteria section
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_get_exit_criteria_returns_none_when_absent(tmp_path)`
- **setup:** Write CHAPTER.md with empty frontmatter (no exit_criteria key)
- **assertion:** `get_exit_criteria(path)` returns `None`

#### Test 6: migrate_file — injects frontmatter into legacy file
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_migrate_file_injects_frontmatter(tmp_path)`
- **setup:** Write CH-060 CHAPTER.md in bold-markdown format with one work item and two exit criteria (one checked, one not)
- **assertion:** After `migrate_file(path)`, `parse_chapter_frontmatter(path)` returns dict with `id="CH-060"`, `work_items` has one entry, `exit_criteria` has two entries with correct `checked` values; markdown body is preserved after `---`

#### Test 7: migrate_file — skips file already having frontmatter
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_migrate_file_skips_existing_frontmatter(tmp_path)`
- **setup:** Write CHAPTER.md with `---\nid: CH-060\n---\n# body`; record file mtime
- **assertion:** `migrate_file(path)` returns `{"skipped": True, ...}`; file content unchanged

#### Test 8: migrate_all — migrates all files in dry_run mode
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_migrate_all_dry_run(tmp_path)`
- **setup:** Create two minimal bold-markdown CHAPTER.md files in tmp_path with paths matching CHAPTER_FILES pattern; monkeypatch `PROJECT_ROOT`
- **assertion:** `migrate_all(base_path=tmp_path, dry_run=True)` returns 2 results with `migrated=True` but files are not written (content unchanged)

#### Test 9: add_work_item_to_frontmatter — adds new item to frontmatter list
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_add_work_item_to_frontmatter(tmp_path)`
- **setup:** Write CHAPTER.md with frontmatter `work_items: [{id: WORK-001, title: Old, status: Active, type: implementation}]`
- **assertion:** `add_work_item_to_frontmatter(path, "WORK-002", "New", "Backlog", "investigation")` returns `True`; `get_work_items(path)` returns list of 2 items including `{id: "WORK-002", ...}`

#### Test 10: add_work_item_to_frontmatter — returns False if work_id already present
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_add_work_item_duplicate_returns_false(tmp_path)`
- **setup:** CHAPTER.md with frontmatter containing WORK-001
- **assertion:** `add_work_item_to_frontmatter(path, "WORK-001", ...)` returns `False`; work_items list unchanged

#### Test 11: update_work_item_in_frontmatter — updates status in frontmatter
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_update_work_item_status_in_frontmatter(tmp_path)`
- **setup:** CHAPTER.md with frontmatter `work_items: [{id: WORK-001, status: Active}]`
- **assertion:** `update_work_item_in_frontmatter(path, "WORK-001", "Complete")` returns `True`; re-read frontmatter shows `status: Complete`

#### Test 12: status_propagator._check_exit_criteria — uses frontmatter when available
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_status_propagator_uses_frontmatter_exit_criteria(tmp_path)`
- **setup:** Create StatusPropagator with tmp_path; create CHAPTER.md with frontmatter including two exit_criteria (one unchecked); create haios.yaml pointing to arcs_dir
- **assertion:** `propagator._check_exit_criteria("CH-060", "call")` returns `{"all_checked": False, "total": 2, "checked": 1, ...}`

#### Test 13: dod_validation.validate_chapter_dod — uses frontmatter exit criteria
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_validate_chapter_dod_with_frontmatter(tmp_path)`
- **setup:** Create CHAPTER.md with frontmatter (all exit_criteria checked=true) in `tmp_path/.claude/haios/epochs/E2_5/arcs/ceremonies/chapters/CH-015-Test/CHAPTER.md`; create one complete work item
- **assertion:** `validate_chapter_dod("CH-015", "ceremonies", base_path=tmp_path)` returns `DoDResult` with `passed=True`

#### Test 14: dod_validation.validate_chapter_dod — falls back to regex for legacy format
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_validate_chapter_dod_legacy_fallback(tmp_path)`
- **setup:** Create CHAPTER.md in CHAPTER.md-in-directory format (legacy markdown body, no frontmatter) with one unchecked exit criterion
- **assertion:** `validate_chapter_dod(...)` returns `passed=False` with exit criteria failure

#### Test 15: scaffold.update_chapter_manifest — uses frontmatter when available
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_update_chapter_manifest_uses_frontmatter(tmp_path)`
- **setup:** Create CHAPTER.md with YAML frontmatter `work_items: []` in chapters directory; call `update_chapter_manifest("WORK-NEW", "Title", "CH-060", base_path=tmp_path)`
- **assertion:** `result["updated"]` is `True`; `parse_chapter_frontmatter(path)["work_items"]` contains `{id: "WORK-NEW", ...}`

#### Test 16: scaffold.update_chapter_manifest — falls back to line insertion for legacy
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_update_chapter_manifest_legacy_fallback(tmp_path)`
- **setup:** Create CHAPTER.md in bold-markdown format (no frontmatter) with `## Work Items` table
- **assertion:** `update_chapter_manifest(...)` returns `{"updated": True, "reason": "row_added", ...}`; `"| WORK-NEW |"` in file content

#### Test 17: build_frontmatter — parses all fields from a realistic CHAPTER.md
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_build_frontmatter_parses_all_fields()`
- **setup:** Use the exact content of CH-060 CHAPTER.md (SessionBoundaryFix) as input string
- **assertion:** `build_frontmatter(content)["id"] == "CH-060"`, `["arc"] == "call"`, `["epoch"] == "E2.8"`, `["status"] == "Complete"`, `len(["exit_criteria"]) == 4`, `all(c["checked"] for c in ["exit_criteria"])`, `len(["work_items"]) == 1`, `["dependencies"] == []`

#### Test 18: _write_frontmatter — preserves body with multiple --- separators (A2 critique fix)
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_write_frontmatter_preserves_body_separators(tmp_path)`
- **setup:** Write CHAPTER.md with frontmatter containing `work_items: [{id: WORK-NEW, title: "New", status: Active, type: implementation}]` AND `---` horizontal rules in body: `---\nid: CH-067\nstatus: Active\nwork_items:\n- id: WORK-NEW\n  title: New\n  status: Active\n  type: implementation\n---\n# Chapter\n\n---\n\n## Section\n\n---\n\n## Another`
- **assertion:** Call `update_work_item_in_frontmatter(path, "WORK-NEW", "Complete")`, re-read file, verify body still contains both `---` lines and `## Section` and `## Another` intact; also verify frontmatter `work_items[0]["status"] == "Complete"`

#### Test 19: update_chapter_manifest_status — finds frontmatter-only work item (A6 critique fix)
- **file:** `tests/test_chapter_frontmatter.py`
- **function:** `test_update_chapter_manifest_status_frontmatter_only_item(tmp_path)`
- **setup:** Create CHAPTER.md with frontmatter containing `work_items: [{id: WORK-NEW, title: "New", status: Active, type: implementation}]` but NO `| WORK-NEW |` row in the markdown table body
- **assertion:** `update_chapter_manifest_status("WORK-NEW", "CH-067", "Complete", base_path=tmp_path)` returns `{"updated": True, ...}`; re-read frontmatter, verify `work_items[0]["status"] == "Complete"`

---

### Design

#### File 1 (NEW): `.claude/haios/lib/chapter_frontmatter.py`

Complete implementation in Desired State section above.

#### File 2 (NEW): `.claude/haios/lib/migrate_chapter_frontmatter.py`

Complete implementation in Desired State section above.

#### File 3 (MODIFY): `.claude/haios/lib/status_propagator.py`

**Location:** Lines 206-240, inside `_check_exit_criteria()`

Replace the inline regex parsing block with a single delegating call to `get_exit_criteria()`. The `_find_chapter_file()` method is preserved unchanged (still needed for path resolution).

Also remove the `import re` if it becomes unused after this change, or verify it is still used elsewhere in the file (it is — lines 218, 221, 224, 307, 349 still use `re`). No change to the import block.

#### File 4 (MODIFY): `.claude/haios/lib/dod_validation.py`

**Location:** Lines 230-291, inside `validate_chapter_dod()`

The `_parse_markdown_field()` function is preserved — it is still called by `validate_arc_dod()` and `validate_epoch_dod()` for ARC.md/EPOCH.md (Phase 2/3 scope).

The `_count_exit_criteria()` function is preserved as the backward-compatible fallback.

Key change: `validate_chapter_dod()` now attempts to find a `CHAPTER.md` companion (the new directory-based format) alongside the globbed `CH-*.md` file, and delegates to `get_exit_criteria()` from `chapter_frontmatter`. If no CHAPTER.md companion, falls back to existing `_count_exit_criteria(content)`.

Note on file path resolution: `validate_chapter_dod` currently globs `arc_dir.glob(f"{chapter_id}-*.md")` which finds flat files like `CH-015-ClosureCeremonies.md`. The new CHAPTER.md files live in subdirectories: `chapters/CH-015-ClosureCeremonies/CHAPTER.md`. The function needs to also search subdirectories. Update the glob pattern:

```python
# Before (line 231):
chapter_files = list(arc_dir.glob(f"{chapter_id}-*.md"))

# After:
chapter_files = list(arc_dir.glob(f"chapters/{chapter_id}-*/CHAPTER.md"))
if not chapter_files:
    # Backward compat: flat file format
    chapter_files = list(arc_dir.glob(f"{chapter_id}-*.md"))
```

#### File 5 (MODIFY): `.claude/haios/lib/scaffold.py`

**Location:** Lines 683-714 (`update_chapter_manifest()`) and 770-794 (`update_chapter_manifest_status()`)

Both functions get a frontmatter-first branch added before the existing line-by-line logic. The existing logic becomes the fallback. See Desired State for exact code.

---

### Call Chain

```
StatusPropagator.propagate()
    |
    +-> _check_exit_criteria(chapter_id, arc_name)
            |
            +-> _find_chapter_file()   # unchanged — path resolution
            |
            +-> get_exit_criteria(chapter_file)   # NEW — delegates here
                    |
                    +-> parse_chapter_frontmatter()  # if frontmatter: read fm
                    |
                    +-> [fallback] regex parse markdown body

scaffold.update_chapter_manifest()
    |
    +-> parse_chapter_frontmatter()   # frontmatter present?
    |       |
    |       +-> add_work_item_to_frontmatter()   # YES: update fm
    |
    +-> [fallback] line-by-line table insertion   # NO: legacy path

migrate_chapter_frontmatter.migrate_all()
    |
    +-> migrate_file(path) x 10
            |
            +-> _has_frontmatter()   # skip if already migrated
            |
            +-> build_frontmatter()  # parse bold-markdown fields
            |
            +-> write ---fm--- + original body
```

---

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| New `chapter_frontmatter.py` module vs. extending dod_validation | New module | Three consumers need the same parsing logic; centralizing in a dedicated module avoids duplication and gives a single change point. Extending dod_validation would create unwanted coupling between scaffold and dod_validation. |
| Frontmatter-first with fallback, not replace-then-migrate | Both paths active simultaneously | L3.6 backward compatibility requirement. Migration script is separate and idempotent. Consumers work on both formats from day 1. Reduces deployment risk: can run migration after code lands. |
| Prepend frontmatter to existing file (not replace body) | Prepend `---\n...\n---\n` before existing content | Preserves the full markdown body verbatim. Human readers still see the same document. ARC.md references, Purpose, and References sections are all kept. |
| `migrate_file()` is idempotent | Check `_has_frontmatter()` and return `skipped` | Safe to re-run. Can call migrate_all() any number of times without corrupting already-migrated files. |
| Lazy import of `chapter_frontmatter` inside functions | `from chapter_frontmatter import ...` at call site | Avoids circular import risk. status_propagator, dod_validation, and scaffold already use try/except ImportError patterns for sibling modules (confirmed in codebase). Lazy import is consistent with existing patterns in status_propagator (line 59: `from hierarchy_engine import HierarchyQueryEngine`). |
| `validate_chapter_dod` searches `chapters/` subdirectory first | New glob `chapters/{chapter_id}-*/CHAPTER.md` before fallback to flat `.md` | The new CHAPTER.md files live in the subdirectory convention. The old tests use flat files. Both must work. The new pattern is tried first since it's the target format. |
| YAML serialization with `sort_keys=False` | Preserve field order as-defined in build_frontmatter | More readable output. Field order matches the order of parsing (id, name, arc, epoch, status, work_items, exit_criteria, dependencies). |

---

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| CHAPTER.md has no exit_criteria key in frontmatter | `get_exit_criteria()` returns `None` (same as no section) | Test 5 |
| CHAPTER.md has frontmatter but work_items is null/empty | `get_work_items()` returns `[]` | (covered by Test 9 — empty list) |
| `migrate_file()` called on file that already has frontmatter | Returns `{"skipped": True}` immediately without reading yaml | Test 7 |
| Bold-markdown field has trailing whitespace or tab | `_parse_bold_field()` uses `.strip()` on capture group | Test 17 (realistic content) |
| Dependencies table has "None" placeholder row | `_parse_dependencies_table()` skips rows where direction is "None" or target is "-" | Test 17 |
| update_chapter_manifest called on frontmatter file for duplicate work_id | Check fm["work_items"] for existing id before calling add_work_item_to_frontmatter | Test 10 |
| validate_chapter_dod with new directory structure | Glob `chapters/{chapter_id}-*/CHAPTER.md` first, fall back to flat glob | Test 13, 14 |

---

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| `validate_chapter_dod` glob change breaks existing test_dod_validation.py tests | H | Keep flat-file fallback in validate_chapter_dod. Existing tests use flat files in `arc_dir/CH-*.md` format — the fallback glob preserves this. Run tests at RED phase to confirm exactly which tests fail. |
| yaml.dump reorders keys in CHAPTER.md frontmatter | L | Use `sort_keys=False` in yaml.dump. Test 17 verifies realistic round-trip. |
| Migration script writes corrupt YAML (e.g. for title with colon) | M | yaml.dump handles escaping automatically. The `title` field from WORK.md is used as-is in work_items; yaml.dump will quote it if needed. |
| Lazy import of chapter_frontmatter fails in test environment | M | Tests add `.claude/haios/lib` to sys.path (same pattern as all existing tests). chapter_frontmatter.py has no external dependencies beyond yaml (already a project dependency). |
| `_write_frontmatter()` called on file without --- delimiters | L | Guard with `raise ValueError` — callers only call it from add/update functions which check parse_chapter_frontmatter first. |
| Migration modifies CHAPTER.md files tracked by git | L | All 10 files are version-controlled. Migration is a commit. Diff is reviewable. Test 8 dry_run mode allows preview before writing. |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Create `tests/test_chapter_frontmatter.py` with all 19 test functions from Layer 1 Tests section. Add `TestUpdateChapterManifestFrontmatter` class to `tests/test_chapter_manifest_update.py` covering Tests 15-16. Add `TestValidateChapterDodFrontmatter` class to `tests/test_dod_validation.py` covering Tests 13-14.
- **output:** Test files exist, all new tests fail (RED state)
- **verify:** `pytest tests/test_chapter_frontmatter.py -v 2>&1 | grep -c "FAILED\|ERROR"` equals 19; `pytest tests/test_chapter_manifest_update.py::TestUpdateChapterManifestFrontmatter -v 2>&1 | grep -c "FAILED\|ERROR"` equals 2; `pytest tests/test_dod_validation.py::TestValidateChapterDodFrontmatter -v 2>&1 | grep -c "FAILED\|ERROR"` equals 2

### Step 2: Implement chapter_frontmatter.py (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (NEW)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Create `.claude/haios/lib/chapter_frontmatter.py` from Layer 1 Desired State — exact code provided
- **output:** Tests 1-11 in test_chapter_frontmatter.py pass
- **verify:** `pytest tests/test_chapter_frontmatter.py::TestParseFrontmatter tests/test_chapter_frontmatter.py::TestGetExitCriteria tests/test_chapter_frontmatter.py::TestWorkItemFunctions -v` exits 0

### Step 3: Implement migrate_chapter_frontmatter.py (GREEN)
- **spec_ref:** Layer 1 > Design > File 2 (NEW)
- **input:** Step 2 complete (chapter_frontmatter.py working)
- **action:** Create `.claude/haios/lib/migrate_chapter_frontmatter.py` from Layer 1 Desired State — exact code provided
- **output:** Tests 6-8 and 17 pass
- **verify:** `pytest tests/test_chapter_frontmatter.py::TestMigration -v` exits 0

### Step 4: Modify status_propagator.py
- **spec_ref:** Layer 1 > Design > File 3 (MODIFY)
- **input:** Step 2 complete (chapter_frontmatter.py available)
- **action:** Replace lines 210-240 in `_check_exit_criteria()` with the 3-line delegating call per Layer 1 Desired State diff
- **output:** Test 12 passes; existing status_propagator tests unaffected
- **verify:** `pytest tests/test_chapter_frontmatter.py::test_status_propagator_uses_frontmatter_exit_criteria -v` exits 0; `pytest tests/ -k "status_propagat" -v` exits 0 with no new failures

### Step 5: Modify dod_validation.py
- **spec_ref:** Layer 1 > Design > File 4 (MODIFY)
- **input:** Step 2 complete (chapter_frontmatter.py available)
- **action:** Update `validate_chapter_dod()` — change glob pattern to try `chapters/{chapter_id}-*/CHAPTER.md` first, then fall back to flat; replace exit criteria section with frontmatter-aware block per Layer 1 Desired State
- **output:** Tests 13-14 pass; existing TestValidateChapterDod tests still pass
- **verify:** `pytest tests/test_dod_validation.py -v` exits 0 with no failures

### Step 6: Modify scaffold.py
- **spec_ref:** Layer 1 > Design > File 5 (MODIFY)
- **input:** Step 2 complete (chapter_frontmatter.py available)
- **action:** Update `update_chapter_manifest()` and `update_chapter_manifest_status()` with frontmatter-first branch per Layer 1 Desired State
- **output:** Tests 15-16 pass; existing TestUpdateChapterManifest tests still pass
- **verify:** `pytest tests/test_chapter_manifest_update.py -v` exits 0 with no failures

### Step 7: Run migration script
- **spec_ref:** Layer 1 > Design > File 2 (NEW) — `migrate_all()`
- **input:** Steps 2-6 complete; consumer modules updated
- **action:** Run `python .claude/haios/lib/migrate_chapter_frontmatter.py` from project root; review output; verify 10 files migrated
- **output:** All 10 CHAPTER.md files have YAML frontmatter prepended; existing markdown body preserved
- **verify:** `python -c "from pathlib import Path; import yaml; content = Path('.claude/haios/epochs/E2_8/arcs/call/chapters/CH-060-SessionBoundaryFix/CHAPTER.md').read_text(); parts = content.split('---', 2); fm = yaml.safe_load(parts[1]); print(fm['id'], fm['status'])"` outputs `CH-060 Complete`

### Step 8: Full regression test
- **spec_ref:** Layer 0 > Test Files
- **input:** Steps 1-7 complete
- **action:** Run full pytest suite
- **output:** All tests pass; no new failures
- **verify:** `pytest tests/ -v --tb=short 2>&1 | tail -5` shows `0 failed`

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_chapter_frontmatter.py -v` | 19 passed, 0 failed |
| `pytest tests/test_dod_validation.py -v` | All passed, 0 failed |
| `pytest tests/test_chapter_manifest_update.py -v` | All passed, 0 failed |
| `pytest tests/ -v --tb=short` | 0 new failures vs pre-implementation baseline |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| CHAPTER.md files have YAML frontmatter | `python -c "from pathlib import Path; import yaml; files = list(Path('.claude/haios/epochs').glob('**/CHAPTER.md')); print(sum(1 for f in files if '---' in f.read_text().split('---', 2)[0] or f.read_text().startswith('---')))"` | 10 |
| status_propagator reads frontmatter | `grep -n "get_exit_criteria" .claude/haios/lib/status_propagator.py` | 1+ match |
| dod_validation reads frontmatter | `grep -n "get_exit_criteria\|chapter_frontmatter" .claude/haios/lib/dod_validation.py` | 1+ match |
| scaffold updates frontmatter | `grep -n "add_work_item_to_frontmatter\|update_work_item_in_frontmatter" .claude/haios/lib/scaffold.py` | 2 matches |
| Migration script exists | `python .claude/haios/lib/migrate_chapter_frontmatter.py --dry-run` | Output contains "10 migrated" |
| chapter_frontmatter.py exists | `python -c "from chapter_frontmatter import parse_chapter_frontmatter; print('ok')"` (from `.claude/haios/lib/`) | `ok` |
| Backward-compatible fallback | `pytest tests/test_dod_validation.py::TestValidateChapterDod -v` | All original tests pass (no regression) |
| All existing tests pass | `pytest tests/ --tb=short 2>&1 | grep -E "passed|failed"` | 0 failed |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| No stale direct regex for exit criteria in status_propagator | `grep -n "Exit Criteria" .claude/haios/lib/status_propagator.py` | 0 matches (regex moved to chapter_frontmatter) |
| No stale bold-markdown exit criteria regex in status_propagator | `grep -n "\\\\[[ x]\\\\]" .claude/haios/lib/status_propagator.py` | 0 matches |
| chapter_frontmatter imported by all 3 consumers | `grep -rn "chapter_frontmatter" .claude/haios/lib/` | 3+ file matches |
| CHAPTER.md body preserved after migration | `grep "Purpose" .claude/haios/epochs/E2_8/arcs/call/chapters/CH-060-SessionBoundaryFix/CHAPTER.md` | 1+ match (body intact) |
| Runtime consumer exists for chapter_frontmatter | `grep -rn "from chapter_frontmatter import\|import chapter_frontmatter" .claude/haios/lib/` | 3 matches (status_propagator, dod_validation, scaffold) |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 8 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] Runtime consumer exists (Consumer Integrity table above)
- [ ] No stale regex in status_propagator._check_exit_criteria (Consumer Integrity table above)
- [ ] All 10 CHAPTER.md files migrated to YAML frontmatter format
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `docs/work/active/WORK-240/WORK.md` (spawning investigation)
- `.claude/haios/lib/status_propagator.py` (consumer: exit criteria, lines 190-240)
- `.claude/haios/lib/dod_validation.py` (consumer: chapter Status, exit criteria, lines 68-93, 199-291)
- `.claude/haios/lib/scaffold.py` (consumer: work items table, lines 647-794)
- `tests/test_chapter_manifest_update.py` (existing scaffold tests)
- `tests/test_dod_validation.py` (existing dod_validation tests)
- Memory: 89402-89407 (WORK-240 investigation findings)
- ADR-033 (work item completion criteria)

---
