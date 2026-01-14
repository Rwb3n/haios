---
template: investigation
status: active
date: 2026-01-05
backlog_id: INV-058
title: Ambiguity Gating for Plan Authoring
author: Hephaestus
session: 175
lifecycle_phase: conclude
spawned_by: E2-271
related:
- E2-271
- E2-272
- E2-273
- E2-274
- E2-275
memory_refs:
- 80806
- 80807
- 80808
- 80809
- 80810
- 80811
- 80812
- 80813
- 80814
- 80815
- 80816
- 80817
version: '2.0'
generated: 2025-12-22
last_updated: '2026-01-05T21:37:08'
---
# Investigation: Ambiguity Gating for Plan Authoring

@docs/README.md
@docs/epistemic_state.md

<!-- FILE REFERENCE REQUIREMENTS (MUST - Session 171 Learning)

     1. MUST use full @ paths for prior work:
        CORRECT: @docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md
        WRONG:   INV-052, "See INV-052"

     2. MUST read ALL @ referenced files BEFORE starting EXPLORE phase:
        - Read each @path listed at document top
        - For directory references (@docs/work/active/INV-052/), MUST Glob to find all files
        - Document key findings in Prior Work Query section
        - Do NOT proceed to EXPLORE until references are read

     3. MUST Glob referenced directories:
        @docs/work/active/INV-052/ → Glob("docs/work/active/INV-052/**/*.md")
        Then read key files (SECTION-*.md, WORK.md, investigations/*.md)

     Rationale: Session 171 wasted ~15% context searching for INV-052 in wrong
     location because agent ignored @ references and guessed file locations.
-->

<!-- TEMPLATE GOVERNANCE (v2.0 - E2-144)

     INVESTIGATION CYCLE: HYPOTHESIZE -> EXPLORE -> CONCLUDE

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: Pure discovery, no design outputs needed"
     - "SKIPPED: Single hypothesis, no complex mapping required"
     - "SKIPPED: External research only, no codebase evidence"

     This prevents silent section deletion and ensures conscious decisions.

     SUBAGENT REQUIREMENT (L3):
     For EXPLORE phase, you MUST invoke investigation-agent subagent:
     Task(prompt='EXPLORE: {hypothesis}', subagent_type='investigation-agent')

     Rationale: Session 101 proved L2 ("RECOMMENDED") guidance is ignored ~20% of time.
     L3 enforcement ensures structured evidence gathering.
-->

---

## Discovery Protocol (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Query memory first | SHOULD | Search for prior investigations on topic before starting |
| Document hypotheses | SHOULD | State what you expect to find before exploring |
| Use investigation-agent | MUST | Delegate EXPLORE phase to subagent for structured evidence |
| Capture findings | MUST | Fill Findings section with evidence, not assumptions |

---

## Context

<!-- HYPOTHESIZE PHASE: Describe background before exploring -->

**Trigger:** During E2-271 plan authoring (Session 175), agent designed a plan based on wrong assumption. Work item had `operator_decision_needed` (implement modules OR remove references) but agent chose "remove references" without asking operator.

**Problem Statement:** No enforcement mechanism exists to surface and resolve ambiguity before plan design begins, leading to wasted effort and operator frustration.

**Prior Observations:**
- E2-271 WORK.md had ambiguous deliverables requiring operator decision
- Agent proceeded to design without surfacing the decision
- Operator caught the error and demanded investigation
- Memory concept 8220: "agent failures and operator burnout caused by executing on ambiguous or incomplete plans"

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "ambiguity gating operator decisions plan authoring template validation"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 80515 | "Plan validation was checking template structure but not requirements alignment" | Direct - validates that structural validation exists but semantic/decision validation missing |
| 8220 | "agent failures and operator burnout caused by executing on ambiguous or incomplete plans" | Direct - confirms this is a known problem class |
| 7621 | "A malicious or poorly designed plan could intentionally omit the guideline context, bypassing the control" | Tangential - shows validation gaps exist |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] No prior investigation specifically on ambiguity gating found

---

## Objective

<!-- One clear question this investigation will answer -->

**Where should ambiguity gating exist in the plan authoring workflow, and what mechanism should enforce it?**

---

## Scope

### In Scope
- Identify all locations where ambiguity can enter plan authoring
- Analyze existing templates and skills for gating opportunities
- Design gating mechanism (template section, skill phase, validation check)
- Spawn implementation work items for each gate location

### Out of Scope
- Implementation of the gates (spawned as separate work items)
- Ambiguity in non-plan contexts (investigations, ADRs)
- Automated ambiguity detection via LLM analysis

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 4 | Templates + skills |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | Codebase | Template, skill analysis |
| Estimated complexity | Medium | Multiple integration points |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | Template needs "Open Decisions" section that MUST be resolved | High | Check implementation_plan.md for existing section | 1st |
| **H2** | plan-authoring-cycle needs AMBIGUITY phase before AUTHOR | High | Read skill, check if work item decisions are surfaced | 2nd |
| **H3** | plan-validation-cycle needs ambiguity check in VALIDATE | Med | Read skill, check for open decision detection | 3rd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order -->

### Phase 1: Evidence Gathering
1. [x] Query memory for prior learnings on topic (done in Prior Work Query)
2. [x] Read implementation_plan.md template
3. [x] Read plan-authoring-cycle skill
4. [x] Read plan-validation-cycle skill
5. [x] Read work_item.md template

### Phase 2: Hypothesis Testing
6. [x] Test H1: Check template for "Open Decisions" section
7. [x] Test H2: Check plan-authoring-cycle for work item decision surfacing
8. [x] Test H3: Check plan-validation-cycle for ambiguity detection

### Phase 3: Synthesis
9. [x] Compile evidence table
10. [x] Determine verdict for each hypothesis
11. [ ] Identify spawned work items

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| Template has "Open Questions" but not "Open Decisions" section | `.claude/templates/implementation_plan.md:292-298` | H1 | Only questions during design, not decisions from work item |
| Template has no mechanism to surface work item ambiguity | `.claude/templates/implementation_plan.md` (entire) | H1 | No reference to work item decision fields |
| plan-authoring-cycle reads specs but NOT work item | `.claude/skills/plan-authoring-cycle/SKILL.md:32` | H2 | Reads plan file only, not source work item |
| plan-authoring-cycle has no AMBIGUITY phase | `.claude/skills/plan-authoring-cycle/SKILL.md:21-25` | H2 | Cycle is ANALYZE->AUTHOR->VALIDATE, no decision surfacing |
| plan-validation-cycle checks section completeness | `.claude/skills/plan-validation-cycle/SKILL.md:29-39` | H3 | Checks for placeholders but not for open decisions |
| plan-validation-cycle has no ambiguity check | `.claude/skills/plan-validation-cycle/SKILL.md:88-116` | H3 | VALIDATE phase checks quality but not decisions |
| work_item template has no `operator_decision_needed` field | `.claude/templates/work_item.md` (entire) | H1,H2 | No structured field for decisions |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 80515 | "Plan validation was checking template structure but not requirements alignment" | H3 | Confirms validation gap exists |
| 8220 | "agent failures caused by executing on ambiguous plans" | H1,H2,H3 | Confirms problem class |

### External Evidence (if applicable)

**SKIPPED:** Investigation is codebase-focused, no external sources needed.

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **Confirmed** | Template has "Open Questions" (line 292) but no "Open Decisions" section for work item ambiguity | High |
| H2 | **Confirmed** | plan-authoring-cycle reads plan file (line 32) but never reads source work item to check for decisions | High |
| H3 | **Confirmed** | plan-validation-cycle VALIDATE phase (lines 88-116) checks quality but has no check for unresolved decisions | High |

### Detailed Findings

#### Finding 1: No Structured Field for Operator Decisions

**Evidence:**
```yaml
# work_item.md template - NO field for operator_decision_needed
# E2-271 WORK.md had this as prose in Deliverables, not structured field
```

**Analysis:** Work items can have ambiguity but there's no structured way to flag it. Agents must infer from prose, which is unreliable.

**Implication:** Add `operator_decisions` field to work_item template (structured list of decisions needed).

#### Finding 2: Plan-Authoring Doesn't Read Work Item

**Evidence:**
```markdown
# plan-authoring-cycle/SKILL.md:32
1. Read the plan file: `docs/work/active/{backlog_id}/plans/PLAN.md`
# Note: Does NOT say "Read work file first"
```

**Analysis:** The skill starts from the plan, never reading the work item that may contain operator decision requirements. Even if work item had structured decisions, they would be ignored.

**Implication:** Add AMBIGUITY phase to plan-authoring-cycle that reads work item FIRST and blocks if `operator_decisions` field has unresolved items.

#### Finding 3: Plan-Validation Has No Decision Check

**Evidence:**
```markdown
# plan-validation-cycle/SKILL.md:88-116 (VALIDATE Phase)
**Quality Checks:**
- Goal: Single sentence, measurable outcome
- Effort: Real numbers from file analysis
- Tests: Concrete assertions, not placeholders
# Note: No check for "Open Decisions resolved?"
```

**Analysis:** Validation is structural/quality only. A plan can pass all checks while having unresolved operator decisions.

**Implication:** Add to plan-validation-cycle VALIDATE phase: "Open Decisions section has no `[BLOCKED]` entries"

#### Finding 4: Defense in Depth Required

**Analysis:** Single gate is insufficient. E2-271 showed that even with good intentions, agents skip checks. Multiple gates provide redundancy:
1. **Work item gate** - Structured `operator_decisions` field
2. **Authoring gate** - AMBIGUITY phase reads work item first
3. **Validation gate** - Checks plan has no unresolved decisions
4. **Template gate** - "Open Decisions" section forces documentation

**Implication:** Implement all four gates (4 spawned work items).

---

## Design Outputs

### Schema Design: Work Item `operator_decisions` Field

```yaml
# Addition to work_item.md template frontmatter
operator_decisions:
  - question: "Implement modules or remove references?"
    options: ["implement", "remove"]
    resolved: false  # MUST be true before plan authoring can proceed
    chosen: null     # Filled when operator decides
```

### Schema Design: Plan "Open Decisions" Section

```markdown
## Open Decisions (MUST resolve before implementation)

<!-- If ANY decisions are unresolved, plan-validation-cycle will BLOCK -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| [From work item] | [A, B] | [BLOCKED] | [Why this choice] |
```

### Mechanism Design: Ambiguity Gating Flow

```
TRIGGER: Agent invokes plan-authoring-cycle

GATE 1 (AMBIGUITY Phase - NEW):
    1. Read work item: docs/work/active/{id}/WORK.md
    2. Check `operator_decisions` field
    3. IF any decision has `resolved: false`:
       BLOCK with message: "Unresolved decisions in work item. Ask operator."
       Present AskUserQuestion with options from work item
    4. ELSE: Proceed to ANALYZE phase

GATE 2 (AUTHOR Phase - Existing):
    5. Populate "Open Decisions" section in plan from work item decisions

GATE 3 (plan-validation-cycle VALIDATE Phase - Enhanced):
    6. Check "Open Decisions" section
    7. IF any row has `[BLOCKED]` in Chosen column:
       BLOCK with message: "Open decisions unresolved in plan."
    8. ELSE: Proceed to APPROVE

OUTCOME: Plan only proceeds to DO phase when all decisions resolved
```

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| 4 gates vs 1 | 4 gates (defense in depth) | Single gate can be bypassed; E2-271 proved agents skip checks |
| Structured field vs prose | Structured `operator_decisions` | Prose is ambiguous; structured fields can be machine-checked |
| BLOCK vs WARN | BLOCK | Warnings are ignored (L3 LLM Nature: "No internal friction") |
| New phase vs existing | New AMBIGUITY phase | Clean separation; doesn't overload ANALYZE |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

- [x] **E2-272: Add operator_decisions Field to Work Item Template**
  - Description: Add structured `operator_decisions` field to work_item.md template
  - Fixes: Finding 1 - no structured field for operator decisions
  - Spawned via: `/new-work E2-272 "Add operator_decisions Field to Work Item Template"`

- [x] **E2-273: Add Open Decisions Section to Implementation Plan Template**
  - Description: Add "Open Decisions" section to implementation_plan.md template
  - Fixes: Finding 1 - template doesn't surface work item ambiguity
  - Spawned via: `/new-work E2-273 "Add Open Decisions Section to Implementation Plan Template"`

- [x] **E2-274: Add AMBIGUITY Phase to plan-authoring-cycle**
  - Description: Add new phase that reads work item and blocks if unresolved decisions
  - Fixes: Finding 2 - plan-authoring doesn't read work item
  - Spawned via: `/new-work E2-274 "Add AMBIGUITY Phase to plan-authoring-cycle"`

- [x] **E2-275: Add Decision Check to plan-validation-cycle**
  - Description: Add check in VALIDATE phase for unresolved Open Decisions
  - Fixes: Finding 3 - validation has no decision check
  - Spawned via: `/new-work E2-275 "Add Decision Check to plan-validation-cycle"`

### Future (Requires more work first)

**None** - All 4 gates can be implemented independently.

### Implementation Order Recommendation

1. **E2-272** first (schema foundation)
2. **E2-273** next (template uses schema)
3. **E2-274** next (skill uses both)
4. **E2-275** last (validation uses all)

After all 4 complete, unblock E2-271 and resolve its operator decision.

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 175 | 2026-01-05 | HYPOTHESIZE | Started | Initial context and hypotheses |
| - | - | - | - | No additional sessions yet |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-HN have verdict | [ ] | |
| Evidence has sources | All findings have file:line or concept ID | [ ] | |
| Spawned items created | Items exist in backlog or via /new-* | [ ] | |
| Memory stored | ingester_ingest called, memory_refs populated | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | [Yes/No] | |
| Are all evidence sources cited with file:line or concept ID? | [Yes/No] | |
| Were all hypotheses tested with documented verdicts? | [Yes/No] | |
| Are spawned items created (not just listed)? | [Yes/No] | |
| Is memory_refs populated in frontmatter? | [Yes/No] | |

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete ALL items before /close -->

### Required (MUST complete)
- [ ] **Findings synthesized** - Answer to objective documented in Findings section
- [ ] **Evidence sourced** - All findings have file:line or concept ID citations
- [ ] **Hypotheses resolved** - All hypotheses have Confirmed/Refuted/Inconclusive verdict
- [ ] **Spawned items created** - Via /new-* commands with `spawned_by` field (or rationale if none)
- [ ] **Memory stored** - `ingester_ingest` called with findings summary
- [ ] **memory_refs populated** - Frontmatter updated with concept IDs
- [ ] **lifecycle_phase updated** - Set to `conclude`
- [ ] **Ground Truth Verification complete** - All items checked above

### Optional
- [ ] Design outputs documented (if applicable)
- [ ] Session progress updated (if multi-session)

---

## References

- [Spawned by: Session/Investigation/Work item that triggered this]
- [Related investigation 1]
- [Related ADR or spec]

---
