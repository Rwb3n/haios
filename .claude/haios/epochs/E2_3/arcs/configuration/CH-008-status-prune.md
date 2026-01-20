# generated: 2026-01-20
# System Auto: last updated on: 2026-01-20T21:07:15
# Chapter: Status Prune

## Definition

**Chapter ID:** CH-008
**Arc:** configuration
**Status:** Planned

---

## Problem

haios-status.json is 258KB. Most of it is never used.

Current state:
```
Section             Size      Consumers
-------             ----      ---------
live_files          102KB     None
outstanding_items   22KB      None
stale_items         18KB      None
alignment           14KB      None
milestones          4KB       cascade_engine, user_prompt_submit
templates           4KB       None
spawn_map           1KB       None
(useful stuff)      ~5KB      Various hooks
```

156KB of bloat with no runtime consumers.

---

## Agent Need

> "Status should be fast to read and contain only what's needed."

---

## Requirements

### R1: Remove Unused Sections

Delete from `generate_full_status()`:
- `live_files`
- `outstanding_items`
- `stale_items`
- `alignment`

### R2: Keep Used Sections

Preserve:
- `generated`
- `milestone`
- `session_delta`
- `work_cycle`
- `session_state`
- `active_work`
- `blocked_items`
- `counts`
- `infrastructure`
- `milestones` (used by cascade)
- `workspace` (used by user_prompt_submit)

### R3: Size Target

haios-status.json < 10KB after pruning.

### R4: Deprecate Slim

After prune, full status IS slim. Delete haios-status-slim.json.

One file. One source of truth.

---

## Interface

```bash
just update-status
# Generates pruned haios-status.json
```

---

## Success Criteria

- [ ] haios-status.json < 10KB
- [ ] haios-status-slim.json deleted
- [ ] All current consumers still work
- [ ] `just update-status` faster (less computation)

---

## Migration

1. Audit consumers (done in Session 215)
2. Remove sections from generate_full_status()
3. Update write_full_status()
4. Delete generate_slim_status(), write_slim_status()
5. Delete haios-status-slim.json
6. Update consumers that referenced slim to use full
7. Run tests

---

## Non-Goals

- Restructuring status format
- Adding new status sections
- Real-time status updates
