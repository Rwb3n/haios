---
template: work_item
id: INV-068
title: Cycle Delegation Architecture - Subagents for Cycle Execution
status: complete
owner: Hephaestus
created: 2026-01-17
closed: '2026-02-02'
milestone: null
priority: medium
effort: medium
category: investigation
spawned_by: null
spawned_by_investigation: null
arc: pipeline
blocked_by: []
blocks: []
enables: []
related:
- INV-062
- INV-065
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-17 15:07:16
  exited: null
cycle_docs: {}
memory_refs:
- 83213
- 83214
- 83215
- 83216
- 83217
- 83218
- 83219
- 83220
- 83221
- 83222
- 83223
- 83224
- 83231
- 83232
- 83233
- 83234
- 83235
operator_decisions: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-17
last_updated: '2026-02-02T19:32:28'
---
# WORK-INV-068: Cycle Delegation Architecture - Subagents for Cycle Execution

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Main agent track (orchestrator) reaches context limits faster as governance strengthens. Coldstart, hooks, status injection, and inline cycle execution all consume context. The main track should focus on operator/supervisor routing, not execute full cycles inline.

**Root Cause:** Cycles (implementation-cycle, close-work-cycle, investigation-cycle) execute inline in the main conversation. Each phase consumes context. The orchestrator becomes a worker instead of delegating.

**Alignment:**
- L4 Epoch 4 vision: Orchestrator at L3-L4, Workers at L5-L7
- S25 SDK path: Custom tools execute cycles, harness controls flow
- S20 pressure dynamics: Main track [volumous] survey/route, subagents [tight] execution

---

## Current State

Investigation COMPLETE (Session 292). Findings synthesized, spawned WORK-081.

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
-->

- [x] Findings document with architectural options for cycle delegation
- [x] Trade-off analysis: inline execution vs subagent delegation
- [x] Spawned work items for implementation (if warranted) - WORK-081

---

## History

### 2026-01-17 - Created (Session 199)
- Initial creation

### 2026-02-02 - Investigation Complete (Session 292)
- EXPLORE: Gathered evidence from INV-065, S20, S24, S25, existing agents, CycleRunner
- HYPOTHESIZE: 4 hypotheses formed from evidence
- VALIDATE: H1-H3 Confirmed, H4 Inconclusive
- CONCLUDE: Findings synthesized, spawned WORK-081
- Key finding: Task tool provides sufficient isolation for cycle delegation
- Estimated 70-90% context reduction for main track

---

## Findings Summary

### Hypothesis Verdicts

| Hypothesis | Verdict | Confidence |
|------------|---------|------------|
| H1: 60-80% context reduction | Confirmed | High |
| H2: Task tool sufficient for isolation | Confirmed | High |
| H3: SDK better but Task tool viable bridge | Confirmed | High |
| H4: Phase-as-Subagent superior | Inconclusive | Medium |

### Architectural Decision

Implement **Cycle-as-Subagent** pattern:
- Main track (orchestrator) invokes Task subagent
- Subagent executes full cycle autonomously
- Returns structured summary
- Patterns port to SDK custom tools (Epoch 4)

### Trade-off Analysis

| Factor | Inline Execution | Cycle-as-Subagent |
|--------|------------------|-------------------|
| Main track context | High | Low (70-90% reduction) |
| Gate enforcement | Self-enforced | Same (soft) |
| SDK migration | Requires rewrite | Direct port |

---

## References

- @docs/work/active/INV-065/investigations/001-session-state-cascade-architecture.md (Skill() unhookable finding)
- @.claude/haios/epochs/E2/architecture/S25-sdk-path-to-autonomy.md (SDK migration path)
- @.claude/haios/epochs/E2_3/architecture/S20-pressure-dynamics.md (volumous/tight pattern)
- @.claude/haios/epochs/E2/architecture/S24-staging-pattern.md (L3-L4/L5-L7 vision)
- @.claude/agents/README.md (existing agent patterns)
- Memory: 82320, 82355, 47531, 72323 (prior cycle delegation concepts)
