---
template: work_item
id: E2-108
title: Gate Observability for Implementation Cycle
status: complete
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-29
milestone: M7c-Governance
priority: medium
effort: medium
category: implementation
spawned_by: Session 64 observation
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-23 19:06:12
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-23
last_updated: '2025-12-28T22:17:51'
---
# WORK-E2-108: Gate Observability for Implementation Cycle

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Hard gates (MUST validation) work for governance compliance, but lack observability. When agents skip phases or validation fails, there's no event trail. This makes it hard to measure governance effectiveness or debug workflow issues.

**Evolution (from memory):**
- Session 64: Chose "soft gates" (Option B) over hard gates
- Later sessions: Evidence that L2 guidance ignored ~20% of time
- Concept 79898: "Hard gate > soft suggestion: Agents biased toward completion"
- Current state: Hard gates are working (E2-217 observation gate, dod-validation-cycle)

**Transformed Scope (Session 141):** Keep hard gates, add observability layer to track phase transitions and validation outcomes.
---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

Add observability layer to hard gates (keep blocking behavior, add event logging). Goal: measure governance effectiveness and trigger appropriate actions.

### 1. Event Schema & Logging

- [ ] Define `CyclePhaseEntered` event schema (phase, work_id, timestamp, agent)
- [ ] Define `ValidationOutcome` event schema (gate, work_id, result, reason)
- [ ] Log phase transitions in implementation-cycle skill (PLAN→DO→CHECK→DONE)
- [ ] Log validation outcomes for bridge skills (preflight, dod, observation)

### 2. Consumption & Actions (Trigger→Action→Owner)

Per memory concept 27238: observability needs trigger→action→owner→SLA chain.

| Trigger | Action | Owner | SLA |
|---------|--------|-------|-----|
| Validation failure count > threshold | Surface in `/status` warning | Agent (coldstart) | Next session |
| Phase skipped (no event) | Log to governance drift metric | Audit system | Weekly review |
| Same gate fails 3x in session | Prompt agent to investigate | Agent (dynamic) | Same session |
| Work item closed without events | Warning in close-work-cycle | Agent (close) | Immediate |

- [ ] Implement threshold-based alerting in UserPromptSubmit
- [ ] Implement "governance drift" detection in audit skill
- [ ] Implement repeated failure prompt (3x same gate)

### 3. Metrics Surface

- [ ] Add `just governance-metrics` recipe to summarize events
- [ ] Surface governance health in `/status` command
- [ ] Track: phase transitions, validation pass/fail rates, common failures

### 4. Verification

- [ ] Test: Complete work item, verify phase events logged
- [ ] Test: Fail validation 3x, verify prompt appears
- [ ] Test: Close without events, verify warning
- [ ] Existing tests continue to pass

---

## History

### 2025-12-28 - Transformed (Session 141)
- Cleaned up corrupted deliverables (copy-paste contamination)
- **Scope transformed:** Original "soft gates" contradicted by later evidence (concept 79898)
- New scope: Add observability to existing hard gates (not replace them)
- 11 deliverables across 4 categories

### 2025-12-23 - Created (Session 105)
- Initial creation

---

## References

- implementation-cycle skill (`.claude/skills/implementation-cycle/SKILL.md`) - target for soft gates
- preflight-checker agent (`.claude/agents/preflight-checker.md`) - structured warnings
- close-work-cycle skill - cycle event validation
- ADR-033: Work Item Lifecycle Governance
