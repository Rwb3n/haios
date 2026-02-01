---
template: work_item
id: WORK-037
title: Investigation Cycle Redesign - EXPLORE-FIRST Pattern
type: investigation
status: complete
owner: Hephaestus
created: 2026-01-30
spawned_by: WORK-036
chapter: null
arc: null
closed: '2026-02-01'
priority: low
effort: medium
traces_to: []
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-30 19:26:12
  exited: null
artifacts: []
cycle_docs:
  investigation: investigations/001-explore-first-design.md
memory_refs:
- 82646
- 82647
- 82648
- 82649
- 82650
- 82651
- 82652
- 82653
- 82654
- 82655
- 82656
- 82721
- 82722
- 82723
- 82829
- 82830
- 82831
- 82832
- 82833
- 82834
- 82835
- 82836
- 82837
- 82852
- 82853
- 82854
- 82855
extensions: {}
version: '2.0'
generated: 2026-01-30
last_updated: '2026-02-01T15:20:48'
---
# WORK-037: Investigation Cycle Redesign - EXPLORE-FIRST Pattern

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Background:** WORK-036 investigation found the investigation-cycle imposes a "Template Tax" (25 MUST gates + 27 checkboxes) that constrains depth. The Explore agent (built-in, unconstrained) produced deeper analysis in Session 262 than formal investigations typically achieve.

**L4 Decision (Session 265):** The EXPLORE-FIRST pattern was **approved** as part of E2.4 "The Activity Layer". Memory concepts 82721-82723 capture this decision:
- "L4 Decision Session 265: Investigation Flow (EXPLORE-FIRST)"
- "This inverts the previous HYPOTHESIZE → EXPLORE → CONCLUDE pattern."
- New flow: `EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE`

**Pivot (Session 271):** The original scope (evaluate Options C and D) is superseded. This investigation now focuses on **designing the implementation** of the approved EXPLORE-FIRST pattern.

**Design Questions:**
1. How should the investigation-cycle skill be restructured?
2. How do fractured phase templates (E2.4 Templates arc) interact with new flow?
3. What governed activities apply to each new phase?
4. What migration path exists for existing investigations?

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

- [x] Design spec: EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE phase definitions
- [x] Integration: How new flow interacts with E2.4 fractured phase templates
- [x] Governed activities: Activity matrix for each investigation phase
- [x] Migration path: How to handle existing investigations (if any in-flight)
- [x] Skill update: Draft changes to investigation-cycle/SKILL.md
- [x] Store findings to memory (concepts 82829-82837)

---

## History

### 2026-01-30 - Created (Session 263)
- Spawned from WORK-036 investigation findings
- Options C (EXPLORE-FIRST) and D (Hybrid) identified for further exploration
- Marked low priority per operator direction ("leave for later triage")

### 2026-02-01 - Pivoted (Session 271)
- L4 Decision (Session 265) approved EXPLORE-FIRST, superseding original evaluation scope
- Scope pivoted from "evaluate options" to "design implementation"
- Added memory refs to Session 265 L4 decisions (82721-82723)

### 2026-02-01 - Complete (Session 271)
- Design spec complete: investigations/001-explore-first-design.md
- All deliverables checked
- Memory stored: concepts 82829-82837
- Spawned: WORK-061 (implementation)

---

## References

- @docs/work/active/WORK-036/WORK.md (spawning investigation)
- @docs/work/active/WORK-036/investigations/001-investigation-template-vs-explore-agent-effectiveness.md
- @.claude/skills/investigation-cycle/SKILL.md
- @.claude/haios/epochs/E2_4/EPOCH.md (E2.4 decisions)
- @.claude/haios/epochs/E2_4/arcs/templates/ARC.md (fractured templates arc)
- Memory concepts 82646-82656 (WORK-036 findings)
- Memory concepts 82721-82723 (L4 Decision: EXPLORE-FIRST)
- Memory concepts 82829-82837 (WORK-037 design findings)
- @docs/work/active/WORK-061/WORK.md (spawned implementation)
