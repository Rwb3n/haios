---
template: readme
status: active
date: 2025-12-06
component: commands
generated: 2025-12-23
last_updated: '2026-01-25T01:50:11'
---
# Slash Commands

Custom slash commands for HAIOS governance. Available via `/command` syntax.

@.claude/hooks/README.md
@.claude/templates/README.md

## Available Commands

| Command | Description | Implementation |
|---------|-------------|----------------|
| `/coldstart` | Load session context | Reads CLAUDE.md, epistemic_state.md, latest checkpoint |
| `/haios` | Show system status | Dashboard with hooks, memory, agents status |
| `/status` | Compact status | Tests, memory count, git status |
| `/validate <file>` | Validate template | `just validate` recipe |
| `/new-plan <backlog_id> <title>` | Create plan → implementation-cycle | `just plan` → skill chain |
| `/new-checkpoint <session> <title>` | Create checkpoint from template | `just checkpoint` recipe |
| `/new-handoff <type> <name>` | Create handoff from template | `just scaffold` recipe |
| `/new-adr <number> <title>` | Create ADR from template | `just adr` recipe |
| `/new-report <name>` | Create report | `just scaffold report` recipe |
| `/new-work <backlog_id> <title>` | Create work item file | `just work` → work-creation-cycle skill |
| `/new-investigation <backlog_id> <title>` | Create investigation → investigation-cycle | `just inv` → skill chain |
| `/schema [table]` | Quick schema lookup | MCP schema_info tool |
| `/workspace` | Outstanding work status | Parses haios-status.json |
| `/close <backlog_id>` | Close work item with DoD validation | ADR-033 enforcement |
| `/critique <artifact>` | Invoke critique agent on artifact | critique-agent subagent |

## Scaffold Commands (Template-Based)

Session 36+ converted these commands from LLM generation to template-based scaffolding:
- `/new-plan`
- `/new-checkpoint`
- `/new-handoff`
- `/new-adr`
- `/new-report`
- `/new-work` (E2-150 - M6-WorkCycle)
- `/new-investigation`

**Why?** Template-based approach:
- No LLM cost per invocation
- Consistent file structure
- Faster execution (no API call)
- Aligns with "Doing right should be easy"

Templates are in `.claude/templates/`
Scaffolding via `just scaffold` recipe (Python-based, cross-platform)

## Command File Format

```yaml
---
allowed-tools: Bash, Write, Read
description: Short description shown in help
argument-hint: <arg1> <arg2>
---

# Command Title

Instructions for Claude to execute when command is invoked.
Use $ARGUMENTS to access command arguments.
```

## Adding New Commands

1. Create `.claude/commands/command-name.md`
2. Add YAML frontmatter with description
3. Add execution instructions
4. Optional: Create template in `.claude/templates/`
5. Optional: Add `just` recipe for the command

---
