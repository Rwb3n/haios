---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-24
backlog_id: WORK-212
title: "Mechanical Phase Delegation to Haiku Subagents"
author: Hephaestus
lifecycle_phase: plan
session: 442
generated: 2026-02-24
last_updated: 2026-02-24T13:00:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-212/WORK.md"
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
# Implementation Plan: Mechanical Phase Delegation to Haiku Subagents

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

Modify the five implementation-cycle skill contract files (DO.md, CHECK.md, DONE.md, CHAIN.md, test-runner.md) so that all mechanical operations — pytest runs, git commits, grep verifications, and README updates — are delegated to haiku subagents instead of running inline in the main agent context.

---

## Open Decisions

<!-- No operator_decisions were present in the work item frontmatter. All design choices are resolved. -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Git commit agent type | New named agent card vs anonymous Task(Bash, haiku) | Anonymous Task(Bash, haiku) | Operator directive (S436 / Memory 88081): no new agent cards for git commits — use anonymous haiku Bash delegation |
| New agent cards for grep/README | New card vs anonymous Task(Bash, haiku) | Anonymous Task(Bash, haiku) | Same operator directive — mechanical one-shot operations do not warrant a dedicated agent card |
| test-runner card scope update | Keep CHECK-only vs expand to DO+CHECK | Expand to DO+CHECK | test-runner is invoked from DO phase now; card must reflect actual invocation scope |

---

## Layer 0: Inventory

<!-- MUST complete before any design work. Map the blast radius.
     Producer: plan-author agent
     Consumer: all downstream agents (DO, CHECK, critique) -->

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/skills/implementation-cycle/phases/DO.md` | MODIFY | 1 |
| `.claude/skills/implementation-cycle/phases/CHECK.md` | MODIFY | 1 |
| `.claude/skills/implementation-cycle/phases/DONE.md` | MODIFY | 1 |
| `.claude/skills/implementation-cycle/phases/CHAIN.md` | MODIFY | 1 |
| `.claude/agents/test-runner.md` | MODIFY | 1 |

### Consumer Files

<!-- These are markdown skill files read by the main agent at runtime. Their "consumers" are the agents
     that read them during lifecycle execution — not Python importers. No grep for Python imports applies.
     The test-runner.md card is referenced by CHECK.md and DO.md (after this change). -->

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `.claude/skills/implementation-cycle/SKILL.md` | References phase files indirectly via phase table | N/A | VERIFY (no edit needed — phases listed by name, not path) |

### Test Files

**SKIPPED:** This is a markdown-only refactor of skill contract files. There is no Python code to test. No test files are created or modified. Manual verification steps replace automated tests (see Ground Truth Verification section).

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | No new files |
| Files to modify | 5 | Primary Files table (5 MODIFY rows) |
| Tests to write | 0 | Markdown-only refactor; manual verification used |
| Total blast radius | 5 | Sum of all unique files above |

---

## Layer 1: Specification

<!-- The contract that the DO agent implements.
     Producer: plan-author agent
     Consumer: DO agent

     MUST INCLUDE:
     1. Actual current code that will be changed (copy from source)
     2. Exact target code (not pseudocode)
     3. Function signatures with types
     4. Input/output examples with REAL system data

     NOTE: All "code" here is markdown text content, not Python. Diff notation applies to
     markdown line changes within skill contract files. -->

### Current State

**DO.md — Tools line (line 84):**
```
**Tools:** Write, Edit, Bash(pytest), Task(implementation-cycle-agent), Task(design-review-validation-agent, model=sonnet)
```

**DO.md — Dispatch Protocol step 2d (line 44):**
```
   d. Run the step's `verify` command to confirm output
```
(Verification is run inline by main agent — no delegation specified.)

**DO.md — TDD Enforcement section (lines 64-67):**
```
**TDD Enforcement (Session 90):**
- Tests **MUST** exist before implementation code (in both v1.5 and v2.0 flows)
- For non-pytest code (PowerShell, configs), define manual verification steps in plan
- If no tests possible, document why in plan and get operator approval
```
(No mention of delegation; implies tests run inline.)

**CHECK.md — Actions step 1 (line 15):**
```
1. Run test suite: `pytest tests/ -v`
```
(Inline pytest call.)

**CHECK.md — Tools line (line 77):**
```
**Tools:** Bash(pytest), Read, Task(test-runner), Task(validation-agent), Task(preflight-checker, model=haiku), /validate, just update-status
```

**DONE.md — Actions section (lines 14-17):**
```
**Actions:**
1. Capture WHY: Store learnings to memory
2. Update plan status: `status: complete`
3. Update documentation if behavior changed
```
(No git commit delegation. No haiku delegation for doc updates.)

**DONE.md — Tools line (line 24):**
```
**Tools:** ingester_ingest, Edit, Write
```

**CHAIN.md — Actions section (lines 14-31):**
```
**Actions:**
1. Close work item: `/close {backlog_id}`
2. Query next work: `just ready`
...
```
(No git commit delegation.)

**CHAIN.md — Tools line (line 42):**
```
**Tools:** /close, Bash(just ready), Read, Skill(routing-gate)
```

**test-runner.md — description (line 3):**
```
description: Execute pytest in isolated context. Returns structured pass/fail summary.
  Use during CHECK phase.
```

**test-runner.md — invoked_by (lines 14-15):**
```
invoked_by:
  - implementation-cycle (CHECK phase, optional)
```

**test-runner.md — Requirement Level section (lines 34-35):**
```
**OPTIONAL** but **RECOMMENDED** during CHECK phase for large test suites.
```

**Behavior:** Tests run inline in main agent context (Bash(pytest)). Git commits are not explicitly delegated. README/doc updates are done inline. test-runner is listed as optional/CHECK-only.

**Problem:** Main agent consumes context tokens for zero-judgment work. S436 operator directive (Memory 88078) requires pytest, git commits, grep verifications, and README updates to delegate to haiku subagents. test-runner card does not reflect DO-phase invocation.

---

### Desired State

**DO.md — TDD Enforcement section (replace):**
```markdown
**TDD Enforcement (Session 90):**
- Tests **MUST** exist before implementation code (in both v1.5 and v2.0 flows)
- For non-pytest code (PowerShell, configs), define manual verification steps in plan
- If no tests possible, document why in plan and get operator approval
- **For v2.0 plans, test runs MUST be delegated to test-runner haiku subagent** (S436 / Memory 88078):
  ```
  Task(subagent_type='test-runner', model='haiku', prompt='Run tests: {test_path_or_filter}. Report pass/fail counts and any failures.')
  ```
  For v2.0 plans, main agent MUST NOT run pytest inline. Receive structured summary from subagent.
```

**DO.md — Dispatch Protocol step 2d (replace):**
```markdown
   d. Delegate step verification to test-runner haiku subagent:
      ```
      Task(subagent_type='test-runner', model='haiku', prompt='Run verification: {step_verify_command}. Report pass/fail.')
      ```
   e. If verify fails: re-delegate with failure context, or fix inline (max 2 retries)
   f. If verify passes: proceed to next step
```

**DO.md — Tools line (replace):**
```
**Tools:** Write, Edit, Task(test-runner, model=haiku), Task(implementation-cycle-agent), Task(design-review-validation-agent, model=sonnet)
```

**CHECK.md — Actions step 1 (replace):**
```markdown
1. **Delegate test suite run to test-runner haiku subagent** (S436 / Memory 88078):
   ```
   Task(subagent_type='test-runner', model='haiku', prompt='Run full test suite: pytest tests/ -v --tb=short. Report pass/fail counts, duration, and any failed test names with errors.')
   ```
   For v2.0 plans, main agent MUST NOT run pytest inline. Receive structured summary from subagent.
2. Verify all tests pass (no regressions) per subagent summary
```

**CHECK.md — Tools line (replace):**
```
**Tools:** Read, Task(test-runner, model=haiku), Task(validation-agent), Task(preflight-checker, model=haiku), /validate, just update-status
```

**DONE.md — Actions section (replace):**
```markdown
**Actions:**
1. Capture WHY: Store learnings to memory
2. Update plan status: `status: complete`
3. Update documentation if behavior changed — **delegate to haiku subagent** (S436 / Memory 88078):
   - Before delegating: enumerate the specific behavioral changes made in this session (e.g., "Added Task(test-runner, model=haiku) delegation to DO.md TDD section"). Substitute into the prompt below.
   ```
   Task(subagent_type='Bash', model='haiku', prompt='Update CLAUDE.md and relevant READMEs to reflect changes from {backlog_id}. Specific changes: [enumerate changes from this session]. Verify grep confirms updates.')
   ```
4. **Delegate git commit to haiku subagent** (S436 / Memory 88078):
   ```
   Task(subagent_type='Bash', model='haiku', prompt='Stage and commit all changes for {backlog_id}. Command: git add -A && git commit -m "Session {session}: {backlog_id} {title}". Report exit code and commit hash.')
   ```
```

**DONE.md — Exit Criteria (add git commit checkbox):**
```markdown
**Exit Criteria:**
- [ ] WHY captured (memory_refs in checkpoint)
- [ ] Plan marked complete
- [ ] Docs updated (CLAUDE.md, READMEs) — delegated to haiku subagent
- [ ] Git commit executed — delegated to haiku subagent
```

**DONE.md — Tools line (replace):**
```
**Tools:** ingester_ingest, Edit, Task(Bash, model=haiku)
```

**CHAIN.md — Actions section, after step 1 (insert new step 2):**
```markdown
**Actions:**
1. Close work item: `/close {backlog_id}`
2. **Delegate git commit to haiku subagent** (S436 / Memory 88078):
   ```
   Task(subagent_type='Bash', model='haiku', prompt='Stage and commit all changes for {backlog_id}. Command: git add -A && git commit -m "Session {session}: {backlog_id} {title}". Report exit code and commit hash.')
   ```
3. Query next work: `just ready`
4. If items returned, read first work file to check `documents.plans`
5. Read work item `type` field from WORK.md
6. **Apply routing decision table** (see `routing-gate` skill): ...
```

**CHAIN.md — Tools line (replace):**
```
**Tools:** /close, Task(Bash, model=haiku), Bash(just ready), Read, Skill(routing-gate)
```

**test-runner.md — description (replace):**
```yaml
description: Execute pytest in isolated context. Returns structured pass/fail summary.
  Use during DO and CHECK phases.
```

**test-runner.md — invoked_by (replace):**
```yaml
invoked_by:
  - implementation-cycle (DO phase, TDD test runs)
  - implementation-cycle (CHECK phase, full suite verification)
```

**test-runner.md — Requirement Level section (replace):**
```markdown
**REQUIRED** during DO phase for all pytest test runs.
**REQUIRED** during CHECK phase for full test suite verification.

Main agent MUST NOT run pytest inline. Delegate all test execution to this subagent (S436 / Memory 88078).
```

**Behavior after:** All mechanical test runs, git commits, grep verifications, and README updates are executed by haiku subagents. Main agent receives structured summaries only. test-runner card accurately reflects DO+CHECK invocation scope.

**Result:** Main agent context preserved for judgment-requiring work. Haiku handles all zero-judgment mechanical operations.

---

### Tests

**SKIPPED (markdown-only refactor):** These skill files are behavioral contracts read by the main agent — they contain no Python code and are not imported by any module. There is no pytest-testable interface.

Manual verification steps replace automated tests (see Ground Truth Verification section). Verification approach:
1. Grep the modified files for presence of delegation patterns
2. Grep for absence of inline pytest/bash calls for test runs
3. Confirm test-runner.md invoked_by field includes DO phase
4. Confirm DONE.md and CHAIN.md contain Task(Bash, model=haiku) for git commit

This satisfies acceptance criterion 4: "DO.md and CHECK.md contain no inline pytest/bash tool calls for test runs."

---

### Design

#### File 1 (MODIFY): `.claude/skills/implementation-cycle/phases/DO.md`

**Location:** TDD Enforcement section and Tools line.

**Current Code (lines 64-67, 84):**
```markdown
**TDD Enforcement (Session 90):**
- Tests **MUST** exist before implementation code (in both v1.5 and v2.0 flows)
- For non-pytest code (PowerShell, configs), define manual verification steps in plan
- If no tests possible, document why in plan and get operator approval

...

**Tools:** Write, Edit, Bash(pytest), Task(implementation-cycle-agent), Task(design-review-validation-agent, model=sonnet)
```

**Target Code:**
```markdown
**TDD Enforcement (Session 90):**
- Tests **MUST** exist before implementation code (in both v1.5 and v2.0 flows)
- For non-pytest code (PowerShell, configs), define manual verification steps in plan
- If no tests possible, document why in plan and get operator approval
- **For v2.0 plans, test runs MUST be delegated to test-runner haiku subagent** (S436 / Memory 88078):
  ```
  Task(subagent_type='test-runner', model='haiku', prompt='Run tests: {test_path_or_filter}. Report pass/fail counts and any failures.')
  ```
  For v2.0 plans, main agent MUST NOT run pytest inline. Receive structured summary from subagent.

...

**Tools:** Write, Edit, Task(test-runner, model=haiku), Task(implementation-cycle-agent), Task(design-review-validation-agent, model=sonnet)
```

Also update Dispatch Protocol step 2d (line 44):

**Current:**
```markdown
   d. Run the step's `verify` command to confirm output
   e. If verify fails: re-delegate with failure context, or fix inline (max 2 retries)
   f. If verify passes: proceed to next step
```

**Target:**
```markdown
   d. Delegate step verification to test-runner haiku subagent:
      ```
      Task(subagent_type='test-runner', model='haiku', prompt='Run verification: {step_verify_command}. Report pass/fail.')
      ```
   e. If verify fails: re-delegate with failure context, or fix inline (max 2 retries)
   f. If verify passes: proceed to next step
```

---

#### File 2 (MODIFY): `.claude/skills/implementation-cycle/phases/CHECK.md`

**Location:** Actions step 1 and Tools line.

**Current Code (lines 15, 77):**
```markdown
1. Run test suite: `pytest tests/ -v`

...

**Tools:** Bash(pytest), Read, Task(test-runner), Task(validation-agent), Task(preflight-checker, model=haiku), /validate, just update-status
```

**Target Code:**
```markdown
1. **Delegate test suite run to test-runner haiku subagent** (S436 / Memory 88078):
   ```
   Task(subagent_type='test-runner', model='haiku', prompt='Run full test suite: pytest tests/ -v --tb=short. Report pass/fail counts, duration, and any failed test names with errors.')
   ```
   For v2.0 plans, main agent MUST NOT run pytest inline. Receive structured summary from subagent.
2. Verify all tests pass (no regressions) per subagent summary

...

**Tools:** Read, Task(test-runner, model=haiku), Task(validation-agent), Task(preflight-checker, model=haiku), /validate, just update-status
```

Note: The existing Actions list shifts numbering — original step 2 ("Verify all tests pass") is absorbed into the new step 1 as a follow-up action. Original steps 3-8 become steps 3-8 (with numbering adjusted naturally in context). The explicit two-part presentation above is the target for the first two action items.

---

#### File 3 (MODIFY): `.claude/skills/implementation-cycle/phases/DONE.md`

**Location:** Actions section, Exit Criteria, and Tools line.

**Current Code (lines 14-24):**
```markdown
**Actions:**
1. Capture WHY: Store learnings to memory
2. Update plan status: `status: complete`
3. Update documentation if behavior changed

**Exit Criteria:**
- [ ] WHY captured (memory_refs in checkpoint)
- [ ] Plan marked complete
- [ ] Docs updated (CLAUDE.md, READMEs)

**Tools:** ingester_ingest, Edit, Write
```

**Target Code:**
```markdown
**Actions:**
1. Capture WHY: Store learnings to memory
2. Update plan status: `status: complete`
3. Update documentation if behavior changed — **delegate to haiku subagent** (S436 / Memory 88078):
   - Before delegating: enumerate the specific behavioral changes made in this session (e.g., "Added Task(test-runner, model=haiku) delegation to DO.md TDD section"). Substitute into the prompt below.
   ```
   Task(subagent_type='Bash', model='haiku', prompt='Update CLAUDE.md and relevant READMEs to reflect changes from {backlog_id}. Specific changes: [enumerate changes from this session]. Verify grep confirms updates.')
   ```
4. **Delegate git commit to haiku subagent** (S436 / Memory 88078):
   ```
   Task(subagent_type='Bash', model='haiku', prompt='Stage and commit all changes for {backlog_id}. Command: git add -A && git commit -m "Session {session}: {backlog_id} {title}". Report exit code and commit hash.')
   ```

**Exit Criteria:**
- [ ] WHY captured (memory_refs in checkpoint)
- [ ] Plan marked complete
- [ ] Docs updated (CLAUDE.md, READMEs) — delegated to haiku subagent
- [ ] Git commit executed — delegated to haiku subagent

**Tools:** ingester_ingest, Edit, Task(Bash, model=haiku)
```

---

#### File 4 (MODIFY): `.claude/skills/implementation-cycle/phases/CHAIN.md`

**Location:** Actions section and Tools line.

**Current Code (lines 14-30, 42):**
```markdown
**Actions:**
1. Close work item: `/close {backlog_id}`
2. Query next work: `just ready`
3. If items returned, read first work file to check `documents.plans`
4. Read work item `type` field from WORK.md
5. **Apply routing decision table** (see `routing-gate` skill): ...

...

**Tools:** /close, Bash(just ready), Read, Skill(routing-gate)
```

**Target Code:**
```markdown
**Actions:**
1. Close work item: `/close {backlog_id}`
2. **Delegate git commit to haiku subagent** (S436 / Memory 88078):
   ```
   Task(subagent_type='Bash', model='haiku', prompt='Stage and commit all changes for {backlog_id}. Command: git add -A && git commit -m "Session {session}: {backlog_id} {title}". Report exit code and commit hash.')
   ```
3. Query next work: `just ready`
4. If items returned, read first work file to check `documents.plans`
5. Read work item `type` field from WORK.md
6. **Apply routing decision table** (see `routing-gate` skill):
   - If `next_work_id` is None → `await_operator`
   - If `type` == "investigation" OR ID starts with `INV-` → `invoke_investigation`
   - If `has_plan` is True → `invoke_implementation`
   - Else → `invoke_work_creation`
7. Execute the action:
   - `invoke_investigation` -> `Skill(skill="investigation-cycle")`
   - `invoke_implementation` -> `Skill(skill="implementation-cycle")`
   - `invoke_work_creation` -> `Skill(skill="work-creation-cycle")`
   - `await_operator` -> Report "No unblocked work. Awaiting operator direction."

...

**Tools:** /close, Task(Bash, model=haiku), Bash(just ready), Read, Skill(routing-gate)
```

---

#### File 5 (MODIFY): `.claude/agents/test-runner.md`

**Location:** Frontmatter description, invoked_by, and Requirement Level body section.

**Current Code (lines 3-4, 14-15, 34-35):**
```yaml
description: Execute pytest in isolated context. Returns structured pass/fail summary.
  Use during CHECK phase.
```
```yaml
invoked_by:
  - implementation-cycle (CHECK phase, optional)
```
```markdown
**OPTIONAL** but **RECOMMENDED** during CHECK phase for large test suites.

Executes tests in isolated context, returns clean summary to parent.
```

**Target Code:**
```yaml
description: Execute pytest in isolated context. Returns structured pass/fail summary.
  Use during DO and CHECK phases.
```
```yaml
invoked_by:
  - implementation-cycle (DO phase, TDD test runs — required)
  - implementation-cycle (CHECK phase, full suite verification — required)
```
```markdown
**REQUIRED** during DO phase for all pytest test runs.
**REQUIRED** during CHECK phase for full test suite verification.

Main agent MUST NOT run pytest inline. Delegate all test execution to this subagent (S436 / Memory 88078).

Executes tests in isolated context, returns clean summary to parent.
```

---

### Call Chain

```
Main Agent (implementation-cycle)
    |
    +-> DO Phase
    |     |
    |     +-> Task(test-runner, model=haiku)   # TDD test runs (RED/GREEN)
    |     |       Returns: pass/fail summary
    |     |
    |     +-> Task(design-review-validation-agent, model=sonnet)  # Exit gate
    |
    +-> CHECK Phase
    |     |
    |     +-> Task(test-runner, model=haiku)   # Full suite run
    |     |       Returns: structured summary
    |     |
    |     +-> Task(preflight-checker, model=haiku)  # Deliverables gate
    |
    +-> DONE Phase
    |     |
    |     +-> Task(Bash, model=haiku)          # README/CLAUDE.md updates
    |     +-> Task(Bash, model=haiku)          # git commit
    |
    +-> CHAIN Phase
          |
          +-> Task(Bash, model=haiku)          # git commit
```

---

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Git commit agent type | Anonymous `Task(subagent_type='Bash', model='haiku')` | Operator directive (S436 / Memory 88081): no new agent cards for one-shot mechanical ops. Anonymous haiku Bash is sufficient. |
| Grep/README agent type | Anonymous `Task(subagent_type='Bash', model='haiku')` | Same operator directive. grep and README updates are zero-judgment; no dedicated card warranted. |
| test-runner requirement level | Change from OPTIONAL to REQUIRED | OPTIONAL implies inline pytest is acceptable fallback. After this change, inline pytest is explicitly prohibited in DO/CHECK. Card must state REQUIRED. |
| DONE vs CHAIN for git commit | Add to BOTH | DONE is the primary closure; CHAIN is the handoff. Retaining git commit in DONE ensures work is committed even if CHAIN is not reached. CHAIN commit handles any files touched during routing. |
| TDD enforcement wording | Add bullet + code block to existing section | Least disruptive edit. Existing section header and first three bullets remain. New bullet adds delegation mandate. Preserves operator context (Session 90 attribution). |
| CHECK step 1 rewrite | Full replacement of "Run test suite: `pytest tests/ -v`" | Inline pytest call must be completely removed. Partial edit risks ambiguity. Full replacement is unambiguous. |
| Memory query result | Memory 88078, 88081, 87218 found relevant | 88078: S436 directive (pytest/git/grep/README = haiku). 88081: PARTIAL DELEGATE pattern. 87218: sonnet for judgment, haiku for structural. All confirm this design. |

---

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| Non-pytest work items (docs, ADRs) | CHECK.md already has "For non-code tasks" section — delegation pattern still applies but test-runner is skipped per existing guidance | Manual verification |
| Git commit fails (nothing to commit) | haiku subagent reports exit code; main agent notes in session log; not a blocking error | Manual verification |
| Test-runner haiku subagent returns FAIL | Main agent receives structured summary, returns to DO phase inline per existing retry logic | Manual verification |
| CHAIN phase skipped (rare operator path) | DONE phase git commit is sufficient; CHAIN commit is belt-and-suspenders | N/A |

---

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Old inline pytest habit persists | M | Tools line explicitly removes `Bash(pytest)` from DO.md and CHECK.md; new agents reading the contract will not see it as a valid tool |
| DONE vs CHAIN git commit duplication | L | Two commits for same work is benign; second commit will be a no-op if DONE already committed. Git handles gracefully. |
| test-runner card says REQUIRED but main agent does not enforce | M | MUST language + rationale reference (S436) in TDD Enforcement section provides behavioral pressure; plan-validation-cycle will check for delegation pattern in plans going forward |
| Grep verifications acceptance criterion not fully addressed by these changes | M | The acceptance criterion "Grep verifications delegated" is addressed in DONE.md step 3 (Bash haiku for README/grep confirm). CHECK phase preflight-checker haiku already covers deliverable grep checks. |

---

## Layer 2: Implementation Steps

<!-- Ordered steps. Each step is a sub-agent delegation unit.
     Producer: plan-author agent
     Consumer: DO agent + orchestrator -->

### Step 1: Modify DO.md — TDD Enforcement and Dispatch Protocol
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY)
- **input:** Source file read; current content known
- **action:** Edit `.claude/skills/implementation-cycle/phases/DO.md` — (a) add delegation bullet + code block to TDD Enforcement section, (b) replace step 2d in Dispatch Protocol with haiku delegation call, (c) replace Tools line removing `Bash(pytest)`
- **output:** DO.md contains `Task(test-runner, model=haiku)` in TDD section; Tools line has no `Bash(pytest)`
- **verify:** `grep -n "Bash(pytest)" .claude/skills/implementation-cycle/phases/DO.md` returns 0 matches AND `grep -n "test-runner" .claude/skills/implementation-cycle/phases/DO.md` returns 2+ matches

### Step 2: Modify CHECK.md — Delegate pytest and Update Tools
- **spec_ref:** Layer 1 > Design > File 2 (MODIFY)
- **input:** Source file read; current content known
- **action:** Edit `.claude/skills/implementation-cycle/phases/CHECK.md` — (a) replace Action step 1 `pytest tests/ -v` inline call with `Task(test-runner, model=haiku)` delegation block, (b) replace Tools line removing `Bash(pytest)`
- **output:** CHECK.md step 1 contains Task delegation; no inline pytest call; Tools line updated
- **verify:** `grep -n "Bash(pytest)" .claude/skills/implementation-cycle/phases/CHECK.md` returns 0 matches AND `grep -n "test-runner" .claude/skills/implementation-cycle/phases/CHECK.md` returns 2+ matches (body delegation block + Tools line)

### Step 3: Modify DONE.md — Add Git Commit and Doc Update Delegation
- **spec_ref:** Layer 1 > Design > File 3 (MODIFY)
- **input:** Source file read; current content known
- **action:** Edit `.claude/skills/implementation-cycle/phases/DONE.md` — (a) expand Actions to 4 steps adding haiku Bash delegation for doc updates and git commit, (b) add git commit checkbox to Exit Criteria, (c) replace Tools line
- **output:** DONE.md Actions has 4 steps; Exit Criteria has git commit checkbox; Tools line updated
- **verify:** `grep -n "Task(Bash, model=haiku)" .claude/skills/implementation-cycle/phases/DONE.md` returns 2 matches AND `grep -n "git commit" .claude/skills/implementation-cycle/phases/DONE.md` returns 2+ matches

### Step 4: Modify CHAIN.md — Add Git Commit Delegation
- **spec_ref:** Layer 1 > Design > File 4 (MODIFY)
- **input:** Source file read; current content known
- **action:** Edit `.claude/skills/implementation-cycle/phases/CHAIN.md` — (a) insert new step 2 with haiku Bash git commit delegation after the `/close` step, (b) fix pre-existing duplicate step numbering: current file has two items both labeled "5." (line 19: routing decision table, line 24: execute the action) — renumber all subsequent steps so final sequence is 1-7 with no duplicates, (c) add `Task(Bash, model=haiku)` to Tools line
- **output:** CHAIN.md has git commit delegation as step 2; 7 sequential steps with no duplicates; Tools line updated
- **verify:** `grep -c "^[0-9]\." .claude/skills/implementation-cycle/phases/CHAIN.md` returns 7 AND `grep -n "Task(Bash, model=haiku)" .claude/skills/implementation-cycle/phases/CHAIN.md` returns 1 match

### Step 5: Modify test-runner.md — Expand Scope to DO+CHECK
- **spec_ref:** Layer 1 > Design > File 5 (MODIFY)
- **input:** Source file read; current content known
- **action:** Edit `.claude/agents/test-runner.md` — (a) update description to say "DO and CHECK phases", (b) update invoked_by to list both DO and CHECK entries with "(required)", (c) replace Requirement Level section body from OPTIONAL to REQUIRED with rationale
- **output:** test-runner.md describes DO+CHECK scope; invoked_by has two entries; Requirement Level says REQUIRED
- **verify:** `grep -n "DO phase" .claude/agents/test-runner.md` returns 1+ match AND `grep -n "REQUIRED" .claude/agents/test-runner.md` returns 2+ matches

---

## Ground Truth Verification

<!-- Computable verification protocol.
     Producer: plan-author agent
     Consumer: CHECK agent + orchestrator

     Every line has a command and expected output.
     The CHECK agent runs these mechanically — no judgment needed. -->

### Tests

**SKIPPED:** Markdown-only refactor. No pytest tests exist or are needed. Manual verification via grep commands (see Deliverables table) replaces automated test suite.

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| pytest delegation in DO phase | `grep -c "test-runner" .claude/skills/implementation-cycle/phases/DO.md` | 2 or more |
| No inline pytest in DO phase | `grep -c "Bash(pytest)" .claude/skills/implementation-cycle/phases/DO.md` | 0 |
| pytest delegation in CHECK phase | `grep -c "test-runner" .claude/skills/implementation-cycle/phases/CHECK.md` | 2 or more |
| No inline pytest in CHECK phase | `grep -c "Bash(pytest)" .claude/skills/implementation-cycle/phases/CHECK.md` | 0 |
| Git commit in DONE phase | `grep -c "git commit" .claude/skills/implementation-cycle/phases/DONE.md` | 2 or more |
| Git commit haiku delegation in DONE | `grep -c "Task(Bash, model=haiku)" .claude/skills/implementation-cycle/phases/DONE.md` | 2 |
| Git commit in CHAIN phase | `grep -c "git commit" .claude/skills/implementation-cycle/phases/CHAIN.md` | 1 or more |
| Git commit haiku delegation in CHAIN | `grep -c "Task(Bash, model=haiku)" .claude/skills/implementation-cycle/phases/CHAIN.md` | 1 |
| test-runner covers DO phase | `grep -c "DO phase" .claude/agents/test-runner.md` | 1 or more |
| test-runner is REQUIRED | `grep -c "REQUIRED" .claude/agents/test-runner.md` | 2 or more |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| DO.md Tools line has no Bash(pytest) | `grep "Bash(pytest)" .claude/skills/implementation-cycle/phases/DO.md` | 0 matches |
| CHECK.md Tools line has no Bash(pytest) | `grep "Bash(pytest)" .claude/skills/implementation-cycle/phases/CHECK.md` | 0 matches |
| DONE.md Tools line updated | `grep "Task(Bash, model=haiku)" .claude/skills/implementation-cycle/phases/DONE.md` | 1+ match |
| CHAIN.md Tools line updated | `grep "Task(Bash, model=haiku)" .claude/skills/implementation-cycle/phases/CHAIN.md` | 1+ match |
| All 5 source files exist | `ls .claude/skills/implementation-cycle/phases/DO.md .claude/skills/implementation-cycle/phases/CHECK.md .claude/skills/implementation-cycle/phases/DONE.md .claude/skills/implementation-cycle/phases/CHAIN.md .claude/agents/test-runner.md` | 5 files listed |

### Completion Criteria (DoD)

- [ ] All WORK.md deliverables verified (table above passes all grep checks)
- [ ] No inline pytest calls remain in DO.md or CHECK.md Tools lines
- [ ] Git commit delegation present in DONE.md and CHAIN.md
- [ ] test-runner.md updated to DO+CHECK scope with REQUIRED status
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" =/= "Deliverables complete". For this markdown-only work: grep verification = test pass. Both deliverable verification AND scope completeness required. (E2-290)

---

## References

- WORK-209: Parent work item (S436 ceremony automation investigation)
- WORK-212: This work item
- Memory 88078: S436 operator observation — pytest, git commits, grep verifications, README updates are all haiku jobs
- Memory 88081: PARTIAL DELEGATE pattern — mechanical steps delegate, AskUserQuestion stays in main agent
- Memory 87218: sonnet for judgment, haiku for structural checks
- `.claude/agents/test-runner.md`: Existing test-runner subagent card (source file)
- `.claude/skills/implementation-cycle/phases/DO.md`: Source file (TDD enforcement, dispatch protocol)
- `.claude/skills/implementation-cycle/phases/CHECK.md`: Source file (Actions step 1, Tools)
- `.claude/skills/implementation-cycle/phases/DONE.md`: Source file (Actions, Exit Criteria, Tools)
- `.claude/skills/implementation-cycle/phases/CHAIN.md`: Source file (Actions, Tools)

---
