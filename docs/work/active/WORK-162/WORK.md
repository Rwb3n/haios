---
template: work_item
id: WORK-162
title: Coldstart Context Injection
type: design
status: complete
owner: Hephaestus
created: 2026-02-17
spawned_by: Session-394-decomposition
spawned_children: []
chapter: CH-061
arc: call
closed: '2026-02-20'
priority: high
effort: medium
traces_to:
- REQ-CONFIG-001
requirement_refs: []
source_files:
- .claude/commands/coldstart.md
- .claude/haios/lib/coldstart_orchestrator.py
acceptance_criteria:
- 'Minimum viable context contract defined: identity + mission + prior + work + operational
  HOW'
- Coldstart skill has ZERO Read instructions — all context injected by orchestrator
- Operational patterns (module paths, Tier model, recipe usage) injected, not manual
  read
- Tiered coldstart system designed (full, light, minimal) with criteria for each
- After coldstart, agent can execute work without reading any additional files
- 'S393/S394 evidence addressed: 200k agent operational failure after coldstart'
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-17 22:08:08
  exited: '2026-02-20T23:42:49.886633'
artifacts:
- docs/ADR/ADR-047-tiered-coldstart-context-injection.md
cycle_docs: {}
memory_refs:
- 84835
- 84836
- 85459
- 87131
extensions:
  epoch: E2.8
version: '2.0'
generated: 2026-02-17
last_updated: '2026-02-20T23:42:49.889772'
queue_history:
- position: ready
  entered: '2026-02-20T23:12:14.571489'
  exited: '2026-02-20T23:12:14.603655'
- position: working
  entered: '2026-02-20T23:12:14.603655'
  exited: '2026-02-20T23:42:49.886633'
- position: done
  entered: '2026-02-20T23:42:49.886633'
  exited: null
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

- [x] Tier definitions (full, light, minimal) with criteria — ADR-047 Option B tier table
- [x] Token budget analysis for each tier — ADR-047 Context section + tier token estimates
- [x] Progressive loading strategy (load more on demand) — ADR-047 Escape Hatch (--extend)
- [x] Interface design for tier selection (argument to /coldstart or auto-detect) — ADR-047 auto-detection heuristic + explicit override
- [x] Design document or ADR — ADR-047 accepted S412

---

## History

### 2026-02-17 - Created (Session 394)
- Spawned during E2.8 arc decomposition
- CH-061 LightweightColdstart

### 2026-02-20 - Design Complete (Session 412)
- EXPLORE: Analyzed current coldstart system — 88% manual reads, 12% automated
- EXPLORE: Queried S393/S394 evidence (mem:85915-85924) — agent failure from missing HOW context
- SPECIFY: Drafted ADR-047 with 3 options (Monolithic, Tiered, MCP Server)
- CRITIQUE: 2 passes — Pass 1 REVISE (A3 staleness, A6 sequencing), Pass 2 REVISE (A7 spec marking, A8 output integration). All resolved.
- COMPLETE: ADR-047 accepted. Decision: Option B (Tiered Coldstart with Auto-Detection)
- Key design elements: 3 tiers (Full/Light/Minimal), 2 new loaders (EpochLoader, OperationsLoader), auto-detection with staleness threshold, --extend escape hatch

---

## References

- @docs/ADR/ADR-047-tiered-coldstart-context-injection.md (design ADR)
- @.claude/haios/epochs/E2_8/arcs/call/ARC.md
- @.claude/commands/coldstart.md
- @.claude/haios/lib/coldstart_orchestrator.py
- Memory: 84835, 84836 (coldstart overhead), 85459 (most tokens on context loading), 85923 (minimum viable contract), 85924 (CH-061 reframing)
