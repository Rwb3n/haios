---
template: implementation_plan
status: complete
date: 2026-01-08
backlog_id: E2-278
title: Create observation-capture-cycle Skill
author: Hephaestus
lifecycle_phase: plan
session: 182
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-08T20:45:41'
---
# Implementation Plan: Create observation-capture-cycle Skill

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

A standalone `observation-capture-cycle` skill will force agents to reflect before closing work items, using volumous phases that create cognitive space for genuine observation rather than mechanical checkbox completion.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `.claude/skills/close-work-cycle/SKILL.md`, `.claude/commands/close.md` |
| Lines of code affected | ~65 lines | OBSERVE phase in close-work-cycle (lines 66-129) |
| New files to create | 1 | `.claude/skills/observation-capture-cycle/SKILL.md` |
| Tests to write | 3 | Skill structure, phase flow, integration |
| Dependencies | 1 | `observations.py` (already exists) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only touches /close command flow |
| Risk of regression | Low | Adding new skill, modifying existing flow |
| External dependencies | Low | Uses existing observations.py functions |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Create skill file | 30 min | High |
| Update close-work-cycle | 15 min | High |
| Update /close command | 10 min | High |
| Tests | 20 min | Medium |
| **Total** | ~75 min | High |

---

## Current State vs Desired State

### Current State

```
# .claude/skills/close-work-cycle/SKILL.md - Flow diagram (lines 19-31)
[dod-validation-cycle] --> VALIDATE --> OBSERVE --> ARCHIVE --> MEMORY --> CHAIN
                                            │
                                      observations
                                      captured here
                                      (4 mechanical actions)
```

**Behavior:** OBSERVE phase embedded in close-work-cycle with 4 sub-actions:
1. Scaffold observations.md
2. Prompt to populate
3. Validate gate
4. Threshold check

**Result:** Agent rushes through in "completion mode" - checks boxes without genuine reflection (Session 179 evidence).

### Desired State

```
# /close {id} - New flow
/close {id}
  ├── observation-capture-cycle  <-- FIRST, dedicated context
  │     ├── RECALL  [volumous, MAY] - "What happened?"
  │     ├── NOTICE  [volumous, MAY] - "What surprised you?"
  │     └── COMMIT  [tight, MUST]   - Capture + validate
  │
  └── close-work-cycle (modified)
        ├── VALIDATE (DoD)
        ├── ARCHIVE   <-- OBSERVE phase REMOVED
        └── MEMORY
```

**Behavior:** Standalone skill invoked BEFORE close-work-cycle forces dedicated cognitive focus with 2 volumous phases for genuine reflection.

**Result:** Agent inhabits reflection space before entering "closing mode", producing better observations.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Skill File Structure Validation
```python
def test_observation_capture_cycle_skill_exists():
    """Verify skill file exists with required sections."""
    skill_path = Path(".claude/skills/observation-capture-cycle/SKILL.md")
    assert skill_path.exists(), "Skill file must exist"

    content = skill_path.read_text()
    # Check YAML frontmatter
    assert "name: observation-capture-cycle" in content
    # Check required phases
    assert "RECALL" in content and "[volumous" in content
    assert "NOTICE" in content and "[volumous" in content
    assert "COMMIT" in content and "[tight" in content
```

### Test 2: Close-Work-Cycle OBSERVE Phase Removed
```python
def test_close_work_cycle_observe_phase_removed():
    """Verify OBSERVE phase is removed from close-work-cycle."""
    skill_path = Path(".claude/skills/close-work-cycle/SKILL.md")
    content = skill_path.read_text()

    # OBSERVE phase should NOT be in the cycle diagram
    assert "OBSERVE" not in content or "observation-capture-cycle" in content
    # Should reference observation-capture-cycle instead
    assert "observation-capture-cycle" in content
```

### Test 3: Integration - Close Command Chains Skills
```python
def test_close_command_chains_observation_capture():
    """Verify /close command invokes observation-capture-cycle first."""
    cmd_path = Path(".claude/commands/close.md")
    content = cmd_path.read_text()

    # Should invoke observation-capture-cycle before close-work-cycle
    obs_pos = content.find("observation-capture-cycle")
    close_pos = content.find("close-work-cycle")
    assert obs_pos < close_pos, "observation-capture-cycle must be invoked before close-work-cycle"
```

---

## Detailed Design

### New File: `.claude/skills/observation-capture-cycle/SKILL.md`

Following the pattern established by sibling skills (observation-triage-cycle, close-work-cycle).

**Structure:**
```yaml
---
name: observation-capture-cycle
description: HAIOS Observation Capture Cycle for genuine reflection before work closure.
  Guides RECALL->NOTICE->COMMIT workflow with volumous phases for cognitive space.
generated: 2026-01-08
last_updated: '2026-01-08'
---
```

**Phase Design (from INV-059 findings):**

```
RECALL [volumous, MAY] --> NOTICE [volumous, MAY] --> COMMIT [tight, MUST]
    │                           │                          │
    │                           │                          +-> scaffold + validate gate
    │                           +-> "What surprised you?"
    +-> "What happened during this work?"
```

### File 1: `.claude/skills/observation-capture-cycle/SKILL.md`

**Content Structure:**

```markdown
# Observation Capture Cycle

This skill defines the RECALL-NOTICE-COMMIT cycle for genuine reflection before work closure.
It forces dedicated cognitive focus with volumous phases that create space for reflection.

## When to Use

**Invoked automatically** by `/close` command BEFORE close-work-cycle.
**Manual invocation:** `Skill(skill="observation-capture-cycle")` when capturing observations.

---

## The Cycle

[ASCII diagram showing RECALL -> NOTICE -> COMMIT]

---

### 1. RECALL Phase [volumous, MAY]

**Goal:** Freeform replay of what happened during this work.

**Pressure:** [volumous] - create space, no constraints.

**Prompt:**
> "Before closing, replay what happened during this work.
> What did you do? What steps did you take?
> Freeform - no structure required."

**Actions:**
1. Agent produces freeform narrative of work session
2. No validation - pure reflection space

**Exit Criteria:**
- [ ] Freeform narrative produced (any length)

**Tools:** None (pure reflection)

---

### 2. NOTICE Phase [volumous, MAY]

**Goal:** Surface surprises and anomalies.

**Pressure:** [volumous] - create space, low constraint.

**Prompt:**
> "Now reflect on what surprised you:
> - What didn't go as expected?
> - What was harder or easier than anticipated?
> - What did you notice that might be relevant for future work?"

**Actions:**
1. Agent surfaces noticings
2. No validation - exploratory space

**Exit Criteria:**
- [ ] Noticings produced (can be empty with explicit "nothing noticed")

**Tools:** None (pure reflection)

---

### 3. COMMIT Phase [tight, MUST]

**Goal:** Capture observations in observations.md with validation.

**Pressure:** [tight] - must cross gate.

**Actions:**
1. Scaffold observations.md if not exists:
   ```bash
   just scaffold-observations {id}
   ```
2. Populate observations.md from RECALL/NOTICE phases
3. Validate gate:
   ```bash
   just validate-observations {id}
   ```
4. If validation fails, BLOCK and prompt to fix

**Exit Criteria:**
- [ ] observations.md exists
- [ ] observations.md populated (or "None observed" checked)
- [ ] `just validate-observations` passes

**Tools:** Bash(just scaffold-observations), Edit, Bash(just validate-observations)

---

## Quick Reference

| Phase | Pressure | Question | Gate |
|-------|----------|----------|------|
| RECALL | [volumous, MAY] | "What happened?" | None |
| NOTICE | [volumous, MAY] | "What surprised you?" | None |
| COMMIT | [tight, MUST] | N/A | validate_observations() |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Three phases | RECALL -> NOTICE -> COMMIT | S22 observation:recall pattern |
| Two volumous phases | RECALL + NOTICE | Creates genuine reflection space (S20) |
| Single tight phase | COMMIT only | Forces commitment after exploration |
| No tools in volumous | Pure reflection | Avoids mechanical distraction |
| Standalone skill | Not embedded | INV-059: embedding causes completion mode |
```

### File 2: Modify `.claude/skills/close-work-cycle/SKILL.md`

**Remove:** Lines 66-129 (entire OBSERVE phase section)

**Modify:** Flow diagram (lines 19-31) to show observation-capture-cycle as pre-requisite

**Current:**
```
[dod-validation-cycle] --> VALIDATE --> OBSERVE --> ARCHIVE --> MEMORY --> CHAIN
```

**Target:**
```
[observation-capture-cycle] --> [dod-validation-cycle] --> VALIDATE --> ARCHIVE --> MEMORY --> CHAIN
```

### File 3: Modify `.claude/commands/close.md`

**Add:** After work item lookup, before invoking close-work-cycle:

```markdown
## Chain to Observation Capture

After work item is found, first invoke observation-capture-cycle:

```
Skill(skill="observation-capture-cycle")
```

This forces genuine reflection before entering closure flow.

Then invoke close-work-cycle:

```
Skill(skill="close-work-cycle")
```
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Standalone skill | Not embedded in close-work-cycle | INV-059: Embedding causes completion mode bias |
| 3-phase structure | RECALL -> NOTICE -> COMMIT | Follows S22 observation:recall pattern |
| Two volumous phases | RECALL + NOTICE are [MAY] | S20: Creates space for genuine reflection |
| One tight phase | COMMIT is [MUST] | Forces commitment, prevents drift |
| Invoked before close-work-cycle | Not after or inside | Dedicated cognitive context before "closing mode" |
| No tools in reflection phases | Pure text output | Avoids mechanical distraction during reflection |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Agent produces empty RECALL | Accept - volumous is permissive | N/A (volumous) |
| Agent skips to COMMIT | Skill structure enforces order | Test 1 |
| observations.md already exists | Just populate, don't re-scaffold | Test 3 |
| validate_observations fails | BLOCK with message, prompt to fix | Existing coverage |

### Open Questions

**Q: Should RECALL/NOTICE phases have minimum length requirements?**

No - S20 guidance is that volumous phases should not impose constraints. Quality emerges from the dedicated cognitive space, not from enforced minimums. The COMMIT phase gate is sufficient.

---

## Open Decisions (MUST resolve before implementation)

**No open decisions.** Work item `operator_decisions: []` is empty. Investigation INV-059 resolved all design decisions.

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_observation_capture_cycle.py`
- [ ] Add test_observation_capture_cycle_skill_exists
- [ ] Add test_close_work_cycle_observe_phase_removed
- [ ] Add test_close_command_chains_observation_capture
- [ ] Verify all tests fail (red)

### Step 2: Create observation-capture-cycle Skill
- [ ] Create directory `.claude/skills/observation-capture-cycle/`
- [ ] Create `SKILL.md` with YAML frontmatter
- [ ] Add RECALL phase [volumous, MAY]
- [ ] Add NOTICE phase [volumous, MAY]
- [ ] Add COMMIT phase [tight, MUST]
- [ ] Add Quick Reference and Key Design Decisions tables
- [ ] Test 1 passes (green)

### Step 3: Modify close-work-cycle
- [ ] Remove OBSERVE phase (lines 66-129)
- [ ] Update flow diagram to show observation-capture-cycle as entry gate
- [ ] Add "Entry Gate" section referencing observation-capture-cycle
- [ ] Test 2 passes (green)

### Step 4: Modify /close Command
- [ ] Add invocation of observation-capture-cycle before close-work-cycle
- [ ] Update flow description
- [ ] Test 3 passes (green)

### Step 5: Integration Verification
- [ ] All 3 tests pass
- [ ] Run full test suite (no regressions): `pytest tests/`

### Step 6: README Sync (MUST)
- [ ] **MUST:** Create/update `.claude/skills/observation-capture-cycle/README.md`
- [ ] **MUST:** Update `.claude/skills/README.md` with new skill entry
- [ ] **MUST:** Verify README content matches actual file state

### Step 7: Consumer Verification
- [ ] Grep for OBSERVE phase references in docs
- [ ] Update any docs referencing old OBSERVE flow
- [ ] Verify no stale references remain

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent still rushes through volumous phases | Medium | S20 guidance: volumous phases create space but can't force reflection. Monitor empirically. |
| Breaking existing close flow | Low | Tests verify integration; minimal changes to close-work-cycle |
| Observation-triage-cycle integration unclear | Low | Triage remains in close-work-cycle (threshold check after observation-capture-cycle) |

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
| `.claude/skills/observation-capture-cycle/SKILL.md` | RECALL, NOTICE, COMMIT phases defined | [ ] | |
| `.claude/skills/close-work-cycle/SKILL.md` | OBSERVE phase removed, observation-capture-cycle referenced | [ ] | |
| `.claude/commands/close.md` | observation-capture-cycle invoked before close-work-cycle | [ ] | |
| `tests/test_observation_capture_cycle.py` | 3 tests exist and pass | [ ] | |
| `.claude/skills/README.md` | observation-capture-cycle listed | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_observation_capture_cycle.py -v
# Expected: 3 tests passed
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

- **INV-059:** Source investigation with full design rationale (completed Session 182)
- **S20-pressure-dynamics.md:** Phase pressure design (volumous vs tight)
- **S22-skill-patterns.md:** observation:recall pattern specification
- **S19-skill-work-unification.md:** Section 19.1 decision
- **Memory concepts:** 81105-81117 (INV-059 findings), 81118-81122 (closure summary)

---
