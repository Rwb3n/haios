# generated: 2025-12-23
# System Auto: last updated on: 2026-01-28T22:43:42
# Create Work Item

**MUST** use this command when creating files in `docs/work/`.

Arguments: `<title>` or `<backlog_id> <title>`

## ID Policy (WORK-030)

All new work items use **WORK-XXX** format (auto-incremented).

- If only title provided: auto-assign next WORK-XXX ID
- If ID provided: use that ID (for backwards compatibility)
- The `type` field determines behavior, not the ID prefix

## Create Work Item

**Option 1: Auto-assign ID (recommended)**
```bash
# Get next ID
python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from scaffold import get_next_work_id; print(get_next_work_id())"
# Then scaffold with that ID
just work WORK-031 "New Feature Implementation"
```

**Option 2: Explicit ID (backwards compatible)**
```bash
just work WORK-031 "<title>"
```

Example:
```bash
just work WORK-031 "New Feature Implementation"
# Creates: docs/work/active/WORK-031/WORK.md
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
