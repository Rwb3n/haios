# generated: 2025-12-23
# System Auto: last updated on: 2025-12-30T21:01:48
# Create Work Item

**MUST** use this command when creating files in `docs/work/`.

Arguments: `<backlog_id> <title>`

## Create Work Item

Run scaffolding via just recipe:

```bash
just work <backlog_id> "<title>"
```

Example:
```bash
just work E2-160 "New Feature Implementation"
# Creates: docs/work/active/WORK-E2-160-new-feature-implementation.md
```

Report the created file path to the user.

---

## Chain to Work Creation Cycle

After scaffolding, **MUST** immediately invoke the work-creation-cycle skill:

```
Skill(skill="work-creation-cycle")
```

This chains the creation into the structured VERIFY → POPULATE → READY workflow.
The skill will:
1. Verify work item has required fields populated
2. Guide filling in Context and Deliverables sections
3. Ensure work item is ready for planning or implementation

---

## Allowed Field Values

| Field | Allowed Values |
|-------|----------------|
| status | `active`, `blocked`, `complete`, `archived` |
| current_node | `backlog`, `discovery`, `plan`, `implement`, `close` |
| priority | `high`, `medium`, `low` |

---

## Work File Directory Structure

Work files are stored in directories matching their status:

```
docs/work/
├── active/      # status: active (work in progress)
├── blocked/     # status: blocked (waiting on dependencies)
└── archive/     # status: complete | archived
```

When status changes, move the file to the appropriate directory.
