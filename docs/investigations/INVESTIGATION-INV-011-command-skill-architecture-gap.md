---
template: investigation
status: complete
date: 2025-12-14
backlog_id: INV-011
title: "Investigation: Command-Skill Architecture Gap"
author: Hephaestus
lifecycle_phase: discovery
version: "1.0"
generated: 2025-12-22
last_updated: 2025-12-22T22:45:09
---
# Investigation: Command-Skill Architecture Gap

@docs/README.md
@docs/epistemic_state.md

---

## Context

Session 71 discovered that `/close E2-043` and `/close E2-044` required 6 manual steps each, despite being a "command". The operator asked: "why did you have to do manual actions just now?" This revealed a fundamental architecture gap in how Epoch 2 governance commands were built.

Commands like `/close` and `/coldstart` are **pure prompts** (instruction manuals for Claude to interpret), not **automation wrappers** (thin entries that invoke scripts/skills).

---

## Objective

Determine the correct architecture for governance commands and design a migration path from "commands as prompts" to "commands as skill invocations".

---

## Scope

### In Scope
- Command architecture patterns (COMMANDS-REF.md)
- Skill architecture patterns (SKILLS-REF.md)
- Current governance commands: `/close`, `/coldstart`, `/validate`, `/new-*`
- Hook integration with commands and skills
- Migration strategy for existing commands

### Out of Scope
- Memory retrieval architecture (covered by INV-010)
- Template validation logic (working correctly)
- Hook event triggers (working correctly)

---

## Hypotheses

1. **H1:** Commands should be thin wrappers that invoke skills or scripts, not thick instruction manuals
2. **H2:** The separation is: Command = WHAT (locks you in), Skill = HOW (pattern + tools)
3. **H3:** Scripts should be EXECUTED by skills, not interpreted step-by-step by Claude
4. **H4:** Progressive disclosure (metadata -> instructions -> resources) reduces context bloat

---

## Investigation Steps

### Analysis (Session 71 - COMPLETE)

1. [x] Compare working commands (`/new-*`) with broken commands (`/close`)
2. [x] Review COMMANDS-REF.md for intended command architecture
3. [x] Review SKILLS-REF.md for skill structure patterns
4. [x] Identify the architectural mistake

### Design (PENDING)

5. [ ] Design skill structure for `/close` workflow
6. [ ] Design skill structure for `/coldstart` workflow
7. [ ] Define command-skill interface pattern
8. [ ] Plan migration for existing commands

---

## Findings

### The Architectural Mistake

**What Commands CAN Do (per COMMANDS-REF.md):**
```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*)
---

## Context
- Current git status: !`git status`    # <-- Executed BEFORE prompt
- Current branch: !`git branch`        # <-- Actual automation
```

**What Skills ARE (per SKILLS-REF.md):**
```
skill-name/
+-- SKILL.md          # Instructions (loaded when triggered)
+-- scripts/
    +-- utility.py    # EXECUTED, not interpreted
```

**What We Built:**
```markdown
# .claude/commands/close.md
# Just a long prompt telling Claude what to do
## Step 1: Grep for backlog item...
## Step 2: Read the section...
## Step 3: Edit to remove...
## Step 4: Edit to append to archive...
## Step 5: Call ingester_ingest...
## Step 6: Run UpdateHaiosStatus.ps1...
```

### The Correct Pattern

| Layer | Purpose | Example |
|-------|---------|---------|
| **Command** | WHAT (entry point, locks tools) | `/close E2-043` |
| **Skill** | HOW (pattern + tools) | `close-work-item/SKILL.md` + scripts |
| **Script** | EXECUTE (automation) | `CloseWorkItem.ps1` |

**Command (thin wrapper):**
```markdown
---
allowed-tools: Skill(close-work-item)
description: Close a work item with DoD validation
---
Close work item: $ARGUMENTS
```

**Skill (pattern + tools):**
```
.claude/skills/close-work-item/
+-- SKILL.md              # DoD checklist, workflow pattern
+-- scripts/
    +-- CloseWorkItem.ps1 # Automation: parse, archive, update
```

### Current State Analysis

| Command | Architecture | Status |
|---------|--------------|--------|
| `/new-checkpoint` | Calls `ScaffoldTemplate.ps1` | CORRECT |
| `/new-investigation` | Calls `ScaffoldTemplate.ps1` | CORRECT |
| `/new-plan` | Calls `ScaffoldTemplate.ps1` | CORRECT |
| `/validate` | Calls `ValidateTemplate.ps1` | CORRECT |
| `/close` | Pure prompt, 6 manual steps | BROKEN |
| `/coldstart` | Pure prompt, manual reads | BROKEN |
| `/haios` | Reads haios-status.json | PARTIAL |
| `/status` | Calls pytest, git | PARTIAL |

### Root Cause

We conflated "documentation for Claude" with "automation that Claude triggers". The `/close` command is 150+ lines of instructions that Claude must interpret and execute step-by-step, leading to:
- Inconsistent execution
- Missed steps
- Manual errors
- Context bloat (loading instructions every time)

### The Insight (from Operator)

> "The command locks you in, then the skill gives you the pattern and tools for the pattern."

This is the correct mental model:
- **Command** = Entry point with constraints (allowed-tools)
- **Skill** = Capability with instructions + automation

### Untapped Hook Mechanisms (Session 72 Discovery)

HOOKS-REF.md reveals hook events we haven't leveraged:

**PreCompact** (lines 365-372):
- Fires BEFORE compact operation
- Matchers: `manual` (from `/compact`) or `auto` (context window full)
- Use case: Save state, prep for summary

**SessionStart with `compact` matcher** (lines 374-385):
- Fires AFTER compact completes (new session starts)
- Input includes `"source": "compact"` field
- Use case: Inject "you were compacted" signal into agent context

Example (not yet implemented):
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [{
          "type": "command",
          "command": "echo 'SYSTEM: Context compaction completed. Previous context summarized.'"
        }]
      }
    ]
  }
}
```

This is another instance of the same pattern: **the mechanism exists, we just haven't built the automation**.

---

## Spawned Work Items

### Immediate (Fix `/close`)
- [ ] E2-048: Create `close-work-item` skill with CloseWorkItem.ps1
- [ ] E2-049: Refactor `/close` command to invoke skill

### Secondary (Fix `/coldstart`)
- [ ] E2-050: Create `session-init` skill with context loading automation
- [ ] E2-051: Refactor `/coldstart` to invoke skill

### Hook Automation
- [ ] E2-055: Implement SessionStart[compact] hook for post-compact signaling
- [ ] E2-056: Implement PreCompact hook for state preservation

### Architectural
- [ ] ADR-038: Command-Skill Architecture (formalize the pattern)

---

## Supersession Notes (Session 101)

**Status: PARTIALLY SUPERSEDED**

The investigation correctly identified the command-skill architecture gap. However, the system evolved differently than the spawned work items specified:

**What Happened:**
1. E2-048-051 (close skill, coldstart skill) were never implemented
2. E2-055-056 (PreCompact, SessionStart hooks) were never implemented
3. ADR-038 was created but covers Symphony Architecture, not Command-Skill

**What DID Happen:**
- implementation-cycle skill exists (different approach)
- investigation-cycle skill exists (different approach)
- /close command works via detailed prompt (not skill invocation)
- /coldstart works via detailed prompt (not skill invocation)

**Assessment:**
The vision ("command locks you in, skill gives pattern and tools") was VALID but the implementation path diverged. Commands still use prompt-based instructions rather than invoking dedicated skills. This may be revisited in Epoch 3 with INV-022 (Work-Cycle-DAG).

**Spawned Items Status:**
- E2-048, E2-049, E2-050, E2-051: Ghost IDs (never created in backlog)
- ADR-038: Different topic (Symphony, not Command-Skill)

---

## Expected Deliverables

- [x] Findings report (this document)
- [x] Architecture pattern definition
- [~] Skill structure design for `/close` - SUPERSEDED
- [~] Migration plan for existing commands - SUPERSEDED
- [x] Memory storage (concepts)

---

## References

- `.claude/COMMANDS-REF.md` - Claude Code command documentation
- `.claude/SKILLS-REF.md` - Claude Code skill documentation
- `.claude/HOOKS-REF.md` - Claude Code hook events (PreCompact, SessionStart matchers)
- `.claude/commands/close.md` - Current (broken) implementation
- `.claude/skills/memory-agent/` - Example working skill structure
- INV-010: Memory Retrieval Architecture Mismatch (related context bloat issue)

---
