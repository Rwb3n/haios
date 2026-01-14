# generated: 2025-12-14
# System Auto: last updated on: 2025-12-23T19:09:11
# HAIOS Backlog Archive - Completed Items

> **Migration Date:** 2025-12-13 (Session 70)
> **Source:** docs/pm/backlog.md
> **Reason:** ADR-036 PM Data Architecture - reduce active backlog bloat
> **Items Migrated:** 33

This archive contains completed, closed, and subsumed work items.
Items preserve their original content for historical reference.
Status values normalized to `complete` per ADR-033.

---

## Epoch 2: Governance Suite (Archived)

<!-- Archived: 2025-12-23 via /close (Session 106) -->
### [COMPLETE] E2-151: Backlog Migration Script
- **Status:** complete
- **Priority:** low
- **Owner:** Hephaestus
- **Created:** 2025-12-23
- **Closed:** 2025-12-23 (Session 106)
- **Session:** 105
- **spawned_by:** INV-024
- **blocked_by:** [E2-150]
- **Milestone:** M6-WorkCycle
- **Context:** Phase A.2 of Work-Item-as-File migration. Script to convert backlog.md entries to work files.
- **Deliverables:**
  - [x] Script to parse backlog.md and extract entries
  - [x] Create WORK-{id}.md files in `docs/work/active/`
  - [x] Preserve original content as `## Context`
  - [x] Retain backlog.md as legacy index (read-only)
- **Effort:** Medium
- **Related:** [ADR-039, E2-150]
- **Memory refs:** [77347-77354]

<!-- Archived: 2025-12-23 via /close (Session 106) -->
### [COMPLETE] E2-150: Work-Item Infrastructure
- **Status:** complete
- **Priority:** medium
- **Owner:** Hephaestus
- **Created:** 2025-12-23
- **Closed:** 2025-12-23 (Session 106)
- **Session:** 105
- **spawned_by:** INV-024
- **Milestone:** M6-WorkCycle
- **Context:** Phase A.1 of Work-Item-as-File migration (ADR-039). Create infrastructure for work-item files.
- **Absorbs:** E2-096 (Cycle State Frontmatter) - work file schema supersedes plan-only cycle_state
- **Deliverables:**
  - [x] Create `docs/work/{active,blocked,archive}/` directories
  - [x] Create `work_item` template in `.claude/templates/` (INV-022 schema v2)
  - [x] Add `/new-work` command
  - [x] Update status.py to scan `docs/work/`
- **Effort:** Medium
- **Related:** [ADR-039, INV-024, INV-022, E2-096]
- **Memory refs:** [77343, 77344, 77345, 77346]

<!-- Archived: 2025-12-23 via /close (Session 104) -->
### [COMPLETE] E2-146: Validation Error Message Placeholder Sections
- **Status:** complete
- **Priority:** high
- **Owner:** Hephaestus
- **Created:** 2025-12-23
- **Closed:** 2025-12-23 (Session 104)
- **Session:** 104
- **spawned_by:** E2-145
- **Milestone:** M5-Plugin
- **Context:** E2-145 added placeholder detection to validate.py. When validation fails due to placeholder_sections (not missing_sections), the error message was confusing.
- **Problem:** Error message said "Missing sections without SKIPPED rationale: ." with empty list
- **Solution:** Updated error message to include both missing_sections AND placeholder_sections
- **Deliverables:**
  - [x] Updated `validate_template()` error message to report placeholder_sections
  - [x] Added test: `test_error_message_includes_placeholder_sections`
- **Pattern:** Bug fix - error message accuracy
- **Test Count:** 393 passed

<!-- Archived: 2025-12-23 via /close (Session 104) -->
### [COMPLETE] E2-142: Investigation-Cycle Subagent Enforcement
- **Status:** complete
- **Priority:** medium
- **Owner:** Hephaestus
- **Created:** 2025-12-23
- **Closed:** 2025-12-23 (Session 104)
- **Session:** 101-104
- **spawned_by:** INV-022
- **Milestone:** M5-Plugin
- **Context:** Session 101 demonstrated agent bypassing investigation-agent subagent despite skill saying "RECOMMENDED". L2 guidance ignored ~20% of time.
- **Problem:** Agent does investigation work directly instead of delegating to specialized subagent
- **Solution:** Changed investigation-cycle skill from "RECOMMENDED" to "MUST invoke investigation-agent for EXPLORE phase"
- **Deliverables:**
  - [x] Update investigation-cycle/SKILL.md with L3 language ("MUST follow" + guardrail #1)
  - [x] Add explicit MUST requirement for subagent invocation in investigation-agent.md
- **Pattern:** L2 → L3 upgrade - from suggestion to requirement
- **Related:** [INV-022, E2-144, investigation-cycle skill]

<!-- Archived: 2025-12-23 via /close (Session 104) -->
### [COMPLETE] E2-145: Validate Script Section Enforcement
- **Status:** complete
- **Priority:** high
- **Owner:** Hephaestus
- **Created:** 2025-12-23
- **Closed:** 2025-12-23 (Session 104)
- **Session:** 103-104
- **spawned_by:** E2-140 (plan audit revealed gap)
- **Milestone:** M5-Plugin
- **Context:** validate.py only checked frontmatter. Sections could be silently deleted without rationale.
- **Problem:** Template governance requires `**SKIPPED:**` rationale for omitted sections, but this was L2 (suggestion) not L4 (mechanical).
- **Solution:** Enhanced validate.py with:
  1. `is_placeholder_content()` function to detect `[...]`, `TODO`, `TBD` patterns
  2. `expected_sections` for investigation template (11 sections)
  3. `placeholder_sections` tracking in `check_section_coverage()`
- **Deliverables:**
  - [x] Define `expected_sections` for investigation template (11 sections)
  - [x] Add `is_placeholder_content()` function to validate.py
  - [x] Detect `**SKIPPED:**` pattern as valid skip (already existed, preserved)
  - [x] Add heuristic for placeholder detection (`[...]`, `TODO`, `TBD`)
  - [x] 5 tests for section validation
- **Pattern:** L2 → L4 upgrade - mechanical enforcement of section requirements
- **Related:** [E2-140, INV-022, INV-020 (L4 pattern)]
- **Test Count:** 392 passed

<!-- Archived: 2025-12-23 via /close (Session 103) -->
### [COMPLETE] E2-141: Backlog ID Uniqueness Gate
- **Status:** complete
- **Priority:** high
- **Owner:** Hephaestus
- **Created:** 2025-12-23
- **Closed:** 2025-12-23 (Session 103)
- **Session:** 101-103
- **spawned_by:** INV-022
- **Milestone:** M5-Plugin
- **Context:** Session 101 found ID collision - two INV-011 files existed. No validation prevented duplicate backlog_id creation.
- **Problem:** Duplicate IDs cause confusion, broken references
- **Solution:** PreToolUse hook checks for existing backlog_id before allowing new file creation
- **Deliverables:**
  - [x] Add uniqueness check to pre_tool_use.py
  - [x] Grep all docs/ for backlog_id before allowing new file
  - [x] Return blocking message with existing file path
- **Pattern:** L3 gate - prevent wrong action before it happens
- **Plan:** `docs/plans/PLAN-E2-141-backlog-id-uniqueness-gate.md`
- **Memory:** Concepts 77290-77296

<!-- Archived: 2025-12-23 via /close (Session 103) -->
### [COMPLETE] E2-140: Investigation Status Sync Hook
- **Status:** complete
- **Priority:** high
- **Owner:** Hephaestus
- **Created:** 2025-12-23
- **Closed:** 2025-12-23 (Session 103)
- **Session:** 101-103
- **spawned_by:** INV-022
- **Milestone:** M5-Plugin
- **Context:** Session 101 audit found 5 investigations with file `status: active` but already archived in backlog-complete.md. /close updates backlog but not investigation file frontmatter.
- **Problem:** Governance drift - file status ≠ archive status
- **Solution:** PostToolUse hook on Edit to backlog-complete.md that auto-updates corresponding investigation file `status: complete`
- **Deliverables:**
  - [x] Add investigation sync logic to post_tool_use.py (Part 6)
  - [x] When archiving INV-*, also update investigation file status
  - [x] Test with 7 unit tests
- **Pattern:** L4 automation - sync is mechanical, not manual
- **Related:** [INV-022, E2-076e, post_tool_use.py]
- **Effort:** Small
- **Plan:** `docs/plans/PLAN-E2-140-investigation-status-sync-hook.md`
- **Memory:** Concepts 77279-77286

<!-- Archived: 2025-12-22 via /close (Session 98) -->
### [COMPLETE] E2-111: Investigation Cycle Skill
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-20
- **Closed:** 2025-12-22 (Session 98)
- **Session:** 97-98
- **Milestone:** M4-Research
- **Context:** HYPOTHESIZE-EXPLORE-CONCLUDE workflow for research work. Parallel to implementation-cycle.
- **Deliverables:**
  - [x] Create `.claude/skills/investigation-cycle/SKILL.md`
  - [x] Create `.claude/skills/investigation-cycle/README.md`
  - [x] Three phases: HYPOTHESIZE, EXPLORE, CONCLUDE
  - [x] Memory query at start (prior work check)
  - [x] Spawned work items as required exit criterion
- **Effort:** Small (~30 min)
- **Related:** [implementation-cycle, E2-112, E2-113, E2-115]
- **Plan:** `docs/plans/PLAN-E2-111-investigation-cycle-skill.md`
- **Memory:** Concepts 77115-77117

<!-- Archived: 2025-12-22 via /close (Session 98) -->
### [COMPLETE] E2-115: Investigation Closure
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-20
- **Closed:** 2025-12-22 (Session 98)
- **Session:** 98
- **Milestone:** M4-Research
- **Context:** DoD for investigations: findings documented, spawns created and linked.
- **Deliverables:**
  - [x] Extend `/close` with Step 1.5 for INV-* items
  - [x] Check Findings section has content
  - [x] Check Spawned Work Items has entries
  - [x] Check memory_refs populated
  - [x] Gate closure on investigation DoD
- **Effort:** Small (~45 min)
- **Related:** [E2-111, E2-023, ADR-033]
- **Plan:** `docs/plans/PLAN-E2-115-investigation-closure.md`
- **Memory:** Concepts 77123-77125

<!-- Archived: 2025-12-22 via /close (Session 98) -->
### [COMPLETE] E2-113: Investigation Events
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-20
- **Closed:** 2025-12-22 (Session 98)
- **Session:** 98
- **Milestone:** M4-Research
- **Context:** Log investigation phase transitions to haios-events.jsonl.
- **Deliverables:**
  - [x] Extend `_log_cycle_transition` to handle INVESTIGATION-*.md
  - [x] Same event schema as plan events
  - [x] Verified with INV-023 phase change
- **Effort:** Small (~25 min)
- **Related:** [E2-097, E2-111, E2-084]
- **Plan:** `docs/plans/PLAN-E2-113-investigation-events.md`
- **Memory:** Concepts 77141-77143

<!-- Archived: 2025-12-22 via /close (Session 100) -->
### [COMPLETE] INV-020: LLM Energy Channeling Patterns
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-21
- **Closed:** 2025-12-22 (Session 100)
- **Session:** 95, 100
- **Type:** Research/Investigation
- **Core Finding:** "Doing right should be easy" means "doing wrong should be hard." Only L3/L4 enforcement changes behavior; L2 suggestions are ignored.
- **Findings:**
  - F1: Enforcement Spectrum Analysis (L0-L4)
  - F2: What's Actually Blocking (3 L3 gates)
  - F3: Dead Infrastructure (RESONANCE, lifecycle guidance, RFC2119)
  - F4: Effective vs Ineffective Patterns
  - F5: The "Last Mile" Problem
  - F6: Hypothesis Verdicts (H1, H2, H4, H5 confirmed)
- **Spawned:** E2-135, E2-136 (M5-Plugin), E2-137, E2-138 (M6-Feedback)
- **Investigation:** `docs/investigations/INVESTIGATION-INV-020-llm-energy-channeling-patterns.md`
- **Memory:** Concepts 77199-77209

<!-- Archived: 2025-12-22 via inline fix (Session 100) -->
### [COMPLETE] E2-133: Scaffold Session Auto-Population Fix
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-22
- **Closed:** 2025-12-22 (Session 100)
- **Session:** 100
- **spawned_by:** E2-116 demo observation
- **Context:** Scaffold only populated {{SESSION}} for checkpoints. All other templates left {{SESSION}} as placeholder.
- **Root Cause:** get_prev_session() read wrong path, SESSION only for checkpoints
- **Fix:** Added get_current_session(), fixed get_prev_session(), SESSION now for all templates
- **Tests:** 24 tests pass
- **Spawned:** E2-134 (Session Number from Events Log)
- **Memory:** Concepts 77195-77197

<!-- Archived: 2025-12-22 via /close (Session 100) -->
### [COMPLETE] E2-116: Investigate @ Reference Necessity in Checkpoints
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-20
- **Closed:** 2025-12-22 (Session 100)
- **Session:** 100
- **Milestone:** M4-Research
- **Context:** Investigation into whether @ references in checkpoints provide value beyond memory_refs.
- **Findings:**
  - Claude Code @ syntax is a PROMPT feature, not file parsing
  - /coldstart does NOT use @ references
  - @ refs are purely ceremonial - zero functional value
  - All 4 hypotheses CONFIRMED
- **Recommendation:** Remove @ refs from checkpoint template
- **Spawned:** E2-132 (Remove @ References from Checkpoint Template)
- **Effort:** Small
- **Investigation:** `docs/investigations/INVESTIGATION-E2-116-at-reference-necessity-in-checkpoints.md`
- **Memory:** Concepts 77186-77190

<!-- Archived: 2025-12-21 via /close (Session 94) -->
### [COMPLETE] E2-120: Plugin Architecture Migration
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-20
- **Closed:** 2025-12-21 (Session 94)
- **Session:** 91-94
- **Milestone:** M5-Plugin
- **Spawned By:** Session 91 operator decision - Plugin-first architecture
- **Context:** Migrated HAIOS from project-embedded code to portable Claude Code plugin. All Python code moved to `.claude/lib/`, all PowerShell to Python. Enables installation into ANY project.
- **Phases Completed:**
  - Phase 0: Foundation (plugin.json, lib structure)
  - Phase 1: Core modules (database, retrieval, synthesis, mcp_server)
  - Phase 2: Status functions (28 tests), Scaffold (23 tests), Validate (22 tests)
  - Phase 3: PS1 archival, YAML timestamp fix, E2-126 unblocked
- **Test Results:** 322 passed, 1 skipped (pending E2-126)
- **Effort:** Epic (~9 hours across 3 sessions)
- **Enables:** [E2-117, E2-118, E2-119, E2-125, E2-126, Plugin distribution]
- **Related:** [E2-085, PLUGINS-REF.md]
- **Plan:** `docs/plans/PLAN-E2-120-complete-powershell-to-python-migration.md`
- **Memory:** Concept 77022

<!-- Archived: 2025-12-20 via /close (Session 91) -->
### [COMPLETE] E2-085: Hook System Migration (PowerShell to Python)
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-16
- **Closed:** 2025-12-20 (Session 91)
- **Session:** 91
- **Milestone:** M4-Research
- **Context:** Migrated 4 PowerShell hooks to single Python dispatcher. Fixed recurring bash/PowerShell escaping issues. 22 tests, all passing. ~1,146 lines PS1 replaced with ~500 lines Python.
- **Effort:** Medium (1 session with TDD)
- **Related:** [E2-076d, E2-037, E2-007, E2-117]
- **Plan:** `docs/plans/PLAN-E2-085-hook-system-migration-powershell-to-python.md`
- **Investigation:** `docs/investigations/INVESTIGATION-E2-085-hook-migration-powershell-to-python.md`
- **Memory:** Concepts 76916-76923

<!-- Archived: 2025-12-20 via /close (Session 90) -->
### [COMPLETE] E2-110: Spawn Field Governance
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-20
- **Closed:** 2025-12-20 (Session 90)
- **Session:** 90
- **Milestone:** M4-Research
- **Context:** Added spawn_map tracking to haios-status.json. Get-SpawnMap function scans docs for spawned_by fields and maps parent IDs to children arrays. Enables E2-114 (Spawn Tree Query) and E2-115 (Investigation Closure).
- **Effort:** Small
- **Related:** [E2-114, E2-115]
- **Plan:** `docs/plans/PLAN-E2-110-spawn-field-governance.md`
- **Memory:** Concepts 76877-76882

<!-- Archived: 2025-12-20 via /close (Session 89) -->
### [COMPLETE] E2-103: Populate failure_reason in Stop Hook
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-19
- **Closed:** 2025-12-20 (Session 89)
- **Session:** 89
- **Spawned By:** INV-017
- **Context:** ReasoningBank tracks failures but failure_reason was NULL. Root cause: INSERT omitted the column despite error_details being available.
- **Fix:** Added failure_reason to INSERT in retrieval.py:record_reasoning_trace()
- **Effort:** Small
- **Related:** [INV-017, ReasoningBank]
- **Plan:** `docs/plans/PLAN-E2-103-populate-failurereason-in-stop-hook.md`
- **Memory:** 76861-76864

<!-- Archived: 2025-12-20 via /close (Session 89) -->
### [COMPLETE] E2-097: Cycle Events Integration
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-17
- **Closed:** 2025-12-20 (Session 89)
- **Session:** 83
- **Milestone:** M3-Cycles
- **blocked_by:** [E2-091, E2-096]
- **Context:** Log cycle state transitions to haios-events.jsonl for observability.
- **Deliverables:**
  - [x] Log `cycle_transition` events (from_state, to_state, backlog_id)
  - [x] Add `just cycle-events` recipe to show cycle events
  - [x] PostToolUse hook detects lifecycle_phase changes
- **Effort:** Small
- **Related:** [E2-084, E2-091]
- **Plan:** `docs/plans/PLAN-E2-097-cycle-events-integration.md`
- **Memory:** 76839

<!-- Archived: 2025-12-20 via /close (Session 89) -->
### [COMPLETE] E2-093: Preflight Checker Subagent
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-17
- **Closed:** 2025-12-20 (Session 89)
- **Session:** 83
- **Milestone:** M3-Cycles
- **blocked_by:** [E2-091]
- **Context:** Isolated subagent for PLAN->DO transition. Validates plan readiness and enforces DO phase guardrails (>3 file gate).
- **Deliverables:**
  - [x] Create `.claude/agents/preflight-checker.md`
  - [x] Tools: Read, Glob (minimal, read-only)
  - [x] Check plan sections filled (not placeholders)
  - [x] Verify status is approved
  - [x] >3 files triggers confirmation requirement
- **Effort:** Small
- **Related:** [E2-091, schema-verifier]
- **Plan:** `docs/plans/PLAN-E2-093-preflight-checker-subagent.md`
- **Memory:** 76827-76832

<!-- Archived: 2025-12-20 via /close (Session 89) -->
### [COMPLETE] E2-092: /implement Command
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-17
- **Closed:** 2025-12-20 (Session 89)
- **Session:** 83
- **Milestone:** M3-Cycles
- **blocked_by:** [E2-091]
- **Context:** Command wrapper that loads implementation-cycle skill, accepts backlog_id, triggers cycle start.
- **Deliverables:**
  - [x] Create `.claude/commands/implement.md`
  - [x] Frontmatter: allowed-tools, argument-hint
  - [x] Load implementation-cycle skill on invocation
  - [x] Pass $1 as backlog_id
  - [x] Trigger PLAN state entry
- **Effort:** Small
- **Related:** [E2-091]
- **Plan:** `docs/plans/PLAN-E2-092-implement-command.md`
- **Memory:** 76822

<!-- Archived: 2025-12-20 via /close (Session 88) -->
### [COMPLETE] E2-FIX-004: Fix Synthesis Query Ordering Bug
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-20
- **Closed:** 2025-12-20 (Session 88)
- **Session:** 88
- **Spawned By:** INV-019
- **Context:** Synthesis query uses `ORDER BY id ASC LIMIT 1000`, always selecting concepts 1-1000 and never reaching 60k+. Progress tracking also broken (`synthesized_at` not set but query checked it).
- **Root Cause:** synthesis.py:109-116 - query filtered on `synthesized_at IS NULL` but store_synthesis set `synthesis_cluster_id`.
- **Fix:** Added `AND c.synthesis_cluster_id IS NULL` to WHERE clause (2 lines)
- **Impact:** 53,545 concepts now reachable (was only ~6,765 repeatedly)
- **Plan:** `docs/plans/PLAN-E2-FIX-004-fix-synthesis-query-ordering-bug.md`
- **Related:** INV-019, PLAN-SYNTHESIS-001, E2-FIX-001
- **Memory:** concepts 72741-72748 (WHY)
- **DoD:** Tests (41), WHY captured, docs current, plan complete

<!-- Archived: 2025-12-20 via /close (Session 88) -->
### [COMPLETE] INV-019: Synthesis Coverage Gap - Query Ordering Bug
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-20
- **Closed:** 2025-12-20 (Session 88)
- **Session:** 88
- **Investigation:** `docs/investigations/INVESTIGATION-INV-019-synthesis-coverage-gap-query-ordering-bug.md`
- **Context:** During Session 88 introspection, discovered synthesis only covers 11% of ancient memory (1-60k) and 0% of recent memory (60k+).
- **Findings:**
  - 6,767 unique sources used in synthesis (of 60,000 ancient concepts)
  - 99.6% of clustering happens in concepts 1-10,000
  - Query/store column mismatch (synthesized_at vs synthesis_cluster_id)
- **Root Cause:** synthesis.py:109-116 query ordering + progress tracking gap
- **Spawned:** E2-FIX-004 (fix implemented)
- **Related:** PLAN-SYNTHESIS-001, E2-FIX-001
- **Memory:** concepts 72741-72748 (shared with E2-FIX-004)

<!-- Archived: 2025-12-14 via /close (Session 74) -->
### [COMPLETE] E2-063: Query Rewriting Layer
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-14
- **Closed:** 2025-12-14 (Session 74)
- **Session:** 73, 74
- **Spawned By:** INV-015
- **Context:** Transform conversational prompts to technical queries using Gemini API before embedding. Addresses INV-015 H1 (raw prompts are poor queries).
- **Plan:** `docs/plans/PLAN-E2-063-query-rewriting-layer.md`
- **Implementation:** Uses gemini-2.5-flash-lite for query rewriting with domain-grounded prompt and few-shot examples.
- **Related:** INV-015, ADR-037
- **Memory:** concepts 71451-71463 (WHY), closure concept pending
- **DoD:** Tests (207), WHY captured, docs current, plan complete

### [COMPLETE] E2-001: Memory-Governance Integration (Umbrella - Decomposed)
- **Status:** closed
- **Owner:** Hephaestus
- **Created:** 2025-12-06
- **Closed:** 2025-12-09 (Session 52)
- **Plan:** PLAN-EPOCH2-008-MEMORY-LEVERAGE.md
- **Context:** Original umbrella was too broad. Decomposed into targeted items.

#### Completed Sub-items:
- [x] P1.1: /coldstart queries memory (coldstart.md line 17)
- [x] MCP Tool Consolidation (Session 48) - deprecate memory_store, update memory-agent skill

#### Decomposed Into:
- **E2-026:** /haios memory_stats (from P1.2)
- **E2-027:** Checkpoint → memory with session tag (from P1.3, refined)
- **INV-003:** Strategy extraction quality (P3.1 merged)
- **DROPPED:** P2.1 (file modification indexing) - superseded by haios-status.json
- **E2-014:** Stop hook → ingester_ingest (already existed)

### [COMPLETE] E2-002: PM Directory Self-Awareness Wiring
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-07
- **Completed:** 2025-12-09 (Session 52)
- **Context:** Wire backlog.md into /coldstart, /haios, and memory sync hooks
- **Enhancement:** /coldstart should invoke /haios for unified init (Session 40 insight)
- **Memory:** Concept 62540
- **Resolution:** Achieved via `haios-status.json` which:
  - Parses backlog.md for active_count, by_priority, last_session
  - Surfaces in /coldstart via workspace section
  - Displays in /haios PM section
  - Auto-updated by UpdateHaiosStatus.ps1

### [COMPLETE] E2-003: Additional Governed Paths
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-07
- **Completed:** 2025-12-09 (Session 52)
- **Session:** 45 (priority bump)
- **Plan:** PLAN-E2-003-ADDITIONAL-GOVERNED-PATHS.md
- **Context:** Add ADR, TRD, README governance with appropriate commands
- **Trigger:** ADR-031 written without governance - gap demonstrated
- **Deliverables:**
  - [x] `/new-adr` command with template scaffolding
  - [x] PreToolUse block for `docs/ADR/*.md`
  - [x] ScaffoldTemplate.ps1 updated to include `architecture_decision_record`
  - [x] CLAUDE.md updated with `/new-adr` documentation
  - [ ] Consider TRD, README governance (deferred per DD-003-03)

### [COMPLETE] E2-005: haios-status.json Auto-Update
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-07
- **Completed:** 2025-12-07 (Session 40)
- **Context:** Eliminate manual status updates. Auto-derive from templates, memory, backlog, checkpoints.
- **Deliverable:** `.claude/hooks/UpdateHaiosStatus.ps1`
- **Features:** 7 data sources, live file tracking, backlog alignment checks

### [COMPLETE] E2-006: File Lifecycle Governance
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-07
- **Completed:** 2025-12-07 (Session 41)
- **Context:** Standardize document phases (OBSERVE->CAPTURE->DECIDE->PLAN->EXECUTE->VERIFY). Create templates for each phase.
- **Implementation:**
  - 5 templates updated with lifecycle_phase defaults (checkpoint=capture, plan=plan, report=capture, handoff_investigation=observe, ADR=decide)
  - Validator updated: all 14 types now accept lifecycle_phase and subtype
  - UpdateHaiosStatus.ps1 enhanced with counts_by_phase tracking
  - ADR-030 (Option D - Hybrid Taxonomy) provides foundation

### [COMPLETE] E2-007: Error Capture Hook
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-07
- **Completed:** 2025-12-13 (Session 69)
- **Session:** 39, 58 (refocused), 69 (implemented)
- **Plan:** PLAN-E2-007-ERROR-CAPTURE-HOOK.md
- **Context:** Build hooks that leverage Claude's tendencies.
- **Original Scope (Session 39):** (1) Schema injection, (2) Error-to-memory, (3) Retry breaker
- **Audit (Session 58):** Schema injection SUPERSEDED by E2-020 (PreToolUse + schema-verifier). Refocused to error capture only.
- **Implementation (Session 69):**
  - ErrorCapture.ps1 - PostToolUse hook for error detection
  - error_capture.py - Python storage via ingester_ingest
  - Test-ErrorCapture.ps1 - 8 tests passing
  - Configured in settings.local.json (matcher: Bash|Read|Write|Edit|Grep|Glob)
- **Memory:** Concepts 62530, 62531 (design), 71247-71255 (closure)

### [COMPLETE] E2-009: Lifecycle Sequence Enforcement
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-07
- **Completed:** 2025-12-11 (Session 63)
- **Session:** 40, 58 (refined), 61 (redesigned), 63 (implemented)
- **Plan:** PLAN-E2-009-LIFECYCLE-SEQUENCE-ENFORCEMENT.md
- **Unblocked By:** E2-032 (ADR-034 Implementation - Session 62)
- **Context:** Enforce ADR-034 canonical lifecycle sequence. Agents should complete discovery before planning.
- **Original Vision (Session 40):** "Plan-First" enforcement
- **Redesign (Session 61):** Expanded to full lifecycle sequence enforcement per ADR-034
- **Implementation (Session 63):** UserPromptSubmit hook Part 3 added
- **Lifecycle:** BACKLOG -> DISCOVERY -> DESIGN -> PLAN -> IMPLEMENT -> VERIFY -> CLOSE
- **Mechanism:** UserPromptSubmit hook detects plan-creation intent, checks for prerequisite INVESTIGATION-* or ADR-*, injects guidance if missing
- **Override:** "skip discovery", "skip investigation", "trivial", "quick fix" in message bypasses check
- **Memory:** Concept 62543

### [COMPLETE] E2-011: Process Observability
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-07
- **Completed:** 2025-12-07 (Session 43-44)
- **Plan:** PLAN-INVESTIGATION-MEMORY-PROCESS-OBSERVABILITY.md
- **Context:** Long-running processes (synthesis, cross-pollination) have no progress visibility. Operator cannot tell if process is working or stuck.
- **Trigger:** Cross-pollination ran 40+ min with no output after initial log.
- **Phases:**
  - [x] Phase 1a: CRITICAL - Comparison loop progress (synthesis.py) - Session 43
  - [x] Phase 1b: HIGH - Clustering function progress - Session 44
  - [x] Phase 2: HIGH - Background job registry (job_registry.py) - Session 44
  - [x] Phase 3: HIGH - System health checks (health_checks.py) - Session 44
  - [x] Phase 4: HIGH - Enhanced /status command - Session 44
- **Deliverables:**
  - synthesis.py: Progress logging in comparison loop and clustering
  - haios_etl/job_registry.py: Background job tracking (12 tests)
  - haios_etl/health_checks.py: DB/Memory/MCP health (13 tests)
  - .claude/commands/status.md: Enhanced with health and jobs
- **Memory:** Concept 62599

### [COMPLETE] E2-012: Synthesis Cross-Pollination Enhancement
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-07
- **Completed:** 2025-12-07 (Session 43)
- **Plan:** PLAN-SYNTHESIS-CROSS-POLLINATION-ENHANCEMENT.md
- **Context:** Enable idempotent cross-pollination with --cross-only, --max-bridges, sample params
- **Deliverables:** _bridge_exists() idempotency, 4 new CLI args, 8 new tests

### [COMPLETE] E2-013: Workspace Awareness (ADR-031)
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-07
- **Completed:** 2025-12-08 (Session 47)
- **Plan:** PLAN-ADR-031-IMPLEMENTATION.md
- **ADR:** docs/ADR/ADR-031-workspace-awareness.md
- **Context:** HAIOS operational self-awareness - system knows outstanding work, stale items, workspace state.
- **Phases:**
  - [x] Phase 1: Draft ADR-031 (Session 45)
  - [x] Phase 2: Operator approval (Session 47)
  - [x] Phase 3: Implement workspace functions in UpdateHaiosStatus.ps1 (Session 47)
  - [x] Phase 4: Create /workspace command (Session 47)
  - [x] Phase 5: Integrate with /coldstart (Session 47)
- **Deliverables:**
  - `Get-OutstandingItems`, `Get-StaleItems`, `Get-WorkspaceSummary` functions
  - `workspace` section in haios-status.json
  - `/workspace` command
  - Updated `/coldstart` with workspace status
  - 13 unit tests passing
- **Enables:**
  - ADR-032: File Lifecycle Governance
  - ADR-033: Work Cycle Governance (OADEV)
  - E2-014: Hook Framework (now unblocked)
- **Memory:** Concept 64601

### [COMPLETE] E2-014: Hook Framework (Config-Driven Governance)
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-08
- **Completed:** 2025-12-13 (Session 69)
- **Session:** 46-47, 65, 69
- **Unblocked by:** E2-013 completion (Session 47)
- **Transformed By:** E2-037 (RFC 2119 Governance Signaling) - Session 65
- **Context:** Current PreToolUse.ps1 has hardcoded governed paths. Vision: checks should be in configuration artifact, not code.
- **Memory References:** Concepts 37910, 37935, 10452, 71241-71246 (closure rationale)
- **Session 65 Insight:** E2-037 introduces RFC 2119 signals in CLAUDE.md as the "governing configuration artifact" for Claude's semantic behavior. This TRANSFORMS E2-014's scope:
  - **Absorbed by E2-037:** Agent behavioral signals (MUST/SHOULD/MAY for commands/skills/agents)
  - **Retained in E2-014:** Hook refactoring, MCP tool governance, mechanical enforcement
- **Deliverables (Revised):**
  - [x] Agent governance signals → MOVED to E2-037 (RFC 2119 in CLAUDE.md)
  - [~] Refactor PreToolUse.ps1 to read governed paths from config (OPTIONAL - current hardcoding works)
  - [x] Add MCP tool governance (CLAUDE.md line 330: memory_store DEPRECATED, ingester_ingest PRIMARY)
  - [~] `governance.json` for mechanical enforcement rules (OPTIONAL - hooks work without it)
- **Closure Note:** Required deliverables complete. Optional items ([~]) remain available for future enhancement but don't block closure.
- **Use Cases:**
  - Governed paths (current: checkpoints, plans, handoffs, reports)
  - MCP tool consolidation (`ingester_ingest` supersedes `memory_store`)
  - Hook-MCP integration (Stop hook -> ingester_ingest for learnings)
- **Session 47 Insight:** `memory_store` has parameter issues (metadata JSON string), `ingester_ingest` is more capable (auto-classify, entity extraction, provenance tracking)
- **Vision:** Adding new governance = edit config, not code. E2-037 fulfills this for semantic (Claude) governance; E2-014 focuses on mechanical (hook) governance.

### [COMPLETE] E2-015: Lifecycle ID Propagation
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-08
- **Completed:** 2025-12-08 (Session 49)
- **Plan:** PLAN-E2-015-LIFECYCLE-ID-PROPAGATION.md
- **Session:** 48-49
- **Related:** E2-001 (Memory-Governance Integration)
- **Context:** Backlog items (E2-xxx) need traceable linkage to all lifecycle documents (plans, checkpoints, reports, handoffs). Previously broken - haios-status.json showed all `backlog_id: null`.
- **Problem Analysis (Session 48):**
  - UpdateHaiosStatus.ps1 extracted backlog IDs from backlog.md
  - Matching logic only ran for draft/proposed status files
  - Approved/complete plans never got linked
  - PM section provided counts but no actionable traceability
- **Solution:** Explicit `backlog_id` field in frontmatter, propagated by scaffold commands
- **Design Decisions:**
  - DD-015-01: Command signature `/new-plan <backlog_id> <title>` (explicit link required)
  - DD-015-02: Checkpoints include `backlog_ids` array (sessions may cover multiple items)
  - DD-015-03: Validation BLOCKS documents missing backlog_id in governed paths
  - DD-015-04: Retrofit existing PLAN-E2-xxx files with backlog_id field
  - DD-015-05: Parse from YAML frontmatter, not filename
- **Deliverables:**
  - [x] Update `/new-plan` command to require backlog_id
  - [x] Add `backlog_id` to implementation_plan template
  - [x] Add `backlog_ids` to checkpoint OptionalFields in ValidateTemplate.ps1
  - [x] Update PreToolUse.ps1 to validate backlog_id presence for plans
  - [x] Update UpdateHaiosStatus.ps1 to parse backlog_id from YAML (not filename)
  - [x] Retrofit existing PLAN-E2-xxx plans with backlog_id field (10 files)
  - [x] 8 TDD tests passing
- **Enables:**
  - Forward tracing: What plans/checkpoints exist for E2-001?
  - Backward tracing: What backlog item does this checkpoint relate to?
  - Completion detection: All plans for E2-001 with status=complete?
  - PM section now shows actual backlog_id values for retrofitted plans

### [COMPLETE] E2-022: Epistemic State Transformation
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-09
- **Completed:** 2025-12-09 (Session 51)
- **Context:** Transform epistemic_state.md from 600+ line history log to slim Operational Self-Awareness Registry.
- **Key Insight:** Agent behavioral patterns (assume over verify, generate over retrieve, move fast, optimistic confidence) are FEATURES of the architecture, not bugs. System should leverage them via hooks/commands/enforcement.
- **New Purpose:**
  - Surface known behavioral anti-patterns with mitigations
  - Track active knowledge gaps with backlog refs
  - Document recently surfaced issues
- **Deliverables:**
  - [x] Archive original to `docs/archive/epistemic_state_v1_2025-12-09.md`
  - [x] Create new slim format with anti-patterns table, knowledge gaps, mitigation mechanisms
  - [x] Include memory references and backlog links for traceability
- **Memory:** Concept 64678 (transformation decision)

### [COMPLETE] E2-020: Schema Discovery via Mechanisms
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-09
- **Completed:** 2025-12-09 (Session 51), **Fixed:** 2025-12-09 (Session 53)
- **Session:** 50-51, 53
- **Plan:** PLAN-E2-020-SCHEMA-DISCOVERY.md
- **Context:** Agent assumes column/table names, wastes queries on schema errors.
- **Original Solution (S51):** Subagent + Skill + Bash (sqlite3) - BROKEN (hook blocked subagent, sqlite3 not on PATH)
- **Fixed Solution (S53):** MCP abstraction layer:
  - **MCP Tool:** `schema_info(table_name)` - portable schema introspection
  - **MCP Tool:** `db_query(sql)` - read-only SELECT queries
  - **Hook (PreToolUse):** Blocks ALL direct SQL, forces MCP usage
  - **Subagent (schema-verifier):** Uses MCP tools (not Bash)
  - **Command (/schema):** Uses MCP tool
- **Key Insight:** MCP provides abstraction for DB migration (SQLite -> Postgres)
- **Deliverables:**
  - [x] `.claude/skills/schema-ref/SKILL.md` (updated to reference MCP)
  - [x] `.claude/agents/schema-verifier.md` (uses MCP tools)
  - [x] PreToolUse.ps1 SQL blocking (unchanged)
  - [x] `/schema` command (uses MCP)
  - [x] CLAUDE.md updated with subagent section
  - [x] `haios_etl/database.py` - `get_schema_info()`, `query_read_only()` methods
  - [x] `haios_etl/mcp_server.py` - `schema_info`, `db_query` MCP tools
- **Memory:** Concepts 64679-64727 (investigation, pattern, correct usage)

### [COMPLETE] E2-023: Work Loop Closure Automation
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-09
- **Session:** 51, 57-58
- **Plan:** PLAN-E2-023-CLOSE-COMMAND.md
- **Context:** Closing work loops is manual - plan status, backlog status, memory storage done separately.
- **Problem:** Agent must remember to update multiple locations when completing work. Easy to miss.
- **Decision (Session 57):** Option A - `/close` command. ADR-033 defines DoD requirements.
- **`/close <backlog_id>` Command Specification:**
  1. Lookup documents via `work_items` tree in haios-status.json
  2. Validate DoD (per ADR-033):
     - All associated plans have status: complete
     - Prompt user to confirm: tests pass, WHY captured, docs current
  3. If DoD passes:
     - Update backlog.md entry status to `complete`
     - Update all associated plan files to status: `complete` (if not already)
     - Store completion summary via `ingester_ingest` with source_path: `closure:<backlog_id>`
     - Run UpdateHaiosStatus.ps1 to refresh work_items tree
  4. Report closure with memory concept IDs
- **Deliverables:**
  - [x] Design decision: Option A - `/close` command (Session 57)
  - [x] Create `/close` command in `.claude/commands/close.md` (Session 58)
  - [x] Implement DoD validation logic (prompt-based, not blocking) (Session 58)
  - [x] Test with E2-031 closure (Session 58)
  - [x] CLAUDE.md documentation of closure process (Session 58)
  - [x] Commands README updated (Session 58)
- **Related:** E2-031 (ADR-033 DoD definition), ADR-033
- **Memory:** Concepts 64728-64735
- **Closed:** 2025-12-10 (Session 58)

### [COMPLETE] E2-026: /haios Memory Stats Display
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-09
- **Completed:** 2025-12-09 (Session 52)
- **Session:** 52
- **Derived From:** E2-001 P1.2
- **Context:** /haios has `mcp__haios-memory__memory_stats` in allowed-tools but doesn't use it.
- **Deliverable:** Update haios.md to call memory_stats() and display in dashboard
- **Resolution:** Added step 3 to haios.md instructing to call memory_stats for live counts

### [COMPLETE] E2-027: Checkpoint Session Insights to Memory
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-09
- **Completed:** 2025-12-09 (Session 53)
- **Session:** 52-53
- **Derived From:** E2-001 P1.3 (refined)
- **Context:** Checkpoints capture session learnings but only in files. Want insights queryable and cross-connectable.
- **Core Want:** "Don't miss reasoning insights. Cross-connect with originating file and other insights."
- **Design:**
  - When checkpoint created, extract key insights (Summary + Key Findings sections)
  - Store to memory via `ingester_ingest` with `source_path: checkpoint:session-NN`
  - Enables: "What did session 52 learn?" query
  - Enables: Cross-pollination connects session insights to other concepts
- **Deliverables:**
  - [x] Update /new-checkpoint command to prompt for key insights
  - [x] Store insights via ingester_ingest with session provenance
  - [x] Verify retrieval: concepts 64766-64772 stored for Session 53
- **Memory:** Session 52 discussion, Session 53 concepts 64766-64772

### [COMPLETE] E2-030: Template Registry Review
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-10
- **Completed:** 2025-12-13 (Session 70)
- **Session:** 56, 70
- **Investigation:** INVESTIGATION-E2-030-template-registry-audit.md
- **Context:** 14 template types in validator, but some may be unused or redundant.
- **Resolution:** Audited all 14 types. Reduced to 7 core types (checkpoint, implementation_plan, architecture_decision_record, investigation, report, readme, backlog_item). Removed 8 unused/deprecated types.
- **Memory:** Concepts 71275-71283
- **Questions:**
  - Is `directive` template still needed? (No `/new-directive` command)
  - Is `verification` template used? (No governed path)
  - Should `proposal` be merged with another type?
  - Are all status values appropriate for each template?
- **Deliverables:**
  - [ ] Audit each template type for usage (grep codebase)
  - [ ] Identify templates without corresponding commands
  - [ ] Propose consolidation or deprecation
  - [ ] Update ValidateTemplate.ps1 if types removed
- **Related:** E2-029 (New Backlog Command), E2-008 (Schema Sync)

### [COMPLETE] E2-031: Work Item Lifecycle Governance
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-10
- **Session:** 56-57
- **ADR:** ADR-033 (accepted 2025-12-10)
- **Context:** No formal definition of work item lifecycle from birth (backlog) to death (complete). Templates work well individually but lack parent-child tracking and unified completion criteria.
- **Problem Statement:**
  - Backlog item spawns plan, checkpoints, handoffs, ADRs - but no genealogy tracking
  - "Done" is ambiguous - code works? tests pass? docs updated? WHY captured?
  - Complex plans become mega-files with no phase management
  - Checkpoint template missing `backlog_ids` field (E2-015 gap - now fixed)
- **Definition of Done (DoD) - ACCEPTED (ADR-033):**
  1. **Tests pass** - Automated verification
  2. **WHY captured** - Not just WHAT and HOW, but reasoning preserved
  3. **Documentation current** - CLAUDE.md, epistemic_state, READMEs updated
  4. **Traced files complete** - All spawned docs (plans, checkpoints, handoffs) show completion
- **Deliverables:**
  - [x] ADR-033: Work Item Lifecycle (Session 57)
  - [x] Add `backlog_ids` to checkpoint template (Session 56)
  - [x] Add `parent_id` to validator for checkpoint/plan (Session 56)
  - [x] Status normalization: `complete` across all templates (Session 57)
  - [x] Add `backlog_ids` to report, handoff, handoff_investigation, ADR, proposal (Session 57)
  - [x] Progress Tracker section in plan template (Session 57)
  - [x] /new-checkpoint enhancement for parent plan linking (Session 57)
  - [x] Document WHY capture workflow in CLAUDE.md (Session 57)
  - [x] UpdateHaiosStatus.ps1: Build work item trees in haios-status.json (Session 57)
  - [x] /close <backlog_id> command for DoD enforcement (moved to E2-023)
- **Related:** E2-015 (Lifecycle ID Propagation), E2-029 (New Backlog Command), E2-030 (Template Review), E2-023 (Work Loop Closure)
- **Memory:** Concepts 65008-65041 (Session 56-57)
- **Closed:** 2025-12-10 (Session 58)

### [COMPLETE] E2-032: ADR-034 Implementation (Ontology Cleanup)
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-11
- **Completed:** 2025-12-11 (Session 62)
- **Session:** 61-62
- **Spawned By:** INV-006 (Document Ontology Audit)
- **ADR:** ADR-034 (accepted 2025-12-11)
- **Context:** ADR-034 defined canonical lifecycle and deprecated handoff documents.
- **Deliverables:**
  - [x] Created `investigation` template (.claude/templates/investigation.md)
  - [x] Created `/new-investigation` command (.claude/commands/new-investigation.md)
  - [x] Created `docs/investigations/` directory with README
  - [x] Deprecated `handoff_investigation` template (added deprecation notice)
  - [x] Updated ValidateTemplate.ps1 with `investigation` template type
  - [x] Updated CLAUDE.md with canonical prefix guidance (ADR-034 section)
  - [x] Updated `.claude/templates/README.md` with deprecation notes
- **Unblocks:** E2-009 (Lifecycle Sequence Enforcement)
- **Related:** INV-006, ADR-034, E2-009
- **Memory:** Concepts 70689-70691

### [COMPLETE] E2-036: UpdateHaiosStatus Regex Pattern Fix
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-13
- **Completed:** 2025-12-13 (Session 65)
- **Session:** 65
- **Spawned By:** Session 64-65 investigation (E2-FIX-002 not tracked in work_items)
- **Context:** `/close E2-FIX-002` failed because work item not in haios-status.json despite plan/investigation files existing.
- **Root Cause:** UpdateHaiosStatus.ps1 uses rigid regex patterns that only match `E2-\d{3}` format:
  ```powershell
  # Line 168: Get-BacklogStats
  (E2-\d{3}|TD-\d{3}|INV-\d{3})

  # Line 219: Get-LiveFiles
  backlog_id:\s*(E2-\d{3})

  # Line 464: Build-WorkItemTrees (backlog_id)
  backlog_id:\s*(E2-\d{3}|TD-\d{3}|INV-\d{3})

  # Line 472: Build-WorkItemTrees (backlog_ids)
  (E2-\d{3}|TD-\d{3}|INV-\d{3})
  ```
- **Missing Patterns:** E2-FIX-XXX, E2-TD-XXX, any variant with hyphenated prefix
- **Fix Scope:**
  - [x] Update 4 regex patterns to: `E2-[A-Z]*-?\d{3}` (matches E2-007, E2-FIX-002, etc.)
  - [x] Test with existing items (E2-007, E2-020) and new format (E2-FIX-002)
  - [x] Re-run UpdateHaiosStatus.ps1 and verify work_items includes E2-FIX-XXX
- **Verification:** E2-FIX-001 and E2-FIX-002 now appear in haios-status.json work_items
- **Effort:** Low (30 min) - Actual: ~10 min
- **Unblocks:** E2-034 (Cold Start Optimization)
- **Related:** E2-034 (Cold Start Optimization)

### [COMPLETE] E2-008: Template Validation Schema Sync
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-07
- **Completed:** 2025-12-07 (Session 40)
- **Context:** Validator didn't recognize several types. Added missing types with proper analysis.
- **Analysis:** Compared structures of disputed types (handoff, handoff_investigation, proposal) - confirmed distinct.
- **Migration:** 3 files moved from `investigation_handoff` → `handoff_investigation` (canonical name).
- **Types Added:** handoff, handoff_investigation, proposal (14 total now)

---

## Technical Debt

### [COMPLETE] E2-FIX-001: Synthesis Embedding Gap
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-11
- **Completed:** 2025-12-12 (Session 63)
- **Session:** 59, 63
- **Plan:** PLAN-E2-FIX-001-SYNTHESIS-EMBEDDING-GAP.md
- **Context:** INV-005 found 2,265 synthesized concepts (99.91%) have NO embeddings - invisible to retrieval.
- **Root Cause:** `synthesis.py:store_synthesis()` creates concepts but never generates embeddings.
- **Evidence:** `collaboration.py:_handle_ingester()` correctly embeds ingested content (lines 239-254).
- **Resolution:** synthesis.py now generates embeddings. 806/806 SynthesizedInsight = 100% coverage.
- **Memory:** Concepts 65070-65071 (INV-005 findings)

### [COMPLETE] E2-FIX-002: Ingester Embedding Gap
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-13
- **Completed:** 2025-12-13 (Session 64)
- **Session:** 64
- **Spawned By:** Session 63 verification (discovered during overnight synthesis check)
- **Investigation:** INVESTIGATION-E2-FIX-002-ingester-embedding-gap.md
- **Plan:** PLAN-E2-FIX-002-ingester-embedding-fix.md
- **Context:** Session 63 verified synthesis embedding fix, but discovered ingester.py does NOT embed concepts.
- **Root Cause:** `haios_etl/agents/ingester.py` lines 160-170 inserted concepts without embedding generation. Ingester class had no ExtractionManager reference.
- **Resolution:**
  - [x] Added `extractor` parameter to Ingester.__init__()
  - [x] Added embedding generation after each insert_concept()
  - [x] Added insert_concept_embedding() to database.py
  - [x] Updated mcp_server.py to pass extraction_manager
  - [x] 4 new tests added (23 total ingester tests pass)
- **Memory:** Concepts 70882-70890 (closure:E2-FIX-002)
- **Note:** Backfill of existing 3,177 unembedded concepts is separate effort (E2-017)
- **Related:** E2-FIX-001 (synthesis side), E2-017 (concept embedding completion)

### [COMPLETE] INV-005: Memory System Reality Check
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-10
- **Session:** 58
- **Context:** We talk about "ReasoningBank", "vectors", "knowledge graphs", "cross-pollination". Is any of it actually working, or is it theater?
- **Core Question:** Are we using what we have sufficiently well?
- **Recon Findings (Session 58):**
  - Strategies: Mixed quality. "Avoid SQL queries" useful, "Leverage hybrid search" generic. Case dupes exist.
  - Cross-pollination: 2,110 clusters synthesized BUT NOT IN RETRIEVAL PATH. Dead code?
- **Investigation Scope:**
  1. **Retrieval audit:** What does `memory_search_with_experience` actually return? Concepts only? Traces? Synthesized insights?
  2. **Cross-poll dead code check:** Are synthesized_concept_ids queryable or orphaned?
  3. **Value assessment:** Sample retrievals - do they help agents make decisions?
  4. **Architecture review:** Compare current implementation to original vision docs
- **Reference Documents (ancient work to potentially synthesize):**
  - `docs/COGNITIVE_MEMORY_SYSTEM_SPEC.md` - Original vision
  - `docs/specs/TRD-VALIDATION-AGENT-v1.md` - Validation agent spec
  - `docs/specs/TRD-SYNTHESIS-EXPLORATION.md` - Synthesis design
  - `docs/specs/TRD-REFINEMENT-v1.md` - Refinement spec
  - `docs/risks-decisions/RD-001-llm-non-determinism.md` - Known risks
  - `docs/risks-decisions/RD-004-sqlite-limitations.md` - DB constraints
  - `docs/reports/2025-12-04-REPORT-toon-serializer.md` - Optimization work
  - `docs/reports/2025-12-04-REPORT-multi-index-architecture.md` - Index design
  - `docs/reports/2025-12-04-REPORT-validation-agent.md` - Validation work
  - `haios_etl/agents/interpreter.py` - Interpreter agent code
  - `haios_etl/agents/collaboration.py` - Collaboration agent code
- **Output:** Reality assessment + actionable recommendations (fix, deprecate, or document as aspirational)
- **Subsumes:** INV-003 (strategy quality), INV-004 (cross-poll effectiveness)

### [COMPLETE] INV-007: Work Item Spawning Patterns
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-11
- **Completed:** 2025-12-11 (Session 62)
- **Session:** 61-62
- **Spawned By:** Session 61 insight during INV-006 closure
- **Context:** Session 61 revealed that INV-006 spawned multiple outputs (ADR-034, E2-032, E2-009 unblock) but this relationship pattern wasn't captured.
- **Findings:**
  - **Vertical spawning** (containment): Documents belong to work items - governed by ADR-033 parent_id/backlog_ids
  - **Horizontal spawning** (generation): Work items create new work items - previously ungoverned
  - **Closure Completeness Constraint:** Investigations cannot close until spawned items exist and link back
- **Output:** ADR-033 Section 2b amendment (Sibling Spawning)
- **Deliverables:**
  - [x] ADR-033 amended with Section 2b (Sibling Spawning)
  - [x] ValidateTemplate.ps1: Added spawned_by, blocks, blocked_by to backlog_item OptionalFields
  - [x] Memory storage: Concepts 70685-70688
- **Memory:** Concepts 70685-70688

### [COMPLETE] INV-006: Document Ontology & Work Lifecycle Audit
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-11
- **Session:** 60
- **Context:** Before redesigning E2-009 (Plan-First Enforcement), need clarity on what lifecycle phases exist and what artifacts belong to each.
- **Problem Statement:**
  - Current naming chaos: INVESTIGATION vs INQUIRY vs RESEARCH (same phase?)
  - Template mismatch: `handoff` vs `handoff_investigation` vs `directive` for analysis work
  - Lifecycle undefined: Backlog → ??? → Spec → Plan → Implement → Verify → Close
  - Analysis/Discovery phase exists but has no canonical name or artifact
- **Audit Scope:**
  1. **File prefix inventory:** All unique prefixes (INVESTIGATION, TASK, INQUIRY, etc.)
  2. **Template-to-phase mapping:** Which templates serve which lifecycle phase?
  3. **Lifecycle phase proposal:** Define canonical phases and their artifacts
  4. **Ontology cleanup:** Propose canonical names, deprecate synonyms
- **Current Mess (Session 60 audit):**
  - 14+ distinct file prefixes (INVESTIGATION, TASK, INQUIRY, EVALUATION, VALIDATION, COMPLETION, GAP-CLOSER, PROTOTYPE, PROPOSAL, RESEARCH, etc.)
  - Templates don't map 1:1 to lifecycle phases
  - No clear distinction between: analysis types (INV vs INQUIRY), task types (TASK vs DIRECTIVE), report types (EVALUATION vs VALIDATION vs COMPLETION)
- **Proposed Lifecycle (to validate):**
  ```
  Backlog Item → Analysis/Discovery → Spec/Design → Plan → Implementation → Verification → Close
  ```
- **Output:** ADR-034 proposal with clean ontology, template mapping, and lifecycle phase definitions
- **Blocks:** E2-009 redesign (need lifecycle clarity first)

### [COMPLETE] INV-003: Strategy Extraction Quality Audit
- **Status:** subsumed
- **Owner:** Hephaestus
- **Created:** 2025-12-09
- **Subsumed By:** INV-005 (Memory System Reality Check) - Session 58
- **Context:** Strategies are meta-level, not domain-specific.
- **Recon (Session 58):** Mixed quality. Some useful ("Avoid SQL queries"), some generic. Case dupes.
- **Memory:** Concepts 64641-64652

### [COMPLETE] INV-004: Cross-Pollination Effectiveness
- **Status:** subsumed
- **Owner:** Hephaestus
- **Created:** 2025-12-09
- **Subsumed By:** INV-005 (Memory System Reality Check) - Session 58
- **Context:** 2,110 cross clusters created but effectiveness unknown.
- **Recon (Session 58):** Synthesized concepts exist BUT not in retrieval path. Likely dead code.
- **Memory:** Concepts 64641-64652

### [COMPLETE] INV-001: Cross-Pollination Zero Results
- **Status:** complete
- **Owner:** Genesis
- **Closed:** 2025-12-06
- **Resolution:** Deleted garbage traces, lowered threshold to 0.65

### [COMPLETE] INV-002: PreToolUse Hook Capability
- **Status:** complete
- **Owner:** Hephaestus
- **Closed:** 2025-12-07
- **Resolution:** PreToolUse IS supported, was misconfigured. Now working with deny enforcement.

### [COMPLETE] INV-008: haios-status.json Architecture Optimization
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-13
- **Completed:** 2025-12-13 (Session 70)
- **Context:** haios-status.json bloat (1,365 lines, 66% work_items). Pre-computed index is stale cache.
- **Findings:** work_items (895 lines) + lifecycle.live_files (345 lines) = 91% of file. Rarely used data bloating coldstart.
- **Recommendation:** Remove cached indexes, query at runtime. Target: ~120 lines.
- **Spawns:** E2-041, E2-042
- **ADR:** ADR-036 (PM Data Architecture)

### [COMPLETE] INV-009: Backlog Archival Governance
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-13
- **Completed:** 2025-12-13 (Session 70)
- **Context:** backlog.md bloat (961 lines, 70% non-active items). No archival governance.
- **Findings:** 36 non-active items (28 complete, 8 completed, 3 subsumed). Status inconsistency: 8 items use `completed` not `complete`.
- **Recommendation:** Auto-archive on /close. Normalize status during archival.
- **Spawns:** E2-043, E2-044
- **ADR:** ADR-036 (PM Data Architecture)

<!-- Archived: 2025-12-14 via /close -->
### [COMPLETE] E2-042: Update /close to Query Documents at Runtime
- **Status:** complete
- **Priority:** high
- **Owner:** Hephaestus
- **Created:** 2025-12-13
- **Completed:** 2025-12-14 (Session 70)
- **Context:** Part of ADR-036 Phase 1. Replace pre-computed work_items lookup with grep for backlog_id in docs/.
- **Spawned By:** INV-008
- **Blocks:** E2-041 (must update /close before removing work_items)
- **ADR:** ADR-036

<!-- Archived: 2025-12-14 via /close -->
### [COMPLETE] E2-041: Remove work_items from haios-status.json
- **Status:** complete
- **Priority:** high
- **Owner:** Hephaestus
- **Created:** 2025-12-13
- **Completed:** 2025-12-14 (Session 70)
- **Context:** Part of ADR-036 Phase 1. Remove work_items section (895 lines) from UpdateHaiosStatus.ps1.
- **Spawned By:** INV-008
- **ADR:** ADR-036

<!-- Archived: 2025-12-14 via /close -->
### [COMPLETE] E2-043: One-Time Backlog Archival Migration
- **Status:** complete
- **Priority:** medium
- **Owner:** Hephaestus
- **Created:** 2025-12-13
- **Completed:** 2025-12-14 (Session 71)
- **Context:** Part of ADR-036 Phase 2. Migrated 33 non-active items to docs/pm/archive/backlog-complete.md. Normalized status during migration.
- **Spawned By:** INV-009
- **ADR:** ADR-036

<!-- Archived: 2025-12-14 via /close -->
### [COMPLETE] E2-044: Auto-Archive on /close
- **Status:** complete
- **Priority:** medium
- **Owner:** Hephaestus
- **Created:** 2025-12-13
- **Completed:** 2025-12-14 (Session 71)
- **Context:** Part of ADR-036 Phase 2. Updated /close command to auto-archive completed items instead of leaving in backlog.md.
- **Spawned By:** INV-009
- **ADR:** ADR-036

<!-- Archived: 2025-12-14 via /close -->
### [COMPLETE] INV-010: Memory Retrieval Architecture Mismatch
- **Status:** complete
- **Priority:** high
- **Owner:** Hephaestus
- **Created:** 2025-12-14
- **Completed:** 2025-12-14 (Session 72)
- **Session:** 71-72
- **Context:** Coldstart memory injection consumes ~60k tokens but returns philosophically-related rather than task-relevant content. Retrieval optimizes for semantic similarity when coldstart needs temporal recency + actionability.
- **Investigation:** `docs/investigations/INVESTIGATION-INV-010-memory-retrieval-architecture-mismatch.md`
- **Related:** INV-003 (strategy quality), TOON encoding
- **Hypotheses (ALL CONFIRMED):**
  - H1: Static query formulation (CONFIRMED)
  - H2: Semantic similarity bias - filters unused (CONFIRMED)
  - H3: No temporal weighting (CONFIRMED)
  - H4: Embedding distribution skewed - recent 0.5%, older 99.5% (CONFIRMED)
  - H5: Synthesis dilution - 98.6% recent content is SynthesizedInsight (CONFIRMED)
- **Recommendation:** Option B - Hybrid Retrieval Architecture (implemented as ADR-037)
- **Spawned Work:** E2-045, E2-046, E2-047, ADR-037
- **Resolution:** ADR-037 implemented - mode parameter added to search_memories() with session_recovery and knowledge_lookup modes
- **Memory:** Concepts 71410-71414 (Session 72 checkpoint)

<!-- Archived: 2025-12-22 via /close (Session 101) -->
### [COMPLETE] INV-018: Adaptive Coldstart Query Formulation
- **Status:** complete
- **Priority:** medium
- **Owner:** Hephaestus
- **Created:** 2025-12-19
- **Completed:** 2025-12-22 (Session 101 - SUPERSEDED)
- **Session:** 87
- **Investigation:** `docs/investigations/INVESTIGATION-INV-018-adaptive-coldstart-query-formulation.md`
- **Context:** Memory self-critique flagged static query limitation. Investigation superseded by E2-083 implementation which added adaptive query formulation to coldstart.
- **Hypotheses (ALL IMPLEMENTED via E2-083):**
  - H1: Using checkpoint backlog_ids → IMPLEMENTED
  - H2: session_delta.added weighting → IMPLEMENTED
  - H3: Milestone context useful → IMPLEMENTED
  - H4: Two-stage retrieval → PARTIAL (mode=session_recovery)
- **Resolution:** SUPERSEDED by E2-083 implementation in coldstart.md
- **Related:** E2-078, E2-083, ADR-037

<!-- Archived: 2025-12-22 via /close (Session 101) -->
### [COMPLETE] E2-078: Coldstart Work Delta from Checkpoints
- **Status:** complete
- **Priority:** high
- **Owner:** Hephaestus
- **Created:** 2025-12-15
- **Completed:** 2025-12-22 (Session 101 - Implementation Gap Closure)
- **Session:** 76
- **Parent:** E2-076d (Vitals Injection)
- **Context:** Coldstart now reads 2 most recent checkpoints and shows session_delta for momentum awareness.
- **Deliverables (ALL IMPLEMENTED):**
  - [x] coldstart.md reads 2 most recent checkpoints (line 18)
  - [x] session_delta field in haios-status-slim.json
  - [x] Vitals inject delta display
- **Evidence:** coldstart.md line 18, haios-status-slim.json session_delta field
- **Related:** E2-076, E2-076d, E2-076e

<!-- Archived: 2025-12-22 via /close (Session 101) -->
### [COMPLETE] E2-083: Proactive Memory Query (LISTENING)
- **Status:** complete
- **Priority:** medium
- **Owner:** Hephaestus
- **Created:** 2025-12-16
- **Completed:** 2025-12-22 (Session 101 - Implementation Gap Closure)
- **Session:** 78
- **Context:** Memory query now proactive in coldstart, new-plan, and new-investigation commands.
- **Deliverables (ALL IMPLEMENTED):**
  - [x] coldstart.md queries memory with active work context (E2-083: Targeted Query section)
  - [x] new-plan.md queries "implementation planning strategies" (line 23-28)
  - [x] new-investigation.md queries "prior investigations" (line 21-27)
  - [x] memory-agent skill available
- **Evidence:** coldstart.md lines 25-29, new-plan.md lines 23-28, new-investigation.md lines 21-27
- **Related:** E2-021, memory-agent skill, ADR-037

<!-- Archived: 2025-12-22 via /close (Session 101) -->
### [COMPLETE] INV-011: Command-Skill Architecture Gap
- **Status:** complete (PARTIALLY SUPERSEDED)
- **Priority:** high
- **Owner:** Hephaestus
- **Created:** 2025-12-14
- **Completed:** 2025-12-22 (Session 101)
- **Session:** 71
- **Investigation:** `docs/investigations/INVESTIGATION-INV-011-command-skill-architecture-gap.md`
- **Key Insight:** "Command locks you in, skill gives you pattern and tools" - VALID insight
- **Resolution:** Vision valid but implementation diverged. Spawned items (E2-048-051) never created. System evolved with implementation-cycle and investigation-cycle skills as alternative approach. INV-022 (Work-Cycle-DAG) may revisit in Epoch 3.
- **Related:** INV-010, INV-012, INV-022, ADR-036

---

## M3-Cycles: Cycle Framework (Archived)

<!-- Archived: 2025-12-18 via /close (Session 84) -->
### [COMPLETE] E2-091: Implementation Cycle Skill
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-17
- **Closed:** 2025-12-18 (Session 84)
- **Session:** 83 (design), 84 (implementation)
- **Milestone:** M3-Cycles
- **Plan:** `docs/plans/PLAN-E2-091-implementation-cycle-skill.md`
- **Context:** Define the Implementation Cycle as a Skill with progressive disclosure. PLAN-DO-CHECK-DONE workflow with phase-specific tooling.
- **Deliverables:**
  - [x] Create `.claude/skills/implementation-cycle/SKILL.md`
  - [x] Define 4 states: PLAN, DO, CHECK, DONE
  - [x] Define transitions and guards
  - [x] DO phase guardrails (file manifest, atomic changes, >3 file gate)
  - [x] Reference subagents for isolated steps (E2-093, E2-094, E2-095)
  - [x] Documentation in REFS/GOVERNANCE.md
- **Key Design Decisions:**
  - Skill not Command (guidance vs invocation)
  - 4 phases minimal (Deming/PDCA)
  - Composition pattern (references subagents without embedding)
  - L2 guidance + L3 future gate (E2-093 preflight)
- **Related:** [E2-092, E2-093, E2-094, E2-095, E2-096, E2-097]
- **Enables:** E2-092, E2-093, E2-096
- **Memory:** Concepts 72314-72319 (WHY)
- **DoD:** Skill file exists, WHY captured, docs current, plan complete

<!-- Archived: 2025-12-19 via /close (Session 87) -->
### [COMPLETE] E2-094: Test Runner Subagent
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-17
- **Closed:** 2025-12-19 (Session 87)
- **Session:** 87
- **Milestone:** M3-Cycles
- **Plan:** `docs/plans/PLAN-E2-094-test-runner-subagent.md`
- **Context:** Isolated subagent for CHECK phase. Runs pytest, captures results, reports pass/fail.
- **Deliverables:**
  - [x] Create `.claude/agents/test-runner.md`
  - [x] Tools: Bash(pytest), Read
  - [x] Run pytest with appropriate flags
- **Note:** Claude Code subagent registry doesn't hot-reload mid-session; agent available next session
- **Memory:** Concepts 72427-72429
- **DoD:** Agent exists, discoverable in vitals, WHY captured, docs current

<!-- Archived: 2025-12-19 via /close (Session 87) -->
### [COMPLETE] E2-095: WHY Capturer Subagent
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-17
- **Closed:** 2025-12-19 (Session 87)
- **Session:** 87
- **Milestone:** M3-Cycles
- **Plan:** `docs/plans/PLAN-E2-095-why-capturer-subagent.md`
- **Context:** Isolated subagent for DONE phase. Extracts learnings from completed work and stores to memory via ingester_ingest.
- **Deliverables:**
  - [x] Create `.claude/agents/why-capturer.md`
  - [x] Tools: Read, mcp__haios-memory__ingester_ingest
  - [x] Extract key decisions and learnings from plan files
  - [x] FORESIGHT calibration ready (E2-106 bridge)
- **Note:** Same hot-reload limitation as E2-094; agent available next session
- **Memory:** Concepts 72439-72441
- **DoD:** Agent exists, discoverable in vitals, WHY captured, demo successful

<!-- Archived: 2025-12-23 via /close (Session 101) -->
### [COMPLETE] INV-022: Work-Cycle-DAG Unified Architecture
- **Status:** complete
- **Priority:** high
- **Owner:** Hephaestus
- **Created:** 2025-12-22
- **Closed:** 2025-12-23 (Session 101)
- **Session:** 98, 101
- **Milestone:** Future (Epoch 3)
- **Type:** Investigation (Architecture Design)
- **Investigation:** `docs/investigations/INVESTIGATION-INV-022-work-cycle-dag-unified-architecture.md`
- **Context:** Unified INV-011 (work-as-file), INV-012 (workflow state machine), and E2-076 (DAG governance) into coherent Work-Cycle-DAG architecture.
- **Key Findings:**
  - H1: Template channeling scales to cycles at L2, needs L4 for reliability
  - H2: Scaffold-on-entry beats exit-criteria (Session 101 proved with 5 drift cases)
  - H3: Mechanical propagation exists, blocking gaps identified
- **Designs Produced:**
  - Node-Cycle Mapping (6 nodes, 5 cycles)
  - Work File Schema v2 (with node_history, cycle_docs)
  - Scaffold-on-Entry mechanism design
  - Node Exit Gate design
  - Node-Cycle Binding Configuration (YAML schema)
- **Spawned Items:**
  - E2-140: Investigation Status Sync Hook
  - E2-141: Backlog ID Uniqueness Gate
  - E2-142: Investigation-Cycle Subagent Enforcement
  - E2-143: Audit Recipe Suite
  - E2-144: Investigation Template Enhancement (COMPLETE)
  - ADR-039: Work-Cycle-DAG Architecture (Future)
  - Mx-WorkCycle Milestone (E2-150-154, Epoch 3)
- **Memory:** Concepts 77243-77253, 77254-77260 (E2-144)
- **Related:** [INV-011, INV-012, INV-024, E2-076, E2-111, ADR-038]
