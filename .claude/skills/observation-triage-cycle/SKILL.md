---
name: observation-triage-cycle
type: ceremony
description: "HAIOS Observation Triage Cycle for processing captured observations.
  Use when scanning archived work items to triage and act on observations.
  Supports both memory-based retro-triage (WORK-143) and filesystem-based legacy triage.
  Guides SCAN->TRIAGE->PROMOTE workflow with dimension validation."
category: memory
input_contract:
  - field: scan_scope
    type: string
    required: false
    description: "Scope to scan for pending observations (default: all archived work)"
  - field: source
    type: string
    required: false
    description: "Data source: memory|filesystem|both (default: both)"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether triage completed successfully"
  - field: scanned_count
    type: integer
    guaranteed: always
    description: "Number of observations scanned"
  - field: actions
    type: list
    guaranteed: on_success
    description: "List of actions taken (spawn:INV, spawn:WORK, memory, dismiss, etc.)"
  - field: spawned_ids
    type: list
    guaranteed: on_success
    description: "IDs of spawned work items or investigations"
  - field: retro_entries_count
    type: integer
    guaranteed: on_success
    description: "Number of retro-cycle entries found in memory (WORK-143)"
  - field: kss_aggregation
    type: object
    guaranteed: on_success
    description: "K/S/S frequency aggregation: {keep: [...], stop: [...], start: [...]}"
  - field: bug_candidates
    type: list
    guaranteed: on_success
    description: "Bug candidates with confidence tags from retro-extract"
  - field: feature_candidates
    type: list
    guaranteed: on_success
    description: "Feature candidates with confidence tags from retro-extract"
side_effects:
  - "Promote observations to work items or investigations"
  - "Store insights to memory via ingester_ingest"
  - "Update triage_status in observation files"
generated: 2025-12-28
last_updated: '2026-02-13T20:30:00'
---
# Observation Triage Cycle

This skill defines the SCAN-TRIAGE-PROMOTE cycle for processing archived observations and routing them to actionable outcomes.

## When to Use

**Manual invocation:** `Skill(skill="observation-triage-cycle")` when processing accumulated observations.
**Via recipe:** `just triage-observations` for quick scan.
**Scheduled:** Can be invoked during heartbeat or session-end.

---

## The Cycle

```
SCAN --> TRIAGE --> PROMOTE
  |         |           |
  |         |           +-> spawn:INV, spawn:WORK, spawn:FIX
  |         |           +-> memory (store insight)
  |         |           +-> discuss (flag for operator)
  |         |           +-> dismiss (no action)
  |         |
  |         +-> Apply dimensions: category, action, priority
  |
  +-> Find archived observations with triage_status: pending
```

---

### 1. SCAN Phase

**Goal:** Find observations from both memory (retro-cycle outputs) and filesystem (legacy observations.md).

**Actions:**

#### 1a. Memory Scan (retro-triage, WORK-143)

Query memory for retro-cycle outputs using MCP `db_query` tool:

**K/S/S Directives:**
```
mcp__haios-memory__db_query(sql="SELECT id, content FROM concepts WHERE type = 'Directive' AND (content LIKE 'KEEP-%' OR content LIKE 'STOP-%' OR content LIKE 'START-%') ORDER BY id")
```

**Bug Candidates:**
```
mcp__haios-memory__db_query(sql="SELECT id, content FROM concepts WHERE type = 'Critique' AND content LIKE 'BUG %' ORDER BY id DESC")
```

**Feature Candidates:**
```
mcp__haios-memory__db_query(sql="SELECT id, content FROM concepts WHERE type = 'Critique' AND content LIKE 'FEATURE %' ORDER BY id DESC")
```

Report counts for each category.

#### 1b. Filesystem Scan (legacy)

```bash
just triage-observations
```

Report count of items with pending observations.

**Exit Criteria:**
- [ ] Memory scan completed (K/S/S, bugs, features)
- [ ] Filesystem scan completed
- [ ] Counts reported for both sources

**Tools:** mcp__haios-memory__db_query, Bash(just triage-observations), Read

---

### 2. TRIAGE Phase

**Goal:** Process observations from both memory and filesystem sources.

#### 2a. Retro-Triage (memory source, WORK-143)

**K/S/S Frequency Aggregation:**
From K/S/S directive query results, group by directive text (normalized):
- Count frequency of each Keep/Stop/Start directive across entries
- Format: `KEEP-N:` prefix → category=keep, directive=text after prefix
- Rank by frequency descending — high-frequency directives are strongest signals
- Present aggregated K/S/S to operator with counts

**Bug Candidate Surfacing:**
From bug query results, parse `BUG (confidence): description` format:
- Extract confidence tag (high/medium/low) and description
- Sort by confidence (high first)
- Present to operator for disposition (spawn:WORK, spawn:FIX, dismiss)

**Feature Candidate Surfacing:**
From feature query results, parse `FEATURE (confidence): description` format:
- Extract confidence tag and description
- Sort by confidence (high first)
- Present to operator for epoch-level triage (spawn:WORK, discuss, dismiss)

#### 2b. Legacy Triage (filesystem source)

**Triage Dimensions (Industry Standard):**

| Dimension | Question | Values |
|-----------|----------|--------|
| **Category** | What type? | bug, gap, debt, insight, question, noise |
| **Action** | What to do? | spawn:INV, spawn:WORK, spawn:FIX, memory, discuss, dismiss |
| **Priority** | When? | P0 (blocking), P1 (this session), P2 (next), P3 (backlog) |

For each filesystem observation, prompt for dimensions:
- Category: What type of observation is this?
- Action: What should happen next?
- Priority: How urgent is this?

**Example Triage Prompt:**
```
Observation: "commit-close recipe uses legacy patterns"
Section: Gaps Noticed
Source: E2-217

Category? [bug/gap/debt/insight/question/noise]: gap
Action? [spawn:INV/spawn:WORK/spawn:FIX/memory/discuss/dismiss]: spawn:FIX
Priority? [P0/P1/P2/P3]: P2
```

**Exit Criteria:**
- [ ] Retro-triage: K/S/S aggregation presented, bug/feature candidates surfaced
- [ ] Legacy triage: All filesystem observations triaged with valid dimensions
- [ ] Combined triaged list ready for promotion

**Tools:** AskUserQuestion (for dimension selection and disposition), triage_observation()

---

### 3. PROMOTE Phase

**Goal:** Execute the action for each triaged observation.

**Action Handlers:**

| Action | Execution |
|--------|-----------|
| `spawn:INV` | Create investigation via `/new-investigation` |
| `spawn:WORK` | Create work item via `/new-work` |
| `spawn:FIX` | Create quick fix work item (priority P1) |
| `memory` | Store insight via `ingester_ingest` |
| `discuss` | Flag for operator (report but no action) |
| `dismiss` | Mark as noise (no action needed) |

**Actions:**
1. For each triaged observation, execute action
2. Track results (spawned IDs, memory IDs)
3. Update observations.md with triage log entry
4. Set triage_status: triaged in frontmatter

**Exit Criteria:**
- [ ] All actions executed
- [ ] Observations.md updated with triage log
- [ ] triage_status updated to triaged

**Tools:** /new-investigation, /new-work, ingester_ingest, Edit

---

## Composition Map

| Phase | Primary Tool | Output |
|-------|--------------|--------|
| SCAN (memory) | mcp__haios-memory__db_query | K/S/S directives, bug/feature candidates |
| SCAN (filesystem) | Bash, Read | List of pending observations |
| TRIAGE (retro) | AskUserQuestion | KSS aggregation, candidate disposition |
| TRIAGE (legacy) | AskUserQuestion | Triaged observation list |
| PROMOTE | /new-*, ingester | Action results |

---

## Quick Reference

| Phase | Question to Ask | If NO |
|-------|-----------------|-------|
| SCAN | Any pending observations? | Exit - nothing to triage |
| TRIAGE | All dimensions valid? | Reprompt with validation error |
| PROMOTE | Action executed? | Report error, continue to next |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Standalone skill | Not embedded in close-work-cycle | Keeps closure lean; triage runs independently |
| Interactive triage | Agent prompts per observation | Avoids automated misclassification |
| triage_status field | In frontmatter | Enables scan to skip processed files |
| Industry dimensions | bug/gap/debt/insight/question/noise | Aligns with bug triage patterns |
| Dual-source scan (WORK-143) | Memory + filesystem | Retro-cycle stores to memory; legacy observations in files. Both sources feed triage. |
| Content-pattern queries (WORK-143) | Query by type + content prefix, NOT source_adr | A1 critique: ingester_ingest source_path not stored in source_adr. Content patterns verified against actual data. |
| MCP db_query for memory scan (WORK-143) | Agent calls db_query directly | Python functions use db_query_fn injection for testability. Agent uses MCP tool at runtime. |

---

## Related

- **E2-217:** Observation Capture Gate (capture mechanism)
- **INV-047:** Close Cycle Observation Phase Ordering (capture timing)
- **INV-023:** ReasoningBank Feedback Loop Architecture (same pattern)
- **close-work-cycle skill:** Captures observations during closure
- **retro-cycle skill:** Produces typed outputs stored to memory (WORK-142)
- **observations.py:** Core functions for scan, parse, triage, promote, and retro-triage (WORK-143)
- **WORK-143:** Retro-triage consumer update for memory-based provenance tags
