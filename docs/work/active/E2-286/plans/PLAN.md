---
template: implementation_plan
status: approved
date: 2026-01-12
backlog_id: E2-286
title: Add session_state to haios-status-slim.json
author: Hephaestus
lifecycle_phase: plan
session: 189
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-12T01:40:33'
---
# Implementation Plan: Add session_state to haios-status-slim.json

@docs/README.md
@docs/epistemic_state.md

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

HAIOS will have session-level cycle tracking via a `session_state` section in haios-status-slim.json, enabling UserPromptSubmit hooks to detect when work is attempted outside an active cycle.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/lib/status.py` |
| Lines of code affected | ~20 | Add session_state to generate_slim_status() |
| New files to create | 0 | Schema extension only |
| Tests to write | 2 | Test session_state schema, test default values |
| Dependencies | 0 | No new imports required |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single file modification, self-contained change |
| Risk of regression | Low | Additive change - existing fields unchanged |
| External dependencies | Low | No external APIs |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 10 min | High |
| Implement schema extension | 15 min | High |
| Verify integration | 5 min | High |
| **Total** | 30 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/lib/status.py:935-957 - generate_slim_status()
slim = {
    "generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    "milestone": milestone_data,
    "session_delta": session_delta_slim,
    "work_cycle": work_cycle,  # E2-118: Active work cycle context
    "active_work": active_work,
    "blocked_items": blocked_dict,
    "counts": {...},
    "infrastructure": {...},
}
```

**Behavior:** Status includes `work_cycle` (work item lifecycle) but no session-level cycle tracking

**Result:** Hooks cannot detect when agent is working outside an active governance cycle (survey-cycle, implementation-cycle, etc.)

### Desired State

```python
# .claude/lib/status.py:935-957 - generate_slim_status() after change
slim = {
    "generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    "milestone": milestone_data,
    "session_delta": session_delta_slim,
    "work_cycle": work_cycle,
    "session_state": {  # NEW: Session-level cycle tracking
        "active_cycle": None,       # e.g., "implementation-cycle"
        "current_phase": None,      # e.g., "DO", "CHECK"
        "work_id": None,           # e.g., "E2-286"
        "entered_at": None,        # ISO8601 timestamp
    },
    "active_work": active_work,
    "blocked_items": blocked_dict,
    "counts": {...},
    "infrastructure": {...},
}
```

**Behavior:** Status includes `session_state` tracking which cycle the agent is in

**Result:** UserPromptSubmit hook (E2-287) can warn when work detected outside active cycle

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Session State Schema Present in Slim Status
```python
def test_session_state_in_slim_status():
    """Verify generate_slim_status() includes session_state section."""
    from status import generate_slim_status

    slim = generate_slim_status()

    assert "session_state" in slim
    assert isinstance(slim["session_state"], dict)
    # Verify all required fields present
    assert "active_cycle" in slim["session_state"]
    assert "current_phase" in slim["session_state"]
    assert "work_id" in slim["session_state"]
    assert "entered_at" in slim["session_state"]
```

### Test 2: Session State Default Values Are Null
```python
def test_session_state_default_values():
    """Verify session_state fields default to None when no cycle active."""
    from status import generate_slim_status

    slim = generate_slim_status()

    # Default state: no active cycle
    assert slim["session_state"]["active_cycle"] is None
    assert slim["session_state"]["current_phase"] is None
    assert slim["session_state"]["work_id"] is None
    assert slim["session_state"]["entered_at"] is None
```

### Test 3: Backward Compatibility - Existing Fields Unchanged
```python
def test_existing_fields_unchanged():
    """Verify existing slim status fields are not affected."""
    from status import generate_slim_status

    slim = generate_slim_status()

    # All existing top-level keys must be present
    assert "generated" in slim
    assert "milestone" in slim
    assert "session_delta" in slim
    assert "work_cycle" in slim
    assert "active_work" in slim
    assert "blocked_items" in slim
    assert "counts" in slim
    assert "infrastructure" in slim
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

### Exact Code Change

**File:** `.claude/lib/status.py`
**Location:** Lines 935-957 in `generate_slim_status()`

**Current Code:**
```python
# .claude/lib/status.py:935-957
slim = {
    "generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    "milestone": milestone_data,
    "session_delta": session_delta_slim,
    "work_cycle": work_cycle,  # E2-118: Active work cycle context
    "active_work": active_work,
    "blocked_items": blocked_dict,
    "counts": {
        "concepts": memory_stats.get("concepts", 0),
        "entities": memory_stats.get("entities", 0),
        "backlog_pending": backlog_stats.get("active_count", 0),
    },
    "infrastructure": {
        "commands": commands,
        "skills": skills,
        "agents": agents,
        "mcps": [
            {"name": "haios-memory", "tools": 13},
            {"name": "context7", "tools": 2},
        ],
    },
}
```

**Changed Code:**
```python
# .claude/lib/status.py:935-963 - After change
slim = {
    "generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    "milestone": milestone_data,
    "session_delta": session_delta_slim,
    "work_cycle": work_cycle,  # E2-118: Active work cycle context
    "session_state": {  # E2-286: Session-level cycle tracking
        "active_cycle": None,       # e.g., "implementation-cycle"
        "current_phase": None,      # e.g., "DO", "CHECK"
        "work_id": None,           # e.g., "E2-286"
        "entered_at": None,        # ISO8601 timestamp
    },
    "active_work": active_work,
    "blocked_items": blocked_dict,
    "counts": {
        "concepts": memory_stats.get("concepts", 0),
        "entities": memory_stats.get("entities", 0),
        "backlog_pending": backlog_stats.get("active_count", 0),
    },
    "infrastructure": {
        "commands": commands,
        "skills": skills,
        "agents": agents,
        "mcps": [
            {"name": "haios-memory", "tools": 13},
            {"name": "context7", "tools": 2},
        ],
    },
}
```

**Diff:**
```diff
     "session_delta": session_delta_slim,
     "work_cycle": work_cycle,  # E2-118: Active work cycle context
+    "session_state": {  # E2-286: Session-level cycle tracking
+        "active_cycle": None,       # e.g., "implementation-cycle"
+        "current_phase": None,      # e.g., "DO", "CHECK"
+        "work_id": None,           # e.g., "E2-286"
+        "entered_at": None,        # ISO8601 timestamp
+    },
     "active_work": active_work,
```

### Call Chain Context

```
just update-status
    |
    +-> status.py generate_slim_status()  # <-- What we're changing
    |       Returns: dict (slim status structure)
    |
    +-> write_slim_status() -> haios-status-slim.json
    |
    +-> UserPromptSubmit hook reads haios-status-slim.json
            |
            +-> E2-287: Will read session_state for warnings
```

### Function/Component Signatures

```python
# No signature change - internal structure addition
def generate_slim_status() -> dict[str, Any]:
    """Generate slim status structure for haios-status-slim.json.

    This is the main orchestrator that calls all core functions.

    Returns:
        Dict matching haios-status-slim.json structure.
        Now includes 'session_state' section for cycle tracking.
    """
```

### Behavior Logic

**Current Flow:**
```
generate_slim_status() → builds dict → no session cycle info → hooks blind to cycle state
```

**Fixed Flow:**
```
generate_slim_status() → builds dict with session_state
                              |
                              +-> active_cycle = None (default)
                              +-> current_phase = None (default)
                              +-> work_id = None (default)
                              +-> entered_at = None (default)
                              |
                      → UserPromptSubmit hook can check session_state
                              |
                              +-> E2-287: warn if work outside cycle
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| State location | haios-status-slim.json | INV-062 H1 confirmed - hooks already read this file; single source of truth (Memory 81307) |
| Default values | All None | No cycle active initially; E2-288 will populate via `just set-cycle` |
| Field structure | Flat dict with 4 fields | Matches work_cycle pattern; active_cycle, current_phase, work_id, entered_at |
| No state loading function | Defer to E2-288 | This work item adds schema only; state management is separate concern |

### Input/Output Examples

**Current haios-status-slim.json (real data):**
```json
{
    "generated": "2026-01-12T01:32:54",
    "milestone": {...},
    "session_delta": {...},
    "work_cycle": {
        "id": "E2-279",
        "title": "WorkEngine Decomposition",
        "current_node": "plan",
        "cycle_type": "implementation",
        "lifecycle_phase": null
    },
    "active_work": [],
    "blocked_items": {},
    "counts": {...},
    "infrastructure": {...}
}
```
**Problem:** No session-level cycle tracking - only work_cycle (which tracks work item lifecycle, not governance cycles)

**After fix (expected):**
```json
{
    "generated": "2026-01-12T01:32:54",
    "milestone": {...},
    "session_delta": {...},
    "work_cycle": {...},
    "session_state": {
        "active_cycle": null,
        "current_phase": null,
        "work_id": null,
        "entered_at": null
    },
    "active_work": [],
    "blocked_items": {},
    "counts": {...},
    "infrastructure": {...}
}
```
**Improvement:** E2-287 UserPromptSubmit hook can now check `session_state.active_cycle` and warn if null when work detected

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No cycle active | All fields None | Test 2 |
| First status generation | session_state with all None | Test 1, Test 2 |
| Existing JSON file | session_state added on next refresh | Manual verify |

### Open Questions

**Q: Should session_state persist across status refreshes?**

Answer: No. This work item adds schema with defaults only. E2-288 (`just set-cycle`) will handle reading/preserving state during refresh. For now, defaults are regenerated each refresh - acceptable until E2-288 completes.

---

## Open Decisions (MUST resolve before implementation)

<!-- No operator_decisions in work item - INV-062 already resolved all design questions -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| *None* | - | - | All design decisions resolved in INV-062 investigation |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add tests to `tests/test_status.py` (or create if missing)
- [ ] Add `test_session_state_in_slim_status()`
- [ ] Add `test_session_state_default_values()`
- [ ] Add `test_existing_fields_unchanged()`
- [ ] Verify all 3 tests fail (red)

### Step 2: Add session_state to generate_slim_status()
- [ ] Edit `.claude/lib/status.py` lines 935-957
- [ ] Add `session_state` dict after `work_cycle` key
- [ ] Fields: active_cycle, current_phase, work_id, entered_at (all None)
- [ ] Tests 1, 2, 3 pass (green)

### Step 3: Integration Verification
- [ ] Run `pytest tests/test_status.py -v`
- [ ] Run `just update-status`
- [ ] Verify `haios-status-slim.json` contains `session_state` section

### Step 4: README Sync (MUST)
- [ ] **SKIPPED:** No new files created, no README updates needed
- [ ] Schema change documented in plan - no separate README

### Step 5: Consumer Verification (MUST for migrations/refactors)
- [ ] **SKIPPED:** Additive change - no existing consumers affected
- [ ] E2-287 (UserPromptSubmit warning) is downstream consumer - not yet implemented

**Note:** This is an additive schema change. No migration, no rename, no consumer updates needed.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| State not persisted on refresh | Low | Expected behavior for E2-286; E2-288 handles state persistence |
| Hook doesn't read new field | Medium | Verify JSON structure matches expected schema before E2-287 |
| Spec misalignment | Low | INV-062 provides clear schema spec with rationale |
| Regression in status generation | Low | Test 3 verifies existing fields unchanged |

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

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/status.py` | `session_state` dict in generate_slim_status() | [ ] | |
| `tests/test_status.py` | 3 tests for session_state | [ ] | |
| `.claude/haios-status-slim.json` | `session_state` section present after refresh | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_status.py -v -k session_state
# Expected: 3 tests passed

just update-status
# Expected: haios-status-slim.json refreshed with session_state
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
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.

---

## References

- INV-062: Session State Tracking and Cycle Enforcement Architecture (spawned this work)
- Memory 81307: Architecture Decision - State location in haios-status-slim.json
- Memory 81304: H1 Confirmed - Session state can live in haios-status-slim.json
- `.claude/lib/status.py`: Target implementation file
- `.claude/haios-status-slim.json`: Output file with new schema

---
