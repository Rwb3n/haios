# generated: 2025-12-29
# System Auto: last updated on: 2026-02-24T10:45:00
# HAIOS Agents

Agent definitions live in this directory as `.md` files with structured YAML frontmatter.

See **[AGENTS.md](../../AGENTS.md)** in the project root for the full agent registry
(auto-generated from frontmatter, vendor-neutral discovery layer).

## Capability Card Schema (WORK-144 + WORK-164)

Each agent `.md` file includes structured capability card fields in YAML frontmatter:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Agent identifier (used in `Task(subagent_type=...)`) |
| `description` | string | One-line purpose |
| `tools` | string/list | Available tools |
| `model` | enum | `haiku`, `sonnet`, `opus` |
| `id` | string | Unique identifier (same as name) |
| `role` | string | Semantic role: `gate`, `verifier`, `utility`, `cycle-delegate` |
| `capabilities` | list | What this agent can do |
| `requirement_level` | enum | `required`, `recommended`, `optional` |
| `category` | enum | `gate`, `verification`, `utility`, `cycle-delegation` |
| `trigger_conditions` | list | When to invoke this agent |
| `input_contract` | string | What the agent expects from its parent |
| `output_contract` | string | What the agent returns to its parent |
| `produces` | list | Artifact types this agent creates |
| `consumes` | list | Artifact types this agent reads |
| `invoked_by` | list | Which skills/cycles invoke this agent |
| `related_agents` | list | Cross-references to related agents |

## Invocation Pattern

```python
Task(subagent_type='<agent-name>', prompt='<task description>')
```

## Programmatic Access

```python
from agent_cards import list_agents, get_agent, filter_agents

# List all agents
agents = list_agents()

# Get specific agent
critique = get_agent("critique-agent")

# Filter by category
gates = filter_agents(category="gate")
```

Module: `.claude/haios/lib/agent_cards.py`

## Agent Index

| Agent | Role | Required |
|-------|------|----------|
| `anti-pattern-checker` | verifier | no |
| `close-work-cycle-agent` | cycle-delegate | no |
| `critique-agent` | gate | no |
| `design-review-validation-agent` | verifier | no |
| `implementation-cycle-agent` | cycle-delegate | no |
| `investigation-agent` | utility | no |
| `investigation-cycle-agent` | cycle-delegate | no |
| `plan-authoring-agent` | cycle-delegate | no |
| `preflight-checker` | gate | yes |
| `retro-enrichment-agent` | utility | no |
| `schema-verifier` | gate | yes |
| `test-runner` | utility | no |
| `validation-agent` | verifier | no |
| `why-capturer` | utility | no |

## Related

- **AGENTS.md** (project root) - Auto-generated registry
- **Skills:** `.claude/skills/` - Workflow definitions that may invoke agents
- **Commands:** `.claude/commands/` - User-invocable slash commands
- **Hooks:** `.claude/hooks/` - Event-driven governance enforcement
