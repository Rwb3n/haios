---
template: work_item
id: E2-028
title: "Greek Triad Classification Gap"
status: archived
owner: Hephaestus
created: 2025-12-23
closed: null
milestone: M8-Memory
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
memory_refs: [64974, 64975, 64976, 64977, 64978, 64979, 64980, 64981, 64982, 64983, 64984, 64985, 64986, 64987, 64988, 64989, 64990, 64991, 64992]
documents:
  investigations: []
  plans: []
  checkpoints: []
version: "1.0"
generated: 2025-12-23
last_updated: 2025-12-23T18:04:04
---
# WORK-E2-028: Greek Triad Classification Gap

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Greek Triad (episteme/techne/doxa) barely used - 39 concepts total vs 64,971 using extraction types.
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
- [ ] Add memory-specific MUST/SHOULD rules to CLAUDE.md governance triggers (E2-037 Phase 1)
- [ ] Add `memory_refs` field to backlog_item template
- [ ] PreToolUse hook validates memory_refs on backlog.md edits (warn, not block)
- [ ] `/new-backlog-item` command that prompts for memory references
- [ ] Weekly review cycle: query memory for stale/unlinked concepts
- [ ] `/memory-audit` command: surfaces backlog items without memory refs
- [ ] Integration with `/workspace`: show memory coverage stats
- [ ] Create `.claude/agents/critic.md` subagent definition
- [ ] Define critique framework (Assumption Surfacing as default)
- [ ] Create `/critique <artifact>` command or skill invocation
- [ ] Test on 3 existing designs, validate improvement
- [ ] Test PreToolUse enforcement (intentionally try raw Write)
- [ ] Sample 10 extracted strategies, rate quality
- [ ] Scan all .md files for template compliance rate
- [ ] Review alignment_issues from UpdateHaiosStatus.ps1
- [ ] Timeline analysis: when was Triad introduced vs bulk extraction
- [ ] Schema update: add `knowledge_class` column (episteme/techne/doxa)
- [ ] Mapping heuristics: can extraction types inform Triad? (Critique often → doxa)
- [ ] Doxa identification: what content qualifies as belief/opinion
- [ ] Migration plan: backfill existing concepts with knowledge_class
- [ ] Ingester update: auto-classify knowledge_class on ingest

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
