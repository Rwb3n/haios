---
template: work_item
id: WORK-014
title: Type-Based Routing Migration
type: chore
status: complete
owner: Hephaestus
created: 2026-01-25
spawned_by: WORK-013
chapter: null
arc: workuniversal
closed: '2026-01-25'
priority: high
effort: medium
traces_to: []
requirement_refs: []
source_files:
- .claude/lib/routing.py
- .claude/lib/status.py
- .claude/haios/modules/portal_manager.py
- .claude/haios/modules/memory_bridge.py
acceptance_criteria:
- Routing uses type field instead of ID prefix
- All 12 identified files updated
- Existing legacy items continue to work
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-25 20:08:30
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82414
- 82415
- 82416
- 82417
- 82418
extensions: {}
version: '2.0'
generated: 2026-01-25
last_updated: '2026-01-25T20:09:00'
---
# WORK-014: Type-Based Routing Migration

@docs/work/active/WORK-013/WORK.md
@docs/specs/TRD-WORK-ITEM-UNIVERSAL.md

---

## Context

**Problem:** Routing logic uses ID prefix (`INV-*`, `E2-*`, `TD-*`) to determine work type. TRD-WORK-ITEM-UNIVERSAL specifies type as a field, not a prefix. This creates inconsistency where WORK-XXX items with `type: investigation` route incorrectly.

**Root Cause:** WORK-013 investigation found 12 files with prefix-based routing:
- 4 Python modules
- 8 skill/command files

**Solution:** Update all routing logic to check `type` field instead of ID prefix. Legacy items will continue to work because WorkEngine falls back to inferring type from prefix when `type` field is missing.

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

### Python Modules (4 files)
- [ ] `.claude/lib/routing.py:62-67` - Route by type field
- [ ] `.claude/lib/status.py:819-820` - Determine cycle_type by type field
- [ ] `.claude/haios/modules/portal_manager.py:225-226` - Remove INV- prefix check
- [ ] `.claude/haios/modules/memory_bridge.py:211` - Add WORK-* to regex patterns

### Skill Files (6 files)
- [ ] `.claude/skills/survey-cycle/SKILL.md` - Update routing table
- [ ] `.claude/skills/routing-gate/SKILL.md` - Update decision table
- [ ] `.claude/skills/implementation-cycle/SKILL.md:270` - Update routing
- [ ] `.claude/skills/investigation-cycle/SKILL.md:152` - Update routing
- [ ] `.claude/skills/close-work-cycle/SKILL.md:72,191` - Update DoD logic
- [ ] `.claude/skills/work-creation-cycle/SKILL.md:173` - Update routing

### Command Files (1 file)
- [ ] `.claude/commands/close.md` - Update INV-* handling

### Deprecated (1 file - optional)
- [ ] `.claude/lib/work_item.py:247` - Remove if still used, or leave as deprecated

---

## History

### 2026-01-25 - Created (Session 238)
- Spawned from WORK-013 investigation findings
- Scope: 12 files need type-based routing updates

---

## References

- @docs/work/active/WORK-013/WORK.md (parent investigation)
- @docs/specs/TRD-WORK-ITEM-UNIVERSAL.md (type-as-field specification)
