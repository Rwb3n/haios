---
template: work_item
id: E2-236
title: Orphan Session Detection and Recovery
status: complete
owner: Hephaestus
created: 2025-12-30
closed: '2026-01-26'
milestone: M7b-WorkInfra
priority: medium
effort: medium
category: implementation
spawned_by: INV-052
spawned_by_investigation: INV-052
arc: configuration
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-30 20:19:18
  exited: null
cycle_docs: {}
memory_refs:
- 82459
- 82460
- 82461
- 82466
traces_to:
- REQ-CONTEXT-001
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-30
last_updated: '2026-01-26T20:21:07'
---
# WORK-E2-236: Orphan Session Detection and Recovery

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** When context exhausts or connection drops, there's no automatic recovery: no session-end is logged, no checkpoint is created, and work may be lost (not committed).

**Root cause:** No crash detection mechanism exists. Session state assumes clean session-end will always happen.

**Source:** INV-052 Issue 5 (No Crash Recovery)

---

## Current State

Work item created from INV-052 findings. Ready for implementation.

---

## Deliverables

- [ ] Add function `detect_orphan_session()` in `.claude/haios/lib/governance_events.py`
- [ ] Check governance-events.jsonl for "start without end" pattern (session N started, no end logged, session N+1 started)
- [ ] Scan WORK.md files for `exited: null` node_history entries (incomplete transitions)
- [ ] Report incomplete work to agent during coldstart (inject into context)
- [ ] Log synthetic session-end event for orphaned session
- [ ] Wire into ColdstartOrchestrator to run detection before context loading
- [ ] Test recovery with simulated crash scenarios
- [ ] Runtime consumer: ColdstartOrchestrator calls `detect_orphan_session()`

---

## History

### 2026-01-26 - Populated (Session 245)
- Added `traces_to: REQ-CONTEXT-001`
- Expanded deliverables to cover INV-052 design outputs
- Added reference to INV-052 Section 2A (crash recovery design)
- Added runtime consumer requirement

### 2025-12-30 - Created (Session 150)
- Initial creation

---

## References

- @docs/work/archive/INV-052/SECTION-2A-SESSION-LIFECYCLE.md (design source, lines 68-76)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CONTEXT-001)
- @.claude/haios/modules/coldstart_orchestrator.py (runtime consumer)
