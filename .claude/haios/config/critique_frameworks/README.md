# generated: 2026-01-25
# System Auto: last updated on: 2026-01-25T01:28:32
# Critique Frameworks

Portable YAML configurations for the critique-agent.

## Available Frameworks

| Framework | Purpose |
|-----------|---------|
| **assumption_surfacing** | Surface implicit assumptions in designs before implementation |

## Framework Structure

Each framework YAML must contain:

```yaml
name: framework_name
version: "1.0"
description: "What this framework does"

categories:
  - id: category_id
    label: "Human-readable label"
    prompt: "Question to ask during critique"

verdict_rules:
  BLOCK: "Condition that blocks proceeding"
  REVISE: "Condition that suggests revision"
  PROCEED: "Condition that allows proceeding"
```

## Adding New Frameworks

1. Create `{framework_name}.yaml` in this directory
2. Follow the structure above
3. Update haios.yaml `agents.critique.framework` to use new framework
4. Tests in `tests/test_critique_agent.py` validate framework loading

## Usage

The critique-agent loads framework from config:
1. Reads `haios.yaml` for `agents.critique.framework` setting
2. Loads `{framework}.yaml` from this directory
3. Applies categories to plan content
4. Returns verdict per verdict_rules

## Extensibility

Future frameworks could include:
- `pre_mortem.yaml` - Imagine failure, work backward
- `red_team.yaml` - Adversarial analysis
- `security_review.yaml` - Security-focused critique

## Related

- **critique-agent**: `.claude/agents/critique-agent.md`
- **plan-validation-cycle**: Invokes critique in CRITIQUE phase
- **E2-072**: Implementation work item
