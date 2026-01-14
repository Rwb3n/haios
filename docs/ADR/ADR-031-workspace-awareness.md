---
template: architecture_decision_record
status: accepted
date: 2025-12-08
adr_id: ADR-031
title: "Operational Self-Awareness"
author: Hephaestus
session: 46
lifecycle_phase: decide
decision: accepted
---
# generated: 2025-12-07
# System Auto: last updated on: 2025-12-08 21:05:30
# ADR-031: Operational Self-Awareness

@docs/README.md
@docs/epistemic_state.md
@CLAUDE.md

> **Status:** Proposed
> **Date:** 2025-12-08
> **Decision:** Pending
> **Revision:** 2 (Session 46 - Complete reframing)

---

## The HAIOS Vision

HAIOS is an **operating-system-like orchestration layer** for AI-assisted project execution. It exists to make the **OPERATOR successful**.

Within HAIOS, **APIP (Agent Project Interface Protocol)** provides the governance model:
- Templates are Classes
- Documents are Instances
- Validation is Type Checking
- Slash Commands are Constructors
- Hooks are Event Handlers

**Hierarchy:** HAIOS (system) > APIP (protocol) > Hooks/Commands/Skills (mechanisms)

This ADR addresses a gap: **the system lacks awareness of its own operational state**.

---

## Problem Statement

HAIOS has governance infrastructure (hooks, commands, templates) but cannot answer:

1. **What work is outstanding?** - Checkpoints with pending items, handoffs awaiting investigation
2. **What's blocked?** - Backlog items stalled, plans waiting on dependencies
3. **What's forgotten?** - Reports incomplete, handoffs never picked up
4. **What's the operational rhythm?** - No heartbeat, no active management

The system governs document creation but doesn't understand document state.

### Current State

`haios-status.json` tracks **system infrastructure**:
- Hooks (PreToolUse, PostToolUse, UserPromptSubmit, Stop)
- Memory (concepts, entities, reasoning traces)
- Skills (memory-agent, extract-content)
- Templates (14 valid types)
- PM (backlog counts)

`haios-status.json.lifecycle` tracks **file existence**:
- 23 files with template, status, date, path
- Counts by status and lifecycle_phase

**Gap:** No understanding of **operational meaning**:
- Which checkpoints have unfinished work?
- Which handoffs are waiting for pickup?
- Which plans are approved but not started?
- Which backlog items are stale?

---

## Decision Drivers

### The Heartbeat Requirement

A self-aware system should:
1. **Know what's pending** - Surface outstanding items automatically
2. **Survive compaction** - Context transitions preserve critical state
3. **Actively manage flow** - Items reviewed, shuffled, merged, pruned
4. **Support composable commands** - `/coldstart` = `/haios` + `/workspace`

### Separation of Concerns

| Domain | Command | Scope |
|--------|---------|-------|
| **System Status** | `/haios` | Infrastructure: hooks, memory, skills, templates |
| **Workspace Status** | `/workspace` | Operations: checkpoints, handoffs, plans, reports, backlog |

Both query `haios-status.json` - different views of same data.

### Integration with Existing Rhythm

```
SESSION START
    SessionStart hook -> environment setup

USER PROMPT
    UserPromptSubmit hook -> date/time + memory strategies
    /coldstart -> /haios + /workspace + memory query (composable)

TOOL USE (governed paths)
    PreToolUse hook -> prompt for proper commands
    [Tool executes]
    PostToolUse hook -> timestamp + validation + status update

SESSION END
    Stop hook -> ReasoningBank extraction
```

**Workspace awareness plugs into existing rhythm, not parallel to it.**

---

## Considered Options

### Option A: Extend UpdateHaiosStatus.ps1 (Recommended)

**Description:** Add operational awareness to existing infrastructure.

UpdateHaiosStatus.ps1 already:
- Scans governed paths (checkpoints, plans, ADR, reports, handoff)
- Parses frontmatter (template, status, lifecycle_phase)
- Produces `lifecycle.live_files`

**Extension:**
1. Parse document content for outstanding items (checkboxes, pending sections)
2. Add `workspace` section to haios-status.json with operational state
3. Create `/workspace` command as view into this data
4. Integrate `/coldstart` to compose `/haios` + `/workspace`

**Pros:**
- Single source of truth (one script, one JSON)
- Follows existing rhythm (PostToolUse trigger)
- No new infrastructure
- Composable commands

**Cons:**
- UpdateHaiosStatus.ps1 grows in complexity
- Need to define "outstanding item" heuristics

### Option B: Separate UpdateWorkspace.ps1

**Description:** New script producing haios-workspace.json.

**Pros:**
- Separation of concerns (system vs operations)
- Independent evolution

**Cons:**
- 80% overlap with UpdateHaiosStatus.ps1
- Two files to maintain
- Two JSON files to query
- Violates DRY

### Option C: Database-Backed State

**Description:** Store operational state in haios_memory.db.

**Pros:**
- Rich queries
- Persistence

**Cons:**
- Synchronization complexity
- Overkill for current needs
- Adds database dependency to commands

---

## Decision

**Option A: Extend UpdateHaiosStatus.ps1**

Rationale:
1. **Single source of truth** - One script, one JSON, one rhythm
2. **Composable** - `/coldstart` = `/haios` + `/workspace` naturally
3. **Minimal change** - Extend existing patterns
4. **Heartbeat ready** - PostToolUse already triggers on file changes

---

## Implementation

### Phase 1: Extend haios-status.json Schema

Add `workspace` section:

```json
{
  "workspace": {
    "outstanding": {
      "checkpoints": [
        {"path": "...", "pending_items": ["Item 1", "Item 2"]}
      ],
      "handoffs": [
        {"path": "...", "status": "pending", "age_days": 2}
      ],
      "plans": [
        {"path": "...", "status": "approved", "not_started": true}
      ]
    },
    "stale": {
      "backlog_items": [
        {"id": "E2-003", "status": "blocked", "age_days": 5}
      ]
    },
    "summary": {
      "pending_handoffs": 3,
      "incomplete_checkpoints": 1,
      "stale_backlog": 2,
      "approved_not_started": 4
    }
  }
}
```

### Phase 2: Extend UpdateHaiosStatus.ps1

Add functions:
- `Get-OutstandingItems` - Parse checkboxes, pending sections
- `Get-StaleItems` - Age calculation, blocked detection
- `Get-WorkspaceSummary` - Aggregate counts

### Phase 3: Create /workspace Command

```markdown
---
description: Show operational workspace status
---
# Workspace Status

!`powershell.exe -Command "Get-Content '.claude/haios-status.json' | ConvertFrom-Json | Select-Object -ExpandProperty workspace | ConvertTo-Json -Depth 5"`

## Outstanding Work
[Parse and display pending items]

## Stale Items
[Parse and display items needing attention]

## Recommendations
[Suggest next actions based on state]
```

### Phase 4: Integrate with /coldstart

Modify coldstart.md to compose:
1. Load system status (`/haios` equivalent)
2. Load workspace status (`/workspace` equivalent)
3. Query memory for relevant strategies
4. Surface outstanding items prominently

### Phase 5: Heartbeat Integration

- PreCompact hook saves workspace state
- SessionStart hook restores awareness
- Stop hook checks for forgotten items

---

## Consequences

### Positive

- **Self-aware system** - Knows its own operational state
- **No amnesia** - Survives context compaction
- **Active management** - Outstanding items surfaced automatically
- **Composable commands** - Clean separation of system vs workspace
- **Single source of truth** - One script, one JSON

### Negative

- **Heuristics needed** - "Outstanding item" requires definition
- **Script complexity** - UpdateHaiosStatus.ps1 grows

### Neutral

- **No new files** - Extends existing infrastructure
- **HAIOS-RAW not indexed** - Legacy transformation is separate concern

---

## Relationship to Vision

```
                    HAIOS (Operating System)
                    "Make the OPERATOR successful"
                              |
              +---------------+---------------+
              |                               |
        System Status                 Workspace Status
        (/haios)                      (/workspace)
              |                               |
    +----+----+----+              +----+----+----+
    |    |    |    |              |    |    |    |
  Hooks Skills Mem  Templates   Checkpts Plans Handoffs Backlog

                    Composed by /coldstart
                    Survives compaction
                    Heartbeat of the system
```

---

## HAIOS-RAW Note

HAIOS-RAW (58 legacy ADRs) is **not** added to workspace scanning. HAIOS-RAW is the **subject of transformation**, not part of current governance. The system prepares to withstand that explosive transformation by being operationally self-aware first.

---

## References

- **Cody_Report_0047** - Hooks as automated task dispatchers
- **HAIOS-RAW/docs/onboarding/README.md** - Original HAiOS vision
- **Vision Interpretation Session** - "HAIOS exists to make the OPERATOR successful"
- **Memory Concept 64607** - Session 45 vision alignment

---
