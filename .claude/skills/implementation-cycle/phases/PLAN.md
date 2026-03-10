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
- [ ] **Tier-aware:** Exit gates applied per tier (see Exit Gate below — REQ-LIFECYCLE-005)

**Exit Gate (Tier-Aware — REQ-LIFECYCLE-005, REQ-CEREMONY-005):**

Before transitioning to DO phase, determine the work item's governance tier, then apply the appropriate gate set.

**Step 1: Determine Tier**

Read `docs/work/active/{backlog_id}/WORK.md` frontmatter (already read at PLAN entry) and classify:

| Tier | Conditions |
|------|-----------|
| **architectural** | `type: design` OR any entry in `traces_to` starts with `ADR-` |
| **trivial** | `effort: small` AND `source_files` has 1-2 entries AND not architectural |
| **small** | `effort: small` AND `source_files` has 1-3 entries AND not architectural |
| **standard** | All other cases (default — conservative) |

> **Note:** Architectural is checked first (escalation always wins). Absent or empty `source_files` defaults to **standard** per REQ-LIFECYCLE-005 invariant: "Absent data MUST NOT produce a more permissive classification."

**Step 2: Apply Gate Set**

**If tier = trivial:**
> All exit gates SKIPPED. Trivial work items have no architectural decisions, no plan complexity requiring independent validation, and no source-file scope requiring preflight. Rationale: REQ-CEREMONY-005 (ceremony depth scales proportionally: none->checklist->full->operator). Gate-skip governance events are logged by the hook layer (PostToolUse observes PLAN->DO transition; critique_injector.py logs CritiqueInjected events for non-trivial tiers).

**If tier = small:**
> Gate 1 (Critique) runs in checklist mode — no subagent, inline self-check only. Verify:
> - [ ] All acceptance criteria are achievable with current design
> - [ ] Source files referenced in WORK.md exist and are correct
> - [ ] No implicit assumptions about interfaces or data formats
> - [ ] Edge cases identified (empty inputs, missing files, permission errors)
> - [ ] Fail-permissive pattern applied where appropriate
>
> Gate 2 (Plan-Validation) SKIPPED. Gate 3 (Preflight) SKIPPED.
> Rationale: Small items have 1-3 source files and no ADR. Structural validation overhead exceeds protection benefit.
> **Note:** critique_injector.py hook may also inject this same checklist via additionalContext. If you see the checklist in both the hook injection and this skill text, run it once (they are the same check).

**If tier = standard:**

**Gate 1 - MUST: Critique (Assumption Surfacing)**
Invoke critique-agent to surface implicit assumptions on the raw plan:
```
Task(subagent_type='critique-agent', model='sonnet', prompt='Critique plan: docs/work/active/{backlog_id}/plans/PLAN.md')
```

Apply critique-revise loop based on verdict:
- **PROCEED on first pass:** All assumptions mitigated. Continue to Gate 2. (Only case where single pass is sufficient.)
- **REVISE:** Flagged assumptions exist. Revise plan to address them, then **MUST** re-invoke critique to verify revisions. Minimum 2 passes when first verdict is REVISE. Repeat until PROCEED or max 3 iterations (then escalate to operator via AskUserQuestion).
- **BLOCK:** Unmitigated low-confidence assumptions. Return to plan-authoring-cycle. DO phase blocked.

> **S397 Operator Directive:** NEVER accept a single critique pass when verdict is REVISE. The agent addressing findings is not the same as the agent verifying they were addressed. Minimum 2 passes enforced.

> Critique runs BEFORE validation so assumptions are surfaced on the raw plan, not one already "blessed" by structural checks. This prevents the S343 anti-pattern where validation momentum caused critique to be skipped.

**Gate 2 - MUST: Plan Validation (as haiku subagent — S397 Operator Directive)**
```
Task(subagent_type='preflight-checker', model='haiku', prompt='Run plan-validation-cycle for {backlog_id}. Plan: docs/work/active/{backlog_id}/plans/PLAN.md. Check: all required sections present, no placeholders. Spec-align: read all referenced specs and verify plan matches. Validate: quality checks, no [BLOCKED] in Open Decisions. Report pass/fail with specifics.')
```
Validates structural completeness and quality. Delegated to haiku subagent to save main context tokens — structural checks, not judgment calls.

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
   This is the handoff signal — if `pending` is empty, the build-session will not detect the approved plan.
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
