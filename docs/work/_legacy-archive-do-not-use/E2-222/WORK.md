---
template: work_item
id: E2-222
title: Routing Threshold Configuration
status: complete
owner: Hephaestus
created: 2025-12-28
closed: 2025-12-28
milestone: M7c-Governance
priority: medium
effort: small
category: implementation
spawned_by: null
spawned_by_investigation: INV-048
blocked_by: []
blocks: []
enables: []
related:
- E2-221
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-28 17:25:31
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
last_updated: '2025-12-28T20:31:08'
---
# WORK-E2-222: Routing Threshold Configuration

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** No configurable thresholds exist for routing-gate system health checks. Thresholds need to be operator-tunable policy.

**Root Cause:** INV-048 designed threshold architecture but configuration file doesn't exist yet.

---

## Current State

Work item in BACKLOG node. Medium priority (can be done alongside or after E2-221).

---

## Deliverables

- [ ] Create `.claude/config/routing-thresholds.yaml` with schema from INV-048
- [ ] Add observation_pending threshold (enabled: true, max_count: 10)
- [ ] Document threshold configuration in CLAUDE.md or relevant README

---

## History

### 2025-12-28 - Created (Session 137)
- Spawned from INV-048: Routing Gate Architecture
- Schema designed in INV-048 investigation

---

## References

- Spawned by: INV-048 (Routing Gate Architecture with Observation Triage Threshold)
- Design spec: `docs/work/active/INV-048/investigations/001-*.md`
- Related: E2-221 (routing-gate skill)
