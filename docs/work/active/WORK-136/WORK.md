---
template: work_item
id: WORK-136
title: Checkpoint Pending Item Staleness Detection
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-12
spawned_by: null
chapter: CH-051
arc: infrastructure
closed: '2026-02-16'
priority: low
effort: small
traces_to:
- REQ-CEREMONY-001
requirement_refs: []
source_files:
- .claude/skills/checkpoint-cycle/SKILL.md
acceptance_criteria:
- Stale pending items are detectable at session start
- Mechanism to mark pending items resolved without full close cycle
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-12 20:53:11
  exited: '2026-02-16T21:23:12.312569'
artifacts: []
cycle_docs: {}
memory_refs:
- 85704
- 85705
- 85706
- 85707
extensions: {}
version: '2.0'
generated: 2026-02-12
last_updated: '2026-02-16T21:23:12.315227'
queue_history:
- position: ready
  entered: '2026-02-16T21:15:53.829516'
  exited: '2026-02-16T21:15:53.859064'
- position: working
  entered: '2026-02-16T21:15:53.859064'
  exited: '2026-02-16T21:23:12.312569'
- position: done
  entered: '2026-02-16T21:23:12.312569'
  exited: null
spawned_children:
- WORK-156
---
# WORK-136: Checkpoint Pending Item Staleness Detection

---

## Context

Session 355 survey-cycle loaded checkpoint pending items from S353. One item (`test_skill_is_minimal` bug) was already resolved but still appeared as pending. The agent spent time investigating before confirming it was stale.

**Problem:** Checkpoint pending items persist across sessions without validation. No mechanism exists to:
1. Mark a pending item as resolved without a full close cycle
2. Detect at session start that a pending item references something already fixed
3. Age-out items that have been pending for N sessions

**Question:** How should stale pending items be detected and handled?

---

## Deliverables

- [x] Investigation findings on staleness detection approach
- [x] Recommendation: manual vs automated resolution

---

## History

### 2026-02-12 - Created (Session 355)
- Discovered when `test_skill_is_minimal` bug appeared in pending but was already resolved

### 2026-02-16 - Investigation Complete (Session 387)
- **Finding:** 58% of pending items contain WORK-IDs (auto-resolvable), 42% are free-text
- **Recommendation:** Automated — WORK-ID items auto-resolved via WorkEngine status; free-text items get age markers
- **Integration point:** SessionLoader.extract() annotates at extraction time
- **Co-located bug:** WorkLoader._get_pending_from_checkpoint() has lexicographic sort bug
- **Spawned:** WORK-156 for implementation
- **Verdict:** PROCEED (no blocking unknowns)

---

## References

- `docs/checkpoints/2026-02-12-01-SESSION-353-ch016-memory-ceremonies.md` — source checkpoint
- `.claude/skills/checkpoint-cycle/SKILL.md` — checkpoint creation skill
- Memory: 84986 (stale waste), 84983 (staleness), 85621 (scope), 85704-85707 (findings)
