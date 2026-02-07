---
template: work_item
id: E2-218
title: Observation Triage Cycle
status: complete
owner: Hephaestus
created: 2025-12-28
closed: 2025-12-28
milestone: M7c-Governance
priority: high
effort: medium
category: implementation
spawned_by: E2-217
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related:
- E2-217
- INV-047
- INV-023
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-28 15:08:05
  exited: null
cycle_docs:
  backlog: docs/work/active/E2-218/plans/PLAN.md
memory_refs:
- 79877
- 79894
documents:
  investigations: []
  plans:
  - docs/work/active/E2-218/plans/PLAN.md
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-28T15:08:54'
---
# WORK-E2-218: Observation Triage Cycle

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Observations are captured (E2-217) but never consumed. observations.md files sit in archive with no feedback loop. This is the same write-heavy, read-weak pattern identified in INV-023 (ReasoningBank).

**Root cause:** Close-work-cycle captures observations as a gate, but has no mechanism to route observations to actionable outcomes.

**Solution:** Standalone triage cycle (not embedded in close-work-cycle) that scans observations and promotes them to appropriate destinations.

---

## Current State

```
CURRENT:  Capture → Archive → (nothing)
TARGET:   Capture → Archive → Triage → Spawn/Memory/Discuss
```

Observations accumulate but aren't acted upon.

---

## Deliverables

- [ ] Create observation-triage-cycle skill (SCAN → TRIAGE → PROMOTE)
- [ ] Add triage fields to observations.md template (category, action, priority)
- [ ] Update observations.py with triage status tracking
- [ ] Add `just triage-observations` recipe
- [ ] Document industry alignment (bug triage pattern)

---

## Design (Session 134)

### Triage Dimensions (Industry Standard)

| Dimension | Question | Values |
|-----------|----------|--------|
| **Category** | What type? | bug, gap, debt, insight, question, noise |
| **Action** | What to do? | spawn:INV, spawn:WORK, spawn:FIX, memory, discuss, dismiss |
| **Priority** | When? | P0 (blocking), P1 (this session), P2 (next), P3 (backlog) |

### Cycle Phases

```
SCAN    → Find untriaged observations (status: pending)
TRIAGE  → Classify each observation (category/action/priority)
PROMOTE → Execute actions (spawn items, store memory, flag discuss)
```

### Invocation

- Manual: `Skill(skill="observation-triage-cycle")` or `/triage`
- Automated: Heartbeat, session-end hook
- NOT embedded in close-work-cycle (keeps closure lean)

---

## History

### 2025-12-28 - Created (Session 134)
- Spawned from E2-217 observation gate design discussion
- Operator insight: observations should spawn INVs, fixes, memories, discussions
- Industry alignment: bug triage pattern (category/priority/action)
- Memory: 79877-79894 (friction surfacing insight)

---

## References

- E2-217: Observation Capture Gate (capture mechanism)
- INV-047: Close Cycle Observation Phase Ordering (capture timing)
- INV-023: ReasoningBank Feedback Loop Architecture (same pattern)
- Session 134: Epistemic insight on friction surfacing
- Industry: Bug triage, incident triage, support ticket triage patterns
