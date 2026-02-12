---
template: work_item
id: WORK-137
title: Implement Spawn Ceremony (CH-017)
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-12
spawned_by: null
chapter: CH-017
arc: ceremonies
closed: '2026-02-12'
priority: medium
effort: medium
traces_to:
- REQ-CEREMONY-001
- REQ-CEREMONY-002
requirement_refs: []
source_files:
- .claude/skills/spawn-work-ceremony/SKILL.md
- .claude/haios/modules/work_engine.py
- .claude/haios/lib/scaffold.py
acceptance_criteria:
- Spawn ceremony skill de-stubbed with working implementation
- spawned_from field tracked in child WORK.md
- spawned_children field tracked in parent WORK.md
- SpawnedWork event logged to governance events
- Lineage queryable via WorkEngine
- Unit tests pass for spawn ceremony
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-12 21:28:40
  exited: '2026-02-12T21:55:22.392334'
artifacts: []
cycle_docs: {}
memory_refs:
- 85030
- 85031
- 85032
- 85033
- 85034
extensions: {}
version: '2.0'
generated: 2026-02-12
last_updated: '2026-02-12T21:55:43.465424'
queue_history:
- position: done
  entered: '2026-02-12T21:55:22.392334'
  exited: null
---
# WORK-137: Implement Spawn Ceremony (CH-017)

---

## Context

Work creation currently lacks parent-child lineage tracking. The `spawned_by` field references chapters, not work items. When work completes and spawns follow-on tasks (e.g., investigation spawns implementation), there is no governed ceremony and no bidirectional link between parent and child. This is the last chapter (CH-017) in the ceremonies arc, which is the final active arc in E2.5. Completing it unlocks E2.5 exit criteria verification.

**What exists:** spawn-work-ceremony skill (stub), work-creation-cycle, `spawned_by` field (chapter ref only).
**What's missing:** `spawned_from` field (parent work item), `spawned_children` field, SpawnedWork event, `get_work_lineage()`, de-stubbed ceremony implementation.

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

- [x] De-stub spawn-work-ceremony SKILL.md with full ceremony logic
- [x] Verify `spawned_by` field handles parent work item IDs (existing field; `spawned_from` per CH-017 maps to `spawned_by`)
- [x] Add `spawned_children` field to work_item template and WorkEngine parsing
- [x] Implement parent update (append child ID to parent's spawned_children)
- [x] Log SpawnWork event to governance-events.jsonl
- [x] Create REFS.md portal for spawned child items (structural parity with WorkEngine.create_work)
- [x] Add `get_work_lineage()` method to WorkEngine
- [x] Unit tests for spawn ceremony (contract validation, lineage tracking, event logging)
- [x] Integration test: spawn from parent, verify bidirectional lineage

---

## History

### 2026-02-12 - Created (Session 357)
- Initial creation

---

## References

- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-017-SpawnCeremony.md
- @.claude/skills/spawn-work-ceremony/SKILL.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-001, REQ-CEREMONY-002)
- @.claude/haios/epochs/E2_5/arcs/queue/CH-010-QueueCeremonies.md (intake ceremony pattern)
