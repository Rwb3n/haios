---
template: work_item
id: WORK-145
title: "Legacy Duplication Cleanup"
type: implementation
status: complete
owner: null
created: 2026-02-14
spawned_by: S365-epoch-planning
spawned_children: []
chapter: CH-043
arc: observability
closed: 2026-02-15
priority: low
effort: small
traces_to:
- REQ-CONFIG-003
requirement_refs: []
source_files:
- .claude/haios/lib/
acceptance_criteria:
- 3 duplicated lib/ files resolved (single source of truth)
- Deprecated skill identified and removed or marked
- Stale templates cleaned up
- No broken imports after cleanup
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-02-14T12:45:14
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.6
version: "2.0"
generated: 2026-02-14
last_updated: 2026-02-14T12:48:00
---
# WORK-145: Legacy Duplication Cleanup

---

## Context

**Problem:** S365 system audit identified legacy duplication that harms referenceability:
- 3 duplicated files in lib/ (exact duplicates or near-duplicates of modules/)
- At least 1 deprecated skill still present
- Stale templates from pre-E2.5 era

**Why it matters:**
- Agents may find the wrong version of a file
- Duplication violates REQ-CONFIG-003 (single-source-of-truth)
- Stale artifacts confuse discovery mechanisms

**Scope:** Cleanup only. No new features. Remove or consolidate duplicates.

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning) -->

- [ ] Identify all duplicated lib/ files (audit report)
- [ ] Remove duplicates, update imports
- [ ] Remove or mark deprecated skill(s)
- [ ] Remove stale templates
- [ ] Tests still pass after cleanup

---

## History

### 2026-02-14 - Created (Session 366)
- E2.6 arc decomposition: assigned to observability arc, CH-043
- Scope from S365 system audit findings

---

## References

- @.claude/haios/epochs/E2_6/system-audit-S365.md (findings)
