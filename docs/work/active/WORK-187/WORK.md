---
template: work_item
id: WORK-187
title: Fracture Implementation-Cycle SKILL.md into Phase Files
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-22
spawned_by: WORK-163
spawned_children: []
chapter: CH-062
arc: query
closed: '2026-02-22'
priority: medium
effort: small
traces_to:
- REQ-ASSET-001
- REQ-TEMPLATE-002
requirement_refs: []
source_files:
- .claude/skills/implementation-cycle/SKILL.md
acceptance_criteria:
- implementation-cycle SKILL.md reduced to slim router (~80 lines)
- 5 phase files created (PLAN.md, DO.md, CHECK.md, DONE.md, CHAIN.md)
- 2 reference files created (decisions.md, composition.md)
- Each phase file is self-contained (no cross-phase references)
- Existing tests still pass
blocked_by: []
blocks:
- WORK-188
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-22 10:15:01
  exited: '2026-02-22T11:12:25.289161'
artifacts: []
cycle_docs: {}
memory_refs:
- 85815
- 87398
- 87399
- 87400
- 87401
- 87402
- 87403
- 87404
- 87434
- 87435
extensions:
  epoch: E2.8
version: '2.0'
generated: 2026-02-22
last_updated: '2026-02-22T11:12:25.292699'
queue_history:
- position: ready
  entered: '2026-02-22T10:38:01.930578'
  exited: '2026-02-22T10:38:01.955489'
- position: working
  entered: '2026-02-22T10:38:01.955489'
  exited: '2026-02-22T11:12:25.289161'
- position: done
  entered: '2026-02-22T11:12:25.289161'
  exited: null
---
# WORK-187: Fracture Implementation-Cycle SKILL.md into Phase Files

---

## Context

Implementation-cycle SKILL.md is 21,500 chars / 468 lines — the largest ceremony contract. An agent executing a 30-line DONE phase loads all 468 lines. ADR-048 specifies phase-per-file fracturing to reduce token consumption by ~80%.

This work item covers the content restructuring: splitting the monolithic SKILL.md into a slim router + per-phase files + reference files. Hook-based auto-injection is handled by WORK-188.

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

- [x] Slim router SKILL.md (~80 lines: cycle diagram, phase table, "When to Use")
- [x] phases/PLAN.md (full PLAN behavioral contract)
- [x] phases/DO.md (full DO behavioral contract)
- [x] phases/CHECK.md (full CHECK behavioral contract)
- [x] phases/DONE.md (full DONE behavioral contract)
- [x] phases/CHAIN.md (full CHAIN behavioral contract)
- [x] reference/decisions.md (design decisions, rationale)
- [x] reference/composition.md (composition map, quick reference)
- [x] All existing tests pass (1589 passed, 0 failed, 8 skipped — S421)

---

## History

### 2026-02-22 - Created (Session 420)
- Spawned from WORK-163 (Progressive Contracts design)
- ADR-048 specifies the fracturing pattern

---

## References

- @docs/ADR/ADR-048-progressive-contracts-phase-per-file-skill-fracturing.md
- @docs/work/active/WORK-163/WORK.md
- Memory: 85815 (context-switching token cost)
