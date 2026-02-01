---
template: work_item
id: WORK-041
title: Design CH-003 GovernanceRules
type: design
status: complete
owner: Hephaestus
created: 2026-01-30
spawned_by: null
chapter: CH-003
arc: activities
closed: '2026-02-01'
priority: medium
effort: medium
traces_to:
- REQ-ACTIVITY-001
- REQ-ACTIVITY-002
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
memory_refs:
- 82798
- 82799
- 82800
- 82801
- 82802
- 82803
- 82804
- 82805
- 82806
- 82807
- 82808
- 82809
- 82810
- 82811
- 82812
extensions: {}
version: '2.0'
generated: 2026-01-30
last_updated: '2026-02-01T14:22:38'
---
# WORK-041: Design CH-003 GovernanceRules

---

## Context

CH-001 ActivityMatrix defines the full matrix of Primitive × State × Rule (102 cells across 17 primitives and 6 states). CH-002 StateDefinitions formalizes the 6 states with schemas, entry/exit conditions, and detection logic.

**Problem:** The rules themselves exist only as table cells in CH-001. We need:

1. **Rule schema** - What fields define a governance rule? (action: allow/warn/block/redirect, message, conditions)
2. **Rule lookup data structure** - How are rules stored for fast lookup by (primitive, state)?
3. **Rule application logic** - How does `check_activity()` evaluate rules with context?
4. **Warning vs Block behavior** - When to warn (continue with message) vs block (halt with error)?
5. **Context sensitivity** - How do path patterns, tool inputs affect rule application?

**Depends on:**
- CH-001 ActivityMatrix (defines what rules govern)
- CH-002 StateDefinitions (defines states used in lookup)

**Enables:**
- CH-004 PreToolUseIntegration (needs rules to enforce)

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

- [x] **Rule Schema** - YAML schema defining rule structure (action, message, path_patterns, tool_inputs, conditions)
- [x] **Rule Actions Spec** - Formal definition of allow/warn/block/redirect with expected caller behavior
- [x] **Data Structure Design** - How rules are stored (activity_matrix.yaml format) for O(1) lookup
- [x] **check_activity() Algorithm** - Pseudocode for rule lookup and context-sensitive evaluation
- [x] **Path Classification Logic** - Algorithm for classifying write paths (spec, artifact, notes, etc.)
- [x] **Skill Restriction Rules** - DO-phase skill allowlist/blocklist per CH-001 "Skill Restrictions in DO"
- [x] **CH-003-GovernanceRules.md** - Chapter file documenting all of the above

---

## History

### 2026-01-30 - Created (Session 247)
- Initial scaffold

### 2026-02-01 - Populated (Session 269)
- Added context from CH-001 ActivityMatrix and CH-002 StateDefinitions
- Defined deliverables covering rule schema, data structure, algorithms
- Linked to REQ-ACTIVITY-001, REQ-ACTIVITY-002

### 2026-02-01 - Completed (Session 269)
- Created CH-003-GovernanceRules.md with all 6 design sections
- Rule schema: action, message, redirect_to, path_patterns, tool_inputs, conditions
- Data structure: activity_matrix.yaml with O(1) lookup
- Algorithms: check_activity(), classify_path(), _check_skill_restriction()
- All 7 deliverables verified complete
- WHY captured to memory (82798-82803)

---

## References

- @.claude/haios/epochs/E2_4/arcs/activities/CH-001-ActivityMatrix.md (source spec)
- @.claude/haios/epochs/E2_4/arcs/activities/CH-002-StateDefinitions.md (state definitions)
- @.claude/haios/epochs/E2_4/arcs/activities/ARC.md (parent arc)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-ACTIVITY-001, REQ-ACTIVITY-002)
