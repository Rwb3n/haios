# generated: 2025-12-29
# System Auto: last updated on: 2026-02-15T21:05:00
# HAIOS Agents

Subagents for isolated, focused operations within the HAIOS governance framework.

## Capability Card Schema (WORK-144, REQ-DISCOVER-004)

Each agent `.md` file includes structured capability card fields in YAML frontmatter:

| Field | Type | Description |
|-------|------|-------------|
| `requirement_level` | enum | `required`, `recommended`, `optional` |
| `category` | enum | `gate`, `verification`, `utility`, `cycle-delegation` |
| `trigger_conditions` | list | When to invoke this agent |
| `input_contract` | string | What the agent expects from its parent |
| `output_contract` | string | What the agent returns to its parent |
| `invoked_by` | list | Which skills/cycles invoke this agent |
| `related_agents` | list | Cross-references to related agents |

## Available Agents (11)

| Agent | Requirement | Category | Purpose |
|-------|-------------|----------|---------|
| **anti-pattern-checker** | recommended | verification | Verify claims against 6 L1 anti-patterns before acceptance |
| **close-work-cycle-agent** | optional | cycle-delegation | Execute full close-work-cycle in isolated context |
| **critique-agent** | recommended | verification | Pre-implementation assumption surfacing |
| **implementation-cycle-agent** | optional | cycle-delegation | Execute full implementation-cycle in isolated context |
| **investigation-agent** | required | utility | EXPLORE phase evidence gathering for investigations |
| **investigation-cycle-agent** | optional | cycle-delegation | Execute full investigation-cycle in isolated context |
| **preflight-checker** | required | gate | Plan readiness + >3 file gate |
| **schema-verifier** | required | gate | Isolated schema queries (blocks direct SQL) |
| **test-runner** | optional | utility | Isolated test execution |
| **validation-agent** | recommended | verification | Unbiased CHECK phase validation |
| **why-capturer** | recommended | utility | Automated learning extraction |

## Invocation Pattern

```python
Task(subagent_type='<agent-name>', prompt='<task description>')
```

## Agent Categories

### Required Gates
- **preflight-checker**: MUST invoke before DO phase in implementation-cycle
- **schema-verifier**: MUST use for any database schema queries

### Cycle Delegation Agents (WORK-081)

Context-reducing agents that execute full cycles in isolated context, returning structured summaries.

| Agent | Cycle | Phases | Use Case |
|-------|-------|--------|----------|
| **implementation-cycle-agent** | implementation-cycle | PLAN→DO→CHECK→DONE→CHAIN | Work items with approved plans |
| **investigation-cycle-agent** | investigation-cycle | EXPLORE→HYPOTHESIZE→VALIDATE→CONCLUDE→CHAIN | Research/discovery work |
| **close-work-cycle-agent** | close-work-cycle | VALIDATE→ARCHIVE→MEMORY→CHAIN | Work item closure |

**Invocation Example:**
```python
Task(
    subagent_type='implementation-cycle-agent',
    prompt='''Execute implementation cycle for WORK-081.
Plan: docs/work/active/WORK-081/plans/PLAN.md
Work: docs/work/active/WORK-081/WORK.md'''
)
```

**Benefits:**
- 70-90% context reduction for main track
- Fresh context per cycle (no inherited bloat)
- Structured output for consistent parsing
- Patterns port to SDK custom tools (Epoch 4)

### Verification Agents
- **anti-pattern-checker**: Verify claims against L1 anti-patterns
- **critique-agent**: Pre-implementation assumption surfacing
- **validation-agent**: Unbiased CHECK phase validation

### Utility Agents
- **investigation-agent**: Evidence gathering during investigations
- **test-runner**: Isolated pytest execution
- **why-capturer**: Extract learnings for memory storage

## Related

- **Skills:** `.claude/skills/` - Workflow definitions that may invoke agents
- **Commands:** `.claude/commands/` - User-invocable slash commands
- **Hooks:** `.claude/hooks/` - Event-driven governance enforcement
