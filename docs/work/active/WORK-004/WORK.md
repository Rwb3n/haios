---
template: work_item
id: WORK-004
title: Update Coldstart to Read .claude/session
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
- .claude/commands/coldstart.md
acceptance_criteria:
- Coldstart reads session from .claude/session
- Coldstart does not parse haios-status.json for session number
blocked_by:
- WORK-003
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-21 11:07:01
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82189
- 82190
- 82191
- 82192
- 82193
extensions: {}
version: '2.0'
generated: 2026-01-21
last_updated: '2026-01-21T12:17:20'
---
# WORK-004: Update Coldstart to Read .claude/session

@docs/work/active/WORK-003/WORK.md
@.claude/haios/epochs/E2_3/arcs/configuration/CH-002-session-simplify.md

---

## Context

Once `just session-start` writes to `.claude/session` (WORK-003), coldstart should read from it.

Currently coldstart reads haios-status.json to get session number. After this work:
1. Read session from `.claude/session` (single `cat` or file read)
2. No JSON parsing needed

---

## Deliverables

- [x] Update coldstart command to read from `.claude/session`
- [x] Remove session number extraction from haios-status.json in coldstart
- [x] Test: `/coldstart` correctly identifies session number

---

## History

### 2026-01-21 - Created (Session 216)
- Triaged from CH-002 Session Simplify
- Blocked by WORK-003 (writer must work first)

---

## References

- WORK-003: Update just session-start (blocker)
- CH-002: Session Simplify
