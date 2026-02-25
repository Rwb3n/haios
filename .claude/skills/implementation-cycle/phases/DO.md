---
phase: DO
skill: implementation-cycle
---
# DO Phase

**On Entry:**
```bash
just set-cycle implementation-cycle DO {work_id}
```

**Goal:** Execute the plan's implementation steps via sub-agent delegation.

**The Three Contracts:**
- **Scope contract:** `docs/work/active/{backlog_id}/WORK.md` (WHAT — deliverables, AC)
- **Content contract:** `docs/work/active/{backlog_id}/plans/PLAN.md` (HOW — spec, steps, verification)
- **Dispatch contract:** This skill (HOW to orchestrate — agent sequence, handoffs, failure modes)

**Dispatch Protocol (v2.0 plans with `spec_ref`):**

For plans with `plan_version: "2.0"` in frontmatter, the DO phase dispatches mechanically:

1. Read plan Layer 2 (Implementation Steps)
2. For each step (or batch of related steps):
   a. Read the step's `spec_ref` field
   b. Extract the referenced section from Layer 1
   c. Delegate to DO sub-agent:
   ```
   Task(subagent_type='implementation-cycle-agent', prompt='
     Execute this implementation step.

     Step: {step_name}
     Action: {step_action}

     Specification (from plan):
     {extracted_spec_ref_content}

     Expected output: {step_output}
     Verification: {step_verify}

     Write the code. Run the verification command. Report result.
   ')
   ```
   d. Delegate step verification to test-runner haiku subagent:
      ```
      Task(subagent_type='test-runner', model='haiku', prompt='Run verification: {step_verify_command}. Report pass/fail.')
      ```
   e. If verify fails: re-delegate with failure context, or fix inline (max 2 retries)
   f. If verify passes: proceed to next step

3. After all steps complete, invoke design-review-validation

**Step Batching (recommended):**
- Steps 1+2 (RED+GREEN) batch naturally — TDD cycle is one delegation unit
- Steps 3 (integrate) is a separate delegation — different files, different concern
- Steps 4+5 (consumers+docs) batch naturally — both are update sweeps

**Fallback (v1.5 plans without `spec_ref`):**

For plans without `plan_version: "2.0"`, fall back to inline execution:

1. Read plan's Layer 1 / Detailed Design section
2. **MUST** write failing tests first (from plan's Tests section)
3. Implement ONE change at a time (RED -> GREEN -> REFACTOR)
4. Follow plan's Implementation Steps

**TDD Enforcement (Session 90):**
- Tests **MUST** exist before implementation code (in both v1.5 and v2.0 flows)
- For non-pytest code (PowerShell, configs), define manual verification steps in plan
- If no tests possible, document why in plan and get operator approval
- **For v2.0 plans, test runs MUST be delegated to test-runner haiku subagent** (S436 / Memory 88078):
  ```
  Task(subagent_type='test-runner', model='haiku', prompt='Run tests: {test_path_or_filter}. Report pass/fail counts and any failures.')
  ```
  For v2.0 plans, main agent MUST NOT run pytest inline. Receive structured summary from subagent.

**Exit Criteria:**
- [ ] All Layer 2 steps verified (v2.0) OR all Implementation Steps complete (v1.5)
- [ ] Each step's verify command passed
- [ ] Implementation matches Layer 1 Specification / Detailed Design
- [ ] **MUST:** Invoke design-review-validation as sonnet subagent before proceeding to CHECK

**Exit Gate (MUST):**
Before transitioning to CHECK phase, **MUST** invoke design-review-validation as a sonnet subagent:
```
Task(subagent_type='design-review-validation-agent', model='sonnet', prompt='Run design-review-validation for {backlog_id}. Plan: docs/work/active/{backlog_id}/plans/PLAN.md. Implementation files: [list from Layer 0 Primary Files]. Compare implementation against Layer 1 Specification. Report: PASS (aligned) or FAIL (deviations). For each deviation: file, expected, actual, intentional/error classification.')
```
This verifies implementation aligns with Layer 1 Specification / Detailed Design. CHECK phase is blocked until validation passes.

> **Rationale:** design-review-validation requires judgment (comparing plan intent to code) — sonnet model appropriate. Delegating saves main-agent context for DO phase implementation work.

**Tools:** Write, Edit, Task(test-runner, model=haiku), Task(implementation-cycle-agent), Task(design-review-validation-agent, model=sonnet)
