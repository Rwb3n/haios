---
template: implementation_plan
plan_version: "2.0"
status: approved
date: 2026-03-07
backlog_id: WORK-245
title: "ARC.md YAML Frontmatter Migration"
author: Hephaestus
lifecycle_phase: plan
session: 468
generated: 2026-03-07
last_updated: 2026-03-07T12:30:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-245/WORK.md"
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
# Implementation Plan: ARC.md YAML Frontmatter Migration

---

## Goal

Migrate all 34 ARC.md files to YAML frontmatter format and replace 4 duplicate pipe-split table parsers across hierarchy_engine, status_propagator, epoch_loader, and epoch_validator with a centralized `arc_frontmatter` module, while preserving backward-compatible fallback for unmigrated files.

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
| `.claude/haios/lib/arc_frontmatter.py` | CREATE | 2 |
| `.claude/haios/lib/migrate_arc_frontmatter.py` | CREATE | 2 |
| `.claude/haios/lib/hierarchy_engine.py` | MODIFY | 2 |
| `.claude/haios/lib/status_propagator.py` | MODIFY | 2 |
| `.claude/haios/lib/epoch_loader.py` | MODIFY | 2 |
| `.claude/haios/lib/epoch_validator.py` | MODIFY | 2 |
| `.claude/haios/lib/dod_validation.py` | MODIFY | 2 |

### Consumer Files

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| All 34 ARC.md files | data files migrated by script | N/A | MIGRATE (via script) |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_arc_frontmatter.py` | CREATE | New test file for arc_frontmatter.py and migrate_arc_frontmatter.py |
| `tests/test_chapter_frontmatter.py` | NO CHANGE | Existing tests remain valid |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 3 | arc_frontmatter.py, migrate_arc_frontmatter.py, test_arc_frontmatter.py |
| Files to modify | 5 | hierarchy_engine, status_propagator, epoch_loader, epoch_validator, dod_validation |
| ARC.md files to migrate | 34 | Glob `.claude/haios/epochs/**/ARC.md` |
| Tests to write | 22 | Test Files table (19 original + 3 critique-driven: 7a, 7b, 7c) |
| Total blast radius | 8 | 3 new + 5 modified (excludes 34 data files) |

---

## Layer 1: Specification

### Current State

```python
# hierarchy_engine.py:282-292 — _parse_arc_metadata
def _parse_arc_metadata(self, arc_file: Path) -> Dict[str, str]:
    """Extract theme and status from ARC.md definition section."""
    content = arc_file.read_text(encoding="utf-8")
    theme = ""
    status = ""
    for line in content.split("\n"):
        if line.startswith("**Theme:**"):
            theme = line.split("**Theme:**", 1)[1].strip()
        elif line.startswith("**Status:**"):
            status = line.split("**Status:**", 1)[1].strip()
    return {"theme": theme, "status": status}

# hierarchy_engine.py:294-327 — _parse_arc_chapters
def _parse_arc_chapters(self, arc_file: Path, arc_name: str) -> List[ChapterInfo]:
    content = arc_file.read_text(encoding="utf-8")
    chapters = []
    for line in content.split("\n"):
        if re.match(r"\s*\|\s*CH-\d+", line):
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) >= 6:
                ch_id = cells[0]
                title = cells[1]
                work_str = cells[2]
                status = cells[-1]
                work_items = re.findall(r"WORK-\d+", work_str)
                chapters.append(ChapterInfo(
                    id=ch_id, title=title, work_items=work_items,
                    status=status, arc=arc_name,
                ))
    return chapters

# status_propagator.py:247-293 — update_arc_chapter_status (line-by-line table surgery)
# status_propagator.py:295-326 — is_arc_complete (table row scanning)
# epoch_loader.py:91-107 — _extract_chapter_table (pipe-split parsing)
# epoch_validator.py:194-211 — validate_epoch_status (table row parsing for WORK-IDs)
# dod_validation.py:362 and 446 — _parse_markdown_field(content, "Status") for ARC.md status
```

**Behavior:** Each of the 4 consumers independently re-implements pipe-split table parsing to read ARC.md chapter data. status_propagator performs fragile regex table surgery to update a chapter row's status cell.

**Problem:** 4 duplicate parsers diverge independently; table surgery is brittle (cell count assumptions, whitespace sensitivity); any ARC.md format change requires 4 coordinated fixes.

### Desired State

```python
# .claude/haios/lib/arc_frontmatter.py — new centralized module
# All consumers import from here instead of parsing inline

# hierarchy_engine.py (after):
from arc_frontmatter import get_arc_status, get_arc_metadata, get_chapters

def _parse_arc_metadata(self, arc_file: Path) -> Dict[str, str]:
    return get_arc_metadata(arc_file)

def _parse_arc_chapters(self, arc_file: Path, arc_name: str) -> List[ChapterInfo]:
    raw = get_chapters(arc_file)
    return [
        ChapterInfo(
            id=ch["id"],
            title=ch["title"],
            work_items=re.findall(r"WORK-\d+", " ".join(ch.get("work_items", []))),
            status=ch["status"],
            arc=arc_name,
        )
        for ch in raw
    ]

# status_propagator.py (after):
from arc_frontmatter import update_chapter_in_frontmatter, get_chapters

def update_arc_chapter_status(self, arc_name, chapter_id, new_status):
    arc_file = self._resolve_arc_file(arc_name)
    result = update_chapter_in_frontmatter(arc_file, chapter_id, new_status)
    if result:
        return {"updated": True}
    return {"updated": False, "reason": "chapter_not_found_or_no_frontmatter"}

def is_arc_complete(self, arc_name):
    arc_file = self._resolve_arc_file(arc_name)
    chapters = get_chapters(arc_file)
    if not chapters:
        return False
    return all(ch["status"].lower() in ARC_COMPLETE_STATUSES for ch in chapters)
```

**Behavior:** arc_frontmatter.py is the single source of truth for ARC.md parsing. All 4 consumers delegate to it. Frontmatter-first with backward-compatible bold-markdown/table fallback (L3.6).

**Result:** 4 duplicate parsers eliminated; status updates are dict writes not regex surgery; format changes require only arc_frontmatter.py to change.

### Tests

#### Test 1: parse_arc_frontmatter — returns dict when frontmatter present
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_parse_arc_frontmatter_returns_dict(tmp_path)`
- **setup:** Write ARC.md with `---\nid: infrastructure\nepoch: "E2.8"\nstatus: Planning\n---\n# Arc body\n`
- **assertion:** `parse_arc_frontmatter(path)` returns `{"id": "infrastructure", "epoch": "E2.8", "status": "Planning"}`

#### Test 2: parse_arc_frontmatter — returns None for legacy bold-markdown file
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_parse_arc_frontmatter_returns_none_for_legacy(tmp_path)`
- **setup:** Write ARC.md with `**Arc ID:** infrastructure\n**Status:** Planning\n`
- **assertion:** `parse_arc_frontmatter(path)` returns `None`

#### Test 3: get_arc_status — reads from frontmatter when present
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_get_arc_status_from_frontmatter(tmp_path)`
- **setup:** Write ARC.md with frontmatter containing `status: Active`
- **assertion:** `get_arc_status(path)` returns `"Active"`

#### Test 4: get_arc_status — falls back to bold-markdown when no frontmatter
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_get_arc_status_fallback(tmp_path)`
- **setup:** Write ARC.md legacy format with `**Status:** Planning`
- **assertion:** `get_arc_status(path)` returns `"Planning"`

#### Test 5: get_arc_metadata — returns id, epoch, theme, status, started
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_get_arc_metadata_from_frontmatter(tmp_path)`
- **setup:** Write ARC.md with full frontmatter (id, epoch, theme, status, started)
- **assertion:** `get_arc_metadata(path)` returns `{"theme": "Fix what's broken", "status": "Planning"}`

#### Test 6: get_chapters — reads chapter list from frontmatter
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_get_chapters_from_frontmatter(tmp_path)`
- **setup:** Write ARC.md frontmatter with chapters list containing CH-065 and CH-067
- **assertion:** `get_chapters(path)` returns list of 2 dicts; first has `id="CH-065"`, `status="Complete"`

#### Test 7: get_chapters — falls back to 6-column table parsing when no frontmatter
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_get_chapters_fallback_6col_table(tmp_path)`
- **setup:** Write legacy ARC.md with `| CH-065 | BugBatch-E28 | New | REQ-CEREMONY-001 | None | Complete |` table row
- **assertion:** `get_chapters(path)` returns list with `{"id": "CH-065", "title": "BugBatch-E28", "status": "Complete", ...}`

#### Test 7a: get_chapters — falls back to 4-column table parsing (A1/A7 critique)
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_get_chapters_fallback_4col_table(tmp_path)`
- **setup:** Write legacy E2-era ARC.md with `## Chapters\n| Chapter | Name | Status | Purpose |\n|---|---|---|---|\n| CH-001 | GroundCycle | Complete | Core grounding |\n`
- **assertion:** `get_chapters(path)` returns list with `{"id": "CH-001", "title": "GroundCycle", "status": "Complete", "work_items": [], "requirements": [], "dependencies": []}`

#### Test 7b: get_chapters — falls back to 5-column table parsing (A7 critique)
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_get_chapters_fallback_5col_table(tmp_path)`
- **setup:** Write legacy ARC.md with `## Chapters\n| CH-ID | Title | Requirements | Dependencies | Status |\n|---|---|---|---|---|\n| CH-018 | ChapterReview | REQ-FEEDBACK-001 | None | Complete |\n`
- **assertion:** `get_chapters(path)` returns list with `{"id": "CH-018", "title": "ChapterReview", "status": "Complete", "work_items": [], "requirements": ["REQ-FEEDBACK-001"], "dependencies": []}`

#### Test 7c: get_exit_criteria — falls back to Arc Completion Criteria heading (A3 critique)
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_get_exit_criteria_fallback_arc_completion_heading(tmp_path)`
- **setup:** Write legacy E2-era ARC.md with `## Arc Completion Criteria\n- [x] done\n- [ ] pending\n`
- **assertion:** `get_exit_criteria(path)` returns `{"all_checked": False, "total": 2, "checked": 1, "unchecked_items": ["pending"]}`

#### Test 8: get_exit_criteria — reads from frontmatter
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_get_exit_criteria_from_frontmatter(tmp_path)`
- **setup:** Write ARC.md frontmatter with `exit_criteria: [{text: "bugs resolved", checked: true}]`
- **assertion:** `get_exit_criteria(path)` returns `{"all_checked": True, "total": 1, "checked": 1, "unchecked_items": []}`

#### Test 9: get_exit_criteria — falls back to checkbox parsing when no frontmatter
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_get_exit_criteria_fallback(tmp_path)`
- **setup:** Write legacy ARC.md with `## Exit Criteria\n- [x] done\n- [ ] pending\n`
- **assertion:** `get_exit_criteria(path)` returns `{"all_checked": False, "total": 2, "checked": 1, "unchecked_items": ["pending"]}`

#### Test 10: update_chapter_in_frontmatter — updates chapter status
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_update_chapter_in_frontmatter(tmp_path)`
- **setup:** Write ARC.md with frontmatter chapters list containing CH-067 with `status: Active`
- **assertion:** `update_chapter_in_frontmatter(path, "CH-067", "Complete")` returns `True`; re-read frontmatter shows `ch["status"] == "Complete"`

#### Test 11: update_chapter_in_frontmatter — returns False when chapter not found
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_update_chapter_not_found(tmp_path)`
- **setup:** Write ARC.md frontmatter with chapters list not containing CH-999
- **assertion:** `update_chapter_in_frontmatter(path, "CH-999", "Complete")` returns `False`

#### Test 12: update_chapter_in_frontmatter — returns False when no frontmatter
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_update_chapter_no_frontmatter(tmp_path)`
- **setup:** Write legacy ARC.md (no frontmatter)
- **assertion:** `update_chapter_in_frontmatter(path, "CH-067", "Complete")` returns `False`

#### Test 13: migrate_file — injects frontmatter into legacy ARC.md
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_migrate_arc_file_injects_frontmatter(tmp_path)`
- **setup:** Write `ARC_INFRA_LEGACY_CONTENT` (full infrastructure ARC.md content) to tmp_path/ARC.md
- **assertion:** `migrate_file(path)` returns `{"migrated": True, "skipped": False}`; `parse_arc_frontmatter(path)` returns dict with `id="infrastructure"`, 2 chapters in list, exit_criteria with `checked=True`; original markdown body still present

#### Test 14: migrate_file — skips file already having frontmatter
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_migrate_arc_file_skips_existing(tmp_path)`
- **setup:** Write ARC.md with frontmatter already; record original_content
- **assertion:** `migrate_file(path)` returns `{"skipped": True}`; file content unchanged

#### Test 15: migrate_file — dry_run does not write
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_migrate_arc_file_dry_run(tmp_path)`
- **setup:** Write legacy ARC.md; record original_content
- **assertion:** `migrate_file(path, dry_run=True)` returns `{"migrated": True}`; file content unchanged

#### Test 16: build_arc_frontmatter — parses all fields from realistic ARC.md
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_build_arc_frontmatter_parses_all_fields()`
- **setup:** Use `ARC_INFRA_LEGACY_CONTENT` fixture (no file I/O)
- **assertion:** `build_arc_frontmatter(content)` returns dict with `id="infrastructure"`, `epoch="E2.8"`, `theme="Fix what's broken"`, `status="Planning"`, `started="2026-02-17 (Session 393)"`, 2 chapters, 1 exit criterion with `checked=True`

#### Test 17: hierarchy_engine uses arc_frontmatter for chapters
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_hierarchy_engine_uses_arc_frontmatter(tmp_path)`
- **setup:** Create haios.yaml + ARC.md with frontmatter chapters in tmp_path structure; HierarchyQueryEngine(base_path=tmp_path)
- **assertion:** `engine.get_chapters("infrastructure")` returns ChapterInfo list where `chapters[0].id == "CH-065"` and `chapters[0].status == "Complete"`

#### Test 18: status_propagator uses arc_frontmatter for chapter update
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_status_propagator_uses_arc_frontmatter(tmp_path)`
- **setup:** Create haios.yaml + ARC.md with frontmatter chapters (CH-067 Active) in tmp_path; StatusPropagator(base_path=tmp_path)
- **assertion:** `propagator.update_arc_chapter_status("infrastructure", "CH-067", "Complete")` returns `{"updated": True}`; re-read ARC.md frontmatter shows CH-067 status is "Complete"

#### Test 19: dod_validation.validate_epoch_dod uses arc_frontmatter
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `test_epoch_dod_uses_arc_frontmatter(tmp_path)`
- **setup:** Create ARC.md with frontmatter `status: Complete` in tmp_path epoch structure; validate_epoch_dod("E2_8", base_path=tmp_path)
- **assertion:** Result `passed is True`; legacy `_parse_markdown_field` not needed

### Design

#### File 1 (NEW): `.claude/haios/lib/arc_frontmatter.py`

```python
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
```

#### File 2 (NEW): `.claude/haios/lib/migrate_arc_frontmatter.py`

```python
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
```

#### File 3 (MODIFY): `.claude/haios/lib/hierarchy_engine.py`

**Location:** Lines 282-327 — `_parse_arc_metadata()` and `_parse_arc_chapters()`

**Current Code (lines 282-327):**
```python
def _parse_arc_metadata(self, arc_file: Path) -> Dict[str, str]:
    """Extract theme and status from ARC.md definition section."""
    content = arc_file.read_text(encoding="utf-8")
    theme = ""
    status = ""
    for line in content.split("\n"):
        if line.startswith("**Theme:**"):
            theme = line.split("**Theme:**", 1)[1].strip()
        elif line.startswith("**Status:**"):
            status = line.split("**Status:**", 1)[1].strip()
    return {"theme": theme, "status": status}

def _parse_arc_chapters(
    self, arc_file: Path, arc_name: str
) -> List[ChapterInfo]:
    """Parse chapter table rows from ARC.md.
    ...
    """
    content = arc_file.read_text(encoding="utf-8")
    chapters = []
    for line in content.split("\n"):
        if re.match(r"\s*\|\s*CH-\d+", line):
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) >= 6:
                ch_id = cells[0]
                title = cells[1]
                work_str = cells[2]
                status = cells[-1]
                work_items = re.findall(r"WORK-\d+", work_str)
                chapters.append(
                    ChapterInfo(
                        id=ch_id,
                        title=title,
                        work_items=work_items,
                        status=status,
                        arc=arc_name,
                    )
                )
    return chapters
```

**Target Code:**
```python
def _parse_arc_metadata(self, arc_file: Path) -> Dict[str, str]:
    """Extract theme and status from ARC.md — frontmatter-first with fallback."""
    try:
        from arc_frontmatter import get_arc_metadata
    except ImportError:
        from .arc_frontmatter import get_arc_metadata
    return get_arc_metadata(arc_file)

def _parse_arc_chapters(
    self, arc_file: Path, arc_name: str
) -> List[ChapterInfo]:
    """Parse chapter rows from ARC.md — frontmatter-first with table fallback.

    Note (A4 critique): ChapterInfo.work_items is INFORMATIONAL only
    (from ARC.md). For authoritative chapter membership, use
    get_work(chapter_id) which scans WORK.md files.
    """
    try:
        from arc_frontmatter import get_chapters
    except ImportError:
        from .arc_frontmatter import get_chapters
    raw = get_chapters(arc_file)
    chapters = []
    for ch in raw:
        # Extract WORK-NNN IDs from the work_items list entries
        work_str = " ".join(ch.get("work_items", []))
        work_items = re.findall(r"WORK-\d+", work_str)
        chapters.append(
            ChapterInfo(
                id=ch["id"],
                title=ch["title"],
                work_items=work_items,
                status=ch["status"],
                arc=arc_name,
            )
        )
    return chapters
```

**Diff:**
```diff
 def _parse_arc_metadata(self, arc_file: Path) -> Dict[str, str]:
-    """Extract theme and status from ARC.md definition section."""
-    content = arc_file.read_text(encoding="utf-8")
-    theme = ""
-    status = ""
-    for line in content.split("\n"):
-        if line.startswith("**Theme:**"):
-            theme = line.split("**Theme:**", 1)[1].strip()
-        elif line.startswith("**Status:**"):
-            status = line.split("**Status:**", 1)[1].strip()
-    return {"theme": theme, "status": status}
+    """Extract theme and status from ARC.md — frontmatter-first with fallback."""
+    try:
+        from arc_frontmatter import get_arc_metadata
+    except ImportError:
+        from .arc_frontmatter import get_arc_metadata
+    return get_arc_metadata(arc_file)

 def _parse_arc_chapters(self, arc_file: Path, arc_name: str) -> List[ChapterInfo]:
-    content = arc_file.read_text(encoding="utf-8")
-    chapters = []
-    for line in content.split("\n"):
-        if re.match(r"\s*\|\s*CH-\d+", line):
-            cells = [c.strip() for c in line.split("|") if c.strip()]
-            if len(cells) >= 6:
-                ch_id = cells[0]
-                title = cells[1]
-                work_str = cells[2]
-                status = cells[-1]
-                work_items = re.findall(r"WORK-\d+", work_str)
-                chapters.append(ChapterInfo(id=ch_id, title=title,
-                    work_items=work_items, status=status, arc=arc_name))
-    return chapters
+    try:
+        from arc_frontmatter import get_chapters
+    except ImportError:
+        from .arc_frontmatter import get_chapters
+    raw = get_chapters(arc_file)
+    chapters = []
+    for ch in raw:
+        work_str = " ".join(ch.get("work_items", []))
+        work_items = re.findall(r"WORK-\d+", work_str)
+        chapters.append(ChapterInfo(id=ch["id"], title=ch["title"],
+            work_items=work_items, status=ch["status"], arc=arc_name))
+    return chapters
```

#### File 4 (MODIFY): `.claude/haios/lib/status_propagator.py`

**Location:** Lines 247-326 — `update_arc_chapter_status()` and `is_arc_complete()`

**Current Code:**
```python
def update_arc_chapter_status(self, arc_name, chapter_id, new_status):
    # ... (haios.yaml loading, arc_file resolution) ...
    content = arc_file.read_text(encoding="utf-8")
    lines = content.split("\n")
    found = False
    for i, line in enumerate(lines):
        if re.match(rf"\s*\|\s*{re.escape(chapter_id)}\s*\|", line):
            cells = line.split("|")
            for j in range(len(cells) - 1, -1, -1):
                if cells[j].strip():
                    cells[j] = f" {new_status} "
                    break
            lines[i] = "|".join(cells)
            found = True
            break
    if not found:
        return {"updated": False, "reason": "chapter_row_not_found"}
    arc_file.write_text("\n".join(lines), encoding="utf-8")
    return {"updated": True}

def is_arc_complete(self, arc_name):
    # ... (haios.yaml loading, arc_file resolution) ...
    content = arc_file.read_text(encoding="utf-8")
    statuses = []
    for line in content.split("\n"):
        if re.match(r"\s*\|\s*CH-\d+", line):
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if cells:
                statuses.append(cells[-1])
    if not statuses:
        return False
    return all(s.lower() in ARC_COMPLETE_STATUSES for s in statuses)
```

**Target Code:**
```python
def _resolve_arc_file(self, arc_name: str):
    """Shared helper: resolve ARC.md path from haios.yaml config."""
    haios_path = self._base_path / ".claude" / "haios" / "config" / "haios.yaml"
    if not haios_path.exists():
        return None
    haios_config = yaml.safe_load(haios_path.read_text(encoding="utf-8"))
    arcs_dir = haios_config.get("epoch", {}).get("arcs_dir", "")
    arc_file = self._base_path / arcs_dir / arc_name / "ARC.md"
    return arc_file if arc_file.exists() else None

def update_arc_chapter_status(self, arc_name, chapter_id, new_status):
    """A4 critique fix: frontmatter-first with table surgery fallback for legacy files."""
    try:
        from arc_frontmatter import update_chapter_in_frontmatter
    except ImportError:
        from .arc_frontmatter import update_chapter_in_frontmatter

    arc_file = self._resolve_arc_file(arc_name)
    if arc_file is None:
        return {"updated": False, "reason": "arc_file_not_found"}

    # Try frontmatter update first
    result = update_chapter_in_frontmatter(arc_file, chapter_id, new_status)
    if result:
        return {"updated": True}

    # Fallback: legacy table surgery for unmigrated files
    content = arc_file.read_text(encoding="utf-8")
    lines = content.split("\n")
    found = False
    for i, line in enumerate(lines):
        if re.match(rf"\s*\|\s*{re.escape(chapter_id)}\s*\|", line):
            cells = line.split("|")
            for j in range(len(cells) - 1, -1, -1):
                if cells[j].strip():
                    cells[j] = f" {new_status} "
                    break
            lines[i] = "|".join(cells)
            found = True
            break
    if not found:
        return {"updated": False, "reason": "chapter_row_not_found"}
    arc_file.write_text("\n".join(lines), encoding="utf-8")
    return {"updated": True}

def is_arc_complete(self, arc_name):
    try:
        from arc_frontmatter import get_chapters
    except ImportError:
        from .arc_frontmatter import get_chapters

    arc_file = self._resolve_arc_file(arc_name)
    if arc_file is None:
        return False

    chapters = get_chapters(arc_file)
    if not chapters:
        return False
    return all(ch["status"].lower() in ARC_COMPLETE_STATUSES for ch in chapters)
```

**Note on _resolve_arc_file:** The haios.yaml loading logic is currently duplicated inline in both methods (lines ~264-271 and ~308-315). Extract to `_resolve_arc_file()` helper as part of this change. Verify the method does not already exist before adding.

#### File 5 (MODIFY): `.claude/haios/lib/epoch_loader.py`

**Location:** Lines 91-107 — `_extract_chapter_table()`

**Current Code:**
```python
def _extract_chapter_table(self, content: str) -> List[Dict]:
    """Extract chapter status rows from arc markdown tables."""
    chapters = []
    for line in content.split("\n"):
        line_s = line.strip()
        if not line_s.startswith("|"):
            continue
        if "CH-ID" in line_s or "---" in line_s:
            continue
        cells = [c.strip() for c in line_s.split("|") if c.strip()]
        if len(cells) >= 4 and cells[0].startswith("CH-"):
            chapters.append({
                "id": cells[0],
                "title": cells[1],
                "status": cells[-1],
            })
    return chapters
```

**Target Code:**
```python
def _extract_chapter_table(self, content: str, arc_path: Optional[Path] = None) -> List[Dict]:
    """Extract chapter status rows — frontmatter-first if arc_path given, else table parse."""
    if arc_path is not None and arc_path.exists():
        try:
            from arc_frontmatter import get_chapters
        except ImportError:
            from .arc_frontmatter import get_chapters
        chapters = get_chapters(arc_path)
        if chapters:
            return [{"id": ch["id"], "title": ch["title"], "status": ch["status"]} for ch in chapters]

    # Fallback: inline table parsing (for callers that pass content only)
    chapters = []
    for line in content.split("\n"):
        line_s = line.strip()
        if not line_s.startswith("|"):
            continue
        if "CH-ID" in line_s or "---" in line_s:
            continue
        cells = [c.strip() for c in line_s.split("|") if c.strip()]
        if len(cells) >= 4 and cells[0].startswith("CH-"):
            chapters.append({
                "id": cells[0],
                "title": cells[1],
                "status": cells[-1],
            })
    return chapters
```

**Note on caller:** Find where `_extract_chapter_table(content)` is called in `extract()` and pass `arc_path` alongside. Read lines 109-180 of epoch_loader.py to identify the call site before making this change.

#### File 6 (MODIFY): `.claude/haios/lib/epoch_validator.py`

**Location:** Lines 194-211 — inline table row parsing inside `validate_epoch_status()`

**Current Code:**
```python
# Parse table rows with CH- prefix (arc chapter tables)
for line in active_content.split("\n"):
    line_stripped = line.strip()
    if not line_stripped.startswith("|"):
        continue
    if "CH-ID" in line_stripped or "---" in line_stripped:
        continue
    work_ids = re.findall(r"WORK-\d{3}", line_stripped)
    if not work_ids:
        continue
    cells = [c.strip() for c in line_stripped.split("|") if c.strip()]
    if len(cells) < 4:
        continue
    epoch_status = cells[-1].lower()
    for work_id in work_ids:
        # ... drift detection logic ...
```

**Target Code:**
```python
# Read arc chapter data via arc_frontmatter if arc_file is resolvable,
# else fall back to inline table parsing from EPOCH.md content
try:
    from arc_frontmatter import get_chapters as get_arc_chapters
    _arc_fm_available = True
except ImportError:
    try:
        from .arc_frontmatter import get_chapters as get_arc_chapters
        _arc_fm_available = True
    except ImportError:
        _arc_fm_available = False

# Resolve arc files from arcs_dir config
arc_chapters_map = {}  # chapter_id -> {"work_items": [...], "status": str}
if _arc_fm_available and self._arcs_dir:
    for arc_dir in self._arcs_dir.iterdir():
        arc_file = arc_dir / "ARC.md"
        if arc_file.exists():
            for ch in get_arc_chapters(arc_file):
                arc_chapters_map[ch["id"]] = ch

# Process: prefer arc_frontmatter data, fall back to EPOCH.md table parsing
if arc_chapters_map:
    for ch_id, ch_data in arc_chapters_map.items():
        work_ids = re.findall(r"WORK-\d{3}", " ".join(ch_data.get("work_items", [])))
        epoch_status = ch_data["status"].lower()
        for work_id in work_ids:
            # ... drift detection logic (same as current) ...
else:
    # Legacy fallback: parse EPOCH.md table rows directly
    for line in active_content.split("\n"):
        # ... existing table parsing logic unchanged ...
```

**A5 critique fix — arcs_dir derivation:** EpochValidator has `self._haios_config` and `self._base_path` but no `_arcs_dir` attribute. Derive it inline:
```python
arcs_dir_str = self._haios_config.get("epoch", {}).get("arcs_dir", "")
arcs_dir = self._base_path / arcs_dir_str if arcs_dir_str else None
```
Replace `self._arcs_dir` in the target code above with this derivation. DO agent must read lines 55-77 of epoch_validator.py to confirm these attributes exist.

#### File 7 (MODIFY): `.claude/haios/lib/dod_validation.py`

**Location:** Lines 362 and 446 — `_parse_markdown_field(content, "Status")` calls for ARC.md status

**Current Code (validate_arc_dod, lines 360-362):**
```python
for ch_file in chapter_files:
    content = ch_file.read_text(encoding="utf-8")
    status = _parse_markdown_field(content, "Status") or "Unknown"
```

**Note:** `validate_arc_dod` reads CHAPTER.md files (ch_file), not ARC.md — this already uses chapter_frontmatter patterns from WORK-244. Review whether this function needs changes at all. The real target is `validate_epoch_dod` which reads ARC.md files.

**Current Code (validate_epoch_dod, lines 443-446):**
```python
for arc_file in arc_files:
    arc_name = arc_file.parent.name
    content = arc_file.read_text(encoding="utf-8")
    status = _parse_markdown_field(content, "Status") or "Unknown"
```

**Target Code (validate_epoch_dod):**
```python
try:
    from arc_frontmatter import get_arc_status
except ImportError:
    from .arc_frontmatter import get_arc_status

for arc_file in arc_files:
    arc_name = arc_file.parent.name
    status = get_arc_status(arc_file) or "Unknown"
    # rest unchanged (deferred check, incomplete list)
```

**Diff (validate_epoch_dod section):**
```diff
+try:
+    from arc_frontmatter import get_arc_status
+except ImportError:
+    from .arc_frontmatter import get_arc_status
+
 for arc_file in arc_files:
     arc_name = arc_file.parent.name
-    content = arc_file.read_text(encoding="utf-8")
-    status = _parse_markdown_field(content, "Status") or "Unknown"
+    status = get_arc_status(arc_file) or "Unknown"
```

### Call Chain

```
close_work_cycle ARCHIVE phase
    |
    +-> StatusPropagator.propagate("WORK-XXX")
            |
            +-> update_arc_chapter_status(arc, chapter_id, "Complete")
                    |
                    +-> update_chapter_in_frontmatter(arc_file, chapter_id, "Complete")
                            |
                            +-> parse_arc_frontmatter(arc_file)   # read
                            +-> _write_frontmatter(arc_file, fm)  # write
            |
            +-> is_arc_complete(arc_name)
                    |
                    +-> get_chapters(arc_file)    # read chapters list

HierarchyQueryEngine.get_arcs()
    |
    +-> _parse_arc_metadata(arc_file)    -> get_arc_metadata(arc_file)
    +-> _parse_arc_chapters(arc_file, arc_name) -> get_chapters(arc_file)

EpochLoader.extract()
    |
    +-> _extract_chapter_table(content, arc_path) -> get_chapters(arc_path)

EpochValidator.validate_epoch_status()
    |
    +-> get_arc_chapters(arc_file)   # from arc_frontmatter

dod_validation.validate_epoch_dod()
    |
    +-> get_arc_status(arc_file)    # from arc_frontmatter
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| New `arc_frontmatter.py` vs extending `chapter_frontmatter.py` | New module | ARC.md schema differs: chapters list has 6 fields each vs CHAPTER.md work_items with 4. Separate concerns; consumers import from named module. |
| Frontmatter-first with backward-compatible fallback | Yes (L3.6) | 34 ARC.md files span multiple epochs; migration is best-effort; runtime must not break on unmigrated files. Same pattern as chapter_frontmatter.py. |
| Import pattern: try/except ImportError | Matches sibling chapter_frontmatter.py callers | Consistent with existing modules; works both as standalone lib and when called from modules/ context. |
| `_resolve_arc_file()` helper in status_propagator | Extract shared haios.yaml loading | The haios.yaml load+resolve sequence is duplicated in update_arc_chapter_status and is_arc_complete. Extracting removes the duplication. |
| `_extract_chapter_table(arc_path=None)` signature | Optional arc_path parameter | Preserves backward compat for callers passing content only; adds frontmatter path when arc_path known. |
| epoch_validator fallback to EPOCH.md table parsing | Keep legacy path | epoch_validator._arcs_dir may not be available; safe degradation avoids breaking drift detection if arc_frontmatter unavailable. |
| migrate all 34 ARC.md files | Yes, all epochs | Consistent format removes mixed-format maintenance burden. Idempotent script makes re-runs safe. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| ARC.md has no chapters table | `get_chapters()` returns `[]`; `is_arc_complete()` returns `False` | Test 7 |
| ARC.md chapter has "New" as work_items cell | Parsed as `["New"]`; `re.findall(r"WORK-\d+", ...)` returns `[]` — no false work IDs | Test 16 |
| update_chapter_in_frontmatter on legacy file | Returns `False`; caller falls back to legacy table surgery (status_propagator keeps old code path until all files migrated) | Test 12 |
| `---` in markdown body (multiple separators) | `content.split("---", 2)` with maxsplit=2 preserves body; `_write_frontmatter` uses same pattern as chapter_frontmatter.py Test 18 | Test 13 |
| ARC.md not found | `migrate_file()` returns `{"error": "not_found"}`; `_resolve_arc_file()` returns None | Test 14 |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| status_propagator fallback: legacy ARC.md after migration | M | update_chapter_in_frontmatter returns False for legacy files. Keep legacy table-surgery code path commented-out as fallback until verified all 34 files migrated. After Ground Truth verification confirms 0 legacy files remain, remove fallback. |
| epoch_validator arcs_dir not injectable | M | Read epoch_validator __init__ before implementing. If no _arcs_dir attribute, derive from haios.yaml path or use `self._epoch_path.parent / "arcs"`. |
| `_extract_chapter_table` callers in epoch_loader | M | Read epoch_loader lines 109-180 to find all call sites before changing signature. If only one call site, add arc_path arg there. |
| YAML dump key ordering changes ARC.md readability | L | `sort_keys=False` preserves field order (same as chapter_frontmatter.py). |
| Migration corrupts ARC.md with invalid YAML | H | Test 13 verifies body preserved. Run --dry-run first. Full pytest suite after migration before commit. |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Create `tests/test_arc_frontmatter.py` with all 22 tests (19 original + 3 critique-driven: 7a, 7b, 7c). Use `ARC_INFRA_LEGACY_CONTENT` fixture matching actual E2_8 infrastructure ARC.md content. Follow `test_chapter_frontmatter.py` structure (fixtures at top, grouped test classes).
- **output:** `tests/test_arc_frontmatter.py` exists, all 22 tests fail with ImportError or AttributeError
- **verify:** `pytest tests/test_arc_frontmatter.py -v 2>&1 | grep -c "FAILED\|ERROR"` equals 19

### Step 2: Implement arc_frontmatter.py (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (NEW)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Create `.claude/haios/lib/arc_frontmatter.py` from Layer 1 Design File 1 spec exactly
- **output:** Tests 1-12 pass (parse, get_*, update, get_exit_criteria functions)
- **verify:** `pytest tests/test_arc_frontmatter.py::TestParseArcFrontmatter tests/test_arc_frontmatter.py::TestGetArcStatus tests/test_arc_frontmatter.py::TestGetChapters tests/test_arc_frontmatter.py::TestGetExitCriteria tests/test_arc_frontmatter.py::TestUpdateChapter -v` exits 0

### Step 3: Implement migrate_arc_frontmatter.py
- **spec_ref:** Layer 1 > Design > File 2 (NEW)
- **input:** Step 2 complete (arc_frontmatter.py green)
- **action:** Create `.claude/haios/lib/migrate_arc_frontmatter.py` from Layer 1 Design File 2 spec exactly
- **output:** Tests 13-16 pass (migrate_file, build_arc_frontmatter)
- **verify:** `pytest tests/test_arc_frontmatter.py::TestMigration tests/test_arc_frontmatter.py::TestBuildArcFrontmatter -v` exits 0

### Step 4: Modify hierarchy_engine.py
- **spec_ref:** Layer 1 > Design > File 3 (MODIFY)
- **input:** Step 3 complete; arc_frontmatter.py importable
- **action:** Replace `_parse_arc_metadata` and `_parse_arc_chapters` per Layer 1 Design File 3 diff
- **output:** Test 17 passes; existing hierarchy_engine tests still pass
- **verify:** `pytest tests/test_arc_frontmatter.py::TestHierarchyEngineIntegration -v` exits 0; `pytest tests/test_hierarchy_engine.py -v` exits 0

### Step 5: Modify status_propagator.py
- **spec_ref:** Layer 1 > Design > File 4 (MODIFY)
- **input:** Step 4 complete
- **action:** (a) Add `_resolve_arc_file()` helper; (b) Replace `update_arc_chapter_status` table surgery with `update_chapter_in_frontmatter` call; (c) Replace `is_arc_complete` table parsing with `get_chapters` call
- **output:** Test 18 passes; existing status_propagator tests still pass
- **verify:** `pytest tests/test_arc_frontmatter.py::TestStatusPropagatorIntegration -v` exits 0; `pytest tests/test_status_propagator.py -v` exits 0

### Step 6: Modify epoch_loader.py
- **spec_ref:** Layer 1 > Design > File 5 (MODIFY)
- **input:** Step 5 complete
- **action:** Update `_extract_chapter_table` signature to accept optional `arc_path`; update call site in `extract()` to pass arc_path; add frontmatter-first path
- **output:** epoch_loader tests still pass
- **verify:** `pytest tests/test_epoch_loader.py -v` exits 0 (no regressions)

### Step 7: Modify epoch_validator.py
- **spec_ref:** Layer 1 > Design > File 6 (MODIFY)
- **input:** Step 6 complete; READ epoch_validator.py lines 1-100 first to verify _arcs_dir availability
- **action:** Add arc_frontmatter import; replace inline table parsing with get_arc_chapters when arc_files resolvable; preserve fallback
- **output:** epoch_validator tests still pass
- **verify:** `pytest tests/test_epoch_validator.py -v` exits 0

### Step 8: Modify dod_validation.py
- **spec_ref:** Layer 1 > Design > File 7 (MODIFY)
- **input:** Step 7 complete
- **action:** Add `from arc_frontmatter import get_arc_status` in `validate_epoch_dod`; replace `_parse_markdown_field(content, "Status")` for ARC.md files with `get_arc_status(arc_file)`
- **output:** Test 22 passes; dod_validation tests still pass
- **verify:** `pytest tests/test_arc_frontmatter.py::TestDodValidationIntegration -v` exits 0; `pytest tests/test_dod_validation.py -v` exits 0

### Step 9: Run Migration on All 34 ARC.md Files
- **spec_ref:** Layer 1 > Design > File 2 (NEW) — `migrate_all()`
- **input:** Steps 2-8 complete (arc_frontmatter.py and consumers working)
- **action:** Run `python .claude/haios/lib/migrate_arc_frontmatter.py --dry-run` first; review output; run without --dry-run
- **output:** 34 ARC.md files have YAML frontmatter prepended; migration script prints "34 migrated, 0 skipped, 0 errors"
- **verify:** `python -c "from pathlib import Path; files = list(Path('.claude/haios/epochs').rglob('ARC.md')); no_fm = [f for f in files if not f.read_text().lstrip().startswith('---')]; print(f'{len(no_fm)} files without frontmatter')"` prints `0 files without frontmatter`

### Step 10: Full Test Suite Verification
- **spec_ref:** Ground Truth Verification > Tests
- **input:** All prior steps complete
- **action:** Run full pytest suite; verify no new failures
- **output:** All existing tests pass; 22 new tests pass
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows 0 failures; new test count = prior count + 19

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_arc_frontmatter.py -v` | 22 passed, 0 failed |
| `pytest tests/test_hierarchy_engine.py -v` | 0 new failures vs pre-WORK-245 baseline |
| `pytest tests/test_status_propagator.py -v` | 0 new failures vs pre-WORK-245 baseline |
| `pytest tests/test_epoch_loader.py -v` | 0 new failures vs pre-WORK-245 baseline |
| `pytest tests/test_epoch_validator.py -v` | 0 new failures vs pre-WORK-245 baseline |
| `pytest tests/test_dod_validation.py -v` | 0 new failures vs pre-WORK-245 baseline |
| `pytest tests/ -v` | 0 new failures vs pre-WORK-245 baseline |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| ARC.md files have YAML frontmatter | `python -c "from pathlib import Path; files=list(Path('.claude/haios/epochs').rglob('ARC.md')); no_fm=[f for f in files if not f.read_text().lstrip().startswith('---')]; print(len(no_fm))"` | `0` |
| arc_frontmatter.py created | `test -f .claude/haios/lib/arc_frontmatter.py && echo exists` | `exists` |
| migrate_arc_frontmatter.py created | `test -f .claude/haios/lib/migrate_arc_frontmatter.py && echo exists` | `exists` |
| hierarchy_engine uses arc_frontmatter | `grep "from arc_frontmatter import" .claude/haios/lib/hierarchy_engine.py` | 1+ match |
| status_propagator uses arc_frontmatter | `grep "from arc_frontmatter import" .claude/haios/lib/status_propagator.py` | 1+ match |
| epoch_loader uses arc_frontmatter | `grep "from arc_frontmatter import" .claude/haios/lib/epoch_loader.py` | 1+ match |
| epoch_validator uses arc_frontmatter | `grep "from arc_frontmatter import" .claude/haios/lib/epoch_validator.py` | 1+ match |
| dod_validation uses arc_frontmatter | `grep "from arc_frontmatter import" .claude/haios/lib/dod_validation.py` | 1+ match |
| 4 duplicate table parsers eliminated | `grep -c "re.match.*CH-\\\d" .claude/haios/lib/hierarchy_engine.py .claude/haios/lib/status_propagator.py .claude/haios/lib/epoch_loader.py .claude/haios/lib/epoch_validator.py` | All counts 0 (moved to arc_frontmatter.py) |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| No stale pipe-split chapter parsing | `grep -n "split.*\|.*CH-" .claude/haios/lib/hierarchy_engine.py .claude/haios/lib/status_propagator.py .claude/haios/lib/epoch_loader.py .claude/haios/lib/epoch_validator.py` | 0 matches |
| arc_frontmatter importable from lib | `python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from arc_frontmatter import parse_arc_frontmatter, get_chapters, get_arc_status, update_chapter_in_frontmatter; print('ok')"` | `ok` |
| migrate_arc_frontmatter importable | `python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from migrate_arc_frontmatter import migrate_all, build_arc_frontmatter; print('ok')"` | `ok` |
| Migration idempotent | Run `python .claude/haios/lib/migrate_arc_frontmatter.py` twice; second run output | `34 migrated, 0 skipped` then `0 migrated, 34 skipped` |

### Completion Criteria (DoD)

- [ ] All tests pass (19 new + 0 regressions in existing suite)
- [ ] All WORK.md deliverables verified (table above)
- [ ] arc_frontmatter.py has runtime consumers (hierarchy_engine, status_propagator, epoch_loader, epoch_validator, dod_validation)
- [ ] 34 ARC.md files migrated (0 files without frontmatter)
- [ ] 4 duplicate table parsers eliminated from consumers
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `docs/work/active/WORK-244/plans/PLAN.md` — Phase 1 plan (CHAPTER.md migration, same pattern)
- `docs/work/active/WORK-244/WORK.md` — Phase 1 work item
- `.claude/haios/lib/chapter_frontmatter.py` — sibling module (exact pattern to follow)
- `.claude/haios/lib/migrate_chapter_frontmatter.py` — sibling migration script (exact pattern to follow)
- `tests/test_chapter_frontmatter.py` — sibling test file (structure to follow)
- Memory: 89402-89407 (WORK-240 investigation findings), 87137 (propagator drift)

---
