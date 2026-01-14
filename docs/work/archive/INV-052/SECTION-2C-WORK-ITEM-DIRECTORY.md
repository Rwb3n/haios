# generated: 2025-12-29
# System Auto: last updated on: 2025-12-29T23:26:30
# Section 2C: Work Item Directory Structure

Generated: 2025-12-29 (Session 149)
Purpose: Self-contained universe with portals

---

## Directory Structure

```
docs/work/active/E2-150/
├── WORK.md                    # State machine (node, phase, history)
│
├── investigations/            # Discovery artifacts (multiple)
│   ├── INV-001-initial.md
│   └── INV-002-deeper.md
│
├── plans/                     # Planning artifacts (multiple)
│   ├── PLAN-v1.md
│   └── PLAN-v2.md
│
├── observations/              # Captured during work
│   └── observations.md
│
├── references/                # Portals to other universes
│   ├── REFS.md
│   └── memory-refs.md
│
└── artifacts/                 # Implementation outputs
    └── test-results/
```

---

## Portals (Links to Other Universes)

```yaml
# references/REFS.md
---
type: portal-index
work_id: E2-150
---

# Related Work Items
- **Spawned from:** [[INV-045]]
- **Blocks:** [[E2-160]], [[E2-161]]
- **Related:** [[E2-148]]

# ADRs
- [[ADR-033]] - Work Item Lifecycle

# Memory Concepts
- [[concept:78234]] - Strategy for retrieval
```

---

## Portal Types

| Type | Points To | Purpose |
|------|-----------|---------|
| spawned_from | Parent work/investigation | Provenance |
| blocks | Downstream work items | Dependency |
| related | Sibling work items | Context |
| adr | Architecture decisions | Governance |
| memory | Memory concepts | Strategies |
| external | URLs, docs | Reference |

---

## Why Portals, Not Embedding

**Wrong:** Copy related content into work item
- Gets stale
- Duplicates information

**Right:** Link to canonical location
- Always current
- Single source of truth
- Discoverable via traversal
