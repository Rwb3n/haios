---
template: work_item
id: E2-221
title: Routing-Gate Skill Implementation
status: complete
owner: Hephaestus
created: 2025-12-28
closed: 2025-12-28
milestone: M7c-Governance
priority: high
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: INV-048
blocked_by: []
blocks:
- E2-223
enables:
- E2-222
related:
- E2-218
- INV-047
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-28 17:25:22
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans:
  - plans/PLAN.md
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-28T17:37:18'
---
# WORK-E2-221: Routing-Gate Skill Implementation

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Routing logic is duplicated across 3 cycle skills (implementation-cycle, investigation-cycle, close-work-cycle) with identical 4-signal routing tables. No system health checks exist before routing.

**Root Cause:** Each skill evolved independently. INV-048 confirmed the duplication and designed the routing-gate architecture.

---

## Current State

Work item in BACKLOG node. High priority for M7c-Governance. Blocks E2-223 (integration).

---

## Deliverables

- [ ] Create `.claude/skills/routing-gate/SKILL.md` with Gate Contract (Entry/Guardrails/Exit)
- [ ] Implement threshold check phase (observation triage as first implementation)
- [ ] Implement work-type routing phase (4-signal table from INV-048)
- [ ] Implement escape hatch (priority=critical bypasses thresholds)
- [ ] Add tests for routing-gate logic

---

## History

### 2025-12-28 - Created (Session 137)
- Spawned from INV-048: Routing Gate Architecture
- Design contract documented in INV-048 investigation

---

## References

- Spawned by: INV-048 (Routing Gate Architecture with Observation Triage Threshold)
- Design spec: `docs/work/active/INV-048/investigations/001-*.md`
- Related: E2-218 (observation-triage-cycle)
- Related: INV-047 (Close Cycle Observation Phase Ordering)
- Memory: 78921, 78924, 78876 (gate contract patterns)
