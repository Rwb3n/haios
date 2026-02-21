---
template: work_item
id: WORK-182
title: "Three-Contract Model Formalization"
type: design
status: active
owner: Hephaestus
created: 2026-02-21
spawned_by: null
spawned_children: []
chapter: null
arc: null
closed: null
priority: low
effort: medium
traces_to:
  - REQ-LIFECYCLE-001
requirement_refs: []
source_files:
  - .claude/skills/implementation-cycle/SKILL.md
  - .claude/templates/plans/implementation-v2.md
acceptance_criteria:
  - "Three-contract model (Scope/Content/Dispatch) documented as ADR"
  - "Contract hierarchy (system-level vs work-level) formalized"
  - "Chapter-as-contract-container pattern explored"
blocked_by: []
blocks: []
enables: []
queue_position: parked
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-21T16:01:53
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-21
last_updated: 2026-02-21T16:01:53
---
# WORK-182: Three-Contract Model Formalization

---

## Context

Three-contract model emerged from S416 stress-testing of the v2.0 plan template as a sub-agent handoff mechanism. The model identifies three distinct contract types that govern all HAIOS work:

1. **Scope contract** (WORK.md) — WHAT is expected. Set by operator/designer. Deliverables, acceptance criteria, requirement traces.
2. **Content contract** (PLAN.md / ADR / TRD) — HOW to build it. Produced by author agents, consumed by DO agents. The v2.0 plan with `spec_ref` fields makes dispatch mechanical.
3. **Dispatch contract** (SKILL.md) — HOW to orchestrate. System-level, keyed by work type. Agent sequence, handoffs, failure modes.

Additionally, contracts exist at two levels:
- **System-level:** Dispatch (SKILL.md), Schema (templates) — change per work type
- **Work-level:** Scope (WORK.md), Content (PLAN.md) — change per work item

Parked insights for E2.9:
- Contract hierarchy formalization (system vs work level)
- Chapter-as-contract-container pattern (chapters group related contracts)
- `system.db` concept for system-level contract registry
- Critique/retro/checkpoint outputs are NOT contracts (ephemeral feedback, session state, audit trail)

**Status: PARKED for E2.9.** The v2.0 dispatch protocol is already implemented and tested (S416). This work formalizes the conceptual model as an ADR.

---

## Deliverables

- [ ] ADR documenting three-contract model (Scope/Content/Dispatch)
- [ ] Contract hierarchy diagram (system-level vs work-level)
- [ ] Chapter-as-contract-container exploration (findings or ADR)

---

## History

### 2026-02-21 - Created (Session 416)
- Surfaced from S416 stress-testing of v2.0 plan template as sub-agent handoff
- Three-contract model validated: Scope(WORK.md) + Content(PLAN.md) + Dispatch(SKILL.md)
- Parked for E2.9 — current E2.8 has working implementation, formalization is design work

---

## References

- @.claude/skills/implementation-cycle/SKILL.md (dispatch protocol, lines 161-199)
- @.claude/templates/plans/implementation-v2.md (spec_ref fields, lines 229-269)
- Memory: S416 conversation (three-contract stress test)
