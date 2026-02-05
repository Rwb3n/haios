# generated: 2026-02-05
# System Auto: last updated on: 2026-02-05T20:26:23
# Validation Phase Templates

Phase-specific templates for the validation lifecycle (Artifact x Spec -> Verdict).

## Templates

| Template | Phase | Maps to State | Purpose |
|----------|-------|---------------|---------|
| [VERIFY.md](VERIFY.md) | VERIFY | CHECK | Gather evidence, run tests, inspect artifacts |
| [JUDGE.md](JUDGE.md) | JUDGE | CHECK | Evaluate evidence against criteria |
| [REPORT.md](REPORT.md) | REPORT | CHECK | Document findings and verdict |

## Contract Pattern

Each template follows:

```
# {PHASE} Phase

## Input Contract     <- Prerequisites
## Governed Activities <- From activity_matrix.yaml
## Output Contract    <- Required outputs
## Template           <- Minimal structure
```

## Machine-Readable Contracts (WORK-088)

Templates include machine-readable contracts in YAML frontmatter:

```yaml
input_contract:
  - field: <field_name>
    type: <type>
    required: <bool>
    description: <string>

output_contract:
  - field: <field_name>
    type: <type>
    required: <bool>
    description: <string>
```

## Usage

During validation lifecycle phases, read the corresponding template for guidance on:
- What must exist before starting (Input Contract)
- What activities are allowed/blocked (Governed Activities)
- What must be produced (Output Contract)

## Related

- `.claude/templates/investigation/` - Investigation lifecycle templates
- `.claude/templates/design/` - Design lifecycle templates
- `.claude/templates/implementation/` - Implementation lifecycle templates
- WORK-091 - Created these templates

---

*Created: Session 316 (WORK-091)*
