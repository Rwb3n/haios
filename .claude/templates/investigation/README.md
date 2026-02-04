# generated: 2026-02-01
# System Auto: last updated on: 2026-02-04T22:31:43
# Investigation Phase Templates

Phase-specific templates for the investigation cycle (E2.4 EXPLORE-FIRST design).

## Templates

| Template | Phase | Maps to State | Purpose |
|----------|-------|---------------|---------|
| [EXPLORE.md](EXPLORE.md) | EXPLORE | EXPLORE | Evidence gathering before hypothesis |
| [HYPOTHESIZE.md](HYPOTHESIZE.md) | HYPOTHESIZE | DESIGN | Form hypotheses from evidence |
| [VALIDATE.md](VALIDATE.md) | VALIDATE | CHECK | Test hypotheses against evidence |
| [CONCLUDE.md](CONCLUDE.md) | CONCLUDE | DONE | Synthesize, spawn work, store memory |

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

As of v1.1, templates include machine-readable contracts in YAML frontmatter:

```yaml
input_contract:
  - field: <field_name>     # Field to check
    type: <type>            # markdown | table | list | string | boolean
    required: <bool>        # true = must exist
    description: <string>   # Human-readable explanation

output_contract:
  - field: <field_name>
    type: <type>
    required: <bool>
    description: <string>
```

CycleRunner validates these contracts on phase entry/exit via:
- `validate_phase_input(phase, work_id)` - checks input_contract
- `validate_phase_output(phase, work_id)` - checks output_contract

MVP uses soft validation (warn but allow). Hard gates in CH-007.

## Usage

During investigation-cycle phases, read the corresponding template for guidance on:
- What must exist before starting (Input Contract)
- What activities are allowed/blocked (Governed Activities)
- What must be produced (Output Contract)

## Related

- `.claude/templates/investigation.md` - Monolithic template (preserved for backward compat)
- `.claude/haios/config/activity_matrix.yaml` - Governance source
- WORK-037 - Investigation cycle redesign to use these templates

---

*Created: Session 271 (WORK-043)*
