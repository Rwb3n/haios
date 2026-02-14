---
template: work_item
id: WORK-146
title: Gate Skip Violation Logging
type: implementation
status: complete
owner: null
created: 2026-02-14
spawned_by: S365-epoch-planning
spawned_children: []
chapter: CH-040
arc: traceability
closed: '2026-02-14'
priority: medium
effort: small
traces_to:
- REQ-OBSERVE-005
requirement_refs: []
source_files:
- .claude/haios/governance-events.jsonl
- .claude/hooks/
acceptance_criteria:
- MUST gate violations produce events in governance-events.jsonl
- Event includes gate_id, work_id, violation_type, timestamp
- Logging does not block agent workflow (warn, not block)
- At least PreToolUse gate skips are logged
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-14 12:45:14
  exited: '2026-02-14T16:55:54.677353'
artifacts: []
cycle_docs: {}
memory_refs:
- 85400
- 85401
extensions:
  epoch: E2.6
version: '2.0'
generated: 2026-02-14
last_updated: '2026-02-14T16:55:54.680927'
queue_history:
- position: ready
  entered: '2026-02-14T16:27:49.658525'
  exited: '2026-02-14T16:27:49.684744'
- position: working
  entered: '2026-02-14T16:27:49.684744'
  exited: '2026-02-14T16:55:54.677353'
- position: done
  entered: '2026-02-14T16:55:54.677353'
  exited: null
---
# WORK-146: Gate Skip Violation Logging

---

## Context

**Problem:** When MUST gates are skipped (e.g., working outside governance cycles, missing preflight checks), no record is produced. The system cannot observe its own governance violations.

**Evidence:**
- S365 session ran entirely outside governance (acceptable for strategic planning, but unlogged)
- E2.5 anti-pattern: "Skipping MUST gates without logging"
- REQ-OBSERVE-005: MUST gate violations logged to governance events

**Scope:** Add logging to existing hook infrastructure. When a MUST gate detects a violation and allows it (warn mode), emit an event to governance-events.jsonl.

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning) -->

- [ ] Event schema defined for gate violations
- [ ] PreToolUse hooks emit violation events on skip
- [ ] Events include: gate_id, work_id, violation_type, timestamp, context
- [ ] Verification: run outside governance, confirm event logged
- [ ] Documentation updated (event types in L4 observability section)

---

## History

### 2026-02-14 - Created (Session 366)
- E2.6 arc decomposition: assigned to traceability arc, CH-040
- Derives from E2.5 anti-pattern and S365 pending item

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-OBSERVE-005)
- @.claude/haios/epochs/E2_6/EPOCH.md (exit criteria: MUST gate violations logged)
