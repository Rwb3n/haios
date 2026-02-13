---
template: work_item
id: WORK-139
title: Fix close-epoch-ceremony Stale File-Move Documentation
type: bugfix
status: complete
owner: Hephaestus
created: 2026-02-12
spawned_by: null
spawned_children: []
chapter: null
arc: null
closed: '2026-02-13'
priority: low
effort: small
traces_to: []
requirement_refs: []
source_files:
- .claude/skills/close-epoch-ceremony/SKILL.md
acceptance_criteria:
- close-epoch-ceremony SKILL.md no longer references mv or file moves for work items
- ARCHIVE phase documents ADR-041 status-over-location approach
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-12 22:40:28
  exited: '2026-02-13T08:38:45.101186'
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-02-12
last_updated: '2026-02-13T08:38:45.104264'
queue_history:
- position: done
  entered: '2026-02-13T08:38:45.101186'
  exited: null
---
# WORK-139: Fix close-epoch-ceremony Stale File-Move Documentation

---

## Context

close-epoch-ceremony SKILL.md ARCHIVE phase documents `mv docs/work/active/* docs/work/archive/{epoch_id}/` which contradicts ADR-041 (status over location). Work items stay in `docs/work/active/` and `status: complete` determines their state, not directory path. This stale documentation actively misled the agent during S358 E2.5 closure — operator had to intervene.

---

## Deliverables

- [ ] Update close-epoch-ceremony SKILL.md ARCHIVE phase to reflect ADR-041
- [ ] Remove all `mv` and file-move references from the skill
- [ ] Add note about ADR-041 status-over-location principle

---

## History

### 2026-02-12 - Created (Session 358)
- Agent proposed moving 116 work items during E2.5 closure
- Operator corrected: ADR-041 says status over location

---

## References

- @.claude/skills/close-epoch-ceremony/SKILL.md
- ADR-041: Status over location
