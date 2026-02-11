---
template: work_item
id: WORK-118
title: Implement CeremonyLifecycleDistinction (CH-013)
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-11
spawned_by: null
chapter: CH-013
arc: ceremonies
closed: '2026-02-11'
priority: medium
effort: medium
traces_to:
- REQ-CEREMONY-003
requirement_refs: []
source_files:
- .claude/haios/modules/cycle_runner.py
- .claude/haios/modules/ceremony_runner.py
- .claude/skills/
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-11 18:54:12
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 84841
- 84842
- 84843
- 84844
- 84845
- 84846
- 84851
- 84852
extensions: {}
version: '2.0'
generated: 2026-02-11
last_updated: '2026-02-11T19:33:23.554001'
---
# WORK-118: Implement CeremonyLifecycleDistinction (CH-013)

---

## Context

CycleRunner currently handles both lifecycles (artifact production) and ceremonies (state changes) with no code distinction. The `-cycle` suffix is used for both true lifecycles (implementation-cycle, investigation-cycle) and ceremonies (close-work-cycle, checkpoint-cycle, work-creation-cycle). REQ-CEREMONY-003 requires ceremonies to be distinct from lifecycles: lifecycles transform work (WHAT), ceremonies govern transitions (WHEN). CH-013 defines the separation: a new CeremonyRunner class, `type: lifecycle|ceremony` in skill frontmatter, and renaming misnamed `-cycle` ceremonies to `-ceremony`.

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

- [x] CeremonyRunner class in `.claude/haios/modules/ceremony_runner.py` (separate from CycleRunner)
- [x] CeremonyResult dataclass with state-change semantics (distinct from LifecycleOutput)
- [x] `type: lifecycle|ceremony` field added to skill frontmatter for all skills (33/33)
- [x] CYCLE_PHASES split: lifecycle phases stay in CycleRunner, ceremony phases move to CeremonyRunner
- [ ] ~~Rename ceremony skills~~ DEFERRED to WORK-119 (391 refs across 107 files, operator decision S342)
- [ ] ~~Update all consumers of renamed skills~~ DEFERRED to WORK-119
- [x] Unit tests for CeremonyRunner (12 tests, all passing)
- [x] Unit tests verifying CycleRunner no longer handles ceremony phases

---

## History

### 2026-02-11 - Created (Session 342)
- Initial creation

---

## References

- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-013-CeremonyLifecycleDistinction.md
- @.claude/haios/modules/cycle_runner.py
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-003)
