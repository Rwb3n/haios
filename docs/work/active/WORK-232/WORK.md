---
template: work_item
id: WORK-232
title: Inject Memory Schema Hints into Coldstart Orchestrator Output
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
  entered: '2026-02-25T22:08:58.239880'
  exited: '2026-02-25T22:43:00.190534'
queue_history:
- position: backlog
  entered: '2026-02-25T22:08:58.239880'
  exited: '2026-02-25T22:37:52.862422'
- position: ready
  entered: '2026-02-25T22:37:52.862422'
  exited: '2026-02-25T22:41:14.120557'
- position: working
  entered: '2026-02-25T22:41:14.120557'
  exited: '2026-02-25T22:43:00.190534'
- position: done
  entered: '2026-02-25T22:43:00.190534'
  exited: null
memory_refs: []
requirement_refs: []
source_files:
- .claude/haios/lib/coldstart_orchestrator.py
- docs/specs/memory_db_schema_v3.sql
acceptance_criteria:
- Coldstart orchestrator output includes memory schema hints (concepts table column
  names)
- Agent can query memory correctly without first calling schema_info — column names
  are in coldstart context
- Schema hints are injected in SESSION or OPERATIONS phase, not a new phase
artifacts: []
extensions: {}
version: '2.0'
generated: '2026-02-25'
last_updated: '2026-02-25T22:43:00.196061'
---
# WORK-232: Inject Memory Schema Hints into Coldstart Orchestrator Output

---

## Context

During S459 coldstart, the agent queried memory with `concept_type` (wrong column name). The actual column is `type`. This happens every session because the memory schema is not in coldstart context — the agent must call `schema_info` first or guess wrong.

Fix: Inject a compact schema hint into the coldstart orchestrator output so agents know column names without a round-trip. The concepts table has 8 columns: `id`, `type`, `content`, `source_adr`, `synthesis_confidence`, `synthesized_at`, `synthesis_cluster_id`, `synthesis_source_count`.

Implementation: Add schema hints to an existing phase (SESSION or OPERATIONS) in `coldstart_orchestrator.py`. No new phase needed.

---

## Deliverables

- [ ] Schema hint block added to coldstart orchestrator output
- [ ] Hint includes concepts table column names and key types

---

## References

- @.claude/haios/lib/coldstart_orchestrator.py (target file)
- @docs/specs/memory_db_schema_v3.sql (schema source of truth)
- @docs/work/active/WORK-235/WORK.md (parent investigation)
