---
template: work_item
id: E2-171
title: Cascade Event Consumer
status: wontfix
owner: Hephaestus
created: 2025-12-24
closed: 2025-12-27
milestone: M7d-Plumbing
priority: low
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-24 20:12:21
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-24
last_updated: '2025-12-27T12:04:18'
---
# WORK-E2-171: Cascade Event Consumer

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** PostToolUse hook (`_detect_cascade` at `.claude/hooks/hooks/post_tool_use.py:455-525`) logs `cascade_trigger` events to `haios-events.jsonl` when work items complete, but nothing consumes these events to actually propagate cascades.

**Root Cause:** Comment says "justfile cascade command handles this" but the event log is never read - gap between event emission and consumption.

**Discovery:** Session 114 during E2-090 recipe audit.

---

## Current State

Work item in BACKLOG node. Low priority - cascade propagation works manually via `just cascade`.

---

## Deliverables

- [ ] Consumer mechanism that reads `cascade_trigger` events from `haios-events.jsonl`
- [ ] Auto-invoke `just cascade <id> <status>` for each pending trigger
- [ ] OR: Remove event logging if manual cascade is sufficient (simplify)

**Options:**
1. **Heartbeat integration:** Add cascade consumption to hourly heartbeat
2. **Hook integration:** Call `just cascade` directly in PostToolUse instead of logging
3. **Delete:** Remove cascade event logging as dead code

---

## History

### 2025-12-24 - Created (Session 114)
- Spawned from E2-090 cascade hook audit finding
- PostToolUse logs events but nothing reads them

---

## References

- E2-090: Recipe consolidation (source of finding)
- E2-076e: Original cascade hooks implementation
- `.claude/hooks/hooks/post_tool_use.py:455-525`
