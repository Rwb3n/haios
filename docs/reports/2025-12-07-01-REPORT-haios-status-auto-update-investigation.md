---
template: report
status: completed
date: 2025-12-07
title: "Investigation: haios-status.json Auto-Update Mechanism"
author: Hephaestus
session: 39
tags: [report, analysis, governance, automation]
---
# generated: 2025-12-07
# System Auto: last updated on: 2025-12-07 11:05:29
# Investigation: haios-status.json Auto-Update Mechanism

@docs/README.md
@docs/epistemic_state.md

> **Date:** 2025-12-07
> **Session:** 39
> **Assignee:** Hephaestus
> **Status:** Completed

---

## Executive Summary

Investigated sources for auto-populating `haios-status.json` to eliminate manual updates. Identified 6 data sources that can feed into the status file: templates directory, memory MCP stats, backlog.md, checkpoints, and hooks directory. Recommended PowerShell-based solution triggered by `/coldstart` and `/haios` commands.

Key insight: Template YAML front matter and section headers form a queryable schema that can be indexed to memory for cross-referencing.

---

## Technical Details

### 1. Current haios-status.json Structure

```json
{
  "hooks": { ... },           // Static - configured hooks
  "auto_features": { ... },   // Static - feature flags
  "valid_templates": [...],   // CAN AUTO-DERIVE from .claude/templates/
  "memory": {
    "mcp_server": "haios-memory",
    "tools_count": 13         // CAN AUTO-DERIVE from memory_stats()
  },
  "skills": [...],            // Static - available skills
  "agents": [...],            // Static - available agents
  "pm": {
    "backlog_path": "docs/pm/backlog.md",
    "active_count": 5,        // CAN AUTO-DERIVE from backlog parsing
    "last_session": 38        // CAN AUTO-DERIVE from latest checkpoint
  }
}
```

### 2. Data Sources for Auto-Population

| Field | Source | Method |
|-------|--------|--------|
| `valid_templates[]` | `.claude/templates/*.md` | Scan directory, extract `template:` from YAML front matter |
| `memory.concepts_count` | `memory_stats()` | MCP tool call returns JSON with counts |
| `memory.entities_count` | `memory_stats()` | MCP tool call |
| `memory.reasoning_traces` | `memory_stats()` | MCP tool call |
| `memory.embeddings_count` | `memory_stats()` | MCP tool call |
| `pm.active_count` | `docs/pm/backlog.md` | Parse markdown, count items not marked done |
| `pm.last_session` | `docs/checkpoints/*.md` | Find latest file by date, extract session from filename |
| `hooks.*` | `.claude/hooks/*.ps1` | Enumerate directory for hook scripts |

### 3. Template-as-Schema Architecture

Templates have parseable structure that enables queryable indexing:

**YAML Front Matter Fields:**
- `template`: Type identifier (checkpoint, plan, report, etc.)
- `status`: Lifecycle state (draft, active, completed, archived)
- `date`: Creation/update date
- `title`: Human-readable title
- `session`: Session number (for checkpoints)
- `author`: Creator agent

**Section Headers (## Headings):**
- `## Session Summary` - Brief description
- `## Key Findings` - Important discoveries
- `## Pending Work` - Outstanding items
- `## Completed Work` - Done items

**Query Examples:**
- "Find checkpoints where Key Findings mention 'hook'"
- "List plans with status: in_progress"
- "Show all reports from session 38+"

### 4. Implementation Options Analysis

| Option | Trigger | Pros | Cons |
|--------|---------|------|------|
| **A. PowerShell Script** | `/coldstart`, `/haios` | Native to hook ecosystem, low complexity | Requires Python subprocess for memory stats |
| **B. PostToolUse Hook** | File changes in governed paths | Real-time updates | Risk of infinite loops, complexity |
| **C. Python Module** | CLI command | Full access to memory MCP, database | Separate runtime, not integrated with hooks |
| **D. Hybrid (Recommended)** | `/haios` triggers PS1, which calls Python | Best of both worlds | Two-language coordination |

---

## Recommendations / Next Steps

1. **Implement Option D (Hybrid)**: Create `UpdateHaiosStatus.ps1` that:
   - Scans `.claude/templates/` for valid_templates
   - Scans `.claude/hooks/` for active hooks
   - Calls Python subprocess to get memory_stats()
   - Parses `docs/pm/backlog.md` for active_count
   - Finds latest checkpoint for last_session
   - Writes updated `haios-status.json`

2. **Wire to /haios command**: Call the update script before displaying status

3. **Consider Template Indexing**: PostToolUse hook could extract YAML + sections and store to memory for cross-referencing

4. **Add Caching**: Optional TTL (e.g., 60s) to avoid redundant file system scans

---

## Artifacts

- `.claude/haios-status.json` - Current manual status file
- `.claude/templates/*.md` - Template source files
- `docs/pm/backlog.md` - Backlog source file
- `docs/checkpoints/*.md` - Checkpoint source files

---

## Related

- Session 38 Checkpoint: `docs/checkpoints/2025-12-07-01-SESSION-38-governance-pm-structure.md`
- PM Self-Awareness Plan: `docs/plans/PLAN-PM-SELF-AWARENESS.md`

---


<!-- VALIDATION ERRORS (2025-12-07 11:05:30):
  - ERROR: Unknown template type 'report'. Valid types: architecture_decision_record, backlog_item, checkpoint, directive, guide, implementation_plan, implementation_report, meta_template, readme, verification
-->
