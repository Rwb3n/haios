---
template: work_item
id: WORK-202
title: "Effort Tier Predicate File-Type Weighting"
type: design
status: active
owner: Hephaestus
created: 2026-02-23
spawned_by: WORK-200
spawned_children: []
chapter: null
arc: null
closed: null
priority: low
effort: small
traces_to:
  - REQ-LIFECYCLE-005
requirement_refs: []
source_files:
  - .claude/haios/manifesto/L4/functional_requirements.md
acceptance_criteria:
  - "Analysis of whether file type (markdown vs Python) should weight effort tier predicate"
  - "If yes: proposed predicate modification with backward compatibility"
  - "If no: documented rationale for current predicate being sufficient"
blocked_by: []
blocks: []
enables: []
queue_position: parked
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-02-23T12:26:41
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
  - 87756
extensions: {}
version: "2.0"
generated: 2026-02-23
last_updated: 2026-02-23T12:26:41
---
# WORK-202: Effort Tier Predicate File-Type Weighting

---

## Context

During WORK-200 implementation (proportional close ceremony), all changes were markdown-only (4 skill/command files). Despite effort=medium classification (correct given 4 source files + plan), execution complexity felt closer to small — the DO phase completed in under 5 minutes with parallel sub-agent dispatch.

Current effort tier predicate in REQ-LIFECYCLE-005 uses `effort` field + `source_files` count. It does not consider file type. Markdown-only changes have lower cognitive complexity than Python changes at the same file count (no test failures to debug, no import chains, no runtime behavior).

This is a refinement, not a bug. Current predicate works correctly for all cases. Parked for future epoch consideration.

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning) -->

- [ ] Analysis document: file-type weighting pros/cons
- [ ] Decision: modify predicate or document as sufficient

---

## History

### 2026-02-23 - Created (Session 430)
- Spawned from WORK-200 retro-cycle EXTRACT-2 (upgrade, priority: later)
- Evidence: WORK-200 effort=medium but markdown-only DO phase completed in <5 min

---

## References

- @docs/work/active/WORK-200/WORK.md (parent)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-LIFECYCLE-005)
- Memory: 87756 (retro-extract:WORK-200 EXTRACT-2)
