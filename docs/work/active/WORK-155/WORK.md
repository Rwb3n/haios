---
template: work_item
id: WORK-155
title: Lifecycle Work-Type Awareness Beyond Plan Templates
type: design
status: complete
owner: Hephaestus
created: 2026-02-16
spawned_by: null
spawned_children: []
chapter: CH-047
arc: composability
closed: 2026-02-16
priority: medium
effort: medium
traces_to:
- REQ-LIFECYCLE-001
requirement_refs: []
source_files:
- .claude/skills/implementation-cycle/SKILL.md
- .claude/haios/config/activity_matrix.yaml
- .claude/templates/implementation/PLAN.md
acceptance_criteria:
- Design document specifying how lifecycle adapts to work type (implementation, design,
  investigation, cleanup)
- 'Ceremony chain adapts: design work skips TDD gates, investigation skips file manifests,
  cleanup skips detailed design'
- Computable predicate pattern (retro-cycle Phase 0) extended to full implementation
  cycle
- WORK-152 (plan template fracturing) identified as first implementation step
blocked_by: []
blocks: []
enables: []
queue_position: working
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-16 18:45:11
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 85737
- 85738
- 85739
- 85740
- 85741
- 85742
- 85743
- 85744
extensions: {}
version: '2.0'
generated: 2026-02-16
last_updated: '2026-02-16T23:22:47.018999'
queue_history:
- position: ready
  entered: '2026-02-16T23:22:46.988998'
  exited: '2026-02-16T23:22:47.015454'
- position: working
  entered: '2026-02-16T23:22:47.015454'
  exited: null
---
# WORK-155: Lifecycle Work-Type Awareness Beyond Plan Templates

---

## Context

WORK-152 (Plan Template Fracturing by Work Type) addresses one symptom: the plan template is skewed toward code implementation, forcing design work to SKIP 8+ sections. But the broader problem is that the entire lifecycle (ceremony chain, gates, phases) doesn't adapt to work type.

Evidence from S383 triage (Theme 4, 6+ convergent entries):
- A type=design work item routes through the same 12-phase ceremony chain as type=implementation (85540)
- Design work needs decision quality critique but not TDD; investigation needs hypothesis tracking but not file manifests (85541)
- The retro-cycle Phase 0 trivial predicate is a proven prototype for proportional scaling (85534, 85578)
- Template and lifecycle should be work-type-aware from the start, not just at plan time (85539)

This is a design item: produce the specification for how lifecycle adapts to work type. WORK-152 becomes the first concrete implementation step. Relates to WORK-101 (proportional governance, E2.9) but scoped to type-awareness rather than effort-based scaling.

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

- [ ] Design document: lifecycle adaptation by work type
- [ ] Type-to-ceremony mapping: which phases/gates are mandatory/optional per type
- [ ] Computable predicate extension design (from retro-cycle Phase 0 to full cycle)
- [ ] Relationship to WORK-152 and WORK-101 clarified

---

## History

### 2026-02-16 - Created (Session 383)
- Spawned from S383 observation triage cycle (Theme 4: Plan Template / Work-Type Awareness)
- Broader scope than WORK-152: full lifecycle adaptation, not just plan templates
- Memory evidence: 85558, 85541, 85540, 85539, 85534, 85530, 85529, 85528, 85578

---

## References

- WORK-152 (plan template fracturing — first implementation step)
- WORK-101 (proportional governance — effort-based scaling, E2.9)
- Memory: 85558, 85541, 85540, 85539, 85534, 85530, 85578 (triage evidence)
- Memory: 85605-85608 (S383 triage synthesis: ceremony overhead)
