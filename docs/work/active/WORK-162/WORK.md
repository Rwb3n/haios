---
template: work_item
id: WORK-162
title: "Coldstart Context Injection"
type: design
status: active
owner: Hephaestus
created: 2026-02-17
spawned_by: Session-394-decomposition
spawned_children: []
chapter: CH-061
arc: call
closed: null
priority: high
effort: medium
traces_to:
  - REQ-CONFIG-001
requirement_refs: []
source_files:
  - .claude/skills/coldstart/SKILL.md
  - .claude/haios/modules/coldstart_orchestrator.py
acceptance_criteria:
  - "Minimum viable context contract defined: identity + mission + prior + work + operational HOW"
  - "Coldstart skill has ZERO Read instructions — all context injected by orchestrator"
  - "Operational patterns (module paths, Tier model, recipe usage) injected, not manual read"
  - "Tiered coldstart system designed (full, light, minimal) with criteria for each"
  - "After coldstart, agent can execute work without reading any additional files"
  - "S393/S394 evidence addressed: 200k agent operational failure after coldstart"
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
  - 84835
  - 84836
  - 85459
extensions:
  epoch: E2.8
version: "2.0"
generated: 2026-02-17
last_updated: 2026-02-17T22:08:08
---
# WORK-162: Lightweight Coldstart

---

## Context

Coldstart is overkill for housekeeping sessions (mem:84835, 84836). Most tokens are spent on context loading (mem:85459). A full coldstart loads identity, session, work, epoch, arcs — even when the session is just fixing a typo or updating docs.

**Proposed tiers:**
- **Full:** New epoch/arc work — loads everything (identity, session, epoch, arcs, memory refs)
- **Light:** Continuation of prior session — loads session context + active work item only
- **Minimal:** Housekeeping — loads config + session number only, skips survey-cycle

Design phase: define the tiers, criteria, and progressive loading strategy.

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

- [ ] Tier definitions (full, light, minimal) with criteria
- [ ] Token budget analysis for each tier
- [ ] Progressive loading strategy (load more on demand)
- [ ] Interface design for tier selection (argument to /coldstart or auto-detect)
- [ ] Design document or ADR

---

## History

### 2026-02-17 - Created (Session 394)
- Spawned during E2.8 arc decomposition
- CH-061 LightweightColdstart

---

## References

- @.claude/haios/epochs/E2_8/arcs/query/ARC.md
- @.claude/skills/coldstart/SKILL.md
- Memory: 84835, 84836 (coldstart overhead), 85459 (most tokens on context loading)
