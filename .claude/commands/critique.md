---
allowed-tools: Read, Glob, Task
description: Invoke critique agent on an artifact to surface implicit assumptions
argument-hint: <artifact_path>
generated: 2026-01-25
last_updated: '2026-01-25T01:49:59'
---
# Critique Command

Manually invoke the critique agent on any artifact to surface implicit assumptions.

## Usage

```
/critique <artifact_path>
```

## Examples

```
/critique docs/work/active/E2-072/plans/PLAN.md
/critique docs/adr/ADR-045-new-architecture.md
/critique docs/investigations/INV-058.md
```

## Process

1. Parse artifact path from `$ARGUMENTS`
2. Verify artifact exists using Glob
3. Invoke critique-agent subagent:
   ```
   Task(subagent_type='critique-agent', prompt='Critique artifact: {artifact_path}')
   ```
4. Agent loads framework from `haios.yaml` `agents.critique.frameworks_dir`
5. Agent produces:
   - Critique report (human-readable)
   - Assumptions YAML (machine-parseable)
6. Report verdict and findings summary

## Verdicts

| Verdict | Meaning |
|---------|---------|
| **PROCEED** | All assumptions mitigated or high confidence |
| **REVISE** | Risks identified, consider plan revision |
| **BLOCK** | Unmitigated low-confidence assumptions, needs work |

## Output Location

When critiquing a plan file at `docs/work/active/{id}/plans/PLAN.md`:
- Report: `docs/work/active/{id}/critique/critique-report.md`
- YAML: `docs/work/active/{id}/critique/assumptions.yaml`

For other artifacts, output is displayed inline.

## Related

- **critique-agent:** `.claude/agents/critique-agent.md`
- **plan-validation-cycle:** Integrates critique as CRITIQUE phase
- **assumption_surfacing.yaml:** Default framework in `.claude/haios/config/critique_frameworks/`
