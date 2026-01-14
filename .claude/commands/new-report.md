---
allowed-tools: Bash
description: Create new Report with template
argument-hint: <name>
---
# generated: 2025-12-07
# System Auto: last updated on: 2025-12-19 21:04:48

# Create Report

**MUST** use this command (not raw Write) when creating files in `docs/reports/`.

Arguments: $ARGUMENTS

Run scaffolding via just recipe (Session 86 fix - E2-105):

```bash
just scaffold report "" "<title>"
```

Example:
```bash
just scaffold report "" "Memory System Audit"
# Creates: docs/reports/2025-12-19-01-REPORT-memory-system-audit.md
```

Note: Reports don't have backlog IDs, so pass empty string as second argument.

Report the created file path to the user.

---

## Allowed Field Values

| Field | Allowed Values |
|-------|----------------|
| status | `draft`, `active`, `completed`, `archived`, `final` |

Templates default to `status: draft`. Use `final` for reports that should not be modified.
