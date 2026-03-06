---
template: work_item
id: WORK-242
title: "Remove plan status double-update from impl-cycle DONE phase"
type: implementation
status: active
owner: Hephaestus
created: 2026-03-06
spawned_by: WORK-238
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: small
traces_to:
- REQ-CEREMONY-002
requirement_refs: []
source_files:
- .claude/skills/implementation-cycle/phases/DONE.md
acceptance_criteria:
- "Plan status update (step 2) removed from DONE.md"
- "DONE.md retains WHY capture, docs update, and git commit steps"
- "close-work ARCHIVE remains the sole owner of plan status -> complete"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-03-06T23:42:12
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 89334
- 89337
extensions: {}
version: "2.0"
generated: 2026-03-06
last_updated: 2026-03-06T23:42:12
---
# WORK-242: Remove plan status double-update from impl-cycle DONE phase

---

## Context

WORK-238 investigation (S465) confirmed plan status is set to complete twice: once in impl-cycle DONE.md:16 and again in close-work ARCHIVE (SKILL.md:209, with "(if not already)" qualifier). The ARCHIVE step is the authoritative closure action via hierarchy_close_work. DONE's plan update is redundant.

---

## Deliverables

- [ ] Remove "Update plan status: status: complete" (step 2) from DONE.md
- [ ] Renumber remaining DONE steps (1, 3, 4 -> 1, 2, 3)
- [ ] Update DONE exit criteria to remove "Plan marked complete"
- [ ] Verify close-work ARCHIVE still handles plan status (no change needed there)

---

## References

- @docs/work/active/WORK-238/investigations/001-done-chain-duplication.md
- @.claude/skills/implementation-cycle/phases/DONE.md
- @.claude/skills/close-work-cycle/SKILL.md (ARCHIVE phase, line 209)
