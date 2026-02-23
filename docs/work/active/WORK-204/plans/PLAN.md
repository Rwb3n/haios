---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-23
backlog_id: WORK-204
title: "Chapter Manifest Auto-Update on Work Closure"
author: Hephaestus
lifecycle_phase: plan
session: 432
generated: 2026-02-23
last_updated: 2026-02-23T14:22:37

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-204/WORK.md"
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
# Implementation Plan: Chapter Manifest Auto-Update on Work Closure

---

## Goal

When `WorkEngine.close()` closes a work item that has a `chapter` field, the parent chapter's CHAPTER.md work items table is auto-updated to reflect `Complete` status — fail-permissive, never blocking closure.

---

## Open Decisions

None — design mirrors WORK-177 creation-side pattern exactly.

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/lib/scaffold.py` | MODIFY | 2 |
| `.claude/haios/modules/work_engine.py` | MODIFY | 2 |

### Consumer Files

None — the new function is called only from `WorkEngine.close()`.

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_chapter_manifest_update.py` | UPDATE | Add closure-side tests alongside existing creation-side tests |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | — |
| Files to modify | 3 | scaffold.py, work_engine.py, test file |
| Tests to write | 3 | Success, missing file, status already Complete |
| Total blast radius | 3 | — |

---

## Layer 1: Specification

### Current State

```python
# .claude/haios/modules/work_engine.py:570-613
def close(self, id: str) -> Path:
    check_ceremony_required("close")
    work = self.get_work(id)
    if work is None:
        raise WorkNotFoundError(f"Work item {id} not found")

    work.status = "complete"
    work.queue_position = "done"
    work.cycle_phase = "done"

    # ... queue_history, node_history updates ...

    self._write_work_file(work)
    self._set_closed_date(work.path, datetime.now().strftime("%Y-%m-%d"))
    # ADR-041: No move to archive
    return work.path
```

**Behavior:** `close()` sets status/queue/cycle fields and closed date. Does not touch parent chapter.
**Problem:** Chapter CHAPTER.md work items table shows stale status (e.g., "Active") after work closure, causing progressive drift.

### Desired State

```python
# .claude/haios/modules/work_engine.py:570-615 (after change)
def close(self, id: str) -> Path:
    check_ceremony_required("close")
    work = self.get_work(id)
    if work is None:
        raise WorkNotFoundError(f"Work item {id} not found")

    work.status = "complete"
    work.queue_position = "done"
    work.cycle_phase = "done"

    # ... queue_history, node_history updates ...

    self._write_work_file(work)
    self._set_closed_date(work.path, datetime.now().strftime("%Y-%m-%d"))

    # WORK-204: Auto-update chapter manifest status (fail-permissive)
    chapter_id = getattr(work, 'chapter', None)
    if chapter_id:
        _try_update_chapter_manifest_status(work.id, chapter_id)

    return work.path
```

**Behavior:** After closing, updates the chapter manifest row status to "Complete".
**Result:** Chapter CHAPTER.md stays in sync with work item status automatically.

### Tests

#### Test 1: Chapter manifest status updated on work closure
- **file:** `tests/test_chapter_manifest_update.py`
- **function:** `test_chapter_manifest_status_updated_on_close()`
- **setup:** Create CHAPTER.md with work item row showing "Active" status. Call `update_chapter_manifest_status()` with work_id and chapter_id, base_path=tmp_path.
- **assertion:** CHAPTER.md row for work_id now shows "Complete". Return dict has `updated: True`.

#### Test 2: Missing chapter file returns graceful failure
- **file:** `tests/test_chapter_manifest_update.py`
- **function:** `test_chapter_manifest_status_missing_file_no_error()`
- **setup:** No chapter file created. Call `update_chapter_manifest_status()` with nonexistent chapter_id, base_path=tmp_path.
- **assertion:** Return dict has `updated: False, reason: chapter_file_not_found`. No exception raised.

#### Test 3: Work ID not in chapter table returns graceful result
- **file:** `tests/test_chapter_manifest_update.py`
- **function:** `test_chapter_manifest_status_work_not_in_table()`
- **setup:** Create CHAPTER.md with different work items. Call `update_chapter_manifest_status()` with work_id not in table.
- **assertion:** Return dict has `updated: False, reason: work_id_not_found`. File unchanged.

### Design

#### File 1 (MODIFY): `.claude/haios/lib/scaffold.py`

Add `update_chapter_manifest_status()` function after existing `update_chapter_manifest()` (line ~714). Mirrors existing pattern.

```python
def update_chapter_manifest_status(
    work_id: str,
    chapter_id: str,
    new_status: str = "Complete",
    base_path: Optional[Path] = None,
) -> dict:
    """Update chapter CHAPTER.md work items table status for a work item. WORK-204.

    Locates the chapter file by glob pattern matching CH-{id}-* directory
    under the current epoch's arcs. Updates the status column for the
    matching work ID row.

    Fail-permissive: returns result dict, never raises.
    Mirrors update_chapter_manifest() (WORK-177) for the closure side.

    Args:
        work_id: Work item ID (e.g., "WORK-204")
        chapter_id: Chapter ID (e.g., "CH-059")
        new_status: New status string (default: "Complete")
        base_path: Project root (injectable for testing)

    Returns:
        {"updated": True/False, "reason": str, "chapter_file": str|None}
    """
    root = base_path or PROJECT_ROOT
    pattern = f".claude/haios/epochs/*/arcs/*/chapters/{chapter_id}-*/CHAPTER.md"
    matches = list(root.glob(pattern))
    if not matches:
        return {"updated": False, "reason": "chapter_file_not_found", "chapter_file": None}

    chapter_file = matches[0]
    content = chapter_file.read_text(encoding="utf-8")

    # Find the row for this work_id
    if f"| {work_id} |" not in content:
        return {"updated": False, "reason": "work_id_not_found", "chapter_file": str(chapter_file)}

    # Replace the status in the matching row
    # Table format: | ID | Title | Status | Type |
    # Strategy: find line containing "| {work_id} |" and replace 3rd column
    lines = content.split("\n")
    updated = False
    for i, line in enumerate(lines):
        if f"| {work_id} |" in line:
            parts = line.split("|")
            if len(parts) >= 5:  # | ID | Title | Status | Type |
                parts[3] = f" {new_status} "
                lines[i] = "|".join(parts)
                updated = True
            break

    if not updated:
        return {"updated": False, "reason": "parse_error", "chapter_file": str(chapter_file)}

    chapter_file.write_text("\n".join(lines), encoding="utf-8")
    return {"updated": True, "reason": "status_updated", "chapter_file": str(chapter_file)}
```

Add `_try_update_chapter_manifest_status()` fail-permissive wrapper (mirrors `_try_update_chapter_manifest()`):

```python
def _try_update_chapter_manifest_status(
    work_id: str, chapter_id: str
) -> None:
    """Fail-permissive wrapper for update_chapter_manifest_status. WORK-204.

    Never raises. Emits warnings.warn() on non-update or exception
    for operator observability (mirrors WORK-177 pattern).
    """
    import warnings
    try:
        result = update_chapter_manifest_status(work_id, chapter_id)
        if not result.get("updated"):
            warnings.warn(
                f"WORK-204: Chapter manifest status not updated for {work_id}: {result.get('reason')}",
                stacklevel=2,
            )
    except Exception as exc:
        warnings.warn(
            f"WORK-204: Chapter manifest status update failed (non-blocking): {exc}",
            stacklevel=2,
        )
```

#### File 2 (MODIFY): `.claude/haios/modules/work_engine.py`

**Location:** `close()` method, after `_set_closed_date()` call (line ~611)

**Current Code:**
```python
        self._set_closed_date(work.path, datetime.now().strftime("%Y-%m-%d"))

        # ADR-041: No move to archive - status field determines state
        return work.path
```

**Target Code:**
```python
        self._set_closed_date(work.path, datetime.now().strftime("%Y-%m-%d"))

        # WORK-204: Auto-update chapter manifest status (fail-permissive)
        chapter_id = getattr(work, 'chapter', None)
        if chapter_id:
            from scaffold import _try_update_chapter_manifest_status
            _try_update_chapter_manifest_status(work.id, chapter_id)

        # ADR-041: No move to archive - status field determines state
        return work.path
```

### Call Chain

```
just close-work {id}
    |
    +-> WorkEngine.close(id)
    |       +-> _write_work_file(work)
    |       +-> _set_closed_date(path, date)
    |       +-> _try_update_chapter_manifest_status(id, chapter_id)  # <-- NEW
    |       |       +-> update_chapter_manifest_status(id, chapter_id)
    |       |               Returns: {"updated": bool, "reason": str}
    |       Returns: Path
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Mirror WORK-177 pattern | Same function structure, same fail-permissive wrapper | Consistency. Creation-side and closure-side use identical patterns. |
| Function in scaffold.py | Not work_engine.py | Chapter file manipulation belongs with scaffold (WORK-177 precedent). WorkEngine calls scaffold. |
| Import inside close() | Lazy import from scaffold | Avoid circular imports. work_engine.py doesn't normally import scaffold. Matches cycle_state.py pattern. |
| Default status "Complete" | Not "complete" (lowercase) | Matches existing table convention (e.g., "Active", "Backlog", "Complete" in CHAPTER.md). |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| Chapter file missing | Return `chapter_file_not_found` | Test 2 |
| Work ID not in table | Return `work_id_not_found` | Test 3 |
| Row parse error | Return `parse_error` | Implicit (malformed table) |
| No chapter field on work item | Skip entirely (getattr returns None) | Integration (WorkEngine path) |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Table format mismatch | L — wrong column updated | Split on `|` and count parts >= 5 |
| Concurrent file access | L — unlikely in single-agent system | Fail-permissive, no data loss |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Add 3 test methods to `tests/test_chapter_manifest_update.py`
- **output:** Test file updated, all 3 new tests fail (ImportError — function doesn't exist yet)
- **verify:** `pytest tests/test_chapter_manifest_update.py -v -k "status"` shows 3 FAILED

### Step 2: Implement `update_chapter_manifest_status()` (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Add `update_chapter_manifest_status()` and `_try_update_chapter_manifest_status()` to `scaffold.py`
- **output:** All 3 new tests pass
- **verify:** `pytest tests/test_chapter_manifest_update.py -v -k "status"` shows 3 passed

### Step 3: Integrate into WorkEngine.close()
- **spec_ref:** Layer 1 > Design > File 2 (MODIFY)
- **input:** Step 2 complete (tests green)
- **action:** Add chapter manifest status update call to `work_engine.py close()` method
- **output:** Closure path now triggers chapter update
- **verify:** `grep "_try_update_chapter_manifest_status" .claude/haios/modules/work_engine.py` returns 1 match

### Step 4: Full test suite regression
- **spec_ref:** Ground Truth
- **input:** Step 3 complete
- **action:** Run full test suite
- **output:** No regressions
- **verify:** `pytest tests/test_chapter_manifest_update.py tests/test_work_engine.py -v` all pass

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_chapter_manifest_update.py -v` | 9 passed (6 existing + 3 new), 0 failed |
| `pytest tests/test_work_engine.py -v` | All pass, 0 new failures |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| Chapter manifest update function in scaffold.py | `grep "def update_chapter_manifest_status" .claude/haios/lib/scaffold.py` | 1 match |
| Fail-permissive wrapper | `grep "def _try_update_chapter_manifest_status" .claude/haios/lib/scaffold.py` | 1 match |
| Integration in WorkEngine.close() | `grep "_try_update_chapter_manifest_status" .claude/haios/modules/work_engine.py` | 1 match |
| Test for success case | `grep "test_chapter_manifest_status_updated_on_close" tests/test_chapter_manifest_update.py` | 1 match |
| Test for missing file | `grep "test_chapter_manifest_status_missing_file_no_error" tests/test_chapter_manifest_update.py` | 1 match |
| Test for work not in table | `grep "test_chapter_manifest_status_work_not_in_table" tests/test_chapter_manifest_update.py` | 1 match |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 2 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] Runtime consumer exists (WorkEngine.close calls the function)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

---

## References

- @docs/work/active/WORK-177/WORK.md (creation-side equivalent — reference pattern)
- @.claude/haios/lib/scaffold.py:647-737 (existing update_chapter_manifest and wrapper)
- @.claude/haios/modules/work_engine.py:570-613 (close method — integration point)
- @tests/test_chapter_manifest_update.py (existing tests — add to this file)
- Memory: 87789 (retro-extract FEATURE-1 from WORK-179)

---
