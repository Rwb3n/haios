---
template: work_item
id: E2-210
title: Context Threshold Auto-Checkpoint
status: complete
owner: Hephaestus
created: 2025-12-27
closed: 2025-12-27
milestone: M7b-WorkInfra
priority: medium
effort: medium
category: implementation
spawned_by: INV-041
spawned_by_investigation: INV-041
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-27 14:35:31
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-27
last_updated: '2025-12-27T20:41:59'
---
# WORK-E2-210: Context Threshold Auto-Checkpoint

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** HAIOS has no auto-checkpoint mechanism. Agent relies on human to say "checkpoint" before context exhaustion. Memory has strategies about proactive checkpointing at thresholds, but no implementation exists.

**Root Cause:** Only 4 hooks exist (user_prompt_submit, pre_tool_use, post_tool_use, stop). No context % monitoring. E2-025 (PreCompact) was investigated but closed WONTFIX because operator uses clear not compact.

**Evidence:** Grep for "context.*remaining" found no implementation. Memory 68696: "proactive checkpointing at 9% context threshold"

**Discovery (Session 130):** Hook payloads do NOT include context percentage or token usage. No Claude Code API exists to query remaining context budget from hooks. Must use **transcript-based estimation** approach instead:
- Parse `transcript_path` file (JSONL format)
- Estimate tokens from message/tool content
- Rough formula: tokens ~ chars / 4, threshold against 200k window

---

## Current State

Work item in BACKLOG node. Awaiting prioritization and investigation of feasibility.

---

## Deliverables

- [x] Investigate if Claude Code provides context % in hook payloads (Session 130: NO - not available)
- [ ] Implement transcript-based context estimation function in `.claude/lib/`
- [ ] Add context check to `user_prompt_submit.py` hook
- [ ] Return warning message when estimated context > 80% threshold
- [ ] Test with real transcript files to calibrate estimation accuracy

---

## History

### 2025-12-27 - Created (Session 127)
- Initial creation

### 2025-12-27 - Discovery (Session 130)
- Investigated Claude Code hook payloads via claude-code-guide agent
- Finding: Hook payloads do NOT include context % or token usage
- No API exists to query remaining context budget from hooks
- Revised approach: Transcript-based estimation (parse transcript_path JSONL)
- Updated deliverables to reflect transcript-based approach

---

## References

- [Related documents]
