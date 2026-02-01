# generated: 2026-02-01
# System Auto: last updated on: 2026-02-01T15:26:23
# Chapter: CH-001 InvestigationFracture

## Chapter Definition

**Chapter ID:** CH-001
**Arc:** templates
**Name:** InvestigationFracture
**Status:** Complete
**Work Item:** WORK-043

---

## Purpose

Split the monolithic investigation template (368 lines) into four phase-specific templates with explicit input/output contracts and governed activity references.

---

## Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Keep old investigation.md | Preserve for backward compatibility | Existing documents reference it; skills can migrate gradually without breaking |
| Use frontmatter with phase field | `phase: EXPLORE` etc. | Enables template routing by phase; machine-parseable |
| Reference activity_matrix.yaml | List activities from matrix, not hardcode | Single source of truth; templates stay in sync with governance |
| ~35 lines per template | Within 30-50 line budget | Sufficient for contracts + minimal structure; avoids Template Tax |
| Phase maps to state | EXPLORE→EXPLORE, HYPOTHESIZE→DESIGN, VALIDATE→CHECK, CONCLUDE→DONE | Matches activity_matrix.yaml phase_to_state mapping |
| 4-phase structure | EXPLORE, HYPOTHESIZE, VALIDATE, CONCLUDE | E2.4 target design (EXPLORE-FIRST); investigation-cycle update is WORK-037 |

---

## Artifacts Created

| Artifact | Path | Lines |
|----------|------|-------|
| EXPLORE.md | `.claude/templates/investigation/EXPLORE.md` | ~45 |
| HYPOTHESIZE.md | `.claude/templates/investigation/HYPOTHESIZE.md` | ~45 |
| VALIDATE.md | `.claude/templates/investigation/VALIDATE.md` | ~42 |
| CONCLUDE.md | `.claude/templates/investigation/CONCLUDE.md` | ~48 |

---

## Contract Pattern

Each phase template follows:

```markdown
# {PHASE} Phase

## Input Contract
- [ ] {What must exist before this phase}

## Governed Activities
*From activity_matrix.yaml for {STATE} state*
| Activity | Rule | Notes |

## Output Contract
- [ ] {What must exist after this phase}

## Template
{Minimal markdown structure}
```

---

## Integration Notes

- Templates are guidance documents, not scaffolded artifacts
- Skills read phase templates during their respective phases
- WORK-037 (Investigation Cycle Redesign) will update investigation-cycle skill to use these templates
- Old `investigation.md` preserved for backward compatibility

---

## Memory Refs

- Session 265 fractured templates decisions: 82724-82728
- Session 271 implementation: 82838

---

## References

- @.claude/haios/epochs/E2_4/arcs/templates/ARC.md
- @docs/work/active/WORK-043/WORK.md
- @docs/work/active/WORK-043/plans/PLAN.md
