---
template: work_item
id: WORK-233
title: Add context_pct Field to Governance Events
type: implementation
status: complete
owner: Hephaestus
created: '2026-02-25'
closed: '2026-02-25'
priority: medium
effort: small
chapter: CH-059
arc: call
traces_to:
- REQ-CEREMONY-002
spawned_by: WORK-235
spawned_children: []
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: DONE
node_history:
- node: backlog
  entered: '2026-02-25T22:08:59.358266'
  exited: '2026-02-25T22:45:35.844369'
queue_history:
- position: backlog
  entered: '2026-02-25T22:08:59.358266'
  exited: '2026-02-25T22:37:53.453644'
- position: ready
  entered: '2026-02-25T22:37:53.453644'
  exited: '2026-02-25T22:43:10.309860'
- position: working
  entered: '2026-02-25T22:43:10.309860'
  exited: '2026-02-25T22:45:35.844369'
- position: done
  entered: '2026-02-25T22:45:35.844369'
  exited: null
memory_refs: []
requirement_refs: []
source_files:
- .claude/haios/lib/governance_events.py
- tests/test_governance_events.py
acceptance_criteria:
- All governance event log functions accept optional context_pct parameter
- _append_event includes context_pct field when provided (float, 0-100)
- Tests verify context_pct field appears in logged events when passed
- Existing events without context_pct still work (backward compatible)
artifacts: []
extensions: {}
version: '2.0'
generated: '2026-02-25'
last_updated: '2026-02-25T22:45:35.849774'
---
# WORK-233: Add context_pct Field to Governance Events

---

## Context

S458 observed ~60k tokens burned on close ceremony with no visibility into per-ceremony context consumption. Governance events log phase transitions, validation outcomes, and session boundaries but lack context budget information. Adding `context_pct` enables post-hoc analysis of which ceremonies consume the most context.

Implementation: Add optional `context_pct: Optional[float]` parameter to all `log_*` functions in `governance_events.py`. The `_append_event` helper includes it in the JSON when provided. Callers (hooks) can pass context percentage from `_estimate_context_usage()` in `user_prompt_submit.py`. Backward compatible — existing calls without context_pct still work.

---

## Deliverables

- [ ] `_append_event` accepts and includes optional `context_pct` field
- [ ] All `log_*` functions accept optional `context_pct` parameter and pass through
- [ ] Tests verify field presence when provided and absence when omitted

---

## References

- @.claude/haios/lib/governance_events.py (target file)
- @tests/test_governance_events.py (test file)
- @.claude/hooks/hooks/user_prompt_submit.py (context percentage source)
- @docs/work/active/WORK-235/WORK.md (parent investigation)
