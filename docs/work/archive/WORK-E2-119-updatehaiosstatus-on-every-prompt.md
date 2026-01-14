---
template: work_item
id: E2-119
title: UpdateHaiosStatus on Every Prompt
status: complete
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-26
milestone: M7d-Plumbing
priority: medium
effort: medium
category: implementation
spawned_by: Session 64 observation
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-23 19:06:12
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-23
last_updated: '2025-12-26T17:02:26'
---
# WORK-E2-119: UpdateHaiosStatus on Every Prompt

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** UpdateHaiosStatus currently runs on PostToolUse (file edits) or manually. This leaves pm.last_session, session_delta, and metrics stale between edits. Running on UserPromptSubmit ensures freshness on every interaction.
---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [x] Call `just update-status-slim` in UserPromptSubmit hook (before vitals)
- [x] Ensures pm.last_session, session_delta, and metrics are fresh on every interaction
- [x] Performance: Use slim update (not full) to minimize latency
- [x] Verify vitals reflect current state after each prompt

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

### 2025-12-26 - Completed (Session 124)
- Added `_refresh_slim_status()` function to user_prompt_submit.py
- Uses direct Python import for status module (faster than subprocess)
- Calls `generate_slim_status()` and `write_slim_status()` before reading vitals
- Fail-silent design: stale status better than broken hook

---

## References

- [Related documents]
