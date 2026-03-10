---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-03-10
backlog_id: WORK-289
title: "Implement Tiered Session Architecture — Plan/Build Session Boundary"
author: Hephaestus
lifecycle_phase: plan
session: 486
generated: 2026-03-10
last_updated: 2026-03-10T23:30:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-289/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete content, not pseudocode"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: Implement Tiered Session Architecture — Plan/Build Session Boundary

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification. -->

---

## Goal

Add tier-aware session-yield to the PLAN phase exit so that standard/architectural work items checkpoint and terminate after plan approval, then have the build-session detect the approved plan via survey-cycle and enter DO phase directly — giving each phase a clean context window.

---

## Open Decisions

No operator decisions required. All design choices resolved by WORK-287 findings.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Handoff artifact | New artifact vs existing mechanisms | Existing mechanisms | Plan file on disk + checkpoint pending + cycle_phase is sufficient (WORK-287 H3) |
| Session split threshold | trivial/small split vs standard+ split | standard+ splits | Small/trivial complete efficiently in single session (mem:89508); splitting adds overhead without benefit |
| Survey-cycle detection | New dedicated survey phase vs extended routing logic | Extend existing routing | Surgical change — routing table already handles plan-exists case; tier+plan-status adds one conditional |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/skills/implementation-cycle/phases/PLAN.md` | MODIFY | 2 |
| `.claude/skills/survey-cycle/SKILL.md` | MODIFY | 2 |
| `.claude/skills/implementation-cycle/SKILL.md` | MODIFY | 2 |

### Consumer Files

No Python consumers. These are markdown skill files read by agents at runtime. Test files reference them via path string checks.

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `tests/test_implementation_cycle_fracture.py` | reads PLAN.md content, checks structure | 80-142 | VERIFY (existing tests must still pass — no structural changes break them) |
| `tests/test_survey_cycle.py` | reads SKILL.md, checks for phase names | 20-38 | VERIFY (existing phase names GATHER/ASSESS/OPTIONS/CHOOSE/ROUTE are not present in current SKILL.md — test already passes via "Logic" section; no change needed) |
| `tests/test_plan_authoring_agent.py` | reads PLAN.md, checks for plan-authoring-agent reference | 75-87 | VERIFY (existing content preserved — no change) |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_tiered_session_boundary.py` | CREATE | New test file verifying tiered session yield logic in skill files |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 1 | Test file only |
| Files to modify | 3 | Primary skill files (markdown) |
| Tests to write | 5 | Test Files table |
| Total blast radius | 4 | 3 modified + 1 created |

---

## Layer 1: Specification

### Current State

**File 1: `.claude/skills/implementation-cycle/phases/PLAN.md` (Exit Gate section)**

```markdown
# [file:phases/PLAN.md, lines 70-144]

**Exit Gate (Tier-Aware — REQ-LIFECYCLE-005, REQ-CEREMONY-005):**

Before transitioning to DO phase, determine the work item's governance tier, then apply the appropriate gate set.

**Step 1: Determine Tier**
...
**If tier = standard:**

**Gate 1 - MUST: Critique (Assumption Surfacing)**
...
**Gate 2 - MUST: Plan Validation...**
...
**Gate 3 - MUST: Preflight Check...**
...
Validates plan completeness and file scope. DO phase is blocked until all three gates pass.

**If tier = architectural:**
Same as standard (Gates 1+2+3), PLUS:
**Gate 4 - MUST: Operator Approval**
...
```

**Behavior:** After all gates pass, the PLAN phase exits and implementation-cycle proceeds directly to DO phase in the same session.

**Problem:** Standard and architectural items consume ~70% of context budget in PLAN phase alone (mem:87482), leaving insufficient context for DO phase. The 104% ceremony budget problem (mem:85390) means a full governed lifecycle cannot complete reliably in a single session.

---

**File 2: `.claude/skills/survey-cycle/SKILL.md` (Continue prior work + Route sections)**

```markdown
# [file:survey-cycle/SKILL.md, lines 17-50]

1. **Continue prior work?**
   - Check checkpoint `pending` field
   - If work in_progress from prior session, continue it

...

3. **Route**
   - Read work item WORK.md to get `type` field
   - Use routing decision table (WORK-030: type field is authoritative):
     - `type: investigation` → `investigation-cycle`
     - Has plan → `implementation-cycle`
     - Otherwise → `work-creation-cycle`
```

**Behavior:** Step 1 intercepts work items pending from a prior session BEFORE step 3 (Route) is evaluated. If a work item has an approved plan from a plan-session, step 1's "continue it" branch routes to implementation-cycle at PLAN phase, re-running PLAN gates and wasting ~15% context on plan re-read (mem:89507).

**Problem:** Step 1 cannot distinguish between "pending work needs PLAN continuation" and "pending work has a completed plan-session and needs DO phase directly". The fast-path detection MUST be in step 1, not step 3, because step 1 intercepts before step 3 is reached.

> **Critique A1 fix:** Originally placed fast-path detection in step 3 (Route). Critique identified that step 1 (Continue prior work) intercepts the exact scenario first. Detection moved to step 1.

---

**File 3: `.claude/skills/implementation-cycle/SKILL.md` (On Entry section)**

```markdown
# [file:implementation-cycle/SKILL.md, lines 61-70]

**On Entry (any phase):**
```
mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="{PHASE}", work_id="{work_id}")
```

**On Complete:**
```
mcp__haios-operations__cycle_clear()
```
```

**Behavior:** The slim router documents that any phase can be entered. However, direct DO-phase entry after survey-cycle detection is not documented, leaving agents uncertain about the correct protocol for build-session startup.

**Problem:** Without explicit documentation of the direct-DO-entry pattern, agents in build-sessions may default to re-running PLAN phase from scratch.

---

### Desired State

**File 1: `.claude/skills/implementation-cycle/phases/PLAN.md` — Add Session Yield after standard+ gates**

After all tier-appropriate gates pass, standard and architectural tiers yield the session instead of proceeding to DO. The agent checkpoints and ends the plan-session. The build-session will enter DO directly.

Target addition (appended after Gate 3 for standard, after Gate 4 for architectural):

```markdown
**Session Yield (standard/architectural — MUST after all gates pass):**

After all gates pass, standard+ items MUST yield the session rather than proceeding to DO inline.
This gives the DO phase a clean context window (mem:89943, mem:89951).

**Actions:**
1. Update plan status to `approved` (if not already set by plan-authoring-agent)
2. Update work item `cycle_phase` to `PLAN` (indicates plan-session complete, build-session pending):
   ```
   mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="PLAN", work_id="{work_id}")
   ```
3. Invoke checkpoint-cycle. During the FILL phase, **MUST** set `pending: ["{work_id}"]`.
   This is the handoff signal — if `pending` is empty, the build-session will not detect the approved plan.
   ```
   Skill(skill="checkpoint-cycle")
   ```
4. End the plan-session. **Do NOT proceed to DO phase.** Checkpoint-cycle's CAPTURE phase
   invokes `session_end()`, which mechanically prevents continuation to DO phase.

> **Rationale (WORK-287):** PLAN phase consumes ~70% of context budget (mem:87482). Proceeding inline
> leaves insufficient context for DO phase. Session split gives each phase a full context window.
> Build-session starts clean: coldstart → survey detects approved plan → DO phase (no PLAN re-run).

> **Regression guard:** trivial and small tiers are NOT affected. They continue single-session behavior
> (PLAN → DO inline). Only standard and architectural yield after plan approval.
```

---

**File 2: `.claude/skills/survey-cycle/SKILL.md` — Add approved-plan detection in Route**

Extended routing logic detects when the pending work item has an approved plan and routes to DO phase directly.

Target routing section (replacing current Route section):

```markdown
3. **Route**
   - Read work item WORK.md to get `type` field
   - Use routing decision table (WORK-030: type field is authoritative):
     - `type: investigation` → `investigation-cycle`
     - Has plan AND plan `status: approved` AND `cycle_phase: PLAN` → `implementation-cycle` **at DO phase** (skip PLAN — build-session)
     - Has plan (other states) → `implementation-cycle` (enter at PLAN phase — normal flow)
     - Otherwise → `work-creation-cycle`

**Build-Session Detection (approved-plan fast-path):**

When routing to implementation-cycle after detecting `status: approved` plan:
1. Read `docs/work/active/{id}/plans/PLAN.md` frontmatter → verify `status: approved`
2. Read `docs/work/active/{id}/WORK.md` frontmatter → verify `cycle_phase: PLAN`
   (Both conditions MUST be true to use fast-path. Either condition false → normal PLAN entry.)
3. Invoke implementation-cycle at DO phase:
   ```
   Skill(skill="implementation-cycle")
   # Then immediately:
   mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="DO", work_id="{work_id}")
   ```
4. Read the approved plan from disk before executing DO steps (MUST Gate from phases/PLAN.md).

> **Rationale:** Avoids re-running PLAN phase (wasted ~15% context per mem:89507) when plan was authored
> in a dedicated plan-session. The plan file on disk is the handoff artifact. No new infrastructure needed.
```

---

**File 3: `.claude/skills/implementation-cycle/SKILL.md` — Document direct DO-phase entry**

Add a "Direct Entry" section to the slim router that documents the build-session startup protocol.

Target addition (after "On Entry (any phase)" section):

```markdown
**Direct DO-Phase Entry (Build-Session — post plan-session handoff):**

When survey-cycle detects an approved plan and routes here, skip PLAN phase entirely:
1. `mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="DO", work_id="{work_id}")`
2. Read the approved plan: `docs/work/active/{work_id}/plans/PLAN.md`
3. Execute DO phase per `phases/DO.md`

> This is the build-session entry point for standard/architectural items that had their plan authored
> in a prior plan-session. The cycle diagram still holds — PLAN was completed in session N,
> DO begins in session N+1.
```

---

### Tests

Tests verify the skill file content structure matches the specification. These are markdown content tests (same pattern as existing tests in `test_implementation_cycle_fracture.py` and `test_survey_cycle.py`).

#### Test 1: PLAN phase documents session yield for standard tier
- **file:** `tests/test_tiered_session_boundary.py`
- **function:** `test_plan_phase_documents_session_yield_for_standard()`
- **setup:** Read `.claude/skills/implementation-cycle/phases/PLAN.md` as text
- **assertion:** Content contains "Session Yield" AND "standard" AND "checkpoint-cycle" AND "Do NOT proceed to DO phase"

#### Test 2: PLAN phase preserves single-session behavior for trivial/small
- **file:** `tests/test_tiered_session_boundary.py`
- **function:** `test_plan_phase_single_session_guard_present()`
- **setup:** Read `.claude/skills/implementation-cycle/phases/PLAN.md` as text
- **assertion:** Content contains "trivial and small tiers are NOT affected" OR ("trivial" in content AND "small" in content AND "single-session" in content)

#### Test 3: Survey-cycle documents approved-plan fast-path routing
- **file:** `tests/test_tiered_session_boundary.py`
- **function:** `test_survey_cycle_documents_approved_plan_fast_path()`
- **setup:** Read `.claude/skills/survey-cycle/SKILL.md` as text
- **assertion:** Content contains "status: approved" AND "cycle_phase: PLAN" AND "DO phase" AND "skip PLAN" AND "pending"

#### Test 4: Implementation-cycle slim router documents direct DO-phase entry
- **file:** `tests/test_tiered_session_boundary.py`
- **function:** `test_implementation_cycle_documents_direct_do_entry()`
- **setup:** Read `.claude/skills/implementation-cycle/SKILL.md` as text; verify line count <= 100 (existing constraint from test_implementation_cycle_fracture.py)
- **assertion:** Content contains "Direct DO-Phase Entry" AND "Build-Session" AND "skip PLAN phase"

#### Test 5: Existing tests still pass (regression guard)
- **file:** `tests/test_tiered_session_boundary.py`
- **function:** `test_plan_phase_still_references_authoring_agent()`
- **setup:** Read `.claude/skills/implementation-cycle/phases/PLAN.md` as text
- **assertion:** Content still contains "plan-authoring-agent" AND "Task(subagent_type='plan-authoring-agent'" (existing test_plan_authoring_agent.py assertions preserved)

---

### Design

#### File 1 (MODIFY): `.claude/skills/implementation-cycle/phases/PLAN.md`

**Location:** After Gate 3 block for standard tier (currently ends at "DO phase is blocked until all three gates pass."), and after Gate 4 block for architectural tier.

**Current Code (lines ~127-132, standard tier ending):**
```markdown
**Gate 3 - MUST: Preflight Check (as haiku subagent — S397 Operator Directive)**
```
Task(subagent_type='preflight-checker', model='haiku', prompt='Check plan readiness for {backlog_id}. Plan: docs/work/active/{backlog_id}/plans/PLAN.md. Work item: docs/work/active/{backlog_id}/WORK.md. Verify plan is complete and ready for DO phase.')
```
Validates plan completeness and file scope. DO phase is blocked until all three gates pass.

**If tier = architectural:**
```

**Target Code — insert Session Yield block between Gate 3 and "If tier = architectural":**
```markdown
**Gate 3 - MUST: Preflight Check (as haiku subagent — S397 Operator Directive)**
```
Task(subagent_type='preflight-checker', model='haiku', prompt='Check plan readiness for {backlog_id}. Plan: docs/work/active/{backlog_id}/plans/PLAN.md. Work item: docs/work/active/{backlog_id}/WORK.md. Verify plan is complete and ready for DO phase.')
```
Validates plan completeness and file scope. DO phase is blocked until all three gates pass.

**Session Yield (standard — MUST after all gates pass):**

After all three gates pass, standard items MUST yield the session rather than proceeding to DO inline.
This gives the DO phase a clean context window (mem:89943, mem:89951).

**Actions:**
1. Update plan status to `approved` (if not already set by plan-authoring-agent)
2. Update work item `cycle_phase` to record plan-session complete:
   ```
   mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="PLAN", work_id="{work_id}")
   ```
3. Invoke checkpoint-cycle. During the FILL phase, **MUST** set `pending: ["{work_id}"]`.
   This is the handoff signal for the build-session.
   ```
   Skill(skill="checkpoint-cycle")
   ```
4. End the plan-session. **Do NOT proceed to DO phase.** Checkpoint-cycle's CAPTURE phase
   invokes `session_end()`, which mechanically prevents continuation to DO phase.

> **Rationale (WORK-287):** PLAN phase consumes ~70% of context budget (mem:87482). Proceeding inline
> leaves insufficient context for DO phase. Session split gives each phase a full context window.
> Build-session starts clean: coldstart → survey detects approved plan → DO phase (no PLAN re-run).
>
> **Regression guard:** trivial and small tiers are NOT affected. They continue single-session behavior
> (PLAN → DO inline). Only standard and architectural yield after plan approval.

**If tier = architectural:**
```

**Current Code (lines ~133-143, architectural tier ending):**
```markdown
**If tier = architectural:**

Same as standard (Gates 1+2+3), PLUS:

**Gate 4 - MUST: Operator Approval**
After Gate 3 passes, invoke operator confirmation:
```
AskUserQuestion(questions=[{"question": "Architectural work item {backlog_id} has passed all 3 automated gates. Confirm approach and approve DO phase.", "header": "Operator Approval Required", "options": [{"label": "Approved — proceed to DO phase"}, {"label": "BLOCK — revise plan first"}], "multiSelect": false}])
```
> Architectural items require explicit operator sign-off before DO phase. Gate 4 makes this explicit (was implicit in critique_injector.py TIER_INJECTIONS).

**Tools:** Read, Glob, AskUserQuestion, Task(plan-authoring-agent, model=sonnet), Task(critique-agent, model=sonnet), Task(preflight-checker, model=haiku), Task(plan-validation, model=haiku)
```

**Target Code — append Session Yield for architectural after Gate 4, before Tools line:**
```markdown
**If tier = architectural:**

Same as standard (Gates 1+2+3), PLUS:

**Gate 4 - MUST: Operator Approval**
After Gate 3 passes, invoke operator confirmation:
```
AskUserQuestion(questions=[{"question": "Architectural work item {backlog_id} has passed all 3 automated gates. Confirm approach and approve DO phase.", "header": "Operator Approval Required", "options": [{"label": "Approved — proceed to DO phase"}, {"label": "BLOCK — revise plan first"}], "multiSelect": false}])
```
> Architectural items require explicit operator sign-off before DO phase. Gate 4 makes this explicit (was implicit in critique_injector.py TIER_INJECTIONS).

**Session Yield (architectural — MUST after Gate 4 approval):**

After operator approves, architectural items MUST yield the session (same as standard):
1. Update plan status to `approved`
2. `mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="PLAN", work_id="{work_id}")`
3. `Skill(skill="checkpoint-cycle")` — **MUST** set `pending: ["{work_id}"]` during FILL phase
4. End the plan-session. **Do NOT proceed to DO phase.** (session_end() enforces mechanically)

> **Regression guard:** trivial and small tiers are NOT affected. They continue single-session behavior.

**Tools:** Read, Glob, AskUserQuestion, Task(plan-authoring-agent, model=sonnet), Task(critique-agent, model=sonnet), Task(preflight-checker, model=haiku), Task(plan-validation, model=haiku)
```

---

#### File 2 (MODIFY): `.claude/skills/survey-cycle/SKILL.md`

**Location:** Route section (currently lines 33-37 of the skill body).

**Current Code:**
```markdown
3. **Route**
   - Read work item WORK.md to get `type` field
   - Use routing decision table (WORK-030: type field is authoritative):
     - `type: investigation` → `investigation-cycle`
     - Has plan → `implementation-cycle`
     - Otherwise → `work-creation-cycle`
```

**Target Code:**
```markdown
1. **Continue prior work?**
   - Check checkpoint `pending` field
   - If work in_progress from prior session:
     - **Build-Session Fast-Path:** If plan `status: approved` AND `cycle_phase: PLAN` AND
       work item is in checkpoint `pending` field → route to `implementation-cycle` at DO phase
       (skip PLAN — build-session). See Build-Session Detection below.
     - Otherwise → continue at current phase normally

2. **Otherwise, present options**
   - Run `mcp__haios-operations__queue_list(queue_name="{queue_name}")` for ordered items (default: "default")
   - Alternatively: `mcp__haios-operations__queue_ready()` for flat unordered list (backward compat)
   - Select top 3 from queue head
   - Present via `AskUserQuestion` (or auto-select if autonomous)

**After queue selection:**
```bash
just set-queue {queue_name}
```

3. **Route**
   - Read work item WORK.md to get `type` field
   - Use routing decision table (WORK-030: type field is authoritative):
     - `type: investigation` → `investigation-cycle`
     - Has plan (file exists at `docs/work/active/{id}/plans/PLAN.md`) → `implementation-cycle`
     - Otherwise → `work-creation-cycle`

**Build-Session Detection (approved-plan fast-path — invoked from step 1):**

When the checkpoint `pending` field contains a work item ID, check for the approved-plan state:
1. Read `docs/work/active/{id}/plans/PLAN.md` frontmatter — check `status: approved`
2. Read `docs/work/active/{id}/WORK.md` frontmatter — check `cycle_phase: PLAN`
3. Confirm work item is in checkpoint `pending` field (third condition — prevents false-positive
   on stale approved plans re-entering PLAN phase, since `pending` is only set by plan-session yield)
4. If ALL THREE conditions true: route to implementation-cycle and set phase to DO:
   ```
   mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="DO", work_id="{work_id}")
   ```
5. Read the approved plan from disk before executing DO steps.
   (If any condition is false, enter PLAN phase normally — fail-safe.)

> **Rationale (WORK-289):** Avoids re-running PLAN phase (~15% context wasted per mem:89507) when plan
> was authored in a dedicated plan-session. Three-condition check (plan status + cycle_phase + pending)
> prevents false-positive fast-path. Pending field is only set by plan-session yield, not PLAN entry.
> Note: "Has plan" = file exists at `docs/work/active/{id}/plans/PLAN.md`.
```

---

#### File 3 (MODIFY): `.claude/skills/implementation-cycle/SKILL.md`

**Constraint:** Must remain <= 100 lines (test_implementation_cycle_fracture.py:TestSlimRouter::test_slim_router_line_count). Current file is 70 lines. Addition must be concise.

**Location:** After "On Entry (any phase)" block (currently lines 61-65).

**Current Code:**
```markdown
**On Entry (any phase):**
```
mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="{PHASE}", work_id="{work_id}")
```

**On Complete:**
```
mcp__haios-operations__cycle_clear()
```
```

**Target Code:**
```markdown
**On Entry (any phase):**
```
mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="{PHASE}", work_id="{work_id}")
```

**Direct DO-Phase Entry (Build-Session):**

When survey-cycle routes here after detecting an approved plan (plan `status: approved` + `cycle_phase: PLAN`):
1. `mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="DO", work_id="{work_id}")`
2. Read `docs/work/active/{work_id}/plans/PLAN.md` (the handoff artifact from plan-session)
3. Execute DO phase per `phases/DO.md` — skip PLAN phase

> PLAN was completed in session N. DO begins in session N+1 with clean context.
> See `phases/PLAN.md` Exit Gate and `survey-cycle/SKILL.md` Route for the full protocol.

**On Complete:**
```
mcp__haios-operations__cycle_clear()
```
```

**Line count estimate:** Current 70 lines + ~12 lines added = ~82 lines. Satisfies <= 100 constraint.

---

### Call Chain

```
Session N (plan-session):
  implementation-cycle PLAN phase
      |
      +-> plan-authoring-agent (subagent)
      |       Returns: COMPLETE, plan status=approved
      |
      +-> critique-agent (standard+ Gate 1)
      +-> preflight-checker haiku (standard+ Gate 2+3)
      +-> AskUserQuestion (architectural Gate 4)
      |
      +-> Session Yield (NEW — standard/architectural only)
              |
              +-> cycle_set(phase="PLAN")   # marks plan-session complete
              +-> checkpoint-cycle           # pending={work_id}
              +-> END session N

Session N+1 (build-session):
  coldstart
      |
      +-> survey-cycle
              |
              +-> detect checkpoint pending={work_id}
              +-> read PLAN.md → status=approved
              +-> read WORK.md → cycle_phase=PLAN
              +-> Build-Session Fast-Path (NEW)
                      |
                      +-> cycle_set(phase="DO")
                      +-> read PLAN.md from disk
                      +-> implementation-cycle DO phase
```

---

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Three-condition approval check | plan `status: approved` AND `cycle_phase: PLAN` AND checkpoint `pending` contains work_id | Single or two conditions create false positives. A work item may have an old approved plan from a previous completion cycle. The `pending` field is only set by plan-session yield, not by PLAN entry — it uniquely identifies the handoff state. |
| Yield in PLAN phase (not survey-cycle) | Session yield logic lives in phases/PLAN.md | PLAN phase owns the gates; yield is the natural exit of a successful gate sequence. Survey-cycle only detects and routes. Separation of concerns. |
| cycle_phase remains "PLAN" after yield | Set to PLAN, not a new "PLAN-COMPLETE" value | Avoids new state values. PLAN + approved-plan + pending field is a sufficient three-condition signal. Adding new cycle_phase values would require schema changes and hook updates. |
| No new infrastructure | Reuse plan file + checkpoint pending + cycle_phase | WORK-287 H1: "Handoff is NOT a new artifact." Existing mechanisms are sufficient. Minimal blast radius. |
| Regression guard in skills text | Explicit "trivial and small tiers are NOT affected" statement | Self-documenting regression guard. Agents reading the skill see the exclusion explicitly — no inference required. |
| SKILL.md line count constraint | Addition capped at ~12 lines | test_implementation_cycle_fracture.py enforces <= 100 lines on SKILL.md. Current 70 + 12 = 82 stays within budget. |

---

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| Plan has `status: approved` but `cycle_phase` is not `PLAN` | Fall through to normal PLAN entry (fail-safe) | Test 3 (implicit — three-condition required) |
| Plan has `status: draft` (normal mid-PLAN-phase case) | No fast-path. Normal PLAN entry. | Test 3 |
| trivial/small item with approved plan | No yield — exits PLAN phase, proceeds to DO inline as before | Test 2 |
| Plan-session interrupted before checkpoint | cycle_phase stays at PLAN but no checkpoint pending field | Survey-cycle continues with pending work item; cycle_set finds cycle_phase=PLAN, enters PLAN phase to re-verify plan | Test 3 (implicit) |
| Architectural item — operator rejects at Gate 4 | Yield not triggered. Work item stays in PLAN phase. Re-run critique-revise loop. | Not tested (operator interaction) |

---

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| SKILL.md line count exceeded | H | Measured: current 70 lines + estimated 12 = 82 <= 100. Test will catch if exceeded. |
| Survey-cycle test fails (checks for GATHER/ASSESS phases not present) | L | Test already passes on current SKILL.md which lacks those phases. Changes don't remove existing content. |
| Implementation-cycle fracture tests fail (cross-phase reference check) | M | Addition to SKILL.md references `phases/PLAN.md` and `survey-cycle/SKILL.md` via `See` — not "see PLAN phase" literal. Must verify exact wording avoids the banned patterns in TestSelfContainment. |
| Agent interprets yield as optional | M | Text uses MUST explicitly. "Do NOT proceed to DO phase" is a hard stop, not a suggestion. |
| Handoff state corruption (cycle_phase not set before session end) | M | cycle_set is step 2, checkpoint-cycle is step 3. If session dies between steps 2 and 3, cycle_phase=PLAN is set but no checkpoint pending. Survey-cycle fallback (fail-safe) re-enters PLAN phase. Plan is already approved — PLAN phase reads it, skips authoring, runs gates, yields again. Convergent. |

---

## Layer 2: Implementation Steps

### Step 0: Establish Baseline (Critique A5)
- **spec_ref:** Layer 0 > Consumer Files (VERIFY rows)
- **input:** Plan approved, before any implementation changes
- **action:** Run existing consumer tests to establish baseline. Document any pre-existing failures so they are not attributed to this implementation.
- **output:** Baseline test results recorded
- **verify:** `pytest tests/test_implementation_cycle_fracture.py tests/test_survey_cycle.py tests/test_plan_authoring_agent.py -v` — record pass/fail counts

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Step 0 baseline recorded, Layer 1 test specs defined
- **action:** Create `tests/test_tiered_session_boundary.py` with all 5 test functions from Layer 1 Tests section. Tests reference skill file content that doesn't exist yet — they MUST fail.
- **output:** Test file exists, all 5 tests fail (content not yet in skill files)
- **verify:** `pytest tests/test_tiered_session_boundary.py -v 2>&1 | grep -c "FAILED\|ERROR"` equals 4 (Test 5 may pass since existing content is preserved)

### Step 2: Modify phases/PLAN.md — Add Session Yield (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Insert Session Yield block after Gate 3 (standard) and after Gate 4 (architectural) per Layer 1 Design > File 1 exact target code
- **output:** phases/PLAN.md contains session yield text for standard and architectural tiers
- **verify:** `pytest tests/test_tiered_session_boundary.py::test_plan_phase_documents_session_yield_for_standard tests/test_tiered_session_boundary.py::test_plan_phase_single_session_guard_present tests/test_tiered_session_boundary.py::test_plan_phase_still_references_authoring_agent -v` all pass

### Step 3: Modify survey-cycle/SKILL.md — Add Fast-Path in Step 1 + Route
- **spec_ref:** Layer 1 > Design > File 2 (MODIFY)
- **input:** Step 2 complete
- **action:** Replace Continue-prior-work (step 1) and Route (step 3) sections with extended logic + Build-Session Fast-Path block per Layer 1 Design > File 2 exact target code. Fast-path detection lives in step 1 (not step 3) per critique A1.
- **output:** survey-cycle/SKILL.md contains approved-plan detection with three-condition fast-path in step 1
- **verify:** `pytest tests/test_tiered_session_boundary.py::test_survey_cycle_documents_approved_plan_fast_path -v` passes

### Step 4: Modify implementation-cycle/SKILL.md — Document Direct DO Entry
- **spec_ref:** Layer 1 > Design > File 3 (MODIFY)
- **input:** Step 3 complete
- **action:** Insert Direct DO-Phase Entry block after "On Entry (any phase)" section per Layer 1 Design > File 3 target code. Verify line count constraint.
- **output:** SKILL.md contains build-session entry protocol; line count <= 100
- **verify:** `pytest tests/test_tiered_session_boundary.py::test_implementation_cycle_documents_direct_do_entry -v` passes; `wc -l .claude/skills/implementation-cycle/SKILL.md` output <= 100

### Step 5: Full Suite Regression Check
- **spec_ref:** Layer 0 > Consumer Files (VERIFY rows)
- **input:** Steps 2-4 complete
- **action:** Run full test suite to verify no regressions in existing skill tests
- **output:** All 5 new tests pass, existing tests unchanged
- **verify:** `pytest tests/test_tiered_session_boundary.py tests/test_implementation_cycle_fracture.py tests/test_survey_cycle.py tests/test_plan_authoring_agent.py -v` all pass; `pytest tests/ -v 2>&1 | tail -5` shows 0 new failures vs baseline

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_tiered_session_boundary.py -v` | 5 passed, 0 failed |
| `pytest tests/test_implementation_cycle_fracture.py -v` | All existing tests pass (0 new failures) |
| `pytest tests/test_survey_cycle.py -v` | All existing tests pass (0 new failures) |
| `pytest tests/test_plan_authoring_agent.py -v` | All existing tests pass (0 new failures) |
| `pytest tests/ -v 2>&1 | grep -E "^(FAILED|ERROR)"` | 0 new failures (only pre-existing failures if any) |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| PLAN phase has session yield for standard tier | `grep "Session Yield" .claude/skills/implementation-cycle/phases/PLAN.md` | 2+ matches (standard + architectural) |
| PLAN phase has regression guard for trivial/small | `grep "trivial and small" .claude/skills/implementation-cycle/phases/PLAN.md` | 1+ match |
| Survey-cycle has approved-plan fast-path | `grep "status: approved" .claude/skills/survey-cycle/SKILL.md` | 1+ match |
| Survey-cycle has three-condition check (status:approved + cycle_phase:PLAN + pending) | `grep "cycle_phase: PLAN" .claude/skills/survey-cycle/SKILL.md` | 1+ match |
| SKILL.md documents direct DO entry | `grep "Direct DO-Phase Entry" .claude/skills/implementation-cycle/SKILL.md` | 1 match |
| SKILL.md line count within budget | `wc -l .claude/skills/implementation-cycle/SKILL.md` | <= 100 |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| plan-authoring-agent reference preserved | `grep "plan-authoring-agent" .claude/skills/implementation-cycle/phases/PLAN.md` | 1+ match |
| Task invocation pattern preserved | `grep "Task(subagent_type='plan-authoring-agent'" .claude/skills/implementation-cycle/phases/PLAN.md` | 1 match |
| Cross-phase reference ban respected | `grep -i "see PLAN phase\|see DO phase\|see CHECK phase" .claude/skills/implementation-cycle/phases/PLAN.md` | 0 matches |

### Completion Criteria (DoD)

- [ ] All 5 new tests pass (Layer 2 Step 5 verify)
- [ ] All WORK.md acceptance criteria verified (table above)
- [ ] No regressions in existing skill content tests (Consumer Integrity table above)
- [ ] SKILL.md line count constraint satisfied (<= 100)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves skill file content is correct. "Consumer integrity checks" prove existing references are preserved. (E2-250)

---

## References

- `docs/work/active/WORK-287/FINDINGS.md` — Source investigation, tiered architecture design
- `docs/work/active/WORK-289/WORK.md` — Acceptance criteria
- `.claude/skills/implementation-cycle/phases/PLAN.md` — Primary modification target
- `.claude/skills/survey-cycle/SKILL.md` — Primary modification target
- `.claude/skills/implementation-cycle/SKILL.md` — Primary modification target (line count constraint)
- `.claude/skills/checkpoint-cycle/SKILL.md` — Referenced for checkpoint integration protocol
- Memory: mem:89943, mem:89951 (decouple plan/build), mem:89507 (plan round-trip 30%), mem:87482 (PLAN phase 70% cost), mem:85390 (104% ceremony budget), mem:88086 (plan-authoring-agent patterns)
- `tests/test_implementation_cycle_fracture.py` — Constraint source (SKILL.md <= 100 lines, self-containment rules)
- REQ-LIFECYCLE-001, REQ-LIFECYCLE-005 (traces_to from WORK.md)
