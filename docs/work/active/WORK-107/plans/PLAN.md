---
template: implementation_plan
status: complete
date: 2026-02-08
backlog_id: WORK-107
title: Implement Complete Without Spawn (CH-008)
author: Hephaestus
lifecycle_phase: plan
session: 324
version: '1.5'
generated: 2025-12-21
last_updated: '2026-02-08T23:09:34'
---
# Implementation Plan: Implement Complete Without Spawn (CH-008)

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: New feature, no existing code to show current state"
     - "SKIPPED: Pure documentation task, no code changes"
     - "SKIPPED: Trivial fix, single line change doesn't warrant detailed design"

     This prevents silent section deletion and ensures conscious decisions.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Memory unavailable (embedding model 404) — proceeding without |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

`WorkEngine.close()` sets `queue_position=done` atomically with `status=complete`, and the close-work-cycle skill accepts no-spawn closure as a first-class path without warnings or governance blocks.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `work_engine.py`, `test_close_work_cycle.py` |
| Lines of code affected | ~10 | `close()` method + new tests |
| New files to create | 0 | All changes in existing files |
| Tests to write | 4 | Runtime behavior tests (see Tests First) |
| Dependencies | 1 | `cli.py` calls `engine.close()` via `just close-work` |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single method change in WorkEngine |
| Risk of regression | Low | Existing `close()` tests minimal; `set_queue_position` already tested via WORK-105 |
| External dependencies | Low | No APIs or external services |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| Implementation | 10 min | High |
| Verification | 10 min | High |
| **Total** | **35 min** | |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/modules/work_engine.py:543-571
def close(self, id: str) -> Path:
    """Close work item: set status=complete, closed date."""
    work = self.get_work(id)
    if work is None:
        raise WorkNotFoundError(f"Work item {id} not found")

    # Update status and closed date
    work.status = "complete"
    self._write_work_file(work)

    # Set closed date in frontmatter
    self._set_closed_date(work.path, datetime.now().strftime("%Y-%m-%d"))

    return work.path
```

**Behavior:** Sets `status=complete` and `closed` date, but does NOT update `queue_position`. Work item ends with `status: complete` but `queue_position` remains whatever it was (usually `working` or `backlog`).

**Result:** Inconsistent state — `status: complete` but `queue_position: working`. Violates REQ-QUEUE-001 (queue orthogonal but consistent).

### Desired State

```python
# .claude/haios/modules/work_engine.py:543-575
def close(self, id: str) -> Path:
    """Close work item: set status=complete, queue_position=done, closed date."""
    work = self.get_work(id)
    if work is None:
        raise WorkNotFoundError(f"Work item {id} not found")

    # Update status and queue_position atomically
    work.status = "complete"
    work.queue_position = "done"
    self._write_work_file(work)

    # Set closed date in frontmatter
    self._set_closed_date(work.path, datetime.now().strftime("%Y-%m-%d"))

    return work.path
```

**Behavior:** Sets `status=complete`, `queue_position=done`, and `closed` date in one operation.

**Result:** Consistent terminal state. No spawn required — closure is complete.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Close Sets Queue Position Done

```python
def test_close_sets_queue_position_done(tmp_path):
    """WorkEngine.close() sets queue_position to 'done'."""
    engine = create_engine_with_work_item(tmp_path, "WORK-TEST", queue_position="working")
    engine.close("WORK-TEST")
    work = engine.get_work("WORK-TEST")
    assert work.queue_position == "done"
```

### Test 2: Close Sets Status Complete

```python
def test_close_sets_status_complete(tmp_path):
    """WorkEngine.close() sets status to 'complete'."""
    engine = create_engine_with_work_item(tmp_path, "WORK-TEST", status="active")
    engine.close("WORK-TEST")
    work = engine.get_work("WORK-TEST")
    assert work.status == "complete"
```

### Test 3: Close Without Spawn Is Valid (No Warnings)

```python
def test_close_without_spawn_no_warnings(tmp_path):
    """Closing work item without spawn_next succeeds without warnings.

    REQ-QUEUE-002: 'Complete without spawn' is valid terminal state.
    """
    engine = create_engine_with_work_item(tmp_path, "WORK-TEST")
    path = engine.close("WORK-TEST")
    assert path.exists()
    work = engine.get_work("WORK-TEST")
    assert work.status == "complete"
    assert work.queue_position == "done"
    # No spawn_next field needed — absence is valid
```

### Test 4: Close Persists Queue Position in Frontmatter

```python
def test_close_persists_queue_position_in_frontmatter(tmp_path):
    """Verify queue_position=done is persisted to WORK.md frontmatter."""
    engine = create_engine_with_work_item(tmp_path, "WORK-TEST", queue_position="working")
    engine.close("WORK-TEST")

    # Re-read from disk to verify persistence
    content = (tmp_path / "docs" / "work" / "active" / "WORK-TEST" / "WORK.md").read_text()
    assert "queue_position: done" in content
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/haios/modules/work_engine.py`
**Location:** Lines 543-571 in `close()`

**Current Code:**
```python
# work_engine.py:562-565
    # Update status and closed date
    work.status = "complete"
    self._write_work_file(work)
```

**Changed Code:**
```python
# work_engine.py:562-566
    # Update status and queue_position atomically (CH-008: complete without spawn)
    work.status = "complete"
    work.queue_position = "done"
    self._write_work_file(work)
```

**Diff:**
```diff
-        # Update status and closed date
+        # Update status and queue_position atomically (CH-008: complete without spawn)
         work.status = "complete"
+        work.queue_position = "done"
         self._write_work_file(work)
```

### Call Chain Context

```
just close-work {id}
    |
    +-> cli.py:cmd_close(work_id)
    |       |
    |       +-> WorkEngine.close(id)     # <-- What we're changing
    |               Sets: status=complete, queue_position=done, closed date
    |               Returns: Path
    |
    +-> just cascade {id} complete
    +-> just update-status
```

### Function/Component Signatures

```python
def close(self, id: str) -> Path:
    """
    Close work item: set status=complete, queue_position=done, closed date.

    Per ADR-041 "status over location": work items stay in docs/work/active/
    until epoch cleanup. The status field determines state, not directory path.
    CH-008: Sets queue_position=done atomically. No spawn_next required.

    Args:
        id: Work item ID

    Returns:
        Path to WORK.md (stays in active/)

    Raises:
        WorkNotFoundError: If work item doesn't exist
    """
```

### Behavior Logic

**Current Flow:**
```
close(id) → set status=complete → write → set closed date → return path
             (queue_position unchanged — inconsistent state)
```

**Fixed Flow:**
```
close(id) → set status=complete + queue_position=done → write → set closed date → return path
             (both fields set atomically — consistent terminal state)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Set queue_position in close() | Yes, atomically with status | Ensures consistent terminal state; avoids requiring separate set_queue_position call |
| No spawn_next field in WorkState | Don't add | Spawn decision is caller's (REQ-LIFECYCLE-004); close() doesn't need to know about it |
| No spawn_next in work item template | Don't add | The SKILL.md CHAIN phase already handles spawn choice via AskUserQuestion; no field needed in WORK.md |
| Modify close() not add close_work() | Modify existing | CH-008 spec shows `close_work()` but actual code has `close()` — follow existing patterns |
| No _validate_state_combination changes | Not needed | complete+done is already a valid combination (no forbidden rule) |
| Direct assignment not set_queue_position() | Direct assign + _write_work_file() | _write_work_file() calls _validate_state_combination() internally (line 929). Direct assignment is correct for atomic multi-field updates. set_queue_position() would double-write. |
| No governance mock in tests | Not needed | spawn_next doesn't exist in governance_layer.py or any module — no governance warnings to mock (critique A4/A12 resolved) |
| Cascade doesn't touch queue_position | Verified | cascade() only runs UNBLOCK/RELATED/MILESTONE/SUBSTANTIVE — does not modify queue_position (critique A5 resolved) |

### Input/Output Examples

**Before Fix (with real data):**
```
WorkEngine.close("WORK-106")
  WORK.md before: status: active, queue_position: backlog
  WORK.md after:  status: complete, queue_position: backlog  # <-- inconsistent!
```

**After Fix (expected):**
```
WorkEngine.close("WORK-106")
  WORK.md before: status: active, queue_position: backlog
  WORK.md after:  status: complete, queue_position: done     # <-- consistent
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Item already queue_position=done | close() overwrites to done (no-op) | Implicit in Test 3 |
| Item with queue_position=parked | close() sets to done (valid — parked items can be closed by operator) | Not tested (edge case, valid per _validate_state_combination) |
| Item with blocked_by | close() still works (DoD validation is in skill, not engine) | Existing behavior |

### Open Questions

None. Design is straightforward — single line addition.

---

## Open Decisions (MUST resolve before implementation)

No operator decisions pending. Work item has no `operator_decisions` field.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add 4 tests to `tests/test_close_work_cycle.py` (or new test file for runtime tests)
- [ ] Verify all 4 tests fail (red)

### Step 2: Add queue_position=done to close()
- [ ] Add `work.queue_position = "done"` in `WorkEngine.close()`
- [ ] Update docstring
- [ ] Tests 1-4 pass (green)

### Step 3: Verify No Governance Blockers
- [ ] Grep for any hooks/rules that warn on no-spawn
- [ ] Confirm SKILL.md already has "Complete without spawn" as first-class option
- [ ] No changes needed to SKILL.md (already correct per WORK-087)

### Step 4: Integration Verification
- [ ] All new tests pass
- [ ] Run full test suite (no regressions)
- [ ] Verify with real work item if possible

### Step 5: Consumer Verification
- [ ] Verify `just close-work` still works (calls engine.close via cli.py)
- [ ] No other consumers of close() need changes

---

## Verification

- [ ] Tests pass
- [ ] close() sets queue_position=done
- [ ] No warnings on no-spawn closure

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing tests assume queue_position unchanged after close | Low | Check existing tests for close() — only SKILL.md content tests exist |
| _validate_state_combination rejects complete+done | Low | Verified: no forbidden rule for this combo |
| cascade or update-status overwrite queue_position | Medium | Verify cascade doesn't reset queue_position — it only cascades status changes |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 324 | 2026-02-08 | - | Plan authored | - |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-107/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| close-work-cycle SKILL.md updated: explicit "Store output, no spawn" option | [ ] | Already present per WORK-087 |
| close-work-cycle accepts spawn_next=None without warnings | [ ] | SKILL.md CHAIN phase already lists it |
| WorkEngine.close_work() sets status=complete + queue_position=done | [ ] | Code change verified |
| No governance hooks warn or block on empty spawn_next | [ ] | Grep confirms no such hooks |
| Unit tests: close without spawn returns success | [ ] | Test output |
| Integration test: work item closes with null spawn_next | [ ] | Test output |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/work_engine.py` | close() sets queue_position=done | [ ] | |
| `tests/test_close_work_cycle.py` | 4 new runtime tests + 3 existing | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_close_work_cycle.py -v
# Expected: 7 tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** (`just close-work` calls engine.close())
- [ ] WHY captured (reasoning stored to memory)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- @.claude/haios/epochs/E2_5/arcs/queue/CH-008-CompleteWithoutSpawn.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-QUEUE-002)
- @.claude/skills/close-work-cycle/SKILL.md
- @docs/work/active/WORK-087/ (WORK-087: Caller Chaining — already updated SKILL.md)

---
