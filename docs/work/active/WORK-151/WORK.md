---
template: work_item
id: WORK-151
title: Implement Epistemic Review Step in Investigation CONCLUDE Phase
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-14
spawned_by: WORK-082
spawned_children: []
chapter: CH-041
arc: observability
closed: '2026-02-15'
priority: medium
effort: small
traces_to:
- REQ-CEREMONY-004
requirement_refs: []
source_files:
- .claude/skills/investigation-cycle/SKILL.md
- .claude/templates/investigation/CONCLUDE.md
acceptance_criteria:
- investigation-cycle SKILL.md CONCLUDE phase includes epistemic review step between
  findings synthesis and spawn
- CONCLUDE.md template output contract includes K/I/U section
- Epistemic review has three-level verdict (PROCEED/DEFER/INVESTIGATE-MORE)
- DEFER verdict presents K/I/U to operator via AskUserQuestion
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-14 17:22:16
  exited: '2026-02-15T20:25:34.122566'
artifacts: []
cycle_docs: {}
memory_refs:
- 85437
- 85438
- 85446
extensions:
  epoch: E2.6
version: '2.0'
generated: 2026-02-14
last_updated: '2026-02-15T20:25:34.126575'
queue_history:
- position: ready
  entered: '2026-02-14T17:39:31.263665'
  exited: '2026-02-14T17:39:31.289598'
- position: working
  entered: '2026-02-14T17:39:31.289598'
  exited: '2026-02-15T20:25:34.122566'
- position: done
  entered: '2026-02-15T20:25:34.122566'
  exited: null
---
# WORK-151: Implement Epistemic Review Step in Investigation CONCLUDE Phase

---

## Context

**Problem:** Investigation-cycle CONCLUDE phase produces findings and spawns implementation work, but doesn't force the agent to distinguish between facts/inferences/unknowns. The epistemic discipline exists in output-style.json but isn't enforced at the investigation→implementation boundary.

**Root Cause:** No mandatory step between "findings synthesized" and "spawn work items" in CONCLUDE phase.

**Solution (from WORK-082 investigation):** Add epistemic review as mandatory CONCLUDE sub-step:
1. Categorize findings into KNOWN / INFERRED / UNKNOWN
2. Per-unknown: impact assessment
3. Render verdict: PROCEED / DEFER / INVESTIGATE-MORE
4. If DEFER: present to operator via AskUserQuestion

**Design decisions (WORK-082):**
- Inside CONCLUDE, not a standalone ceremony (requires investigation context)
- Three-level verdict, not binary block (aligns with L3.6 Graceful Degradation)
- K/I/U structure with evidence citations (aligns with L3.2 Evidence Over Assumption)

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

- [ ] investigation-cycle SKILL.md updated: CONCLUDE phase step 3 (epistemic review) added between findings synthesis and spawn
- [ ] CONCLUDE.md template updated: Epistemic Review section in output contract with K/I/U table and verdict
- [ ] Verdict rules documented: PROCEED/DEFER/INVESTIGATE-MORE with conditions
- [ ] DEFER behavior implemented: AskUserQuestion with K/I/U summary for operator decision

---

## History

### 2026-02-14 - Created (Session 372)
- Spawned from WORK-082 investigation (epistemic review ceremony design)
- Design: inside CONCLUDE, not standalone ceremony
- Three-level verdict (PROCEED/DEFER/INVESTIGATE-MORE)
- K/I/U categories with evidence citations

---

## References

- @docs/work/active/WORK-082/WORK.md (spawning investigation)
- @.claude/skills/investigation-cycle/SKILL.md (primary artifact to modify)
- @.claude/templates/investigation/CONCLUDE.md (template to update)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-004)
- L3.2: Evidence Over Assumption
- L3.6: Graceful Degradation
