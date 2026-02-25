---
template: work_item
id: WORK-231
title: 'Coldstart Token Waste: Remove Agent-Read of config.yaml'
type: implementation
status: complete
owner: Hephaestus
created: '2026-02-25'
closed: '2026-02-25'
priority: medium
effort: small
chapter: CH-061
arc: call
traces_to:
- REQ-CONFIG-001
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
  entered: '2026-02-25T22:08:56.964859'
  exited: '2026-02-25T22:49:47.768512'
queue_history:
- position: backlog
  entered: '2026-02-25T22:08:56.964859'
  exited: '2026-02-25T22:48:29.251604'
- position: ready
  entered: '2026-02-25T22:48:29.251604'
  exited: '2026-02-25T22:48:32.989739'
- position: working
  entered: '2026-02-25T22:48:32.989739'
  exited: '2026-02-25T22:49:47.768512'
- position: done
  entered: '2026-02-25T22:49:47.768512'
  exited: null
memory_refs: []
requirement_refs: []
source_files:
- .claude/commands/coldstart.md
acceptance_criteria:
- Step 1 (Read config.yaml) removed from coldstart.md — orchestrator handles config
  internally
- Coldstart still functions correctly after removal (manual verification next session)
artifacts: []
extensions: {}
version: '2.0'
generated: '2026-02-25'
last_updated: '2026-02-25T22:49:47.772154'
---
# WORK-231: Coldstart Token Waste: Remove Agent-Read of config.yaml

---

## Context

The coldstart command Step 1 instructs the agent to Read `.claude/haios/config/haios.yaml` and extract epoch paths. But Step 2 runs `coldstart_orchestrator()` which internally loads the same config via `_load_config()`. The agent Read is redundant — it wastes tokens reading a 146-line YAML file that the orchestrator already parses.

Fix: Remove Step 1 from coldstart.md. The orchestrator output already contains epoch context, active arcs, and all operational paths.

---

## Deliverables

- [ ] Step 1 removed from coldstart.md
- [ ] Step numbering updated (Step 2 becomes Step 1, etc.)

---

## References

- @.claude/commands/coldstart.md (target file)
- @.claude/haios/lib/coldstart_orchestrator.py (already loads config internally)
- @docs/work/active/WORK-235/WORK.md (parent investigation)
