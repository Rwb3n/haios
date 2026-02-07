# generated: 2025-12-29
# System Auto: last updated on: 2025-12-29T21:55:28
# HAIOS Session State System - Architecture Diagram

Generated: 2025-12-29 (Session 148)
Purpose: Comprehensive audit of session state management

---

## Table of Contents

| # | Section | Description | Lines |
|---|---------|-------------|-------|
| 1 | [Complete System Architecture](#1-complete-system-architecture) | Hook layer overview (4 hooks) | ~40 |
| 2 | [Session Lifecycle (Detailed)](#2-session-lifecycle-detailed) | 3 phases: Init, Work, End | ~120 |
| 3 | [State Storage Locations](#3-state-storage-locations) | Primary files, event logs, checkpoints | ~100 |
| 4 | [Data Flow Diagram](#4-data-flow-diagram) | User prompt → hooks → state updates | ~80 |
| 5 | [Session Number Computation](#5-session-number-computation) | How status.py derives sessions | ~50 |
| 6 | [Justfile Recipes](#6-justfile-recipes-session-related) | Session-related just commands | ~50 |
| 7 | [Identified Issues](#7-identified-issues-2025-12-29) | 5 issues found during audit | ~80 |
| 8 | [Recommended Fixes](#8-recommended-fixes) | 4 prioritized recommendations | ~60 |
| 9 | [Today's Session Events](#9-todays-session-events-2025-12-29) | Timeline of sessions 142-148 | ~30 |
| 10 | [Files Reference](#10-files-reference) | Key files by category | ~60 |
| 11 | [Configuration Files](#11-configuration-files) | settings, toggles, thresholds, bindings | ~80 |
| 12 | [Memory Integration & ERD](#12-memory-integration--database-erd) | MCP server + 15-table database ERD | ~180 |
| 13 | [Complete File Tree](#13-complete-file-tree) | Full .claude/ and docs/ structure | ~100 |

**Total:** ~1030 lines

---

## 1. COMPLETE SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           HAIOS SESSION MANAGEMENT SYSTEM                            │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                              HOOK LAYER                                        │  │
│  │  .claude/hooks/hook_dispatcher.py → Routes all events to hooks/               │  │
│  ├───────────────────────────────────────────────────────────────────────────────┤  │
│  │                                                                               │  │
│  │  ┌─────────────────────┐  ┌─────────────────────┐                             │  │
│  │  │  UserPromptSubmit   │  │     PreToolUse      │                             │  │
│  │  │  (E2-085, E2-119)   │  │     (E2-085)        │                             │  │
│  │  ├─────────────────────┤  ├─────────────────────┤                             │  │
│  │  │• Date/time context  │  │• SQL blocking       │                             │  │
│  │  │• Context % (80%     │  │  (E2-020)           │                             │  │
│  │  │  warn threshold)    │  │• PowerShell block   │                             │  │
│  │  │• Refresh slim status│  │  (toggle-controlled)│                             │  │
│  │  │  (E2-119)           │  │• Plan validation    │                             │  │
│  │  │• HAIOS Vitals inject│  │  (E2-015)           │                             │  │
│  │  │• Dynamic thresholds │  │• Memory ref warning │                             │  │
│  │  │• Lifecycle guidance │  │  (E2-021)           │                             │  │
│  │  │  (ADR-034)          │  │• Backlog ID unique  │                             │  │
│  │  │• RFC2119 reminders  │  │  (E2-141)           │                             │  │
│  │  │                     │  │• Exit gates (E2-155)│                             │  │
│  │  │                     │  │• Path governance    │                             │  │
│  │  └─────────────────────┘  └─────────────────────┘                             │  │
│  │                                                                               │  │
│  │  ┌─────────────────────┐  ┌─────────────────────┐                             │  │
│  │  │    PostToolUse      │  │        Stop         │                             │  │
│  │  │    (E2-085)         │  │      (E2-085)       │                             │  │
│  │  ├─────────────────────┤  ├─────────────────────┤                             │  │
│  │  │• Error capture      │  │• ReasoningBank      │                             │  │
│  │  │  (E2-130)           │  │  extraction via     │                             │  │
│  │  │• Timestamp injection│  │  reasoning_         │                             │  │
│  │  │• Template validation│  │  extraction.py      │                             │  │
│  │  │• Discoverable       │  │                     │                             │  │
│  │  │  artifact refresh   │  │                     │                             │  │
│  │  │  (INV-012)          │  │                     │                             │  │
│  │  │• Cycle transition   │  │                     │                             │  │
│  │  │  logging (E2-097)   │  │                     │                             │  │
│  │  │• Investigation sync │  │                     │                             │  │
│  │  │  (E2-140)           │  │                     │                             │  │
│  │  │• Scaffold-on-entry  │  │                     │  │
│  │  │  (E2-154)           │  │                     │                             │  │
│  │  └─────────────────────┘  └─────────────────────┘                             │  │
│  │                                                                               │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. SESSION LIFECYCLE (Detailed)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              SESSION LIFECYCLE                                       │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ╔══════════════════════════════════════════════════════════════════════════════╗  │
│  ║  PHASE 1: SESSION INITIALIZATION                                              ║  │
│  ╠══════════════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                               ║  │
│  ║  User types: /coldstart                                                       ║  │
│  ║         │                                                                     ║  │
│  ║         ▼                                                                     ║  │
│  ║  ┌──────────────────────────────────────────────────────────────────────┐    ║  │
│  ║  │  /coldstart command (.claude/commands/coldstart.md)                   │    ║  │
│  ║  │  ────────────────────────────────────────────────────────────────────│    ║  │
│  ║  │  1. Read CLAUDE.md                                                    │    ║  │
│  ║  │  2. Read docs/epistemic_state.md                                      │    ║  │
│  ║  │  3. Read .claude/config/north-star.md (L0)                            │    ║  │
│  ║  │  4. Read .claude/config/invariants.md (L1)                            │    ║  │
│  ║  │  5. Read .claude/config/roadmap.md                                    │    ║  │
│  ║  │  6. Read latest checkpoint (docs/checkpoints/)                        │    ║  │
│  ║  │  7. Read .claude/haios-status-slim.json (session_delta)               │    ║  │
│  ║  │  8. Run just --list                                                   │    ║  │
│  ║  │  9. Query memory (session_recovery mode)                              │    ║  │
│  ║  │ 10. Run just ready                                                    │    ║  │
│  ║  │ 11. Route to work (investigation-cycle or implementation-cycle)       │    ║  │
│  ║  └──────────────────────────────────────────────────────────────────────┘    ║  │
│  ║         │                                                                     ║  │
│  ║         ▼ (Manual step - SHOULD be automated)                                 ║  │
│  ║  ┌──────────────────────────────────────────────────────────────────────┐    ║  │
│  ║  │  just session-start N                                                 │    ║  │
│  ║  │  ────────────────────────────────────────────────────────────────────│    ║  │
│  ║  │  Appends to .claude/haios-events.jsonl:                               │    ║  │
│  ║  │  {"ts": "...", "type": "session", "action": "start", "session": N}   │    ║  │
│  ║  └──────────────────────────────────────────────────────────────────────┘    ║  │
│  ║                                                                               ║  │
│  ╚══════════════════════════════════════════════════════════════════════════════╝  │
│                                                                                     │
│  ╔══════════════════════════════════════════════════════════════════════════════╗  │
│  ║  PHASE 2: SESSION WORK (Loop)                                                 ║  │
│  ╠══════════════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                               ║  │
│  ║  ┌─────────────────────────────────────────────────────────────────────────┐ ║  │
│  ║  │  Every User Prompt                                                       │ ║  │
│  ║  │  ───────────────────────────────────────────────────────────────────────│ ║  │
│  ║  │  UserPromptSubmit hook fires:                                            │ ║  │
│  ║  │    1. _refresh_slim_status() - calls status.py                          │ ║  │
│  ║  │    2. Injects: Date, Context %, Milestone, Session delta                │ ║  │
│  ║  │    3. Warning if context > 94%                                          │ ║  │
│  ║  └─────────────────────────────────────────────────────────────────────────┘ ║  │
│  ║                     │                                                         ║  │
│  ║                     ▼                                                         ║  │
│  ║  ┌─────────────────────────────────────────────────────────────────────────┐ ║  │
│  ║  │  Work Execution                                                          │ ║  │
│  ║  │  ───────────────────────────────────────────────────────────────────────│ ║  │
│  ║  │  • Edit/Write files → PostToolUse hook fires                            │ ║  │
│  ║  │    - Adds timestamps                                                     │ ║  │
│  ║  │    - Logs cycle_transition if lifecycle_phase changes                   │ ║  │
│  ║  │    - Captures errors to memory                                          │ ║  │
│  ║  │  • Memory ingestion → ingester_ingest MCP tool                          │ ║  │
│  ║  │  • Work item node changes → cascade triggers                            │ ║  │
│  ║  └─────────────────────────────────────────────────────────────────────────┘ ║  │
│  ║                                                                               ║  │
│  ╚══════════════════════════════════════════════════════════════════════════════╝  │
│                                                                                     │
│  ╔══════════════════════════════════════════════════════════════════════════════╗  │
│  ║  PHASE 3: SESSION END                                                         ║  │
│  ╠══════════════════════════════════════════════════════════════════════════════╣  │
│  ║                                                                               ║  │
│  ║  ┌─────────────────────────────────────────────────────────────────────────┐ ║  │
│  ║  │  checkpoint-cycle skill                                                  │ ║  │
│  ║  │  ───────────────────────────────────────────────────────────────────────│ ║  │
│  ║  │  SCAFFOLD: just scaffold checkpoint N "title"                           │ ║  │
│  ║  │       ↓                                                                  │ ║  │
│  ║  │  FILL: Populate sections (summary, files, findings)                     │ ║  │
│  ║  │       ↓                                                                  │ ║  │
│  ║  │  VERIFY: anti-pattern-checker validates completion claims               │ ║  │
│  ║  │       ↓                                                                  │ ║  │
│  ║  │  CAPTURE: ingester_ingest WHY learnings                                 │ ║  │
│  ║  │       ↓                                                                  │ ║  │
│  ║  │  COMMIT: just commit-session N "title"                                  │ ║  │
│  ║  └─────────────────────────────────────────────────────────────────────────┘ ║  │
│  ║                     │                                                         ║  │
│  ║                     ▼                                                         ║  │
│  ║  ┌─────────────────────────────────────────────────────────────────────────┐ ║  │
│  ║  │  just session-end N                                                      │ ║  │
│  ║  │  ───────────────────────────────────────────────────────────────────────│ ║  │
│  ║  │  Appends to .claude/haios-events.jsonl:                                  │ ║  │
│  ║  │  {"ts": "...", "type": "session", "action": "end", "session": N}        │ ║  │
│  ║  └─────────────────────────────────────────────────────────────────────────┘ ║  │
│  ║                                                                               ║  │
│  ╚══════════════════════════════════════════════════════════════════════════════╝  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. STATE STORAGE LOCATIONS

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              STATE STORAGE MAP                                       │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         PRIMARY STATE FILES                                  │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌────────────────────────────┐        ┌────────────────────────────┐             │
│  │  .claude/haios-status-     │        │  .claude/haios-status.json │             │
│  │  slim.json (~85 lines)     │        │  (~500+ lines)             │             │
│  ├────────────────────────────┤        ├────────────────────────────┤             │
│  │ SESSION TRACKING:          │        │ WORKSPACE TRACKING:        │             │
│  │ • session_delta:           │        │ • work_items: full list    │             │
│  │   - prior_session: N       │        │ • outstanding_items        │             │
│  │   - current_session: N+1   │        │ • stale_items              │             │
│  │   - prior_date             │        │ • spawn_map                │             │
│  │   - completed: []          │        │ • alignment_issues         │             │
│  │   - added: []              │        │                            │             │
│  │   - milestone_delta        │        │ GOVERNANCE:                │             │
│  │                            │        │ • valid_templates          │             │
│  │ MILESTONE:                 │        │ • live_files by path       │             │
│  │ • id, name, progress       │        │                            │             │
│  │ • prior_progress           │        │                            │             │
│  │                            │        │                            │             │
│  │ INFRASTRUCTURE:            │        │                            │             │
│  │ • commands[], skills[]     │        │                            │             │
│  │ • agents[], mcps[]         │        │                            │             │
│  │                            │        │                            │             │
│  │ COUNTS:                    │        │                            │             │
│  │ • concepts, entities       │        │                            │             │
│  └────────────────────────────┘        └────────────────────────────┘             │
│            │                                      │                               │
│            │ Updated by:                          │ Updated by:                   │
│            │ 1. UserPromptSubmit hook             │ just update-status            │
│            │ 2. just update-status-slim           │ (calls both)                  │
│            │                                      │                               │
│            └──────────────────┬───────────────────┘                               │
│                               │                                                   │
│                               ▼                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                    status.py (.claude/lib/)                                   │   │
│  │  ─────────────────────────────────────────────────────────────────────────── │   │
│  │  generate_slim_status() → Scans checkpoints for session, work for milestone  │   │
│  │  generate_full_status() → Full workspace scan                                │   │
│  │  get_session_delta()    → Compares last 2 checkpoints                        │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         EVENT LOG                                            │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌────────────────────────────────────────────────────────────────────────────┐    │
│  │  .claude/haios-events.jsonl                                                 │    │
│  ├────────────────────────────────────────────────────────────────────────────┤    │
│  │ EVENT TYPES:                                                                │    │
│  │ • session      {action: start|end, session: N}                             │    │
│  │ • cycle_transition {backlog_id, from_phase, to_phase, session}             │    │
│  │ • heartbeat    {synthesis: bool}                                           │    │
│  │                                                                             │    │
│  │ WRITTEN BY:                                                                 │    │
│  │ • just session-start/end N                                                  │    │
│  │ • PostToolUse hook (_log_cycle_transition)                                  │    │
│  │ • just heartbeat                                                            │    │
│  │                                                                             │    │
│  │ READ BY:                                                                    │    │
│  │ • just events, events-since, events-stats, cycle-events                    │    │
│  │ • close-work-cycle (event verification)                                    │    │
│  └────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                     │
│  ┌────────────────────────────────────────────────────────────────────────────┐    │
│  │  .claude/governance-events.jsonl (E2-108)                                   │    │
│  ├────────────────────────────────────────────────────────────────────────────┤    │
│  │ EVENT TYPES:                                                                │    │
│  │ • CyclePhaseEntered  {phase, work_id, agent, timestamp}                    │    │
│  │ • ValidationOutcome  {gate, work_id, result, reason, timestamp}            │    │
│  │                                                                             │    │
│  │ WRITTEN BY:                                                                 │    │
│  │ • .claude/lib/governance_events.py                                          │    │
│  │                                                                             │    │
│  │ READ BY:                                                                    │    │
│  │ • just governance-metrics                                                   │    │
│  └────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                     │
│  ┌────────────────────────────────────────────────────────────────────────────┐    │
│  │  OTHER STATE FILES                                                          │    │
│  ├────────────────────────────────────────────────────────────────────────────┤    │
│  │ • .claude/pending-alerts.json      Queued validation failures               │    │
│  │ • .claude/validation.jsonl         Template validation history (212KB)      │    │
│  │ • .mcp.json                        MCP server config (haios-memory)         │    │
│  └────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         CHECKPOINTS                                          │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌────────────────────────────────────────────────────────────────────────────┐    │
│  │  docs/checkpoints/YYYY-MM-DD-NN-SESSION-{N}-{title}.md                      │    │
│  ├────────────────────────────────────────────────────────────────────────────┤    │
│  │ FRONTMATTER:                                                                │    │
│  │ • session: N                                                                │    │
│  │ • prior_session: N-1                                                        │    │
│  │ • backlog_ids: [items worked on]                                           │    │
│  │ • memory_refs: [concept IDs captured]                                      │    │
│  │ • milestone: current focus                                                  │    │
│  │                                                                             │    │
│  │ CONTENT:                                                                    │    │
│  │ • Session Summary                                                           │    │
│  │ • Completed Work (checkboxes)                                              │    │
│  │ • Files Modified                                                            │    │
│  │ • Key Findings                                                              │    │
│  │ • WHY Captured table                                                        │    │
│  │ • Continuation Instructions                                                 │    │
│  └────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW                                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│                         ┌──────────────────────┐                                    │
│                         │   User Input         │                                    │
│                         │   (prompt)           │                                    │
│                         └──────────┬───────────┘                                    │
│                                    │                                                │
│                                    ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                     UserPromptSubmit Hook                                    │   │
│  │  (hooks/hooks/user_prompt_submit.py)                                         │   │
│  └────────────────────────────────┬────────────────────────────────────────────┘   │
│                                   │                                                │
│      ┌────────────────────────────┼────────────────────────────┐                   │
│      │                            │                            │                   │
│      ▼                            ▼                            ▼                   │
│  ┌────────────┐            ┌────────────┐            ┌────────────────┐           │
│  │ _refresh_  │            │ _get_haios │            │ _get_context_  │           │
│  │ slim_status│            │ _vitals()  │            │ _percentage()  │           │
│  └─────┬──────┘            └─────┬──────┘            └───────┬────────┘           │
│        │                         │                           │                     │
│        ▼                         │                           │                     │
│  ┌────────────┐                  │                           │                     │
│  │ status.py  │                  │                           │                     │
│  │ generate_  │                  │                           │                     │
│  │ slim_status│                  │                           │                     │
│  └─────┬──────┘                  │                           │                     │
│        │                         │                           │                     │
│        ▼                         │                           │                     │
│  ┌────────────────────────────────────────────────────────────────────────────┐   │
│  │  Scans:                                                                     │   │
│  │  • docs/checkpoints/*.md → latest session number                           │   │
│  │  • docs/work/active/*/WORK.md → milestone progress, work item status       │   │
│  │  • haios_memory.db → concept/entity counts                                 │   │
│  └─────┬──────────────────────────────────────────────────────────────────────┘   │
│        │                                                                           │
│        ▼                                                                           │
│  ┌────────────┐                                                                    │
│  │ Writes:    │                                                                    │
│  │ haios-     │                                                                    │
│  │ status-    │                                                                    │
│  │ slim.json  │                                                                    │
│  └────────────┘                                                                    │
│                                                                                     │
│  ═══════════════════════════════════════════════════════════════════════════════   │
│                                                                                     │
│                         ┌──────────────────────┐                                    │
│                         │   Claude Response    │                                    │
│                         │   (tool calls)       │                                    │
│                         └──────────┬───────────┘                                    │
│                                    │                                                │
│      ┌─────────────────────────────┼─────────────────────────────┐                 │
│      │                             │                             │                 │
│      ▼                             ▼                             ▼                 │
│  ┌────────────┐            ┌────────────┐             ┌────────────────┐          │
│  │ Edit/Write │            │ Bash       │             │ MCP Tools      │          │
│  │ tool       │            │ tool       │             │ (memory)       │          │
│  └─────┬──────┘            └─────┬──────┘             └───────┬────────┘          │
│        │                         │                            │                    │
│        ▼                         │                            │                    │
│  ┌─────────────────┐             │                            │                    │
│  │ PostToolUse     │             │                            │                    │
│  │ Hook            │             │                            │                    │
│  └────────┬────────┘             │                            │                    │
│           │                      │                            │                    │
│     ┌─────┴─────────────┬────────┴─────────┬─────────────────┐│                    │
│     │                   │                  │                 ││                    │
│     ▼                   ▼                  ▼                 ▼│                    │
│  ┌─────────┐     ┌───────────┐      ┌───────────┐     ┌──────────┐                │
│  │Timestamp│     │Cycle      │      │Error      │     │Status    │                │
│  │injection│     │transition │      │capture    │     │refresh   │                │
│  │         │     │logging    │      │(E2-130)   │     │(INV-012) │                │
│  └────┬────┘     └─────┬─────┘      └─────┬─────┘     └────┬─────┘                │
│       │                │                  │                │                       │
│       ▼                ▼                  ▼                ▼                       │
│  ┌─────────┐     ┌───────────┐      ┌───────────┐     ┌──────────┐                │
│  │Modified │     │haios-     │      │haios_     │     │haios-    │                │
│  │file     │     │events.    │      │memory.db  │     │status.   │                │
│  │         │     │jsonl      │      │           │     │json      │                │
│  └─────────┘     └───────────┘      └───────────┘     └──────────┘                │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. SESSION NUMBER COMPUTATION

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                     SESSION NUMBER DERIVATION                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  Source of truth: docs/checkpoints/*.md filenames                                   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  status.py::get_session_delta()                                              │   │
│  │  ───────────────────────────────────────────────────────────────────────────│   │
│  │  1. List all docs/checkpoints/*.md files                                     │   │
│  │  2. Sort by modification time (descending)                                   │   │
│  │  3. Extract session number from filename: SESSION-(\d+)-                     │   │
│  │  4. latest = checkpoints[0].session                                          │   │
│  │  5. prior = checkpoints[1].session (if exists)                               │   │
│  │  6. current_session = latest                                                 │   │
│  │  7. prior_session = prior (or latest - 1)                                    │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  Example:                                                                           │
│  ┌────────────────────────────────────────────────────────────────────────┐        │
│  │  checkpoints/                                                           │        │
│  │  ├── 2025-12-29-04-SESSION-145-...md  ← latest (current_session=145)   │        │
│  │  ├── 2025-12-29-03-SESSION-144-...md  ← prior (prior_session=144)      │        │
│  │  └── 2025-12-29-02-SESSION-143-...md                                    │        │
│  │                                                                         │        │
│  │  Result in haios-status-slim.json:                                      │        │
│  │  "session_delta": {                                                     │        │
│  │    "prior_session": 144,                                                │        │
│  │    "current_session": 145,                                              │        │
│  │    ...                                                                  │        │
│  │  }                                                                      │        │
│  └────────────────────────────────────────────────────────────────────────┘        │
│                                                                                     │
│  PROBLEM: This means "current" session in status is actually the LAST              │
│           COMPLETED session, not the ACTIVE session!                               │
│                                                                                     │
│  ┌────────────────────────────────────────────────────────────────────────┐        │
│  │  When coldstart runs:                                                   │        │
│  │  • Reads: current_session = 145 (last checkpoint)                       │        │
│  │  • Should start: session 146                                            │        │
│  │  • Must run: just session-start 146                                     │        │
│  │                                                                         │        │
│  │  Formula: NEW_SESSION = current_session + 1                             │        │
│  └────────────────────────────────────────────────────────────────────────┘        │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. JUSTFILE RECIPES (Session-Related)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                     SESSION-RELATED JUST RECIPES                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  SESSION LIFECYCLE:                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  just session-start N    → Log start event to haios-events.jsonl            │   │
│  │  just session-end N      → Log end event to haios-events.jsonl              │   │
│  │  just commit-session N T → Git commit checkpoint + work + status            │   │
│  │  just checkpoint-latest  → Get most recent checkpoint filename              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  STATUS MANAGEMENT:                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  just update-status      → Regenerate haios-status.json + slim              │   │
│  │  just update-status-slim → Regenerate haios-status-slim.json only           │   │
│  │  just update-status-dry  → Preview full status without writing              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  EVENT LOG:                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  just events             → Show last 20 events                              │   │
│  │  just events-since DATE  → Show events since date                           │   │
│  │  just events-stats       → Show event counts by type                        │   │
│  │  just cycle-events       → Show last 10 cycle transitions                   │   │
│  │  just events-clear       → Clear event log (caution!)                       │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  SCAFFOLDING:                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  just scaffold checkpoint N "title"                                         │   │
│  │        → Creates docs/checkpoints/YYYY-MM-DD-NN-SESSION-N-title.md          │   │
│  │        → Uses .claude/templates/checkpoint.md as base                       │   │
│  │        → Populates frontmatter (session, prior_session, date)               │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  WORK MANAGEMENT (Session-Adjacent):                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  just ready              → Show unblocked work items                        │   │
│  │  just tree               → Show milestone progress                          │   │
│  │  just close-work ID      → Close work item + cascade + update status        │   │
│  │  just governance-metrics → Show governance event metrics (E2-108)           │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. IDENTIFIED ISSUES (2025-12-29)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              ISSUES FOUND                                            │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────────┐ │
│  │  ISSUE 1: SESSION 145 NO END EVENT                                             │ │
│  │  ─────────────────────────────────────────────────────────────────────────────│ │
│  │  Timeline:                                                                     │ │
│  │  • 12:04:59 - Session 145 started                                             │ │
│  │  • (work in progress)                                                          │ │
│  │  • ~94% context used - warning displayed                                       │ │
│  │  • Context exhaustion - crash before checkpoint                                │ │
│  │  • NO session-end logged                                                       │ │
│  │                                                                                │ │
│  │  Impact: Events show 145 start, then 146 start. Missing 145 end.              │ │
│  │  Fix: Coldstart should detect orphaned sessions and auto-close.               │ │
│  └───────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────────┐ │
│  │  ISSUE 2: SESSION-START NOT AUTOMATED                                          │ │
│  │  ─────────────────────────────────────────────────────────────────────────────│ │
│  │  Current: coldstart.md says "run just session-start N" but doesn't do it.     │ │
│  │  Agent must manually compute N and run the command.                            │ │
│  │                                                                                │ │
│  │  Fix: Add to coldstart.md after step 7:                                        │ │
│  │       "Run: just session-start $(current_session + 1)"                         │ │
│  │  Or:  Enhance coldstart to auto-run session-start.                            │ │
│  └───────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────────┐ │
│  │  ISSUE 3: CONTEXT WARNING TOO LATE                                             │ │
│  │  ─────────────────────────────────────────────────────────────────────────────│ │
│  │  Current: Warning at 94% context                                               │ │
│  │  Problem: Not enough runway to complete checkpoint-cycle                       │ │
│  │           (SCAFFOLD + FILL + VERIFY + CAPTURE + COMMIT needs ~10% context)    │ │
│  │                                                                                │ │
│  │  Fix: Warn at 85%, suggest checkpoint at 90%, force at 95%.                   │ │
│  └───────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────────┐ │
│  │  ISSUE 4: MILESTONE DISPLAY CONFUSION                                          │ │
│  │  ─────────────────────────────────────────────────────────────────────────────│ │
│  │  Status shows: M7b-WorkInfra (62%)                                            │ │
│  │  Checkpoints show: M7c-Governance, M8-SkillArch                               │ │
│  │                                                                                │ │
│  │  This is NOT a bug: Multiple milestones can have active work.                 │ │
│  │  Status shows "highest progress" milestone, checkpoints show "focus".          │ │
│  │                                                                                │ │
│  │  Fix: Documentation clarity. Perhaps show "active milestones: M7b, M7c".      │ │
│  └───────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────────┐ │
│  │  ISSUE 5: NO CRASH RECOVERY                                                    │ │
│  │  ─────────────────────────────────────────────────────────────────────────────│ │
│  │  When context exhausts or connection drops:                                    │ │
│  │  • No automatic checkpoint created                                             │ │
│  │  • No session-end logged                                                       │ │
│  │  • Work may be lost (not committed)                                           │ │
│  │                                                                                │ │
│  │  Fix: Coldstart should:                                                        │ │
│  │  1. Check events for "start without end" pattern                               │ │
│  │  2. Create recovery checkpoint with what's known                               │ │
│  │  3. Log synthetic session-end for orphaned session                            │ │
│  └───────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. RECOMMENDED FIXES

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              RECOMMENDATIONS                                         │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  PRIORITY 1 (Immediate):                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  A. AUTO SESSION-START IN COLDSTART                                          │   │
│  │     Location: .claude/commands/coldstart.md                                   │   │
│  │     Change: After step 7, add:                                                │   │
│  │       "Run `just session-start N` where N = current_session + 1"             │   │
│  │     Effort: Low (documentation update)                                        │   │
│  │     Impact: Ensures all sessions are logged from start                        │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  PRIORITY 2 (Short-term):                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  B. EARLIER CONTEXT WARNING                                                   │   │
│  │     Location: .claude/hooks/hooks/user_prompt_submit.py                       │   │
│  │     Change: _get_context_percentage() threshold from 94% to 85%              │   │
│  │             Add "MUST checkpoint" at 90%                                      │   │
│  │     Effort: Low (threshold change)                                            │   │
│  │     Impact: More runway for clean session ends                                │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  PRIORITY 3 (Medium-term):                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  C. ORPHAN SESSION DETECTION                                                  │   │
│  │     Location: New function in .claude/lib/status.py or coldstart logic        │   │
│  │     Logic:                                                                    │   │
│  │       1. Read last N events from haios-events.jsonl                          │   │
│  │       2. Find most recent session start                                       │   │
│  │       3. Check if corresponding end exists                                    │   │
│  │       4. If not, log: "Session N crashed, creating recovery checkpoint"      │   │
│  │     Effort: Medium (new feature)                                              │   │
│  │     Impact: Clean recovery from crashes                                       │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  PRIORITY 4 (Long-term):                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  D. MULTI-MILESTONE DISPLAY                                                   │   │
│  │     Location: status.py, haios-status-slim.json schema                        │   │
│  │     Change: Track "active_milestones" list instead of single "milestone"     │   │
│  │     Effort: Medium (schema change + downstream updates)                       │   │
│  │     Impact: Clearer view of parallel work streams                             │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. TODAY'S SESSION EVENTS (2025-12-29)

```
TIME        SESSION  ACTION        NOTES
─────────────────────────────────────────────────────────────────────────
10:33:50    142      end           Normal completion (S142 checkpoint exists)
10:38:53    143      start         /coldstart after /clear
11:17:10    143      end           Checkpoint created (S143)
11:19:41    144      start         E2-232 anti-pattern work
11:58:41    144      end           Checkpoint created (S144)
12:04:59    145      start         E2-233 M8-SkillArch
            145      (no end)      ← CRASH - context exhaustion at ~94%
19:18:39    146      start         Resume after 7-hour gap
21:07:09    146      end           Checkpoint created (S146)
21:09:??    147      (no start)    Continuation (session-end logged 21:11)
─────────────────────────────────────────────────────────────────────────

Checkpoint files created today:
• 2025-12-29-02-SESSION-143-m7c-complete-anti-pattern-checker-design.md
• 2025-12-29-03-SESSION-144-e2-232-anti-pattern-checker-and-stale-file-cleanup.md
• 2025-12-29-04-SESSION-145-e2-233-m8-skillarch-complete.md
• 2025-12-29-05-SESSION-146-m7b-workinfra-e2075-superseded.md
```

---

## 10. FILES REFERENCE

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              KEY FILES                                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  HOOKS:                                                                             │
│  • .claude/hooks/hook_dispatcher.py      Main router for all hook events            │
│  • .claude/hooks/hooks/user_prompt_submit.py  Context injection, vitals refresh     │
│  • .claude/hooks/hooks/post_tool_use.py  Timestamps, cycle logging, error capture   │
│  • .claude/hooks/hooks/pre_tool_use.py   SQL blocking, path governance              │
│  • .claude/hooks/hooks/stop.py           ReasoningBank extraction                   │
│                                                                                     │
│  LIB:                                                                               │
│  • .claude/lib/status.py                 Status generation (slim + full)            │
│  • .claude/lib/scaffold.py               Template scaffolding                       │
│  • .claude/lib/governance_events.py      Event logging for governance (E2-108)      │
│  • .claude/lib/work_item.py              Work file operations                       │
│  • .claude/lib/cascade.py                Status cascade propagation                 │
│                                                                                     │
│  COMMANDS:                                                                          │
│  • .claude/commands/coldstart.md         Session initialization prompt              │
│  • .claude/commands/close.md             Work item closure                          │
│  • .claude/commands/new-checkpoint.md    Checkpoint creation                        │
│                                                                                     │
│  SKILLS:                                                                            │
│  • .claude/skills/checkpoint-cycle/      SCAFFOLD→FILL→VERIFY→CAPTURE→COMMIT        │
│  • .claude/skills/implementation-cycle/  PLAN→DO→CHECK→DONE                         │
│  • .claude/skills/close-work-cycle/      VALIDATE→OBSERVE→ARCHIVE→MEMORY            │
│                                                                                     │
│  STATE:                                                                             │
│  • .claude/haios-status-slim.json        Compact status (refreshed every prompt)    │
│  • .claude/haios-status.json             Full status (manual refresh)               │
│  • .claude/haios-events.jsonl            Event log (sessions, cycles, heartbeat)    │
│  • .claude/governance-events.jsonl       Governance events (E2-108 cycle phases)    │
│  • .claude/pending-alerts.json           Validation failures queue                  │
│  • .claude/validation.jsonl              Template validation history                │
│  • .claude/settings.json                 Base settings (minimal)                    │
│  • .claude/settings.local.json           Local settings (hooks, permissions)        │
│  • docs/checkpoints/*.md                 Session checkpoints                        │
│                                                                                     │
│  MCP:                                                                               │
│  • .mcp.json                             MCP server configuration                   │
│    - haios-memory server → .claude/lib/mcp_server.py                               │
│                                                                                     │
│  RECIPES:                                                                           │
│  • justfile                              All just recipes (300+ lines)              │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. CONFIGURATION FILES

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              CONFIGURATION                                           │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  .claude/settings.local.json                                                 │   │
│  │  ───────────────────────────────────────────────────────────────────────────│   │
│  │  HOOKS CONFIGURATION:                                                        │   │
│  │  • PreToolUse:  matcher="Write|Edit|MultiEdit|Bash"                         │   │
│  │                 → python .claude/hooks/hook_dispatcher.py                    │   │
│  │  • PostToolUse: matcher="Edit|Write|MultiEdit|Bash|Read|Grep|Glob"          │   │
│  │                 → python .claude/hooks/hook_dispatcher.py                    │   │
│  │  • UserPromptSubmit: (all prompts)                                          │   │
│  │                 → python .claude/hooks/hook_dispatcher.py                    │   │
│  │  • Stop:        (on stop)                                                    │   │
│  │                 → python .claude/hooks/hook_dispatcher.py                    │   │
│  │                                                                              │   │
│  │  PERMISSIONS:                                                                │   │
│  │  • 84 allow rules for pre-approved tools/commands                          │   │
│  │  • Skills: checkpoint-cycle, implementation-cycle, close-work-cycle, etc.   │   │
│  │  • MCP: haios-memory (enabled)                                              │   │
│  │                                                                              │   │
│  │  OUTPUT STYLE: "hephaestus" (Hephaestus Builder agent persona)              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  .claude/config/governance-toggles.yaml                                      │   │
│  │  ───────────────────────────────────────────────────────────────────────────│   │
│  │  • block_powershell: true  ← Blocks powershell.exe through Bash             │   │
│  │  • (block_sql: hardcoded in pre_tool_use.py, not yet a toggle)              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  .claude/config/routing-thresholds.yaml                                      │   │
│  │  ───────────────────────────────────────────────────────────────────────────│   │
│  │  thresholds:                                                                 │   │
│  │    observation_pending:                                                      │   │
│  │      enabled: true                                                           │   │
│  │      max_count: 10           ← Trigger triage if > 10 pending observations  │   │
│  │      divert_to: observation-triage-cycle                                     │   │
│  │      escape_priorities: [critical]  ← Skip threshold for critical work      │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  .claude/config/node-cycle-bindings.yaml                                     │   │
│  │  ───────────────────────────────────────────────────────────────────────────│   │
│  │  Maps DAG nodes to cycle skills:                                             │   │
│  │  • backlog:   null (no cycle, manual decision)                              │   │
│  │  • discovery: investigation-cycle                                            │   │
│  │  • plan:      plan-cycle                                                     │   │
│  │  • implement: implementation-cycle                                           │   │
│  │  • close:     closure-cycle                                                  │   │
│  │                                                                              │   │
│  │  Each node has:                                                              │   │
│  │  • scaffold: Docs to create on entry (e.g., /new-investigation)             │   │
│  │  • exit_criteria: Conditions to check when leaving                          │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  .claude/templates/*.md                                                      │   │
│  │  ───────────────────────────────────────────────────────────────────────────│   │
│  │  Templates for governed documents:                                           │   │
│  │  • checkpoint.md          Session checkpoint (SESSION-N-*.md)               │   │
│  │  • implementation_plan.md PLAN.md files                                     │   │
│  │  • investigation.md       INVESTIGATION-*.md files                          │   │
│  │  • work_item.md           WORK.md files                                     │   │
│  │  • observations.md        observations.md files                             │   │
│  │  • architecture_decision_record.md  ADR-*.md files                          │   │
│  │  • report.md, handoff_investigation.md                                      │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 12. MEMORY INTEGRATION & DATABASE ERD

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              MEMORY SYSTEM                                           │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  MCP Server: haios-memory                                                    │   │
│  │  ───────────────────────────────────────────────────────────────────────────│   │
│  │  Database: haios_memory.db (SQLite + sqlite-vec)                            │   │
│  │  Schema: docs/specs/memory_db_schema_v3.sql (AUTHORITATIVE)                 │   │
│  │                                                                              │   │
│  │  KEY TOOLS (Session-Relevant):                                               │   │
│  │  • ingester_ingest         Store WHY learnings with classification          │   │
│  │  • memory_search_with_experience  Query with strategy injection             │   │
│  │  • memory_stats            Get concept/entity counts                        │   │
│  │                                                                              │   │
│  │  USED BY:                                                                    │   │
│  │  • coldstart: Query mode='session_recovery' for prior strategies           │   │
│  │  • checkpoint-cycle CAPTURE: Store WHY learnings                            │   │
│  │  • close-work-cycle MEMORY: Store closure reasoning                         │   │
│  │  • PostToolUse (E2-130): Error capture to memory                            │   │
│  │  • Stop hook: ReasoningBank extraction                                      │   │
│  │                                                                              │   │
│  │  CURRENT COUNTS (from haios-status-slim.json):                              │   │
│  │  • concepts: 80,133                                                          │   │
│  │  • entities: 8,755                                                           │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Database ERD (memory_db_schema_v3.sql)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           HAIOS MEMORY DATABASE ERD                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ═══════════════════════════════════════════════════════════════════════════════   │
│  CORE TABLES (Phase 3 ETL)                                                          │
│  ═══════════════════════════════════════════════════════════════════════════════   │
│                                                                                     │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐          │
│  │    artifacts     │      │     entities     │      │    concepts      │          │
│  ├──────────────────┤      ├──────────────────┤      ├──────────────────┤          │
│  │ id (PK)          │      │ id (PK)          │      │ id (PK)          │          │
│  │ file_path        │      │ type             │      │ type             │          │
│  │ file_hash        │      │ value            │      │ content          │          │
│  │ last_processed_at│      │ UNIQUE(type,val) │      │ source_adr       │          │
│  │ version          │      └────────┬─────────┘      │ synthesis_*      │←──┐      │
│  │ space_id         │               │                │ cluster_id (FK)  │   │      │
│  └────────┬─────────┘               │                └────────┬─────────┘   │      │
│           │                         │                         │             │      │
│           │         ┌───────────────┴───────────────┐         │             │      │
│           │         │                               │         │             │      │
│           ▼         ▼                               ▼         ▼             │      │
│  ┌──────────────────────────┐           ┌──────────────────────────┐       │      │
│  │   entity_occurrences     │           │   concept_occurrences    │       │      │
│  ├──────────────────────────┤           ├──────────────────────────┤       │      │
│  │ id (PK)                  │           │ id (PK)                  │       │      │
│  │ artifact_id (FK)         │           │ artifact_id (FK)         │       │      │
│  │ entity_id (FK)           │           │ concept_id (FK)          │       │      │
│  │ line_number              │           │ line_number              │       │      │
│  │ context_snippet          │           │ context_snippet          │       │      │
│  └──────────────────────────┘           └──────────────────────────┘       │      │
│                                                                             │      │
│  ┌──────────────────┐      ┌──────────────────┐                            │      │
│  │  processing_log  │      │  quality_metrics │                            │      │
│  ├──────────────────┤      ├──────────────────┤                            │      │
│  │ id (PK)          │      │ id (PK)          │                            │      │
│  │ file_path        │      │ artifact_id (FK) │                            │      │
│  │ status           │      │ entities_extracted│                           │      │
│  │ attempt_count    │      │ concepts_extracted│                           │      │
│  │ last_attempt_at  │      │ processing_time  │                            │      │
│  │ error_message    │      │ llm_tokens_used  │                            │      │
│  └──────────────────┘      └──────────────────┘                            │      │
│                                                                             │      │
│  ═══════════════════════════════════════════════════════════════════════════════   │
│  RETRIEVAL TABLES (Phase 4 ReasoningBank)                                           │
│  ═══════════════════════════════════════════════════════════════════════════════   │
│                                                                                     │
│  ┌──────────────────────────┐           ┌──────────────────────────┐              │
│  │      embeddings          │           │    reasoning_traces      │              │
│  ├──────────────────────────┤           ├──────────────────────────┤              │
│  │ id (PK)                  │           │ id (PK)                  │              │
│  │ artifact_id (FK)         │           │ query                    │              │
│  │ concept_id (FK)          │           │ query_embedding          │              │
│  │ entity_id (FK)           │           │ approach_taken           │              │
│  │ vector (BLOB)            │           │ outcome                  │              │
│  │ model                    │           │ strategy_title           │←─ ReasoningBank│
│  │ dimensions               │           │ strategy_description     │              │
│  └──────────────────────────┘           │ strategy_content         │              │
│                                         │ space_id                 │              │
│                                         │ similar_to_trace_id (FK) │──┐           │
│                                         └──────────────────────────┘  │ self-ref  │
│                                                     ▲                 │           │
│                                                     └─────────────────┘           │
│                                                                                     │
│  ═══════════════════════════════════════════════════════════════════════════════   │
│  KNOWLEDGE LAYER (Phase 8 Refinement)                                               │
│  ═══════════════════════════════════════════════════════════════════════════════   │
│                                                                                     │
│  ┌──────────────────────────┐           ┌──────────────────────────┐              │
│  │    memory_metadata       │           │  memory_relationships    │              │
│  ├──────────────────────────┤           ├──────────────────────────┤              │
│  │ id (PK)                  │           │ id (PK)                  │              │
│  │ memory_id (FK→artifacts) │           │ source_id (FK→artifacts) │              │
│  │ key                      │           │ target_id (FK→artifacts) │              │
│  │ value                    │           │ relationship_type        │              │
│  └──────────────────────────┘           │ (implements|justifies|   │              │
│                                         │  derived_from|supports|  │              │
│                                         │  contradicts|related)    │              │
│                                         └──────────────────────────┘              │
│                                                                                     │
│  ═══════════════════════════════════════════════════════════════════════════════   │
│  SYNTHESIS TABLES (Phase 9 Memory Synthesis)                                        │
│  ═══════════════════════════════════════════════════════════════════════════════   │
│                                                                                     │
│  ┌──────────────────────────┐                                                      │
│  │   synthesis_clusters     │◄───────────────────────────────────┐                │
│  ├──────────────────────────┤                                    │                │
│  │ id (PK)                  │           ┌──────────────────────────┐              │
│  │ cluster_type             │           │ synthesis_cluster_members│              │
│  │ (concept|trace|cross)    │           ├──────────────────────────┤              │
│  │ centroid_embedding       │           │ id (PK)                  │              │
│  │ member_count             │◄──────────│ cluster_id (FK)          │              │
│  │ synthesized_concept_id   │───┐       │ member_type              │              │
│  │ status                   │   │       │ member_id                │              │
│  └──────────────────────────┘   │       │ similarity_to_centroid   │              │
│                                 │       └──────────────────────────┘              │
│                                 │                                                  │
│                                 │       ┌──────────────────────────┐              │
│                                 │       │  synthesis_provenance    │              │
│                                 │       ├──────────────────────────┤              │
│                                 └──────►│ synthesized_concept_id(FK)│             │
│                                         │ source_type              │              │
│                                         │ source_id                │              │
│                                         │ contribution_weight      │              │
│                                         └──────────────────────────┘              │
│                                                                                     │
│  ═══════════════════════════════════════════════════════════════════════════════   │
│  AGENT ECOSYSTEM (Session 17)                                                       │
│  ═══════════════════════════════════════════════════════════════════════════════   │
│                                                                                     │
│  ┌──────────────────────────┐           ┌──────────────────────────┐              │
│  │    agent_registry        │           │     skill_registry       │              │
│  ├──────────────────────────┤           ├──────────────────────────┤              │
│  │ id (PK, TEXT)            │◄──────────│ provider_agent_id (FK)   │              │
│  │ name                     │           │ id (PK, TEXT)            │              │
│  │ version                  │           │ name                     │              │
│  │ type (subagent|worker|   │           │ description              │              │
│  │       orchestrator)      │           │ parameters (JSON)        │              │
│  │ capabilities (JSON)      │           └──────────────────────────┘              │
│  │ tools (JSON)             │                                                      │
│  │ status                   │                                                      │
│  └──────────────────────────┘                                                      │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Session-Memory Flow

```
  coldstart ──► memory_search_with_experience(mode='session_recovery')
                        │
                        ▼
              Strategies from prior sessions (reasoning_traces.strategy_*)
                        │
                        ▼
              SESSION WORK (with strategy context)
                        │
                        ▼
  checkpoint-cycle ──► ingester_ingest(content, source_path)
                        │
                        ▼
              New concepts stored (concepts table, memory_refs in frontmatter)
```

---

## 13. COMPLETE FILE TREE

```
.claude/
├── .claude-plugin/
│   └── plugin.json              ← Plugin manifest (v0.2.0)
├── commands/
│   ├── coldstart.md             ← Session initialization
│   ├── close.md                 ← Work item closure
│   ├── new-checkpoint.md        ← Checkpoint creation
│   └── ... (18 total)
├── config/
│   ├── governance-toggles.yaml   ← Feature flags
│   ├── node-cycle-bindings.yaml  ← DAG node→cycle mapping
│   ├── routing-thresholds.yaml   ← Health thresholds
│   ├── north-star.md             ← L0 mission/purpose
│   ├── invariants.md             ← L1 patterns/rules
│   └── roadmap.md                ← Strategic direction
├── hooks/
│   ├── hook_dispatcher.py        ← Main router
│   ├── memory_retrieval.py       ← Memory query helpers
│   ├── reasoning_extraction.py   ← ReasoningBank extraction
│   └── hooks/
│       ├── user_prompt_submit.py ← Context injection
│       ├── pre_tool_use.py       ← Governance blocking
│       ├── post_tool_use.py      ← Timestamps, logging
│       └── stop.py               ← ReasoningBank
├── lib/
│   ├── status.py            ← Status generation
│   ├── scaffold.py          ← Template scaffolding
│   ├── work_item.py         ← Work file operations
│   ├── cascade.py           ← Status cascade
│   ├── governance_events.py ← Event logging
│   └── ... (27 total)
├── skills/
│   ├── checkpoint-cycle/    ← SCAFFOLD→FILL→VERIFY→CAPTURE→COMMIT
│   ├── implementation-cycle/← PLAN→DO→CHECK→DONE
│   ├── investigation-cycle/ ← HYPOTHESIZE→EXPLORE→CONCLUDE
│   ├── close-work-cycle/    ← VALIDATE→OBSERVE→ARCHIVE→MEMORY
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
│   ├── context7_mcp.md          ← Context7 docs reference
│   ├── haios_memory_mcp.md      ← Memory MCP reference
│   └── ide_mcp.md               ← IDE integration
├── output-styles/
│   └── hephaestus.md            ← Builder agent persona
├── REFS/
│   ├── COMMANDS-REF.md          ← Commands reference
│   ├── HOOKS-REF.md             ← Hooks reference
│   ├── SKILLS-REF.md            ← Skills reference
│   ├── SUBAGENTS-REF.md         ← Subagents reference
│   └── ... (10 total)           ← SDK, MCP, Plugins, Troubleshooting
├── settings.local.json          ← Hook configuration
├── haios-status.json            ← Full status
├── haios-status-slim.json       ← Compact status (refreshed every prompt)
├── haios-events.jsonl           ← Session/cycle event log
├── governance-events.jsonl      ← E2-108 cycle phase events
├── pending-alerts.json          ← Validation failures queue
└── validation.jsonl             ← Template validation history

docs/
├── checkpoints/             ← Session checkpoints (SESSION-N-*.md)
├── work/
│   ├── active/              ← Active work items (WORK.md + plans/)
│   └── archive/             ← Completed work items
├── investigations/          ← Investigation documents (INVESTIGATION-*.md)
├── specs/
│   └── memory_db_schema_v3.sql  ← Database schema (authoritative)
└── epistemic_state.md       ← Current project phase/status

justfile                     ← All execution recipes (300+ lines)
haios_memory.db              ← Memory database

haios_etl/                   ← DEPRECATED (but still used by justfile)
├── cli.py                   ← CLI entry point (python -m haios_etl.cli)
├── database.py              ← DatabaseManager
├── synthesis.py             ← Memory synthesis
├── retrieval.py             ← Query execution
├── extraction.py            ← Content extraction
├── mcp_server.py            ← MCP server definition
└── DEPRECATED.md            ← Migration guide → .claude/lib/
```

**NOTE:** haios_etl/ is deprecated since Session 92 (E2-120). Code migrated to `.claude/lib/`.
However, justfile still uses `python -m haios_etl.cli` for ETL recipes:
- `just status` → haios_etl.cli status
- `just synthesis` → haios_etl.cli synthesis run
- `just process` → haios_etl.cli process
- `just ingest` → haios_etl.cli ingest

---

*This diagram captures the full HAIOS session state system as of Session 148.*
*Related: ADR-033 (Work Item Lifecycle), E2-167 (commit-session), E2-119 (vitals refresh)*
*Created: INV-052 (Session State System Audit)*
