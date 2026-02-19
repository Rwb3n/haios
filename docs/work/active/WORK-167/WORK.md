---
template: work_item
id: WORK-167
title: Governance Tier Detection
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-19
spawned_by: WORK-160
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-02-19'
priority: high
effort: small
traces_to:
- REQ-CEREMONY-005
- REQ-LIFECYCLE-005
requirement_refs: []
source_files:
- .claude/haios/lib/session_end_actions.py
- .claude/haios/lib/tier_detector.py
acceptance_criteria:
- detect_tier(work_id) returns correct tier for all 4 predicate paths (trivial/small/standard/architectural)
- Absent effort or source_files fields default to Standard tier (conservative safe
  default)
- Absent or empty traces_to does not trigger Architectural tier; with all other fields
  absent/empty, defaults to Standard (conservative safe default per REQ-LIFECYCLE-005)
- Tier determination logged to governance-events.jsonl as TierDetected event
- Tests cover all 4 tiers plus edge cases (missing fields, empty fields)
- Zero dependency on hook infrastructure (pure lib/ function)
blocked_by: []
blocks:
- WORK-169
enables:
- WORK-169
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-19 00:17:34
  exited: '2026-02-19T01:18:05.253351'
artifacts: []
cycle_docs: {}
memory_refs:
- 85390
- 86700
extensions:
  epoch: E2.8
  parent: WORK-160
version: '2.0'
generated: 2026-02-19
last_updated: '2026-02-19T01:18:05.256351'
queue_history:
- position: done
  entered: '2026-02-19T01:18:05.253351'
  exited: null
---
# WORK-167: Governance Tier Detection

---

## Context

REQ-CEREMONY-005 (Proportional Ceremony Depth) defines a four-tier model: None (trivial) -> Checklist (small) -> Full (standard) -> Operator (architectural). REQ-LIFECYCLE-005 defines computable predicates for tier classification based on work item metadata (effort, source_files, plan existence, ADR reference). Currently no function exists to compute the tier — agents apply the predicates manually from reading documentation.

This work item implements a pure function `detect_tier(work_id) -> str` in `lib/tier_detector.py` that computes the governance tier from WORK.md frontmatter. This is the foundation for all other ceremony automation — critique-as-hook (WORK-169), phase migration (WORK-171), and proportional scaling all depend on tier detection.

**Predicate specification (from WORK-101 design, functional_requirements.md):**
- **Trivial (None):** effort=small AND source_files <= 2 AND no plan AND no ADR AND no type=design
- **Small (Checklist):** effort=small AND source_files <= 3 AND no ADR AND no type=design
- **Standard (Full):** Default when neither Trivial nor Small match
- **Architectural (Operator):** type=design OR ADR in traces_to

**Pattern:** Follows `session_end_actions.py` — pure functions in lib/, fail-permissive, testable without hook infrastructure, `_default_project_root()` for path derivation.

---

## Deliverables

- [ ] New file `lib/tier_detector.py` with `detect_tier(work_id)` function
- [ ] Implements all 4 tier predicates from REQ-LIFECYCLE-005
- [ ] Conservative defaults for missing fields (-> Standard)
- [ ] Governance event logging for tier determination
- [ ] Tests in `tests/test_tier_detector.py` covering all tiers + edge cases

---

## History

### 2026-02-19 - Created (Session 399)
- Spawned from WORK-160 decomposition
- Foundation item — blocks WORK-169 (Critique-as-Hook)

---

## References

- @docs/work/active/WORK-160/WORK.md (parent)
- @docs/work/active/WORK-101/plans/PLAN.md (tier predicate specification)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-LIFECYCLE-005, REQ-CEREMONY-005)
- @.claude/haios/lib/session_end_actions.py (pattern template)
- Memory: 85390 (104% problem — motivation for proportional governance)
