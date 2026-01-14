---
template: implementation_plan
status: complete
date: 2026-01-03
backlog_id: E2-247
title: Enhance Validation with L4 Alignment Check
author: Hephaestus
lifecycle_phase: plan
session: 159
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-03T14:58:58'
---
# Implementation Plan: Enhance Validation with L4 Alignment Check

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

Plan-validation-cycle will verify that implementation plans align with L4 functional requirements, ensuring plans cover what the spec says MUST be built.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/skills/plan-validation-cycle/SKILL.md` |
| Lines of code affected | ~141 | `wc -l` on SKILL.md |
| New files to create | 0 | Skill guidance only, no Python helper |
| Tests to write | 0 | Manual validation via skill execution |
| Dependencies | 0 | Skill is pure markdown guidance |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only affects plan-validation-cycle skill |
| Risk of regression | Low | Adding new phase, not modifying existing |
| External dependencies | Low | Reads L4-implementation.md, no services |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Design L4 alignment phase | 15 min | High |
| Write tests | 15 min | High |
| Implement skill changes | 20 min | High |
| **Total** | ~50 min | |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/skills/plan-validation-cycle/SKILL.md (current phases)

## The Cycle

CHECK --> VALIDATE --> APPROVE

### 1. CHECK Phase - Verify sections exist
### 2. VALIDATE Phase - Check content quality
### 3. APPROVE Phase - Mark ready
```

**Behavior:** Validates template structure and content quality only.

**Result:** Plans can pass validation while missing L4 functional requirements (e.g., E2-246 plan missing cycle definitions despite L4 requiring them).

### Desired State

```markdown
# .claude/skills/plan-validation-cycle/SKILL.md (new phases)

## The Cycle

CHECK --> VALIDATE --> L4_ALIGN --> APPROVE

### 1. CHECK Phase - Verify sections exist
### 2. VALIDATE Phase - Check content quality
### 3. L4_ALIGN Phase - Match plan against L4 requirements  # <-- NEW
### 4. APPROVE Phase - Mark ready
```

**Behavior:** After content validation, reads L4-implementation.md and cross-references plan deliverables against L4 functional requirements for the work item's module.

**Result:** Gaps between plan and L4 are flagged before implementation begins.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: L4 Requirements Parsing
```python
def test_parse_l4_functional_requirements():
    """Extract module functional requirements from L4-implementation.md."""
    # Setup: L4 contains GovernanceLayer section with functions table
    l4_content = """
## Functional Requirements Summary

### GovernanceLayer (E2-240)

| Function | Input | Output | Acceptance Test |
|----------|-------|--------|-----------------|
| `check_gate(gate_id, context)` | Gate ID + work context | `GateResult(allowed, reason)` | Returns deny for incomplete DoD |
"""
    # Action
    reqs = parse_l4_requirements(l4_content, work_id="E2-240")

    # Assert
    assert "GovernanceLayer" in reqs["module"]
    assert "check_gate" in [f["function"] for f in reqs["functions"]]
```

### Test 2: Plan Deliverables Parsing
```python
def test_parse_plan_deliverables():
    """Extract deliverables from plan Implementation Steps."""
    plan_content = """
## Implementation Steps

### Step 2: Implement check_gate function
- [ ] Add check_gate(gate_id, context) method
- [ ] Return GateResult with allowed and reason
"""
    deliverables = parse_plan_deliverables(plan_content)

    assert "check_gate" in deliverables
```

### Test 3: Gap Detection
```python
def test_detect_l4_gaps():
    """Flag when L4 requires X but plan doesn't cover X."""
    l4_reqs = {"functions": ["check_gate", "validate_transition", "load_handlers"]}
    plan_deliverables = ["check_gate", "validate_transition"]  # Missing load_handlers

    gaps = detect_gaps(l4_reqs, plan_deliverables)

    assert "load_handlers" in gaps
    assert len(gaps) == 1
```

### Test 4: Backward Compatibility
```python
def test_existing_validation_unchanged():
    """L4_ALIGN is additive - existing CHECK/VALIDATE phases still work."""
    # Existing behavior: plan with complete sections passes CHECK/VALIDATE
    plan_content = """## Goal\nBuild something\n## Tests First\ntest_x"""

    check_result = check_phase(plan_content)
    validate_result = validate_phase(plan_content)

    assert check_result["passed"]  # Same as before
    assert validate_result["passed"]  # Same as before
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
     4. Input/output examples with REAL data from the system -->

### Exact Code Change

**File:** `.claude/skills/plan-validation-cycle/SKILL.md`
**Location:** Lines 19-22 (The Cycle section)

**Current Code:**
```markdown
## The Cycle

```
CHECK --> VALIDATE --> APPROVE
```
```

**Changed Code:**
```markdown
## The Cycle

```
CHECK --> VALIDATE --> L4_ALIGN --> APPROVE
```
```

**New Phase to Add (after VALIDATE, before APPROVE):**

```markdown
### 3. L4_ALIGN Phase

**Goal:** Verify plan deliverables align with L4 functional requirements.

**Prerequisite:** Get work_id from plan frontmatter `backlog_id` field.

**Actions:**
1. Read `.claude/haios/manifesto/L4-implementation.md`
2. Find work_id in L4 (search for "### ModuleName (work_id)")
3. Extract function requirements from table
4. Parse plan "Implementation Steps" for deliverables
5. Match: For each L4 function, check if plan mentions it
6. Report gaps and extras

**Exit Criteria:**
- [ ] All L4 functions mentioned in plan steps
- [ ] No gaps reported (or gaps accepted by operator)

**On Gap Found:** Report gap, ask operator to accept or revise plan.

**Tools:** Read
```

### Call Chain Context

```
implementation-cycle PLAN phase
    |
    +-> plan-validation-cycle (this skill)
    |       |
    |       +-> CHECK (template sections)
    |       +-> VALIDATE (content quality)
    |       +-> L4_ALIGN (requirements match)  # <-- NEW
    |       +-> APPROVE (mark ready)
    |
    +-> preflight-checker (file count gate)
```

### Function/Component Signatures

This is a skill (markdown guidance), not code. The "functions" are conceptual:

```
parse_l4_requirements(l4_content: str, work_id: str) -> dict
    """Extract module requirements from L4."""
    # Regex: find "### ModuleName (work_id)" section
    # Parse table rows under "| Function | Input | Output |"
    # Return: {"module": str, "functions": list[str]}

detect_gaps(l4_reqs: dict, plan_deliverables: list[str]) -> list[str]
    """Find L4 requirements not covered by plan."""
    # For each L4 function, check if any plan step mentions it
    # Return: list of missing function names
```

### Behavior Logic

**Current Flow:**
```
Plan → CHECK (sections) → VALIDATE (quality) → APPROVE
                                                  ↓
                                            Plan passes
                                            (may miss L4 reqs)
```

**Fixed Flow:**
```
Plan → CHECK → VALIDATE → L4_ALIGN → APPROVE
                              │
                              ├─ Gaps found? → Report, ask operator
                              │                   ├─ Accept → APPROVE
                              │                   └─ Revise → Back to authoring
                              │
                              └─ No gaps → APPROVE
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Add L4_ALIGN vs replace VALIDATE | Add new phase | VALIDATE checks content quality, L4_ALIGN checks requirements coverage - different concerns |
| Match by function name | Substring match | Simple, catches "check_gate" in "Implement check_gate function" |
| Gap = warning not block | Operator can accept | Some plans may intentionally defer functions (iterative implementation) |
| Extras not flagged | Ignore | Plan can do MORE than L4 specifies; that's fine |

### Input/Output Examples

**Real Example with E2-246:**

```
L4 Section for Config MVP (E2-246):

| File | Required Sections | Acceptance Test |
|------|-------------------|-----------------|
| `haios.yaml` | manifest, toggles, thresholds | Loads without error |
| `cycles.yaml` | node_bindings | Node bindings parseable |
| `components.yaml` | skills, agents, hooks | Empty placeholders |

Scope Clarification: cycles.yaml starts with node_bindings ONLY
(cycle definitions are E2-240 responsibility)

E2-246 Plan Steps:
- Step 2: Create haios.yaml with manifest, toggles, thresholds
- Step 3: Create cycles.yaml with node_bindings
- Step 4: Create components.yaml with empty registries

L4_ALIGN Check:
- haios.yaml sections covered? YES (manifest, toggles, thresholds in Step 2)
- cycles.yaml node_bindings covered? YES (Step 3)
- components.yaml registries covered? YES (Step 4)

Result: PASS (no gaps)
```

**Real Example with Missing Requirement:**

```
Hypothetical E2-240 Plan (incomplete):

L4 Requires:
- check_gate(gate_id, context)
- validate_transition(from_node, to_node)
- load_handlers(config_path)
- on_event(event_type, payload)

Plan Steps mention:
- check_gate
- validate_transition

L4_ALIGN Check:
Gaps: load_handlers, on_event

Report: "Plan missing L4 requirements: load_handlers, on_event.
        Accept gaps or revise plan?"
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Work ID not in L4 | Skip L4_ALIGN with warning ("No L4 requirements found for {id}") | Manual verification |
| L4 section has no function table | Skip with warning ("L4 section found but no functions table") | Manual verification |
| Plan step mentions partial match | Substring match (e.g., "gate_check" matches "check_gate") | Test 2 |
| L4 says "MUST" vs "SHOULD" | All treated equally for MVP; can enhance later | Deferred |

### Open Questions

**Q: Should L4_ALIGN be mandatory or optional?**

Optional for MVP. Some plans may not have corresponding L4 entries (older work items, investigations). Make it a quality enhancement, not a hard gate.

**Q: How to handle L4 requirements that span multiple work items?**

For MVP, match only exact work_id. If L4 says "### GovernanceLayer (E2-240)", only E2-240 plans trigger that section. Cross-module dependencies handled via work item `blocks:` field.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Add L4_ALIGN Phase to Skill
- [ ] Update cycle diagram: `CHECK --> VALIDATE --> L4_ALIGN --> APPROVE`
- [ ] Add "### 3. L4_ALIGN Phase" section with actions, exit criteria
- [ ] Renumber APPROVE to "### 4. APPROVE Phase"
- [ ] Update Composition Map table
- [ ] Update Quick Reference table

### Step 2: README Sync (MUST)
- [ ] **MUST:** Update `.claude/skills/plan-validation-cycle/README.md` with new phase

### Step 3: Verification
- [ ] Invoke plan-validation-cycle on E2-246 plan to test L4_ALIGN

---

## Verification

- [ ] Tests pass (`pytest tests/test_plan_validation.py -v`)
- [ ] **MUST:** `.claude/skills/plan-validation-cycle/README.md` updated
- [ ] **MUST:** `.claude/lib/README.md` updated (if l4_align.py added)
- [ ] L4_ALIGN phase documented in skill

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| L4 format changes break parsing | Medium | Use flexible regex, handle missing sections gracefully |
| False positives (plan mentions unrelated "gate") | Low | Require function name match, not just substring |
| Agent ignores L4_ALIGN warnings | Medium | Make gaps obvious in output, track in checkpoints |

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
| `.claude/skills/plan-validation-cycle/SKILL.md` | L4_ALIGN phase documented | [ ] | |
| `.claude/skills/plan-validation-cycle/README.md` | **MUST:** Updated with L4_ALIGN | [ ] | |

**Verification Commands:**
```bash
# Manual: invoke skill on E2-246 plan
Skill(skill="plan-validation-cycle")
# Expected: L4_ALIGN phase executes, reports alignment status
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
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- INV-054: Validation Cycle Fitness for Purpose (spawned this work)
- Session 158 Checkpoint: L4 enhancement with functional requirements
- L4-implementation.md: Functional Requirements Summary section

---
