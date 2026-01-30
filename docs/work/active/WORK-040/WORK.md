---
template: work_item
id: WORK-040
title: Design CH-002 StateDefinitions
type: design
status: active
owner: Hephaestus
created: 2026-01-30
spawned_by: null
chapter: CH-002
arc: activities
closed: null
priority: high
effort: medium
traces_to:
- REQ-ACTIVITY-001
- REQ-FLOW-001
- REQ-FLOW-002
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-30 21:50:40
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-30
last_updated: '2026-01-30T22:53:32'
---
# WORK-040: Design CH-002 StateDefinitions

---

## Context

CH-001 ActivityMatrix (completed Session 266) defined a preliminary state table:

| State | Phase | Purpose | Default Posture |
|-------|-------|---------|-----------------|
| EXPLORE | Discovery | Gather information freely | Permissive |
| DESIGN | Requirements → Spec | Define what to build | Permissive |
| PLAN | Spec → Implementation plan | Define how to build | Permissive |
| DO | Plan → Artifact | Execute the plan | **Restrictive** |
| CHECK | Artifact → Verdict | Verify correctness | Permissive |
| DONE | Closure | Archive and memory | Permissive |

**Problem:** These definitions are insufficient for implementation. We need:
1. **Formal state object schema** - What fields define a state?
2. **Entry/exit conditions** - What must be true to enter/exit each state?
3. **State transition rules** - Valid transitions, forbidden transitions
4. **State detection logic** - How does `get_activity_state()` determine current state?

CH-002 formalizes these so GovernanceLayer can implement state-aware governance.

**Depends on:** CH-001 ActivityMatrix (defines what states govern)
**Enables:** CH-003 GovernanceRules (rules need formal state definitions)

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning)

     These checkboxes are the SOURCE OF TRUTH for work completion.

     During CHECK phase of implementation-cycle:
     - Agent MUST read this section
     - Agent MUST verify EACH checkbox can be marked complete
     - If ANY deliverable is incomplete, work is NOT done

     "Tests pass" ≠ "Deliverables complete"
     Tests verify code works. Deliverables verify scope is complete.

     NOTE (WORK-001): Acceptance criteria are in frontmatter (machine-parseable).
     Deliverables are implementation outputs, not requirements.
-->

- [ ] **State Object Schema** - YAML schema defining state structure (name, posture, entry_conditions, exit_conditions, allowed_activities, blocked_activities)
- [ ] **State Transition Diagram** - Valid transitions (EXPLORE→DESIGN→PLAN→DO→CHECK→DONE) with forbidden paths
- [ ] **State Detection Logic** - Algorithm for `get_activity_state()` using cycle phase mapping
- [ ] **Investigation Variant** - EXPLORE→HYPOTHESIZE→VALIDATE→CONCLUDE mapped to ActivityMatrix states
- [ ] **Failure Mode Handling** - Behavior when state cannot be determined (fallback to EXPLORE per CH-001)
- [ ] **CH-002-StateDefinitions.md** - Chapter file documenting all of the above

---

## History

### 2026-01-30 - Created (Session 247)
- Initial scaffold

### 2026-01-30 - Populated (Session 267)
- Added context from CH-001 ActivityMatrix
- Defined deliverables covering state schema, transitions, detection, variants
- Linked to REQ-ACTIVITY-001, REQ-FLOW-001, REQ-FLOW-002

---

## References

- @.claude/haios/epochs/E2_4/arcs/activities/CH-001-ActivityMatrix.md (depends on)
- @.claude/haios/epochs/E2_4/arcs/activities/ARC.md (parent arc)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-ACTIVITY-001, REQ-FLOW-001, REQ-FLOW-002)
