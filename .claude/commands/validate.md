---
allowed-tools: Bash
description: Validate a markdown file against HAIOS templates (TRD, ADR, Checkpoint,
  etc.)
argument-hint:
- file_path
generated: '2026-01-05'
last_updated: '2026-01-05T21:09:38'
---

# Validate Template

**SHOULD** run before committing governed documents to verify template compliance.

Ref: `just validate` recipe (justfile line 16-17)

## Logic
1. If NO arguments are provided:
   - Ask user for target file path.
2. If Argument is provided:
   - Run: `just validate <file_path>`

## Output
- Present the stdout from the script (Status, Errors, Warnings) clearly to the user.
- If errors exist, suggest immediate fixes.
