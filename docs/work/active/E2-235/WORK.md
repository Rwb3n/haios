---
template: work_item
id: E2-235
title: Earlier Context Warning Thresholds
status: active
owner: Hephaestus
created: 2025-12-30
closed: null
milestone: M7b-WorkInfra
priority: high
effort: low
category: implementation
spawned_by: INV-052
spawned_by_investigation: INV-052
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-30 20:19:17
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-30
last_updated: '2025-12-30T20:19:54'
---
# WORK-E2-235: Earlier Context Warning Thresholds

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Current context warning threshold is 94%, which leaves insufficient runway (~6%) to complete checkpoint-cycle (SCAFFOLD + FILL + VERIFY + CAPTURE + COMMIT needs ~10% context).

**Root cause:** Threshold was set high to avoid premature warnings, but this backfires during complex sessions where context exhaustion happens abruptly.

**Source:** INV-052 Issue 3 (Context Warning Too Late)

---

## Current State

Work item created from INV-052 findings. Ready for implementation.

---

## Deliverables

- [ ] Update `.claude/hooks/hooks/user_prompt_submit.py` warning threshold from 94% to 85%
- [ ] Add escalating warnings: 85% (suggest checkpoint), 90% (MUST checkpoint), 94% (critical)
- [ ] Configure thresholds in `.claude/config/thresholds.yaml` for easy adjustment
- [ ] Test with sessions approaching context limit

---

## History

### 2025-12-30 - Created (Session 150)
- Initial creation

---

## References

- [Related documents]
