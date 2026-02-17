---
template: work_item
id: WORK-165
title: "Infrastructure Ceremonies"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-17
spawned_by: Session-394-decomposition
spawned_children: []
chapter: CH-064
arc: discover
closed: null
priority: medium
effort: medium
traces_to:
  - REQ-CEREMONY-001
  - REQ-CEREMONY-002
requirement_refs: []
source_files:
  - .claude/skills/open-epoch-ceremony/SKILL.md
  - .claude/skills/close-epoch-ceremony/SKILL.md
  - .claude/skills/close-arc-ceremony/SKILL.md
  - .claude/skills/close-chapter-ceremony/SKILL.md
acceptance_criteria:
  - "Open-epoch-ceremony skill verified functional (created S393)"
  - "Ceremony skills discoverable via infrastructure (not CLAUDE.md listing)"
  - "Ceremony loop standardized (open/close pairs for epoch, arc, chapter)"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-02-17T22:08:08
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
  - 85098
  - 85108
extensions:
  epoch: E2.8
  note: "open-epoch-ceremony already created in S393"
version: "2.0"
generated: 2026-02-17
last_updated: 2026-02-17T22:08:08
---
# WORK-165: Infrastructure Ceremonies

---

## Context

Ceremonies should be discoverable via infrastructure, not by an agent reading CLAUDE.md or memorizing skill names. The open-epoch-ceremony skill was created in S393, completing the ceremony loop (open + close for epoch, arc, chapter, work).

This work item ensures:
1. The ceremony loop is standardized and complete
2. Ceremonies are discoverable via the same infrastructure as agent cards
3. Open-epoch-ceremony (created S393) is verified functional

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

- [ ] Verify open-epoch-ceremony functional
- [ ] Audit ceremony loop completeness (open/close pairs)
- [ ] Ceremony infrastructure discovery mechanism
- [ ] Tests for ceremony discovery

---

## History

### 2026-02-17 - Created (Session 394)
- Spawned during E2.8 arc decomposition
- CH-064 InfrastructureCeremonies

---

## References

- @.claude/haios/epochs/E2_8/arcs/discover/ARC.md
- @.claude/skills/open-epoch-ceremony/SKILL.md
- Memory: 85098, 85108 (WORK-143 triage consumer)
