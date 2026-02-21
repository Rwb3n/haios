---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-21
backlog_id: WORK-176
title: "Plan-Authoring-Cycle Subagent Delegation"
author: Hephaestus
lifecycle_phase: plan
session: 415
generated: 2026-02-21
last_updated: 2026-02-21T14:30:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-176/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete code blocks, not pseudocode"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: Plan-Authoring-Cycle Subagent Delegation

---

## Goal

The implementation-cycle PLAN phase will delegate plan authoring to a sonnet subagent via `Task(subagent_type='plan-authoring-agent')`, freeing the main context for DO/CHECK/DONE phases while maintaining plan quality and gate compliance.

---

## Open Decisions

<!-- No operator_decisions in WORK-176 frontmatter. No blocked decisions. -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| N/A | N/A | N/A | No operator decisions in work item |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/agents/plan-authoring-agent.md` | CREATE | 2 |
| `.claude/skills/implementation-cycle/SKILL.md` | MODIFY | 2 |

### Consumer Files

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `.claude/agents/README.md` | references agent table | 22-35 | UPDATE |
| `.claude/commands/new-plan.md` | chains to plan-authoring-cycle inline | ~end | UPDATE |
| `tests/test_agent_capability_cards.py` | hardcoded agent count assertion | 72 | UPDATE |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_plan_authoring_agent.py` | CREATE | New test file for agent card validation |
| `tests/test_agent_capability_cards.py` | UPDATE | Update agent count from 11 to 12 |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 2 | plan-authoring-agent.md + test file |
| Files to modify | 4 | implementation-cycle SKILL.md + README.md + new-plan.md + test_agent_capability_cards.py |
| Tests to write | 4 | Test Files table |
| Total blast radius | 6 | Sum of all unique files |

---

## Layer 1: Specification

### Current State

```markdown
# .claude/skills/implementation-cycle/SKILL.md:62-67
# PLAN Phase Actions:
1. Read the plan file: `docs/work/active/{backlog_id}/plans/PLAN.md`
2. Verify plan has filled-in sections (not template placeholders)
3. Check `status: draft` -> if so, fill in design first
4. **MUST:** Read referenced specifications (see MUST Gate below)
5. Optional: Run preflight checker (E2-093 when available)
```

**Behavior:** When a plan has `status: draft` or needs population, the main agent must either manually fill in sections or invoke `Skill(skill="plan-authoring-cycle")` inline, consuming main context tokens for mechanical template-filling work.

**Problem:** Plan authoring is structural work (read specs, fill sections, validate completeness) that consumes ~40% of main context tokens (mem:86709). This leaves less context for the implementation DO phase where judgment is actually needed.

### Desired State

```markdown
# .claude/skills/implementation-cycle/SKILL.md:62-67 (updated)
# PLAN Phase Actions:
1. Read the plan file: `docs/work/active/{backlog_id}/plans/PLAN.md`
2. Verify plan has filled-in sections (not template placeholders)
3. Check `status: draft` -> if so, delegate to plan-authoring subagent:
   ```
   Task(subagent_type='plan-authoring-agent', model='sonnet',
        prompt='Author plan for {backlog_id}. Work: docs/work/active/{backlog_id}/WORK.md. Plan: docs/work/active/{backlog_id}/plans/PLAN.md. Follow plan-authoring-cycle skill phases: AMBIGUITY->ANALYZE->AUTHOR->VALIDATE. Return completed plan with status: approved.')
   ```
   After subagent returns:
   - If `COMPLETE`: verify plan status is `approved`, continue to step 4.
   - If `BLOCKED` (unresolved operator_decisions): read WORK.md `operator_decisions`, invoke `AskUserQuestion` with options, update WORK.md `resolved: true, chosen: <value>`, then re-invoke subagent.
   - If `BLOCKED` (missing source spec): read subagent Issues output for missing path, surface to operator via `AskUserQuestion`, block DO phase until resolved (spawn investigation or provide spec).
4. **MUST:** Read returned plan and verify referenced specifications (see MUST Gate below)
5. Optional: Run preflight checker (E2-093 when available)
```

> **Tools for PLAN phase (updated):** Read, Glob, AskUserQuestion, Task(plan-authoring-agent, model=sonnet), Task(critique-agent, model=sonnet), Task(preflight-checker, model=haiku), Task(plan-validation, model=haiku)

**Behavior:** Plan authoring runs in an isolated sonnet subagent context. The subagent reads the skill definition, work item, and source files, then populates the plan following the AMBIGUITY->ANALYZE->AUTHOR->VALIDATE phases. If the subagent encounters unresolved operator decisions or missing specs, it returns BLOCKED and the main context handles the resolution before re-invoking. Main context receives the completed plan and proceeds to exit gates (critique, validation, preflight).

**Result:** Main context tokens freed for DO phase. Plan quality maintained because the subagent follows the same skill definition. Exit gates (Gate 1/2/3) remain in main context as caller-owned verification.

### Tests

#### Test 1: Agent Card Has Required Frontmatter Fields
- **file:** `tests/test_plan_authoring_agent.py`
- **function:** `test_agent_card_has_required_frontmatter()`
- **setup:** Read `.claude/agents/plan-authoring-agent.md`, parse YAML frontmatter
- **assertion:** All required fields present: name, description, tools, model, context, requirement_level, category, trigger_conditions, input_contract, output_contract, invoked_by, related_agents

#### Test 2: Agent Card References Correct Skill
- **file:** `tests/test_plan_authoring_agent.py`
- **function:** `test_agent_card_references_plan_authoring_skill()`
- **setup:** Read `.claude/agents/plan-authoring-agent.md` body content
- **assertion:** Body references `.claude/skills/plan-authoring-cycle/SKILL.md` as source of truth for phase structure

#### Test 3: Implementation Cycle References Subagent Pattern
- **file:** `tests/test_plan_authoring_agent.py`
- **function:** `test_implementation_cycle_delegates_to_subagent()`
- **setup:** Read `.claude/skills/implementation-cycle/SKILL.md`
- **assertion:** PLAN phase contains `Task(subagent_type='plan-authoring-agent'` invocation pattern

#### Test 4: Agent Listed in README
- **file:** `tests/test_plan_authoring_agent.py`
- **function:** `test_agent_listed_in_readme()`
- **setup:** Read `.claude/agents/README.md`
- **assertion:** `plan-authoring-agent` appears in agent table

### Design

#### File 1 (NEW): `.claude/agents/plan-authoring-agent.md`

```markdown
---
name: plan-authoring-agent
description: Execute plan-authoring-cycle in isolated context. Reads work item, source
  specs, and populates plan following AMBIGUITY->ANALYZE->AUTHOR->VALIDATE phases.
  Returns completed plan with status approved.
tools: Read, Glob, Grep, Edit, Write
model: sonnet
context: fork
requirement_level: optional
category: cycle-delegation
trigger_conditions:
  - implementation-cycle PLAN phase detects plan with status draft
  - Plan needs population and main context should be preserved for DO phase
input_contract: "work_id, plan_path, work_path"
output_contract: "Completed plan file with status: approved. Report sections populated, specs verified, no placeholders remaining."
invoked_by:
  - implementation-cycle (PLAN phase, when plan status is draft)
related_agents:
  - critique-agent (runs AFTER this agent returns, on the completed plan)
  - preflight-checker (runs AFTER critique, validates plan readiness)
  - implementation-cycle-agent (full cycle delegation alternative)
generated: '2026-02-21'
last_updated: '2026-02-21T14:30:00'
---
# Plan Authoring Agent

Executes the plan-authoring-cycle in isolated context, returning a populated plan to the main agent.

## Requirement Level

**OPTIONAL** - Alternative to inline plan authoring for context reduction.

## When to Use

Parent agent invokes this when:
- Plan file exists with `status: draft` (template placeholders)
- Main context should be preserved for implementation (DO phase)
- Work item has source files and specs to read

## Process

1. **Read** the skill definition: `.claude/skills/plan-authoring-cycle/SKILL.md`
2. **Read** the work item at the provided work_path
3. **Execute** plan-authoring-cycle phases:
   - AMBIGUITY: Check operator_decisions, resolve if needed
   - ANALYZE: Read plan, identify placeholder sections
   - AUTHOR: Read source specs, query memory, populate all sections
   - VALIDATE: Verify no placeholders remain, set status to approved
4. **Return** summary of populated sections and any issues

## Guardrails

- **MUST** read the plan-authoring-cycle SKILL.md first — it is the source of truth
- **MUST** read all source specifications referenced in the work item
- **MUST** query memory for prior patterns before designing
- **MUST NOT** invoke AskUserQuestion — this agent returns BLOCKED on unresolved operator decisions. Operator interaction is the caller's responsibility (implementation-cycle handles interactive resolution).
- **MUST NOT** invoke critique-agent or plan-validation-cycle — those are caller-owned gates
- **MUST NOT** invoke checkpoint-cycle — that is parent responsibility

## Output Format

Return this structure to parent:

\```
Plan Authoring Result: COMPLETE | BLOCKED

## Summary
- Work ID: {work_id}
- Sections populated: {list}
- Specs read: {list}
- Memory queried: yes/no

## Plan Status
- Status: approved | draft (if blocked)
- Placeholders remaining: {count}

## Issues (if BLOCKED)
- {List specific blockers — unresolved decisions, missing specs, etc.}
\```

## Edge Cases

| Case | Handling |
|------|----------|
| operator_decisions unresolved | Return BLOCKED — cannot resolve without operator |
| Source spec not found | Return BLOCKED with missing path |
| Memory query returns nothing | Continue — document "no prior patterns found" |

## Related

- **plan-authoring-cycle skill**: Source of truth for phase structure
- **critique-agent**: Runs AFTER this agent (caller-owned Gate 1)
- **preflight-checker**: Runs AFTER critique (caller-owned Gate 3)
- **implementation-cycle skill**: Invokes this agent during PLAN phase
```

#### File 2 (MODIFY): `.claude/skills/implementation-cycle/SKILL.md`

**Location:** Lines 62-67 in PLAN Phase Actions section

**Current Code:**
```markdown
**Actions:**
1. Read the plan file: `docs/work/active/{backlog_id}/plans/PLAN.md` (or legacy `docs/plans/PLAN-{backlog_id}-*.md`)
2. Verify plan has filled-in sections (not template placeholders)
3. Check `status: draft` -> if so, fill in design first
4. **MUST:** Read referenced specifications (see MUST Gate below)
5. Optional: Run preflight checker (E2-093 when available)
```

**Target Code:**
```markdown
**Actions:**
1. Read the plan file: `docs/work/active/{backlog_id}/plans/PLAN.md` (or legacy `docs/plans/PLAN-{backlog_id}-*.md`)
2. Verify plan has filled-in sections (not template placeholders)
3. Check `status: draft` -> if so, delegate to plan-authoring subagent:
   ```
   Task(subagent_type='plan-authoring-agent', model='sonnet',
        prompt='Author plan for {backlog_id}. Work: docs/work/active/{backlog_id}/WORK.md. Plan: docs/work/active/{backlog_id}/plans/PLAN.md. Follow plan-authoring-cycle skill phases: AMBIGUITY->ANALYZE->AUTHOR->VALIDATE. Return completed plan with status: approved.')
   ```
   After subagent returns:
   - If `COMPLETE`: verify plan status is `approved`, continue to step 4.
   - If `BLOCKED` (unresolved operator_decisions): read WORK.md `operator_decisions`, invoke `AskUserQuestion` with options, update WORK.md `resolved: true, chosen: <value>`, then re-invoke subagent.
   - If `BLOCKED` (missing source spec): read subagent Issues output for missing path, surface to operator via `AskUserQuestion`, block DO phase until resolved.
4. **MUST:** Read the plan (whether authored by subagent or pre-existing) and verify referenced specifications match (see MUST Gate below)
5. Optional: Run preflight checker (E2-093 when available)
```

**Diff:**
```diff
 **Actions:**
 1. Read the plan file: `docs/work/active/{backlog_id}/plans/PLAN.md` (or legacy `docs/plans/PLAN-{backlog_id}-*.md`)
 2. Verify plan has filled-in sections (not template placeholders)
-3. Check `status: draft` -> if so, fill in design first
-4. **MUST:** Read referenced specifications (see MUST Gate below)
+3. Check `status: draft` -> if so, delegate to plan-authoring subagent:
+   ```
+   Task(subagent_type='plan-authoring-agent', model='sonnet',
+        prompt='Author plan for {backlog_id}. Work: docs/work/active/{backlog_id}/WORK.md. Plan: docs/work/active/{backlog_id}/plans/PLAN.md. Follow plan-authoring-cycle skill phases: AMBIGUITY->ANALYZE->AUTHOR->VALIDATE. Return completed plan with status: approved.')
+   ```
+   After subagent returns:
+   - If `COMPLETE`: verify plan status is `approved`, continue to step 4.
+   - If `BLOCKED` (unresolved operator_decisions): read WORK.md `operator_decisions`, invoke `AskUserQuestion` with options, update WORK.md `resolved: true, chosen: <value>`, then re-invoke subagent.
+   - If `BLOCKED` (missing source spec): read subagent Issues output for missing path, surface to operator via `AskUserQuestion`, block DO phase until resolved.
+4. **MUST:** Read the plan (whether authored by subagent or pre-existing) and verify referenced specifications match (see MUST Gate below)
 5. Optional: Run preflight checker (E2-093 when available)
```

**Additional SKILL.md change — Composition Map (A3 critique finding):**

The Composition Map table (line ~337) PLAN row must also be updated:

**Current:**
```markdown
| PLAN  | Read, Glob   | preflight-checker | /new-plan |
```

**Target:**
```markdown
| PLAN  | Read, Glob   | plan-authoring-agent*, preflight-checker | /new-plan |
```
> *plan-authoring-agent: mandatory when plan `status: draft`; skipped when plan is already populated.

#### File 3 (MODIFY): `.claude/agents/README.md`

**Location:** Agent table (line 22-35)

**Target:** Add row:
```markdown
| **plan-authoring-agent** | optional | cycle-delegation | Execute plan-authoring-cycle in isolated context |
```

Update count from 11 to 12 in heading.

#### File 4 (MODIFY): `.claude/haios/config/haios.yaml`

**SKIPPED:** haios.yaml agent configs are optional (only critique-agent has one). Plan-authoring-agent needs no special config beyond the agent card.

#### File 5 (MODIFY): `.claude/commands/new-plan.md`

**Location:** Chain to Plan Authoring Cycle section (end of file)

**Target:** Add note that plan-authoring may also be invoked as subagent by implementation-cycle:
```markdown
> **Note:** When invoked from implementation-cycle PLAN phase, plan authoring is delegated to `plan-authoring-agent` subagent instead of inline skill invocation. The `/new-plan` command continues to use inline skill for interactive use.
```

### Call Chain

```
operator invokes /implement WORK-176
    |
    +-> implementation-cycle PLAN phase
    |       |
    |       +-> Entry Gate: critique-agent (work item)
    |       |
    |       +-> Read plan -> status: draft?
    |       |       |
    |       |       YES -> Task(subagent_type='plan-authoring-agent')  # <-- NEW
    |       |       |          Reads skill, work item, specs
    |       |       |          Populates plan sections
    |       |       |          Returns completed plan
    |       |       |
    |       |       NO -> plan already populated, continue
    |       |
    |       +-> MUST: Read plan, verify specs
    |       |
    |       +-> Exit Gate 1: critique-agent (plan)      # caller-owned
    |       +-> Exit Gate 2: plan-validation (haiku)     # caller-owned
    |       +-> Exit Gate 3: preflight-checker (haiku)   # caller-owned
    |
    +-> DO phase (main context preserved)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| New agent card vs. reuse implementation-cycle-agent | New dedicated agent | plan-authoring is a focused sub-cycle (AMBIGUITY->AUTHOR->VALIDATE), not a full implementation cycle. Dedicated agent has tighter tool set (no Bash, no Task) and clearer contract. |
| Subagent model | sonnet | Plan authoring is structural (read specs, fill sections). Does not require opus judgment. Consistent with implementation-cycle-agent pattern (mem:84125). |
| Gates remain caller-owned | Yes — critique, validation, preflight stay in main context | Memory 86986 STOP directive: "don't delegate multi-step implementation to subagents without explicit step verification." Gates are verification steps that MUST remain with the caller. Subagent only does AMBIGUITY->AUTHOR->VALIDATE. |
| `/new-plan` still uses inline skill | Yes — interactive use remains inline | `/new-plan` is operator-initiated and benefits from inline interaction (AskUserQuestion for operator_decisions). Only implementation-cycle automated invocation delegates. |
| No Bash tool for subagent | Excluded from tools list | Plan authoring reads files and writes markdown. No shell commands needed. Tighter tool set = safer isolation. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| Subagent returns BLOCKED (unresolved decisions) | Main context surfaces to operator via AskUserQuestion | N/A (skill behavior, not testable via file content) |
| Subagent returns plan with placeholders | Main context detects via spec verification MUST gate, blocks | N/A (runtime behavior) |
| Plan already has status: approved | Skip subagent invocation entirely | Test 3 (pattern exists in SKILL.md) |
| Subagent context exhausts | Returns partial result, main context re-invokes or falls back to inline | N/A (runtime) |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Subagent produces lower-quality plans than inline | Med | Same skill definition as source of truth. Critique agent (Gate 1) catches quality issues after subagent returns. |
| operator_decisions cannot be resolved by subagent | Low | Subagent returns BLOCKED, main context handles interaction. This is documented in agent edge cases. |
| Token savings less than ~40% | Low | Acceptance criterion uses "~" qualifier. Any delegation saves tokens. Measurement deliverable tracks actual. |
| Stale plan-authoring-cycle SKILL.md changes not picked up | Low | Subagent reads SKILL.md at invocation time (fresh context). No caching issue. |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Create `tests/test_plan_authoring_agent.py` with 4 tests from Layer 1
- **output:** Test file exists, all 4 tests fail (files don't exist yet)
- **verify:** `pytest tests/test_plan_authoring_agent.py -v 2>&1 | grep -c "FAILED\|ERROR"` equals 4

### Step 2: Create Agent Card (GREEN)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Create `.claude/agents/plan-authoring-agent.md` from Layer 1 Design (File 1)
- **output:** Tests 1, 2 pass (agent card frontmatter + skill reference)
- **verify:** `pytest tests/test_plan_authoring_agent.py::test_agent_card_has_required_frontmatter tests/test_plan_authoring_agent.py::test_agent_card_references_plan_authoring_skill -v` exits 0

### Step 2.5: Update Agent Count Test (A1 fix)
- **input:** Step 2 complete (new agent card created)
- **action:** Edit `tests/test_agent_capability_cards.py`: line 71 change `assert len(agent_files) == 11` to `assert len(agent_files) == 12`, line 72 change `"Expected 11 agents` to `"Expected 12 agents`
- **output:** test_agent_count no longer regresses
- **verify:** `pytest tests/test_agent_capability_cards.py::test_agent_count -v` exits 0

### Step 3: Update Implementation Cycle SKILL.md (GREEN)
- **input:** Step 2.5 complete
- **action:** Edit `.claude/skills/implementation-cycle/SKILL.md` PLAN phase Actions per Layer 1 diff. Also update Composition Map PLAN row: Optional Subagent cell from `preflight-checker` to `plan-authoring-agent, preflight-checker` (A3 fix).
- **output:** Test 3 passes (subagent invocation pattern in SKILL.md)
- **verify:** `pytest tests/test_plan_authoring_agent.py::test_implementation_cycle_delegates_to_subagent -v` exits 0

### Step 4: Update Agent README (GREEN)
- **input:** Step 3 complete
- **action:** Add plan-authoring-agent row to `.claude/agents/README.md` table, update count
- **output:** Test 4 passes (agent in README)
- **verify:** `pytest tests/test_plan_authoring_agent.py::test_agent_listed_in_readme -v` exits 0, all 4 passed

### Step 5: Update new-plan Command
- **input:** Step 4 complete
- **action:** Add note to `.claude/commands/new-plan.md` about subagent delegation from implementation-cycle
- **output:** Command file updated with delegation note
- **verify:** `grep "plan-authoring-agent" .claude/commands/new-plan.md` returns 1+ match

### Step 6: Full Test Suite Regression Check
- **input:** Step 5 complete
- **action:** Run full test suite
- **output:** No new failures beyond pre-existing baseline
- **verify:** `pytest tests/ -v` shows 0 new failures

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_plan_authoring_agent.py -v` | 4 passed, 0 failed |
| `pytest tests/ -v` | 0 new failures vs pre-existing baseline |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| Plan-authoring subagent configuration | `test -f .claude/agents/plan-authoring-agent.md && echo EXISTS` | EXISTS |
| implementation-cycle PLAN phase updated | `grep "plan-authoring-agent" .claude/skills/implementation-cycle/SKILL.md` | 1+ match |
| Plan quality validation (same gates) | `grep "critique-agent" .claude/skills/implementation-cycle/SKILL.md \| grep -c "Gate 1"` | 1+ (gates preserved) |
| Token savings measurement (qualitative) | `grep "plan-authoring-agent" .claude/skills/implementation-cycle/SKILL.md` | 1+ match (subagent pattern replaces inline) |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| Agent in README | `grep "plan-authoring-agent" .claude/agents/README.md` | 1+ match |
| New-plan updated | `grep "plan-authoring-agent" .claude/commands/new-plan.md` | 1+ match |
| No stale inline references | `grep "Skill(skill=\"plan-authoring-cycle\")" .claude/skills/implementation-cycle/SKILL.md` | 0 matches |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 6 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] Runtime consumer exists (implementation-cycle references subagent)
- [ ] No stale references (Consumer Integrity table above)
- [ ] READMEs updated (Consumer Integrity table above)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- @.claude/skills/plan-authoring-cycle/SKILL.md (target skill)
- @.claude/skills/implementation-cycle/SKILL.md (consumer skill)
- @.claude/agents/implementation-cycle-agent.md (sibling pattern)
- @.claude/agents/critique-agent.md (related agent)
- Memory: 84125 (plan subagent delegation decision)
- Memory: 86695-86698 (proposals for Task invocation pattern)
- Memory: 86986 (STOP: no multi-step delegation without step verification)
- WORK-176 (parent work item)

---
