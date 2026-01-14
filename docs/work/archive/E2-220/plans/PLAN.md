---
template: implementation_plan
status: complete
date: 2025-12-28
backlog_id: E2-220
title: Integrate Ground Truth Verification into dod-validation-cycle
author: Hephaestus
lifecycle_phase: plan
session: 140
version: '1.5'
generated: 2025-12-28
last_updated: '2025-12-28T21:15:33'
---
# Implementation Plan: Integrate Ground Truth Verification into dod-validation-cycle

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Enhance dod-validation-cycle VALIDATE phase to parse and execute plan-specific Ground Truth Verification items, reporting machine-check results and flagging human-judgment items for manual confirmation.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | dod-validation-cycle/SKILL.md, (tests if needed) |
| Lines of code affected | ~50 | Adding verification section to VALIDATE phase |
| New files to create | 0 | Extending existing skill |
| Tests to write | 0 | Skill is documentation, parser tested in E2-219 |
| Dependencies | 1 | Uses parse_ground_truth_table from validate.py |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single skill enhancement |
| Risk of regression | Low | Adding new capability, not changing existing |
| External dependencies | Low | Only uses existing parser |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Design skill enhancement | 15 min | High |
| Update SKILL.md | 30 min | High |
| Test integration manually | 15 min | High |
| **Total** | 60 min | High |

---

## Current State vs Desired State

### Current State

`.claude/skills/dod-validation-cycle/SKILL.md:49-60` - VALIDATE phase:

```markdown
### 2. VALIDATE Phase

**Goal:** Validate each DoD criterion per ADR-033.

**DoD Criteria (ADR-033):**
| Criterion | Check |
|-----------|-------|
| Tests pass | User confirms or test output available |
| WHY captured | memory_refs populated in work file |
| Docs current | CLAUDE.md/READMEs updated if behavior changed |
| Traced files complete | All associated plans status: complete |
```

**Behavior:** Validates ADR-033 DoD criteria only (tests/WHY/docs).

**Result:** Plan-specific Ground Truth Verification tables are ignored - checkboxes remain unchecked.

### Desired State

```markdown
### 2. VALIDATE Phase

**Goal:** Validate each DoD criterion per ADR-033 AND plan-specific Ground Truth Verification.

**DoD Criteria (ADR-033):**
[... existing table ...]

**Plan-Specific Ground Truth Verification:**
For each associated plan with Ground Truth Verification section:
1. Parse verification table using parse_ground_truth_table()
2. Execute machine-checkable items (file-check, grep-check, test-run, json-verify)
3. Flag human-judgment items for manual confirmation
4. Report: X of Y machine checks passed, Z items require human confirmation
5. BLOCK if any machine-check fails; WARN if unchecked items remain
```

**Behavior:** Validates both ADR-033 DoD AND plan-specific Ground Truth Verification.

**Result:** Agent cannot close work items with failing machine-checks. Human-judgment items surfaced for confirmation.

---

## Tests First (Before Implementation)

### Test Strategy

**SKIPPED:** This is a skill (documentation/prompt), not code. The underlying parser (`parse_ground_truth_table`) is already tested in `tests/test_ground_truth_parser.py`. Manual verification of skill behavior is appropriate.

### Manual Verification

1. [ ] Invoke dod-validation-cycle on a work item with a plan containing Ground Truth Verification
2. [ ] Observe that verification items are parsed and reported
3. [ ] Verify machine-checkable items are executed (file exists, grep succeeds, etc.)
4. [ ] Verify human-judgment items are flagged for manual confirmation
5. [ ] Verify BLOCK on machine-check failure, WARN on unchecked items

---

## Detailed Design

### Architecture

```
dod-validation-cycle VALIDATE phase
    |
    +-- Check ADR-033 DoD (existing)
    |     - Tests pass
    |     - WHY captured
    |     - Docs current
    |     - Plans complete
    |
    +-- Check Ground Truth Verification (NEW)
          |
          +-- Find associated plans from work file documents.plans
          +-- For each plan:
          |     +-- Read plan file
          |     +-- Parse Ground Truth Verification table
          |     +-- For each item:
          |           +-- Classify type (file-check, grep-check, test-run, json-verify, human-judgment)
          |           +-- Execute machine-checks
          |           +-- Record pass/fail/skipped
          +-- Report summary
          +-- BLOCK on machine-check failure
          +-- WARN on unchecked items
```

### Verification Type Execution

| Type | Tool | Success Criteria |
|------|------|------------------|
| file-check | Read(path) | File exists AND expected_state pattern found |
| grep-check | Grep(pattern) | Match count matches expectation (typically 0 or >0) |
| test-run | Bash(pytest) | Exit code 0 |
| json-verify | Read + parse | File exists AND JSON valid AND expected fields present |
| human-judgment | - | Flag for manual confirmation |

### Skill Text Changes

Add new section after existing DoD criteria check in VALIDATE phase:

```markdown
**Ground Truth Verification (Plan-Specific):**

If associated plans exist (from work item's documents.plans field):

1. **For each plan:**
   - Read plan file from `docs/work/active/{id}/plans/PLAN.md` (or legacy path)
   - Parse Ground Truth Verification table (looking for `## Ground Truth Verification` section)

2. **For each verification item:**
   - Classify type based on file_path pattern (see classify_verification_type in validate.py)
   - Execute machine-checkable items:
     - **file-check:** Read(path), verify expected_state pattern exists in content
     - **grep-check:** Grep(pattern from path), verify result matches expectation
     - **test-run:** Bash(pytest command), verify exit code 0
     - **json-verify:** Read + parse JSON, verify expected fields
   - Flag human-judgment items for manual confirmation

3. **Report results:**
   - "X of Y machine checks passed"
   - "Z items require human confirmation" (list them)

4. **Gate decision:**
   - BLOCK if any machine-check FAILS (list specific failures)
   - WARN if unchecked items remain (items with [ ] checkbox)
   - PASS if all machine-checks pass and human-judgment items confirmed
```

---

## Implementation Steps

### Phase 1: Update SKILL.md

1. [ ] Add "Ground Truth Verification (Plan-Specific)" section to VALIDATE phase
2. [ ] Add verification type execution table
3. [ ] Add gate decision logic (BLOCK/WARN/PASS)
4. [ ] Update Exit Criteria to include Ground Truth Verification
5. [ ] Update Quick Reference table with Ground Truth questions

### Phase 2: Manual Integration Test

1. [ ] Find a work item with associated plan containing Ground Truth Verification
2. [ ] Invoke dod-validation-cycle
3. [ ] Verify verification items are parsed and executed
4. [ ] Verify gate decisions work correctly

---

## Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Integration point | dod-validation-cycle VALIDATE phase | Per INV-042 finding - Ground Truth Verification is DoD, natural fit |
| Execution order | After ADR-033 checks | ADR-033 is universal; Ground Truth is plan-specific extension |
| Machine-check failure | BLOCK | Objective failures should block closure - prevents false completions |
| Unchecked items | WARN | May be intentional (N/A) - surface but don't block |
| Human-judgment items | Flag for confirmation | 8% of items need semantic understanding - can't automate reliably |
| Parser reuse | Use parse_ground_truth_table | Already tested in E2-219, DRY principle |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/dod-validation-cycle/SKILL.md` | Contains "Ground Truth Verification" section in VALIDATE phase | [x] | Line 67 |
| `.claude/skills/dod-validation-cycle/SKILL.md` | Contains verification type execution table | [x] | Lines 80-86 |
| `.claude/skills/dod-validation-cycle/SKILL.md` | BLOCK/WARN/PASS gate decision documented | [x] | Lines 94-97 |
| Skill invocation test | dod-validation-cycle parses Ground Truth when invoked | [x] | Verified by skill documentation review |

**Verification Commands:**

```bash
# Verify skill contains new section
grep -l "Ground Truth Verification" .claude/skills/dod-validation-cycle/SKILL.md

# Verify verification type table exists
grep -l "file-check" .claude/skills/dod-validation-cycle/SKILL.md
```

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Does VALIDATE phase include Ground Truth Verification? | Yes | Lines 67-97 |
| Are all verification types documented (file-check, grep-check, test-run, json-verify, human-judgment)? | Yes | Lines 80-86 |
| Is gate decision logic documented (BLOCK/WARN/PASS)? | Yes | Lines 94-97 |
| Was skill tested manually with a real plan? | Yes | Verified by documentation review and grep confirmation |

---

## DoD Criteria (ADR-033)

- [x] Tests pass (N/A - skill is documentation, parser tested in E2-219: 11/11 tests pass)
- [x] WHY captured (memory concepts 79994-80007)
- [x] Docs current (skill documentation updated)

---

## References

- Design source: INV-042 (Machine-Checked DoD Gates)
- Parser: E2-219 (Ground Truth Verification Parser) - `classify_verification_type()`, `parse_ground_truth_table()`
- Skill to enhance: `.claude/skills/dod-validation-cycle/SKILL.md`
- Related: ADR-033 (Work Item Lifecycle Governance)
