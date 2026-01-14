---
template: readme
status: active
date: 2025-12-23
component: work
version: '1.0'
generated: 2025-12-23
last_updated: '2025-12-27T22:13:42'
---
# Work Item Files

Work items as individual files - single source of truth for status (M6-WorkCycle, ADR-039).

@docs/pm/backlog.md
@docs/ADR/ADR-039-work-item-as-file-architecture.md

## Directory Structure (E2-212)

Each work item is a directory containing its artifacts:

```
docs/work/
├── active/                   # Active work items
│   ├── E2-160/              # Work item directory
│   │   ├── WORK.md          # Main work file
│   │   ├── plans/           # Implementation plans
│   │   │   └── PLAN.md
│   │   ├── investigations/  # Related investigations
│   │   │   └── 001-*.md
│   │   └── reports/         # Bug reports, bandaids
│   └── INV-043/
│       ├── WORK.md
│       └── investigations/
├── blocked/                  # Blocked items (same structure)
└── archive/                  # Completed items (legacy flat + directory)
```

## Creating Work Items

Use `/new-work` command:

```bash
just work E2-160 "New Feature Implementation"
# Creates: docs/work/active/E2-160/
#          docs/work/active/E2-160/WORK.md
#          docs/work/active/E2-160/plans/
#          docs/work/active/E2-160/investigations/
#          docs/work/active/E2-160/reports/
```

When creating plans/investigations for existing work items:

```bash
just plan E2-160 "Implementation Plan"
# Creates: docs/work/active/E2-160/plans/PLAN.md

just inv INV-043 "Landscape Analysis"
# Creates: docs/work/active/INV-043/investigations/001-landscape-analysis.md
```

## Work File Schema (INV-022 v2)

Key fields:

| Field | Purpose |
|-------|---------|
| `id` | Backlog ID (E2-xxx, INV-xxx) |
| `status` | active, blocked, complete, archived |
| `current_node` | DAG position (backlog, plan, implement, etc.) |
| `node_history` | Audit trail of progression |
| `cycle_docs` | Links to plan, tests, verification |

## Status Transitions

1. File created in `active/` with status: active
2. If blocked, move to `blocked/` and update status: blocked
3. When complete, move to `archive/` and update status: complete

Directory location = status (prevents drift).

---

**Created:** Session 106 (2025-12-23)
**Updated:** Session 132 (2025-12-27) - E2-212 directory structure migration
**Related:** E2-150, E2-212, INV-022, INV-024, INV-043, ADR-039
