---
template: work_item
id: INV-069
title: PostToolUse Timestamp Hook Value Assessment
type: investigation
status: active
owner: Hephaestus
created: 2026-01-27
spawned_by: WORK-027
chapter: CH-012
arc: configuration
closed: null
priority: medium
effort: medium
traces_to:
- REQ-GOVERN-002
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-27 21:47:31
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-27
last_updated: '2026-01-27T21:48:58'
---
# INV-069: PostToolUse Timestamp Hook Value Assessment

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** The PostToolUse hook injects `last_updated` timestamps into every file saved by the agent. During batch operations (WORK-027: 20+ file migration), this causes "file modified since read" errors because the hook rewrites the file between Claude's read and edit operations. This roughly doubles tool calls for mechanical tasks.

**Question:** Does the `last_updated` timestamp provide enough value to justify the friction, or should it be removed/made conditional? Git already tracks file modification via commit history.

**Scope:**
- Audit what the PostToolUse hook does (all behaviors, not just timestamps)
- Measure value: who/what consumes `last_updated`? Is it used in any logic?
- Measure cost: how much friction does it add per session?
- Recommend: keep, remove, or make conditional (e.g., toggle in haios.yaml)

---

## Deliverables

- [ ] Document all PostToolUse hook behaviors (not just timestamps)
- [ ] Identify all consumers of `last_updated` field (grep for usage)
- [ ] Assess value vs cost with evidence
- [ ] Recommendation: keep / remove / conditional toggle
- [ ] If remove/toggle: spawn implementation work item

---

## History

### 2026-01-27 - Created (Session 250)
- Spawned from WORK-027 friction during batch file edits
- Traced to configuration arc, CH-012

---

## References

- @.claude/haios/epochs/E2_3/arcs/configuration/CH-012-hook-value-assessment.md
- @.claude/hooks/post_tool_use.py
- @docs/work/active/WORK-027/observations.md
