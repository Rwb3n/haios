---
template: work_item
id: E2-294
title: Wire Session Event Logging into Lifecycle
type: implementation
status: active
owner: Hephaestus
created: 2026-01-26
spawned_by: E2-236
chapter: null
arc: configuration
milestone: M7b-WorkInfra
closed: null
priority: high
effort: small
traces_to:
- REQ-CONTEXT-001
requirement_refs: []
source_files:
- .claude/haios/lib/governance_events.py
- justfile
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-26 20:38:50
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82466
extensions: {}
version: '2.0'
generated: 2026-01-26
last_updated: '2026-01-26T20:39:30'
---
# E2-294: Wire Session Event Logging into Lifecycle

@docs/README.md
@docs/work/active/E2-236/WORK.md

---

## Context

**Problem:** E2-236 implemented `log_session_start()` and `log_session_end()` functions in governance_events.py, but they are not wired into the actual session lifecycle. Without this wiring, `detect_orphan_session()` will never find orphans because no `SessionStarted` events exist.

**Root cause:** Deferred during E2-236 to keep scope contained. The detection infrastructure exists but isn't triggered.

**Source:** E2-236 plan Step 5 and checkpoint pending items

---

## Deliverables

- [ ] Modify `just session-start` to call `log_session_start(session_number, agent)`
- [ ] Modify `just session-end` to call `log_session_end(session_number, agent)`
- [ ] Verify events appear in `.claude/haios/governance-events.jsonl`
- [ ] Test: run coldstart after session with events, verify no false orphan detection

---

## History

### 2026-01-26 - Created (Session 245)
- Spawned from E2-236 as follow-up work
- High priority: completes orphan detection feature

---

## References

- @docs/work/active/E2-236/WORK.md (parent work)
- @docs/work/active/E2-236/plans/PLAN.md (Step 5: Wire Session Logging)
- @.claude/haios/lib/governance_events.py (functions exist at lines 96, 117)
