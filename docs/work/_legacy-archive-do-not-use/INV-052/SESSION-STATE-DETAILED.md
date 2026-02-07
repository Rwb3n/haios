# generated: 2025-12-29
# System Auto: last updated on: 2025-12-29T21:47:11
# HAIOS Session State System (Detailed, No ASCII)

Generated: 2025-12-29 (Session 148)
Purpose: Comprehensive audit - full detail, minimal token usage

---

## Table of Contents

1. [Complete System Architecture](#1-complete-system-architecture)
2. [Session Lifecycle](#2-session-lifecycle)
3. [State Storage Locations](#3-state-storage-locations)
4. [Data Flow](#4-data-flow)
5. [Session Number Computation](#5-session-number-computation)
6. [Justfile Recipes](#6-justfile-recipes)
7. [Identified Issues](#7-identified-issues)
8. [Recommended Fixes](#8-recommended-fixes)
9. [Session Events (2025-12-29)](#9-session-events)
10. [Files Reference](#10-files-reference)
11. [Configuration Files](#11-configuration-files)
12. [Memory Integration & Database ERD](#12-memory-integration--database-erd)
13. [Complete File Tree](#13-complete-file-tree)

---

## 1. Complete System Architecture

### Hook Layer

All hooks routed via `.claude/hooks/hook_dispatcher.py`

| Hook | Trigger | Functions |
|------|---------|-----------|
| **UserPromptSubmit** | Every user prompt | `_refresh_slim_status()` calls status.py; Injects date, context %, milestone, session delta; Warning if context > 94% |
| **PreToolUse** | Write, Edit, MultiEdit, Bash | SQL blocking (hardcoded); PowerShell blocking (toggle); Path governance for governed docs |
| **PostToolUse** | Edit, Write, MultiEdit, Bash, Read, Grep, Glob | Timestamp injection (`last_updated`); Template validation; Cycle transition logging (E2-097); Error capture to memory (E2-130) |
| **Stop** | Session end | ReasoningBank extraction |

### Work Items Referenced

- E2-085: Hook system migration PowerShell→Python
- E2-119: Vitals refresh on every prompt
- E2-097: Cycle transition logging
- E2-130: Error capture to memory

---

## 2. Session Lifecycle

### Phase 1: Session Initialization

**Trigger:** User types `/coldstart`

**Steps (coldstart.md):**
1. Read CLAUDE.md
2. Read docs/epistemic_state.md
3. Read .claude/config/north-star.md (L0)
4. Read .claude/config/invariants.md (L1)
5. Read .claude/config/roadmap.md
6. Read latest checkpoint (docs/checkpoints/)
7. Read .claude/haios-status-slim.json (session_delta)
8. Run `just --list`
9. Query memory (mode='session_recovery')
10. Run `just ready`
11. Route to work (investigation-cycle or implementation-cycle)

**Manual step (SHOULD be automated):**
- Run `just session-start N` where N = current_session + 1
- Appends to .claude/haios-events.jsonl: `{"ts": "...", "type": "session", "action": "start", "session": N}`

### Phase 2: Session Work (Loop)

**Every User Prompt:**
1. UserPromptSubmit hook fires
2. `_refresh_slim_status()` regenerates haios-status-slim.json
3. Injects: Date, Context %, Milestone, Session delta
4. Warning if context > 94%

**Work Execution:**
- Edit/Write files → PostToolUse hook fires
  - Adds `last_updated` timestamps
  - Logs cycle_transition if lifecycle_phase changes
  - Captures errors to memory
- Memory ingestion → `ingester_ingest` MCP tool
- Work item node changes → cascade triggers

### Phase 3: Session End

**checkpoint-cycle skill:**
1. SCAFFOLD: `just scaffold checkpoint N "title"`
2. FILL: Populate sections (summary, files, findings)
3. VERIFY: anti-pattern-checker validates completion claims
4. CAPTURE: `ingester_ingest` WHY learnings
5. COMMIT: `just commit-session N "title"`

**Session end logging:**
- `just session-end N`
- Appends to .claude/haios-events.jsonl: `{"ts": "...", "type": "session", "action": "end", "session": N}`

---

## 3. State Storage Locations

### Primary State Files

| File | Size | Contents | Updated By |
|------|------|----------|------------|
| `.claude/haios-status-slim.json` | ~85 lines | session_delta (prior_session, current_session, prior_date, completed, added, milestone_delta); milestone (id, name, progress, prior_progress); infrastructure (commands, skills, agents, mcps); counts (concepts, entities) | UserPromptSubmit hook, `just update-status-slim` |
| `.claude/haios-status.json` | ~500+ lines | work_items (full list); outstanding_items; stale_items; spawn_map; alignment_issues; valid_templates; live_files by path | `just update-status` |

### Event Logs

**haios-events.jsonl:**
- Event types: `session` (action: start/end), `cycle_transition` (backlog_id, from_phase, to_phase, session), `heartbeat` (synthesis: bool)
- Written by: `just session-start/end N`, PostToolUse hook (`_log_cycle_transition`), `just heartbeat`
- Read by: `just events`, `events-since`, `events-stats`, `cycle-events`, close-work-cycle (event verification)

**governance-events.jsonl (E2-108):**
- Event types: `CyclePhaseEntered` (phase, work_id, agent, timestamp), `ValidationOutcome` (gate, work_id, result, reason, timestamp)
- Written by: `.claude/lib/governance_events.py`
- Read by: `just governance-metrics`

### Other State Files

| File | Purpose |
|------|---------|
| `.claude/pending-alerts.json` | Queued validation failures |
| `.claude/validation.jsonl` | Template validation history (212KB) |
| `.mcp.json` | MCP server config (haios-memory) |

### Checkpoints

**Location:** `docs/checkpoints/YYYY-MM-DD-NN-SESSION-{N}-{title}.md`

**Frontmatter:**
- session: N
- prior_session: N-1
- backlog_ids: [items worked on]
- memory_refs: [concept IDs captured]
- milestone: current focus

**Content sections:**
- Session Summary
- Completed Work (checkboxes)
- Files Modified
- Key Findings
- WHY Captured table
- Continuation Instructions

---

## 4. Data Flow

### User Input → Hooks → State

1. **User Input (prompt)** → UserPromptSubmit Hook
2. UserPromptSubmit calls:
   - `_refresh_slim_status()` → status.py → scans checkpoints + work files + haios_memory.db → writes haios-status-slim.json
   - `_get_haios_vitals()` → reads slim status
   - `_get_context_percentage()` → Claude API
3. Injects system reminder with date, context %, milestone, delta

### Claude Response → Hooks → State

1. **Claude Response (tool calls)** → branches to Edit/Write, Bash, or MCP Tools
2. **Edit/Write** → PostToolUse Hook:
   - Timestamp injection → modified file
   - Cycle transition logging → haios-events.jsonl
   - Error capture (E2-130) → haios_memory.db
   - Status refresh (INV-012) → haios-status.json
3. **MCP Tools (memory)** → haios_memory.db

---

## 5. Session Number Computation

**Source of truth:** `docs/checkpoints/*.md` filenames

**status.py::get_session_delta() logic:**
1. List all docs/checkpoints/*.md files
2. Sort by modification time (descending)
3. Extract session number from filename: `SESSION-(\d+)-`
4. latest = checkpoints[0].session
5. prior = checkpoints[1].session (if exists)
6. current_session = latest
7. prior_session = prior (or latest - 1)

**Example:**
```
checkpoints/
├── 2025-12-29-04-SESSION-145-...md  ← latest (current_session=145)
├── 2025-12-29-03-SESSION-144-...md  ← prior (prior_session=144)
└── 2025-12-29-02-SESSION-143-...md
```

Result in haios-status-slim.json:
```json
"session_delta": {
  "prior_session": 144,
  "current_session": 145,
  ...
}
```

**IMPORTANT:** "current" session in status is the LAST COMPLETED session, not the ACTIVE session.

**Formula:** `NEW_SESSION = current_session + 1`

---

## 6. Justfile Recipes

### Session Lifecycle

| Recipe | Purpose |
|--------|---------|
| `just session-start N` | Log start event to haios-events.jsonl |
| `just session-end N` | Log end event to haios-events.jsonl |
| `just commit-session N T` | Git commit checkpoint + work + status |
| `just checkpoint-latest` | Get most recent checkpoint filename |

### Status Management

| Recipe | Purpose |
|--------|---------|
| `just update-status` | Regenerate haios-status.json + slim |
| `just update-status-slim` | Regenerate haios-status-slim.json only |
| `just update-status-dry` | Preview full status without writing |

### Event Log

| Recipe | Purpose |
|--------|---------|
| `just events` | Show last 20 events |
| `just events-since DATE` | Show events since date |
| `just events-stats` | Show event counts by type |
| `just cycle-events` | Show last 10 cycle transitions |
| `just events-clear` | Clear event log (caution!) |

### Scaffolding

| Recipe | Purpose |
|--------|---------|
| `just scaffold checkpoint N "title"` | Creates docs/checkpoints/YYYY-MM-DD-NN-SESSION-N-title.md using .claude/templates/checkpoint.md |

### Work Management (Session-Adjacent)

| Recipe | Purpose |
|--------|---------|
| `just ready` | Show unblocked work items |
| `just tree` | Show milestone progress |
| `just close-work ID` | Close work item + cascade + update status |
| `just governance-metrics` | Show governance event metrics (E2-108) |

---

## 7. Identified Issues

### Issue 1: Session 145 No End Event

**Timeline:**
- 12:04:59 - Session 145 started
- (work in progress)
- ~94% context used - warning displayed
- Context exhaustion - crash before checkpoint
- NO session-end logged

**Impact:** Events show 145 start, then 146 start. Missing 145 end.

**Fix:** Coldstart should detect orphaned sessions and auto-close.

### Issue 2: Session-Start Not Automated

**Current:** coldstart.md says "run just session-start N" but doesn't do it. Agent must manually compute N and run the command.

**Fix:** Add to coldstart.md after step 7: "Run: just session-start $(current_session + 1)" Or: Enhance coldstart to auto-run session-start.

### Issue 3: Context Warning Too Late

**Current:** Warning at 94% context

**Problem:** Not enough runway to complete checkpoint-cycle (SCAFFOLD + FILL + VERIFY + CAPTURE + COMMIT needs ~10% context)

**Fix:** Warn at 85%, suggest checkpoint at 90%, force at 95%.

### Issue 4: Milestone Display Confusion

**Status shows:** M7b-WorkInfra (62%)
**Checkpoints show:** M7c-Governance, M8-SkillArch

**This is NOT a bug:** Multiple milestones can have active work. Status shows "highest progress" milestone, checkpoints show "focus".

**Fix:** Documentation clarity. Perhaps show "active milestones: M7b, M7c".

### Issue 5: No Crash Recovery

**When context exhausts or connection drops:**
- No automatic checkpoint created
- No session-end logged
- Work may be lost (not committed)

**Fix:** Coldstart should:
1. Check events for "start without end" pattern
2. Create recovery checkpoint with what's known
3. Log synthetic session-end for orphaned session

---

## 8. Recommended Fixes

### Priority 1 (Immediate): Auto Session-Start in Coldstart

- **Location:** .claude/commands/coldstart.md
- **Change:** After step 7, add: "Run `just session-start N` where N = current_session + 1"
- **Effort:** Low (documentation update)
- **Impact:** Ensures all sessions are logged from start

### Priority 2 (Short-term): Earlier Context Warning

- **Location:** .claude/hooks/hooks/user_prompt_submit.py
- **Change:** `_get_context_percentage()` threshold from 94% to 85%; Add "MUST checkpoint" at 90%
- **Effort:** Low (threshold change)
- **Impact:** More runway for clean session ends

### Priority 3 (Medium-term): Orphan Session Detection

- **Location:** New function in .claude/lib/status.py or coldstart logic
- **Logic:**
  1. Read last N events from haios-events.jsonl
  2. Find most recent session start
  3. Check if corresponding end exists
  4. If not, log: "Session N crashed, creating recovery checkpoint"
- **Effort:** Medium (new feature)
- **Impact:** Clean recovery from crashes

### Priority 4 (Long-term): Multi-Milestone Display

- **Location:** status.py, haios-status-slim.json schema
- **Change:** Track "active_milestones" list instead of single "milestone"
- **Effort:** Medium (schema change + downstream updates)
- **Impact:** Clearer view of parallel work streams

---

## 9. Session Events

### 2025-12-29 Timeline

| Time | Session | Action | Notes |
|------|---------|--------|-------|
| 10:33:50 | 142 | end | Normal completion (S142 checkpoint exists) |
| 10:38:53 | 143 | start | /coldstart after /clear |
| 11:17:10 | 143 | end | Checkpoint created (S143) |
| 11:19:41 | 144 | start | E2-232 anti-pattern work |
| 11:58:41 | 144 | end | Checkpoint created (S144) |
| 12:04:59 | 145 | start | E2-233 M8-SkillArch |
| - | 145 | (no end) | CRASH - context exhaustion at ~94% |
| 19:18:39 | 146 | start | Resume after 7-hour gap |
| 21:07:09 | 146 | end | Checkpoint created (S146) |
| 21:09:?? | 147 | (no start) | Continuation (session-end logged 21:11) |
| 21:30:?? | 148 | start | INV-052 audit |

### Checkpoint Files Created Today

- 2025-12-29-02-SESSION-143-m7c-complete-anti-pattern-checker-design.md
- 2025-12-29-03-SESSION-144-e2-232-anti-pattern-checker-and-stale-file-cleanup.md
- 2025-12-29-04-SESSION-145-e2-233-m8-skillarch-complete.md
- 2025-12-29-05-SESSION-146-m7b-workinfra-e2075-superseded.md
- 2025-12-29-06-SESSION-148-inv-052-session-state-system-audit-complete.md

---

## 10. Files Reference

### Hooks

| File | Purpose |
|------|---------|
| `.claude/hooks/hook_dispatcher.py` | Main router for all hook events |
| `.claude/hooks/hooks/user_prompt_submit.py` | Context injection, vitals refresh |
| `.claude/hooks/hooks/post_tool_use.py` | Timestamps, cycle logging, error capture |
| `.claude/hooks/hooks/pre_tool_use.py` | SQL blocking, path governance |
| `.claude/hooks/hooks/stop.py` | ReasoningBank extraction |
| `.claude/hooks/memory_retrieval.py` | Memory query helpers |
| `.claude/hooks/reasoning_extraction.py` | ReasoningBank extraction utilities |

### Lib

| File | Purpose |
|------|---------|
| `.claude/lib/status.py` | Status generation (slim + full) |
| `.claude/lib/scaffold.py` | Template scaffolding |
| `.claude/lib/governance_events.py` | Event logging for governance (E2-108) |
| `.claude/lib/work_item.py` | Work file operations |
| `.claude/lib/cascade.py` | Status cascade propagation |

### Commands

| File | Purpose |
|------|---------|
| `.claude/commands/coldstart.md` | Session initialization prompt |
| `.claude/commands/close.md` | Work item closure |
| `.claude/commands/new-checkpoint.md` | Checkpoint creation |

### Skills

| File | Purpose |
|------|---------|
| `.claude/skills/checkpoint-cycle/` | SCAFFOLD→FILL→VERIFY→CAPTURE→COMMIT |
| `.claude/skills/implementation-cycle/` | PLAN→DO→CHECK→DONE |
| `.claude/skills/close-work-cycle/` | VALIDATE→OBSERVE→ARCHIVE→MEMORY |

### State

| File | Purpose |
|------|---------|
| `.claude/haios-status-slim.json` | Compact status (refreshed every prompt) |
| `.claude/haios-status.json` | Full status (manual refresh) |
| `.claude/haios-events.jsonl` | Event log (append-only) |
| `docs/checkpoints/*.md` | Session checkpoints |

### Recipes

| File | Purpose |
|------|---------|
| `justfile` | All just recipes (300+ lines) |

---

## 11. Configuration Files

### .claude/settings.local.json

**Hooks Configuration:**
- PreToolUse: matcher="Write|Edit|MultiEdit|Bash" → python .claude/hooks/hook_dispatcher.py
- PostToolUse: matcher="Edit|Write|MultiEdit|Bash|Read|Grep|Glob" → python .claude/hooks/hook_dispatcher.py
- UserPromptSubmit: (all prompts) → python .claude/hooks/hook_dispatcher.py
- Stop: (on stop) → python .claude/hooks/hook_dispatcher.py

**Permissions:**
- 84 allow rules for pre-approved tools/commands
- Skills: checkpoint-cycle, implementation-cycle, close-work-cycle, etc.
- MCP: haios-memory (enabled)

**Output Style:** "hephaestus" (Hephaestus Builder agent persona)

### .claude/config/governance-toggles.yaml

| Toggle | Value | Effect |
|--------|-------|--------|
| `block_powershell` | true | Blocks powershell.exe through Bash |
| `block_sql` | (hardcoded) | In pre_tool_use.py, not yet a toggle |

### .claude/config/routing-thresholds.yaml

```yaml
thresholds:
  observation_pending:
    enabled: true
    max_count: 10           # Trigger triage if > 10 pending observations
    divert_to: observation-triage-cycle
    escape_priorities: [critical]  # Skip threshold for critical work
```

### .claude/config/node-cycle-bindings.yaml

**Maps DAG nodes to cycle skills:**

| Node | Cycle | Scaffold | Exit Criteria |
|------|-------|----------|---------------|
| backlog | null | [] | Manual decision only |
| discovery | investigation-cycle | /new-investigation | Investigation status=complete, Findings min 50 chars |
| plan | plan-cycle | /new-plan | Plan status=approved |
| implement | implementation-cycle | [] | Tests verified via /close |
| close | closure-cycle | [] | DoD verified via /close |

### .claude/templates/*.md

Templates for governed documents:
- checkpoint.md - Session checkpoint (SESSION-N-*.md)
- implementation_plan.md - PLAN.md files
- investigation.md - INVESTIGATION-*.md files
- work_item.md - WORK.md files
- observations.md - observations.md files
- architecture_decision_record.md - ADR-*.md files
- report.md, handoff_investigation.md

---

## 12. Memory Integration & Database ERD

### MCP Server: haios-memory

**Database:** haios_memory.db (SQLite + sqlite-vec)
**Schema:** docs/specs/memory_db_schema_v3.sql (AUTHORITATIVE)

**Key Tools (Session-Relevant):**

| Tool | Purpose |
|------|---------|
| `ingester_ingest` | Store WHY learnings with classification |
| `memory_search_with_experience` | Query with strategy injection |
| `memory_stats` | Get concept/entity counts |

**Used By:**
- coldstart: Query mode='session_recovery' for prior strategies
- checkpoint-cycle CAPTURE: Store WHY learnings
- close-work-cycle MEMORY: Store closure reasoning
- PostToolUse (E2-130): Error capture to memory
- Stop hook: ReasoningBank extraction

**Current Counts:** concepts: 80,133 | entities: 8,755

### Database ERD (15 Tables)

#### Core Tables (Phase 3 ETL)

| Table | Key Columns | Purpose |
|-------|-------------|---------|
| **artifacts** | id, file_path, file_hash, space_id | Source files processed |
| **entities** | id, type, value | Extracted entities (User, Agent, ADR) |
| **entity_occurrences** | artifact_id (FK), entity_id (FK), line_number | Links entities to sources |
| **concepts** | id, type, content, source_adr, synthesis_* | Extracted concepts (Directive, Proposal, Critique) |
| **concept_occurrences** | artifact_id (FK), concept_id (FK), line_number | Links concepts to sources |
| **processing_log** | file_path, status, attempt_count, error_message | Batch processing tracking |
| **quality_metrics** | artifact_id (FK), entities_extracted, concepts_extracted | Processing quality |

#### Retrieval Tables (Phase 4 ReasoningBank)

| Table | Key Columns | Purpose |
|-------|-------------|---------|
| **embeddings** | artifact_id (FK), concept_id (FK), entity_id (FK), vector | Vector embeddings for semantic search |
| **reasoning_traces** | query, approach_taken, outcome, strategy_title, strategy_description, strategy_content, similar_to_trace_id (FK self-ref) | ReasoningBank pattern |

#### Knowledge Layer (Phase 8 Refinement)

| Table | Key Columns | Purpose |
|-------|-------------|---------|
| **memory_metadata** | memory_id (FK→artifacts), key, value | Key-value metadata (Greek Triad) |
| **memory_relationships** | source_id (FK), target_id (FK), relationship_type | Relationships (implements, justifies, derived_from, supports, contradicts, related) |

#### Synthesis Tables (Phase 9 Memory Synthesis)

| Table | Key Columns | Purpose |
|-------|-------------|---------|
| **synthesis_clusters** | cluster_type (concept/trace/cross), centroid_embedding, synthesized_concept_id (FK) | Clusters for synthesis |
| **synthesis_cluster_members** | cluster_id (FK), member_type, member_id, similarity_to_centroid | Cluster membership |
| **synthesis_provenance** | synthesized_concept_id (FK), source_type, source_id, contribution_weight | Provenance chain |

#### Agent Ecosystem (Session 17)

| Table | Key Columns | Purpose |
|-------|-------------|---------|
| **agent_registry** | id (TEXT PK), name, version, type (subagent/worker/orchestrator), capabilities (JSON), tools (JSON), status | Agent registration |
| **skill_registry** | id (TEXT PK), name, provider_agent_id (FK), parameters (JSON) | Skill registration |

### Session-Memory Flow

1. **coldstart** → `memory_search_with_experience(mode='session_recovery')`
2. → Strategies from prior sessions (reasoning_traces.strategy_*)
3. → SESSION WORK (with strategy context)
4. **checkpoint-cycle** → `ingester_ingest(content, source_path)`
5. → New concepts stored (concepts table, memory_refs in frontmatter)

---

## 13. Complete File Tree

### .claude/

```
.claude/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest (v0.2.0)
├── commands/
│   ├── coldstart.md             # Session initialization
│   ├── close.md                 # Work item closure
│   ├── new-checkpoint.md        # Checkpoint creation
│   └── ... (18 total)
├── config/
│   ├── governance-toggles.yaml  # Feature flags
│   ├── node-cycle-bindings.yaml # DAG node→cycle mapping
│   ├── routing-thresholds.yaml  # Health thresholds
│   ├── north-star.md            # L0 mission/purpose
│   ├── invariants.md            # L1 patterns/rules
│   └── roadmap.md               # Strategic direction
├── hooks/
│   ├── hook_dispatcher.py       # Main router
│   ├── memory_retrieval.py      # Memory query helpers
│   ├── reasoning_extraction.py  # ReasoningBank extraction
│   └── hooks/
│       ├── user_prompt_submit.py # Context injection
│       ├── pre_tool_use.py       # Governance blocking
│       ├── post_tool_use.py      # Timestamps, logging
│       └── stop.py               # ReasoningBank
├── lib/
│   ├── status.py                # Status generation
│   ├── scaffold.py              # Template scaffolding
│   ├── work_item.py             # Work file operations
│   ├── cascade.py               # Status cascade
│   ├── governance_events.py     # Event logging
│   └── ... (27 total)
├── skills/
│   ├── checkpoint-cycle/        # SCAFFOLD→FILL→VERIFY→CAPTURE→COMMIT
│   ├── implementation-cycle/    # PLAN→DO→CHECK→DONE
│   ├── investigation-cycle/     # HYPOTHESIZE→EXPLORE→CONCLUDE
│   ├── close-work-cycle/        # VALIDATE→OBSERVE→ARCHIVE→MEMORY
│   └── ... (15 total)
├── agents/
│   ├── anti-pattern-checker.md
│   ├── preflight-checker.md
│   ├── schema-verifier.md
│   └── ... (7 total)
├── templates/
│   ├── checkpoint.md
│   ├── work_item.md
│   └── ... (9 total)
├── mcp/
│   ├── context7_mcp.md          # Context7 docs reference
│   ├── haios_memory_mcp.md      # Memory MCP reference
│   └── ide_mcp.md               # IDE integration
├── output-styles/
│   └── hephaestus.md            # Builder agent persona
├── REFS/
│   ├── COMMANDS-REF.md          # Commands reference
│   ├── HOOKS-REF.md             # Hooks reference
│   ├── SKILLS-REF.md            # Skills reference
│   ├── SUBAGENTS-REF.md         # Subagents reference
│   └── ... (10 total)           # SDK, MCP, Plugins, Troubleshooting
├── settings.local.json          # Hook configuration
├── haios-status.json            # Full status
├── haios-status-slim.json       # Compact status (refreshed every prompt)
├── haios-events.jsonl           # Session/cycle event log
├── governance-events.jsonl      # E2-108 cycle phase events
├── pending-alerts.json          # Validation failures queue
└── validation.jsonl             # Template validation history
```

### docs/

```
docs/
├── checkpoints/                 # Session checkpoints (SESSION-N-*.md)
├── work/
│   ├── active/                  # Active work items (WORK.md + plans/)
│   └── archive/                 # Completed work items
├── investigations/              # Investigation documents (INVESTIGATION-*.md)
├── specs/
│   └── memory_db_schema_v3.sql  # Database schema (authoritative)
└── epistemic_state.md           # Current project phase/status
```

### Root

```
justfile                         # All execution recipes (300+ lines)
haios_memory.db                  # Memory database

haios_etl/                       # DEPRECATED (but still used by justfile)
├── cli.py                       # CLI entry point (python -m haios_etl.cli)
├── database.py                  # DatabaseManager
├── synthesis.py                 # Memory synthesis
├── retrieval.py                 # Query execution
├── extraction.py                # Content extraction
├── mcp_server.py                # MCP server definition
└── DEPRECATED.md                # Migration guide → .claude/lib/
```

**NOTE:** haios_etl/ is deprecated since Session 92 (E2-120). Code migrated to `.claude/lib/`. However, justfile still uses `python -m haios_etl.cli` for ETL recipes:
- `just status` → haios_etl.cli status
- `just synthesis` → haios_etl.cli synthesis run
- `just process` → haios_etl.cli process
- `just ingest` → haios_etl.cli ingest

---

*This detailed version preserves all information from the ASCII diagram (~1050 lines, ~15-20k tokens) in ~600 lines using markdown tables (~6-8k tokens).*

*Related: ADR-033 (Work Item Lifecycle), E2-167 (commit-session), E2-119 (vitals refresh)*
*Created: INV-052 (Session State System Audit)*
