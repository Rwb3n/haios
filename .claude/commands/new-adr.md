---
allowed-tools: Bash
description: Create a new Architecture Decision Record with template
argument-hint: <adr_number> <title>
---
# generated: 2025-12-09
# System Auto: last updated on: 2025-12-19 23:57:38
# Create Architecture Decision Record

**MUST** use this command (not raw Write) when creating files in `docs/ADR/`.

Arguments: $ARGUMENTS

Parse arguments as: `<adr_number> <title>`
- First argument is the ADR number (e.g., 033)
- Remaining arguments form the title

Run scaffolding via just recipe:

```bash
just adr <adr_number> "<title>"
```

Example:
```bash
just adr 039 "Workflow State Machine"
# Creates: docs/ADR/ADR-039-workflow-state-machine.md
```

Report the created file path to the user.

---

## Allowed Field Values

| Field | Allowed Values |
|-------|----------------|
| status | `proposed`, `accepted`, `rejected`, `superseded`, `deprecated` |

Templates default to `status: proposed`. Typical lifecycle: proposed → accepted. Use `superseded` when replaced by newer ADR.
