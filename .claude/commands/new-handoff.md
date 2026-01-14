---
allowed-tools: Bash
description: Create a handoff document with proper template
argument-hint: <type> <name>
generated: '2026-01-05'
last_updated: '2026-01-05T21:09:53'
---

# Create Handoff

**MUST** use this command (not raw Write) when creating files in `docs/handoff/`.

Arguments: $ARGUMENTS

Types: investigation, task, bug, enhancement, evaluation

Run the scaffold recipe to create a new handoff from template:

```bash
just scaffold handoff_investigation <id> "<title>"
```

Where:
- `<id>` is a unique identifier (e.g., date-based like `2026-01-05-01`)
- `<title>` is the handoff title

Note: Currently only `handoff_investigation` template exists. Other types will use the same template until specific templates are created.

Report the created file path to the user.

---

## Allowed Field Values

| Field | Allowed Values |
|-------|----------------|
| status (handoff) | `draft`, `active`, `ready`, `completed`, `archived` |
| status (handoff_investigation) | `draft`, `active`, `pending`, `closed`, `completed`, `archived` |

Templates default to `status: active`. Use `completed` when work is done, `archived` for historical reference.
