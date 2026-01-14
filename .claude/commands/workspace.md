---
description: Show operational workspace status (outstanding items, stale work)
---
# generated: 2025-12-08
# System Auto: last updated on: 2025-12-08 21:04:22
# Workspace Status

Read `.claude/haios-status.json` and display the workspace section.

## Outstanding Work

Parse `workspace.outstanding` and display:

**Checkpoints with Pending Items:**
- List each checkpoint path with its pending items

**Handoffs Awaiting Pickup:**
- List each handoff with status and age

**Plans Approved but Not Started:**
- List each plan with age

## Stale Items (Needing Attention)

Parse `workspace.stale.items` and display:
- List items with type and age (>3 days for handoffs, >7 days for plans)

## Summary

Display counts from `workspace.summary`:
- Incomplete checkpoints: N
- Pending handoffs: N
- Approved not started: N
- Stale items: N

## Recommendations

Based on workspace state, suggest:
1. Oldest pending handoffs should be addressed first
2. Checkpoints with pending items need continuation
3. Approved plans without activity should be started or archived
