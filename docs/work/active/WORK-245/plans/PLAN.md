---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-03-07
backlog_id: WORK-245
title: "ARC.md YAML Frontmatter Migration"
author: Hephaestus
lifecycle_phase: plan
session: 470
generated: 2026-03-07
last_updated: 2026-03-07T14:30:00

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

Migrate all ARC.md files from bold-markdown field parsing to YAML frontmatter, eliminating 4 duplicate chapter-table parsers across hierarchy_engine, status_propagator, epoch_loader, and epoch_validator by routing all reads and writes through a new `arc_frontmatter.py` module.

---

## Open Decisions

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Multi-column table support in fallback | 4-col only, 4+5+6 col | 4+5+6 column branching | ARC.md files span E2–E2.8 with 3 distinct table formats; failing on older epochs would break migration |
| Status cleaning during migration | Raw copy, strip bold+session annotations | Strip `**...**` and `(S\d+...)` suffixes | Prevents `is_arc_complete` silent failures where `**Complete** (S335)` != `"Complete"` |
| Consumer fallback strategy | No fallback (frontmatter required), frontmatter-first with fallback | Frontmatter-first with backward-compatible fallback | L3.6 graceful degradation; not all ARC.md files may be migrated at once |
| epoch_validator guard | Use frontmatter for all paths, use legacy when work_statuses injected | Legacy path when `work_statuses` injected | Test mode injects work_statuses directly — frontmatter path would require real ARC.md files on disk |

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
| `.claude/haios/lib/README.md` | documents arc_frontmatter and migrate_arc_frontmatter | 99-112 | UPDATE (add rows for new modules) |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_arc_frontmatter.py` | CREATE | 22 tests covering arc_frontmatter.py and migrate_arc_frontmatter.py |
| `tests/test_hierarchy_engine.py` | EXISTING | No changes needed — hierarchy_engine delegates to arc_frontmatter |
| `tests/test_epoch_validator.py` | EXISTING | No changes needed — guard preserves existing test behavior |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 3 | arc_frontmatter.py, migrate_arc_frontmatter.py, test_arc_frontmatter.py |
| Files to modify | 6 | 5 consumers + README.md |
| Tests to write | 22 | test_arc_frontmatter.py (Tests 1–19, with sub-tests 7a, 7b, 7c) |
| Total blast radius | 9 | 3 creates + 6 modifies |

---

## Layer 1: Specification

### Current State

The 4 consumers each have their own independent chapter-table parsing logic:

```python
# hierarchy_engine.py lines 282-318 — _parse_arc_metadata and _parse_arc_chapters
# Before WORK-245: both used inline bold-markdown and >= 6 column table parsing

def _parse_arc_metadata(self, arc_file: Path) -> Dict[str, str]:
    content = arc_file.read_text(encoding="utf-8")
    theme = ""
    status = ""
    for line in content.split("\n"):
        if line.startswith("**Theme:**"):
            theme = line.split("**Theme:**", 1)[1].strip()
        elif line.startswith("**Status:**"):
            status = line.split("**Status:**", 1)[1].strip()
    return {"theme": theme, "status": status}

def _parse_arc_chapters(self, arc_file: Path, arc_name: str) -> List[ChapterInfo]:
    content = arc_file.read_text(encoding="utf-8")
    chapters = []
    for line in content.split("\n"):
        if re.match(r"\s*\|\s*CH-\d+", line):
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) >= 6:
                # Only handles 6-column tables -- silently drops 4- and 5-column formats
                ...
```

```python
# status_propagator.py lines 257-302 — update_arc_chapter_status
# Before WORK-245: pure regex table surgery with no frontmatter path

def update_arc_chapter_status(self, arc_name, chapter_id, new_status) -> dict:
    arc_file = self._resolve_arc_file(arc_name)
    content = arc_file.read_text(encoding="utf-8")
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if re.match(rf"\s*\|\s*{re.escape(chapter_id)}\s*\|", line):
            cells = line.split("|")
            for j in range(len(cells) - 1, -1, -1):
                if cells[j].strip():
                    cells[j] = f" {new_status} "
                    break
            lines[i] = "|".join(cells)
            break
    arc_file.write_text("\n".join(lines), encoding="utf-8")
```

```python
# epoch_loader.py lines 91-117 — _extract_chapter_table
# Before WORK-245: inline table parsing, no frontmatter path
def _extract_chapter_table(self, content: str, arc_path=None) -> List[Dict]:
    chapters = []
    for line in content.split("\n"):
        line_s = line.strip()
        if not line_s.startswith("|"):
            continue
        if "CH-ID" in line_s or "---" in line_s:
            continue
        cells = [c.strip() for c in line_s.split("|") if c.strip()]
        if len(cells) >= 4 and cells[0].startswith("CH-"):
            chapters.append({"id": cells[0], "title": cells[1], "status": cells[-1]})
    return chapters
```

```python
# epoch_validator.py lines 194-274 — validate_epoch_status
# Before WORK-245: inline EPOCH.md table parsing only, no arc_frontmatter path
```

```python
# dod_validation.py lines 362 and 441-461 — validate_arc_dod, validate_epoch_dod
# Before WORK-245: uses _parse_markdown_field for **Status:** bold-markdown
def validate_arc_dod(arc, base_path=None, epoch_dir=".claude/haios/epochs/E2_5"):
    ...
    for ch_file in chapter_files:
        content = ch_file.read_text(encoding="utf-8")
        status = _parse_markdown_field(content, "Status") or "Unknown"
```

**Behavior:** Each consumer independently parses ARC.md using different methods. No shared abstraction. Multi-column table variants handled inconsistently (hierarchy_engine silently ignores 4- and 5-column tables).

**Problem:** 4 duplicate parsers that drift independently. `is_arc_complete` fails silently when status has bold formatting `**Complete** (S335)`. Chapter table updates via regex table surgery are fragile and error-prone.

---

### Desired State

All ARC.md reads and writes route through `arc_frontmatter.py` with graceful fallback:

```python
# .claude/haios/lib/arc_frontmatter.py — complete public API

def parse_arc_frontmatter(path: Path) -> Optional[dict]:
    """Returns frontmatter dict if --- delimiters found, else None."""

def get_arc_status(path: Path) -> Optional[str]:
    """Frontmatter status field, fallback to **Status:** bold-markdown."""

def get_arc_metadata(path: Path) -> Dict[str, str]:
    """Returns {"theme": str, "status": str}. Frontmatter-first."""

def get_chapters(path: Path) -> List[dict]:
    """Returns chapters list. Frontmatter-first, fallback to 4/5/6-column tables."""
    # Each chapter dict: {id, title, work_items, requirements, dependencies, status}

def get_exit_criteria(path: Path) -> Optional[Dict]:
    """Returns exit criteria. Frontmatter-first, fallback to checkbox parsing."""
    # Handles: ## Exit Criteria, ## Arc Completion Criteria, ## Completion Criteria

def update_chapter_in_frontmatter(path: Path, chapter_id: str, new_status: str) -> bool:
    """Updates chapter status in frontmatter. Returns False if no frontmatter."""

def _write_frontmatter(path: Path, fm: dict) -> None:
    """Rewrites ARC.md with updated frontmatter, preserving markdown body."""
```

```python
# hierarchy_engine.py — _parse_arc_metadata and _parse_arc_chapters delegate to arc_frontmatter
def _parse_arc_metadata(self, arc_file: Path) -> Dict[str, str]:
    try:
        from arc_frontmatter import get_arc_metadata
    except ImportError:
        from .arc_frontmatter import get_arc_metadata
    return get_arc_metadata(arc_file)

def _parse_arc_chapters(self, arc_file: Path, arc_name: str) -> List[ChapterInfo]:
    try:
        from arc_frontmatter import get_chapters
    except ImportError:
        from .arc_frontmatter import get_chapters
    raw = get_chapters(arc_file)
    # ... convert to ChapterInfo objects
```

```python
# status_propagator.py — update_arc_chapter_status: frontmatter-first, table surgery fallback
def update_arc_chapter_status(self, arc_name, chapter_id, new_status) -> dict:
    try:
        from arc_frontmatter import update_chapter_in_frontmatter
    except ImportError:
        from .arc_frontmatter import update_chapter_in_frontmatter
    arc_file = self._resolve_arc_file(arc_name)
    result = update_chapter_in_frontmatter(arc_file, chapter_id, new_status)
    if result:
        return {"updated": True}
    # Fallback: table surgery for unmigrated files
    ...

# is_arc_complete: delegates to arc_frontmatter.get_chapters
def is_arc_complete(self, arc_name) -> bool:
    try:
        from arc_frontmatter import get_chapters
    except ImportError:
        from .arc_frontmatter import get_chapters
    arc_file = self._resolve_arc_file(arc_name)
    chapters = get_chapters(arc_file)
    return all(ch["status"].lower() in ARC_COMPLETE_STATUSES for ch in chapters)
```

```python
# epoch_loader.py — _extract_chapter_table: frontmatter-first when arc_path provided
def _extract_chapter_table(self, content: str, arc_path=None) -> List[Dict]:
    if arc_path is not None and arc_path.exists():
        try:
            from arc_frontmatter import get_chapters
        except ImportError:
            from .arc_frontmatter import get_chapters
        chapters = get_chapters(arc_path)
        if chapters:
            return [{"id": ch["id"], "title": ch["title"], "status": ch["status"]} for ch in chapters]
    # Fallback: inline table parsing
```

```python
# epoch_validator.py — validate_epoch_status: frontmatter path for production,
#   legacy EPOCH.md table parsing when work_statuses injected (test mode)
_use_frontmatter = (_arc_fm_available and arcs_dir and arcs_dir.exists()
                    and self._work_statuses is None)
```

```python
# dod_validation.py — validate_epoch_dod: uses arc_frontmatter.get_arc_status
try:
    from arc_frontmatter import get_arc_status
except ImportError:
    from .arc_frontmatter import get_arc_status
# ...
status = get_arc_status(arc_file) or "Unknown"
```

**Behavior:** Single shared `arc_frontmatter.py` abstraction. All consumers use frontmatter when available, fall back to legacy parsing when not. Migration script converts legacy files idempotently.

**Result:** 4 duplicate parsers eliminated. `_parse_markdown_field` no longer called for ARC.md status. Chapter status updates are dict writes, not regex table surgery. Older ARC.md files without frontmatter continue to work unchanged.

---

### Tests

All 22 tests are defined in `tests/test_arc_frontmatter.py`. Tests are organized by module and function.

#### Test 1: parse_arc_frontmatter returns dict when frontmatter present
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestParseArcFrontmatter::test_parse_arc_frontmatter_returns_dict()`
- **setup:** Write ARC.md with YAML frontmatter `{id: infrastructure, epoch: E2.8, status: Planning}`
- **assertion:** `parse_arc_frontmatter(path)` returns dict with `id == "infrastructure"`

#### Test 2: parse_arc_frontmatter returns None for legacy format
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestParseArcFrontmatter::test_parse_arc_frontmatter_returns_none_for_legacy()`
- **setup:** Write ARC.md in bold-markdown format (no --- delimiters)
- **assertion:** `parse_arc_frontmatter(path)` returns None

#### Test 3: get_arc_status reads from frontmatter
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestGetArcStatus::test_get_arc_status_from_frontmatter()`
- **setup:** Write ARC.md with frontmatter `status: Active`
- **assertion:** `get_arc_status(path) == "Active"`

#### Test 4: get_arc_status falls back to bold-markdown
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestGetArcStatus::test_get_arc_status_fallback()`
- **setup:** Write ARC.md with `**Status:** Planning` (no frontmatter)
- **assertion:** `get_arc_status(path) == "Planning"`

#### Test 5: get_arc_metadata returns theme and status from frontmatter
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestGetArcMetadata::test_get_arc_metadata_from_frontmatter()`
- **setup:** Write ARC.md with `theme: "Fix what's broken"` and `status: Planning`
- **assertion:** `result["theme"] == "Fix what's broken"` and `result["status"] == "Planning"`

#### Test 6: get_chapters reads from frontmatter chapters list
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestGetChapters::test_get_chapters_from_frontmatter()`
- **setup:** Write ARC.md with frontmatter chapters list (CH-065, CH-067)
- **assertion:** `len(result) == 2`, `result[0]["id"] == "CH-065"`, `result[0]["status"] == "Complete"`

#### Test 7: get_chapters falls back to 6-column table
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestGetChapters::test_get_chapters_fallback_6col_table()`
- **setup:** Legacy ARC.md with `| CH-ID | Title | Work Items | Requirements | Dependencies | Status |` table
- **assertion:** Chapter parsed correctly with all 6 fields

#### Test 7a: get_chapters falls back to 4-column table (E2 era)
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestGetChapters::test_get_chapters_fallback_4col_table()`
- **setup:** Legacy ARC.md with `| Chapter | Name | Status | Purpose |` 4-col table
- **assertion:** `result[0]["id"] == "CH-001"`, `result[0]["work_items"] == []`

#### Test 7b: get_chapters falls back to 5-column table
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestGetChapters::test_get_chapters_fallback_5col_table()`
- **setup:** Legacy ARC.md with `| CH-ID | Title | Requirements | Dependencies | Status |` 5-col table
- **assertion:** `result[0]["requirements"] == ["REQ-FEEDBACK-001"]`, `result[0]["work_items"] == []`

#### Test 7c: get_exit_criteria handles "Arc Completion Criteria" heading variant
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestGetExitCriteria::test_get_exit_criteria_fallback_arc_completion_heading()`
- **setup:** Legacy ARC.md with `## Arc Completion Criteria` section (E2 era heading)
- **assertion:** Criteria parsed: `total == 2`, `checked == 1`, `unchecked_items == ["pending"]`

#### Test 8: get_exit_criteria reads from frontmatter
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestGetExitCriteria::test_get_exit_criteria_from_frontmatter()`
- **setup:** ARC.md with frontmatter `exit_criteria: [{text: "bugs resolved", checked: True}]`
- **assertion:** `result["all_checked"] is True`, `result["total"] == 1`

#### Test 9: get_exit_criteria falls back to checkbox parsing
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestGetExitCriteria::test_get_exit_criteria_fallback()`
- **setup:** Legacy ARC.md with `## Exit Criteria` and `- [x] done\n- [ ] pending`
- **assertion:** `result["all_checked"] is False`, `unchecked_items == ["pending"]`

#### Test 10: update_chapter_in_frontmatter updates status
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestUpdateChapterInFrontmatter::test_update_chapter_in_frontmatter()`
- **setup:** ARC.md with frontmatter, CH-067 status: Active
- **assertion:** Returns True; re-parsing confirms `chapters[0]["status"] == "Complete"`

#### Test 11: update_chapter_in_frontmatter returns False when chapter not found
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestUpdateChapterInFrontmatter::test_update_chapter_not_found()`
- **setup:** ARC.md with CH-065; try to update CH-999
- **assertion:** Returns False; file unchanged

#### Test 12: update_chapter_in_frontmatter returns False when no frontmatter
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestUpdateChapterInFrontmatter::test_update_chapter_no_frontmatter()`
- **setup:** Legacy ARC.md (no frontmatter)
- **assertion:** Returns False

#### Test 13: migrate_file injects frontmatter into legacy ARC.md
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestMigration::test_migrate_arc_file_injects_frontmatter()`
- **setup:** Write realistic legacy `ARC_INFRA_LEGACY_CONTENT` (infrastructure arc, 6-col table)
- **assertion:** `result["migrated"] is True`; frontmatter parseable; `id == "infrastructure"`, `len(chapters) == 2`; markdown body preserved

#### Test 14: migrate_file skips file already having frontmatter
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestMigration::test_migrate_arc_file_skips_existing()`
- **setup:** ARC.md with existing frontmatter
- **assertion:** `result["skipped"] is True`; file content unchanged

#### Test 15: migrate_file dry_run does not write to disk
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestMigration::test_migrate_arc_file_dry_run()`
- **setup:** Legacy ARC.md; call with `dry_run=True`
- **assertion:** `result["migrated"] is True` (computed); file content unchanged

#### Test 16: build_arc_frontmatter parses all fields from realistic content
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestBuildArcFrontmatter::test_build_arc_frontmatter_parses_all_fields()`
- **setup:** Use `ARC_INFRA_LEGACY_CONTENT` constant
- **assertion:** `id == "infrastructure"`, `epoch == "E2.8"`, `theme == "Fix what's broken"`, `status == "Planning"`, `len(chapters) == 2`, `chapters[0]["status"] == "Complete"`, `len(exit_criteria) == 1`, `exit_criteria[0]["checked"] is True`

#### Test 17: hierarchy_engine.get_chapters uses arc_frontmatter
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestConsumerIntegration::test_hierarchy_engine_uses_arc_frontmatter()`
- **setup:** tmp_path with haios.yaml + ARC.md with frontmatter chapters; `HierarchyQueryEngine(base_path=tmp_path)`
- **assertion:** `engine.get_chapters("infrastructure")` returns `ChapterInfo` list; CH-065 status is "Complete"

#### Test 18: status_propagator.update_arc_chapter_status uses arc_frontmatter
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestConsumerIntegration::test_status_propagator_uses_arc_frontmatter()`
- **setup:** tmp_path with ARC.md with frontmatter CH-067 Active; `StatusPropagator(base_path=tmp_path)`
- **assertion:** `update_arc_chapter_status("infrastructure", "CH-067", "Complete")` returns `{"updated": True}`; frontmatter re-read confirms status updated

#### Test 19: dod_validation.validate_epoch_dod uses arc_frontmatter
- **file:** `tests/test_arc_frontmatter.py`
- **function:** `TestConsumerIntegration::test_epoch_dod_uses_arc_frontmatter()`
- **setup:** tmp_path with EPOCH.md + ARC.md with `status: Complete` frontmatter; `validate_epoch_dod("E2_8", base_path=tmp_path)`
- **assertion:** `result.passed is True`

---

### Design

#### File 1 (NEW): `.claude/haios/lib/arc_frontmatter.py`

Complete module providing parse/read/write access to ARC.md YAML frontmatter with backward-compatible fallback to bold-markdown and multi-column table parsing.

**Public functions:**
- `parse_arc_frontmatter(path: Path) -> Optional[dict]` — returns frontmatter dict or None
- `get_arc_status(path: Path) -> Optional[str]` — status field, fallback to `**Status:**`
- `get_arc_metadata(path: Path) -> Dict[str, str]` — `{"theme": str, "status": str}`
- `get_chapters(path: Path) -> List[dict]` — chapters list, fallback 4/5/6-col table
- `get_exit_criteria(path: Path) -> Optional[Dict]` — exit criteria, fallback checkbox parsing
- `update_chapter_in_frontmatter(path: Path, chapter_id: str, new_status: str) -> bool`
- `_write_frontmatter(path: Path, fm: dict) -> None` — internal write helper

**Key implementation notes:**
- `parse_arc_frontmatter`: strips `# ` comment lines before checking for `---` (same as `chapter_frontmatter.py`)
- `get_chapters` fallback: branches on `len(cells)` — `>= 6` (6-col), `== 5` (5-col), `== 4` (4-col)
- `get_exit_criteria` fallback: regex `^##\s+(Exit Criteria|Arc Completion Criteria|...)` covers all epoch heading variants
- `update_chapter_in_frontmatter`: returns False without fallback — caller owns fallback responsibility
- `_write_frontmatter`: splits on `"---"` (3 parts), rewrites `---\n{yaml}---{body}`

**Import pattern (sibling consistency):**
```python
import re
from pathlib import Path
from typing import Dict, List, Optional
import yaml
```

#### File 2 (NEW): `.claude/haios/lib/migrate_arc_frontmatter.py`

Migration script to inject YAML frontmatter into all existing ARC.md files.

**Key functions:**
- `build_arc_frontmatter(content: str) -> dict` — parses bold-markdown into frontmatter dict
- `_parse_chapters_table(content: str) -> List[dict]` — 4/5/6-col branching with `_clean_status()`
- `_clean_status(raw: str) -> str` — strips `**...**` and `(S\d+...)` annotations
- `_parse_exit_criteria(content: str) -> List[dict]` — handles all section heading variants
- `migrate_file(path: Path, dry_run: bool = False) -> dict` — idempotent single-file migration
- `migrate_all(base_path=None, dry_run=False) -> List[dict]` — batch migration of `ARC_FILES` list

**`ARC_FILES` list:** 34 paths covering E2 through E2.8 (all epochs that have ARC.md files).

**Status cleaning in `build_arc_frontmatter`:**
```python
def _clean_status(raw: str) -> str:
    cleaned = raw.replace("**", "").strip()
    cleaned = re.sub(r"\s*\(S\d+.*?\)\s*$", "", cleaned)
    return cleaned
```

**Migration output preserves markdown body:**
```python
new_content = f"---\n{yaml_block}---\n{content}"
```

#### File 3 (MODIFY): `.claude/haios/lib/hierarchy_engine.py`

**Location:** `_parse_arc_metadata()` and `_parse_arc_chapters()` methods.

**Current Code (before WORK-245):**
```python
def _parse_arc_metadata(self, arc_file: Path) -> Dict[str, str]:
    content = arc_file.read_text(encoding="utf-8")
    theme = ""
    status = ""
    for line in content.split("\n"):
        if line.startswith("**Theme:**"):
            theme = line.split("**Theme:**", 1)[1].strip()
        elif line.startswith("**Status:**"):
            status = line.split("**Status:**", 1)[1].strip()
    return {"theme": theme, "status": status}
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

def _parse_arc_chapters(self, arc_file: Path, arc_name: str) -> List[ChapterInfo]:
    """Parse chapter rows from ARC.md — frontmatter-first with table fallback."""
    try:
        from arc_frontmatter import get_chapters
    except ImportError:
        from .arc_frontmatter import get_chapters
    raw = get_chapters(arc_file)
    chapters = []
    for ch in raw:
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

#### File 4 (MODIFY): `.claude/haios/lib/status_propagator.py`

**Location:** `update_arc_chapter_status()` and `is_arc_complete()` methods.

**Target Code for `update_arc_chapter_status`:**
```python
def update_arc_chapter_status(self, arc_name, chapter_id, new_status) -> dict:
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
```

**Target Code for `is_arc_complete`:**
```python
def is_arc_complete(self, arc_name) -> bool:
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

#### File 5 (MODIFY): `.claude/haios/lib/epoch_loader.py`

**Location:** `_extract_chapter_table()` method, lines 91–117.

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

#### File 6 (MODIFY): `.claude/haios/lib/epoch_validator.py`

**Location:** `validate_epoch_status()` method, lines 194–274.

**Key additions (frontmatter path):**
```python
try:
    from arc_frontmatter import get_chapters as get_arc_chapters
    _arc_fm_available = True
except ImportError:
    try:
        from .arc_frontmatter import get_chapters as get_arc_chapters
        _arc_fm_available = True
    except ImportError:
        _arc_fm_available = False

arcs_dir_str = self._haios_config.get("epoch", {}).get("arcs_dir", "")
arcs_dir = self._base_path / arcs_dir_str if arcs_dir_str else None

# Guard: only use frontmatter path when work_statuses is NOT injected (production mode)
_use_frontmatter = (_arc_fm_available and arcs_dir and arcs_dir.exists()
                    and self._work_statuses is None)
if _use_frontmatter:
    for arc_dir in arcs_dir.iterdir():
        if not arc_dir.is_dir():
            continue
        arc_file = arc_dir / "ARC.md"
        if arc_file.exists():
            for ch in get_arc_chapters(arc_file):
                arc_chapters_map[ch["id"]] = ch
```

The `self._work_statuses is None` guard preserves test isolation: existing epoch_validator tests inject `work_statuses` directly and do not need ARC.md files on disk.

#### File 7 (MODIFY): `.claude/haios/lib/dod_validation.py`

**Location:** `validate_epoch_dod()` function, lines 430–476.

**Current Code (before WORK-245):**
```python
for arc_file in arc_files:
    arc_name = arc_file.parent.name
    content = arc_file.read_text(encoding="utf-8")
    status = _parse_markdown_field(content, "Status") or "Unknown"
```

**Target Code:**
```python
try:
    from arc_frontmatter import get_arc_status
except ImportError:
    from .arc_frontmatter import get_arc_status

incomplete = []
skipped = []
for arc_file in arc_files:
    arc_name = arc_file.parent.name
    status = get_arc_status(arc_file) or "Unknown"
    if "deferred" in status.lower():
        skipped.append(arc_name)
        continue
    if status != "Complete":
        incomplete.append((arc_name, status))
```

---

### Call Chain

```
close-work-cycle ARCHIVE phase
    |
    +-> StatusPropagator.propagate("WORK-245")
    |       |
    |       +-> update_arc_chapter_status("infrastructure", "CH-067", "Complete")
    |               |
    |               +-> arc_frontmatter.update_chapter_in_frontmatter()  # frontmatter path
    |               +-> [table surgery fallback for unmigrated files]
    |
    +-> is_arc_complete("infrastructure")
            |
            +-> arc_frontmatter.get_chapters()
```

```
coldstart-orchestrator
    |
    +-> EpochLoader.load()
    |       |
    |       +-> _extract_chapter_table(content, arc_path=arc_path)
    |               |
    |               +-> arc_frontmatter.get_chapters()  # frontmatter path
    |
    +-> EpochValidator.validate()
            |
            +-> validate_epoch_status()
                    |
                    +-> arc_frontmatter.get_chapters()  # production only
                    +-> [EPOCH.md table fallback in test mode]
```

```
dod_validation.validate_epoch_dod("E2_8")
    |
    +-> arc_frontmatter.get_arc_status(arc_file)  # frontmatter-first
    +-> [**Status:** fallback for unmigrated files]
```

---

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Module placement | `lib/arc_frontmatter.py` (not `modules/`) | No GovernanceLayer dependency — pure file I/O. Matches chapter_frontmatter.py placement. |
| Import pattern | `try/except ImportError` with relative fallback | Consistent with all sibling modules (chapter_frontmatter.py, hierarchy_engine.py). Works from lib/ and modules/ callers. |
| Multi-column table branching | `len(cells) >= 6`, `== 5`, `== 4` | ARC.md files span E2–E2.8 with 3 distinct table formats. Silent failure on 4/5-col is the existing bug. |
| Status cleaning in migration | Strip `**...**` and `(S\d+...)` | `is_arc_complete` fails silently when ARC.md has `**Complete** (S335)` — cleaning fixes this at source. |
| `update_chapter_in_frontmatter` no fallback | Returns False, caller owns fallback | Separation of concerns: frontmatter module does frontmatter. StatusPropagator owns the decision to fall back to table surgery. |
| epoch_validator guard (`work_statuses is None`) | Use legacy path when `work_statuses` injected | Existing tests inject work_statuses directly — frontmatter path would require ARC.md files on disk in test fixtures. Guard preserves test isolation without changes to existing tests. |
| Frontmatter schema | id, epoch, theme, status, started, chapters (list), exit_criteria (list) | Matches what hierarchy_engine, status_propagator, epoch_loader, epoch_validator each need. No extra fields. |
| Migration file list (ARC_FILES) | Explicit list of 34 paths | All ARC.md files across E2–E2.8. Explicit list is idempotent and auditable vs. glob (glob would pick up test fixtures). |

---

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| No frontmatter in ARC.md | All functions fall back to bold-markdown / table parsing | Tests 2, 4, 7, 7a, 7b, 9 |
| 4-column chapter table (E2 era) | `len(cells) == 4` branch: id, title, status columns | Test 7a |
| 5-column chapter table (E2.5 variant) | `len(cells) == 5` branch: id, title, reqs, deps, status | Test 7b |
| "Arc Completion Criteria" heading (E2 era) | Regex alternation in section heading match | Test 7c |
| Status with bold formatting `**Complete** (S335)` | `_clean_status()` strips markers in migration script | Test 16 |
| Chapter not found in frontmatter | `update_chapter_in_frontmatter` returns False | Test 11 |
| Migration of already-migrated file | `_has_frontmatter()` check → `{"skipped": True}` | Test 14 |
| dry_run=True | Computes result but does not write | Test 15 |
| epoch_validator test mode (`work_statuses` injected) | `_use_frontmatter = False` guard | Design (no separate test needed — existing tests verify) |
| ARC.md file not found during migration | Returns `{"error": "not_found"}` | Covered by migrate_file guard |

---

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| All 34 ARC.md files may already have frontmatter | Low | `migrate_all` is idempotent — files with frontmatter are skipped; verify with `--dry-run` |
| epoch_validator existing tests break due to frontmatter path | Medium | `work_statuses is None` guard explicitly disabled frontmatter path in test mode; run `pytest tests/test_epoch_validator.py` before full suite |
| `_write_frontmatter` split on `"---"` breaks ARC.md with `---` in body | Low | `content.split("---", 2)` limits to first 2 splits; body `---` horizontal rules are fine |
| Migration script loses markdown body content | High | `new_content = f"---\n{yaml_block}---\n{content}"` prepends frontmatter, preserves full original content; Test 13 verifies `## Definition` present |
| 4-column table mistakenly matches non-chapter rows | Medium | Pattern `re.match(r"\s*\|\s*CH-\d+", line)` anchors on `CH-\d+` prefix — only real chapter rows match |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Create `tests/test_arc_frontmatter.py` with all 22 tests (Tests 1–19 including 7a, 7b, 7c)
- **output:** Test file exists; all 22 tests fail with `ModuleNotFoundError: arc_frontmatter`
- **verify:** `pytest tests/test_arc_frontmatter.py -v 2>&1 | grep -c "ERROR\|FAILED"` equals 22

### Step 2: Implement arc_frontmatter.py (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (NEW)
- **input:** Step 1 complete (22 failing tests)
- **action:** Create `.claude/haios/lib/arc_frontmatter.py` with all 7 public functions per spec
- **output:** Tests 1–12 and 17–19 pass; migration tests (13–16) may still fail
- **verify:** `pytest tests/test_arc_frontmatter.py::TestParseArcFrontmatter tests/test_arc_frontmatter.py::TestGetArcStatus tests/test_arc_frontmatter.py::TestGetArcMetadata tests/test_arc_frontmatter.py::TestGetChapters tests/test_arc_frontmatter.py::TestGetExitCriteria tests/test_arc_frontmatter.py::TestUpdateChapterInFrontmatter -v` exits 0

### Step 3: Implement migrate_arc_frontmatter.py
- **spec_ref:** Layer 1 > Design > File 2 (NEW)
- **input:** Step 2 complete (arc_frontmatter.py exists)
- **action:** Create `.claude/haios/lib/migrate_arc_frontmatter.py` with `build_arc_frontmatter`, `migrate_file`, `migrate_all`, `ARC_FILES` list
- **output:** All 22 tests pass
- **verify:** `pytest tests/test_arc_frontmatter.py -v` exits 0, output contains `22 passed`

### Step 4: Update Consumer — hierarchy_engine.py
- **spec_ref:** Layer 1 > Design > File 3 (MODIFY)
- **input:** Step 3 complete
- **action:** Replace `_parse_arc_metadata()` and `_parse_arc_chapters()` bodies with arc_frontmatter delegation
- **output:** Existing hierarchy_engine tests still pass
- **verify:** `pytest tests/test_hierarchy_engine.py -v` exits 0

### Step 5: Update Consumer — status_propagator.py
- **spec_ref:** Layer 1 > Design > File 4 (MODIFY)
- **input:** Step 4 complete
- **action:** Add frontmatter-first path to `update_arc_chapter_status()` and update `is_arc_complete()` to use `get_chapters()`
- **output:** StatusPropagator tests pass; Test 18 passes
- **verify:** `pytest tests/test_arc_frontmatter.py::TestConsumerIntegration::test_status_propagator_uses_arc_frontmatter -v` exits 0

### Step 6: Update Consumer — epoch_loader.py
- **spec_ref:** Layer 1 > Design > File 5 (MODIFY)
- **input:** Step 5 complete
- **action:** Add frontmatter-first path to `_extract_chapter_table()` when `arc_path` provided
- **output:** EpochLoader tests pass
- **verify:** `pytest tests/test_epoch_loader.py -v` exits 0

### Step 7: Update Consumer — epoch_validator.py
- **spec_ref:** Layer 1 > Design > File 6 (MODIFY)
- **input:** Step 6 complete
- **action:** Add frontmatter import + `_use_frontmatter` guard in `validate_epoch_status()`
- **output:** Existing epoch_validator tests pass (guard preserved); production path uses frontmatter
- **verify:** `pytest tests/test_epoch_validator.py -v` exits 0

### Step 8: Update Consumer — dod_validation.py
- **spec_ref:** Layer 1 > Design > File 7 (MODIFY)
- **input:** Step 7 complete
- **action:** Replace `_parse_markdown_field(content, "Status")` call in `validate_epoch_dod()` with `get_arc_status(arc_file)`
- **output:** DoD validation tests pass; Test 19 passes
- **verify:** `pytest tests/test_arc_frontmatter.py::TestConsumerIntegration::test_epoch_dod_uses_arc_frontmatter tests/test_dod_validation.py tests/test_multilevel_dod.py -v` exits 0

### Step 9: Run Migration Script
- **spec_ref:** Layer 0 > Primary Files (migrate_arc_frontmatter.py)
- **input:** Step 8 complete; all tests passing
- **action:** `python .claude/haios/lib/migrate_arc_frontmatter.py --dry-run` (verify), then `python .claude/haios/lib/migrate_arc_frontmatter.py` (execute)
- **output:** All 34 ARC.md files skipped (already have frontmatter) or migrated
- **verify:** `python .claude/haios/lib/migrate_arc_frontmatter.py --dry-run 2>&1 | grep -c "MIGRATED\|SKIPPED"` equals 34

### Step 10: Update README.md
- **spec_ref:** Layer 0 > Consumer Files
- **input:** Step 9 complete
- **action:** Add rows for `arc_frontmatter.py` and `migrate_arc_frontmatter.py` to the Modules table in `.claude/haios/lib/README.md`
- **output:** README reflects new modules
- **verify:** `grep "arc_frontmatter" .claude/haios/lib/README.md` returns 2 matches

### Step 11: Full Test Suite
- **spec_ref:** Ground Truth Verification > Tests
- **input:** Steps 1–10 complete
- **action:** Run full test suite
- **output:** 0 new failures vs. pre-WORK-245 baseline
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows 0 new failures

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_arc_frontmatter.py -v` | 22 passed, 0 failed |
| `pytest tests/test_hierarchy_engine.py -v` | 0 new failures |
| `pytest tests/test_epoch_validator.py -v` | 0 new failures |
| `pytest tests/test_dod_validation.py tests/test_multilevel_dod.py -v` | 0 new failures |
| `pytest tests/test_epoch_loader.py -v` | 0 new failures |
| `pytest tests/ -v` | 0 new failures vs. pre-WORK-245 baseline |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| ARC.md files have YAML frontmatter | `python .claude/haios/lib/migrate_arc_frontmatter.py --dry-run` | All 34 files: SKIPPED (already migrated) or MIGRATED |
| hierarchy_engine reads ARC.md frontmatter | `grep "from arc_frontmatter import" .claude/haios/lib/hierarchy_engine.py` | 2 matches (get_arc_metadata, get_chapters) |
| status_propagator updates frontmatter | `grep "update_chapter_in_frontmatter" .claude/haios/lib/status_propagator.py` | 1 match |
| epoch_loader reads frontmatter chapters | `grep "from arc_frontmatter import" .claude/haios/lib/epoch_loader.py` | 1 match |
| epoch_validator reads frontmatter | `grep "from arc_frontmatter import" .claude/haios/lib/epoch_validator.py` | 1 match |
| dod_validation reads frontmatter status | `grep "from arc_frontmatter import" .claude/haios/lib/dod_validation.py` | 1 match |
| Migration script exists and runs | `python .claude/haios/lib/migrate_arc_frontmatter.py --dry-run` | Exit 0; prints migration summary |
| 4 duplicate parsers eliminated | `grep "_parse_arc_metadata\|_parse_arc_chapters" .claude/haios/lib/hierarchy_engine.py` | Both functions delegate to arc_frontmatter (no inline parsing) |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| No inline bold-markdown arc parsing in consumers | `grep "\*\*Status:\*\*\|\*\*Theme:\*\*" .claude/haios/lib/status_propagator.py .claude/haios/lib/epoch_loader.py .claude/haios/lib/epoch_validator.py .claude/haios/lib/dod_validation.py` | 0 matches |
| README updated | `grep "arc_frontmatter" .claude/haios/lib/README.md` | 2 matches |
| arc_frontmatter module importable from lib | `cd /d/PROJECTS/haios && python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from arc_frontmatter import parse_arc_frontmatter; print('OK')"` | prints OK |

### Completion Criteria (DoD)

- [ ] All 22 tests in `tests/test_arc_frontmatter.py` pass
- [ ] No new failures in full test suite (pytest tests/)
- [ ] All WORK.md deliverables verified (table above)
- [ ] Migration script runs cleanly on all 34 ARC.md files
- [ ] No stale inline bold-markdown parsing for arc Status in consumers
- [ ] README.md updated with arc_frontmatter.py and migrate_arc_frontmatter.py rows
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `docs/work/active/WORK-244/WORK.md` — Phase 1 prerequisite (CHAPTER.md migration pattern)
- `.claude/haios/lib/chapter_frontmatter.py` — module pattern to follow
- `.claude/haios/lib/migrate_chapter_frontmatter.py` — migration script pattern to follow
- `docs/work/active/WORK-240/WORK.md` — spawning investigation (4 duplicate parsers finding)
- Memory: 89402–89407 (WORK-240 investigation findings)
- Memory: 89484–89492 (WORK-245 design decisions)
- Memory: 87137 (StatusPropagator drift — ARC.md not updated on propagation)

---
