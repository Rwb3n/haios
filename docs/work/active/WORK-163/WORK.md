---
template: work_item
id: WORK-163
title: "Progressive Contracts"
type: design
status: active
owner: Hephaestus
created: 2026-02-17
spawned_by: Session-394-decomposition
spawned_children: []
chapter: CH-062
arc: query
closed: null
priority: medium
effort: medium
traces_to:
  - REQ-ASSET-001
requirement_refs: []
source_files:
  - .claude/skills/implementation-cycle/SKILL.md
  - .claude/skills/investigation-cycle/SKILL.md
acceptance_criteria:
  - "Contract progressive disclosure pattern designed"
  - "Agent reads summary first, details on demand"
  - "Contracts use engine functions for context retrieval"
  - "Reduced token consumption for ceremony phase transitions"
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
  - 85815
extensions:
  epoch: E2.8
version: "2.0"
generated: 2026-02-17
last_updated: 2026-02-17T22:08:08
---
# WORK-163: Progressive Contracts

---

## Context

Context switching between ceremony phases costs tokens with no work output (mem:85815). Current SKILL.md files are monolithic — the agent loads the entire ceremony contract even when it only needs one phase. Progressive disclosure means: load phase summary, expand details on demand.

**Design question:** How to restructure ceremony contracts so the agent reads only what it needs for the current phase, while maintaining the full contract for reference?

Options include: phase-per-file fracturing (like templates), inline progressive sections, or engine-function-driven phase loading.

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

- [ ] Current contract token audit (size per SKILL.md, per phase)
- [ ] Progressive disclosure pattern design
- [ ] Prototype for one ceremony (e.g., implementation-cycle)
- [ ] Design document or ADR

---

## History

### 2026-02-17 - Created (Session 394)
- Spawned during E2.8 arc decomposition
- CH-062 ProgressiveContracts

---

## References

- @.claude/haios/epochs/E2_8/arcs/query/ARC.md
- Memory: 85815 (Dimension 2: context switching)
