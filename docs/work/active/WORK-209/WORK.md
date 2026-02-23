---
template: work_item
id: WORK-209
title: Enforce Session and Process Review Computable Predicates via Hooks
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-23
spawned_by: WORK-102
spawned_children: [WORK-210, WORK-211, WORK-212]
chapter: CH-059
arc: call
closed: '2026-02-23'
priority: high
effort: medium
traces_to:
- REQ-CEREMONY-005
- REQ-FEEDBACK-006
- REQ-FEEDBACK-007
requirement_refs: []
source_files:
- .claude/haios/lib/session_review_predicate.py (new)
- .claude/hooks/hooks/stop.py
- .claude/hooks/hooks/pre_tool_use.py
- tests/test_session_review_predicate.py (new)
- tests/test_pre_tool_use_process_review.py (new)
- .claude/haios/lib/README.md
acceptance_criteria:
- Session Review trigger predicate extracted to lib/ function (computable, testable)
- Stop hook or session-end flow injects 'MUST run session-review-cycle' when predicate
  passes
- PreToolUse hook blocks Write to manifesto/L3/ and manifesto/L4/ paths without preceding
  ProcessReviewApproved governance event
- Tests for predicate function and hook enforcement
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: DO
node_history:
- node: backlog
  entered: 2026-02-23 18:07:51
  exited: '2026-02-23T19:02:41.644339'
artifacts: []
cycle_docs: {}
memory_refs:
- 778
- 779
- 780
- 781
extensions: {}
version: '2.0'
generated: 2026-02-23
last_updated: '2026-02-23T19:02:41.648524'
queue_history:
- position: ready
  entered: '2026-02-23T18:21:13.113009'
  exited: '2026-02-23T18:21:13.145759'
- position: working
  entered: '2026-02-23T18:21:13.145759'
  exited: '2026-02-23T19:02:41.644339'
- position: done
  entered: '2026-02-23T19:02:41.644339'
  exited: null
---
# WORK-209: Enforce Session and Process Review Computable Predicates via Hooks

---

## Context

WORK-102 (S435) designed Session Review and Process Review ceremonies as SKILL.md files (Tier 3: agent reads markdown). The ceremonies contain computable predicates and enforcement gates that are currently agent-judged:

1. **Session Review trigger:** Agent checks session-log.jsonl for closed work items / retro count. Agent can skip or misjudge.
2. **Session Review ASSESS exclusion rule:** "Don't restate retro findings" — pure agent judgment, no enforcement.
3. **Process Review APPROVE gate:** "Log governance event before Write to L3/L4" — agent can forget the event.
4. **Process Review scope-conditional query depth:** Agent chooses what to query — can under-query.

**The pattern:** Computable predicates belong in `lib/` functions (testable). Enforcement belongs in hooks (Tier 1/2). Skills describe the ceremony contract but don't enforce it.

**Operator concern (S435):** These "computable" decisions left to agent judgment will be easily skipped, especially after context compaction. Moving enforceable parts from SKILL.md to hooks/lib is the CH-059 CeremonyAutomation mandate.

**Three enforcement tiers:**

| What | From (Tier 3) | To (Tier 1/2) | Mechanism |
|------|---------------|----------------|-----------|
| Session Review trigger predicate | Agent reads SKILL.md | `lib/session_review_predicate.py` | Python function, testable |
| Session Review invocation reminder | Agent remembers | Stop/PostToolUse hook injection | Hook injects into context at session-end |
| L3/L4 Write protection | Agent logs event voluntarily | PreToolUse hook on Write | Block Write to manifesto paths without ProcessReviewApproved event |

---

## Deliverables

- [ ] `lib/session_review_predicate.py`: Extract trigger predicate (check session-log.jsonl for WorkClosed/RetroCycleCompleted events)
- [ ] Hook injection: At session-end, if predicate passes, inject "MUST run session-review-cycle" into agent context
- [ ] PreToolUse hook: Block Write to `manifesto/L3/` and `manifesto/L4/` paths unless ProcessReviewApproved event exists in governance-events.jsonl for current session
- [ ] Tests for predicate function
- [ ] Tests for hook enforcement (Write block)

---

## History

### 2026-02-23 - Created (Session 435)
- Operator flagged concern that computable predicates in SKILL.md are unenforceable
- Spawned from WORK-102 retro discussion

---

## References

- @docs/work/active/WORK-102/WORK.md (parent — ceremony design)
- @.claude/skills/session-review-cycle/SKILL.md (trigger predicate to extract)
- @.claude/skills/process-review-cycle/SKILL.md (APPROVE gate to enforce)
- @.claude/hooks/hooks/post_tool_use.py (hook target)
- CH-059 CeremonyAutomation (chapter mandate: mechanical phases to hooks)
