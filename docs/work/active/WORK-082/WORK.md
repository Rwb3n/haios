---
template: work_item
id: WORK-082
title: Epistemic Review Ceremony After Investigation Closure
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-02
spawned_by: INV-068
chapter: CH-041
arc: observability
closed: '2026-02-14'
priority: medium
effort: medium
traces_to:
- REQ-CEREMONY-004
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables:
- WORK-081
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-02 19:57:56
  exited: '2026-02-14T17:28:18.053250'
artifacts: []
cycle_docs: {}
memory_refs:
- 85419
- 85420
- 85421
- 85422
- 85423
- 85424
- 85434
extensions:
  epoch: E2.6
version: '2.0'
generated: 2026-02-02
last_updated: '2026-02-14T17:28:18.058281'
queue_history:
- position: ready
  entered: '2026-02-14T17:18:37.861184'
  exited: '2026-02-14T17:18:43.418878'
- position: working
  entered: '2026-02-14T17:18:43.418878'
  exited: '2026-02-14T17:28:18.053250'
- position: done
  entered: '2026-02-14T17:28:18.053250'
  exited: null
queue_position: done
cycle_phase: done
---
# WORK-082: Epistemic Review Ceremony After Investigation Closure

---

## Context

**Problem:** Investigation closure (investigation-cycle CONCLUDE phase) produces findings but doesn't systematically surface "what do we actually know now?" before spawned implementation work begins. The agent jumps from findings → spawned work item without explicit epistemic review.

**Evidence (Session 292 - INV-068):** After closing INV-068, operator asked "what's your epistemy for WORK-081?" Agent had to manually produce:
- KNOWN (facts verified from files)
- INFERRED (reasoned from facts)
- UNKNOWN (explicit gaps)
- RISKS
- READINESS ASSESSMENT

This review surfaced 5 explicit unknowns that need resolution before implementation. Without the prompt, agent would have proceeded to `/implement WORK-081` with implicit assumptions.

**Root Cause:** Investigation-cycle CONCLUDE phase captures findings and spawns work, but doesn't force the agent to distinguish between facts/inferences/unknowns. The epistemic discipline exists (in output-style.json) but isn't enforced at the investigation→implementation boundary.

**Solution:** Add epistemic-review ceremony as bridge between investigation-cycle CONCLUDE and spawned implementation work. Three questions:
1. What do you KNOW? (verified facts with sources)
2. What did you INFER? (reasoned conclusions)
3. What is UNKNOWN? (explicit gaps needing resolution)

**Alignment:**
- L3.2: Evidence Over Assumption - requires distinguishing facts from inferences
- S20: Tight phase (high pressure) - forces commitment to epistemic state
- E2.4 Decision 4: Critique as Hard Gate - epistemic review is pre-implementation critique

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning)

     These checkboxes are the SOURCE OF TRUTH for work completion.

     During CHECK phase of implementation-cycle:
     - Agent MUST read this section
     - Agent MUST verify EACH checkbox can be marked complete
     - If ANY deliverable is incomplete, work is NOT done

     "Tests pass" ≠ "Deliverables complete"
     Tests verify code works. Deliverables verify scope is complete.

     NOTE (WORK-001): Acceptance criteria are in frontmatter (machine-parseable).
     Deliverables are implementation outputs, not requirements.
-->

- [x] Determine ceremony exit point (within CONCLUDE vs after vs at implementation entry)
- [x] Determine exit behavior when unknowns are significant (block spawn, proceed with gaps, spawn follow-up investigation)
- [x] Define ceremony structure (questions, format, gate conditions)
- [x] Analyze interaction with existing ceremonies (observation-capture, critique-agent)
- [x] Spawned implementation work item(s) for ceremony creation

---

## Findings

### Hypothesis Verdicts

| Hypothesis | Verdict | Confidence | Key Evidence |
|-----------|---------|------------|--------------|
| H1: Inside CONCLUDE as mandatory sub-step | Confirmed | High | CONCLUDE already has the insertion point; standalone ceremony loses investigation context |
| H2: Standalone bridge skill | Refuted | High | Context loss fatal; epistemic review needs investigation findings in-context |
| H3: Gate-with-escape (three-level verdict) | Confirmed | High | S292 unknowns weren't all blocking; L3.6 Graceful Degradation; L3.4 Duties Separated |
| H4: K/I/U + verdict structure | Confirmed (refined) | High | Output-style already defines K/I/U; RISKS subsumed by UNKNOWN impact; READINESS = verdict |

### Design

**Location:** Inside investigation-cycle CONCLUDE phase, between "synthesize answer" and "spawn work items."

**Structure:**
- Three categories: KNOWN (facts + citations), INFERRED (reasoning chains), UNKNOWN (gaps + impact)
- Three-level verdict: PROCEED / DEFER / INVESTIGATE-MORE
- DEFER presents K/I/U to operator via AskUserQuestion

**Interactions:**
- critique-agent: No overlap (plans vs findings)
- retro-cycle: No overlap (work quality vs knowledge state)
- observation-capture: Partially subsumed (unknowns surface same gaps)

### Spawned Work

| ID | Title | spawned_by |
|----|-------|------------|
| WORK-151 | Implement Epistemic Review Step in Investigation CONCLUDE Phase | WORK-082 |

---

## History

### 2026-02-02 - Created (Session 292)
- Spawned from operator feedback after INV-068 closure
- Operator asked "what's your epistemy for WORK-081?" revealing gap
- Manual epistemic review surfaced 5 explicit unknowns

### 2026-02-14 - Investigation Complete (Session 372)
- EXPLORE: Read INV-068, WORK-081, investigation-cycle SKILL, CONCLUDE template, retro-cycle, close-work-cycle, critique-agent, L4 requirements, memory (84711, 85389)
- HYPOTHESIZE: 4 hypotheses from evidence (location, structure, gate behavior, K/I/U format)
- VALIDATE: H1 confirmed, H2 refuted, H3 confirmed, H4 confirmed with refinement
- CONCLUDE: Design synthesized, WORK-151 spawned for implementation
- Key finding: Epistemic review is a CONCLUDE sub-step, not a standalone ceremony

---

## References

- @docs/work/active/INV-068/WORK.md (triggering investigation)
- @docs/work/active/WORK-081/WORK.md (spawned work that needed epistemic review)
- @docs/work/active/WORK-151/WORK.md (spawned implementation)
- @.claude/skills/investigation-cycle/SKILL.md (CONCLUDE phase to modify)
- @.claude/skills/retro-cycle/SKILL.md (ceremony pattern reference)
- @.claude/agents/critique-agent.md (verdict pattern reference)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-004)
- L3.2: Evidence Over Assumption (manifesto principle)
- L3.6: Graceful Degradation (verdict design)
- L3.4: Duties Are Separated (DEFER to operator)
