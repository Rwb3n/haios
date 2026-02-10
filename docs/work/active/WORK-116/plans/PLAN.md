---
template: implementation_plan
status: complete
date: 2026-02-10
backlog_id: WORK-116
title: "Adopt ceremony_context() in Ceremony Skills"
author: Hephaestus
lifecycle_phase: plan
session: 337
version: "1.5"
generated: 2026-02-10
last_updated: 2026-02-10T21:00:00
---
# Implementation Plan: Adopt ceremony_context() in Ceremony Skills

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Memory 84320-84334 loaded (CH-011/CH-012 context) |
| Document design decisions | MUST | See Key Design Decisions table |
| Ground truth metrics | MUST | File counts from Glob/Grep below |

---

## Goal

After this plan is complete, all ceremony Python modules that perform state changes will wrap those changes in `ceremony_context()`, so `check_ceremony_required()` guards in WorkEngine are satisfied and warn-mode enforcement becomes meaningful (silent when in ceremony, warning only for ungoverned mutations).

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | `queue_ceremonies.py`, `cli.py`, CH-012 spec |
| Lines of code affected | ~30 | Wrapping existing function bodies |
| New files to create | 0 | Tests added to existing `tests/test_ceremony_context.py` |
| Tests to write | 4 | See Tests First section |
| Dependencies | 1 | `governance_layer.ceremony_context` imported into 2 modules |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | 2 Python modules + 1 spec doc |
| Risk of regression | Low | ceremony_context() is additive, fail-permissive in warn mode |
| External dependencies | Low | No APIs, only internal module imports |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| Implementation | 20 min | High |
| Spec fix + verification | 10 min | High |
| **Total** | **45 min** | |

---

## Current State vs Desired State

### Current State

**queue_ceremonies.py:99-117** — `execute_queue_transition()`:
```python
def execute_queue_transition(work_engine, work_id, to_position, ceremony, ...):
    work = work_engine.get_work(work_id)
    from_position = work.queue_position
    try:
        updated_work = work_engine.set_queue_position(work_id, to_position)  # triggers guard
        log_queue_ceremony(...)
        return {"success": True, "work": updated_work}
    except ValueError as e:
        return {"success": False, "error": str(e)}
```

**cli.py:53-59** — `cmd_close()`:
```python
def cmd_close(work_id: str) -> int:
    engine = get_engine()
    try:
        path = engine.close(work_id)  # triggers guard
        print(f"Closed: {work_id} -> {path}")
        return 0
    except WorkNotFoundError:
```

**Behavior:** Every call to `set_queue_position()`, `close()`, `create_work()`, etc. triggers `check_ceremony_required()` which logs a warning because no `ceremony_context` is active. All warnings are identical noise.

**Result:** Warn-mode enforcement is a no-op — every operation warns, nothing is distinguishable.

### Desired State

**queue_ceremonies.py** — wrapped:
```python
def execute_queue_transition(work_engine, work_id, to_position, ceremony, ...):
    work = work_engine.get_work(work_id)
    from_position = work.queue_position
    try:
        with _ceremony_context_safe(f"queue-{ceremony.lower()}") as ctx:
            updated_work = work_engine.set_queue_position(work_id, to_position)
            if ctx:
                ctx.log_side_effect("queue_transition", {...})
            log_queue_ceremony(...)  # Inside block (A7: correct event ordering)
        return {"success": True, "work": updated_work}
    except ValueError as e:
        return {"success": False, "error": str(e)}
```

**cli.py** — wrapped:
```python
def cmd_close(work_id: str) -> int:
    from governance_layer import ceremony_context  # flat import (A3: runs as __main__)
    engine = get_engine()
    try:
        with ceremony_context("close-work") as ctx:
            path = engine.close(work_id)
            ctx.log_side_effect("status_changed", {"work_id": work_id, "to": "complete"})
        print(f"Closed: {work_id} -> {path}")
        return 0
```

**Behavior:** Guards see active ceremony context and stay silent. Only truly ungoverned mutations (direct WorkEngine calls without ceremony wrapping) trigger warnings.

**Result:** Warn-mode enforcement becomes meaningful — warnings signal actual governance violations.

---

## Tests First (TDD)

### Test 1: Queue transition within ceremony context produces no warning
```python
def test_execute_queue_transition_uses_ceremony_context(tmp_path, caplog):
    """execute_queue_transition wraps state change in ceremony_context."""
    import logging
    # Setup: Create work engine with test work item at backlog
    # Action: Call execute_queue_transition(engine, work_id, "ready", "Prioritize")
    # Assert: No "outside ceremony context" warning in caplog
    with caplog.at_level(logging.WARNING):
        result = execute_queue_transition(engine, work_id, "ready", "Prioritize")
    assert result["success"] is True
    assert "outside ceremony context" not in caplog.text
```

### Test 2: Queue transition logs CeremonyStart/CeremonyEnd events
```python
def test_execute_queue_transition_logs_ceremony_events(tmp_path):
    """execute_queue_transition produces CeremonyStart and CeremonyEnd events."""
    # Setup: Create work engine, read events file
    # Action: Call execute_queue_transition
    # Assert: Events file contains CeremonyStart and CeremonyEnd for queue-prioritize
    result = execute_queue_transition(engine, work_id, "ready", "Prioritize")
    events = read_events(events_file)
    ceremony_events = [e for e in events if e["type"] in ("CeremonyStart", "CeremonyEnd")]
    assert len(ceremony_events) >= 2
    assert ceremony_events[-2]["ceremony"] == "queue-prioritize"
```

### Test 3: cmd_close within ceremony context produces no warning
```python
def test_cmd_close_uses_ceremony_context(tmp_path, caplog):
    """cmd_close wraps engine.close() in ceremony_context."""
    import logging
    # Setup: Create work item via engine
    # Action: Call cmd_close(work_id)
    # Assert: No "outside ceremony context" warning
    with caplog.at_level(logging.WARNING):
        result = cmd_close(work_id)
    assert result == 0
    assert "outside ceremony context" not in caplog.text
```

### Test 4: Backward compatibility — ungoverned direct call still warns
```python
def test_direct_set_queue_position_still_warns(tmp_path, caplog):
    """Direct WorkEngine call outside ceremony_context still warns."""
    import logging
    # Setup: Create work engine
    # Action: Call engine.set_queue_position(work_id, "ready") directly (no ceremony)
    # Assert: Warning IS present
    with caplog.at_level(logging.WARNING):
        engine.set_queue_position(work_id, "ready")
    assert "outside ceremony context" in caplog.text
```

---

## Detailed Design

### Exact Code Change 1: queue_ceremonies.py

**File:** `.claude/haios/lib/queue_ceremonies.py`
**Location:** Lines 73-117 in `execute_queue_transition()`

**Current Code:**
```python
def execute_queue_transition(
    work_engine: Any,
    work_id: str,
    to_position: str,
    ceremony: str,
    rationale: Optional[str] = None,
    agent: Optional[str] = None,
) -> dict:
    work = work_engine.get_work(work_id)
    if work is None:
        return {"success": False, "error": f"Work item {work_id} not found"}

    from_position = work.queue_position

    try:
        updated_work = work_engine.set_queue_position(work_id, to_position)
        log_queue_ceremony(
            ceremony=ceremony,
            items=[work_id],
            from_position=from_position,
            to_position=to_position,
            rationale=rationale,
            agent=agent,
        )
        return {"success": True, "work": updated_work}
    except ValueError as e:
        return {"success": False, "error": str(e)}
```

**Changed Code:**
```python
def execute_queue_transition(
    work_engine: Any,
    work_id: str,
    to_position: str,
    ceremony: str,
    rationale: Optional[str] = None,
    agent: Optional[str] = None,
) -> dict:
    work = work_engine.get_work(work_id)
    if work is None:
        return {"success": False, "error": f"Work item {work_id} not found"}

    from_position = work.queue_position

    try:
        with _ceremony_context_safe(f"queue-{ceremony.lower()}") as ctx:
            updated_work = work_engine.set_queue_position(work_id, to_position)
            if ctx:
                ctx.log_side_effect("queue_transition", {
                    "work_id": work_id, "from": from_position, "to": to_position
                })
            log_queue_ceremony(
                ceremony=ceremony,
                items=[work_id],
                from_position=from_position,
                to_position=to_position,
                rationale=rationale,
                agent=agent,
            )
        return {"success": True, "work": updated_work}
    except ValueError as e:
        return {"success": False, "error": str(e)}
```

**Diff:**
```diff
+from contextlib import contextmanager
+
+
+@contextmanager
+def _ceremony_context_safe(name: str):
+    """Import and use ceremony_context with fail-permissive fallback.
+
+    Handles: ImportError (no governance module), CeremonyNestingError
+    (already inside ceremony context — reuse outer context).
+    """
+    try:
+        from governance_layer import ceremony_context, in_ceremony_context
+        if in_ceremony_context():
+            yield None  # Already inside ceremony — no-op (avoid nesting)
+        else:
+            with ceremony_context(name) as ctx:
+                yield ctx
+    except ImportError:
+        yield None  # Fail-permissive: no governance module available
+
+
 def execute_queue_transition(...):
     ...
-        updated_work = work_engine.set_queue_position(work_id, to_position)
-        log_queue_ceremony(...)
+        with _ceremony_context_safe(f"queue-{ceremony.lower()}") as ctx:
+            updated_work = work_engine.set_queue_position(work_id, to_position)
+            if ctx:
+                ctx.log_side_effect("queue_transition", {
+                    "work_id": work_id, "from": from_position, "to": to_position
+                })
+            log_queue_ceremony(...)  # Inside ceremony block (A7: correct event ordering)
```

### Exact Code Change 2: cli.py cmd_close

**File:** `.claude/haios/modules/cli.py`
**Location:** Lines 53-60 in `cmd_close()`

**Current Code:**
```python
def cmd_close(work_id: str) -> int:
    """Close work item (set complete, closed date). Per ADR-041: stays in active/."""
    engine = get_engine()
    try:
        path = engine.close(work_id)
        print(f"Closed: {work_id} -> {path}")
        return 0
    except WorkNotFoundError:
```

**Changed Code:**
```python
def cmd_close(work_id: str) -> int:
    """Close work item (set complete, closed date). Per ADR-041: stays in active/."""
    from governance_layer import ceremony_context  # flat import (A3: cli.py runs as __main__)
    engine = get_engine()
    try:
        with ceremony_context("close-work") as ctx:
            path = engine.close(work_id)
            ctx.log_side_effect("status_changed", {"work_id": work_id, "to": "complete"})
        print(f"Closed: {work_id} -> {path}")
        return 0
    except WorkNotFoundError:
```

### Exact Code Change 3: cli.py cmd_archive

**File:** `.claude/haios/modules/cli.py`
**Location:** `cmd_archive()` function

Need to check if archive is called from close-work recipe. Let me verify — `just close-work` calls `cli.py close` but not `cli.py archive` separately. The `close()` method already has the guard. Archive is separate. Will wrap if it exists as standalone path.

### Call Chain Context

```
Ceremony Skill (markdown prompt)
    |
    +-> Agent executes Python code or `just` command
    |       |
    |       +-> queue_ceremonies.execute_queue_transition()  # <-- WRAP HERE
    |       |       |
    |       |       +-> work_engine.set_queue_position()     # guard fires
    |       |
    |       +-> cli.py cmd_close()                           # <-- WRAP HERE
    |               |
    |               +-> work_engine.close()                  # guard fires
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Wrap at Python module level, not skill markdown | Python modules | Skills are markdown prompts — can't import Python. Wrapping at module level gives one integration point per state-change pathway. Module-level wrapping IS skill-level wrapping (the Python module is what the skill invokes). |
| Use `_ceremony_context_safe()` helper in queue_ceremonies | Fail-permissive wrapper with `in_ceremony_context()` check | (A1/A5) Checks if already inside ceremony context first — yields None if so, avoiding CeremonyNestingError. Falls back on ImportError. Covers both failure modes. |
| Flat import in cli.py (no dot prefix) | `from governance_layer import ceremony_context` | (A3) cli.py runs as `__main__` via `python .claude/haios/modules/cli.py`. Relative imports (`from .governance_layer`) fail in `__main__` context. Flat import matches existing pattern at line 28. |
| Ceremony names use skill-name convention | `queue-prioritize`, `close-work` etc. | Matches existing ceremony skill names, enables correlation between skill invocation and ceremony events |
| Move `log_queue_ceremony()` inside ceremony_context block | Inside block | (A7) Corrects event ordering: QueueCeremony event appears between CeremonyStart and CeremonyEnd in audit log, not after CeremonyEnd. |
| Don't modify WorkEngine guards | Keep WORK-115 implementation as-is | Guards are correct — they enforce the boundary. This work wires the callers to satisfy the boundary. |
| D4/D5/D6 coverage is transitive | Session/memory/spawn skills route through cli.py or scaffold (not guarded) | (A2/A4) `create_work()` guard fires only in tests — production creation goes through `scaffold_template()` which writes files directly. Session/memory ceremonies don't call guarded methods. |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| governance_layer import fails | `_ceremony_context_safe` yields None, operation proceeds | Covered by fail-permissive design |
| execute_queue_transition raises ValueError | ceremony_context __exit__ runs before error propagates, CeremonyEnd logged | Test 2 covers events |
| Nested queue transitions (batch Prioritize) | Each call gets its own ceremony_context, no nesting — sequential calls | No nesting since each transition is a separate function call |
| Already inside ceremony_context (A1/A5) | `_ceremony_context_safe` checks `in_ceremony_context()` first, yields None if already active | Avoids CeremonyNestingError |
| cmd_close called outside skill (manual `just close-work`) | Still wrapped — ceremony_context is in the Python path | Test 3 covers |
| Future skill-level wrapping added on top (A5) | `_ceremony_context_safe` no-ops, outer context used | Protected by `in_ceremony_context()` check |

### Open Questions

**Q: Should `cmd_archive()` also be wrapped?**
**RESOLVED:** Yes. `cmd_archive()` exists at cli.py:65 as standalone path (`cli.py archive <id>`). `engine.archive()` has guard at line 619. Will wrap in `ceremony_context("archive-work")`.

**Q: Should `cmd_transition()` also be wrapped?**
**RESOLVED:** Yes. `cmd_transition()` exists at cli.py:38 as standalone path (`cli.py transition <id> <node>`). `engine.transition()` has guard at line 348. Will wrap in `ceremony_context("transition-work")`.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | - | - | All design decisions resolved above |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 4 tests to `tests/test_ceremony_context.py`
- [ ] Verify all 4 tests fail (red) — queue/close operations produce warnings

### Step 2: Wrap queue_ceremonies.execute_queue_transition
- [ ] Add `_ceremony_context_safe()` helper to queue_ceremonies.py
- [ ] Wrap `set_queue_position()` call in `ceremony_context`
- [ ] Tests 1, 2 pass (green)

### Step 3: Wrap cli.py cmd_close, cmd_archive, cmd_transition
- [ ] Add `ceremony_context` import to relevant functions
- [ ] Wrap `engine.close()` in `ceremony_context("close-work")`
- [ ] Wrap `engine.archive()` in `ceremony_context("archive-work")` if standalone
- [ ] Wrap `engine.transition()` in `ceremony_context("transition-work")` if standalone
- [ ] Test 3 passes (green)

### Step 4: Fix CH-012 spec naming drift
- [ ] Read CH-012 spec, find `update_work()` references
- [ ] Replace with actual WorkEngine API: `close()`, `create_work()`, `archive()`, `set_queue_position()`, `transition()`

### Step 5: Integration Verification
- [ ] All 4 new tests pass
- [ ] Run full test suite — no regressions
- [ ] Demo: run `execute_queue_transition` and verify no warning in logs

### Step 6: README Sync (MUST)
- [ ] Check if lib/ or modules/ READMEs need update (new import)

### Step 7: Consumer Verification
- [ ] Grep for any other direct WorkEngine state-change calls outside ceremony_context
- [ ] Verify `_ceremony_context_safe` pattern is consistent

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Import cycle between lib/ and modules/ | Medium | `_ceremony_context_safe` uses lazy import with try/except |
| CeremonyNestingError if future skill-level wrapping added (A1/A5) | Medium | `_ceremony_context_safe` checks `in_ceremony_context()` before entering — yields None if already active |
| Relative import in cli.py fails at runtime (A3) | High | Use flat import `from governance_layer import ...` matching existing line 28 pattern |
| Performance overhead of context manager | Low | ceremony_context is lightweight (contextvars + event log) |
| Duplicate `_append_event` across modules (A8) | Low | Pre-existing, out of scope. Noted for future cleanup. Both resolve to same file currently. |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 337 | 2026-02-10 | - | Plan authored | |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-116/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Identify all ceremony skills with state-changing operations | [ ] | Grep + analysis |
| ceremony_context in closure ceremony skills | [ ] | cli.py cmd_close wrapping |
| ceremony_context in queue ceremony skills | [ ] | queue_ceremonies.py wrapping |
| ceremony_context in session ceremony skills | [ ] | session skills use justfile recipes that call cli.py |
| ceremony_context in memory ceremony skills | [ ] | memory skills call ingester_ingest (read-only, may be N/A) |
| ceremony_context in spawn-work-ceremony | [ ] | spawn creates via work_engine.create_work (cli.py path) |
| Update CH-012 spec naming drift | [ ] | Replace update_work() refs |
| Tests: CeremonyStart/CeremonyEnd events | [ ] | Test 2 |
| Tests: warn-mode silent inside ceremony_context | [ ] | Test 1, 3 |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/queue_ceremonies.py` | `_ceremony_context_safe` + wrapped transition | [ ] | |
| `.claude/haios/modules/cli.py` | `cmd_close`, `cmd_archive`, `cmd_transition` wrapped | [ ] | |
| `tests/test_ceremony_context.py` | 4 new tests passing | [ ] | |
| `.claude/haios/epochs/E2_5/arcs/ceremonies/CH-012-SideEffectBoundaries.md` | No `update_work()` refs | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_ceremony_context.py -v
# Expected: all tests pass
```

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** — ceremony skills invoke queue_ceremonies and cli.py
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories
- [ ] **MUST:** Consumer verification complete
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-012-SideEffectBoundaries.md
- @docs/work/active/WORK-115/WORK.md
- @.claude/haios/modules/governance_layer.py
- @.claude/haios/lib/queue_ceremonies.py
- @docs/checkpoints/2026-02-10-01-SESSION-336-work-115-plan-approved.md

---
