---
template: implementation_plan
status: complete
date: 2025-12-25
backlog_id: E2-185
title: Validation Agent for CHECK Phase
author: Hephaestus
lifecycle_phase: plan
session: 116
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-25T18:10:30'
---
# Implementation Plan: Validation Agent for CHECK Phase

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

## Goal

A validation-agent sub-agent will exist that supports the implementation-cycle CHECK phase by performing unbiased verification of tests, demos, and regressions in an isolated context.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/skills/implementation-cycle/SKILL.md` (add agent invocation) |
| Lines of code affected | ~5 | Add Task(validation-agent) to CHECK phase |
| New files to create | 1 | `.claude/agents/validation-agent.md` |
| Tests to write | 0 | Agent is markdown, verified via runtime discovery |
| Dependencies | 1 | implementation-cycle skill invokes this agent |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only used by implementation-cycle CHECK phase |
| Risk of regression | Low | New agent, no existing code |
| External dependencies | Low | Uses existing tools (Bash, Read) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Design agent structure | 10 min | High |
| Create agent file | 10 min | High |
| Verify discovery | 5 min | High |
| **Total** | 25 min | High |

---

## Current State vs Desired State

### Current State

No validation-agent exists. The CHECK phase in implementation-cycle relies on:
1. `test-runner` agent (OPTIONAL) - runs pytest
2. Direct Bash commands from main context
3. No dedicated unbiased verification agent

**Behavior:** CHECK phase validation is ad-hoc, relies on main agent following instructions.

**Result:** Validation may be biased - main agent may unconsciously skip edge cases or demos that reveal its own implementation errors.

### Desired State

A `validation-agent` sub-agent exists that:
1. Runs in isolated context (unbiased)
2. Performs comprehensive CHECK phase validation
3. Returns structured pass/fail summary

**Behavior:** CHECK phase can invoke validation-agent for unbiased verification.

**Result:** Implementation errors caught by fresh-context review, demos executed without confirmation bias.

---

## Tests First (TDD)

**SKIPPED:** Pure markdown agent file - no Python code to test. Verification via runtime discovery (`just update-status-slim` + check haios-status-slim.json).

---

## Detailed Design

### Part 1: Create validation-agent File

**File:** `.claude/agents/validation-agent.md`

**Agent Structure (following existing agent pattern):**

```markdown
---
name: validation-agent
description: Unbiased CHECK phase validation. Runs tests, demos features, checks DoD criteria in isolated context.
tools: Bash, Read, Glob
---
# Validation Agent

Performs unbiased verification during implementation-cycle CHECK phase.

## Requirement Level

**OPTIONAL** but **RECOMMENDED** for complex implementations.
The implementation-cycle skill will invoke this when available.

## Process

1. Receive plan path and implementation summary from parent
2. Read plan's Ground Truth Verification section
3. Run test suite: `pytest tests/ -v --tb=short`
4. Demo the feature (exercise happy path)
5. Check DoD criteria (tests pass, docs updated)
6. Return structured validation summary

## Output Format

```
Validation Results: PASS | FAIL

## Tests
Total: X passed, Y failed
[If failures, list them]

## Demo
Feature exercised: [description]
Result: PASS | FAIL
[Any bugs found]

## DoD Checklist
- [x] Tests pass
- [x] Implementation matches design
- [ ] Docs updated (if needed)

## Verdict
Ready for DONE phase: YES | NO
[If NO, list blockers]
```

## Examples

Input: "Validate E2-185 implementation"
Output:
```
Validation Results: PASS

## Tests
Total: 24 passed, 0 failed
Duration: 2.1s

## Demo
Feature exercised: validation-agent invocation from CHECK phase
Result: PASS

## DoD Checklist
- [x] Tests pass
- [x] Implementation matches design
- [x] README updated

## Verdict
Ready for DONE phase: YES
```
```

### Part 2: Update implementation-cycle Skill

**File:** `.claude/skills/implementation-cycle/SKILL.md`
**Location:** CHECK phase, line ~146

**Current Code:**
```markdown
**Tools:** Bash(pytest), Read, Task(test-runner) [future], /validate, just update-status
```

**Changed Code:**
```markdown
**Tools:** Bash(pytest), Read, Task(test-runner), Task(validation-agent), /validate, just update-status
```

**Additional Change:** Add validation-agent invocation option to CHECK phase Actions:

**Current (line ~110-116):**
```markdown
**Actions:**
1. Run test suite: `pytest tests/ -v`
2. Verify all tests pass (no regressions)
3. **DEMO the feature** - Exercise the new code path to surface bugs (Session 90)
4. Run plan's Ground Truth Verification
5. Check DoD criteria (ADR-033)
6. **If creating discoverable artifact:** Verify runtime discovery (see below)
```

**Changed:**
```markdown
**Actions:**
1. Run test suite: `pytest tests/ -v`
2. Verify all tests pass (no regressions)
3. **DEMO the feature** - Exercise the new code path to surface bugs (Session 90)
4. Run plan's Ground Truth Verification
5. Check DoD criteria (ADR-033)
6. **If creating discoverable artifact:** Verify runtime discovery (see below)
7. **(Optional) Invoke validation-agent** for unbiased review: `Task(subagent_type='validation-agent')`
```

### Call Chain Context

```
Operator starts implementation
    |
    +-> /implement command
    |       |
    |       +-> implementation-cycle (SKILL)
    |               |
    |               +-> PLAN phase
    |               +-> DO phase
    |               +-> CHECK phase
    |               |       |
    |               |       +-> validation-agent (AGENT)  # <-- NEW
    |               |               Uses: Bash, Read, Glob
    |               |               Returns: Validation summary
    |               |
    |               +-> DONE phase
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Agent vs Skill | Agent | Needs isolated context for unbiased review |
| Optional invocation | Yes | Not all implementations need full validation |
| Tools: Bash, Read, Glob | Minimal set | Just enough for tests, demos, file checks |
| Returns structured summary | Yes | Parent can parse and act on results |

### Edge Cases

| Case | Handling |
|------|----------|
| No tests to run | Report "No tests found", focus on demo/docs |
| Demo fails | Return FAIL with specific error |
| Partial pass | Return FAIL with list of blockers |

---

## Implementation Steps

### Step 1: Create validation-agent File
- [ ] Create `.claude/agents/validation-agent.md` with agent definition
- [ ] Follow pattern from existing agents (test-runner, preflight-checker)

### Step 2: Update implementation-cycle Skill
- [ ] Add `Task(validation-agent)` to CHECK phase Tools section
- [ ] Add step 7 to CHECK phase Actions

### Step 3: Verify Runtime Discovery
- [ ] Run `just update-status-slim`
- [ ] Check `haios-status-slim.json` for validation-agent in agents list

### Step 4: Demo the Agent
- [ ] Invoke validation-agent manually via Task tool
- [ ] Verify structured output format

### Step 5: README Sync (MUST)
- [ ] **MUST:** No README exists in `.claude/agents/` - SKIP (pattern matches other agents)
- [ ] Parent README: Skills README already documents agents section

---

## Verification

- [ ] Agent file exists
- [ ] Runtime discovery shows validation-agent
- [ ] implementation-cycle skill updated
- [ ] Manual demo works

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent not discovered | Low | Use same pattern as existing agents |
| Skill update breaks cycle | Low | Additive change only |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 118 | 2025-12-25 | - | In Progress | Plan authored |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/agents/validation-agent.md` | Agent with name, description, tools | [x] | Created with correct frontmatter |
| `.claude/skills/implementation-cycle/SKILL.md` | CHECK phase references validation-agent | [x] | Lines 119, 159 |
| `.claude/haios-status-slim.json` | validation-agent in agents list | [x] | Line 66 |

**Verification Commands:**
```bash
just update-status-slim
# Check output for validation-agent
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | Read agent file, grep'd skill |
| Runtime discovery confirmed? | Yes | Appears in haios-status-slim.json |
| Any deviations from plan? | No | Implemented as designed |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Agent file created
- [ ] WHY captured (reasoning stored to memory)
- [ ] Skill updated with agent invocation
- [ ] Runtime discovery verified
- [ ] Ground Truth Verification completed above

---

## References

- INV-035: Skill Architecture Refactoring (spawned this item)
- ADR-033: Work Item Lifecycle Governance

---
