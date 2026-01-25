---
template: work_item
id: WORK-012
title: HAIOS Agent Registration Architecture
type: investigation
status: active
owner: Hephaestus
created: 2026-01-25
spawned_by: E2-072 observation (Session 236)
chapter: null
arc: configuration
closed: null
priority: medium
effort: medium
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-25 02:10:56
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-25
last_updated: '2026-01-25T02:11:44'
---
# WORK-012: HAIOS Agent Registration Architecture

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** HAIOS-defined agents (`.claude/agents/*.md`) are not available to the Task tool's `subagent_type` parameter. Only Claude Code plugin-registered agents work. Discovered during E2-072 when `Task(subagent_type='critique-agent')` failed despite the agent file existing.

**Question:** How should HAIOS agents be registered/exposed for Task tool invocation?

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

- [ ] Document how Claude Code agent registration works
- [ ] Identify options for HAIOS agent exposure
- [ ] Recommend architecture (or workaround pattern)

---

## History

### 2026-01-25 - Created (Session 236)
- Initial creation

---

## References

- [Related documents]
