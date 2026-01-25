---
template: work_item
id: WORK-013
title: INV Prefix Deprecation and Pruning
type: investigation
status: complete
owner: Hephaestus
created: 2026-01-25
spawned_by: Session 236 observation triage
chapter: null
arc: workuniversal
closed: '2026-01-25'
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
memory_refs:
- 82401
- 82402
- 82403
- 82404
- 82405
- 82406
- 82407
- 82408
- 82409
- 82410
- 82411
extensions: {}
version: '2.0'
generated: 2026-01-25
last_updated: '2026-01-25T20:09:43'
---
# WORK-013: INV Prefix Deprecation and Pruning

@docs/README.md
@docs/epistemic_state.md
@docs/specs/TRD-WORK-ITEM-UNIVERSAL.md

---

## Context

**Problem:** Legacy ID prefixes (INV-*, E2-*, TD-*) encode type in the ID. TRD-WORK-ITEM-UNIVERSAL specifies sequential IDs (WORK-XXX) with type as a field. Agent just attempted to spawn INV-072 instead of WORK-012.

**Scope:**
1. Identify all places that spawn/reference legacy prefixes (commands, skills, recipes, code)
2. Update to use WORK-XXX with `type: investigation/feature/bug/chore/spike`
3. Determine fate of existing INV-*, E2-*, TD-* items in queue

---

## Hypotheses

**H1:** Routing logic (skills, commands) checks ID prefix to determine work type.
- **Expected:** `survey-cycle`, `routing-gate`, and similar use `INV-*` prefix matching
- **If True:** Update to check `type` field instead

**H2:** Spawn logic (scaffold, /new-* commands) generates legacy prefixes.
- **Expected:** `scaffold.py` or templates still generate INV-XXX, E2-XXX, TD-XXX
- **If True:** Update to use `get_next_work_id()` for WORK-XXX

**H3:** Existing queue items with legacy prefixes need migration or exclusion.
- **Expected:** Queue contains INV-*, E2-*, TD-* items
- **Decision Needed:** Migrate to WORK-XXX, let them age out, or mark as legacy

---

## Exploration Plan

- [x] **Step 1:** Grep for `INV-*` prefix matching in routing logic
- [x] **Step 2:** Grep for ID generation/spawn logic using legacy prefixes
- [x] **Step 3:** Count legacy items in queue by prefix
- [x] **Step 4:** Check TRD-WORK-ITEM-UNIVERSAL for migration guidance
- [x] **Step 5:** Document decision on existing items

---

## Findings

### H1: Routing Logic (CONFIRMED)

12 locations check ID prefix to determine work type:

| File | Line | Pattern |
|------|------|---------|
| `.claude/lib/routing.py` | 62-67 | `startswith("INV-")` routes to investigation-cycle |
| `.claude/lib/status.py` | 819-820 | `startswith("INV-")` determines cycle_type |
| `.claude/haios/modules/portal_manager.py` | 225-226 | `startswith("INV-")` sets spawned_by_investigation |
| `.claude/lib/work_item.py` | 247 | `startswith("INV-")` (DEPRECATED but still present) |
| `.claude/haios/modules/memory_bridge.py` | 211 | Regex: `r"E2-\d+"`, `r"INV-\d+"`, `r"TD-\d+"` |
| `.claude/skills/survey-cycle/SKILL.md` | 35 | Prose: "INV-* prefix -> investigation-cycle" |
| `.claude/skills/routing-gate/SKILL.md` | 36,69,85 | Multiple INV-* references |
| `.claude/skills/implementation-cycle/SKILL.md` | 270 | "If ID starts with INV-*" |
| `.claude/skills/investigation-cycle/SKILL.md` | 152 | Same pattern |
| `.claude/skills/close-work-cycle/SKILL.md` | 72,191 | "For INV-* items" |
| `.claude/skills/work-creation-cycle/SKILL.md` | 173 | INV-* auto-chain |
| `.claude/commands/close.md` | 38,39,99,101 | INV-* specific DoD |

### H2: Spawn Logic (NOT AN ISSUE)

`scaffold.py:154-174` already generates WORK-XXX only:
```python
if subdir.name.startswith("WORK-"):
    # Only scans WORK-* directories for sequence
```

Legacy prefixes are NOT being spawned by current code. The issue is routing, not spawning.

### H3: Queue Counts

| Prefix | Total | Active | Archived/Complete |
|--------|-------|--------|-------------------|
| INV-* | 21 | 6 | 15 |
| E2-* | 41 | 3 | 38 |
| TD-* | 3 | 2 | 1 |
| WORK-* | 13 | 2 | 11 |

**Active legacy items:** INV-017, INV-019, INV-041, INV-066, INV-068, E2-236, E2-249, E2-293, TD-001, TD-002

### TRD Migration Decision (Lines 209-213, 262-266)

> - Existing `E2-XXX` and `INV-XXX` items keep their IDs (archived)
> - New items use `WORK-XXX` format
> - No renaming of historical items
> - Active E2/INV items: Keep as-is until complete, then archive

**Conclusion:** No migration needed. Let legacy items age out naturally. Focus on routing logic update.

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

- [x] Audit: List all code/skills/commands that spawn or route based on INV-* prefix
- [x] Audit: Count legacy items in queue by prefix (INV-*, E2-*, TD-*)
- [x] Decision: Migrate existing items or let them age out
- [x] Update: Modify spawn logic to use WORK-XXX + type field (N/A - already correct)
- [ ] Update: Modify routing logic to check type field, not ID prefix → **Spawned WORK-014**

---

## History

### 2026-01-25 - Created (Session 236)
- Initial creation

### 2026-01-25 - Investigation Complete (Session 238)
- Audited 12 files with prefix-based routing
- Confirmed spawn logic already uses WORK-XXX
- Decision: Let legacy items age out per TRD
- Spawned WORK-014 for routing migration implementation

---

## References

- @docs/specs/TRD-WORK-ITEM-UNIVERSAL.md (migration guidance)
- @docs/work/active/WORK-014/WORK.md (spawned implementation)
