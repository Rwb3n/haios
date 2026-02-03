---
template: work_item
id: WORK-081
title: Implement Cycle-as-Subagent Delegation Pattern
type: implementation
status: active
owner: Hephaestus
created: 2026-02-02
spawned_by: INV-068
chapter: null
arc: lifecycles
closed: null
priority: medium
effort: medium
traces_to: []
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-02 19:30:24
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.5
version: '2.0'
generated: 2026-02-02
last_updated: '2026-02-03T20:52:14'
---
# WORK-081: Implement Cycle-as-Subagent Delegation Pattern

---

## Context

**Problem:** Main agent track (orchestrator) reaches context limits faster as governance strengthens. Coldstart, hooks, status injection, and inline cycle execution all consume context. The main track should focus on operator/supervisor routing, not execute full cycles inline.

**Root Cause:** Cycles (implementation-cycle, close-work-cycle, investigation-cycle) execute inline in the main conversation. Each phase consumes context. The orchestrator becomes a worker instead of delegating.

**Solution (from INV-068):** Implement Cycle-as-Subagent pattern using Claude Code Task tool:
- Main track invokes `Task(subagent_type='implementation-cycle-agent', ...)`
- Subagent executes full cycle autonomously in fresh context
- Returns structured summary to main track
- Estimated 70-90% context reduction for main track

**Alignment:**
- L4 Epoch 4 vision: Orchestrator at L3-L4, Workers at L5-L7
- S25 SDK path: Patterns port directly to SDK custom tools
- S20 pressure dynamics: Main track [volumous] survey/route, subagents [tight] execution

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

- [ ] Create `implementation-cycle-agent` (.claude/agents/implementation-cycle-agent.md)
- [ ] Create `investigation-cycle-agent` (.claude/agents/investigation-cycle-agent.md)
- [ ] Create `close-work-cycle-agent` (.claude/agents/close-work-cycle-agent.md)
- [ ] Update cycle skills to offer subagent delegation as alternative to inline execution
- [ ] Test: verify subagent executes cycle and returns structured summary
- [ ] Document pattern in agents/README.md

---

## History

### 2026-02-02 - Created (Session 292)
- Spawned from INV-068 investigation findings
- Confirmed Task tool provides sufficient isolation for cycle execution
- Estimated 70-90% context reduction for main track

---

## References

- @docs/work/active/INV-068/WORK.md (spawning investigation)
- @.claude/haios/epochs/E2/architecture/S25-sdk-path-to-autonomy.md (SDK migration path)
- @.claude/haios/epochs/E2_3/architecture/S20-pressure-dynamics.md (volumous/tight pattern)
- @.claude/haios/epochs/E2/architecture/S24-staging-pattern.md (L3-L4 orchestrator, L5-L7 workers)
- @.claude/agents/README.md (existing agent patterns)
