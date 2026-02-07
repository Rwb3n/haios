# generated: 2025-12-30
# System Auto: last updated on: 2025-12-30T23:12:32
# Section 9: Slash Commands

Generated: 2025-12-30 (Session 151)
Purpose: Document all slash commands, invocation patterns, and chaining behavior
Status: COMPLETE

---

## Gaps Identified (S152 Analysis)

| Gap | Description | Target Fix |
|-----|-------------|------------|
| **Argument handling inconsistent** | Some use `$ARGUMENTS`, others use positional parsing | Standardize argument schema in frontmatter |
| **allowed-tools not enforced** | Commands declare tools but Claude can use any | Make informational or enforce via hooks |
| **No command state machine** | Commands invoked manually, no auto-suggestion | Track command history, suggest next based on work state |

---

## Target Architecture: Command Schema

```yaml
# .claude/haios/config/command-manifest.yaml
commands:
  new-work:
    description: Create work item
    arguments:
      - name: backlog_id
        required: true
        pattern: "^(E2|INV)-\\d+$"
      - name: title
        required: true
        type: string
    chains_to: work-creation-cycle
    phase_context: backlog  # When to suggest this command

  close:
    description: Close work item with DoD validation
    arguments:
      - name: backlog_id
        required: true
    chains_to: close-work-cycle
    phase_context: implement  # Suggest after implementation
    gates:
      - dod-validation-cycle
```

**Portable:** Commands are Claude CLI native. Manifest in `.claude/haios/config/` for LLM-agnostic parsing.

---

## Overview

Slash commands are user-invocable prompts that serve as entry points for human operators. They live in `.claude/commands/<name>.md` and are invoked by typing `/<name>`.

**Location:** `.claude/commands/` (18 files)
**Invocation:** User types `/<name>` or `Skill(skill="<name>")`

---

## Command Inventory (18 commands)

### Session Commands

| Command | Purpose | Chains To |
|---------|---------|-----------|
| `/coldstart` | Session initialization, context load | work routing via `just ready` |
| `/haios` | Show full haios-status.json | - |
| `/status` | Show system health | - |

### Creation Commands

| Command | Purpose | Chains To |
|---------|---------|-----------|
| `/new-work` | Create work item | work-creation-cycle |
| `/new-plan` | Create implementation plan | plan-authoring-cycle → implementation-cycle |
| `/new-investigation` | Create investigation | investigation-cycle |
| `/new-checkpoint` | Create checkpoint | checkpoint-cycle |
| `/new-adr` | Create Architecture Decision Record | - |
| `/new-handoff` | Create handoff document | - |
| `/new-report` | Create report document | - |

### Lifecycle Commands

| Command | Purpose | Chains To |
|---------|---------|-----------|
| `/implement` | Start implementation cycle | implementation-cycle |
| `/close` | Close work item | close-work-cycle |

### Utility Commands

| Command | Purpose | Chains To |
|---------|---------|-----------|
| `/validate` | Validate file against template | - |
| `/schema` | Database schema lookup | - |
| `/ready` | Show unblocked work | - |
| `/tree` | Show milestone progress | - |
| `/workspace` | Show workspace status | - |
| `/reason` | Inject reasoning framework | - |

---

## Command Structure

### File Location
```
.claude/commands/<name>.md
```

### Frontmatter Fields

| Field | Purpose | Example |
|-------|---------|---------|
| `allowed-tools` | Tools the command can use | `Read, Glob, Bash` |
| `description` | Brief description | `Initialize session...` |
| `argument-hint` | Expected arguments | `<backlog_id>` |
| `generated` | Creation date | `2025-12-25` |
| `last_updated` | Last modification | `2025-12-28T10:52:20` |

### Example Frontmatter
```yaml
---
allowed-tools: Bash, Edit, Read, Grep, Glob, mcp__haios-memory__ingester_ingest
description: Close a work item with DoD validation
argument-hint: <backlog_id>
generated: 2025-12-22
last_updated: '2025-12-28T10:52:20'
---
```

---

## Chaining Patterns

### Creation → Cycle Chain
```
/new-work <id> <title>
    ↓
work-creation-cycle (VERIFY→POPULATE→READY→CHAIN)
    ↓
If INV-*: investigation-cycle
If E2-* with plan: implementation-cycle
```

### Plan → Implementation Chain
```
/new-plan <id> <title>
    ↓
plan-authoring-cycle (ANALYZE→AUTHOR→VALIDATE)
    ↓
implementation-cycle (PLAN→DO→CHECK→DONE)
```

### Close Chain
```
/close <id>
    ↓
close-work-cycle (VALIDATE→OBSERVE→ARCHIVE→MEMORY→CHAIN)
    ↓
routing-gate → next work
```

---

## Key Command Details

### `/coldstart`

**Purpose:** Initialize session with full context load

**Actions:**
1. Read CLAUDE.md, epistemic_state.md
2. Read L0-L2 context (north-star, invariants, roadmap)
3. Read latest checkpoint
4. Read haios-status-slim.json
5. Run `just --list`
6. Query memory with session_recovery mode
7. Run `just ready` to find work

**Memory Integration:** `memory_search_with_experience(mode='session_recovery')`

### `/close <id>`

**Purpose:** Close work item with DoD validation

**Actions:**
1. Find work file (directory or flat)
2. Chain to `close-work-cycle`
3. Validate DoD per ADR-033
4. Archive work file
5. Store closure to memory
6. Update status

**Gate:** DoD must pass (tests, WHY captured, docs current)

### `/new-plan <id> <title>`

**Purpose:** Create implementation plan

**Actions:**
1. Scaffold plan document
2. Chain to plan-authoring-cycle
3. After approval, chain to implementation-cycle

**Memory Integration:** Query for prior patterns

---

## Standalone vs Chaining Commands

### Standalone (No Skill Chain)
```
/haios          → Just reads haios-status.json
/status         → Just shows health
/validate       → Just validates file
/schema         → Just queries schema
/ready          → Just runs `just ready`
/tree           → Just runs `just tree`
/workspace      → Just shows workspace
/reason         → Just injects framework
/new-adr        → Just scaffolds (no cycle)
/new-handoff    → Just scaffolds (no cycle)
/new-report     → Just scaffolds (no cycle)
```

### Chaining (Invokes Skill)
```
/coldstart          → work routing
/new-work           → work-creation-cycle
/new-plan           → plan-authoring-cycle → implementation-cycle
/new-investigation  → investigation-cycle
/new-checkpoint     → checkpoint-cycle
/implement          → implementation-cycle
/close              → close-work-cycle
```

---

## Argument Handling

### Pattern: `$ARGUMENTS`
Commands receive arguments via `$ARGUMENTS` variable:
```markdown
**Arguments:** $ARGUMENTS

Parse the backlog_id (e.g., `E2-023`, `INV-033`).
```

### Common Argument Types

| Type | Format | Example |
|------|--------|---------|
| backlog_id | `E2-NNN` or `INV-NNN` | `E2-155`, `INV-035` |
| title | Quoted string | `"My Feature"` |
| file path | Relative path | `docs/plans/PLAN.md` |

---

## Command vs Skill Disambiguation

| User Types | Claude Sees | Action |
|------------|-------------|--------|
| `/coldstart` | Command invocation | Load + execute command prompt |
| `Skill(skill="coldstart")` | Skill invocation | Same effect (commands are skills) |
| `/implementation-cycle` | **Invalid** | Commands and skills have different namespaces |
| `Skill(skill="implementation-cycle")` | Skill invocation | Execute skill |

**Key insight:** Commands are a subset of skills intended for human invocation.

---

*Populated Session 151*
