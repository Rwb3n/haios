---
template: work_item
id: WORK-194
title: "UserPromptSubmit Hook Injection Candidates Evaluation"
type: investigation
status: active
owner: Hephaestus
created: 2026-02-22
spawned_by: WORK-189
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: small
traces_to:
- REQ-OBSERVE-002
requirement_refs: []
source_files:
- .claude/hooks/hooks/user_prompt_submit.py
acceptance_criteria:
- "Each candidate injection evaluated for: token cost, data source, implementation effort, value to agent"
- "Clear recommendation per candidate: implement now, defer, or reject"
- "Spawns implementation work items for approved candidates"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-22T15:41:56
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 87537
- 87538
- 87539
extensions:
  epoch: E2.8
version: "2.0"
generated: 2026-02-22
last_updated: 2026-02-22T15:41:56
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

- [ ] Evaluation table for all 4 candidates
- [ ] Recommendation per candidate (implement/defer/reject)
- [ ] Spawned implementation work items for approved candidates

---

## History

### 2026-02-22 - Created (Session 423)
- Operator-Hephaestus discussion during WORK-189 closure CHAIN phase
- Follows successful WORK-189 (context window injection) — exploring what else to inject

---

## References

- @docs/work/active/WORK-189/WORK.md (parent: context window injection)
- Memory: 87537-87539 (context budget calibration data from S423)
