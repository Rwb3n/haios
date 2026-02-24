---
template: work_item
id: WORK-213
title: "Retro-Cycle Phase Reordering: COMMIT before EXTRACT"
type: refactor
status: active
owner: Hephaestus
created: 2026-02-24
spawned_by: WORK-164
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: medium
traces_to:
  - REQ-CEREMONY-002
requirement_refs: []  # DEPRECATED: use traces_to instead
source_files:
  - .claude/skills/retro-cycle/SKILL.md
acceptance_criteria:
  - "Retro-cycle phase order is REFLECT → DERIVE → COMMIT → EXTRACT"
  - "COMMIT stores observations + K/S/S to memory, returns concept IDs"
  - "EXTRACT creates work items referencing stored memory concept IDs"
  - "EXTRACT no longer classifies observations (DERIVE handles this)"
  - "Context alert threshold changed to 15%"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-24T10:57:10
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
  - 88137
  - 88138
  - 88139
extensions: {}
version: "2.0"
generated: 2026-02-24
last_updated: 2026-02-24T10:57:10
---
# WORK-213: Retro-Cycle Phase Reordering: COMMIT before EXTRACT

---

## Context

S439 retro-cycle revealed phase ordering issue. Current: REFLECT → DERIVE → EXTRACT → COMMIT. EXTRACT (haiku subagent) used 37K tokens, 146s, 14 tool calls for marginal signal over DERIVE — it reclassifies observations that DERIVE already synthesized into K/S/S. COMMIT stores everything at the end, meaning EXTRACT can't reference memory IDs.

Operator directive: reorder to REFLECT → DERIVE → COMMIT → EXTRACT. COMMIT stores observations + K/S/S immediately (they're complete cognitive outputs). EXTRACT then creates work items that reference stored memory concept IDs — traceable from birth. Clean separation: DERIVE = insights, COMMIT = persistence, EXTRACT = operationalize as work items.

Also: context alert threshold should be 15% (currently 19% triggers). 10% is close territory, 5% is emergency stop.

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

- [ ] retro-cycle SKILL.md updated with new phase order
- [ ] COMMIT phase moved before EXTRACT
- [ ] EXTRACT phase redefined: creates work items with mem ID references
- [ ] Context alert threshold set to 15% in hooks

---

## History

### 2026-02-24 - Created (Session 439)
- Initial creation

---

## References

- @.claude/skills/retro-cycle/SKILL.md
- Memory: 88137-88143 (S439 operator directive on phase reordering)
- S439 retro evidence: EXTRACT haiku 37K tokens / 14 tool calls for marginal signal
