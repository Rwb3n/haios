---
template: work_item
id: WORK-003
title: Update just session-start for .claude/session
type: implementation
status: complete
owner: Hephaestus
created: 2026-01-21
spawned_by: CH-002
chapter: CH-002
arc: configuration
closed: '2026-01-21'
priority: high
effort: small
requirement_refs:
- R3
source_files:
- .claude/haios/epochs/E2_3/arcs/configuration/CH-002-session-simplify.md
- justfile
acceptance_criteria:
- just session-start reads from .claude/session
- just session-start increments and writes to .claude/session
- 'Backward compat: session_delta in haios-status.json also updated'
blocked_by:
- WORK-002
blocks:
- WORK-004
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-21 11:06:58
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82180
- 82181
- 82182
- 82183
- 82184
- 82185
- 82186
- 82187
- 82188
extensions: {}
version: '2.0'
generated: 2026-01-21
last_updated: '2026-01-21T12:12:11'
---
# WORK-003: Update just session-start for .claude/session

@docs/work/active/WORK-002/WORK.md
@.claude/haios/epochs/E2_3/arcs/configuration/CH-002-session-simplify.md

---

## Context

Once `.claude/session` exists (WORK-002), the `just session-start` recipe needs to use it.

Currently session-start updates haios-status.json. After this work:
1. Read session from `.claude/session`
2. Increment
3. Write to `.claude/session`
4. Also update haios-status.json (backward compat during transition)

---

## Deliverables

- [x] Update `just session-start` to read from `.claude/session`
- [x] Update `just session-start` to write to `.claude/session`
- [x] Maintain backward compat: also update session_delta in haios-status.json
- [x] Test: `just session-start` increments session correctly

---

## History

### 2026-01-21 - Created (Session 216)
- Triaged from CH-002 Session Simplify
- Blocked by WORK-002 (file must exist first)

---

## References

- WORK-002: Create .claude/session File (blocker)
- CH-002: Session Simplify
