# generated: 2026-01-20
# System Auto: last updated on: 2026-01-20T21:06:36
# Chapter: Work Loader

## Definition

**Chapter ID:** CH-006
**Arc:** configuration
**Status:** Planned
**Depends:** CH-003 (Loader Base)

---

## Problem

Agent invokes survey-cycle which runs `just queue`, parses output, presents options.

Current state:
```
1. Invoke survey-cycle skill
2. Skill runs just queue
3. Parse queue output
4. Check checkpoint pending
5. Present options via AskUserQuestion
```

Survey-cycle is a skill doing what a loader should do.

---

## Agent Need

> "What work is available? What was pending? What should I do?"

---

## Requirements

### R1: Work Extraction Config

```yaml
# config/loaders/work.yaml
sources:
  queue:
    method: command
    command: just queue default
    parse: work_items
    limit: 5

  pending:
    source: "{checkpoint.pending}"
    type: list

  epoch_alignment:
    method: check
    queue_items: "{queue}"
    current_epoch: "{epoch.current}"
```

### R2: Epoch Alignment Warning

If queue items don't match current epoch, warn:

```yaml
output:
  template: |
    === WORK OPTIONS ===

    {if epoch_alignment.misaligned}
    WARNING: Queue contains {epoch_alignment.legacy_count} items from prior epochs.
    Current epoch: {epoch.current}
    {endif}

    Queue (top 5):
    {queue}

    Pending from checkpoint:
    {pending}
```

### R3: Decision Ready

Output formatted for agent to make selection or ask operator.

### R4: Single Invocation

```bash
just work-options
# Outputs available work with context
```

---

## Interface

```bash
just work-options
# Outputs formatted work options
```

---

## Success Criteria

- [ ] Work options loaded via one command
- [ ] Epoch alignment checked
- [ ] Pending items included
- [ ] Coldstart Phase 3 uses this loader

---

## Non-Goals

- Work item details (agent reads WORK.md after selection)
- Automatic selection
- Queue manipulation
