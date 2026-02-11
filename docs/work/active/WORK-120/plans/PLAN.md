---
template: implementation_plan
status: complete
date: 2026-02-11
backlog_id: WORK-120
title: "Implement Session Ceremonies (CH-014)"
author: Hephaestus
lifecycle_phase: plan
session: 343
version: "1.5"
generated: 2026-02-11
last_updated: 2026-02-11T19:45:15
---
# Implementation Plan: Implement Session Ceremonies (CH-014)

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

All three session ceremonies (Start, End, Checkpoint) will have working implementations with ceremony logic, contract enforcement, and event logging per REQ-CEREMONY-001/002.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | session-start-ceremony/SKILL.md, session-end-ceremony/SKILL.md, checkpoint-cycle/SKILL.md |
| Lines of code affected | ~250 | Skill markdown expansions |
| New files to create | 1 | tests/test_session_ceremonies.py |
| Tests to write | 10 | 3 session-start, 4 session-end, 3 checkpoint/shared |
| Dependencies | 3 | governance_events.py, governance_layer.py, ceremony_runner.py (read-only, not modified) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Skills are markdown; no runtime code imports to break |
| Risk of regression | Low | De-stubbing stubs; existing coldstart/checkpoint flows unaffected |
| External dependencies | Low | All infrastructure already exists (governance_events, ceremony_context) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| Skill de-stubbing (3 files) | 20 min | High |
| Integration verification | 10 min | High |
| **Total** | **45 min** | |

---

## Current State vs Desired State

### Current State

**session-start-ceremony** (`.claude/skills/session-start-ceremony/SKILL.md`):
- `stub: true` in frontmatter
- Contract defined (input/output/side_effects)
- 5 ceremony steps as one-liners — no implementation detail
- Agent must improvise execution

**session-end-ceremony** (`.claude/skills/session-end-ceremony/SKILL.md`):
- `stub: true` in frontmatter
- Contract defined
- 4 ceremony steps as one-liners — no orphan detection detail
- Never invoked by any workflow

**checkpoint-cycle** (`.claude/skills/checkpoint-cycle/SKILL.md`):
- Fully functional with SCAFFOLD/FILL/VERIFY/CAPTURE/COMMIT phases
- `type: ceremony` field present
- No contract validation enforcement (predates CH-011)

**Infrastructure that EXISTS (read-only dependencies):**
- `governance_events.log_session_start(session, agent)` — works
- `governance_events.log_session_end(session, agent)` — works
- `governance_layer.scan_incomplete_work(project_root)` — works
- `governance_layer.detect_orphan_session()` — works
- `CeremonyRunner.invoke()` — works
- `ceremony_context()` — works

**Behavior:** Session start event logged via `just session-start N` (inline Python). No formal ceremony. Session end logged via `just session-end N`. No orphan detection. Checkpoint works but doesn't reference ceremony contracts.

**Result:** Sessions lack ceremony boundaries. No orphan detection on end. Agent has no detailed instructions for ceremony execution.

### Desired State

**session-start-ceremony**: De-stubbed with:
1. `stub: true` removed
2. Detailed ceremony steps: read `.claude/session`, increment, use `ceremony_context("session-start")`, log event, load config, load epoch/arcs, query memory refs, report state
3. Reference to governance_events.log_session_start()
4. Integration flow showing relationship to coldstart

**session-end-ceremony**: De-stubbed with:
1. `stub: true` removed
2. Detailed ceremony steps: use `ceremony_context("session-end")`, run `scan_incomplete_work()`, check `git status`, log event, report summary
3. Reference to governance_events.log_session_end()
4. Session summary format (completed, orphans, pending)

**checkpoint-cycle**: Updated with:
1. Contract validation note referencing CH-011 framework
2. Existing functionality preserved

**Behavior:** All three session ceremonies have detailed implementation instructions with ceremony boundary enforcement.

**Result:** Agent knows exactly how to execute each session ceremony. Orphan detection on session end. Contract references for checkpoint.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Session Start Not Stub
```python
def test_session_start_ceremony_not_stub():
    """session-start-ceremony must not have stub: true."""
    skill_path = PROJECT_ROOT / ".claude/skills/session-start-ceremony/SKILL.md"
    content = skill_path.read_text(encoding="utf-8")
    fm = _extract_frontmatter(content)
    assert fm.get("stub") is not True
```

### Test 2: Session Start Has Detailed Ceremony Steps
```python
def test_session_start_has_detailed_steps():
    """session-start-ceremony must have ceremony steps with implementation detail."""
    skill_path = PROJECT_ROOT / ".claude/skills/session-start-ceremony/SKILL.md"
    content = skill_path.read_text(encoding="utf-8")
    assert "## Ceremony Steps" in content
    steps_idx = content.index("## Ceremony Steps")
    steps_section = content[steps_idx:]
    assert len(steps_section) > 300, "Ceremony steps too brief"
```

### Test 3: Session Start References Ceremony Context
```python
def test_session_start_references_ceremony_context():
    """session-start-ceremony must reference ceremony boundary enforcement."""
    skill_path = PROJECT_ROOT / ".claude/skills/session-start-ceremony/SKILL.md"
    content = skill_path.read_text(encoding="utf-8")
    assert "ceremony_context" in content or "ceremony boundary" in content.lower()
```

### Test 4: Session End Not Stub
```python
def test_session_end_ceremony_not_stub():
    """session-end-ceremony must not have stub: true."""
    skill_path = PROJECT_ROOT / ".claude/skills/session-end-ceremony/SKILL.md"
    content = skill_path.read_text(encoding="utf-8")
    fm = _extract_frontmatter(content)
    assert fm.get("stub") is not True
```

### Test 5: Session End Has Orphan Detection
```python
def test_session_end_has_orphan_detection():
    """session-end-ceremony must include orphan work detection."""
    skill_path = PROJECT_ROOT / ".claude/skills/session-end-ceremony/SKILL.md"
    content = skill_path.read_text(encoding="utf-8")
    assert "orphan" in content.lower()
    assert "scan_incomplete_work" in content or "incomplete work" in content.lower()
```

### Test 6: Session End Has Uncommitted Change Check
```python
def test_session_end_has_uncommitted_check():
    """session-end-ceremony must check for uncommitted changes."""
    skill_path = PROJECT_ROOT / ".claude/skills/session-end-ceremony/SKILL.md"
    content = skill_path.read_text(encoding="utf-8")
    assert "uncommitted" in content.lower() or "git status" in content.lower()
```

### Test 7: Session End References Ceremony Context
```python
def test_session_end_references_ceremony_context():
    """session-end-ceremony must reference ceremony boundary enforcement."""
    skill_path = PROJECT_ROOT / ".claude/skills/session-end-ceremony/SKILL.md"
    content = skill_path.read_text(encoding="utf-8")
    assert "ceremony_context" in content or "ceremony boundary" in content.lower()
```

### Test 8: Checkpoint Has Contract Reference
```python
def test_checkpoint_has_contract_reference():
    """checkpoint-cycle must reference ceremony contracts."""
    skill_path = PROJECT_ROOT / ".claude/skills/checkpoint-cycle/SKILL.md"
    content = skill_path.read_text(encoding="utf-8")
    assert "contract" in content.lower()
```

### Test 9: All Session Ceremonies Have Type Field
```python
def test_all_session_ceremonies_have_type():
    """All session ceremony skills must have type: ceremony."""
    for name in ["session-start-ceremony", "session-end-ceremony", "checkpoint-cycle"]:
        skill_path = PROJECT_ROOT / f".claude/skills/{name}/SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        fm = _extract_frontmatter(content)
        assert fm.get("type") == "ceremony", f"{name} missing type: ceremony"
```

### Test 10: Session Ceremonies Have Side Effects Declared
```python
def test_session_ceremonies_have_side_effects():
    """All session ceremony skills must declare side_effects."""
    for name in ["session-start-ceremony", "session-end-ceremony", "checkpoint-cycle"]:
        skill_path = PROJECT_ROOT / f".claude/skills/{name}/SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        fm = _extract_frontmatter(content)
        assert "side_effects" in fm, f"{name} missing side_effects"
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
     4. Input/output examples with REAL data from the system

     PATTERN VERIFICATION (E2-255 Learning):
     IF creating a new module that imports from siblings:
       - MUST read at least one sibling module for import/error patterns
       - Verify: try/except conditional imports? sys.path manipulation? error types?
       - Use the SAME patterns as existing siblings (consistency > preference)

     IF modifying existing module:
       - Follow existing patterns in that file

     IF creating module with no siblings (new directory):
       - Document chosen patterns in Key Design Decisions with rationale -->

### Exact Changes

These are skill markdown files (agent instructions), not Python code. Changes are content expansions.

**File 1:** `.claude/skills/session-start-ceremony/SKILL.md`

Remove from frontmatter:
```diff
-stub: true
```

Replace Ceremony Steps section with detailed implementation:
```markdown
## Ceremony Steps

All steps execute within a `ceremony_context("session-start")` boundary.

### Step 1: Read Session Number
- Read `.claude/session` file
- Parse current session number (last non-comment line as integer)
- Increment by 1 for new session

### Step 2: Update Session File
- Write new session number to `.claude/session`
- Update `.claude/haios-status.json` with `session_delta`

### Step 3: Log SessionStarted Event
- Call `just session-start {N}` which invokes:
  `governance_events.log_session_start(session, "Hephaestus")`
- Event logged to `.claude/haios/governance-events.jsonl`

### Step 4: Load Configuration
- Read `.claude/haios/config/haios.yaml`
- Extract epoch, active_arcs, paths

### Step 5: Load Epoch Context
- Read `epoch.epoch_file` from config
- For each arc in `epoch.active_arcs`, read `{arcs_dir}/{arc}/ARC.md`

### Step 6: Query Memory Refs
- If prior checkpoint has `load_memory_refs`, query those concept IDs
- Use `db_query` to retrieve concept content

### Step 7: Report Session State
- Report session number, epoch, active arcs to operator
- List any drift warnings from prior session
- List pending items from prior checkpoint
```

Add integration section:
```markdown
## Integration with Coldstart

The `/coldstart` command orchestrates context loading via ColdstartOrchestrator.
Within coldstart, session-start-ceremony is invoked via `just session-start N`.

Flow:
  /coldstart → ColdstartOrchestrator.run() → context loaded
    → just session-start N → SessionStarted event logged
    → survey-cycle → work selection

This ceremony formalizes the session entry boundary. The coldstart skill
handles the orchestration; this ceremony handles the state change.
```

**File 2:** `.claude/skills/session-end-ceremony/SKILL.md`

Remove from frontmatter:
```diff
-stub: true
```

Replace Ceremony Steps section with detailed implementation:
```markdown
## Ceremony Steps

All steps execute within a `ceremony_context("session-end")` boundary.

### Step 1: Check for Orphan Work Items
- Run `scan_incomplete_work(project_root)` from governance_layer
- This checks for work items with `queue_position: working` that were not closed
- Report any orphan items found to operator with their IDs and titles

### Step 2: Check for Uncommitted Changes
- Run `git status --porcelain` to detect uncommitted changes
- If changes exist, warn operator:
  "Uncommitted changes detected. Consider creating a checkpoint before ending session."
- This is a warning, not a blocker

### Step 3: Log SessionEnded Event
- Call `just session-end {N}` which invokes:
  `governance_events.log_session_end(session, "Hephaestus")`
- Event logged to `.claude/haios/governance-events.jsonl`

### Step 4: Report Session Summary
Format:
  Session {N} ended.
  - Completed: [list work items completed this session]
  - Orphan items: [count] (list IDs if any)
  - Uncommitted changes: [yes/no]
  - Pending for next session: [list from checkpoint]
```

**File 3:** `.claude/skills/checkpoint-cycle/SKILL.md`

Add contract validation note after existing "What to Do" heading:
```markdown
### 0. Contract Validation (CH-011)

This ceremony has input/output contracts defined in frontmatter per REQ-CEREMONY-002.
Before proceeding, verify:
- `session_number` is available (from context or `.claude/session` file)
- Summary of work done is available for `completed` field

Contract enforcement mode is controlled by `ceremony_contract_enforcement`
toggle in haios.yaml (currently: warn).
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Skills are markdown, not Python | Expand markdown instructions for agent | Skills are agent instructions; the agent is the runtime. No Python code needed for ceremony execution. |
| Keep coldstart separate from session-start | session-start invoked WITHIN coldstart | Coldstart orchestrates context loading; session-start formalizes the boundary. Already works this way via `just session-start N`. |
| Orphan detection via existing functions | Use `scan_incomplete_work()` | Already built and tested (INV-052). No reinvention needed. |
| checkpoint-cycle update is minimal | Add contract validation note only | checkpoint-cycle already works well; just needs CH-011 contract framework reference. |
| Remove stub: true entirely | Delete the field | Stub was a signal for CH-014; removing signals implementation is complete. |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No prior checkpoint exists | session-start handles gracefully (first session) | Test 2 |
| No orphan work found | session-end reports clean session | Test 5 |
| Uncommitted changes exist | session-end warns but doesn't block | Test 6 |
| ceremony_context nesting | Not possible — ceremony_context forbids nesting | Existing tests in test_ceremony_context.py |

### Open Questions

None — scope is well-defined by CH-014 and existing stub contracts.

---

## Open Decisions (MUST resolve before implementation)

<!-- Decisions from work item's operator_decisions field.
     If ANY row has [BLOCKED] in Chosen column, plan-validation-cycle will BLOCK.

     POPULATE FROM: Work item frontmatter `operator_decisions` field
     - question -> Decision column
     - options -> Options column
     - chosen -> Chosen column (null = [BLOCKED])
     - rationale -> Rationale column (filled when resolved) -->

No open decisions. Scope defined by CH-014 chapter and existing stub contracts.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_session_ceremonies.py` with all 10 tests
- [ ] Verify tests 1, 4 fail (stub: true still present)
- [ ] Verify tests 2, 3, 5, 6, 7 fail (content too brief / missing references)

### Step 2: De-stub session-start-ceremony
- [ ] Remove `stub: true` from frontmatter
- [ ] Expand Ceremony Steps with 7 detailed sub-steps
- [ ] Add ceremony_context boundary reference
- [ ] Add "Integration with Coldstart" section
- [ ] Tests 1, 2, 3, 9, 10 pass (green)

### Step 3: De-stub session-end-ceremony
- [ ] Remove `stub: true` from frontmatter
- [ ] Expand Ceremony Steps with 4 detailed sub-steps (orphan detection, git status, event log, summary)
- [ ] Add ceremony_context boundary reference
- [ ] Tests 4, 5, 6, 7, 9, 10 pass (green)

### Step 4: Update checkpoint-cycle contract
- [ ] Add "Contract Validation (CH-011)" section
- [ ] Test 8 passes (green)

### Step 5: Integration Verification
- [ ] All 10 tests pass
- [ ] Run full test suite (no regressions)

### Step 6: Consumer Verification
- [ ] Grep for `stub: true` in session ceremony files — zero results
- [ ] Verify coldstart skill references session-start-ceremony correctly
- [ ] No migration/rename needed — file paths unchanged

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Skill changes break coldstart flow | Medium | coldstart invokes `just session-start N`, not the skill directly; changes are additive |
| Tests too coupled to skill content | Low | Test structure (sections exist, minimum length) not exact wording |

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

**MUST** read `docs/work/active/WORK-120/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| session-start-ceremony de-stubbed | [ ] | Read SKILL.md, no stub: true |
| session-end-ceremony de-stubbed | [ ] | Read SKILL.md, no stub: true |
| checkpoint-cycle contract validation | [ ] | Read SKILL.md, contract reference present |
| SessionStarted/SessionEnded events logged | [ ] | Already working via governance_events.py |
| Orphan work detection on session end | [ ] | Read SKILL.md, scan_incomplete_work reference |
| Unit tests for session-start | [ ] | pytest output |
| Unit tests for session-end | [ ] | pytest output |
| Unit tests for checkpoint contract | [ ] | pytest output |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/session-start-ceremony/SKILL.md` | No stub, detailed steps, ceremony_context ref | [ ] | |
| `.claude/skills/session-end-ceremony/SKILL.md` | No stub, orphan detection, uncommitted check | [ ] | |
| `.claude/skills/checkpoint-cycle/SKILL.md` | Contract validation reference added | [ ] | |
| `tests/test_session_ceremonies.py` | 10 tests, all passing | [ ] | |
| `Grep: stub.*true` in session ceremony skills | Zero results | [ ] | |

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

- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-014-SessionCeremonies.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-001, REQ-CEREMONY-002)
- @.claude/haios/modules/ceremony_runner.py
- @.claude/haios/lib/governance_events.py
- @.claude/haios/modules/governance_layer.py (ceremony_context, scan_incomplete_work)

---
