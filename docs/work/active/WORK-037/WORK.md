---
template: work_item
id: WORK-037
title: Investigation Cycle Redesign - EXPLORE-FIRST Pattern
type: investigation
status: active
owner: Hephaestus
created: 2026-01-30
spawned_by: WORK-036
chapter: null
arc: null
closed: null
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
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-30
last_updated: '2026-01-30T19:27:39'
---
# WORK-037: Investigation Cycle Redesign - EXPLORE-FIRST Pattern

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** WORK-036 investigation found the investigation-cycle imposes a "Template Tax" (25 MUST gates + 27 checkboxes) that constrains depth. The Explore agent (built-in, unconstrained) produced deeper analysis in Session 262 than formal investigations typically achieve.

**Root Cause:** The current HYPOTHESIZE → EXPLORE → CONCLUDE cycle assumes scientific method - form hypothesis first, then test. But discovery work benefits from open exploration BEFORE hypothesis formation.

**Options identified (WORK-036):**
- **Option C: EXPLORE-FIRST Pattern** - Invert cycle to EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE
- **Option D: Hybrid** - Add "discovery-investigation" subtype that uses Explore agent, retain current for validation

**Intent:** This work item is for further design exploration of Options C and/or D. Not necessarily for this epoch - may be triaged to future work.

**Note from Operator:** "not sure if it fits this epoch so leave for later triage"

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

- [ ] Design analysis: Compare EXPLORE-FIRST vs current HYPOTHESIZE-FIRST for different work types
- [ ] Evaluate Option C: Full cycle inversion (pros, cons, migration path)
- [ ] Evaluate Option D: Hybrid approach with "discovery" subtype (pros, cons, complexity)
- [ ] Recommendation: Which option (if any) to pursue
- [ ] If recommendation is "proceed": Draft design spec for chosen option
- [ ] Store findings to memory

---

## History

### 2026-01-30 - Created (Session 263)
- Spawned from WORK-036 investigation findings
- Options C (EXPLORE-FIRST) and D (Hybrid) identified for further exploration
- Marked low priority per operator direction ("leave for later triage")

---

## References

- @docs/work/active/WORK-036/WORK.md (spawning investigation)
- @docs/work/active/WORK-036/investigations/001-investigation-template-vs-explore-agent-effectiveness.md
- @.claude/skills/investigation-cycle/SKILL.md
- Memory concepts 82646-82656 (WORK-036 findings)
