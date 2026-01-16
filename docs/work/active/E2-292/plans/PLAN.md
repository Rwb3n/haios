---
template: implementation_plan
status: approved
date: 2026-01-16
backlog_id: E2-292
title: Wire set-cycle Recipe Calls into Cycle Skills
author: Hephaestus
lifecycle_phase: plan
session: 194
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-16T21:01:58'
---
# Implementation Plan: Wire set-cycle Recipe Calls into Cycle Skills

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

Session state in haios-status-slim.json will be live-updated by cycle skills via explicit `just set-cycle`, `just set-queue`, and `just clear-cycle` recipe calls, enabling queue context propagation and phase observability.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 6 | 5 cycle skills + justfile |
| Lines of code affected | ~1004 | `Glob(".claude/skills/*-cycle/SKILL.md")` |
| New files to create | 0 | All edits to existing files |
| Tests to write | 1 | Integration test for session_state update |
| Dependencies | 2 | haios-status-slim.json, user_prompt_submit.py |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Skills are markdown, recipes are isolated |
| Risk of regression | Low | Adding calls, not changing logic |
| External dependencies | Low | Only justfile recipes |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Add set-queue recipe | 10 min | High |
| Extend session_state schema | 10 min | High |
| Wire 5 cycle skills | 30 min | High |
| Test integration | 15 min | High |
| **Total** | ~65 min | High |

---

## Current State vs Desired State

### Current State

```json
// .claude/haios-status-slim.json:27-32
"session_state": {
    "active_cycle": null,
    "current_phase": null,
    "work_id": null,
    "entered_at": null
}
```

```markdown
// .claude/skills/implementation-cycle/SKILL.md - NO recipe calls exist
### 1. PLAN Phase
**Goal:** Verify plan exists...
// No set-cycle call at phase entry
```

**Behavior:** session_state remains null throughout entire cycle execution. Skills execute but state never updates.

**Result:** Queue context lost, phase observability missing, UserPromptSubmit shows "No active governance cycle detected."

### Desired State

```json
// .claude/haios-status-slim.json:27-35 - Extended schema
"session_state": {
    "active_cycle": "implementation-cycle",
    "current_phase": "DO",
    "work_id": "E2-292",
    "entered_at": "2026-01-16T20:55:00",
    "active_queue": "governance",
    "phase_history": [
        {"phase": "PLAN", "at": "2026-01-16T20:50:00"},
        {"phase": "DO", "at": "2026-01-16T20:55:00"}
    ]
}
```

```markdown
// .claude/skills/implementation-cycle/SKILL.md - With recipe calls
### 1. PLAN Phase

**On Entry:**
\`\`\`bash
just set-cycle implementation-cycle PLAN {work_id}
\`\`\`

**Goal:** Verify plan exists...
```

**Behavior:** Each cycle skill calls `just set-cycle` at entry and phase transitions, `just clear-cycle` at exit.

**Result:** Live session_state enables queue context propagation, phase observability, and UserPromptSubmit shows "Currently in implementation-cycle, DO phase."

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: set-queue Recipe Updates active_queue
```python
def test_set_queue_updates_active_queue():
    """Verify just set-queue updates session_state.active_queue."""
    import json
    import subprocess

    # Setup: Clear existing state
    subprocess.run(["just", "clear-cycle"], check=True)

    # Action: Set queue
    subprocess.run(["just", "set-queue", "governance"], check=True)

    # Assert: active_queue is set
    with open(".claude/haios-status-slim.json") as f:
        data = json.load(f)
    assert data["session_state"]["active_queue"] == "governance"
```

### Test 2: set-cycle Updates All Fields
```python
def test_set_cycle_updates_all_fields():
    """Verify just set-cycle updates active_cycle, current_phase, work_id, entered_at."""
    import json
    import subprocess

    # Action
    subprocess.run(["just", "set-cycle", "implementation-cycle", "DO", "E2-292"], check=True)

    # Assert
    with open(".claude/haios-status-slim.json") as f:
        data = json.load(f)
    state = data["session_state"]
    assert state["active_cycle"] == "implementation-cycle"
    assert state["current_phase"] == "DO"
    assert state["work_id"] == "E2-292"
    assert state["entered_at"] is not None
```

### Test 3: clear-cycle Resets State
```python
def test_clear_cycle_resets_state():
    """Verify just clear-cycle resets session_state to nulls."""
    import json
    import subprocess

    # Setup: Set state first
    subprocess.run(["just", "set-cycle", "test-cycle", "TEST", "E2-999"], check=True)

    # Action
    subprocess.run(["just", "clear-cycle"], check=True)

    # Assert
    with open(".claude/haios-status-slim.json") as f:
        data = json.load(f)
    state = data["session_state"]
    assert state["active_cycle"] is None
    assert state["current_phase"] is None
```

---

## Detailed Design

### Component 1: New `just set-queue` Recipe

**File:** `justfile`
**Location:** After line 249 (after clear-cycle)

**New Code:**
```bash
# Set active_queue in session_state (E2-292)
# Usage: just set-queue governance
set-queue queue_name:
    @python -c "import json; p='.claude/haios-status-slim.json'; d=json.load(open(p)); d['session_state']['active_queue']='{{queue_name}}'; json.dump(d,open(p,'w'),indent=4); print(f'Set queue: {{queue_name}}')"
```

### Component 2: Extended session_state Schema

**File:** `.claude/lib/status.py`
**Change:** Add `active_queue` and `phase_history` to session_state generation

**Current Code (status.py:940-945):**
```python
"session_state": {
    "active_cycle": None,
    "current_phase": None,
    "work_id": None,
    "entered_at": None
}
```

**Changed Code:**
```python
"session_state": {
    "active_cycle": None,
    "current_phase": None,
    "work_id": None,
    "entered_at": None,
    "active_queue": None,         # NEW
    "phase_history": []           # NEW
}
```

### Component 3: Skill Prose Wiring Pattern

**Pattern for all cycle skills:**

```markdown
## Entry (at skill start)

**On Entry:**
\`\`\`bash
just set-cycle {skill-name} {first_phase} {work_id}
\`\`\`

## Phase N (at each transition)

**Exit Gate:** [criteria]
\`\`\`bash
just set-cycle {skill-name} {next_phase} {work_id}
\`\`\`

## Final Phase (at skill exit)

**On Complete:**
\`\`\`bash
just clear-cycle
\`\`\`
```

### Skill-Specific Wiring

| Skill | Entry Call | Phase Transitions | Exit Call |
|-------|------------|-------------------|-----------|
| implementation-cycle | `just set-cycle implementation-cycle PLAN {id}` | PLAN→DO→CHECK→DONE | `just clear-cycle` |
| investigation-cycle | `just set-cycle investigation-cycle HYPOTHESIZE {id}` | HYPOTHESIZE→EXPLORE→CONCLUDE | `just clear-cycle` |
| survey-cycle | `just set-cycle survey-cycle GATHER {id}` + `just set-queue {queue}` | GATHER→SELECT | Before routing-gate |
| close-work-cycle | `just set-cycle close-work-cycle VALIDATE {id}` | VALIDATE→ARCHIVE→MEMORY | `just clear-cycle` |
| work-creation-cycle | `just set-cycle work-creation-cycle VERIFY {id}` | VERIFY→POPULATE→READY | Before CHAIN |

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Recipe calls in prose | Bash code blocks in skill markdown | PostToolUse can't intercept Skill() - only viable mechanism (INV-065) |
| active_queue separate from set-cycle | `just set-queue` is independent | Queue context persists across cycle invocations |
| phase_history as array | Last 5 entries | Debugging without unbounded growth |
| Soft enforcement | Warn, don't block | Hard enforcement impossible (Skill unhookable) |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Work ID contains spaces | Quote in recipe call | Manual verification |
| Agent skips recipe call | UserPromptSubmit warning | Existing E2-287 |
| Nested cycle invocations | Each skill manages own state | N/A (cycles don't nest) |

### Open Questions

**Q: Should phase_history be updated by set-cycle?**

Yes, but deferred to future enhancement. Current implementation focuses on core fields. phase_history can be added to set-cycle recipe after core wiring is verified.

---

## Open Decisions (MUST resolve before implementation)

<!-- Decisions from work item's operator_decisions field.
     If ANY row has [BLOCKED] in Chosen column, plan-validation-cycle will BLOCK.

     POPULATE FROM: Work item frontmatter `operator_decisions` field
     - question -> Decision column
     - options -> Options column
     - chosen -> Chosen column (null = [BLOCKED])
     - rationale -> Rationale column (filled when resolved) -->

**No open decisions.** Work item `operator_decisions: []` is empty. All design decisions resolved in INV-065.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Add `just set-queue` Recipe
- [ ] Add set-queue recipe to justfile after clear-cycle (line ~250)
- [ ] Test: `just set-queue governance` updates session_state.active_queue

### Step 2: Extend session_state Schema
- [ ] Update `.claude/lib/status.py` to include active_queue and phase_history
- [ ] Run `just update-status-slim` to verify schema extension
- [ ] Test: New fields appear in haios-status-slim.json

### Step 3: Wire implementation-cycle
- [ ] Add `just set-cycle implementation-cycle PLAN {id}` at PLAN phase entry
- [ ] Add phase transition calls at DO, CHECK, DONE entries
- [ ] Add `just clear-cycle` at CHAIN phase

### Step 4: Wire investigation-cycle
- [ ] Add `just set-cycle investigation-cycle HYPOTHESIZE {id}` at entry
- [ ] Add phase transition calls at EXPLORE, CONCLUDE entries
- [ ] Add `just clear-cycle` at CHAIN phase

### Step 5: Wire survey-cycle
- [ ] Add `just set-cycle survey-cycle GATHER {id}` at entry
- [ ] Add `just set-queue {queue_name}` after queue selection
- [ ] Phase transitions at SELECT, before routing-gate

### Step 6: Wire close-work-cycle
- [ ] Add `just set-cycle close-work-cycle VALIDATE {id}` at entry
- [ ] Add phase transition calls at ARCHIVE, MEMORY entries
- [ ] Add `just clear-cycle` at end of MEMORY phase

### Step 7: Wire work-creation-cycle
- [ ] Add `just set-cycle work-creation-cycle VERIFY {id}` at entry
- [ ] Add phase transition calls at POPULATE, READY entries
- [ ] Clear or transition before CHAIN phase

### Step 8: Integration Test
- [ ] Run a full cycle (e.g., `/implement E2-xxx`) and verify session_state updates
- [ ] Verify UserPromptSubmit displays cycle/phase context
- [ ] Run `pytest tests/test_session_state.py` (if tests exist)

### Step 9: Consumer Verification
- [ ] Grep for any hardcoded session_state assumptions
- [ ] Verify UserPromptSubmit reads new fields correctly

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent ignores recipe calls | Medium | Soft enforcement - UserPromptSubmit warning already exists (E2-287) |
| Skill prose changes break formatting | Low | Review markdown escaping carefully |
| phase_history grows unbounded | Low | Deferred - not implementing in this iteration |
| Work ID with special characters | Low | Quote parameters in recipe calls |

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

**MUST** read `docs/work/active/E2-292/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Add `just set-queue` recipe | [ ] | justfile contains set-queue recipe |
| Extend session_state schema | [ ] | status.py includes active_queue, phase_history |
| Wire implementation-cycle | [ ] | SKILL.md has set-cycle calls at PLAN/DO/CHECK/DONE |
| Wire investigation-cycle | [ ] | SKILL.md has set-cycle calls at HYPOTHESIZE/EXPLORE/CONCLUDE |
| Wire survey-cycle | [ ] | SKILL.md has set-queue after queue selection |
| Wire close-work-cycle | [ ] | SKILL.md has set-cycle and clear-cycle |
| Wire work-creation-cycle | [ ] | SKILL.md has set-cycle at VERIFY/POPULATE/READY |
| Test: UserPromptSubmit displays context | [ ] | Verified via manual test or grep |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `justfile` | set-queue recipe exists around line 250 | [ ] | |
| `.claude/lib/status.py` | session_state includes active_queue, phase_history | [ ] | |
| `.claude/skills/implementation-cycle/SKILL.md` | Recipe calls at phase entries | [ ] | |
| `.claude/skills/investigation-cycle/SKILL.md` | Recipe calls at phase entries | [ ] | |
| `.claude/skills/survey-cycle/SKILL.md` | set-queue after queue selection | [ ] | |
| `.claude/skills/close-work-cycle/SKILL.md` | Recipe calls + clear-cycle | [ ] | |
| `.claude/skills/work-creation-cycle/SKILL.md` | Recipe calls at phase entries | [ ] | |

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

- @docs/work/active/INV-065/investigations/001-session-state-cascade-architecture.md (source investigation)
- @docs/work/archive/E2-286/WORK.md (session_state schema)
- @docs/work/archive/E2-287/WORK.md (UserPromptSubmit warning)
- @docs/work/archive/E2-288/WORK.md (set-cycle/clear-cycle recipes)
- justfile:244-249 (existing recipes)

---
