# generated: 2026-02-05
# System Auto: last updated on: 2026-02-05T20:27:14
# Triage Phase Templates

Phase-specific templates for the triage lifecycle ([Items] -> [PrioritizedItems]).

## Templates

| Template | Phase | Maps to State | Purpose |
|----------|-------|---------------|---------|
| [SCAN.md](SCAN.md) | SCAN | EXPLORE | Collect and enumerate items |
| [ASSESS.md](ASSESS.md) | ASSESS | EXPLORE | Evaluate items against criteria |
| [RANK.md](RANK.md) | RANK | DESIGN | Order items by priority |
| [COMMIT.md](COMMIT.md) | COMMIT | DONE | Select items for action |

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

During triage lifecycle phases, read the corresponding template for guidance on:
- What must exist before starting (Input Contract)
- What activities are allowed/blocked (Governed Activities)
- What must be produced (Output Contract)

## Related

- `.claude/templates/investigation/` - Investigation lifecycle templates
- `.claude/templates/design/` - Design lifecycle templates
- `.claude/templates/implementation/` - Implementation lifecycle templates
- `.claude/templates/validation/` - Validation lifecycle templates
- WORK-092 - Created these templates

---

*Created: Session 316 (WORK-092)*
