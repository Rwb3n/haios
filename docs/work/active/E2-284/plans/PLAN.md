---
template: implementation_plan
status: complete
date: 2026-01-10
backlog_id: E2-284
title: Observation-Capture Simplify to 3 Questions
author: Hephaestus
lifecycle_phase: plan
session: 187
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-10T16:55:48'
---
# Implementation Plan: Observation-Capture Simplify to 3 Questions

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

Replace the 134-line, 3-phase observation-capture-cycle with a minimal 3-question skill and simplified observations.md template (target: ~30 lines each), enforcing S20's "smaller containers, harder boundaries" principle.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `.claude/skills/observation-capture-cycle/SKILL.md`, `.claude/templates/observations.md` |
| Lines of code affected | ~239 | `wc -l`: 134 (SKILL.md) + 105 (observations.md) |
| New files to create | 0 | Simplifying existing files |
| Tests to write | 3 | Adapt existing tests in `tests/test_observation_capture_cycle.py` |
| Dependencies | 2 | `/close` command, `close-work-cycle` skill (consumers) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only `/close` command invokes this skill |
| Risk of regression | Low | Existing tests verify integration order |
| External dependencies | None | Pure markdown skill definition |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 10 min | High |
| Simplify SKILL.md | 15 min | High |
| Simplify observations.md | 10 min | High |
| Verify integration | 5 min | High |
| **Total** | 40 min | High |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/skills/observation-capture-cycle/SKILL.md (134 lines)
# 3 phases: RECALL [volumous] -> NOTICE [volumous] -> COMMIT [tight]

### 1. RECALL Phase [volumous, MAY]
**Prompt:**
> "Before closing, replay what happened during this work..."

### 2. NOTICE Phase [volumous, MAY]
**Prompt:**
> "Now reflect on what surprised you..."

### 3. COMMIT Phase [tight, MUST]
**Actions:**
1. Scaffold observations.md if not exists
2. Populate observations.md from RECALL/NOTICE phases
3. Validate gate: `just validate-observations {id}`
```

**Behavior:** Agent executes 3 named phases procedurally, pattern-matching through checkboxes.

**Result:** Phases add overhead without changing agent cognition. S20 says "each skill does ONE thing."

### Desired State

```markdown
# .claude/skills/observation-capture-cycle/SKILL.md (~30 lines)
# Single responsibility: Ask 3 questions, enforce non-empty

## Questions

1. **What surprised you?** (unexpected behaviors, easier/harder than expected)
2. **What's missing?** (gaps noticed, features that would have helped)
3. **What should we remember?** (learnings for future work)

## Gate

- Answer at least one question OR explicitly mark "None observed"
- Empty responses BLOCK closure
```

**Behavior:** Agent answers 3 questions directly, no phase ceremony.

**Result:** Smaller container, harder boundary. Questions force reflection; gate enforces capture.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Skill Has 3 Questions (not phases)
```python
def test_skill_has_three_questions():
    """Verify skill defines 3 questions, not 3 phases."""
    skill_path = Path(".claude/skills/observation-capture-cycle/SKILL.md")
    content = skill_path.read_text()

    # Should have questions section
    assert "## Questions" in content or "1. **What surprised" in content
    # Should NOT have phase headers
    assert "### 1. RECALL Phase" not in content
    assert "### 2. NOTICE Phase" not in content
    assert "### 3. COMMIT Phase" not in content
```

### Test 2: Skill Is Under 50 Lines
```python
def test_skill_is_minimal():
    """Verify skill follows S20 'smaller containers' principle."""
    skill_path = Path(".claude/skills/observation-capture-cycle/SKILL.md")
    content = skill_path.read_text()
    line_count = len(content.split('\n'))

    assert line_count < 50, f"Skill should be <50 lines, got {line_count}"
```

### Test 3: Gate Requires Non-Empty
```python
def test_gate_requires_content():
    """Verify skill has hard gate for non-empty responses."""
    skill_path = Path(".claude/skills/observation-capture-cycle/SKILL.md")
    content = skill_path.read_text()

    # Should mention gate/block for empty
    assert "gate" in content.lower() or "block" in content.lower()
    assert "none observed" in content.lower() or "explicit" in content.lower()
```

### Test 4: Backward Compatibility - Close Command Still Invokes
```python
def test_close_command_invokes_skill():
    """Verify /close command still invokes observation-capture-cycle."""
    close_path = Path(".claude/commands/close.md")
    content = close_path.read_text()

    assert "observation-capture-cycle" in content
    # Should still come before close-work-cycle
    obs_pos = content.find("observation-capture-cycle")
    close_pos = content.find("close-work-cycle")
    assert obs_pos < close_pos
```

---

## Detailed Design

### File 1: `.claude/skills/observation-capture-cycle/SKILL.md`

**Target:** Replace 134 lines with ~30 lines

**New Content:**
```markdown
---
name: observation-capture-cycle
description: 3 questions for genuine reflection before work closure. Hard gate on non-empty.
generated: 2026-01-10
last_updated: '2026-01-10'
---
# Observation Capture

Capture observations before closing work. Invoked by `/close` command.

## Questions

Answer these 3 questions about the work just completed:

1. **What surprised you?**
   - Unexpected behaviors, bugs encountered
   - Things easier or harder than anticipated
   - Assumptions that proved wrong

2. **What's missing?**
   - Gaps in tooling, docs, or infrastructure noticed
   - Features that would have helped
   - AgentUX friction points

3. **What should we remember?**
   - Learnings for future work
   - Patterns worth reusing
   - Warnings for similar tasks

## Gate

**MUST** provide:
- At least one substantive answer, OR
- Explicit "None observed" with brief justification

Empty responses BLOCK closure.

## Output

Write answers to `docs/work/active/{id}/observations.md` using simplified template.
```

### File 2: `.claude/templates/observations.md`

**Target:** Replace 105 lines with ~25 lines

**New Content:**
```markdown
---
template: observations
work_id: '{{BACKLOG_ID}}'
captured_session: {{SESSION}}
generated: '{{DATE}}'
last_updated: '{{DATE}}'
---
# Observations: {{BACKLOG_ID}}

## What surprised you?

<!-- Unexpected behaviors, things easier/harder than expected -->

- [ ] None observed

## What's missing?

<!-- Gaps, missing features, AgentUX friction -->

- [ ] None observed

## What should we remember?

<!-- Learnings, patterns, warnings -->

- [ ] None observed
```

### Call Chain Context

```
/close command
    |
    +-> observation-capture-cycle  <-- What we're simplifying
    |       Writes: observations.md
    |
    +-> close-work-cycle
            Reads: observations.md (for memory storage)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Remove RECALL/NOTICE/COMMIT phases | Single responsibility: 3 questions | S20: "each skill does ONE thing" - phases add procedural overhead |
| Keep same 3 concepts | What surprised / What's missing / What to remember | Maps to original RECALL (happened) / NOTICE (surprised) / COMMIT (capture) |
| Hard gate on non-empty | BLOCK closure if all empty without justification | Prevents ceremonial "None observed" checkboxes |
| Remove validation recipe | Trust markdown structure | `just validate-observations` added complexity without value |
| Keep skill name | `observation-capture-cycle` | Backward compatibility - `/close` and `close-work-cycle` reference it |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| All "None observed" checked | Allowed if explicit choice | Test 3 |
| Empty file with no checkboxes | BLOCK - must answer or check "None" | Gate definition |
| Work item has no observations.md | Agent creates from template | Implied by gate |

### Open Questions

**Q: Should we remove `just scaffold-observations` recipe?**

Yes - with simplified template, agent can create directly. Recipe adds unnecessary indirection.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | - | - | Work item has no `operator_decisions` - scope is clear from S20 |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Update `tests/test_observation_capture_cycle.py` with new tests
- [ ] Verify tests 1-3 fail (skill still has phases)
- [ ] Test 4 passes (backward compat with /close)

### Step 2: Simplify SKILL.md
- [ ] Replace `.claude/skills/observation-capture-cycle/SKILL.md` with new content
- [ ] Tests 1-3 pass (green)
- [ ] Test 4 still passes

### Step 3: Simplify observations.md Template
- [ ] Replace `.claude/templates/observations.md` with simplified version
- [ ] Verify template renders correctly

### Step 4: Update Consumer References (if any)
- [ ] Check `close-work-cycle` still references skill correctly
- [ ] No changes needed - skill name unchanged

### Step 5: Run Full Test Suite
- [ ] `pytest tests/test_observation_capture_cycle.py -v` passes
- [ ] `pytest` (full suite) - no regressions

### Step 6: README Sync
- [ ] Update `.claude/skills/README.md` description if needed
- [ ] Skill directory has no separate README (content is in SKILL.md)

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment - S20 interpretation | Low | S20 line 98 explicitly says "3 questions, hard gate" |
| Integration break - /close stops working | Medium | Test 4 verifies backward compatibility before changes |
| Loss of reflection quality | Medium | 3 questions preserve same concepts as phases, just without ceremony |
| Existing observations.md files incompatible | Low | Template change only affects new files; existing files work |

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

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/observation-capture-cycle/SKILL.md` | <50 lines, 3 questions, no phases | [ ] | |
| `.claude/templates/observations.md` | <30 lines, 3 sections | [ ] | |
| `tests/test_observation_capture_cycle.py` | 4 tests, all pass | [ ] | |
| `.claude/commands/close.md` | Still invokes observation-capture-cycle | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_observation_capture_cycle.py -v
# Expected: 4 tests passed

wc -l .claude/skills/observation-capture-cycle/SKILL.md
# Expected: <50

wc -l .claude/templates/observations.md
# Expected: <30
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [ ] | |
| Test output pasted above? | [ ] | |
| Any deviations from plan? | [ ] | Explain: |

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

- S20-pressure-dynamics.md (line 98: "3 questions, hard gate")
- Memory 81211-81221 (skills as procedural theater)
- Memory 81262 ("Skills should be single-phase, compose via invocation")
- INV-059 (observation capture isolation investigation)
- E2-278 (original observation-capture-cycle implementation)

---
