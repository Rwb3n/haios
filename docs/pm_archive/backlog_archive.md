# generated: 2025-12-22
# HAIOS Backlog Archive

> **Purpose:** Completed, closed, and absorbed work items moved from main backlog.
> **Note:** These items are preserved for historical reference and memory linkage.

---

## Archived Items (15 items)

### [CLOSED] E2-010: Staleness Awareness Command
- **Status:** superseded
- **Owner:** Hephaestus
- **Created:** 2025-12-07
- **Closed:** 2025-12-10 (Session 58)
- **Session:** 41
- **Context:** Auto-detect stale documentation using System Auto timestamps.
- **Resolution (Session 58):** Achieved via different mechanisms:
  - haios-status.json `stale` section (Session 47)
  - `/workspace` command surfaces stale items
  - `/coldstart` shows workspace summary with stale count
- **Memory:** Concept 62544


### [CLOSED] E2-033: Cascade Unblock on /close
- **Status:** absorbed
- **Owner:** Hephaestus
- **Created:** 2025-12-11
- **Closed:** 2025-12-16 (Session 78)
- **Session:** 63
- **Spawned By:** Session 63 discussion
- **Absorbed By:** E2-076e (Cascade Hooks)
- **Context:** When a blocking work item is closed, items with `blocked_by: <that-id>` should be notified.
- **Resolution (Session 78):** E2-076e implements comprehensive cascade mechanism including unblock detection with multiple-blocker support. E2-033 scope is subset of E2-076e.


### [CLOSED] E2-034: Cold Start Context Optimization
- **Status:** absorbed
- **Owner:** Hephaestus
- **Created:** 2025-12-13
- **Closed:** 2025-12-16 (Session 78)
- **Session:** 64-65
- **Spawned By:** Session 64-65 investigation
- **Absorbed By:** E2-076d (Vitals Injection)
- **Context:** /coldstart consumes 50k+ tokens loading full files. Not optimal.
- **Resolution (Session 78):** E2-076d implements comprehensive L1/L2 progressive context loading including haios-status-slim.json generation, vitals injection, and delta calculation (via E2-078). E2-034 scope is subset of E2-076d.


### [ABSORBED] E2-FIX-003: Error Capture False Positive Tuning
- **Status:** absorbed
- **Absorbed By:** E2-130 (Error Capture Rebuild)
- **Owner:** Hephaestus
- **Created:** 2025-12-13
- **Session:** 69
- **Spawned By:** E2-007 demo (Session 69)
- **Context:** E2-007 Error Capture Hook captures Edit tool responses as errors (false positive).
- **Root Cause:** ErrorCapture.ps1 error patterns are too broad - JSON content containing "error" strings triggers detection even on successful operations.
- **Example:** Edit tool response contains `"oldString"` with code that has "error" in it, triggering false positive.
- **Fix Scope:**
  - [ ] Make error patterns more specific (check for actual error structure, not substring)
  - [ ] Skip detection if tool_response indicates success
  - [ ] Consider checking exit_code for Bash only, response structure for others
- **Effort:** Low (30 min)
- **Related:** E2-007 (Error Capture Hook)


### [CLOSED] INV-013: Spawning Mechanism Consistency Audit
- **Status:** absorbed
- **Priority:** medium
- **Owner:** Hephaestus
- **Created:** 2025-12-14
- **Closed:** 2025-12-16 (Session 78)
- **Session:** 72
- **Absorbed By:** E2-076b (Frontmatter Schema)
- **Context:** ADR-037 used `spawned_by` and `backlog_id` fields not in architecture_decision_record OptionalFields. Fixed ad-hoc in Session 72 but indicates broader inconsistency - spawning fields may be missing from other template types.
- **Resolution (Session 78):** E2-076b performs comprehensive audit and normalization of edge fields (spawned_by, blocked_by, related, milestone) across ALL template types. INV-013 audit scope is subset of E2-076b.
- **Related:** INV-007 (Work Item Spawning Patterns), ADR-033 (Work Item Lifecycle), E2-076b


### [CLOSED] E2-074: Context Efficiency - Split haios-status.json
- **Status:** absorbed
- **Priority:** medium
- **Owner:** Hephaestus
- **Created:** 2025-12-14
- **Closed:** 2025-12-16 (Session 78)
- **Session:** 75
- **Spawned By:** INV-016 (H1)
- **Absorbed By:** E2-076d (Vitals Injection)
- **Context:** `haios-status.json` is 36% bloat (lifecycle files). Need slim version for context loading.
- **Resolution (Session 78):** E2-076d Step 2 implements haios-status-slim.json generation with identical deliverables. E2-074 is exact duplicate of E2-076d scope.
- **Memory:** Concept 75002 (Context Efficiency)


### [CLOSED] E2-070: Backlog Item Milestone Linking
- **Status:** absorbed
- **Priority:** medium
- **Owner:** Hephaestus
- **Created:** 2025-12-14
- **Closed:** 2025-12-16 (Session 78)
- **Session:** 73
- **Spawned By:** E2-069
- **Absorbed By:** E2-076b (Frontmatter Schema)
- **Context:** Add `milestone` field to backlog items. ValidateTemplate.ps1 should validate milestone references exist.
- **Resolution (Session 78):** E2-076b adds milestone field to ALL templates including backlog_item. E2-070 scope is subset of E2-076b.
- **Related:** E2-069, E2-076b


### [COMPLETE] E2-080: Justfile as Claude's Execution Toolkit
- **Status:** complete
- **Priority:** high
- **Owner:** Hephaestus
- **Created:** 2025-12-15
- **Completed:** 2025-12-16 (Session 78)
- **Session:** 76, 78
- **Context:** When Claude needs to execute governance operations, it currently runs verbose PowerShell commands (`powershell.exe -ExecutionPolicy Bypass -Command "& '.claude/hooks/...'"`). Error-prone, hard to read, Windows-only.
- **Key Insight:**
  - **Human uses `/`** - Claude Code's native slash commands (already work)
  - **Claude uses `just`** - Clean execution toolkit for actual operations
- **Architecture:**
  ```
  Human: /new-plan E2-080 "Justfile Integration"
      ↓
  Claude Code expands slash command to prompt
      ↓
  Claude reads prompt, needs to scaffold a file
      ↓
  Claude runs: just scaffold plan E2-080 "Justfile Integration"
      (NOT: powershell.exe -ExecutionPolicy Bypass -Command "& '.claude/hooks/ScaffoldTemplate.ps1' ...")
  ```
- **Solution:** Create `justfile` at project root as Claude's toolkit:
  ```just
  # Scaffolding
  scaffold type id title:
      powershell.exe -ExecutionPolicy Bypass -Command "& '.claude/hooks/ScaffoldTemplate.ps1' -Template '{{type}}' ..."

  # Validation
  validate file:
      powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/ValidateTemplate.ps1 -FilePath {{file}}

  # ETL Operations
  status:
      python -m haios_etl.cli status

  synthesis:
      python -m haios_etl.cli synthesis run

  # Memory
  memory-stats:
      python -c "from haios_etl.database import DatabaseManager; print(DatabaseManager().get_stats())"
  ```
- **Extended Vision: Skill-Sets as Capability Bundles**
  - Skills wrap multiple just recipes + MCPs + tools into cohesive capability sets
  - Subagents get scoped access to skill-sets, not everything
  ```
  skill-set:database          skill-set:governance       skill-set:memory
  ├── just schema-info        ├── just scaffold          ├── just synthesis
  ├── just db-query           ├── just validate          ├── just memory-stats
  ├── mcp schema_info         ├── just close             ├── mcp ingester_ingest
  └── Read (schema only)      └── Write, Edit            └── mcp memory_search

  schema-verifier subagent → allowed: [skill-set:database]
  document-creator subagent → allowed: [skill-set:governance]
  memory-agent subagent → allowed: [skill-set:memory]
  ```
- **Deliverables:**
  - [ ] Install `just` (scoop install just, or cargo install just)
  - [ ] Create `justfile` at project root
  - [ ] Add recipes for: scaffold, validate, status, synthesis, memory operations
  - [ ] Update slash command .md files to instruct Claude to use `just`
  - [ ] Add `just --list` to CLAUDE.md so Claude knows available tools
  - [ ] Design skill-set definitions (future: E2-081?)
  - [ ] Implement subagent capability scoping (future: E2-082?)
- **Pattern:** "Just recipes are atoms, skills are molecules, subagents are constrained executors"
- **Memory:** Concepts 71780-71789 (Skill-Sets Architecture)
- **Related:** [E2-076, E2-079, all governance work]


### [COMPLETE] E2-102: Execute Heartbeat Scheduler Setup
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-19
- **Completed:** 2025-12-19
- **Session:** 87
- **Spawned By:** INV-017
- **Context:** E2-081 designed heartbeat scheduler, but cross-pollination took 3 hours. Fixed with --skip-cross flag.
- **Deliverables:**
  - [x] Run `.claude/hooks/setup-heartbeat-task.ps1` to register scheduled task
  - [x] Verify task appears in Windows Task Scheduler (State=Ready)
  - [x] Fix heartbeat recipe: add --skip-cross (3hr -> 7sec)
  - [x] Verify heartbeat event logged
- **Critical Finding:** Cross-pollination compared 92M pairs. --skip-cross reduces heartbeat to 7 seconds.
- **Related:** [E2-081, INV-017]

## Milestone: M4-Research (Investigation Infrastructure)


### [COMPLETE] E2-125: Full Status Module (Deferred from E2-120)
- **Status:** complete
- **Completed:** 2025-12-21 (Session 94)
- **Owner:** Hephaestus
- **Created:** 2025-12-21
- **Session:** 93
- **Spawned By:** E2-120
- **Context:** E2-120 Phase 2a reduced scope to core status functions only. Full status (workspace analysis, lifecycle tracking, alignment checks) deferred here.
- **Rationale:** Slim status serves coldstart/vitals (90% of runtime use). Full status is /haios debugging only.
- **Deliverables:**
  - [ ] `get_valid_templates()` - Parse template definitions
  - [ ] `get_live_files()` - Scan governed paths for lifecycle
  - [ ] `get_outstanding_items()` - Detect unchecked pending work
  - [ ] `get_stale_items()` - Age-based staleness detection
  - [ ] `get_workspace_summary()` - Aggregate workspace counts
  - [ ] `check_alignment()` - Match files to backlog items
  - [ ] `get_spawn_map()` - E2-110 spawn tree tracking
  - [ ] Full haios-status.json generation
- **Effort:** Medium (8 functions, ~500 LOC)
- **Related:** [E2-120, UpdateHaiosStatus.ps1]


### [COMPLETE] E2-126: Frontmatter Timestamp Migration
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-21
- **Closed:** 2025-12-21 (Session 94)
- **Session:** 94
- **Spawned By:** E2-120
- **Context:** Legacy PowerShell PostToolUse hook injected timestamps OUTSIDE YAML frontmatter.
- **Solution:** Created `scripts/migrate_timestamps.py` with BOM handling.
- **Results:**
  - [x] 22 files migrated to correct format
  - [x] BOM handling fixed (can appear after timestamps)
  - [x] Previously skipped test now enabled (322 -> 323 tests)
- **Related:** [E2-120, post_tool_use.py]


### [ABSORBED] E2-104: Dedicated tool_error Concept Type
- **Status:** absorbed
- **Absorbed By:** E2-130 (Error Capture Rebuild)
- **Owner:** Hephaestus
- **Created:** 2025-12-19
- **Session:** 86
- **Spawned By:** INV-017
- **Context:** ErrorCapture.ps1 is wired but errors flow through generic ingester, classified as Critique/Directive. No dedicated type for tool errors.
- **Problem:** Cannot query "show me all tool errors" - mixed with regular concepts.
- **Deliverables:**
  - [ ] Update ErrorCapture flow to use `type: tool_error` or `type: Error`
  - [ ] Consider adding source field: `source: Bash` / `source: Read` etc.
  - [ ] Verify error concepts queryable by type
- **Effort:** Low (30 min)
- **Related:** [E2-007, E2-FIX-003, INV-017]


### [COMPLETE] E2-105: Fix Justfile-SlashCommand Integration
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-19
- **Completed:** 2025-12-19
- **Session:** 86
- **Spawned By:** Session 86 observability audit
- **Anti-Pattern Fixed:** Ceremonial Completion
- **Context:** E2-080 created justfile with `just scaffold` recipe, but:
  1. Recipe passed params (-BacklogId, -Title) that ScaffoldTemplate.ps1 didn't accept
  2. Slash commands still used verbose PowerShell, not `just scaffold`
  3. No integration test was run
- **Fix Applied:**
  - [x] Enhanced ScaffoldTemplate.ps1 to accept -BacklogId and -Title with auto-generated output paths
  - [x] Updated all `/new-*` slash commands to use `just scaffold`
  - [x] Tested end-to-end: `just scaffold investigation INV-TEST "Test"`
- **Memory:** 72377-72388 (anti-pattern + architectural insight)
- **Related:** [E2-080, INV-017]

---

## M3-Cycles: Cycle Framework (Session 83)

> **Theme:** Codify implementation/discovery/review cycles as composition patterns using Skills, Commands, Subagents, and Justfile recipes.
> **Insight:** Cycles are not new infrastructure - they're recognized patterns that compose existing primitives.
> **Epoch 3 Bridge:** Session 86 identified M3-Cycles as the data generation pattern for FORESIGHT. E2-106 adds optional prediction/calibration fields.


### [COMPLETE] E2-129: Template Section Skip Validation
- **Status:** complete
- **Owner:** Hephaestus
- **Created:** 2025-12-21
- **Completed:** 2025-12-21 (Session 94)
- **Session:** 94
- **Milestone:** M5-Plugin
- **Context:** Template governance v1.4 requires SKIPPED rationale when sections are omitted.
- **Solution:** Added validation rule to validate.py:
  1. `get_expected_sections()` - Return expected sections for template type
  2. `extract_sections()` - Extract ## headings from content
  3. `check_section_coverage()` - Check sections present or have **SKIPPED:** marker
- **Deliverables:**
  - [x] Add section definitions to template registry (implementation_plan has 10 expected sections)
  - [x] Add skip detection logic to validate_template()
  - [x] TDD tests for skip validation (7 tests, 29 total in test_lib_validate.py)
- **Effort:** Small (1 hour)
- **Related:** [E2-120, validate.py, template governance v1.4]


### [COMPLETE] E2-130: Error Capture Rebuild
- **Status:** complete
- **Completed:** 2025-12-21 (Session 95)
- **Owner:** Hephaestus
- **Created:** 2025-12-21
- **Session:** 95
- **Category:** Tech Debt / Maintenance (not milestone work - interrupt to fix broken infrastructure)
- **Absorbs:** E2-FIX-003, E2-104
- **Context:** Error capture (E2-007) was implemented but had critical issues. Rebuilt from scratch.
- **Value Proposition:** Learn from tool errors to inform what operations to wrap in safer abstractions.
- **Deliverables:**
  - [x] Remove stale ErrorCapture.ps1 hook from settings.local.json
  - [x] Fix detection: Only capture actual failures (exit_code != 0, error responses)
  - [x] Add `type: tool_error` for queryability
  - [x] Update imports to `.claude/lib/database.py`
  - [x] Wire into hook_dispatcher PostToolUse flow
  - [x] Clean up 188 false positive concepts from memory
  - [x] TDD tests for error detection logic (7 tests)
- **Known Limitation:** PostToolUse may not fire for failed tool calls (Claude Code limitation)
- **Files:**
  - `.claude/lib/error_capture.py` - Detection + storage
  - `.claude/hooks/hooks/post_tool_use.py` - Integration
  - `tests/test_error_capture.py` - 7 tests
- **Tests:** 345 pass (no regression)
- **Related:** [E2-007, E2-FIX-003, E2-104, INV-017]

---

## Future Investigations

