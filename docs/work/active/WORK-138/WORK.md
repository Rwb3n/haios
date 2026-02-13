---
template: work_item
id: WORK-138
title: Fix Scaffold Checkpoint CLI Arg Parsing
type: bugfix
status: complete
owner: Hephaestus
created: 2026-02-12
spawned_by: null
spawned_children: []
chapter: null
arc: null
closed: '2026-02-13'
priority: medium
effort: small
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/lib/scaffold.py
- .claude/haios/modules/cli.py
acceptance_criteria:
- just scaffold checkpoint --session 358 --title 'test' produces correct filename
- 'Positional args also work: just scaffold checkpoint 358 test-title'
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-12 22:40:28
  exited: '2026-02-13T08:38:44.927637'
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-02-12
last_updated: '2026-02-13T08:38:44.930713'
queue_history:
- position: done
  entered: '2026-02-13T08:38:44.927637'
  exited: null
---
# WORK-138: Fix Scaffold Checkpoint CLI Arg Parsing

---

## Context

`just scaffold checkpoint --session 358 --title "work-100-..."` produces mangled filename: `SESSION---session-358-title-work-100-...`. The `--session` and `--title` flags are treated as literal strings in the filename rather than parsed as named CLI arguments. Discovered during S358 checkpoint creation.

---

## Deliverables

- [ ] Fix CLI arg parsing for `scaffold checkpoint` to handle `--session` and `--title` flags
- [ ] Verify `just scaffold checkpoint --session 358 --title "test"` produces correct filename
- [ ] Add test for checkpoint scaffold filename generation

---

## History

### 2026-02-12 - Created (Session 358)
- Discovered during S358 checkpoint creation
- Had to manually rename the file

---

## References

- @.claude/haios/lib/scaffold.py
- @.claude/haios/modules/cli.py
