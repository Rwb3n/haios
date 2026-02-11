---
template: implementation_plan
status: complete
date: 2026-02-11
backlog_id: WORK-126
title: "Queue transition queue_history tracking"
author: Hephaestus
lifecycle_phase: plan
session: 349
version: "1.5"
generated: 2026-02-11
last_updated: 2026-02-11T22:14:32
---
# Implementation Plan: Queue transition queue_history tracking

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
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Queue transitions via `set_queue_position()` will record a `queue_history` audit trail in WORK.md frontmatter, parallel to `node_history` for lifecycle phases, maintaining orthogonality per REQ-QUEUE-001.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/haios/modules/work_engine.py` |
| Lines of code affected | ~30 | 6 touch points in work_engine.py |
| New files to create | 0 | Tests added to existing file |
| Tests to write | 5 | See Tests First section |
| Dependencies | 0 | No new imports; queue_ceremonies.py unchanged |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only work_engine.py internal changes |
| Risk of regression | Low | Additive field — existing tests unaffected |
| External dependencies | Low | No external APIs or config changes |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| Implementation | 15 min | High |
| Verification | 10 min | High |
| **Total** | 40 min | High |

---

## Current State vs Desired State

### Current State

```python
# work_engine.py:664 - set_queue_position updates queue_position but no history
def set_queue_position(self, id: str, position: str) -> Optional[WorkState]:
    # ... validation ...
    work.queue_position = position
    self._write_work_file(work)  # No queue_history append
    return work
```

**Behavior:** `set_queue_position()` updates `queue_position` field only. No per-item history of queue transitions is recorded in WORK.md.

**Result:** Queue transitions are invisible in work item state. Only governance-events.jsonl captures them externally.

### Desired State

```python
# work_engine.py:664 - set_queue_position now appends queue_history
def set_queue_position(self, id: str, position: str) -> Optional[WorkState]:
    # ... validation ...
    now = datetime.now().isoformat()
    if work.queue_history:
        work.queue_history[-1]["exited"] = now
    work.queue_history.append({"position": position, "entered": now, "exited": None})
    work.queue_position = position
    self._write_work_file(work)
    return work
```

**Behavior:** Every queue transition appends to `queue_history` with timestamps, mirroring `node_history` shape.

**Result:** Work items carry a self-contained audit trail of queue transitions in frontmatter.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: set_queue_position appends queue_history
```python
def test_set_queue_position_appends_queue_history(tmp_path, governance):
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-QH1", "Test Queue History")
    engine.set_queue_position("WORK-QH1", "ready")
    work = engine.get_work("WORK-QH1")
    assert len(work.queue_history) == 2
    assert work.queue_history[0]["position"] == "backlog"
    assert work.queue_history[0]["exited"] is not None
    assert work.queue_history[1]["position"] == "ready"
    assert work.queue_history[1]["exited"] is None
```

### Test 2: queue_history full lifecycle
```python
def test_queue_history_full_lifecycle(tmp_path, governance):
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-QH2", "Full Lifecycle")
    engine.set_queue_position("WORK-QH2", "ready")
    engine.set_queue_position("WORK-QH2", "working")
    work = engine.get_work("WORK-QH2")
    assert len(work.queue_history) == 3
    assert [h["position"] for h in work.queue_history] == ["backlog", "ready", "working"]
    assert all(h["exited"] is not None for h in work.queue_history[:-1])
    assert work.queue_history[-1]["exited"] is None
```

### Test 3: Backward Compatibility (legacy WORK.md without queue_history)
```python
def test_queue_history_backward_compat(tmp_path, governance):
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    # Create legacy WORK.md without queue_history field
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-LEGACY"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text(SAMPLE_WORK_LEGACY_NO_QUEUE, encoding="utf-8")
    work = engine.get_work("WORK-LEGACY")
    assert work.queue_history == []
```

### Test 4: create_work seeds queue_history
```python
def test_create_work_seeds_queue_history(tmp_path, governance):
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-QH4", "Seed Test")
    work = engine.get_work("WORK-QH4")
    assert len(work.queue_history) == 1
    assert work.queue_history[0]["position"] == "backlog"
    assert work.queue_history[0]["entered"] is not None
    assert work.queue_history[0]["exited"] is None
```

### Test 5: close appends done to queue_history
```python
def test_close_appends_done_to_queue_history(tmp_path, governance):
    engine = WorkEngine(governance=governance, base_path=tmp_path)
    engine.create_work("WORK-QH5", "Close Test")
    engine.set_queue_position("WORK-QH5", "ready")
    engine.set_queue_position("WORK-QH5", "working")
    engine.close("WORK-QH5")
    work = engine.get_work("WORK-QH5")
    assert work.queue_history[-1]["position"] == "done"
    assert work.queue_history[-2]["position"] == "working"
    assert work.queue_history[-2]["exited"] is not None
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does.
     Future agents should be able to implement from this section alone.
     This section bridges the gap between tests (WHAT) and steps (HOW).

     MUST INCLUDE (per Session 88 enhancement):
     1. Actual current code that will be changed (copy from source)
     2. Exact diff/change to be made
     3. Function signature details with context
     4. Input/output examples with REAL data from the system

     PATTERN VERIFICATION (E2-255 Learning):
     IF creating a new module that imports from siblings:
       - MUST read at least one sibling module for import/error patterns
       - Verify: try/except conditional imports? sys.path manipulation? error types?
       - Use the SAME patterns as existing siblings (consistency > preference)

     IF modifying existing module:
       - Follow existing patterns in that file

     IF creating module with no siblings (new directory):
       - Document chosen patterns in Key Design Decisions with rationale -->

### Changes (6 touch points in work_engine.py)

**1. WorkState dataclass** (line ~106):
```diff
     node_history: List[Dict[str, Any]] = field(default_factory=list)
+    queue_history: List[Dict[str, Any]] = field(default_factory=list)
     memory_refs: List[int] = field(default_factory=list)
```

**2. `_parse_work_file()`** (line ~960):
```diff
             node_history=fm.get("node_history", []),
+            queue_history=fm.get("queue_history", []),
             memory_refs=fm.get("memory_refs", []) or [],
```

**3. `_write_work_file()`** (line ~994):
```diff
             fm["node_history"] = work.node_history
+            fm["queue_history"] = work.queue_history
             fm["memory_refs"] = work.memory_refs
```

**4. `set_queue_position()`** (line ~700, before `_write_work_file`):
```diff
             work.queue_position = position
+            # WORK-126: Append queue_history entry
+            now = datetime.now().isoformat()
+            if work.queue_history:
+                work.queue_history[-1]["exited"] = now
+            work.queue_history.append({"position": position, "entered": now, "exited": None})
             self._write_work_file(work)
```

**5. `create_work()`** (line ~321, in frontmatter dict):
```diff
             "node_history": [
                 {"node": "backlog", "entered": now.isoformat(), "exited": None}
             ],
+            "queue_history": [
+                {"position": "backlog", "entered": now.isoformat(), "exited": None}
+            ],
```

**6. `close()`** (line ~582, before `_write_work_file`):
```diff
             work.queue_position = "done"
+            # WORK-126: Append done to queue_history
+            now_str = datetime.now().isoformat()
+            if work.queue_history:
+                work.queue_history[-1]["exited"] = now_str
+            work.queue_history.append({"position": "done", "entered": now_str, "exited": None})
             self._write_work_file(work)
```

### Call Chain Context

```
execute_queue_transition()           # queue_ceremonies.py
    |
    +-> set_queue_position()         # <-- MODIFIED: appends queue_history
    |       +-> _write_work_file()   # <-- MODIFIED: persists queue_history
    |
    +-> log_queue_ceremony()         # Unchanged: external audit log
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Separate field vs reuse node_history | Separate `queue_history` | Orthogonality per REQ-QUEUE-001; queue and lifecycle are independent state machines |
| Field shape | `{position, entered, exited}` | Mirrors `node_history` shape `{node, entered, exited}` for consistency |
| Seed on create_work | Yes | New items start with `[{position: "backlog"}]` matching node_history pattern |
| close() appends done | Yes | Parallel to queue_position="done" — history should reflect terminal state |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Legacy WORK.md without queue_history | Defaults to `[]` in `_parse_work_file` | Test 3 |
| Empty queue_history on first transition | Appends without closing prior entry | Covered by create_work seeding (Test 4) |
| close() on item with no queue_history | Appends done entry directly (guard: `if work.queue_history`) | Implicit via Test 5 setup |

---

## Open Decisions (MUST resolve before implementation)

<!-- Decisions from work item's operator_decisions field.
     If ANY row has [BLOCKED] in Chosen column, plan-validation-cycle will BLOCK.

     POPULATE FROM: Work item frontmatter `operator_decisions` field
     - question -> Decision column
     - options -> Options column
     - chosen -> Chosen column (null = [BLOCKED])
     - rationale -> Rationale column (filled when resolved) -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Separate queue_history vs reuse node_history | separate, reuse, skip | separate | Operator decision S349: maintains orthogonality per E2.5 design (REQ-QUEUE-001) |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add 5 tests to `tests/test_work_engine.py`
- [ ] Verify all 5 tests fail (red) — `queue_history` attribute doesn't exist yet

### Step 2: WorkState + parse + write (structural)
- [ ] Add `queue_history` field to WorkState dataclass
- [ ] Update `_parse_work_file()` with backward compat
- [ ] Update `_write_work_file()` to persist
- [ ] Test 3 passes (backward compat: legacy WORK.md defaults to `[]`)

### Step 3: create_work + set_queue_position + close (behavioral)
- [ ] Update `create_work()` to seed initial queue_history
- [ ] Update `set_queue_position()` to append queue_history entries
- [ ] Update `close()` to append done entry
- [ ] Tests 1, 2, 4, 5 pass (green)

### Step 4: Integration Verification
- [ ] All 5 new tests pass
- [ ] Run full `test_work_engine.py` — no regressions
- [ ] Run `test_queue_ceremonies.py` — no regressions

### Step 5: README Sync
**SKIPPED:** No new files created, no directory structure changes. Existing module docstring update only.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing tests break due to new field | Low | Additive field, defaults to `[]`, no existing test asserts on queue_history absence |
| YAML serialization of queue_history list | Low | Same shape as node_history which already serializes correctly |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-126/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Investigate: should node_history track queue transitions or use separate queue_history? | [ ] | Operator decision S349: separate queue_history |
| Implement chosen approach in WorkEngine.set_queue_position() | [ ] | Code change + tests |
| Verify queue ceremony recipes produce history entries | [ ] | Integration test via test_queue_ceremonies.py |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/work_engine.py` | WorkState has queue_history, set_queue_position appends, close appends done | [ ] | |
| `tests/test_work_engine.py` | 5 new queue_history tests, all passing | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_work_engine.py -v -k "queue_history"
# Expected: 5 tests passed
pytest tests/test_work_engine.py -v
# Expected: no regressions
pytest tests/test_queue_ceremonies.py -v
# Expected: no regressions
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
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- @.claude/haios/modules/work_engine.py (set_queue_position, WorkState, create_work, close)
- @.claude/haios/lib/queue_ceremonies.py (execute_queue_transition)
- @docs/work/active/WORK-126/WORK.md
- Memory 84927: Queue transitions via justfile don't update node_history
- Memory 84154: advance_queue_to() test helper proposal
- Memory 84175: Pure additive pattern — ceremony wraps engine

---
