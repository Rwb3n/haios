---
template: implementation_plan
plan_version: "2.0"
status: approved
date: 2026-03-07
backlog_id: WORK-272
title: "Fix Drift Detection False Positives and Update ARC.md Work Items"
author: Hephaestus
lifecycle_phase: plan
session: 478
generated: 2026-03-07
last_updated: 2026-03-07T20:35:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-272/WORK.md"
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
# Implementation Plan: Fix Drift Detection False Positives and Update ARC.md Work Items

---

## Goal

Fix epoch_validator.py drift detection to only flag chapters where ALL work items are complete but the chapter status is not — eliminating false positives for chapters that legitimately contain a mix of complete and incomplete work items. Additionally, update ARC.md chapter work_items lists to reflect current state.

---

## Open Decisions

None — approach confirmed by operator (fix validator + update ARC.md).

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/lib/epoch_validator.py` | MODIFY | 2 |
| `.claude/haios/epochs/E2_8/arcs/call/ARC.md` | MODIFY | 2 |
| `.claude/haios/epochs/E2_8/arcs/infrastructure/ARC.md` | MODIFY | 2 |

### Consumer Files

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `.claude/haios/lib/coldstart_orchestrator.py` | calls EpochValidator | N/A | NO CHANGE (consumer just displays drift output) |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_epoch_validator.py` | UPDATE | Add tests for chapter-level drift logic |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | N/A |
| Files to modify | 4 | epoch_validator.py, 2x ARC.md, test file |
| Tests to write | 4 | Test Files table |
| Total blast radius | 4 | All unique files |

---

## Layer 1: Specification

### Current State

```python
# epoch_validator.py:226-244 — current drift detection
if arc_chapters_map:
    for ch_id, ch_data in arc_chapters_map.items():
        work_ids = re.findall(r"WORK-\d{3}", " ".join(ch_data.get("work_items", [])))
        epoch_status = ch_data["status"].lower()
        for work_id in work_ids:
            if self._work_statuses is not None:
                actual_status = self._work_statuses.get(work_id)
            else:
                actual_status = self._load_work_status(work_id)
            if actual_status is None:
                continue
            if (
                actual_status.lower() in COMPLETE_STATUSES
                and epoch_status not in EPOCH_COMPLETE_LABELS
            ):
                result["drift"].append(
                    f"DRIFT: {work_id} is '{actual_status}' in WORK.md "
                    f"but shown as '{ch_data['status']}' in ARC.md"
                )
```

**Behavior:** Flags drift for EACH individual work item that is complete when the parent chapter is not complete.

**Problem:** A chapter with 5 work items where 3 are complete and 2 are active is correctly "In Progress" — but the validator flags 3 false-positive drift warnings. The validator should only flag when ALL chapter work items are complete but the chapter status hasn't been updated.

### Desired State

```python
# epoch_validator.py:226-244 — fixed drift detection (chapter-level)
if arc_chapters_map:
    for ch_id, ch_data in arc_chapters_map.items():
        work_ids = re.findall(r"WORK-\d{3}", " ".join(ch_data.get("work_items", [])))
        epoch_status = ch_data["status"].lower()
        if not work_ids:
            continue
        # Collect statuses for ALL work items in the chapter
        statuses = {}
        for work_id in work_ids:
            if self._work_statuses is not None:
                actual_status = self._work_statuses.get(work_id)
            else:
                actual_status = self._load_work_status(work_id)
            if actual_status is not None:
                statuses[work_id] = actual_status.lower()
        # Only flag drift when ALL chapter work items are complete
        # but the chapter status is not
        if (
            statuses
            and all(s in COMPLETE_STATUSES for s in statuses.values())
            and epoch_status not in EPOCH_COMPLETE_LABELS
        ):
            ids_str = ", ".join(sorted(statuses.keys()))
            result["drift"].append(
                f"DRIFT: All work items in {ch_id} are complete "
                f"({ids_str}) but chapter status is "
                f"'{ch_data['status']}' in ARC.md"
            )
```

**Behavior:** Only flags drift when ALL work items in a chapter are complete but the chapter status hasn't been promoted.

**Result:** Eliminates false positives. The 6 current warnings disappear because CH-059, CH-061, and CH-067 all have incomplete work items alongside the complete ones.

### Tests

#### Test 1: Chapter with mixed statuses produces no drift
- **file:** `tests/test_epoch_validator.py`
- **function:** `test_validate_epoch_status_no_drift_mixed_chapter()`
- **setup:** Chapter with 2 work items: WORK-A complete, WORK-B active. Chapter status "In Progress". Use `work_statuses` injection.
- **assertion:** `result["drift"] == []`

#### Test 2: Chapter with all complete items but stale status produces drift
- **file:** `tests/test_epoch_validator.py`
- **function:** `test_validate_epoch_status_drift_all_complete()`
- **setup:** Chapter with 2 work items: both complete. Chapter status "In Progress". Use `work_statuses` injection.
- **assertion:** `len(result["drift"]) == 1` and drift message contains chapter ID, not individual work IDs

#### Test 3: Chapter already marked complete produces no drift
- **file:** `tests/test_epoch_validator.py`
- **function:** `test_validate_epoch_status_no_drift_chapter_complete()`
- **setup:** Chapter with 2 work items: both complete. Chapter status "Complete".
- **assertion:** `result["drift"] == []`

#### Test 4: Legacy fallback path also uses chapter-level logic
- **file:** `tests/test_epoch_validator.py`
- **function:** `test_validate_epoch_status_drift_legacy_all_complete()`
- **setup:** Use epoch_content (no frontmatter path). Chapter with 2 work items: both complete. Chapter status "Planning".
- **assertion:** `len(result["drift"]) == 1` and drift message contains chapter ID

### Design

#### File 1 (MODIFY): `.claude/haios/lib/epoch_validator.py`

**Location:** Lines 226-244 in `validate_epoch_status()`

**Current Code:** (see Current State above)

**Target Code:** (see Desired State above)

**ALSO modify legacy fallback** (lines 245-274): Apply same chapter-level logic — collect all work item statuses per chapter row before checking.

```python
# epoch_validator.py:245-274 — legacy fallback (also needs chapter-level fix)
else:
    # Legacy fallback: parse EPOCH.md table rows directly
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
        # Collect statuses for ALL work items in this chapter row
        statuses = {}
        for work_id in work_ids:
            if self._work_statuses is not None:
                actual_status = self._work_statuses.get(work_id)
            else:
                actual_status = self._load_work_status(work_id)
            if actual_status is not None:
                statuses[work_id] = actual_status.lower()
        # Only flag drift when ALL work items are complete
        if (
            statuses
            and all(s in COMPLETE_STATUSES for s in statuses.values())
            and epoch_status not in EPOCH_COMPLETE_LABELS
        ):
            ch_id = cells[0] if cells else "unknown"
            ids_str = ", ".join(sorted(statuses.keys()))
            result["drift"].append(
                f"DRIFT: All work items in {ch_id} are complete "
                f"({ids_str}) but chapter status is "
                f"'{cells[-1]}' in EPOCH.md"
            )
```

#### File 2 (MODIFY): `.claude/haios/epochs/E2_8/arcs/call/ARC.md`

Update chapter work_items in frontmatter to reflect actual work items assigned:
- CH-059: Add work items currently assigned in WORK.md files (grep chapter: CH-059)
- CH-061: Update to reflect complete items WORK-162, WORK-180, WORK-251 plus active WORK-273

#### File 3 (MODIFY): `.claude/haios/epochs/E2_8/arcs/infrastructure/ARC.md`

Update CH-067 work_items to include all items assigned (WORK-244, 245, 264, 265, 269, 254).

### Call Chain

```
ColdstartOrchestrator._run_validation_phase()
    |
    +-> EpochValidator.validate_epoch_status()   # <-- what we're changing
    |       Returns: {"drift": [...], "info": [...], "warnings": [...]}
    |
    +-> formats drift list into coldstart output
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Chapter-level vs item-level drift | Chapter-level | A chapter is the unit of status in ARC.md. Individual work items don't have their own row. |
| Drift message format | Include chapter ID + all work IDs | Actionable: tells you which chapter to update and proves all items are done |
| Legacy fallback also fixed | Yes | Both paths must behave consistently |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| Chapter with no work items in ARC.md | Skip (continue) | Not tested — degenerate case |
| Work item not found on disk | Skip that item (None check) | Existing behavior preserved |
| Chapter with only some items resolvable | Only check resolved items | Graceful degradation |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| ARC.md work_items list incomplete | L | Grep for chapter assignments to build accurate list |
| Existing test_validate_epoch_status_drift breaks | M | Update test to use chapter-level assertion |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Add 4 new test functions to tests/test_epoch_validator.py
- **output:** Test file updated, new tests fail (old logic produces wrong results)
- **verify:** `pytest tests/test_epoch_validator.py -v -k "mixed_chapter or drift_all_complete or chapter_complete or legacy_all_complete"` — tests fail

### Step 2: Fix Drift Detection Logic (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Replace per-item drift logic with chapter-level logic in both frontmatter and legacy paths
- **output:** New tests pass, existing test updated
- **verify:** `pytest tests/test_epoch_validator.py -v` exits 0

### Step 3: Update ARC.md Work Items Lists
- **spec_ref:** Layer 1 > Design > File 2 + File 3
- **input:** Step 2 complete
- **action:** Grep for all WORK.md files with chapter: CH-059, CH-061, CH-067 and update ARC.md frontmatter work_items lists
- **output:** ARC.md files reflect actual chapter assignments
- **verify:** Frontmatter work_items match grep results

### Step 4: Full Test Suite
- **spec_ref:** Layer 0 > Test Files
- **input:** Step 3 complete
- **action:** Run full test suite to check for regressions
- **output:** No new failures
- **verify:** `pytest tests/ -v` — no regressions

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_epoch_validator.py -v` | All passed, 0 failed |
| `pytest tests/ -v` | 0 new failures |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| Fix 6 stale drift warnings | Run coldstart validation | 0 DRIFT warnings for WORK-160,162,167,180,244,245 |
| Root cause identified | Read PLAN.md | Root cause documented: per-item vs chapter-level comparison |
| ARC.md work_items updated | Read ARC.md frontmatter | work_items lists match actual WORK.md assignments |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| Coldstart still runs validation | Run coldstart_orchestrator | VALIDATION phase produces output |
| No stale test assertions | pytest test_epoch_validator.py | All pass |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 2 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] No stale references (Consumer Integrity table above)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

---

## References

- Memory: 87137, 89404, 88990 (StatusPropagator drift is known issue)
- Memory: 85682 (epoch_validator only warns on drift)
- WORK-272 (parent work item)
- WORK-277 (spawned investigation: frontmatter-based hierarchy tracking)

---
