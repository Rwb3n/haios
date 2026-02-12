---
template: work_item
id: WORK-135
title: "Manifest Auto-Sync Mechanism"
type: implementation
status: backlog
owner: null
created: 2026-02-12
spawned_by: null
chapter: null
arc: portability
closed: null
priority: low
effort: small
traces_to: [REQ-PORTABLE-001]
requirement_refs: []
source_files: [".claude/haios/manifest.yaml", ".claude/haios/lib/scaffold.py"]
acceptance_criteria:
  - "Manifest stays in sync when skills/agents are created"
  - "Drift is detectable automatically"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-12T20:53:05
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: [85021, 85022, 85023, 85024]
extensions: {}
version: "2.0"
generated: 2026-02-12
last_updated: 2026-02-12T20:53:05
---
# WORK-135: Manifest Auto-Sync Mechanism

---

## Context

Session 355 discovered 15 skills and 3 agents missing from `manifest.yaml`. Skills/agents are created via scaffold but the manifest is never updated. The `test_manifest.py::test_component_counts_match_file_system` test catches drift but only as a count mismatch — it doesn't identify which items are missing.

**Root cause:** No auto-sync mechanism exists between disk and manifest. Every skill/agent creation silently increases drift.

**Options:**
1. `just manifest-sync` recipe that regenerates manifest components from disk
2. PostToolUse hook on Write for `.claude/skills/*/SKILL.md` that warns about manifest
3. Improve test to show diff, not just count mismatch

---

## Deliverables

- [ ] Mechanism to detect or prevent manifest drift
- [ ] Test improvement: show which items are missing, not just count delta

---

## History

### 2026-02-12 - Created (Session 355)
- Discovered during bug fix pass: 15 skills + 3 agents missing from manifest
- Manual fix applied this session; work item tracks prevention

---

## References

- `.claude/haios/manifest.yaml` — plugin manifest
- `tests/test_manifest.py` — component count test
- Memory: 85021-85024 (manifest drift pattern)
