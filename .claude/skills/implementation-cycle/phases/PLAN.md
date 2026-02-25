---
phase: PLAN
skill: implementation-cycle
---
# PLAN Phase

**On Entry:**
```
mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="PLAN", work_id="{work_id}")
```

**Goal:** Verify plan exists and is ready for implementation.

**Entry Gate (MUST): Work Item Critique (S397 Operator Directive)**
Before reading the plan or taking any action, **MUST** invoke critique-agent on the work item:
```
Task(subagent_type='critique-agent', model='sonnet', prompt='Critique work item for correctness: docs/work/active/{backlog_id}/WORK.md — verify all IDs in acceptance_criteria exist and are not collisions with existing IDs, all paths in source_files and references exist, traces_to references valid requirements, and frontmatter is internally consistent.')
```
- **PROCEED:** Work item is valid. Continue to Actions.
- **REVISE:** Fix identified issues in WORK.md before proceeding.
- **BLOCK:** Fundamental flaws (wrong IDs, nonexistent paths). Fix before any planning.

> **Anti-pattern prevented (S397):** "Carry flawed work item" — accepting a work item with wrong IDs, stale paths, or invalid references and building a plan on top of it. Critique catches drift from epoch transitions and ID collisions.

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

**MUST Gate: Read Source Specifications (E2-254 Learning)**
Even if plan was authored in a prior session, the implementer **MUST** read source specs:
1. Parse plan's `## References` section
2. **MUST** read each referenced specification document
3. Verify plan's Detailed Design matches spec interface
4. If mismatch detected, **BLOCK** and return to plan-authoring-cycle

> **Anti-pattern prevented:** "Inherit without verify" - accepting a plan from a prior session without reading the specs it references leads to implementing the wrong design.

**FORESIGHT Prep (Optional - E2-106):**
Before leaving PLAN phase, capture predictions to frontmatter:
```yaml
foresight_prep:
  predicted_outcome: "What I expect to happen when this is complete"
  predicted_confidence: 0.75  # How confident am I? (0-1)
  knowledge_gaps: ["What do I need to learn?"]
  skill_gaps: ["What abilities am I missing?"]
  competence_domain: "category_tag"  # e.g., "hook_development", "subagent_creation"
```
> This prepares data for Epoch 3 FORESIGHT layer. Captures ANTICIPATE operation output.

**Exit Criteria:**
- [ ] **MUST:** Work item critique passed (Entry Gate — S397)
- [ ] Plan file exists with complete design
- [ ] **MUST:** Referenced specifications read and verified against plan
- [ ] Tests defined in "Tests First" section
- [ ] Current/Desired state documented
- [ ] (Optional) foresight_prep captured with prediction
- [ ] **MUST:** Invoke critique-agent and pass critique-revise loop (see Exit Gate). Minimum 2 passes when REVISE — S397.
- [ ] **MUST:** Invoke plan-validation as haiku subagent (Gate 2 — S397)
- [ ] **MUST:** Invoke preflight-checker as haiku subagent (Gate 3 — S397)

**Exit Gate (MUST):**
Before transitioning to DO phase, execute these three gates in order:

**Gate 1 - MUST: Critique (Assumption Surfacing)**
Invoke critique-agent to surface implicit assumptions on the raw plan:
```
Task(subagent_type='critique-agent', prompt='Critique plan: docs/work/active/{backlog_id}/plans/PLAN.md')
```

Apply critique-revise loop based on verdict:
- **PROCEED on first pass:** All assumptions mitigated. Continue to Gate 2. (Only case where single pass is sufficient.)
- **REVISE:** Flagged assumptions exist. Revise plan to address them, then **MUST** re-invoke critique to verify revisions. Minimum 2 passes when first verdict is REVISE — a single REVISE→address→proceed is insufficient. The revision must be re-verified by critique-agent. Repeat until PROCEED or max 3 iterations (then escalate to operator via AskUserQuestion).
- **BLOCK:** Unmitigated low-confidence assumptions. Return to plan-authoring-cycle. DO phase blocked.

> **S397 Operator Directive:** NEVER accept a single critique pass when verdict is REVISE. The agent addressing findings is not the same as the agent verifying they were addressed. Minimum 2 passes enforced.

> Critique runs BEFORE validation so assumptions are surfaced on the raw plan, not one already "blessed" by structural checks. This prevents the S343 anti-pattern where validation momentum caused critique to be skipped.

**Gate 2 - MUST: Plan Validation (as haiku subagent — S397 Operator Directive)**
```
Task(subagent_type='preflight-checker', model='haiku', prompt='Run plan-validation-cycle for {backlog_id}. Plan: docs/work/active/{backlog_id}/plans/PLAN.md. Check: all required sections present, no placeholders. Spec-align: read all referenced specs and verify plan matches. Validate: quality checks, no [BLOCKED] in Open Decisions. Report pass/fail with specifics.')
```
Validates structural completeness and quality. Runs CHECK → SPEC_ALIGN → VALIDATE → APPROVE logic. Delegated to haiku subagent to save main context tokens — these are structural checks, not judgment calls.

> **S397 Operator Directive:** Plan validation is structural, not cognitive. MUST run as haiku subagent, not inline. Saves ~5k+ main context tokens per invocation.

**Gate 3 - MUST: Preflight Check (as haiku subagent — S397 Operator Directive)**
```
Task(subagent_type='preflight-checker', model='haiku', prompt='Check plan readiness for {backlog_id}. Plan: docs/work/active/{backlog_id}/plans/PLAN.md. Work item: docs/work/active/{backlog_id}/WORK.md. Verify plan is complete and ready for DO phase.')
```
Validates plan completeness and file scope. DO phase is blocked until all three gates pass.

> **S397 Operator Directive:** Preflight is structural verification. MUST run as haiku subagent, not inline.

**Tools:** Read, Glob, AskUserQuestion, Task(plan-authoring-agent, model=sonnet), Task(critique-agent, model=sonnet), Task(preflight-checker, model=haiku), Task(plan-validation, model=haiku)
