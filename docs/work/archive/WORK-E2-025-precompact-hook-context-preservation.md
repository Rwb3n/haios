---
template: work_item
id: E2-025
title: PreCompact Hook - Context Preservation
status: wontfix
owner: Hephaestus
created: 2025-12-23
closed: 2025-12-27
milestone: M7d-Plumbing
priority: medium
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: discovery
node_history:
- node: backlog
  entered: 2025-12-23 19:06:12
  exited: 2025-12-27 13:43:00
- node: discovery
  entered: 2025-12-27 13:43:00
  exited: null
cycle_docs:
  investigations:
  - docs/investigations/INVESTIGATION-E2-025-precompact-hook-context-preservation.md
memory_refs:
- 64752
- 64753
- 64754
- 64755
- 64756
- 64757
- 64758
- 64759
- 64760
- 64761
- 64762
- 64763
- 64764
- 64765
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-23
last_updated: '2025-12-27T14:09:45'
---
# WORK-E2-025: PreCompact Hook - Context Preservation

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Compact is a black box. Happens, context shrinks, continuity breaks. Operator has to re-explain.
---

## Current State

**WONTFIX** - Operator workflow uses `clear + coldstart` instead of compact. PreCompact hook is irrelevant to actual usage patterns. Investigation confirmed technical feasibility but feature serves no purpose.

---

## Deliverables

- [ ] Create PreCompact hook handler in `.claude/hooks/hooks/`
- [ ] Extract key learnings to memory before context lost
- [ ] Auto-create mini-checkpoint with session decisions
- [ ] Store "session did X, Y, Z" summary to memory
- [ ] Flag in-progress work for post-compact pickup
- [ ] Investigate: can we influence what compact preserves?

---

## History

### 2025-12-23 - Created (Session 105)
- Initial creation

### 2025-12-27 - Investigation Complete (Session 126)
- Completed INVESTIGATION-E2-025: All 3 hypotheses confirmed
- PreCompact hooks can only perform side effects (cannot block compact)
- Payload includes session_id, transcript_path, trigger - sufficient for context extraction
- Design: subprocess delegation pattern following stop.py, <10s timeout, memory ingestion
- Ready to proceed with implementation

---

## References

- INVESTIGATION-E2-025-precompact-hook-context-preservation.md
- Claude Code Hooks Docs: code.claude.com/docs/en/hooks
- Memory: 79707-79715 (investigation findings)
