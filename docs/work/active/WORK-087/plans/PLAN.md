---
template: implementation_plan
status: complete
date: 2026-02-03
backlog_id: WORK-087
title: Implement Caller Chaining
author: Hephaestus
lifecycle_phase: plan
session: 303
version: '1.5'
generated: 2025-12-21
last_updated: '2026-02-03T23:05:28'
---
# Implementation Plan: Implement Caller Chaining

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

close-work-cycle CHAIN phase will present routing options to the caller without auto-executing, making "complete without spawn" a first-class valid outcome per REQ-LIFECYCLE-004.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/skills/close-work-cycle/SKILL.md` |
| Lines of code affected | ~50 | CHAIN phase section (lines 164-214) |
| New files to create | 0 | Refactor existing |
| Tests to write | 3 | Unit + integration tests |
| Dependencies | 0 | No module consumers of CHAIN logic |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Skill markdown only, no code modules |
| Risk of regression | Low | Existing tests don't cover CHAIN auto-execution |
| External dependencies | Low | No external APIs |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 15 min | High |
| Refactor CHAIN phase | 20 min | High |
| Verify integration | 10 min | High |
| **Total** | 45 min | High |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/skills/close-work-cycle/SKILL.md:191-200
6. **Apply routing decision table** (WORK-030: type field is authoritative):
   - If `next_work_id` is None → `await_operator`
   - If `type` == "investigation" → `invoke_investigation`
   - If `has_plan` is True → `invoke_implementation`
   - Else → `invoke_work_creation`
7. Execute the action:
   - `invoke_investigation` -> `Skill(skill="investigation-cycle")`
   - `invoke_implementation` -> `Skill(skill="implementation-cycle")`
   - `invoke_work_creation` -> `Skill(skill="work-creation-cycle")`
   - `await_operator` -> Report "No unblocked work. Awaiting operator direction."
```

**Behavior:** CHAIN phase determines routing action then auto-executes the corresponding Skill() call.

**Result:** Caller (Claude/operator) has no choice - routing is embedded in skill, violating REQ-LIFECYCLE-004 "chaining is caller choice."

### Desired State

```markdown
# .claude/skills/close-work-cycle/SKILL.md:191-210 (target)
6. **Determine routing options** (WORK-030: type field is authoritative):
   - Read next work from `just ready`
   - Determine suggested action based on type field

7. **Present options to caller** (REQ-LIFECYCLE-004):
   Work complete. Choose next action:
   1. Complete without spawn (store output, no next work)
   2. Chain to {suggested_cycle} for {next_work_id}
   3. Select different work item

   Await caller choice before executing.

8. **Execute chosen action:**
   - Only after explicit caller selection
   - "Complete without spawn" is valid, emits no warning
```

**Behavior:** CHAIN phase presents options, waits for caller choice, then executes selected action.

**Result:** Caller controls chaining decision per REQ-LIFECYCLE-004. "Complete without spawn" is first-class option.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: CHAIN Phase Presents Options Without Auto-Executing
```python
def test_chain_phase_does_not_auto_invoke_skill():
    """CHAIN phase presents options but does not auto-execute Skill() calls."""
    # Read close-work-cycle SKILL.md
    skill_content = Path(".claude/skills/close-work-cycle/SKILL.md").read_text()

    # Find CHAIN phase section
    chain_section = extract_section(skill_content, "### 4. CHAIN Phase")

    # Should NOT have direct Skill() invocation as automatic action
    # Should have "Present options" or "Await caller choice" pattern
    assert "Present options" in chain_section or "Await" in chain_section
    assert "Complete without spawn" in chain_section
```

### Test 2: Complete Without Spawn Is Valid Option
```python
def test_complete_without_spawn_is_valid_option():
    """'Complete without spawn' is listed as valid option without warnings."""
    skill_content = Path(".claude/skills/close-work-cycle/SKILL.md").read_text()
    chain_section = extract_section(skill_content, "### 4. CHAIN Phase")

    # Option 1 should be "Complete without spawn"
    assert "Complete without spawn" in chain_section
    # Should not contain warning language about this option
    assert "warn" not in chain_section.lower() or "warning" not in chain_section.split("Complete without spawn")[1][:100].lower()
```

### Test 3: Routing Table Preserved But Not Auto-Executed
```python
def test_routing_table_preserved():
    """Routing decision table still exists for guidance, but execution is caller choice."""
    skill_content = Path(".claude/skills/close-work-cycle/SKILL.md").read_text()
    chain_section = extract_section(skill_content, "### 4. CHAIN Phase")

    # Routing logic should still exist (for determining suggestions)
    assert "type" in chain_section  # Type-based routing
    assert "investigation" in chain_section  # Investigation routing

    # But should have explicit caller choice language
    assert "choice" in chain_section.lower() or "choose" in chain_section.lower() or "select" in chain_section.lower()
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does. -->

### Exact Code Change

**File:** `.claude/skills/close-work-cycle/SKILL.md`
**Location:** Lines 164-214 (CHAIN Phase section)

**Current Code:**
```markdown
# .claude/skills/close-work-cycle/SKILL.md:186-200

#### 4b. Route to Next Work

**Actions:**
1. (Closure already completed in MEMORY phase)
2. (Checkpoint completed in 4a)
3. Query next work: `just ready`
4. If items returned, read first work file to check `documents.plans`
5. Read work item `type` field from WORK.md
6. **Apply routing decision table** (WORK-030: type field is authoritative):
   - If `next_work_id` is None → `await_operator`
   - If `type` == "investigation" → `invoke_investigation`
   - If `has_plan` is True → `invoke_implementation`
   - Else → `invoke_work_creation`
7. Execute the action:
   - `invoke_investigation` -> `Skill(skill="investigation-cycle")`
   - `invoke_implementation` -> `Skill(skill="implementation-cycle")`
   - `invoke_work_creation` -> `Skill(skill="work-creation-cycle")`
   - `await_operator` -> Report "No unblocked work. Awaiting operator direction."

**MUST:** Do not pause for acknowledgment - checkpoint then execute routing immediately.
```

**Changed Code:**
```markdown
# .claude/skills/close-work-cycle/SKILL.md:186-220 (target)

#### 4b. Route to Next Work (REQ-LIFECYCLE-004: Caller Choice)

**Actions:**
1. (Closure already completed in MEMORY phase)
2. (Checkpoint completed in 4a)
3. Query next work: `just ready`
4. If items returned, read first work file to determine suggested routing
5. Read work item `type` field from WORK.md
6. **Determine suggested action** (WORK-030: type field is authoritative):
   - If `next_work_id` is None → suggest `complete_without_spawn`
   - If `type` == "investigation" → suggest `investigation-cycle`
   - If `has_plan` is True → suggest `implementation-cycle`
   - Else → suggest `work-creation-cycle`

7. **Present options to caller** (REQ-LIFECYCLE-004):

   Use AskUserQuestion to present choices:
   ```
   AskUserQuestion(questions=[{
     "question": "Work closed. What next?",
     "header": "Next Action",
     "options": [
       {"label": "Complete without spawn", "description": "Store output, no next work item"},
       {"label": "Chain to {suggested_cycle}", "description": "Continue with {next_work_id}"},
       {"label": "Select different work", "description": "Choose from queue"}
     ],
     "multiSelect": false
   }])
   ```

8. **Execute chosen action:**
   - `Complete without spawn` → Report "Work complete. No spawn." (valid, no warning)
   - `Chain to {cycle}` → `Skill(skill="{cycle}")`
   - `Select different work` → `Skill(skill="survey-cycle")`

**Note:** "Complete without spawn" is a first-class valid outcome per REQ-LIFECYCLE-004.
```

**Diff:**
```diff
-#### 4b. Route to Next Work
+#### 4b. Route to Next Work (REQ-LIFECYCLE-004: Caller Choice)

 **Actions:**
 1. (Closure already completed in MEMORY phase)
 2. (Checkpoint completed in 4a)
 3. Query next work: `just ready`
-4. If items returned, read first work file to check `documents.plans`
+4. If items returned, read first work file to determine suggested routing
 5. Read work item `type` field from WORK.md
-6. **Apply routing decision table** (WORK-030: type field is authoritative):
-   - If `next_work_id` is None → `await_operator`
-   - If `type` == "investigation" → `invoke_investigation`
-   - If `has_plan` is True → `invoke_implementation`
-   - Else → `invoke_work_creation`
-7. Execute the action:
-   - `invoke_investigation` -> `Skill(skill="investigation-cycle")`
-   - `invoke_implementation` -> `Skill(skill="implementation-cycle")`
-   - `invoke_work_creation` -> `Skill(skill="work-creation-cycle")`
-   - `await_operator` -> Report "No unblocked work. Awaiting operator direction."
+6. **Determine suggested action** (WORK-030: type field is authoritative):
+   - If `next_work_id` is None → suggest `complete_without_spawn`
+   - If `type` == "investigation" → suggest `investigation-cycle`
+   - If `has_plan` is True → suggest `implementation-cycle`
+   - Else → suggest `work-creation-cycle`
+
+7. **Present options to caller** (REQ-LIFECYCLE-004):
+   Use AskUserQuestion to present choices [...]
+
+8. **Execute chosen action:**
+   - `Complete without spawn` → Report "Work complete. No spawn." (valid, no warning)
+   - `Chain to {cycle}` → `Skill(skill="{cycle}")`
+   - `Select different work` → `Skill(skill="survey-cycle")`

-**MUST:** Do not pause for acknowledgment - checkpoint then execute routing immediately.
+**Note:** "Complete without spawn" is a first-class valid outcome per REQ-LIFECYCLE-004.
```

### Call Chain Context

```
/close command
    |
    +-> observation-capture-cycle
    |
    +-> dod-validation-cycle
    |
    +-> close-work-cycle
            |
            +-> VALIDATE phase
            +-> ARCHIVE phase (just close-work)
            +-> MEMORY phase (ingester_ingest)
            +-> CHAIN phase     # <-- What we're changing
                    |
                    +-> checkpoint-cycle
                    +-> [CHANGED] AskUserQuestion (present options)
                    +-> [CHANGED] Execute CHOSEN action (not auto)
```

### Behavior Logic

**Current Flow (auto-execute):**
```
CHAIN → determine routing → auto-execute Skill() → next cycle starts
                              ↓
                       (no operator choice)
```

**Fixed Flow (caller choice):**
```
CHAIN → determine suggestion → AskUserQuestion(options)
                                    |
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
            "Complete without"  "Chain to X"  "Select different"
                    ↓               ↓               ↓
            Report done      Skill(X)      survey-cycle
            (no warning)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Use AskUserQuestion | Present options via tool | Consistent with other skill patterns; structured choice |
| Keep routing logic | Determine suggestion, don't remove | Provides helpful default; operator can override |
| "Complete without spawn" first | List as option 1 | Per REQ-LIFECYCLE-004, this is valid not exceptional |
| No warning for complete-only | Remove any warning language | Valid outcome should not warn |
| survey-cycle for "select different" | Delegate to existing survey | Reuse existing queue selection logic |

### Input/Output Examples

**Before Fix (current behavior):**
```
CHAIN phase after closing WORK-087:
  1. Queries `just ready` → finds WORK-066
  2. Reads WORK-066 type: feature, no plan
  3. Auto-executes: Skill(skill="work-creation-cycle")

Problem: Operator had no choice, work-creation-cycle started automatically
```

**After Fix (expected):**
```
CHAIN phase after closing WORK-087:
  1. Queries `just ready` → finds WORK-066
  2. Reads WORK-066 type: feature, no plan
  3. Determines suggestion: work-creation-cycle
  4. Presents AskUserQuestion:
     - "Complete without spawn" (operator chose this)
     - "Chain to work-creation-cycle for WORK-066"
     - "Select different work"
  5. Operator chose: "Complete without spawn"
  6. Reports: "Work complete. No spawn."

Improvement: Operator controlled the decision
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No ready items | "Complete without spawn" becomes only option | Test 2 |
| Investigation type | Suggest investigation-cycle but allow override | Test 3 |
| Multiple items in queue | Show first as suggestion, "Select different" for others | Test 3 |

### Open Questions

**Q: Should we remove MUST: "Do not pause for acknowledgment"?**

Yes - this directive contradicts REQ-LIFECYCLE-004. The new design explicitly pauses for choice.

---

## Open Decisions (MUST resolve before implementation)

<!-- No operator_decisions in WORK-087 frontmatter. All design decisions made in CH-004 chapter. -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| N/A | - | - | No unresolved decisions from work item |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_close_work_cycle.py` with 3 tests
- [ ] Test 1: CHAIN phase presents options (fails - current auto-executes)
- [ ] Test 2: "Complete without spawn" is valid option (fails - not present)
- [ ] Test 3: Routing table preserved but not auto-executed (fails)
- [ ] Verify all tests fail (red)

### Step 2: Refactor CHAIN Phase Section
- [ ] Edit `.claude/skills/close-work-cycle/SKILL.md`
- [ ] Replace "Apply routing decision table" with "Determine suggested action"
- [ ] Replace "Execute the action" with "Present options to caller"
- [ ] Add AskUserQuestion pattern for choice presentation
- [ ] Add "Execute chosen action" section
- [ ] Remove "MUST: Do not pause" directive
- [ ] Add "Complete without spawn is valid" note
- [ ] Tests 1, 2, 3 pass (green)

### Step 3: Update Key Design Decisions Table
- [ ] Add decision about caller choice (REQ-LIFECYCLE-004)
- [ ] Document removal of auto-execute pattern

### Step 4: Integration Verification
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Verify no regressions in close-work-cycle behavior
- [ ] Manual test: close a work item, verify options presented

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update `.claude/skills/close-work-cycle/README.md` if exists
- [ ] **MUST:** Verify skill description reflects new behavior

### Step 6: Consumer Verification
- [ ] Grep for "close-work-cycle" references in other skills
- [ ] Verify routing-gate skill alignment (if references close-work-cycle)
- [ ] No code migration needed - skill markdown only

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment: Misinterpreting REQ-LIFECYCLE-004 intent | Medium | Verified against L4 spec: "Chaining is caller choice, not callee side-effect" |
| Integration: Other skills expect auto-routing | Low | Grep for consumers; close-work-cycle is terminal in chain |
| Regression: Breaking existing workflows | Low | Adding options doesn't break; old behavior is subset of new |
| Scope creep: Adding features beyond spec | Low | Limited to CHAIN phase changes only; no module changes |

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

**MUST** read `docs/work/active/WORK-087/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Ensure CycleRunner.run() returns output without auto-chaining | [ ] | Already done in WORK-084; verify unchanged |
| Update close-work-cycle CHAIN phase to prompt options without auto-executing | [ ] | Read SKILL.md, verify AskUserQuestion pattern |
| Verify "Complete without spawn" path doesn't emit warnings | [ ] | Read SKILL.md, verify no warning language |
| Unit tests: design completes -> no implementation started | [ ] | Run pytest, verify test passes |
| Integration test: Design -> prompt -> choose "store only" -> verify no spawn | [ ] | Manual test or automated verification |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/close-work-cycle/SKILL.md` | CHAIN phase has AskUserQuestion pattern | [ ] | |
| `tests/test_close_work_cycle.py` | 3 tests exist and pass | [ ] | |
| `.claude/haios/modules/cycle_runner.py` | run() unchanged, no auto-chain | [ ] | Verify WORK-084 not regressed |

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

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-LIFECYCLE-004)
- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-004-CallerChaining.md (chapter spec)
- @.claude/skills/close-work-cycle/SKILL.md (target file)
- @docs/work/active/WORK-084/WORK.md (LifecycleSignatures - dependency)
- @docs/work/active/WORK-085/WORK.md (PauseSemantics - dependency)
- Memory: 83328 "Chaining is caller choice, not callee side-effect"
- Memory: 79805 "Instruction-based chaining: Skills contain routing instructions"

---
