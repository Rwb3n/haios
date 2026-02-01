# generated: 2026-02-01
# System Auto: last updated on: 2026-02-01T15:26:36
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
