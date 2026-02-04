---
template: work_item
id: WORK-066
title: Queue Position Field and Cycle Wiring Implementation
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-01
spawned_by: WORK-016
chapter: CH-007
arc: queue
closed: '2026-02-04'
priority: high
effort: large
traces_to:
- REQ-QUEUE-001
source_files:
- docs/specs/TRD-WORK-ITEM-UNIVERSAL.md
- .claude/haios/modules/governance_layer.py
- .claude/haios/modules/work_engine.py
- .claude/templates/work_item.md
- .claude/skills/survey-cycle/SKILL.md
- .claude/skills/close-work-cycle/close-work-cycle.md
acceptance_criteria:
- queue_position field added to TRD-WORK-ITEM-UNIVERSAL
- survey-cycle sets queue_position to in_progress on selection
- close-work-cycle sets queue_position to done on closure
- Single in_progress constraint enforced in survey-cycle
- current_node aligned to GovernanceLayer vocabulary
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-01 20:56:18
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82952
- 82953
- 82954
- 83938
- 83939
- 83940
- 83941
- 83942
- 83943
- 83944
- 83945
- 83946
- 83947
- 83948
- 83949
operator_decisions:
- question: Should current_node be renamed to cycle_phase?
  options:
  - rename to cycle_phase
  - keep current_node
  resolved: true
  chosen: rename to cycle_phase
  rationale: Better semantic clarity, aligns with four-dimensional model terminology
extensions:
  epoch: E2.5
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-04T21:17:34.827099'
queue_position: backlog
cycle_phase: backlog
---
# WORK-066: Queue Position Field and Cycle Wiring Implementation

@docs/work/active/WORK-016/WORK.md
@docs/work/active/WORK-065/WORK.md

---

## Context

**Problem:** WORK-016 and WORK-065 investigations concluded that `current_node` conflates queue position and cycle phase, resulting in 94% of work items stuck at `backlog` regardless of status.

**Decision:** Implement four-dimensional work item state model:
1. `status` - ADR-041 authoritative (unchanged)
2. `queue_position` - NEW field for work selection pipeline
3. `cycle_phase` - RENAME from current_node, align to GovernanceLayer
4. `activity_state` - E2.4 (unchanged, derived from cycle/phase)

---

## Deliverables

- [ ] **TRD Update** - Add `queue_position` field to TRD-WORK-ITEM-UNIVERSAL
- [ ] **Template Update** - Add `queue_position` to work_item.md template
- [ ] **Survey-cycle Wiring** - Set `queue_position: in_progress` on work selection
- [ ] **Close-work-cycle Wiring** - Set `queue_position: done` on closure
- [ ] **Single In_Progress Constraint** - Gate in survey-cycle blocking new selection if in_progress exists
- [ ] **Vocabulary Alignment** - Align current_node to GovernanceLayer values (optional: rename to cycle_phase)

---

## Implementation Plan

### Phase 1: Schema Changes
1. Update TRD-WORK-ITEM-UNIVERSAL with `queue_position` field
2. Update work_item.md template
3. Update WorkEngine._parse_work_file() to read queue_position
4. Update scaffold.py to include queue_position

### Phase 2: Cycle Wiring
1. Survey-cycle: After work selection, set queue_position: in_progress
2. Close-work-cycle: In ARCHIVE phase, set queue_position: done

### Phase 3: Constraint Enforcement
1. Survey-cycle: Before selection, check if any item has queue_position: in_progress
2. If yes, block and report current in_progress item
3. Gate can be bypassed with explicit operator override

---

## History

### 2026-02-01 - Created (Session 276)
- Spawned from WORK-016 decision
- Implements four-dimensional model from WORK-065

---

## References

- @docs/work/active/WORK-016/WORK.md (investigation decision)
- @docs/work/active/WORK-065/WORK.md (four-dimensional model design)
- @docs/specs/TRD-WORK-ITEM-UNIVERSAL.md (target spec)
- @.claude/haios/modules/governance_layer.py:59-68 (VALID_TRANSITIONS)
