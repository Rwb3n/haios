---
template: work_item
id: WORK-079
title: CHAIN Phase Stop Pattern Investigation
type: investigation
status: active
owner: null
created: 2026-02-02
spawned_by: null
chapter: null
arc: null
closed: null
priority: high
effort: medium
traces_to:
- REQ-FLOW-001
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-02 12:27:53
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 83156
- 83157
- 83158
- 83159
- 83160
- 83161
extensions: {}
version: '2.0'
generated: 2026-02-02
last_updated: '2026-02-02T13:05:22'
---
# WORK-079: CHAIN Phase Stop Pattern Investigation

---

## Context

**Problem:** Agent execution stops at CHAIN phase boundaries during skill execution. Observed multiple times in Session 285 during close-work-cycle and checkpoint-cycle. The agent formulates intent but doesn't emit the action.

**Hypothesis:** CHAIN phases involve workflow transitions (ending one cycle, starting another). Context pruning or optimization may be triggering at these boundaries, causing execution to stall.

**Observations from Session 285:**
1. Stop after `just coldstart-orchestrator` (large context load)
2. Stop after `just scaffold-checkpoint 285` failed (error → rethink)
3. Stop after scaffold.py error (error recovery path)
4. Stops clustered at ceremony/transition steps, not during core DO phase work

**Potential Mitigations to Investigate:**
1. CHAIN phases as subagents (isolated context, different cognitive mode)
2. CC TaskList continuity (tasks persist across stops, provide resumption point)
3. Simplified CHAIN phase instructions (less ceremony, more direct execution)

---

## Deliverables

- [ ] **Root cause analysis** - Identify what triggers stops at workflow boundaries
- [ ] **Subagent pattern for CHAIN** - Design chain-agent that handles routing
- [ ] **TaskList continuity experiment** - Test if active tasks prevent stops
- [ ] **Recommendations** - Concrete changes to skill definitions

---

## History

### 2026-02-02 - Additional Evidence (Session 286)
- Two stops during WORK-076 CHAIN phase (checkpoint-cycle):
  1. `just scaffold-checkpoint 286` failed (recipe doesn't exist)
  2. Python fallback `scaffold_checkpoint()` failed (function doesn't exist)
- Pattern confirmed: stops at error recovery paths during ceremony/transition steps
- Memory refs 83156-83161 added with evidence

### 2026-02-02 - Created (Session 285)
- Observed pattern: stops at CHAIN phases during WORK-070 closure
- Spawned from discussion with operator about AgentUX friction

---

## References

- @docs/checkpoints/2026-02-02-06-SESSION-285-work-070-multi-level-dod-complete.md
- @.claude/skills/close-work-cycle/SKILL.md (CHAIN phase definition)
- @.claude/skills/implementation-cycle/SKILL.md (CHAIN phase definition)
- @.claude/skills/checkpoint-cycle/SKILL.md (commit/end steps)
