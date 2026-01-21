---
template: work_item
id: WORK-006
title: Migrate .claude/lib to portable plugin directory
type: chore
status: complete
owner: Hephaestus
created: 2026-01-21
spawned_by: null
chapter: null
arc: migration
closed: '2026-01-21'
priority: high
effort: medium
requirement_refs: []
source_files:
- .claude/haios/epochs/E2_3/observations/obs-219-001.md
- .claude/haios/epochs/E2_3/arcs/migration/ARC.md
acceptance_criteria: []
blocked_by: []
blocks:
- WORK-005
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-21 19:29:51
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82252
- 65046
- 65047
- 65048
- 65049
- 82253
- 82254
- 82255
extensions: {}
version: '2.0'
generated: 2026-01-21
last_updated: '2026-01-21T19:32:48'
---
# WORK-006: Migrate .claude/lib to portable plugin directory

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** `.claude/lib/` contains 23 Python modules that live outside the portable plugin directory (`.claude/haios/`). This breaks the portability test: "Can you drop `.claude/haios/` into a fresh workspace and have it work?"

**Root cause:** Historical growth - lib modules were created before the portable plugin structure was defined. Now `.claude/haios/modules/` uses `sys.path` manipulation to import from `.claude/lib/`, creating an external dependency.

**Evidence (Session 220 Ground Truth):**
- `.claude/lib/` has 23 Python files
- `.claude/haios/modules/governance_layer.py` imports `scaffold` via sys.path
- `.claude/hooks/hooks/pre_tool_use.py` imports `node_cycle`
- `.claude/hooks/hooks/post_tool_use.py` imports `validate`, `status`, `node_cycle`

**Impact:**
- Plugin is not portable (depends on external lib/)
- Import path confusion (which lib?)
- New code in `.claude/haios/lib/` vs old in `.claude/lib/` creates drift

**Spawned from:** obs-219-001 (Session 219)

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

- [ ] Move 23 Python modules from `.claude/lib/` to `.claude/haios/lib/`
- [ ] Update all imports in `.claude/haios/modules/` (governance_layer.py imports scaffold)
- [ ] Update all imports in `.claude/hooks/hooks/` (pre_tool_use.py, post_tool_use.py)
- [ ] Create `__init__.py` in `.claude/haios/lib/`
- [ ] Remove sys.path manipulation from modules (use relative imports)
- [ ] Leave compatibility shims in `.claude/lib/` (re-export from new location)
- [ ] Verify all tests pass after migration
- [ ] Update `.claude/haios/lib/README.md` documenting migrated modules
- [ ] Remove old `.claude/lib/` after verification (or mark deprecated)

---

## History

### 2026-01-21 - Created (Session 220)
- Initial creation
- Populated from obs-219-001 via work-creation-cycle
- Marked as blocking WORK-005 (loader.py location depends on migration decision)

---

## References

- @.claude/haios/epochs/E2_3/observations/obs-219-001.md (spawning observation)
- @.claude/haios/epochs/E2_3/arcs/migration/ARC.md (arc context)
- @.claude/haios/manifesto/L4-implementation.md (Module-First principle)
- Session 219 checkpoint (memory_refs: 82230-82242)
