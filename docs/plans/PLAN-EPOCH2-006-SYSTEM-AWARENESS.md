---
template: implementation_plan
status: complete
date: 2025-12-06
backlog_id: E2-006
title: "PLAN-EPOCH2-006: HAIOS System Awareness"
author: Hephaestus
project_phase: Phase 8 Complete
version: "1.0"
---
# generated: 2025-12-06
# System Auto: last updated on: 2025-12-09 18:48:49
# Implementation Plan: HAIOS System Awareness

@docs/README.md
@.claude/settings.local.json

> **ID:** PLAN-EPOCH2-006-SYSTEM-AWARENESS
> **Status:** Draft
> **Author:** Hephaestus (Builder)
> **Context:** Epoch 2 Enablement - Agent Situational Awareness

---

## 1. Goal

Give agents visibility into what HAIOS infrastructure is actively supporting them, similar to how Claude CLI shows its own components (MCP servers, permissions, output style).

## 2. Problem Statement

**Claude CLI provides self-awareness:**
- Shows active MCP servers
- Shows available tools
- Shows permissions
- Shows output style

**HAIOS has NO equivalent:**
- Agent doesn't know which hooks are active
- Agent doesn't know auto-timestamps are being added
- Agent doesn't know validation runs on every edit
- Agent doesn't know what memory injection is doing (or failing)
- Agent doesn't know what skills are available

**Result:** Agent operates blind to its support infrastructure. Can't troubleshoot issues. Doesn't leverage available features.

**Evidence:** This session - I kept trying to add timestamps manually, not knowing the system already does this.

---

## 3. Proposed Solution

### 3.1. `/haios` Command - System Status

**Purpose:** Single command to show all HAIOS-specific infrastructure.

**Output Format:**
```
HAIOS System Status
===================

HOOKS (Active)
--------------
UserPromptSubmit:
  - Date/time injection (WORKING)
  - Memory context injection via memory_retrieval.py (UNKNOWN)

PostToolUse (Edit|Write|MultiEdit):
  - Auto-timestamp: Adds "System Auto: last updated on:" to files
  - Validation: Runs ValidateTemplateHook.ps1

Stop:
  - Reasoning extraction via reasoning_extraction.py (UNKNOWN)

AUTO-FEATURES
-------------
Timestamps:    Auto-added to edited .md files
Validation:    Runs on every Edit/Write
Templates:     6 valid types (checkpoint, implementation_plan, etc.)
@ References:  Minimum 2 required per template file

MEMORY SYSTEM
-------------
MCP Server:    haios-memory (ONLINE)
Tools:         13 available
Concepts:      60,446
Embeddings:    100% coverage
Retrieval:     Status UNKNOWN (check logs)

SKILLS
------
extract-content    Content extraction from documents
memory-agent       Memory retrieval with reasoning

AGENTS
------
The-Proposer       Architect-1 (HAiOS)
The-Adversary      Architect-2 (HAiOS)

SESSION
-------
Current:       35 (estimated from checkpoint dates)
Output Style:  hephaestus (Builder)
```

### 3.2. Integration with `/coldstart`

Add HAIOS awareness to the coldstart command:

```markdown
# Cold Start (Enhanced)

1. Read essential files (CLAUDE.md, epistemic_state.md, latest checkpoint)
2. **NEW:** Display HAIOS system status (abbreviated)
3. Summarize key context
```

### 3.3. HAIOS Status Data Source

Create `.claude/haios-status.json` that captures current configuration:

```json
{
  "hooks": {
    "UserPromptSubmit": {
      "scripts": ["UserPromptSubmit.ps1", "ValidationAlertHook.ps1"],
      "features": ["date_time", "memory_injection", "validation_alerts"]
    },
    "PostToolUse": {
      "matcher": "Edit|Write|MultiEdit",
      "scripts": ["PostToolUse.ps1", "ValidateTemplateHook.ps1"],
      "features": ["auto_timestamp", "template_validation"]
    },
    "Stop": {
      "scripts": ["Stop.ps1"],
      "features": ["reasoning_extraction"]
    }
  },
  "auto_features": {
    "timestamps": true,
    "validation": true,
    "min_references": 2
  },
  "valid_templates": [
    "architecture_decision_record",
    "backlog_item",
    "checkpoint",
    "directive",
    "guide",
    "implementation_plan",
    "implementation_report",
    "meta_template",
    "readme",
    "verification"
  ],
  "memory": {
    "mcp_server": "haios-memory",
    "tools_count": 13
  },
  "skills": ["extract-content", "memory-agent"],
  "agents": ["The-Proposer", "The-Adversary"]
}
```

This file serves as:
1. Documentation for agents
2. Data source for `/haios` command
3. Single source of truth for HAIOS configuration

---

## 4. Implementation

### 4.1. File Structure

```
.claude/
  commands/
    haios.md           # /haios command
  haios-status.json    # Configuration data
```

### 4.2. `/haios` Command Logic

```markdown
---
allowed-tools: Read, Bash
description: Show HAIOS system status and active infrastructure
---

# HAIOS System Status

1. Read `.claude/haios-status.json` for configuration
2. Query memory stats via MCP or sqlite3
3. Check for recent logs in `.claude/logs/`
4. Format and display status

Present the full status showing:
- Active hooks and their features
- Auto-features enabled
- Memory system status
- Available skills and agents
- Current session estimate
```

---

## 5. Verification Plan

### 5.1. Test `/haios`
1. Run `/haios`
2. Verify all sections display
3. Verify memory stats are accurate
4. Verify hooks list matches settings.local.json

### 5.2. Test Agent Awareness
1. Start new session
2. Run `/coldstart`
3. Verify HAIOS status is included
4. Verify agent can reference the information

---

## 6. Benefits

| Benefit | Description |
|---------|-------------|
| **Troubleshooting** | Agent can see what's supposed to be running |
| **Feature Discovery** | Agent learns about available capabilities |
| **Debugging** | "Memory injection UNKNOWN" signals investigation needed |
| **Onboarding** | New agents immediately understand the environment |
| **Self-Correction** | Agent stops doing things the system already does |

---

## 7. Priority

**HIGH** - This is foundational for agent effectiveness. An agent that doesn't know its tools can't use them properly.

---

## 8. Relationship to Other Plans

| Plan | Relationship |
|------|-------------|
| PLAN-001 | `/haios` shows hook status, helps diagnose Python script issues |
| PLAN-003 | Memory status visible in `/haios` output |
| PLAN-005 | `/haios` complements `/status` (system vs project health) |

---

**Requested:** 2025-12-06
**Status:** DRAFT - Ready for implementation
