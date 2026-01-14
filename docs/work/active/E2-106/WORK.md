---
template: work_item
id: E2-106
title: "FORESIGHT Preparation - Cycle Prediction Fields"
status: active
owner: Hephaestus
created: 2025-12-23
closed: null
milestone: M7b-WorkInfra
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
memory_refs: [72389, 72390, 72391, 72392]
documents:
  investigations: []
  plans: []
  checkpoints: []
version: "1.0"
generated: 2025-12-23
last_updated: 2025-12-23T18:04:04
---
# WORK-E2-106: FORESIGHT Preparation - Cycle Prediction Fields

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** M3-Cycles will generate the data that feeds Epoch 3's FORESIGHT layer. By adding optional prediction/calibration fields NOW, we prepare rich seed data for:
  - **World Model:** predicted_outcome vs actual_outcome calibration
  - **Self Model:** competence_estimate by domain
  - **Goal Network:** knowledge_gaps, skill_gaps as blocking_on precursors
  - **Metamemory:** prediction confidence tracking
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
- [ ] Update `README.md` with Keys/Chords/Strings metaphor
- [ ] Create `docs/architecture/HAIOS-SONG.md` reference
- [ ] Update `docs/epistemic_state.md` to reflect new architecture
- [ ] Create `docs/pm/north_star.md` template and file
- [ ] Create `docs/pm/milestones/` directory and M1/M2 files
- [ ] Link existing backlog items to milestones
- [ ] Update `haios-status.json` with milestone tracking logic
- [ ] Update `/workspace` to show milestone progress
- [ ] Create `.claude/skills/schema-query/SKILL.md`
- [ ] Skill loads schema summary (table→columns→types)
- [ ] Skill invokes schema-verifier subagent
- [ ] Skill formats response with "for future reference" schema hints
- [ ] Audit CLAUDE.md sections by usage frequency
- [ ] Identify "always needed" vs "reference lookup" content
- [ ] Create `.claude/REFS/` directory for reference docs
- [ ] Slim CLAUDE.md to essentials (~150 lines)
- [ ] Update coldstart to surface refs availability
- [ ] Add `just heartbeat` recipe to justfile
- [ ] Create Windows Task Scheduler task (hourly)
- [ ] Heartbeat appends to `.claude/haios-events.jsonl`
- [ ] Document: "System has pulse even without operator"
- [ ] Add threshold logic to UserPromptSubmit.ps1 (after vitals)
- [ ] Thresholds: milestone > 90%, stale > 5, blocked > 3
- [ ] Messages: APPROACHING, ATTENTION, BOTTLENECK prefixes
- [ ] Test: artificially set milestone to 95%, verify message
- [ ] Create `.claude/haios-events.jsonl` (empty, append-only)
- [ ] CascadeHook.ps1 appends cascade events
- [ ] Heartbeat appends heartbeat events
- [ ] Add `just events` recipe (tail -20 haios-events.jsonl)
- [ ] Add `just events-since <date>` for filtered view
- [ ] `checkpoint.md` - Add "Session Hygiene" with SHOULD items (e.g., SHOULD review unblocked plans)
- [ ] `implementation_plan.md` - Add "Pre-Implementation Checklist" with MUST items
- [ ] `investigation.md` - Add "Discovery Protocol" with SHOULD items
- [ ] `report.md` - Add "Verification Requirements" with MUST items
- [ ] `architecture_decision_record.md` - Add "Decision Criteria" with MUST items
- [ ] Add staleness detection to cascade (sessions since last update)
- [ ] Surface "Review Prompt" in cascade message for stale unblocked plans
- [ ] Add `last_reviewed_session` field to plan frontmatter
- [ ] Rename `epistemic_state.md` -> `anti-patterns.md`
- [ ] Delete stale sections (Unknowns, Recently Surfaced, Mitigation Mechanisms)
- [ ] Update `/coldstart` to load `anti-patterns.md`
- [ ] Update CLAUDE.md references
- [ ] `just tree` / `just ready` → `/tree` command + `plan-tree` skill
- [ ] `just cascade` → `/cascade` command (or fold into `/close`)
- [ ] `just events*` → `/events` command + `events` skill
- [ ] `just session-start/end` → auto-invoke from commands (no direct user call)
- [ ] Update regex to handle `backlog_ids: [array]` syntax
- [ ] Store as array (first item for backward compat, or all)
- [ ] Verify checkpoints now show correct backlog_ids in haios-status.json
- [ ] `just audit-sync` - compare investigation file status vs archive
- [ ] `just audit-gaps` - find backlog items with implementation evidence but still pending
- [ ] `just audit-stale` - find investigations older than 10 sessions still active
- [ ] `just synthesis-backup` recipe - Copy haios_memory.db before synthesis
- [ ] `just synthesis-rollback` recipe - Restore from backup
- [ ] Add `superseded_by` field to concepts for invalidation tracking
- [ ] Post-synthesis quality report (false positive sampling)
- [ ] Threshold tuning for similarity cutoffs
- [ ] Consider: sampling mode (10% of pairs for 90% of value?)
- [ ] preflight-checker returns structured warnings (not blocks)
- [ ] Events flag "skipped_phase" for non-sequential transitions
- [ ] `/close` warns if no cycle events exist (can override)
- [ ] Consider: cycle state persistence across context refreshes
- [ ] Define `foresight_prep` schema (optional frontmatter section)
- [ ] Update E2-096 (cycle_phase) with foresight_prep fields
- [ ] Update E2-091 (implementation-cycle skill) with prediction prompts
- [ ] Update E2-095 (why-capturer) to also capture prediction accuracy
- [ ] Update E2-097 (cycle events) to include prediction events

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

---

## References

- [Related documents]
