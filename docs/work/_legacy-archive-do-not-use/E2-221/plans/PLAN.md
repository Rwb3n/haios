---
template: implementation_plan
status: complete
date: 2025-12-28
backlog_id: E2-221
title: Routing-Gate Skill Implementation
author: Hephaestus
lifecycle_phase: plan
session: 137
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-28T19:28:22'
---
# Implementation Plan: Routing-Gate Skill Implementation

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

Create a routing-gate bridge skill that extracts duplicated work-type routing logic from 3 cycle skills into a single reusable component. (Threshold checks moved to OBSERVE phase per S137 anti-pattern analysis.)

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | New skill, no existing code to modify |
| Lines of code affected | 0 | All new code |
| New files to create | 2 | `.claude/skills/routing-gate/SKILL.md`, `tests/test_routing_gate.py` |
| Tests to write | 4 | Work-type routing only (threshold moved to OBSERVE phase) |
| Dependencies | 0 | Pure routing, no external dependencies |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Bridge skill, single entry point |
| Risk of regression | Low | New code, existing routing unchanged until E2-223 |
| External dependencies | Low | Only observations.py function |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 20 min | High |
| Create SKILL.md | 30 min | High |
| Verify end-to-end | 10 min | High |
| **Total** | 60 min | High |

---

## Current State vs Desired State

### Current State

```markdown
# close-work-cycle/SKILL.md:184-190 - Inline routing table
**Routing Decision Table:**
| Signal | Action |
|--------|--------|
| No items returned | Report "No unblocked work. Awaiting operator direction." |
| ID starts with `INV-` | Invoke `Skill(skill="investigation-cycle")` |
| Work file has plan in `documents.plans` | Invoke `Skill(skill="implementation-cycle")` |
| Otherwise | Invoke `Skill(skill="work-creation-cycle")` to populate |
```

**Behavior:** Each of 3 cycle skills (implementation, investigation, close-work) has identical routing logic embedded in CHAIN phase. No system health checks.

**Result:** DRY violation. Observations can accumulate without forced triage. Routing has no escape hatch for urgent work.

### Desired State

```markdown
# close-work-cycle/SKILL.md - After E2-223
**Actions:**
1. Invoke routing-gate: `Skill(skill="routing-gate")`
2. Execute returned action

# routing-gate/SKILL.md - New skill
THRESHOLD CHECK:
1. If priority == "critical": skip thresholds
2. If pending_observations > 10: return invoke_triage

WORK-TYPE ROUTING:
3. If next_id starts with INV-*: return invoke_investigation
4. If has_plan: return invoke_implementation
5. If no items: return await_operator
6. Else: return invoke_work_creation
```

**Behavior:** Routing logic extracted to single skill. Threshold checks run before work-type routing. Escape hatch for critical priority.

**Result:** DRY principle satisfied. Observations forcibly triaged when threshold exceeded. Future thresholds can be added without modifying 3 skills.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Route Investigation by ID Prefix
```python
def test_route_investigation_by_prefix():
    """INV-* IDs should route to investigation-cycle."""
    result = determine_route(next_work_id="INV-049", has_plan=False, priority="medium")
    assert result["action"] == "invoke_investigation"
    assert result["threshold_triggered"] == False
```

### Test 2: Route Implementation When Has Plan
```python
def test_route_implementation_when_has_plan():
    """Work items with plans should route to implementation-cycle."""
    result = determine_route(next_work_id="E2-221", has_plan=True, priority="medium")
    assert result["action"] == "invoke_implementation"
```

### Test 3: Route Work Creation When No Plan
```python
def test_route_work_creation_when_no_plan():
    """Work items without plans should route to work-creation-cycle."""
    result = determine_route(next_work_id="E2-222", has_plan=False, priority="medium")
    assert result["action"] == "invoke_work_creation"
```

### Test 4: Await Operator When No Work
```python
def test_await_operator_when_no_work():
    """No work items should return await_operator."""
    result = determine_route(next_work_id=None, has_plan=False, priority="medium")
    assert result["action"] == "await_operator"
```

### Test 5-6: REMOVED
**Threshold tests moved to OBSERVE phase (E2-224).** S137 anti-pattern analysis showed that threshold checks in routing-gate cause context switching mid-workflow. Threshold enforcement belongs in OBSERVE phase where agent is already in reflection mode.

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

### New File: `.claude/skills/routing-gate/SKILL.md`

**SKIPPED: Exact Code Change** - This is a new file, not a modification.

### Skill Structure (from INV-048 design)

```yaml
# Frontmatter
---
name: routing-gate
description: Bridge skill for routing with threshold checks. Use in CHAIN phase.
generated: 2025-12-28
last_updated: 2025-12-28
---
```

### Call Chain Context

```
close-work-cycle CHAIN phase
    |
    +-> routing-gate skill (NEW)     # <-- What we're creating
    |       Inputs: next_work_id, has_plan, priority
    |       Returns: {action, reason, threshold_triggered}
    |
    +-> Skill invocation (investigation/implementation/work-creation/triage)
```

### Function/Component Signatures

```python
# .claude/lib/routing.py (new module)
def determine_route(
    next_work_id: Optional[str],
    has_plan: bool
) -> dict:
    """
    Determine routing action based on work-type signals.

    Pure routing logic - no threshold checks (those live in OBSERVE phase).

    Args:
        next_work_id: ID of next work item (None if no work)
        has_plan: Whether work item has documents.plans populated

    Returns:
        dict with keys:
            action: str - One of: invoke_investigation, invoke_implementation,
                          invoke_work_creation, await_operator
            reason: str - Why this action was chosen

    Raises:
        None - Returns await_operator on any error
    """
```

### Behavior Logic

**Routing-Gate Flow (Pure Work-Type Routing):**
```
Input (next_work_id, has_plan)
    |
    +-> Work-Type Routing
            next_work_id is None?
                ├─ YES → return {action: await_operator}
                └─ NO  → next_work_id starts with "INV-"?
                            ├─ YES → return {action: invoke_investigation}
                            └─ NO  → has_plan?
                                        ├─ YES → return {action: invoke_implementation}
                                        └─ NO  → return {action: invoke_work_creation}
```

**Note:** Threshold checks removed. They now live in close-work-cycle OBSERVE phase (E2-224).

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Separate routing.py module | Not inline in skill | Enables unit testing of routing logic |
| Pure routing only | No threshold checks | S137: Threshold in routing causes context-switching anti-pattern |
| Return dict not tuple | {action, reason} | Self-documenting, extensible |
| Single responsibility | Routing only | Thresholds moved to OBSERVE phase where agent is in reflection mode |

### Input/Output Examples

**Example 1: Normal investigation routing**
```
Input: determine_route(next_work_id="INV-049", has_plan=False, priority="medium")
Output: {
    "action": "invoke_investigation",
    "reason": "ID prefix INV-* routes to investigation-cycle",
    "threshold_triggered": False
}
```

**Example 2: Threshold triggers triage**
```
Input: determine_route(next_work_id="E2-221", has_plan=True, priority="medium")
  # With 15 pending observations (> threshold 10)
Output: {
    "action": "invoke_triage",
    "reason": "Pending observations (15) exceeds threshold (10)",
    "threshold_triggered": True
}
```

**Example 3: Critical priority bypasses**
```
Input: determine_route(next_work_id="E2-221", has_plan=True, priority="critical")
  # With 15 pending observations (but priority=critical)
Output: {
    "action": "invoke_implementation",
    "reason": "Critical priority bypasses threshold checks. Has plan -> implementation.",
    "threshold_triggered": False
}
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| next_work_id is None | Return await_operator | Test 4 |
| Empty pending list | Proceed to work-type routing | Implicit in Tests 1-4 |
| Invalid priority value | Treat as non-critical (no bypass) | Not tested (low risk) |
| scan_archived_observations fails | Treat as 0 pending (fail open) | TBD during implementation |

### Open Questions

**Q: Should scan_archived_observations failure block routing?**

No. Fail open - treat as 0 pending observations. Routing to work is more important than forced triage. Log a warning but don't block.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_routing_gate.py` with 6 tests from Tests First section
- [ ] Verify all 6 tests fail (red) - module doesn't exist yet

### Step 2: Create routing.py Module
- [ ] Create `.claude/lib/routing.py` with `determine_route()` function
- [ ] Implement work-type routing logic (no threshold yet)
- [ ] Tests 1-4 pass (green): investigation, implementation, work-creation, await-operator

### Step 3: Add Threshold Check
- [ ] Import `scan_archived_observations` from observations.py
- [ ] Add threshold check before work-type routing
- [ ] Test 5 passes (green): threshold triggers triage

### Step 4: Add Escape Hatch
- [ ] Add priority check before threshold check
- [ ] priority="critical" bypasses all thresholds
- [ ] Test 6 passes (green): critical priority bypasses

### Step 5: Create SKILL.md
- [ ] Create `.claude/skills/routing-gate/` directory
- [ ] Create `SKILL.md` with bridge skill documentation
- [ ] Document phases: THRESHOLD CHECK -> ROUTING -> ACTION

### Step 6: Integration Verification
- [ ] All 6 tests pass
- [ ] Run full test suite: `pytest tests/ -v` (no regressions)

### Step 7: README Sync (MUST)
- [ ] **MUST:** Create `.claude/skills/routing-gate/README.md`
- [ ] **MUST:** Update `.claude/skills/README.md` with new skill
- [ ] **MUST:** Update `.claude/lib/README.md` with routing.py

### Step 8: Consumer Verification
**SKIPPED:** New code, no consumers yet. E2-223 will add consumers.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| scan_archived_observations fails | Low | Fail open - treat as 0 pending, log warning |
| Integration breaks existing cycles | Med | E2-223 separate - this item is standalone |
| Threshold too aggressive | Low | Default 10, configurable via E2-222 |

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
| `.claude/lib/routing.py` | `determine_route()` function exists, handles all 4 actions | [ ] | |
| `tests/test_routing_gate.py` | 6 tests exist and all pass | [ ] | |
| `.claude/skills/routing-gate/SKILL.md` | Bridge skill documented with phases | [ ] | |
| `.claude/skills/routing-gate/README.md` | **MUST:** Describes skill purpose | [ ] | |
| `.claude/lib/README.md` | **MUST:** Lists routing.py | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_routing_gate.py -v
# Expected: 6 tests passed
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

- Investigation: INV-048 (Routing Gate Architecture with Observation Triage Threshold)
- Design spec: `docs/work/archive/INV-048/investigations/001-*.md`
- Related: E2-218 (observation-triage-cycle)
- Related: E2-222 (Routing Threshold Configuration)
- Related: E2-223 (Integrate Routing-Gate into Cycle Skills)
- Memory: 78921, 78924, 78876 (gate contract patterns from INV-033)

---
