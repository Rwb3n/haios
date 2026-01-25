# generated: 2025-12-29
# System Auto: last updated on: 2026-01-25T01:28:17
# HAIOS Agents

Subagents for isolated, focused operations within the HAIOS governance framework.

## Available Agents (8)

| Agent | Requirement | Purpose |
|-------|-------------|---------|
| **anti-pattern-checker** | SHOULD/MUST | Verify claims against 6 L1 anti-patterns before acceptance |
| **critique-agent** | Optional | Pre-implementation assumption surfacing (E2-072) |
| **investigation-agent** | Optional | EXPLORE phase evidence gathering for investigations |
| **preflight-checker** | REQUIRED | Plan readiness + >3 file gate (E2-186) |
| **schema-verifier** | REQUIRED | Isolated schema queries (blocks direct SQL) |
| **test-runner** | Optional | Isolated test execution |
| **validation-agent** | Optional | Unbiased CHECK phase validation |
| **why-capturer** | Optional | Automated learning extraction |

## Invocation Pattern

```python
Task(subagent_type='<agent-name>', prompt='<task description>')
```

## Agent Categories

### Required Gates
- **preflight-checker**: MUST invoke before DO phase in implementation-cycle
- **schema-verifier**: MUST use for any database schema queries

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
