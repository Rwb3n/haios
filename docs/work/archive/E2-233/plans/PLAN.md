---
template: implementation_plan
status: complete
date: 2025-12-29
backlog_id: E2-233
title: Checkpoint Anti-Pattern Verification Integration
author: Hephaestus
lifecycle_phase: plan
session: 145
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-29T12:47:42'
---
# Implementation Plan: Checkpoint Anti-Pattern Verification Integration

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

Add a VERIFY phase to checkpoint-cycle that invokes the anti-pattern-checker agent on completion claims before session learnings are captured to memory.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/skills/checkpoint-cycle/SKILL.md` |
| Lines of code affected | ~40 | Add VERIFY phase section (~30 lines) + update diagram/tables |
| New files to create | 1 | `tests/test_checkpoint_cycle_verify.py` |
| Tests to write | 3 | Verify phase invocation, claim extraction, agent call |
| Dependencies | 1 | anti-pattern-checker agent (already exists) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only checkpoint-cycle skill file |
| Risk of regression | Low | Adding phase, not modifying existing phases |
| External dependencies | Low | Uses existing agent, no new MCPs |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 15 min | High |
| Implement VERIFY phase | 20 min | High |
| Update docs/README | 10 min | High |
| **Total** | 45 min | High |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/skills/checkpoint-cycle/SKILL.md:22-25 - Current cycle diagram
## The Cycle

SCAFFOLD --> FILL --> CAPTURE --> COMMIT
```

**Behavior:** Checkpoint cycle moves directly from FILL (populating content) to CAPTURE (storing to memory) with no verification step.

**Result:** Completion claims in checkpoints (e.g., "M8-SkillArch complete") are not verified against L1 anti-patterns before being captured to memory.

### Desired State

```markdown
# .claude/skills/checkpoint-cycle/SKILL.md - Target cycle diagram
## The Cycle

SCAFFOLD --> FILL --> VERIFY --> CAPTURE --> COMMIT
                        |
                anti-pattern-checker
                      agent
```

**Behavior:** Before capturing learnings to memory, VERIFY phase scans for completion claims and invokes anti-pattern-checker agent to validate them.

**Result:** Only verified claims are captured to memory. Unsupported claims are flagged for revision before commit.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: VERIFY Phase Exists in Skill Documentation
```python
def test_verify_phase_documented():
    """VERIFY phase section exists between FILL and CAPTURE."""
    skill_path = Path(".claude/skills/checkpoint-cycle/SKILL.md")
    content = skill_path.read_text()

    # VERIFY phase section exists
    assert "### 3. VERIFY Phase" in content or "### VERIFY Phase" in content

    # Diagram shows VERIFY between FILL and CAPTURE
    assert "FILL --> VERIFY --> CAPTURE" in content
```

### Test 2: VERIFY Phase Invokes Anti-Pattern Checker
```python
def test_verify_phase_invokes_agent():
    """VERIFY phase documentation specifies anti-pattern-checker invocation."""
    skill_path = Path(".claude/skills/checkpoint-cycle/SKILL.md")
    content = skill_path.read_text()

    # Find VERIFY phase section
    verify_section = extract_section(content, "VERIFY Phase")

    # References anti-pattern-checker agent
    assert "anti-pattern-checker" in verify_section
    assert "Task(subagent_type='anti-pattern-checker'" in verify_section
```

### Test 3: Composition Map Updated
```python
def test_composition_map_includes_verify():
    """Composition Map table includes VERIFY phase row."""
    skill_path = Path(".claude/skills/checkpoint-cycle/SKILL.md")
    content = skill_path.read_text()

    # Find Composition Map section
    comp_section = extract_section(content, "Composition Map")

    # Has VERIFY row
    assert "VERIFY" in comp_section
    assert "Task" in comp_section  # Tool for VERIFY phase
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/skills/checkpoint-cycle/SKILL.md`
**Location:** Insert new section between FILL Phase and CAPTURE Phase (after line ~67)

**Current Diagram (line 22-25):**
```markdown
## The Cycle

```
SCAFFOLD --> FILL --> CAPTURE --> COMMIT
```
```

**Changed Diagram:**
```markdown
## The Cycle

```
SCAFFOLD --> FILL --> VERIFY --> CAPTURE --> COMMIT
                        |
                anti-pattern-checker
                      agent
```
```

**New Section to Insert (after FILL Phase, before CAPTURE Phase):**

```markdown
---

### 3. VERIFY Phase

**Goal:** Verify completion claims against L1 anti-patterns.

**Guardrails (MUST follow):**
1. **Completion claims MUST be verified** - Claims like "milestone complete" or "100%" require evidence
2. **SHOULD invoke anti-pattern-checker** - For claims in Session Summary or Completed Work

**Actions:**
1. Scan checkpoint content for completion claims (triggers: "complete", "100%", "done", "finished")
2. For each claim found, invoke anti-pattern-checker agent:
   ```
   Task(subagent_type='anti-pattern-checker', prompt='Verify claim: "{claim}" in context: {checkpoint_path}')
   ```
3. If verdict is UNSUPPORTED:
   - Report gaps to agent
   - Suggest revisions to claim
   - Agent can revise and re-verify, or proceed with warning
4. If verdict is SUPPORTED: Continue to CAPTURE phase

**Exit Criteria:**
- [ ] Completion claims identified (or none found)
- [ ] Claims verified via anti-pattern-checker (or N/A if no claims)
- [ ] Unsupported claims either revised or flagged

**Tools:** Read, Task(anti-pattern-checker)
```

### Call Chain Context

```
checkpoint-cycle skill
    |
    +-> SCAFFOLD Phase       (create file)
    |
    +-> FILL Phase           (populate content)
    |
    +-> VERIFY Phase         # <-- NEW: validate claims
    |       Invokes: anti-pattern-checker agent
    |       Returns: verified/flagged claims
    |
    +-> CAPTURE Phase        (store to memory)
    |
    +-> COMMIT Phase         (git commit)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Position between FILL and CAPTURE | VERIFY before CAPTURE | Catch unsupported claims before they're stored to memory |
| SHOULD not MUST | Agent-discretionary | Some checkpoints have no completion claims |
| Trigger words | "complete", "100%", "done", "finished" | Common claim indicators from INV-050 analysis |
| Allow proceed with warning | Don't hard-block | Agent autonomy; warning surfaces issue without blocking |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No completion claims | VERIFY phase notes "N/A - no claims to verify" | N/A |
| Agent not available | Log warning, continue to CAPTURE | N/A |
| Claim partially supported | Report gaps, suggest revisions | Test 2 |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_checkpoint_cycle_verify.py`
- [ ] Add 3 tests from Tests First section
- [ ] Verify all tests fail (red)

### Step 2: Update Cycle Diagram
- [ ] Edit `.claude/skills/checkpoint-cycle/SKILL.md` line 22-25
- [ ] Change `SCAFFOLD --> FILL --> CAPTURE --> COMMIT` to include VERIFY
- [ ] Test 1 passes (green)

### Step 3: Add VERIFY Phase Section
- [ ] Insert new "### 3. VERIFY Phase" section after FILL Phase
- [ ] Include Goal, Guardrails, Actions, Exit Criteria, Tools
- [ ] Renumber CAPTURE to 4 and COMMIT to 5
- [ ] Tests 1, 2 pass (green)

### Step 4: Update Composition Map and Quick Reference
- [ ] Add VERIFY row to Composition Map table
- [ ] Add VERIFY row to Quick Reference table
- [ ] Test 3 passes (green)

### Step 5: Update Key Design Decisions Table
- [ ] Add row explaining 5-phase design rationale
- [ ] Update Related section to reference anti-pattern-checker agent

### Step 6: README Sync (MUST)
- [ ] **MUST:** Update `.claude/skills/checkpoint-cycle/README.md`
- [ ] **MUST:** Update `.claude/skills/README.md` (parent)
- [ ] **MUST:** Verify README content matches actual file state

### Step 7: Integration Verification
- [ ] All 3 new tests pass
- [ ] Run full test suite (no regressions)

---

## Verification

- [ ] Tests pass (3 new tests + no regressions)
- [ ] **MUST:** All READMEs current (checkpoint-cycle, skills)
- [ ] VERIFY phase documented with correct structure

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent not registered until restart | Low | Document as known behavior; agent file exists |
| Over-triggering on false positives | Low | SHOULD level, not MUST; agent discretion |

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
| `.claude/skills/checkpoint-cycle/SKILL.md` | VERIFY phase section exists, diagram updated | [ ] | |
| `tests/test_checkpoint_cycle_verify.py` | 3 tests exist and pass | [ ] | |
| `.claude/skills/checkpoint-cycle/README.md` | **MUST:** Reflects 5-phase cycle | [ ] | |
| `.claude/skills/README.md` | **MUST:** Lists checkpoint-cycle with VERIFY | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_checkpoint_cycle_verify.py -v
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
- [ ] Tests pass (3 new + no regressions)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated (checkpoint-cycle, skills)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- E2-232: Anti-pattern-checker agent implementation
- INV-050: Anti-pattern checker design investigation
- .claude/agents/anti-pattern-checker.md: Agent being integrated

---
