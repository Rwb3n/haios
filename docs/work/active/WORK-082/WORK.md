---
template: work_item
id: WORK-082
title: Epistemic Review Ceremony After Investigation Closure
type: investigation
status: active
owner: Hephaestus
created: 2026-02-02
spawned_by: INV-068
chapter: null
arc: flow
closed: null
priority: medium
effort: medium
traces_to: []
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
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-02-02
last_updated: '2026-02-02T20:02:25'
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

- [ ] Determine ceremony exit point (within CONCLUDE vs after vs at implementation entry)
- [ ] Determine exit behavior when unknowns are significant (block spawn, proceed with gaps, spawn follow-up investigation)
- [ ] Define ceremony structure (questions, format, gate conditions)
- [ ] Analyze interaction with existing ceremonies (observation-capture, critique-agent)
- [ ] Spawned implementation work item(s) for ceremony creation

---

## History

### 2026-02-02 - Created (Session 292)
- Spawned from operator feedback after INV-068 closure
- Operator asked "what's your epistemy for WORK-081?" revealing gap
- Manual epistemic review surfaced 5 explicit unknowns

---

## References

- @docs/work/active/INV-068/WORK.md (triggering investigation)
- @docs/work/active/WORK-081/WORK.md (spawned work that needed epistemic review)
- @.claude/skills/investigation-cycle/SKILL.md (CONCLUDE phase to modify)
- @.claude/skills/observation-capture-cycle/ (parallel ceremony pattern)
- L3.2: Evidence Over Assumption (manifesto principle)
