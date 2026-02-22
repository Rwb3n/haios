---
template: work_item
id: WORK-163
title: Progressive Contracts
type: design
status: complete
owner: Hephaestus
created: 2026-02-17
spawned_by: Session-394-decomposition
spawned_children:
- WORK-187
- WORK-188
chapter: CH-062
arc: query
closed: '2026-02-22'
priority: medium
effort: medium
traces_to:
- REQ-ASSET-001
requirement_refs: []
source_files:
- .claude/skills/implementation-cycle/SKILL.md
- .claude/skills/investigation-cycle/SKILL.md
acceptance_criteria:
- Contract progressive disclosure pattern designed
- Agent reads summary first, details on demand
- Injection mechanism designed (hook-based auto-injection)
- Token audit completed with savings projections
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-17 22:08:08
  exited: '2026-02-22T10:19:59.467650'
artifacts: []
cycle_docs: {}
memory_refs:
- 85815
- 87396
extensions:
  epoch: E2.8
version: '2.0'
generated: 2026-02-17
last_updated: '2026-02-22T10:19:59.470681'
queue_history:
- position: ready
  entered: '2026-02-22T09:32:28.173999'
  exited: '2026-02-22T09:32:38.903216'
- position: working
  entered: '2026-02-22T09:32:38.903216'
  exited: '2026-02-22T10:19:59.467650'
- position: done
  entered: '2026-02-22T10:19:59.467650'
  exited: null
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

- [x] Current contract token audit (size per SKILL.md, per phase)
- [x] Progressive disclosure pattern design (ADR-048)
- [ ] ~~Prototype for one ceremony~~ — spawned as WORK-187 (implementation) + WORK-188 (hooks)
- [x] Design document or ADR (ADR-048)

---

## History

### 2026-02-17 - Created (Session 394)
- Spawned during E2.8 arc decomposition
- CH-062 ProgressiveContracts

### 2026-02-22 - Design Complete (Session 420)
- Token audit: top 7 skills = ~111K chars, implementation-cycle = 21.5K (largest)
- Evaluated 3 options: phase-per-file fracturing, engine-function loader, inline collapsible
- Operator selected: phase-per-file fracturing with dual hook auto-injection (PostToolUse + UserPromptSubmit)
- ADR-048 written and approved
- Spawned: WORK-187 (fracture implementation-cycle), WORK-188 (hook auto-injection)

---

## References

- @.claude/haios/epochs/E2_8/arcs/query/ARC.md
- @docs/ADR/ADR-048-progressive-contracts-phase-per-file-skill-fracturing.md
- Memory: 85815 (Dimension 2: context switching)
