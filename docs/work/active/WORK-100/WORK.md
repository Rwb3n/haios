---
template: work_item
id: WORK-100
title: Fix audit_decision_coverage Hardcoded Epoch Path
type: bugfix
status: active
owner: Hephaestus
created: 2026-02-05
spawned_by: WORK-098
chapter: CH-028-PathConfigMigration
arc: portability
closed: null
priority: low
effort: small
traces_to:
- REQ-PORTABLE-001
- REQ-CONFIG-001
requirement_refs: []
source_files:
- .claude/haios/lib/audit_decision_coverage.py
acceptance_criteria:
- audit_decision_coverage reads epoch path from haios.yaml
- just audit-decision-coverage reports E2.5 decisions
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-05 18:35:12
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.5
  discovered_during: WORK-098
  issue_type: hardcoded_path
version: '2.0'
generated: 2026-02-05
last_updated: '2026-02-05T18:35:36'
---
# WORK-100: Fix audit_decision_coverage Hardcoded Epoch Path

---

## Context

`audit_decision_coverage.py` lines 306-307 hardcode `E2_4` epoch path. Now that we're in E2.5, the audit reports stale E2.4 decisions instead of current epoch. Should read from `haios.yaml` `epoch.epoch_file` and `epoch.arcs_dir`.

This is one of 17 hardcoded paths identified in WORK-094 (portability investigation).

---

## Deliverables

- [ ] Replace hardcoded `E2_4` paths with ConfigLoader or haios.yaml lookup
- [ ] Verify `just audit-decision-coverage` reports E2.5 decisions
- [ ] Add test for dynamic epoch path resolution

---

## History

### 2026-02-05 - Created (Session 314)
- Spawned from WORK-098 investigation (Tier 2 finding)
- Part of portability arc CH-028 (path config migration)

---

## References

- @docs/work/active/WORK-098/WORK.md (investigation)
- @.claude/haios/lib/audit_decision_coverage.py (affected file)
- @.claude/haios/config/haios.yaml (epoch config source)
