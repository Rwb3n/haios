# generated: 2025-09-23
# System Auto: last updated on: 2026-01-28T22:44:39
# Code Implementation & Engineering Guide

## RFC 2119 Keywords

This document uses RFC 2119 keywords to indicate requirement levels:

| Keyword | Meaning |
|---------|---------|
| **MUST** / **REQUIRED** | Absolute requirement - violation breaks the system |
| **MUST NOT** / **SHALL NOT** | Absolute prohibition - violation breaks the system |
| **SHOULD** / **RECOMMENDED** | Strong recommendation - valid reasons may exist to ignore |
| **SHOULD NOT** | Strong discouragement - valid reasons may exist to do otherwise |
| **MAY** / **OPTIONAL** | Truly optional - implement at discretion |

---

## CRITICAL: Platform Awareness

### Current Environment
- **OS:** Windows
- **Shell:** Python (all hooks migrated from PowerShell as of E2-120)
- **Terminal:** Claude Code CLI

### Tool Preference Hierarchy (Search/Query)
When searching files or content, agents **SHOULD** prefer dedicated tools over shell commands:

| Priority | Tool | Use Case |
|----------|------|----------|
| 1 | **Grep** | Content search - no escaping issues |
| 2 | **Glob** | File pattern matching |
| 3 | **Read** | Reading specific files |
| 4 | **Python scripts** | Complex logic (`.claude/lib/`) |
| 5 | **Inline shell** | Last resort |

---

## CRITICAL: Module-First Principle (Session 218 - MUST)

**Commands and skills MUST call modules, not instruct agents to read files manually.**

```
Commands/Skills (prose) → cli.py / just recipes → modules/*.py → lib/*.py
```

We have **11 modules** in `.claude/haios/modules/`. They MUST be used.

| Module | Purpose |
|--------|---------|
| `ContextLoader` | L0-L4 loading, session bootstrap |
| `WorkEngine` | WORK.md CRUD, lifecycle |
| `GovernanceLayer` | Gates, transitions |
| `MemoryBridge` | MCP wrapper |
| `CycleRunner` | Phase execution |
| + 6 more | See modules/README.md |

**Design Gate:** Every chapter/arc/skill design MUST answer:
> "Which module does the work? If none, why not?"

If answer is "agent reads files manually" → design is WRONG.

---

## CRITICAL: Work Item ID Policy (WORK-030)

**All new work items MUST use WORK-XXX format.**

| Rule | Description |
|------|-------------|
| **Format** | `WORK-###` (e.g., WORK-031, WORK-032) |
| **Auto-increment** | Use `get_next_work_id()` from `.claude/haios/lib/scaffold.py` |
| **Type field** | Behavior determined by `type:` field, not ID prefix |

### Type Values

| Type | Cycle | Description |
|------|-------|-------------|
| `investigation` | investigation-cycle | Discovery/research work |
| `implementation` | implementation-cycle | Code/feature work |
| `cleanup` | implementation-cycle | Tech debt/refactoring |

### Deprecated ID Formats

| Format | Status | Migration |
|--------|--------|-----------|
| `E2-XXX` | Legacy (Epoch 2) | Existing items remain, new items use WORK-XXX |
| `INV-XXX` | Deprecated | Use WORK-XXX with `type: investigation` |
| `TD-XXX` | Deprecated | Use WORK-XXX with `type: cleanup` |

**The `type` field determines routing, not the ID prefix.**

---

## Identity & Role

### Who I Am
I am **Claude (Executor)**, the **Orchestrator** of the HAIOS project. I work with **Ruben (Operator)** to define strategy and **Antigravity (Implementer)** to execute technical tasks.

### Project Context
- **Description:** HAIOS (Hybrid AI Operating System) is a **Trust Engine** for AI agents.
- **Current Epoch:** Epoch 2 - Governance Suite (hooks, commands, templates, memory integration)
- **Reference:** See `docs/epistemic_state.md` for detailed phase status.

### Key Reference Locations

#### Database Schema
- **Schema:** `docs/specs/memory_db_schema_v3.sql` - THE authoritative source
- **Manager:** `.claude/lib/database.py` - All database operations

Direct SQL queries are BLOCKED. Agents **MUST** use the schema-verifier subagent:
```
Task(prompt='<your query intent>', subagent_type='schema-verifier')
```

#### Project Structure
- **Plugin Code:** `.claude/lib/` - ALL Python code (database, retrieval, synthesis, status, scaffold, validate)
- **Tests:** `tests/` - All test files following pytest conventions
- **Specifications:** `docs/specs/` - TRDs and schemas
- **Checkpoints:** `docs/checkpoints/` - Session summaries
- **DEPRECATED:** `haios_etl/` - See `haios_etl/DEPRECATED.md` for migration guide

---

## Memory Refs Rule (MUST - Session 178)

**When reading ANY document with `memory_refs` in frontmatter, MUST query those IDs:**

```sql
SELECT id, type, content FROM concepts WHERE id IN ({memory_refs})
```

This applies to:
- Work items (WORK.md) - load prior context for the work
- Checkpoints - load prior session's learnings
- Plans - load design decisions
- Investigations - load findings

**Rationale:** memory_refs exist specifically for direct ID lookup. NOT semantic search. The IDs point to exact concepts stored during that work. Ignoring them loses context.

---

## Governance Quick Reference

### Hooks (`.claude/hooks/`) - ALL PYTHON
| Hook | Handler | Purpose |
|------|---------|---------|
| **PreToolUse** | `hooks/pre_tool_use.py` | Governance enforcement (SQL, PowerShell, paths) |
| **PostToolUse** | `hooks/post_tool_use.py` | YAML timestamps, cascade triggers |
| **UserPromptSubmit** | `hooks/user_prompt_submit.py` | Date/time, vitals injection |
| **Stop** | `hooks/stop.py` | ReasoningBank extraction |

Note: All hooks routed via `hook_dispatcher.py`. PowerShell archived to `hooks/archive/`.

### PreToolUse Governance Checks
| Check | Toggle | Bypass |
|-------|--------|--------|
| SQL blocking | Hardcoded | Use `schema-verifier` subagent |
| PowerShell blocking | `.claude/haios/config/haios.yaml` (toggles.block_powershell) | Set `block_powershell: false` |
| Path governance | Hardcoded | Use `/new-*` commands |

### Routing Thresholds (E2-222)
System health thresholds configured in `.claude/haios/config/haios.yaml` (thresholds section):
- `observation_pending.max_count`: Trigger triage if pending observations > value (default: 10)
- `observation_pending.escape_priorities`: Skip threshold for these priorities (default: [critical])

### Commands (`.claude/commands/`)
| Command | Purpose |
|---------|---------|
| `/coldstart` | Initialize session |
| `/new-checkpoint` | Create session checkpoint |
| `/new-plan` | Create implementation plan → chains to implementation-cycle |
| `/new-investigation` | Create investigation → chains to investigation-cycle |
| `/new-work` | Create work item → chains to work-creation-cycle |
| `/new-adr` | Create Architecture Decision Record |
| `/close` | Close work item → chains to close-work-cycle |
| `/validate` | Validate file against templates |
| `/implement` | Start implementation cycle for existing plan |

### Governance Triggers (MUST)
| Trigger | Action |
|---------|--------|
| Discover bug/gap/issue | **MUST** use `/new-investigation` |
| Any SQL query | **MUST** use `schema-verifier` subagent |
| Close work item | **MUST** use `/close <id>` |
| Create governed document | **MUST** use `/new-*` command |
| Create work item | **MUST** have chapter file first (REQ-TRACE-004) |

### Traceability Chain (MUST - REQ-TRACE-005)
```
L4 Requirement → Epoch → Arc → Chapter → Work Item
```
**No chapter file → work item BLOCKED.** Every work item MUST trace up this chain. No orphan work.

### Memory Tools
| Tool | Purpose |
|------|---------|
| `ingester_ingest` | **PRIMARY** - Ingest with auto-classification |
| `memory_search_with_experience` | Query with strategy injection |

### Skills (`.claude/skills/`) - M8-SkillArch Complete
| Skill | Type | Purpose |
|-------|------|---------|
| `ground-cycle` | Cycle | PROVENANCE→ARCHITECTURE→MEMORY→CONTEXT MAP for context loading |
| `implementation-cycle` | Cycle | PLAN→DO→CHECK→DONE with MUST gates |
| `investigation-cycle` | Cycle | HYPOTHESIZE→EXPLORE→CONCLUDE |
| `work-creation-cycle` | Cycle | VERIFY→POPULATE→READY with placeholder validation |
| `close-work-cycle` | Cycle | VALIDATE→OBSERVE→ARCHIVE→MEMORY |
| `observation-triage-cycle` | Cycle | SCAN→TRIAGE→PROMOTE for archived observations |
| `plan-validation-cycle` | Bridge | Pre-DO plan quality gate |
| `design-review-validation` | Bridge | During-DO design alignment |
| `dod-validation-cycle` | Bridge | Post-DO DoD criteria check |
| `memory-agent` | Utility | Strategy retrieval before complex tasks |
| `audit` | Utility | Find gaps, drift, stale items |

### Agents (`.claude/agents/`)
| Agent | Requirement | Purpose |
|-------|-------------|---------|
| `preflight-checker` | **REQUIRED** | Plan readiness + >3 file gate (E2-186) |
| `validation-agent` | Optional | Unbiased CHECK phase validation |
| `investigation-agent` | Optional | EXPLORE phase evidence gathering |
| `schema-verifier` | **REQUIRED** | Isolated schema queries |
| `test-runner` | Optional | Isolated test execution |
| `why-capturer` | Optional | Automated learning extraction |

---

## Important Reminders

### Governance Compliance
1. **MUST** use slash commands for governed documents (checkpoints, plans, handoffs, reports)
2. PreToolUse hook will prompt when attempting raw Write to governed paths
3. **SHOULD** check memory before complex tasks - strategies from past sessions may help
4. **SHOULD** store learnings after completing significant work

### Database Safety
1. **MUST** read schema first: `docs/specs/memory_db_schema_v3.sql`
2. **MUST NOT** assume column names - verify with schema-verifier subagent
3. **MUST** use `.claude/lib/database.py` methods - **MUST NOT** modify haios_memory.db directly

### Session Hygiene
1. **SHOULD** run `/coldstart` at session start
2. **SHOULD** create checkpoint before compact
3. **SHOULD** store key learnings to memory

### Work Item Completion (ADR-033, E2-250)

| Criterion | How to Verify |
|-----------|---------------|
| **Tests pass** | Run `pytest` - all green |
| **Runtime consumer exists** | `Grep` for imports outside tests - must have callers |
| **WHY captured** | Store reasoning via `ingester_ingest` |
| **Docs current** | CLAUDE.md, READMEs updated if behavior changed |

> **E2-250 Learning:** "Tests pass" ≠ "Code is used". Modules without runtime consumers are prototypes.

### Work Item Location (ADR-041)

**MUST NOT** move work items from `docs/work/active/` to `archive/` on completion.

| Principle | Rule |
|-----------|------|
| **Status over location** | `status: complete` marks closure, not directory path |
| **References stay valid** | Portals, memory_refs, @ links all point to paths |
| **Epoch-level cleanup** | Archive move happens at epoch boundary, not work item close |

**Rationale:** Moving files breaks portal links, memory references, and embedded @ references. The close-work-cycle "ARCHIVE" phase means "mark complete", not "move to archive directory".

---
*Last Updated: 2026-01-15 | Version: Epoch 2.2 (The Refinement)*
*See `docs/epistemic_state.md` for detailed status*
