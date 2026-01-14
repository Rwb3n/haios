---
template: work_item
id: E2-029
title: /new-backlog-item Command
status: complete
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-27
milestone: M7b-WorkInfra
priority: medium
effort: medium
category: implementation
spawned_by: null
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
last_updated: '2025-12-27T15:25:53'
---
# WORK-E2-029: /new-backlog-item Command

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** No governed path for backlog item creation. Items added manually with inconsistent format.
---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Add synthesis stats to `cli.py status` command (clusters, members, last run)
- [ ] Run synthesis with `--max-bridges 200` (double default) to connect E2-015 learnings
- [ ] Identify which concepts lack embeddings (by type, content length, creation date)
- [ ] Run embedding completion script
- [ ] Verify 100% coverage
- [ ] Add entity embedding generation to ETL pipeline
- [ ] Generate embeddings for existing entities
- [ ] Verify entity retrieval works
- [ ] Define canonical type set (Greek Triad + LangExtract core types)
- [ ] Create migration to normalize existing concepts
- [ ] Update extraction to use canonical types
- [ ] `ValidateDependencies.ps1` - checks hooks/subagents/skills/commands exist
- [ ] Integration with `/status` command - surface broken references
- [ ] UserPromptSubmit hook warning on integrity issues
- [ ] Extract key learnings to memory before lost
- [ ] Auto-create mini-checkpoint with session decisions
- [ ] Store "session did X, Y, Z" summary
- [ ] Flag in-progress work for post-compact pickup
- [ ] Investigate: can we influence what compact preserves?
- [ ] Create `/new-backlog-item` command with argument parsing
- [ ] Template scaffold with correct frontmatter
- [ ] Prompt agent for required fields (priority, category, complexity)
- [ ] Optionally prompt for memory_refs (ties to E2-021)

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
