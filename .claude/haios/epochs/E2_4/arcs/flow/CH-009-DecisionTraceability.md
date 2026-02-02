# generated: 2026-02-02
# System Auto: last updated on: 2026-02-02T08:58:52
# Chapter: DecisionTraceability

## Definition

**Chapter ID:** CH-009
**Arc:** flow
**Status:** Active
**implements_decisions:** [D8]
**Depends:** None

---

## Problem

How do we ensure epoch decisions trace to implementing chapters? Currently:
- Decisions in EPOCH.md are prose with no structured traceability
- Chapters can be created without claiming any decisions
- No validation exists to catch orphan decisions or orphan claims

**Design Question:** What schema and ceremony ensures bidirectional traceability?

---

## Solution: Decision Traceability Schema

### EPOCH.md Decision Schema

Add `assigned_to` field to each decision:

```markdown
### Decision N: Title

assigned_to:
  - arc: {arc_name}
    chapters: [{chapter_ids}]

[existing prose description]
```

**Field Semantics:**
- `assigned_to`: List of arc/chapter mappings (optional - absence triggers warning)
- `arc`: Arc ID (must match directory name in `arcs/`)
- `chapters`: List of chapter IDs that implement this decision

### Chapter File Schema

Add `implements_decisions` field to chapter Definition section:

```markdown
## Definition

**Chapter ID:** CH-XXX
**Arc:** {arc_name}
**Status:** {status}
**implements_decisions:** [D1, D3, D8]
**Depends:** {dependencies}
```

**Field Semantics:**
- `implements_decisions`: List of decision IDs this chapter implements
- Format: `D{N}` where N is the decision number from EPOCH.md

---

## Ceremony: Decision Assignment

### When to Assign

During **arc decomposition** (creating chapters from arc theme):
1. Review all epoch decisions relevant to the arc
2. For each decision, identify which chapter(s) will implement it
3. Add `assigned_to` to EPOCH.md decision
4. Add `implements_decisions` to chapter file

### How to Verify

Run the audit command:
```bash
just audit-decision-coverage
```

This validates:
1. All decisions have `assigned_to` (warns if missing)
2. All chapters have `implements_decisions` (warns if missing)
3. Bidirectional consistency (errors on orphan claims)

### When Gaps Found

| Gap Type | Action |
|----------|--------|
| Decision without assigned_to | Assign to appropriate chapter(s) or mark as "deferred" |
| Chapter without implements_decisions | Add field referencing implemented decisions |
| Chapter claims non-existent decision | Remove invalid reference |
| Decision assigned to non-existent chapter | Create chapter or reassign |

---

## Validation Rules

| Rule | Severity | Message |
|------|----------|---------|
| Decision missing assigned_to | Warning | "D{N} has no assigned_to field" |
| Chapter missing implements_decisions | Warning | "{CH-XXX} missing implements_decisions field" |
| Chapter claims invalid decision | Error | "{path} claims {D} which doesn't exist" |
| Orphan decision (assigned but not claimed) | Warning | "D{N} assigned to {path} but not claimed" |

**Design Choice:** Warnings not errors for missing fields enables gradual adoption without blocking existing work.

---

## Integration Points

| Component | Integration |
|-----------|-------------|
| `/audit` skill | Calls `just audit-decision-coverage` |
| `justfile` | Recipe `audit-decision-coverage` runs Python script |
| `.claude/haios/lib/audit_decision_coverage.py` | Validation logic |

---

## Exit Criteria

- [x] Schema documented (this file)
- [x] EPOCH.md Decision 8 has assigned_to example
- [x] Validation script implemented
- [x] Tests pass (7 tests)
- [ ] Integrated into audit workflow

---

## Memory Refs

Session 283: 83112-83114 (schema design learnings)
Session 279: 83018-83029 (multi-level governance investigation)

---

## References

- @.claude/haios/epochs/E2_4/EPOCH.md (Decision 8)
- @.claude/haios/epochs/E2_4/arcs/flow/ARC.md (parent arc)
- @docs/work/active/WORK-055/WORK.md (source investigation)
- @docs/work/active/WORK-069/WORK.md (this implementation)
