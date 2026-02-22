---
template: work_item
id: WORK-187
title: "Fracture Implementation-Cycle SKILL.md into Phase Files"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-22
spawned_by: WORK-163
spawned_children: []
chapter: CH-062
arc: query
closed: null
priority: medium
effort: small
traces_to:
- REQ-ASSET-001
requirement_refs: []
source_files:
- .claude/skills/implementation-cycle/SKILL.md
acceptance_criteria:
- "implementation-cycle SKILL.md reduced to slim router (~80 lines)"
- "5 phase files created (PLAN.md, DO.md, CHECK.md, DONE.md, CHAIN.md)"
- "2 reference files created (decisions.md, composition.md)"
- "Each phase file is self-contained (no cross-phase references)"
- "Existing tests still pass"
blocked_by: []
blocks:
- WORK-188
enables:
- WORK-188
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-22T10:15:01
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 85815
extensions:
  epoch: E2.8
version: "2.0"
generated: 2026-02-22
last_updated: 2026-02-22T10:15:01
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

- [ ] Slim router SKILL.md (~80 lines: cycle diagram, phase table, "When to Use")
- [ ] phases/PLAN.md (full PLAN behavioral contract)
- [ ] phases/DO.md (full DO behavioral contract)
- [ ] phases/CHECK.md (full CHECK behavioral contract)
- [ ] phases/DONE.md (full DONE behavioral contract)
- [ ] phases/CHAIN.md (full CHAIN behavioral contract)
- [ ] reference/decisions.md (design decisions, rationale)
- [ ] reference/composition.md (composition map, quick reference)
- [ ] All existing tests pass

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
