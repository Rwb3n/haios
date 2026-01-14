# generated: 2026-01-12
# System Auto: last updated on: 2026-01-12T01:21:37
# S26: Skill-Recipe Binding

**Status:** Active
**Source:** Session 188

---

## Pattern

Each skill declares 0-3 recipes in frontmatter:

```yaml
---
name: close-work-cycle
recipes:
  - close-work
  - update-status
---
```

---

## Bindings

| Skill | Recipes | Notes |
|-------|---------|-------|
| `plan-authoring-cycle` | `plan` | Scaffolds plan |
| `work-creation-cycle` | `work` | Scaffolds work item |
| `investigation-cycle` | `inv` | Scaffolds investigation |
| `close-work-cycle` | `close-work`, `update-status` | Closes + refreshes |
| `checkpoint-cycle` | `checkpoint`, `commit-session`, `session-end` | Checkpoint + commit |
| `observation-capture-cycle` | `scaffold-observations` | Scaffolds observations.md |
| `survey-cycle` | `ready` | Queries unblocked items |
| `audit` | `audit-gaps`, `audit-stale`, `audit-sync` | Audit recipes |
| `ground-cycle` | (none) | Pure context loading |
| `dod-validation-cycle` | `validate` | Validates files |
| `routing-gate` | (none) | Pure routing logic |

---

## Why

- Layer 0 (recipes) = mechanical execution
- Layer 3 (skills) = cognitive guidance
- Binding makes explicit which recipes a skill uses
- Agent doesn't have to guess from 65+ recipes

---

## References

- S12: Invocation Paradigm (layer definitions)
