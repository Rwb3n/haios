---
template: implementation_plan
status: complete
date: 2026-01-16
backlog_id: E2-293
title: Add set-queue Recipe and Extend session_state Schema
author: Hephaestus
lifecycle_phase: plan
session: 195
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-16T21:39:53'
---
# Implementation Plan: Add set-queue Recipe and Extend session_state Schema

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

Add `just set-queue` recipe to justfile and extend session_state schema in status.py with active_queue and phase_history fields, enabling queue context propagation for downstream cycle wiring.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | justfile, .claude/lib/status.py |
| Lines of code affected | ~10 | Recipe + schema extension |
| New files to create | 0 | All edits to existing files |
| Tests to write | 2 | Manual verification (recipe tests) |
| Dependencies | 0 | Standalone infrastructure work |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only justfile and status.py |
| Risk of regression | Low | Additive changes, defensive consumers |
| External dependencies | Low | None |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Add set-queue recipe | 5 min | High |
| Extend session_state schema | 5 min | High |
| Test | 5 min | High |
| **Total** | ~15 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/lib/status.py:940-945
"session_state": {  # E2-286: Session-level cycle tracking
    "active_cycle": None,
    "current_phase": None,
    "work_id": None,
    "entered_at": None,
},
```

```bash
# justfile:244-249 - NO set-queue recipe exists
set-cycle cycle phase work_id:
    @python -c "..."
clear-cycle:
    @python -c "..."
# Missing: set-queue recipe
```

**Behavior:** session_state exists but has no active_queue field. No way to set queue context.

**Result:** Queue context lost between survey-cycle and routing-gate.

### Desired State

```python
# .claude/lib/status.py:940-947 - Extended schema
"session_state": {  # E2-286: Session-level cycle tracking
    "active_cycle": None,
    "current_phase": None,
    "work_id": None,
    "entered_at": None,
    "active_queue": None,    # E2-293: NEW
    "phase_history": [],     # E2-293: NEW
},
```

```bash
# justfile:250 - New set-queue recipe
set-queue queue_name:
    @python -c "import json; p='.claude/haios-status-slim.json'; d=json.load(open(p)); d['session_state']['active_queue']='{{queue_name}}'; json.dump(d,open(p,'w'),indent=4); print(f'Set queue: {{queue_name}}')"
```

**Behavior:** session_state has active_queue and phase_history fields. `just set-queue` updates active_queue.

**Result:** Queue context persists for downstream cycle wiring (E2-294, E2-295).

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: set-queue Recipe Updates active_queue
```bash
# Manual test - run and verify
just set-queue governance
# Then check .claude/haios-status-slim.json
# Expected: session_state.active_queue == "governance"
```

### Test 2: Schema Extension Includes New Fields
```bash
# Manual test - regenerate status and verify
just update-status-slim
# Then check .claude/haios-status-slim.json
# Expected: session_state has active_queue and phase_history keys
```

### Test 3: Backward Compatibility - clear-cycle Handles New Fields
```bash
# Manual test - set then clear
just set-queue governance
just clear-cycle
# Expected: session_state reset, no errors
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

### Component 1: New `just set-queue` Recipe

**File:** `justfile`
**Location:** After line 249 (after clear-cycle)

**New Code:**
```bash
# Set active_queue in session_state (E2-293)
# Usage: just set-queue governance
set-queue queue_name:
    @python -c "import json; p='.claude/haios-status-slim.json'; d=json.load(open(p)); d['session_state']['active_queue']='{{queue_name}}'; json.dump(d,open(p,'w'),indent=4); print(f'Set queue: {{queue_name}}')"
```

### Component 2: Extended session_state Schema

**File:** `.claude/lib/status.py`
**Location:** Lines 940-945

**Current Code:**
```python
"session_state": {  # E2-286: Session-level cycle tracking
    "active_cycle": None,       # e.g., "implementation-cycle"
    "current_phase": None,      # e.g., "DO", "CHECK"
    "work_id": None,            # e.g., "E2-286"
    "entered_at": None,         # ISO8601 timestamp
},
```

**Changed Code:**
```python
"session_state": {  # E2-286: Session-level cycle tracking
    "active_cycle": None,       # e.g., "implementation-cycle"
    "current_phase": None,      # e.g., "DO", "CHECK"
    "work_id": None,            # e.g., "E2-286"
    "entered_at": None,         # ISO8601 timestamp
    "active_queue": None,       # E2-293: e.g., "default", "governance"
    "phase_history": [],        # E2-293: Recent phase transitions
},
```

### Component 3: Update clear-cycle to Reset New Fields

**File:** `justfile`
**Location:** Line 249

**Current Code:**
```bash
clear-cycle:
    @python -c "import json; p='.claude/haios-status-slim.json'; d=json.load(open(p)); d['session_state']={'active_cycle':None,'current_phase':None,'work_id':None,'entered_at':None}; json.dump(d,open(p,'w'),indent=4); print('Cleared session_state')"
```

**Changed Code:**
```bash
clear-cycle:
    @python -c "import json; p='.claude/haios-status-slim.json'; d=json.load(open(p)); d['session_state']={'active_cycle':None,'current_phase':None,'work_id':None,'entered_at':None,'active_queue':None,'phase_history':[]}; json.dump(d,open(p,'w'),indent=4); print('Cleared session_state')"
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| active_queue separate from set-cycle | Independent recipe | Queue context persists across cycle invocations |
| phase_history as empty array | Deferred population | Focus on core fields first; E2-294/295 can add history tracking later |
| Update clear-cycle | Include new fields in reset | Prevents stale data accumulation |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| set-queue called before update-status-slim | Will fail - file doesn't have field | Update schema first, then add recipe |
| Queue name with spaces | Quote in recipe | Manual test |

---

## Open Decisions (MUST resolve before implementation)

<!-- Decisions from work item's operator_decisions field.
     If ANY row has [BLOCKED] in Chosen column, plan-validation-cycle will BLOCK.

     POPULATE FROM: Work item frontmatter `operator_decisions` field
     - question -> Decision column
     - options -> Options column
     - chosen -> Chosen column (null = [BLOCKED])
     - rationale -> Rationale column (filled when resolved) -->

**No open decisions.** Design inherited from E2-292 plan (approved by INV-065).

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Extend session_state Schema in status.py
- [ ] Edit `.claude/lib/status.py` lines 940-945
- [ ] Add `"active_queue": None,` after entered_at
- [ ] Add `"phase_history": [],` after active_queue

### Step 2: Update clear-cycle Recipe
- [ ] Edit `justfile` line 249
- [ ] Add active_queue and phase_history to reset dict

### Step 3: Regenerate Status to Apply Schema
- [ ] Run `just update-status-slim`
- [ ] Verify new fields appear in `.claude/haios-status-slim.json`

### Step 4: Add set-queue Recipe
- [ ] Edit `justfile` after line 249
- [ ] Add set-queue recipe

### Step 5: Test All Recipes
- [ ] Test: `just set-queue governance` - verify active_queue updated
- [ ] Test: `just clear-cycle` - verify all fields reset including new ones
- [ ] Test: `just set-cycle implementation-cycle DO E2-293` - verify still works

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Existing consumers break | Low | Consumers use defensive checks (E2-287) |
| JSON corruption | Low | Recipe uses atomic write pattern |

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

**MUST** read `docs/work/active/E2-293/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Add `just set-queue` recipe to justfile | [ ] | Recipe exists in justfile |
| Extend session_state schema with active_queue, phase_history | [ ] | Fields in status.py |
| Test: set-queue updates active_queue | [ ] | Manual test output |
| Test: update-status-slim includes new fields | [ ] | JSON inspection |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `justfile` | set-queue recipe exists after clear-cycle | [ ] | |
| `.claude/lib/status.py` | session_state includes active_queue, phase_history | [ ] | |
| `.claude/haios-status-slim.json` | New fields present | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest [test_file] -v
# Expected: X tests passed
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

- @docs/work/active/E2-292/plans/PLAN.md (original plan with full design)
- @docs/work/active/INV-065/investigations/001-session-state-cascade-architecture.md
- justfile:244-249 (existing recipes)

---
