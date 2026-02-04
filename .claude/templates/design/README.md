# generated: 2026-02-04
# System Auto: last updated on: 2026-02-04T23:03:02
# Design Lifecycle Templates

Phase-specific templates for the design lifecycle (WORK-089).

## Phases

| Phase | File | Maps to State | Purpose |
|-------|------|---------------|---------|
| EXPLORE | EXPLORE.md | EXPLORE | Gather requirements and context |
| SPECIFY | SPECIFY.md | DESIGN | Write specification from requirements |
| CRITIQUE | CRITIQUE.md | CHECK | Validate assumptions, surface risks |
| COMPLETE | COMPLETE.md | DONE | Finalize spec, prepare for handoff |

## Structure

Each template follows the investigation template pattern:

```yaml
---
template: design_phase
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

Templates are loaded by skills during design lifecycle execution:

```python
from pathlib import Path

def get_design_template(phase: str) -> Path:
    return Path(f".claude/templates/design/{phase}.md")
```

## References

- REQ-TEMPLATE-002: Templates MUST be fractured by phase
- CH-006-TemplateFracturing: Chapter specification
- .claude/templates/investigation/: Reference pattern
