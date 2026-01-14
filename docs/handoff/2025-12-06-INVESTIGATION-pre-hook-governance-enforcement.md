---
template: handoff_investigation
status: closed
date: 2025-12-06
title: "Investigation: Pre-Hook Governance Enforcement"
author: Hephaestus
priority: high
session: 37
assignee: Gemini
---
# generated: 2025-12-06
# System Auto: last updated on: 2025-12-06 22:45:00
# Investigation: Pre-Hook Governance Enforcement

@docs/epistemic_state.md
@.claude/hooks/README.md

> **Date:** 2025-12-06
> **Session:** 37
> **Priority:** High
> **Assignee:** Gemini (Genesis)
> **Status:** Closed

---

## Findings (Session 37)

**Experiment:**
- Created `PreToolUse.ps1` in `.claude/hooks/`.
- Triggered file write operation.
- **Result:** Hook was NOT triggered. Log file not created.

**Conclusion:**
- **PreToolUse hook is NOT supported** in the current environment.
- Hard blocking of file operations via hooks is **infeasible**.

**Recommendation:**
Proceed with **Reactive Governance** (Solution 2 + 3 + 4):
1.  **PostToolUse Redirect:** Enhance `PostToolUse.ps1` to detect when a governed file (e.g., `checkpoint.md`) is created WITHOUT the template wizard.
    - Action: Warn the agent in the output: *"Warning: You created a checkpoint manually. Next time, use `/checkpoint` to ensure compliance."*
2.  **Agent Instructions:** Update `CLAUDE.md` with explicit mapping of "Intent -> Command".
3.  **Memory Reminders:** Ensure `/coldstart` loads these rules into context so the agent knows them before acting.

---

## Problem Statement
...

Agents bypass governance tools even when they exist. Example from Session 37:

**What happened:**
- Agent needed to create a checkpoint
- Used `Write` tool to create raw markdown
- Did NOT use `/checkpoint` command (which invokes ScaffoldTemplate.ps1)

**Why it's a problem:**
- Templates exist but aren't enforced
- Skills exist but aren't invoked
- Memory tools exist but aren't queried
- "Doing right should be easy" but wrong is easier

---

## Investigation Request

Research solutions for **pre-execution hooks** that:

1. **Intercept** file creation before it happens
2. **Analyze** the intended file type/path
3. **Suggest/Enforce** appropriate governance tools
4. **Block** raw writes to governed paths (optional)

---

## Reference Files to Examine

### Current Hook Infrastructure
```
.claude/hooks/
├── UserPromptSubmit.ps1    # Pre-prompt hook (injects memory)
├── PostToolUse.ps1         # Post-edit hook (timestamps, validation)
├── Stop.ps1                # Session end hook (extraction)
├── ValidateTemplateHook.ps1
├── ScaffoldTemplate.ps1    # Template instantiation
└── README.md
```

### Current Templates
```
.claude/templates/
├── checkpoint.md
├── implementation_plan.md
├── handoff_investigation.md
└── README.md
```

### Current Commands
```
.claude/commands/
├── coldstart.md
├── haios.md
├── status.md
├── validate.md
├── new-plan.md
├── checkpoint.md
├── handoff.md
└── README.md
```

### Claude Code Hook Events
Research what hook events Claude Code supports:
- `UserPromptSubmit` (exists, used)
- `PostToolUse` (exists, used)
- `Stop` (exists, used)
- `PreToolUse` (does it exist?)
- Others?

---

## Potential Solutions

### S1: PreToolUse Hook (if supported)
If Claude Code has a PreToolUse hook:
```powershell
# .claude/hooks/PreToolUse.ps1
# Intercept Write/Edit operations
# Check if path matches governed pattern
# Return suggestion/block if template exists
```

### S2: PostToolUse Redirect
Enhance existing PostToolUse to:
- Detect when governed file was written raw
- Warn agent to use proper command next time
- Optionally reprocess through template

### S3: Agent Instructions Enhancement
Add to CLAUDE.md:
```markdown
## File Creation Rules
- Creating checkpoint? Use /checkpoint command
- Creating plan? Use /new-plan command
- Creating handoff? Use /handoff command
NEVER use raw Write for governed file types
```

### S4: Memory-Based Reminders
Store governance rules in memory:
- When agent queries for "create checkpoint", memory returns "use /checkpoint"
- Proactive reminder before file operations

### S5: Hybrid Approach
Combine multiple solutions:
1. Instructions (soft enforcement)
2. PostToolUse warnings (feedback)
3. Memory reminders (contextual)
4. PreToolUse blocks (hard enforcement, if available)

---

## Success Criteria

| Criterion | Test |
|-----------|------|
| Detection | System detects when governed file is created raw |
| Suggestion | Agent receives suggestion for proper command |
| Adoption | Agent uses commands instead of raw Write |
| Optional: Blocking | Raw writes to governed paths are blocked |

---

## Deliverables

1. Research report on Claude Code hook capabilities
2. Recommended solution architecture
3. Implementation plan (if feasible)

---

## Context

This investigation supports PLAN-EPOCH2-008 (Memory System Leverage):
- Governance tools exist but aren't used
- Infrastructure is built but not enforced
- Need mechanisms to close the loop

---

**Created:** Session 37
**Assignee:** Gemini (Genesis)
**Deadline:** Before Epoch 2 completion
