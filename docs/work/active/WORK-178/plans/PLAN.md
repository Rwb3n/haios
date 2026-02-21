---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-21
backlog_id: WORK-178
title: "CHECK Phase Subagent Delegation"
author: Hephaestus
lifecycle_phase: plan
session: 416
generated: 2026-02-21
last_updated: 2026-02-21T15:30:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-178/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete text blocks, not pseudocode"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: CHECK Phase Subagent Delegation

---

## Goal

Update implementation-cycle SKILL.md so that design-review-validation runs as a sonnet Task() subagent at DO phase exit and deliverables verification runs as a haiku Task() subagent at CHECK phase entry, eliminating inline Skill() and manual Read sequences for both operations.

---

## Open Decisions

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| No operator decisions | N/A | N/A | Work item has no operator_decisions field — all decisions pre-resolved |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/skills/implementation-cycle/SKILL.md` | MODIFY | 2 |
| `.claude/skills/design-review-validation/SKILL.md` | MODIFY | 2 |
| `.claude/agents/design-review-validation-agent.md` | CREATE | 2 |

### Consumer Files

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `CLAUDE.md` | Documents agent table and skills | top | REVIEW (no change needed — skills already listed) |
| `.claude/skills/design-review-validation/README.md` | Invocation pattern (Skill() → Task()) | 22-27 | MODIFY |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| N/A — SKILL.md edits | N/A | Verification is structural grep, not pytest |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 1 | design-review-validation-agent.md |
| Files to modify | 3 | implementation-cycle/SKILL.md + design-review-validation/SKILL.md + README.md |
| Tests to write | 0 | No Python code — verification is grep-based |
| Total blast radius | 4 | Agent file + 2 SKILL.md + README.md |

---

## Layer 1: Specification

### Current State

**File 1: `.claude/skills/implementation-cycle/SKILL.md` — DO phase exit gate (lines 217-224)**

```markdown
**Exit Gate (MUST):**
Before transitioning to CHECK phase, **MUST** invoke design-review-validation:
```
Skill(skill="design-review-validation")
```
This verifies implementation aligns with Layer 1 Specification / Detailed Design. CHECK phase is blocked until validation passes.

**Tools:** Write, Edit, Bash(pytest), Task(implementation-cycle-agent), Skill(design-review-validation)
```

**Behavior:** design-review-validation runs inline in the main agent context as a Skill() call, consuming main-agent tokens for a task that requires judgment but fits the sonnet subagent pattern established for similar validation work (critique-agent, plan-authoring-agent).

**Problem:** Runs in main agent context, consuming tokens for a Read-heavy comparison task. E2.8 Arc 1 theme: "agents spend tokens on work, not bookkeeping." Inline Skill() calls are bookkeeping for the main agent.

---

**File 1: `.claude/skills/implementation-cycle/SKILL.md` — CHECK phase MUST gate (lines 247-256)**

```markdown
**MUST Gate: Deliverables Verification (Session 192)**
Before declaring CHECK complete:
1. **MUST** read `docs/work/active/{backlog_id}/WORK.md`
2. **MUST** find the `## Deliverables` section
3. **MUST** verify EACH deliverable checkbox can be checked:
   - For each `- [ ]` item, confirm the work is actually done
   - If ANY deliverable is incomplete, **BLOCK** - return to DO phase
4. **MUST** also check plan's Implementation Steps are all complete

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290 Session 192). Agent declared victory after tests passed but skipped 2 of 7 deliverables. Tests verify code works, deliverables verify scope is complete. Both are required.
```

**Behavior:** Deliverables verification runs inline — main agent reads WORK.md, reads each deliverable, confirms each is done. Structural check, not judgment: read file, scan checklist, report pass/fail.

**Problem:** Structural file-read-and-report loop burns main-agent tokens. Fits haiku subagent: mechanical, no judgment required.

---

**File 1: `.claude/skills/implementation-cycle/SKILL.md` — CHECK phase Actions list (lines 237-245)**

```markdown
**Actions:**
1. Run test suite: `pytest tests/ -v`
2. Verify all tests pass (no regressions)
3. **DEMO the feature** - Exercise the new code path to surface bugs (Session 90)
4. Run plan's Ground Truth Verification
5. Check DoD criteria (ADR-033)
6. **MUST: Verify WORK.md Deliverables** (Session 192 - E2-290 Learning)
7. **If creating discoverable artifact:** Verify runtime discovery (see below)
8. **(Optional) Invoke validation-agent** for unbiased review: `Task(subagent_type='validation-agent')`
```

**Problem:** Action 6 references an inline process that must become a subagent call.

---

**File 1: `.claude/skills/implementation-cycle/SKILL.md` — Composition Map (lines 366-374)**

```markdown
| Phase | Primary Tool | Optional Subagent | Command |
|-------|--------------|-------------------|---------|
| PLAN  | Read, Glob   | plan-authoring-agent*, preflight-checker | /new-plan |
| DO    | Write, Edit  | -                 | - |
| CHECK | Bash(pytest) | test-runner       | /validate |
| DONE  | Edit, Write  | why-capturer      | - |
| CHAIN | Bash, Skill  | -                 | /close |
```

**Problem:** DO row shows `-` for subagents (misses design-review-validation-agent). CHECK row shows only `test-runner` (misses deliverables-verifier). Critique finding A5 requires this table be updated.

---

**File 2: `.claude/skills/design-review-validation/SKILL.md` — When to Use (lines 15-16)**

```markdown
**Manual invocation:** `Skill(skill="design-review-validation")` after implementation.
**Called from:** implementation-cycle DO phase exit (optional quality gate).
```

**Problem:** Description says "optional quality gate" and invoked by `Skill()`. After this change it is a required sonnet subagent. The "When to Use" and invocation description must reflect the new pattern.

---

### Desired State

**File 1 Change 1 — DO phase Exit Criteria (line 215)**

Replace:
```markdown
- [ ] **MUST:** Invoke `Skill(skill="design-review-validation")` before proceeding to CHECK
```

With:
```markdown
- [ ] **MUST:** Invoke design-review-validation as sonnet subagent before proceeding to CHECK
```

---

**File 1 Change 2 — DO phase Exit Gate block (lines 217-224)**

Replace:
```markdown
**Exit Gate (MUST):**
Before transitioning to CHECK phase, **MUST** invoke design-review-validation:
```
Skill(skill="design-review-validation")
```
This verifies implementation aligns with Layer 1 Specification / Detailed Design. CHECK phase is blocked until validation passes.

**Tools:** Write, Edit, Bash(pytest), Task(implementation-cycle-agent), Skill(design-review-validation)
```

With:
```markdown
**Exit Gate (MUST):**
Before transitioning to CHECK phase, **MUST** invoke design-review-validation as a sonnet subagent:
```
Task(subagent_type='design-review-validation-agent', model='sonnet', prompt='Run design-review-validation for {backlog_id}. Plan: docs/work/active/{backlog_id}/plans/PLAN.md. Implementation files: [list from Layer 0 Primary Files]. Compare implementation against Layer 1 Specification. Report: PASS (aligned) or FAIL (deviations). For each deviation: file, expected, actual, intentional/error classification.')
```
This verifies implementation aligns with Layer 1 Specification / Detailed Design. CHECK phase is blocked until validation passes.

> **Rationale:** design-review-validation requires judgment (comparing plan intent to code) — sonnet model appropriate. Delegating saves main-agent context for DO phase implementation work.

**Tools:** Write, Edit, Bash(pytest), Task(implementation-cycle-agent), Task(design-review-validation-agent, model=sonnet)
```

---

**File 1 Change 3 — CHECK phase Action 6 (line 243)**

Replace:
```markdown
6. **MUST: Verify WORK.md Deliverables** (Session 192 - E2-290 Learning)
```

With:
```markdown
6. **MUST: Delegate deliverables verification to haiku subagent** (Session 192 - E2-290 Learning)
```

---

**File 1 Change 4 — CHECK phase MUST Gate block (lines 247-256)**

Replace:
```markdown
**MUST Gate: Deliverables Verification (Session 192)**
Before declaring CHECK complete:
1. **MUST** read `docs/work/active/{backlog_id}/WORK.md`
2. **MUST** find the `## Deliverables` section
3. **MUST** verify EACH deliverable checkbox can be checked:
   - For each `- [ ]` item, confirm the work is actually done
   - If ANY deliverable is incomplete, **BLOCK** - return to DO phase
4. **MUST** also check plan's Implementation Steps are all complete

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290 Session 192). Agent declared victory after tests passed but skipped 2 of 7 deliverables. Tests verify code works, deliverables verify scope is complete. Both are required.
```

With:
```markdown
**MUST Gate: Deliverables Verification (Session 192 / WORK-178)**
Before declaring CHECK complete, delegate to haiku subagent:
```
Task(subagent_type='preflight-checker', model='haiku', prompt='Verify deliverables for {backlog_id}. Work item: docs/work/active/{backlog_id}/WORK.md. Plan: docs/work/active/{backlog_id}/plans/PLAN.md. For EACH deliverable in the Deliverables section: confirm the work is done (file exists, content matches, grep confirms). For each plan Implementation Step: confirm it is complete. Report PASS (all done) or BLOCK (list incomplete items). If BLOCK: list each incomplete deliverable with reason.')
```

- **PASS:** All deliverables verified. Proceed to remaining CHECK steps.
- **BLOCK:** Incomplete deliverables reported. Return to DO phase, address gaps, then re-run CHECK.

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290 Session 192). Agent declared victory after tests passed but skipped 2 of 7 deliverables. Tests verify code works, deliverables verify scope is complete. Both are required.

> **Rationale (WORK-178):** Deliverables verification is structural (read file, scan checklist, report pass/fail) — no judgment required. Haiku model appropriate. Saves main-agent context for value-add work.
```

---

**File 1 Change 5 — CHECK phase Tools line (line 298)**

Replace:
```markdown
**Tools:** Bash(pytest), Read, Task(test-runner), Task(validation-agent), /validate, just update-status
```

With:
```markdown
**Tools:** Bash(pytest), Read, Task(test-runner), Task(validation-agent), Task(preflight-checker, model=haiku), /validate, just update-status
```

---

**File 1 Change 6 — Composition Map (lines 368-374)**

Replace:
```markdown
| Phase | Primary Tool | Optional Subagent | Command |
|-------|--------------|-------------------|---------|
| PLAN  | Read, Glob   | plan-authoring-agent*, preflight-checker | /new-plan |
| DO    | Write, Edit  | -                 | - |
| CHECK | Bash(pytest) | test-runner       | /validate |
| DONE  | Edit, Write  | why-capturer      | - |
| CHAIN | Bash, Skill  | -                 | /close |
```

With:
```markdown
| Phase | Primary Tool | Subagent | Command |
|-------|--------------|----------|---------|
| PLAN  | Read, Glob   | plan-authoring-agent (sonnet)*, preflight-checker (haiku) | /new-plan |
| DO    | Write, Edit  | design-review-validation-agent (sonnet, exit gate) | - |
| CHECK | Bash(pytest) | test-runner (haiku), preflight-checker/deliverables (haiku) | /validate |
| DONE  | Edit, Write  | why-capturer | - |
| CHAIN | Bash, Skill  | - | /close |
```

---

**File 2 Change 1 — design-review-validation/SKILL.md When to Use (lines 15-16)**

Replace:
```markdown
**Manual invocation:** `Skill(skill="design-review-validation")` after implementation.
**Called from:** implementation-cycle DO phase exit (optional quality gate).
```

With:
```markdown
**Manual invocation:** `Skill(skill="design-review-validation")` after implementation (standalone use).
**Called from:** implementation-cycle DO phase exit as sonnet subagent (WORK-178):
```
Task(subagent_type='design-review-validation-agent', model='sonnet', prompt='...')
```
See implementation-cycle SKILL.md DO phase Exit Gate for full prompt template.
```

---

### Tests

This work modifies SKILL.md text (instructions), not Python code. Verification is structural grep rather than pytest.

#### Test 1: Task() wraps design-review-validation in DO exit gate
- **file:** N/A (grep command)
- **function:** structural check
- **setup:** implementation-cycle SKILL.md modified
- **assertion:** `grep -n "Task(subagent_type='design-review-validation-agent'" .claude/skills/implementation-cycle/SKILL.md` returns 1+ match

#### Test 2: No inline Skill() call for design-review-validation remains
- **file:** N/A (grep command)
- **function:** structural check
- **setup:** implementation-cycle SKILL.md modified
- **assertion:** `grep -n "Skill(skill=\"design-review-validation\")" .claude/skills/implementation-cycle/SKILL.md` returns 0 matches

#### Test 3: Task() wraps deliverables verification in CHECK phase
- **file:** N/A (grep command)
- **function:** structural check
- **setup:** implementation-cycle SKILL.md modified
- **assertion:** `grep -n "Task(subagent_type='preflight-checker', model='haiku'" .claude/skills/implementation-cycle/SKILL.md` returns 3+ matches (Gate 2 + Gate 3 existing + new deliverables)

#### Test 4: Composition Map updated for DO and CHECK rows
- **file:** N/A (grep command)
- **function:** structural check
- **setup:** implementation-cycle SKILL.md modified
- **assertion:** `grep -n "design-review-validation-agent" .claude/skills/implementation-cycle/SKILL.md` returns 2+ matches (exit gate + composition map)

#### Test 5: design-review-validation SKILL.md updated invocation description
- **file:** N/A (grep command)
- **function:** structural check
- **setup:** design-review-validation/SKILL.md modified
- **assertion:** `grep -n "Task(subagent_type='design-review-validation-agent'" .claude/skills/design-review-validation/SKILL.md` returns 1+ match

#### Test 6: Agent registration file exists
- **file:** N/A (file existence check)
- **function:** structural check
- **setup:** agent file created
- **assertion:** `test -f .claude/agents/design-review-validation-agent.md && echo EXISTS` returns EXISTS

#### Test 7: README.md stale Skill() reference removed
- **file:** N/A (grep command)
- **function:** structural check
- **setup:** README.md modified
- **assertion:** `grep -c "Skill(skill=\"design-review-validation\")" .claude/skills/design-review-validation/README.md` returns 0

### Design

#### File 1 (MODIFY): `.claude/skills/implementation-cycle/SKILL.md`

Six targeted edits to the existing file (described in Desired State above):
1. DO Exit Criteria checkbox — update label
2. DO Exit Gate block — replace `Skill()` with `Task(sonnet)`
3. CHECK Action 6 — update label to say "delegate"
4. CHECK MUST Gate block — replace inline steps with `Task(haiku)`
5. CHECK Tools line — add `Task(preflight-checker, model=haiku)`
6. Composition Map table — add subagent columns for DO and CHECK

All edits use Edit tool with exact `old_string`/`new_string` matching.

#### File 2 (MODIFY): `.claude/skills/design-review-validation/SKILL.md`

One targeted edit:
1. "When to Use" section — update invocation description from `Skill()` to `Task(sonnet)`

#### File 3 (CREATE): `.claude/agents/design-review-validation-agent.md`

New agent registration file following plan-authoring-agent pattern:
- name: design-review-validation-agent
- tools: Read, Glob, Grep
- model: sonnet
- context: fork
- category: verification
- description: Execute design-review-validation skill COMPARE->VERIFY->APPROVE in isolated sonnet context

#### File 4 (MODIFY): `.claude/skills/design-review-validation/README.md`

One targeted edit:
1. Lines 22-27 — update invocation from `Skill()` to `Task(sonnet)`, change "Optional quality gate" to "Required exit gate (sonnet subagent)"
2. Line 17 — remove stale L4_ALIGN phase (already removed in SKILL.md Session 233)

### Call Chain

```
implementation-cycle DO phase
    |
    +-> [each step] Task(implementation-cycle-agent)
    |
    +-> [exit gate] Task(design-review-validation-agent, model=sonnet)  # <-- NEW
            Returns: PASS | FAIL
            PASS -> proceed to CHECK
            FAIL -> return to DO

implementation-cycle CHECK phase
    |
    +-> pytest tests/ -v
    +-> DEMO feature
    +-> Ground Truth Verification
    +-> Task(preflight-checker, model=haiku)  # <-- NEW (deliverables)
    |       Returns: PASS | BLOCK
    |       PASS -> continue CHECK
    |       BLOCK -> return to DO
    +-> [optional] Task(validation-agent)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| design-review-validation model | sonnet | Requires judgment: comparing plan intent to implementation. Haiku lacks the reasoning depth for accurate comparison. Pattern matches critique-agent (sonnet). |
| deliverables verification model | haiku | Structural: read file, scan checklist, report. No judgment required. Pattern matches plan-validation and preflight-checker (haiku). Saves ~3k main-context tokens. |
| deliverables subagent_type | preflight-checker | Reuses existing haiku agent type already established in PLAN phase gates. Avoids creating a new agent type for an identical structural-check pattern. |
| design-review-validation subagent_type | design-review-validation-agent | Name matches the skill being invoked. Clear intent. Consistent with plan-authoring-agent naming convention. |
| Scope: design-review-validation SKILL.md | Update "When to Use" only | The COMPARE/VERIFY/APPROVE phases remain correct as instructions for the subagent. Only the invocation description at the top needs updating to reflect Task() call. |
| No changes to exit criteria semantics | Same pass/fail behavior | The delegation changes HOW the verification runs (subagent vs inline), not WHAT it verifies. All existing acceptance criteria remain identical. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| design-review-validation subagent returns FAIL | Same as before: return to DO phase for fixes | Test 1 (Task wrapper present) |
| deliverables subagent returns BLOCK | Same as before: return to DO phase | Test 3 (Task wrapper present) |
| Existing `Skill(design-review-validation)` calls elsewhere | implementation-cycle SKILL.md + design-review-validation README.md — both updated | Test 2 + Test 6 |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Edit old_string mismatch | M | Read exact lines before editing; use full context blocks as old_string |
| Leaving stale `Skill()` reference | M | Test 2 verifies zero inline Skill() calls remain |
| Composition Map row format breaks | L | Use exact table row replacement with verified whitespace |
| Missing second `preflight-checker` reference | L | Test 3 checks for 2+ matches (Gate 2 existing + new deliverables gate) |

---

## Layer 2: Implementation Steps

### Step 0: Create design-review-validation-agent.md
- **input:** plan-authoring-agent.md as template reference
- **action:** Create `.claude/agents/design-review-validation-agent.md` with frontmatter: name, description, tools (Read, Glob, Grep), model (sonnet), context (fork), category (verification), trigger_conditions, input/output contracts. Body: When to Use, Process (COMPARE->VERIFY->APPROVE), Guardrails.
- **output:** Agent file exists at `.claude/agents/design-review-validation-agent.md`
- **verify:** `test -f .claude/agents/design-review-validation-agent.md && echo EXISTS` returns EXISTS

### Step 1: Edit DO Exit Criteria checkbox
- **input:** implementation-cycle SKILL.md read (line 215 confirmed)
- **action:** Replace `Invoke \`Skill(skill="design-review-validation")\`` with `Invoke design-review-validation as sonnet subagent`
- **output:** Exit Criteria checkbox uses subagent language
- **verify:** `grep -n "Invoke design-review-validation as sonnet subagent" .claude/skills/implementation-cycle/SKILL.md` returns 1 match

### Step 2: Edit DO Exit Gate block (core change)
- **input:** Step 1 complete
- **action:** Replace the entire Exit Gate block (including `Skill()` code block and Tools line) with Task(sonnet) version per Desired State
- **output:** DO Exit Gate uses `Task(subagent_type='design-review-validation-agent', model='sonnet', ...)`
- **verify:** `grep -n "Task(subagent_type='design-review-validation-agent'" .claude/skills/implementation-cycle/SKILL.md` returns 1 match

### Step 3: Edit CHECK Action 6 label
- **input:** Step 2 complete
- **action:** Replace action 6 text to say "Delegate deliverables verification to haiku subagent"
- **output:** Action 6 label reflects delegation
- **verify:** `grep -n "Delegate deliverables verification to haiku subagent" .claude/skills/implementation-cycle/SKILL.md` returns 1 match

### Step 4: Edit CHECK MUST Gate block (core change)
- **input:** Step 3 complete
- **action:** Replace the entire MUST Gate block (inline steps 1-4 + anti-pattern note) with Task(haiku) version per Desired State
- **output:** CHECK MUST Gate uses `Task(subagent_type='preflight-checker', model='haiku', ...)`
- **verify:** `grep -c "Task(subagent_type='preflight-checker', model='haiku'" .claude/skills/implementation-cycle/SKILL.md` returns 3 (Gate 2 + Gate 3 existing + new deliverables gate)

### Step 5: Edit CHECK Tools line
- **input:** Step 4 complete
- **action:** Add `Task(preflight-checker, model=haiku)` to CHECK Tools line
- **output:** Tools line includes deliverables haiku subagent
- **verify:** `grep -n "Task(preflight-checker, model=haiku)" .claude/skills/implementation-cycle/SKILL.md` returns 1 match in CHECK Tools line

### Step 6: Edit Composition Map
- **input:** Step 5 complete
- **action:** Update DO row (add design-review-validation-agent) and CHECK row (add preflight-checker/deliverables) per Desired State
- **output:** Composition Map reflects actual subagent usage for DO and CHECK
- **verify:** `grep -n "design-review-validation-agent" .claude/skills/implementation-cycle/SKILL.md` returns 2+ matches

### Step 7: Edit design-review-validation SKILL.md
- **input:** Steps 1-6 complete
- **action:** Update "When to Use" section to describe Task() invocation instead of Skill()
- **output:** design-review-validation SKILL.md reflects that it is called as a subagent
- **verify:** `grep -n "Task(subagent_type='design-review-validation-agent'" .claude/skills/design-review-validation/SKILL.md` returns 1 match

### Step 8: Update design-review-validation README.md
- **input:** Step 7 complete
- **action:** Replace lines 22-27 (Skill() invocation + "Optional quality gate") with Task() invocation + "Required exit gate (sonnet subagent)". Remove stale L4_ALIGN phase from line 17.
- **output:** README.md reflects current invocation pattern, no stale Skill() references
- **verify:** `grep -c "Skill(skill=\"design-review-validation\")" .claude/skills/design-review-validation/README.md` returns 0

### Step 9: Update CLAUDE.md agent table (if needed)
- **input:** Step 8 complete
- **action:** Check CLAUDE.md Agents table for design-review-validation-agent entry. Add if missing.
- **output:** Agent discoverable in CLAUDE.md reference
- **verify:** `grep -n "design-review-validation-agent" CLAUDE.md` returns 1+ match

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/ -v` | 0 new failures vs pre-existing baseline (no Python changes) |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| Design-review-validation delegated to sonnet subagent | `grep -c "Task(subagent_type='design-review-validation-agent', model='sonnet'" .claude/skills/implementation-cycle/SKILL.md` | 1 |
| Deliverables verification delegated to haiku subagent | `grep -c "Task(subagent_type='preflight-checker', model='haiku'" .claude/skills/implementation-cycle/SKILL.md` | 3 (Gate 2 + Gate 3 existing + deliverables) |
| implementation-cycle SKILL.md updated with subagent patterns | `grep -c "design-review-validation-agent" .claude/skills/implementation-cycle/SKILL.md` | 2+ |
| No inline Skill() for design-review-validation | `grep -c "Skill(skill=\"design-review-validation\")" .claude/skills/implementation-cycle/SKILL.md` | 0 |
| Agent registration file exists | `test -f .claude/agents/design-review-validation-agent.md && echo EXISTS` | EXISTS |
| README.md stale reference removed | `grep -c "Skill(skill=\"design-review-validation\")" .claude/skills/design-review-validation/README.md` | 0 |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| Composition Map updated (DO row) | `grep -n "design-review-validation-agent (sonnet" .claude/skills/implementation-cycle/SKILL.md` | 1 match |
| Composition Map updated (CHECK row) | `grep -n "preflight-checker/deliverables" .claude/skills/implementation-cycle/SKILL.md` | 1 match |
| design-review-validation SKILL.md updated | `grep -c "Task(subagent_type='design-review-validation-agent'" .claude/skills/design-review-validation/SKILL.md` | 1 |
| No new inline Skill() regressions | `grep -c "Skill(skill=\"design-review-validation\")" .claude/skills/implementation-cycle/SKILL.md` | 0 |
| README.md no stale Skill() | `grep -c "Skill(skill=\"design-review-validation\")" .claude/skills/design-review-validation/README.md` | 0 |
| Agent file registered | `grep -n "design-review-validation-agent" .claude/agents/design-review-validation-agent.md` | 1+ match |

### Completion Criteria (DoD)

- [ ] All WORK.md deliverables verified (table above)
- [ ] No inline Skill(design-review-validation) calls remain in implementation-cycle SKILL.md
- [ ] Task(sonnet) wraps design-review-validation at DO exit gate
- [ ] Task(haiku) wraps deliverables verification at CHECK entry
- [ ] Composition Map updated for DO and CHECK rows
- [ ] design-review-validation SKILL.md "When to Use" updated
- [ ] design-review-validation-agent.md created in .claude/agents/
- [ ] design-review-validation README.md updated (no stale Skill() reference)
- [ ] CLAUDE.md agent table includes design-review-validation-agent
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `.claude/skills/implementation-cycle/SKILL.md` — primary source file (DO phase exit gate lines 217-224, CHECK phase MUST gate lines 247-256, Composition Map lines 366-374)
- `.claude/skills/design-review-validation/SKILL.md` — secondary source file (When to Use lines 15-16)
- `docs/work/active/WORK-177/WORK.md` — parent work item (CHECK phase subagent rationale)
- E2-290 (Session 192) — "Tests pass = Done" anti-pattern prevented by deliverables gate
- WORK-178 spawned_by WORK-177 — retro finding: CHECK phase activities should be subagents

---
