---
template: implementation_plan
status: complete
date: 2025-12-06
backlog_id: E2-005
title: "PLAN-EPOCH2-005: Utility Commands"
author: Hephaestus
project_phase: Phase 8 Complete
version: "1.0"
---
# generated: 2025-12-06
# System Auto: last updated on: 2025-12-09 18:48:46
# Implementation Plan: Utility Commands

@docs/README.md
@.claude/COMMANDS-REF.md

> **ID:** PLAN-EPOCH2-005-UTILITY-COMMANDS
> **Status:** Draft
> **Author:** Hephaestus (Builder)
> **Context:** Epoch 2 Enablement - Make Right Thing Easy

---

## 1. Goal

Create utility slash commands that reduce friction for common governance tasks: system status checks, cold start initialization, and session checkpointing.

## 2. Problem Statement

Common tasks require multiple manual steps:

| Task | Current Steps | Friction |
|------|--------------|----------|
| Check system health | Run pytest, check memory, check git | 3+ commands |
| Cold start | Read CLAUDE.md, epistemic_state, latest checkpoint | 3+ file reads |
| Create checkpoint | Remember template, fill YAML, add refs | Error-prone |

**Result:** These tasks get skipped or done inconsistently.

---

## 3. Proposed Commands

### 3.1. `/status` - System Health Dashboard

**Purpose:** Single command to see system health.

**Output:**
```
HAIOS Status
============
Tests:      154 passing
Memory:     60,446 concepts | 100% embedded
Validation: 4 files with errors
Git:        3 modified, 0 staged
Session:    35 (current)
```

**Implementation:**
```markdown
---
allowed-tools: Bash, Read
description: Show HAIOS system health (tests, memory, validation, git)
---

# System Status

Run the following diagnostics:

1. **Tests:** `pytest --collect-only -q 2>/dev/null | tail -1`
2. **Memory:** Query haios_memory.db for concept count
3. **Validation:** Count files with validation errors in recent output
4. **Git:** `git status --short`
5. **Session:** Extract from latest checkpoint filename

Present as a compact dashboard.
```

### 3.2. `/coldstart` - Session Initialization

**Purpose:** Load essential context for new session or after context loss.

**Behavior:**
1. Read CLAUDE.md (agent instructions)
2. Read docs/epistemic_state.md (current state)
3. Read latest checkpoint (most recent session context)
4. Summarize key points

**Implementation:**
```markdown
---
allowed-tools: Read, Glob
description: Initialize session by loading essential context files
---

# Cold Start Initialization

Load and summarize these files in order:

1. **Agent Instructions:** Read `CLAUDE.md`
2. **Current State:** Read `docs/epistemic_state.md`
3. **Latest Checkpoint:** Find most recent file in `docs/checkpoints/` and read it

After reading, provide a brief summary:
- Current phase
- Last session focus
- Key pending items
```

### 3.3. `/checkpoint` - Quick Session Checkpoint

**Purpose:** Create session checkpoint with minimal friction.

**Arguments:** `<session_number> <title>`

**Behavior:**
1. Generate filename: `<DATE>-SESSION-<NUM>-<slug>.md`
2. Use checkpoint template (proper YAML, @ refs)
3. Auto-fill date, session number
4. Prompt for summary content

**Implementation:**
```markdown
---
allowed-tools: Write, Bash
description: Create a session checkpoint with proper template
argument-hint: <session_number> <title>
---

# Create Session Checkpoint

Arguments: $ARGUMENTS

1. Parse session number and title from arguments
2. Generate filename: `docs/checkpoints/YYYY-MM-DD-SESSION-<NUM>-<slug>.md`
3. Create file with checkpoint template:
   - YAML header (template: checkpoint, status: complete, date, session, etc.)
   - @ references to docs/README.md and docs/epistemic_state.md
   - Standard sections (Summary, Completed Work, Files Modified, Pending, Continuation)
4. Report success with file path
```

### 3.4. `/handoff` - Quick Handoff Creation

**Purpose:** Create handoff document with type-specific template.

**Arguments:** `<type> <name>`
- Types: investigation, task, bug, enhancement, evaluation

**Behavior:**
1. Generate filename: `<DATE>-<TYPE>-<name>.md`
2. Use type-specific template
3. Auto-fill date, type
4. Include proper YAML and @ refs

---

## 4. File Structure

```
.claude/commands/
  status.md        # /status
  coldstart.md     # /coldstart
  checkpoint.md    # /checkpoint
  handoff.md       # /handoff
```

---

## 5. Verification Plan

### 5.1. Test `/status`
1. Run `/status`
2. Verify all 5 metrics displayed
3. Verify accurate counts

### 5.2. Test `/coldstart`
1. Run `/coldstart`
2. Verify 3 files read
3. Verify summary produced

### 5.3. Test `/checkpoint`
1. Run `/checkpoint 35 test-session`
2. Verify file created with correct template
3. Verify no validation errors

### 5.4. Test `/handoff`
1. Run `/handoff investigation test-issue`
2. Verify file created in docs/handoff/
3. Verify correct template for type

---

## 6. Priority Order

| Command | Priority | Rationale |
|---------|----------|-----------|
| `/status` | HIGH | Instant visibility, catches issues early |
| `/checkpoint` | HIGH | Enables session discipline |
| `/coldstart` | MEDIUM | Helps but manual read works |
| `/handoff` | MEDIUM | Less frequent than checkpoints |

---

## 7. Risks

- **Command parsing:** Slash commands have limited argument handling
- **Path resolution:** Commands run from project root, paths must be relative
- **Output length:** Status must be concise to avoid clutter

---

## 8. Relationship to Other Plans

| Plan | Relationship |
|------|-------------|
| PLAN-004 | Complementary: Handles heavy artifacts (`/new-plan`, `/new-report`) vs Utilities (`/checkpoint`, `/handoff`) |
| PLAN-002 | `/status` could include validation count |
| PLAN-003 | `/status` includes memory stats |

---

**Requested:** 2025-12-06
**Status:** DRAFT - Ready for implementation


<!-- VALIDATION ERRORS (2025-12-06 15:03:44):
  - ERROR: Missing required fields: directive_id
-->
