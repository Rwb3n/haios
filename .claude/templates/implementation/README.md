# generated: 2026-02-04
# System Auto: last updated on: 2026-02-04T23:57:51
# Implementation Lifecycle Templates

Phase-specific templates for the implementation lifecycle (WORK-090).

## Phases

| Phase | File | Maps to State | Purpose |
|-------|------|---------------|---------|
| PLAN | PLAN.md | PLAN | Verify plan exists and is ready |
| DO | DO.md | DO | Implement design from plan |
| CHECK | CHECK.md | CHECK | Verify implementation quality |
| DONE | DONE.md | DONE | Complete and prepare for closure |

## Structure

Each template follows the investigation/design template pattern:

```yaml
---
template: implementation_phase
phase: {PHASE}
maps_to_state: {STATE}
version: '1.0'
input_contract: [...]
output_contract: [...]
---
# {PHASE} Phase

## Input Contract
## Governed Activities
## Output Contract
## Template
```

## Usage

Templates are loaded by skills during implementation lifecycle execution:

```python
from pathlib import Path

def get_implementation_template(phase: str) -> Path:
    return Path(f".claude/templates/implementation/{phase}.md")
```

## References

- REQ-TEMPLATE-002: Templates MUST be fractured by phase
- CH-006-TemplateFracturing: Chapter specification
- .claude/templates/investigation/: Reference pattern
- .claude/templates/design/: Reference pattern
