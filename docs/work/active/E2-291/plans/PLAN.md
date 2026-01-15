---
template: implementation_plan
status: complete
date: 2026-01-15
backlog_id: E2-291
title: Wire Queue into Survey-Cycle and Routing-Gate
author: Hephaestus
lifecycle_phase: plan
session: 193
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-15T23:07:55'
---
# Implementation Plan: Wire Queue into Survey-Cycle and Routing-Gate

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

Survey-cycle and routing-gate will use WorkEngine queue methods (`get_queue()`, `is_cycle_allowed()`) for queue-aware work selection and cycle-locking enforcement.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | justfile, survey-cycle/SKILL.md, routing-gate/SKILL.md |
| Lines of code affected | ~50 | 2 recipes + skill updates |
| New files to create | 0 | N/A |
| Tests to write | 1 | Extend test_work_queues.py |
| Dependencies | 1 | work_engine.py (already tested) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Recipes call existing methods |
| Risk of regression | Low | Existing ready recipe preserved |
| External dependencies | Low | No APIs, uses existing modules |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Add justfile recipes | 15 min | High |
| Update skill files | 20 min | High |
| Test and demo | 10 min | High |
| **Total** | 45 min | High |

---

## Current State vs Desired State

### Current State

**survey-cycle (SKILL.md:22-24):**
```markdown
2. **Otherwise, present options**
   - Run `just ready` for unblocked items
   - Select top 3 by priority + chapter alignment
```

**routing-gate (SKILL.md:57-68):**
```markdown
1. Query next work: `just ready`
2. Read first work file, check `documents.plans` field
3. Apply the decision table above:
   - `next_work_id` is None → `await_operator`
   - ID starts with `INV-` → `invoke_investigation`
   - `has_plan` is True → `invoke_implementation`
   - Otherwise → `invoke_work_creation`
4. Execute the corresponding skill invocation
```

**Behavior:** Flat list from `just ready`, no queue awareness, no cycle-locking

**Result:** Queue infrastructure (E2-290) has no runtime consumers

### Desired State

**survey-cycle:**
```markdown
2. **Otherwise, present options**
   - Run `just queue [name]` for ordered items from queue
   - If no queue specified, use "default"
   - Select top 3 from queue head
```

**routing-gate:**
```markdown
1. Query next work: `just queue [name]` (or `just ready` for backward compat)
2. Check `just is-cycle-allowed [queue] [cycle]`
3. If BLOCKED: return warning with reason
4. If ALLOWED: apply decision table and invoke cycle
```

**Behavior:** Queue-aware selection, cycle-locking enforced

**Result:** Queue infrastructure wired into governance flow

---

## Tests First (TDD)

### Test 1: Queue recipe returns ordered items
```bash
# Manual test - run after adding recipe
just queue governance
# Expected: E2-291, INV-054, INV-041, E2-164 (governance queue order)
```

### Test 2: is-cycle-allowed recipe checks locking
```bash
# Test allowed cycle
just is-cycle-allowed governance implementation-cycle
# Expected: ALLOWED

# Test blocked cycle
just is-cycle-allowed governance work-creation-cycle
# Expected: BLOCKED
```

### Test 3: Python test for cycle enforcement
```python
# tests/test_work_queues.py
def test_queue_cycle_enforcement():
    """E2-291: Queue cycle-locking works end-to-end."""
    engine = WorkEngine(GovernanceLayer())

    # governance queue has allowed_cycles: [implementation-cycle, investigation-cycle]
    assert engine.is_cycle_allowed("governance", "implementation-cycle") == True
    assert engine.is_cycle_allowed("governance", "investigation-cycle") == True
    assert engine.is_cycle_allowed("governance", "work-creation-cycle") == False
```

### Test 4: Backward Compatibility
```bash
# Existing recipe still works
just ready
# Expected: Returns flat unordered list (unchanged behavior)
```

---

## Detailed Design

### Change 1: Add `just queue` recipe

**File:** `justfile`
**Location:** After `ready` recipe (around line 90)

**New Code:**
```just
# Get ordered items from named queue (E2-291)
queue name="default":
    python -c "import sys; sys.path.insert(0, '.claude/haios/modules'); from work_engine import WorkEngine; from governance_layer import GovernanceLayer; e=WorkEngine(GovernanceLayer()); q=e.get_queue('{{name}}'); print('\n'.join([f'{w.id}: {w.title}' for w in q]))"
```

### Change 2: Add `just is-cycle-allowed` recipe

**File:** `justfile`
**Location:** After `queue` recipe

**New Code:**
```just
# Check if cycle is allowed for queue (E2-291)
is-cycle-allowed queue_name cycle_name:
    python -c "import sys; sys.path.insert(0, '.claude/haios/modules'); from work_engine import WorkEngine; from governance_layer import GovernanceLayer; e=WorkEngine(GovernanceLayer()); allowed=e.is_cycle_allowed('{{queue_name}}', '{{cycle_name}}'); print('ALLOWED' if allowed else 'BLOCKED')"
```

### Change 3: Update survey-cycle SKILL.md

**File:** `.claude/skills/survey-cycle/SKILL.md`
**Location:** Lines 21-24 (step 2)

**Current:**
```markdown
2. **Otherwise, present options**
   - Run `just ready` for unblocked items
   - Select top 3 by priority + chapter alignment
   - Present via `AskUserQuestion` (or auto-select if autonomous)
```

**Changed:**
```markdown
2. **Otherwise, present options**
   - Run `just queue [name]` for ordered items (default: "default" queue)
   - Alternatively: `just ready` for flat unordered list (backward compat)
   - Select top 3 from queue head
   - Present via `AskUserQuestion` (or auto-select if autonomous)
```

### Change 4: Update routing-gate SKILL.md

**File:** `.claude/skills/routing-gate/SKILL.md`
**Location:** Insert before decision table (after line 41)

**New Section:**
```markdown
## Cycle-Locking Check (E2-291)

**Before applying the decision table, check cycle-locking:**

1. Determine active queue (from survey-cycle context or "default")
2. Run `just is-cycle-allowed [queue] [cycle]`
3. If BLOCKED:
   - Return `{action: "blocked", reason: "Queue [name] only allows [cycles]"}`
   - Display warning:
     ```
     WARNING: Cycle '[cycle]' is blocked for queue '[queue]'.
     Allowed cycles: [list]
     Queue rationale: "[from config]"
     ```
4. If ALLOWED: continue to decision table
```

**Update Decision Table:**
Add new row at top:
```markdown
| Cycle blocked by queue | `blocked` | None - display warning |
```

### Call Chain Context

```
coldstart
    |
    +-> survey-cycle
    |       Uses: just queue [name]
    |       Returns: selected work_id
    |
    +-> routing-gate
    |       Uses: just is-cycle-allowed [queue] [cycle]
    |       Returns: {action, reason}
    |
    +-> implementation-cycle / investigation-cycle / work-creation-cycle
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Keep `just ready` | Preserved | Backward compatibility - existing flows work unchanged |
| Recipes vs direct Python | Recipes | Skills are markdown, can't call Python directly |
| Queue name as parameter | Optional with default | Most cases use "default", explicit naming for special queues |
| Warning format | Structured text | Clear, parseable, includes rationale from config |

### Input/Output Examples

**Real Example - governance queue:**
```bash
# Current: just ready (flat, unordered)
just ready
# Returns: E2-291, INV-054, E2-164, INV-041, ... (43 items, no order)

# After: just queue governance (ordered by priority)
just queue governance
# Returns:
# E2-291: Wire Queue into Survey-Cycle and Routing-Gate
# INV-054: Validation Cycle Fitness for Purpose
# INV-041: Single Source Path Constants Architecture
# E2-164: Coldstart L1 Context Review
```

**Real Example - cycle-locking:**
```bash
# governance queue config:
# allowed_cycles: [implementation-cycle, investigation-cycle]

just is-cycle-allowed governance implementation-cycle
# Returns: ALLOWED

just is-cycle-allowed governance work-creation-cycle
# Returns: BLOCKED
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Queue doesn't exist | Fallback to get_ready() | Existing test |
| Empty allowed_cycles | All cycles allowed | Test 3 |
| Item not in any explicit queue | Falls into "default" auto-populated | Test 1 |

---

## Open Decisions (MUST resolve before implementation)

**SKIPPED:** No operator decisions required - design is fully specified in INV-064.

---

## Implementation Steps

### Step 1: Add test to test_work_queues.py
- [ ] Add `test_queue_cycle_enforcement` function
- [ ] Verify test passes (uses existing methods)

### Step 2: Add `just queue` recipe
- [ ] Add recipe to justfile after `ready` recipe
- [ ] Test: `just queue` returns default queue items
- [ ] Test: `just queue governance` returns governance queue items

### Step 3: Add `just is-cycle-allowed` recipe
- [ ] Add recipe to justfile after `queue` recipe
- [ ] Test: `just is-cycle-allowed governance implementation-cycle` returns ALLOWED
- [ ] Test: `just is-cycle-allowed governance work-creation-cycle` returns BLOCKED

### Step 4: Update survey-cycle SKILL.md
- [ ] Replace `just ready` reference with `just queue [name]`
- [ ] Add note about backward compat with `just ready`

### Step 5: Update routing-gate SKILL.md
- [ ] Add "Cycle-Locking Check" section before decision table
- [ ] Add `blocked` action to decision table
- [ ] Document warning message format

### Step 6: Demo blocked cycle warning
- [ ] Show warning output when cycle is blocked
- [ ] Verify message includes allowed cycles and rationale

---

## Verification

- [ ] `pytest tests/test_work_queues.py -v` passes
- [ ] `just queue` works
- [ ] `just is-cycle-allowed` works
- [ ] survey-cycle SKILL.md references queue
- [ ] routing-gate SKILL.md has cycle-locking section

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking `just ready` | Medium | Keep ready recipe unchanged, queue is additive |
| Agent ignores cycle-locking | Low | Soft enforcement expected; hard enforcement in E4 (SDK) |
| Queue config missing | Low | Fallback to get_ready() (tested in E2-290) |

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

**MUST** read `docs/work/active/E2-291/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Update survey-cycle to use `get_queue()` instead of `just ready` | [ ] | Read SKILL.md, find `just queue` reference |
| Update routing-gate to call `is_cycle_allowed()` before invoking cycles | [ ] | Read SKILL.md, find cycle-locking section |
| Add queue name parameter to survey-cycle (default: "default") | [ ] | Read SKILL.md, find `[name]` parameter |
| Tests for cycle-locking enforcement in routing | [ ] | Run pytest, see test pass |
| Demo: blocked cycle shows warning message | [ ] | Run `just is-cycle-allowed governance work-creation-cycle`, see BLOCKED |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `justfile` | Has `queue` and `is-cycle-allowed` recipes | [ ] | |
| `.claude/skills/survey-cycle/SKILL.md` | References `just queue` | [ ] | |
| `.claude/skills/routing-gate/SKILL.md` | Has cycle-locking section | [ ] | |
| `tests/test_work_queues.py` | Has `test_queue_cycle_enforcement` | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_work_queues.py -v
# Expected: All tests pass including test_queue_cycle_enforcement

just queue governance
# Expected: Lists governance queue items in order

just is-cycle-allowed governance work-creation-cycle
# Expected: BLOCKED
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

- @docs/work/active/INV-064/investigations/001-work-hierarchy-rename-and-queue-architecture.md (source design)
- @docs/work/archive/E2-290/WORK.md (queue infrastructure - prerequisite)
- @.claude/haios/config/work_queues.yaml (queue configuration)

---
