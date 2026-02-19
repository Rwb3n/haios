---
template: work_item
id: WORK-177
title: Chapter Manifest Auto-Update on Work Creation
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-19
spawned_by: WORK-173
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-02-19'
priority: low
effort: small
traces_to:
- REQ-CEREMONY-001
- REQ-TRACE-004
requirement_refs: []
source_files:
- .claude/haios/lib/scaffold.py
- .claude/haios/modules/work_engine.py
- .claude/haios/lib/spawn_ceremonies.py
acceptance_criteria:
- When a work item is created with a chapter field, the chapter's CHAPTER.md work
  items table is auto-updated
- Auto-update follows fail-permissive pattern (never blocks work creation)
- Tests verify chapter manifest is updated after work creation
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: plan
node_history:
- node: backlog
  entered: 2026-02-19 22:35:07
  exited: '2026-02-19T22:40:16.474787'
- node: plan
  entered: '2026-02-19T22:40:16.509295'
  exited: '2026-02-19T23:08:36.564815'
artifacts: []
cycle_docs: {}
memory_refs:
- 86887
- 86893
- 84297
extensions:
  epoch: E2.8
version: '2.0'
generated: 2026-02-19
last_updated: '2026-02-19T23:08:36.568810'
queue_history:
- position: ready
  entered: '2026-02-19T22:40:16.474787'
  exited: '2026-02-19T22:40:16.505099'
- position: working
  entered: '2026-02-19T22:40:16.505099'
  exited: '2026-02-19T23:08:36.564815'
- position: done
  entered: '2026-02-19T23:08:36.564815'
  exited: null
---
# WORK-177: Chapter Manifest Auto-Update on Work Creation

---

## Context

When work items are batch-created (e.g., S403 created WORK-172-176), the chapter manifest is not updated. This creates traceability drift — work items declare `chapter: CH-059` but CH-059's work items table doesn't list them. The drift persisted from S403 through S405, caught by critique-agent in S406.

Observed in S406: WORK-173 declared `chapter: CH-059` but CH-059 did not list WORK-173. Critique finding A2 (blocking) — traceability chain broken per REQ-TRACE-004. Fixed manually during PLAN phase.

**Fix:** When scaffold_template() (or WorkEngine.create_work()) creates a work item with a `chapter` field, auto-append the new work ID to the chapter's CHAPTER.md work items table. Fail-permissive — never block work creation if chapter update fails.

Spawned from WORK-173 retro-cycle FEATURE-1 (mem:86887, 86893).

---

## Deliverables

- [ ] Auto-update function for chapter manifest on work creation (fail-permissive)
- [ ] Integration into scaffold or WorkEngine create path
- [ ] Tests verifying chapter manifest updated after work creation
- [ ] Tests verifying graceful failure when chapter file missing

---

## History

### 2026-02-19 - Created (Session 406)
- Spawned from WORK-173 retro-cycle FEATURE-1 (WDN-1: CH-059 missing WORK-173-176)
- S403 batch triage created work items without updating chapter manifests

---

## References

- @.claude/haios/lib/scaffold.py (scaffold_template)
- @.claude/haios/epochs/E2_8/arcs/call/chapters/CH-059-CeremonyAutomation/CHAPTER.md (example chapter)
- Memory: 86887, 86893 (retro-extract FEATURE-1)
