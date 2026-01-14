---
template: work_item
id: E2-037
title: "RFC 2119 Governance Signaling System"
status: complete
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-28
milestone: M7c-Governance
priority: medium
effort: medium
category: implementation
spawned_by: "Session 64 observation"
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
  - node: backlog
    entered: 2025-12-23T19:06:12
    exited: null
cycle_docs: {}
memory_refs: [70904, 70905, 70906, 70907, 70908, 70909, 70910, 70911, 70912, 70913, 70914, 70915, 70916, 70917, 70918, 70919, 70920, 70921, 70922, 70923, 70924, 70925, 70926, 70927, 70928, 70929, 70930, 70931, 70932, 70933, 70934, 70935, 70936, 70937, 70938, 70939]
documents:
  investigations: []
  plans: []
  checkpoints: []
version: "1.0"
generated: 2025-12-23
last_updated: 2025-12-23T18:04:04
---
# WORK-E2-037: RFC 2119 Governance Signaling System

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Session 65 discovered fundamental gap: work events (discoveries, decisions) don't automatically spawn artifacts (investigations, ADRs, plans).
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
- [ ] Document pattern: "Discovery spawns backlog items" → MOVED to E2-037 (MUST /new-investigation)
- [ ] Checkpoint template: Add "Spawned Work Items" section
- [ ] /new-checkpoint prompt: "Did this session discover issues that need new backlog items?"
- [ ] Optional: /close enhancement - when closing item, prompt for discovered follow-up items
- [ ] ADR-035: Document decision and rationale
- [ ] CLAUDE.md: Add governance triggers table (MUST/SHOULD/MAY)
- [ ] UserPromptSubmit enhancement: Keyword detection → reminder injection
- [ ] Define event taxonomy (canonical work events)
- [ ] Test compliance over 5 sessions
- [ ] **Phase 5 (Session 80):** Add "SHOULD review unblocked plans before starting" trigger

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
