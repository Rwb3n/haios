---
template: work_item
id: WORK-013
title: INV Prefix Deprecation and Pruning
type: investigation
status: active
owner: Hephaestus
created: 2026-01-25
spawned_by: Session 236 observation triage
chapter: null
arc: workuniversal
closed: null
priority: high
effort: medium
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-25 02:11:12
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-25
last_updated: '2026-01-25T02:12:27'
---
# WORK-013: INV Prefix Deprecation and Pruning

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Legacy ID prefixes (INV-*, E2-*, TD-*) encode type in the ID. TRD-WORK-ITEM-UNIVERSAL specifies sequential IDs (WORK-XXX) with type as a field. Agent just attempted to spawn INV-072 instead of WORK-012.

**Scope:**
1. Identify all places that spawn/reference legacy prefixes (commands, skills, recipes, code)
2. Update to use WORK-XXX with `type: investigation/feature/bug/chore/spike`
3. Determine fate of existing INV-*, E2-*, TD-* items in queue

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

- [ ] Audit: List all code/skills/commands that spawn or route based on INV-* prefix
- [ ] Audit: Count legacy items in queue by prefix (INV-*, E2-*, TD-*)
- [ ] Decision: Migrate existing items or let them age out
- [ ] Update: Modify spawn logic to use WORK-XXX + type field
- [ ] Update: Modify routing logic to check type field, not ID prefix

---

## History

### 2026-01-25 - Created (Session 236)
- Initial creation

---

## References

- [Related documents]
