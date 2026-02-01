---
template: work_item
id: WORK-061
title: EXPLORE-FIRST Investigation Cycle Implementation
type: implementation
status: active
owner: Hephaestus
created: 2026-02-01
spawned_by: WORK-037
chapter: null
arc: flow
closed: null
priority: medium
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
  entered: 2026-02-01 15:18:38
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82829
- 82830
- 82831
- 82832
- 82833
- 82834
- 82835
- 82836
- 82837
extensions: {}
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-01T15:19:42'
---
# WORK-061: EXPLORE-FIRST Investigation Cycle Implementation

---

## Context

**Background:** WORK-037 investigation designed the EXPLORE-FIRST pattern for investigation-cycle. L4 Decision (Session 265) approved inverting the cycle from HYPOTHESIZE→EXPLORE→CONCLUDE to EXPLORE→HYPOTHESIZE→VALIDATE→CONCLUDE.

**Design Spec:** See @docs/work/active/WORK-037/investigations/001-explore-first-design.md for full phase contracts, governed activities matrix, and skill update specification.

**Key Changes:**
1. Four phases instead of three (adds VALIDATE)
2. Template Tax reduction: 368 lines → ~140 lines (62% reduction)
3. MUST gates reduction: 18 → 9 (50% reduction)
4. Fractured templates: one ~30-line template per phase

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

- [ ] Update activity_matrix.yaml with new phase-to-state mappings
- [ ] Create fractured templates directory (.claude/templates/investigation/)
- [ ] Create EXPLORE.md phase template (~30 lines)
- [ ] Create HYPOTHESIZE.md phase template (~30 lines)
- [ ] Create VALIDATE.md phase template (~30 lines)
- [ ] Create CONCLUDE.md phase template (~30 lines)
- [ ] Update investigation-cycle/SKILL.md with new flow
- [ ] Add deprecation notice to monolithic investigation.md
- [ ] Store implementation learnings to memory

---

## History

### 2026-02-01 - Created (Session 271)
- Spawned from WORK-037 investigation (EXPLORE-FIRST design)
- Design spec complete in WORK-037/investigations/001-explore-first-design.md

---

## References

- @docs/work/active/WORK-037/WORK.md (spawning investigation)
- @docs/work/active/WORK-037/investigations/001-explore-first-design.md (design spec)
- @.claude/skills/investigation-cycle/SKILL.md (target for update)
- @.claude/haios/config/activity_matrix.yaml (phase mappings)
- @.claude/haios/epochs/E2_4/arcs/flow/ARC.md (parent arc)
- Memory concepts 82829-82837 (WORK-037 design findings)
