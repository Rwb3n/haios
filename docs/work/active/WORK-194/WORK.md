---
template: work_item
id: WORK-194
title: UserPromptSubmit Hook Injection Candidates Evaluation
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-22
spawned_by: WORK-189
spawned_children:
- WORK-195
- WORK-196
chapter: CH-059
arc: call
closed: '2026-02-22'
priority: medium
effort: small
traces_to:
- REQ-OBSERVE-002
requirement_refs: []
source_files:
- .claude/hooks/hooks/user_prompt_submit.py
acceptance_criteria:
- 'Each candidate injection evaluated for: token cost, data source, implementation
  effort, value to agent'
- 'Clear recommendation per candidate: implement now, defer, or reject'
- Spawns implementation work items for approved candidates
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-22 15:41:56
  exited: '2026-02-22T16:30:39.931518'
artifacts: []
cycle_docs: {}
memory_refs:
- 87537
- 87538
- 87539
- 87580
- 87581
- 87582
- 87583
extensions:
  epoch: E2.8
version: '2.0'
generated: 2026-02-22
last_updated: '2026-02-22T16:30:39.934607'
queue_history:
- position: ready
  entered: '2026-02-22T16:21:00.113969'
  exited: '2026-02-22T16:21:11.025131'
- position: working
  entered: '2026-02-22T16:21:11.025131'
  exited: '2026-02-22T16:30:39.931518'
- position: done
  entered: '2026-02-22T16:30:39.931518'
  exited: null
---
# WORK-194: UserPromptSubmit Hook Injection Candidates Evaluation

---

## Context

WORK-189 added context window usage injection (`[CONTEXT: N% used]`). S423 operator discussion identified 4 additional candidates for UserPromptSubmit hook injection. Each needs effort evaluation before implementation — the hook fires on every prompt so token cost compounds.

Design constraint: each injection should be <20 tokens to keep per-prompt overhead minimal.

### Candidates

1. **Session number** — inject `[SESSION: 423]`. Data source: `.claude/session` file (already read by other hooks). Saves a Read tool call on every coldstart. Estimated: trivial effort.

2. **Working item** — inject `[WORKING: WORK-189]` when a cycle is active. Data source: `haios-status-slim.json` (already parsed by session state warning). Useful after compaction when phase contract context is lost. Estimated: trivial effort.

3. **Time-in-session** — inject `[DURATION: 61m]`. Data source: needs session start timestamp (governance-events.jsonl or `.claude/session`). Operator time awareness per L1.6 (limited time). Estimated: small effort (needs timestamp parsing).

4. **Pending count** — inject `[READY: 3 items]`. Data source: would need WorkEngine or `work_queues.yaml` parsing. Ambient backlog pressure awareness. Estimated: medium effort (WorkEngine import in hook context).

### Evaluation Criteria

For each candidate:
- Token cost per prompt (must be <20 tokens)
- Data source availability (already parsed vs new file read)
- Implementation effort (trivial/small/medium)
- Value to agent decision-making (high/medium/low)
- Risk of noise (does it add signal or clutter?)

---

## Deliverables

- [x] Evaluation table for all 4 candidates
- [x] Recommendation per candidate (implement/defer/reject)
- [x] Spawned implementation work items for approved candidates (WORK-195, WORK-196)

---

## History

### 2026-02-22 - Completed (Session 425)

**Evaluation Table:**

| Candidate | Injection | Tokens | Data Source | Effort | Value | Recommendation |
|-----------|-----------|--------|-------------|--------|-------|----------------|
| 1. Session number | `[SESSION: 425]` | ~5 | `.claude/session` (50 bytes) | Trivial | High | **Implement** |
| 2. Working item | `[WORKING: WORK-194]` | ~5 | slim JSON `session_state.work_id` (already parsed) | Trivial | High | **Implement** |
| 3. Time-in-session | `[DURATION: 61m]` | ~5 | `.claude/session` mtime (stat() syscall) | Small | Medium | **Implement** |
| 4. Pending count | `[READY: 6 items]` | ~5 | WorkEngine (heavy import, all WORK.md) | Medium-High | Low | **Defer** |

**Key findings:**
- Candidates 1+3 share a single Path object (read content + stat mtime)
- Candidate 2 piggybacks on existing slim JSON parse (already read by `_get_session_state_warning`)
- Candidate 4 deferred: WorkEngine imports GovernanceLayer, parses all active WORK.md — too heavy for per-prompt
- Bonus finding: slim JSON read 4x per handle() call — spawned WORK-195 prerequisite refactor

**Spawned:**
- WORK-195: Slim-read-once refactor (prerequisite)
- WORK-196: Hook injection batch — session, working, duration (blocked by WORK-195)

### 2026-02-22 - Created (Session 423)
- Operator-Hephaestus discussion during WORK-189 closure CHAIN phase
- Follows successful WORK-189 (context window injection) — exploring what else to inject

---

## References

- @docs/work/active/WORK-189/WORK.md (parent: context window injection)
- @docs/work/active/WORK-195/WORK.md (spawned: slim refactor)
- @docs/work/active/WORK-196/WORK.md (spawned: injection batch)
- Memory: 87537-87539 (context budget calibration data from S423)
