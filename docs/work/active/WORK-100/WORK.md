---
template: work_item
id: WORK-100
title: Fix audit_decision_coverage Hardcoded Epoch Path
type: bugfix
status: complete
owner: Hephaestus
created: 2026-02-05
spawned_by: WORK-098
chapter: CH-028-PathConfigMigration
arc: portability
closed: '2026-02-12'
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
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-05 18:35:12
  exited: '2026-02-12T22:11:59.447082'
artifacts: []
cycle_docs: {}
memory_refs:
- 85035
- 85036
- 85037
- 85038
- 85039
- 85040
extensions:
  epoch: E2.5
  discovered_during: WORK-098
  issue_type: hardcoded_path
version: '2.0'
generated: 2026-02-05
last_updated: '2026-02-12T22:12:19.875216'
queue_history:
- position: ready
  entered: '2026-02-12T22:07:47.142549'
  exited: '2026-02-12T22:07:47.165363'
- position: working
  entered: '2026-02-12T22:07:47.165363'
  exited: '2026-02-12T22:11:59.447082'
- position: done
  entered: '2026-02-12T22:11:59.447082'
  exited: null
---
# WORK-100: Fix audit_decision_coverage Hardcoded Epoch Path

---

## Context

`audit_decision_coverage.py` lines 306-307 hardcode `E2_4` epoch path. Now that we're in E2.5, the audit reports stale E2.4 decisions instead of current epoch. Should read from `haios.yaml` `epoch.epoch_file` and `epoch.arcs_dir`.

This is one of 17 hardcoded paths identified in WORK-094 (portability investigation).

---

## Deliverables

- [x] Replace hardcoded `E2_4` paths with ConfigLoader or haios.yaml lookup
- [x] Verify `just audit-decision-coverage` reports E2.5 decisions
- [x] Add test for dynamic epoch path resolution

---

## History

### 2026-02-12 - Implemented (Session 358)
- Extracted `get_default_paths()` function reading from ConfigLoader
- Replaced hardcoded `E2_4` paths in `__main__` block
- Added 3 tests: `TestGetDefaultPaths` (config read, Path types, existence)
- `just audit-decision-coverage` now reports E2.5 decisions

### 2026-02-05 - Created (Session 314)
- Spawned from WORK-098 investigation (Tier 2 finding)
- Part of portability arc CH-028 (path config migration)

---

## References

- @docs/work/active/WORK-098/WORK.md (investigation)
- @.claude/haios/lib/audit_decision_coverage.py (affected file)
- @.claude/haios/config/haios.yaml (epoch config source)
