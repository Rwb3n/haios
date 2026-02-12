---
template: work_item
id: WORK-141
title: "Fix audit-decision-coverage Warnings-Only Exit Code"
type: bugfix
status: active
owner: Hephaestus
created: 2026-02-12
spawned_by: WORK-100
spawned_children: []
chapter: null
arc: null
closed: null
priority: low
effort: small
traces_to: []
requirement_refs: []
source_files:
- .claude/haios/lib/audit_decision_coverage.py
acceptance_criteria:
- "audit-decision-coverage distinguishes warnings from errors in exit code"
- "Warnings (missing assigned_to) do not mask errors (orphan decisions)"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-12T22:40:28
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-12
last_updated: 2026-02-12T22:40:28
---
# WORK-141: Fix audit-decision-coverage Warnings-Only Exit Code

---

## Context

`just audit-decision-coverage` returns exit code 0 (CONSISTENT) even when all 6 decisions have no `assigned_to` field and 33 chapters have no `implements_decisions`. Warnings-only mode makes the audit toothless — it reports "CONSISTENT" when the data is incomplete. Memory 84233 from S331 already noted this. The exit code should distinguish between "no errors" and "warnings present" so consumers can decide severity.

---

## Deliverables

- [ ] Add severity levels to audit exit code (0=clean, 1=errors, 2=warnings-only)
- [ ] Or: separate `--strict` flag that treats warnings as errors
- [ ] Update `validate_full_coverage` to track warning-vs-error distinction
- [ ] Add test for exit code behavior

---

## History

### 2026-02-12 - Created (Session 358)
- Observed during E2.5 epoch closure validation
- Memory 84233 (S331) already noted this issue
- Spawned from WORK-100 (same file, related concern)

---

## References

- @.claude/haios/lib/audit_decision_coverage.py
- Memory 84233 (S331 observation)
