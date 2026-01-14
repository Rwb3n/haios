---
allowed-tools: Bash, Read, Edit
description: Create a session checkpoint manifest
argument-hint: <session_number> <title>
generated: '2025-12-25'
last_updated: '2026-01-10T12:25:14'
---

# Create Session Checkpoint

**MUST** use this command when creating checkpoint files.

Arguments: $ARGUMENTS

## Step 1: Scaffold

```bash
just scaffold checkpoint <session_number> "<title>"
```

This creates a minimal manifest file in `docs/checkpoints/`.

## Step 2: Populate the Manifest

The checkpoint is a **loading manifest**, not an activity log.

### Required Fields

1. **load_principles** - Files the next session MUST read
   - Default: S20, S22 (architectural principles)
   - Add any principles relevant to pending work

2. **load_memory_refs** - Concept IDs to query at coldstart
   - Add all concept IDs returned by `ingester_ingest` this session
   - These learnings will be injected into the next session's context

3. **pending** - Work for next session
   - List work item IDs or descriptions
   - These surface in survey

4. **drift_observed** - Principle violations noticed
   - If work this session violated S20/S22, note it here
   - Next session's coldstart surfaces these as warnings

5. **completed** - What was done (for git log only)
   - Brief list of completed work
   - Not loaded by coldstart - just for commit message

## Step 3: Commit

```bash
just commit-session <session_number> "<title>"
```

---

## Example Completed Manifest

```yaml
---
template: checkpoint
session: 186
prior_session: 185
date: 2026-01-10

load_principles:
  - .claude/haios/epochs/E2/architecture/S20-pressure-dynamics.md
  - .claude/haios/epochs/E2/architecture/S22-skill-patterns.md

load_memory_refs:
  - 81222
  - 81248
  - 81266

pending:
  - E2-281
  - E2-282

drift_observed:
  - "survey-cycle is 5 phases, S20 says single-phase"

completed:
  - E2-279
---
```

**The checkpoint is a manifest. The memory is the content. Git is the log.**
