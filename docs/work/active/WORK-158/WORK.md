---
template: work_item
id: WORK-158
title: ConfigLoader Path Migration
type: feature
status: complete
owner: Hephaestus
created: 2026-02-17
spawned_by: null
spawned_children: []
chapter: CH-046
arc: composability
closed: '2026-02-17'
priority: high
effort: large
traces_to:
- REQ-CONFIG-001
- REQ-CONFIG-003
requirement_refs: []
source_files:
- .claude/haios/config/haios.yaml
- .claude/haios/lib/scaffold.py
- .claude/haios/modules/work_engine.py
acceptance_criteria:
- ConfigLoader.get_path() used for all path resolution (zero hardcoded PROJECT_ROOT
  / 'docs' patterns)
- All hardcoded path patterns identified via audit (grep for PROJECT_ROOT /)
- Each pattern migrated to ConfigLoader.get_path() with appropriate key
- New path keys added to haios.yaml paths section as needed
- Tests for ConfigLoader path resolution
- No regressions in existing test suite
blocked_by: []
blocks:
- CH-048
enables:
- CH-048
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-17 08:22:37
  exited: '2026-02-17T19:45:44.719932'
artifacts: []
cycle_docs: {}
memory_refs:
- 85463
- 85802
- 85803
- 85804
- 85805
extensions:
  epoch: E2.7
version: '2.0'
generated: 2026-02-17
last_updated: '2026-02-17T19:45:44.722934'
queue_history:
- position: ready
  entered: '2026-02-17T19:25:55.303645'
  exited: '2026-02-17T19:25:55.331963'
- position: working
  entered: '2026-02-17T19:25:55.331963'
  exited: '2026-02-17T19:45:44.719932'
- position: done
  entered: '2026-02-17T19:45:44.719932'
  exited: null
---
# WORK-158: Flat Metadata Migration and ConfigLoader

---

## Context

**Problem:** Path resolution is scattered across modules using hardcoded patterns like `PROJECT_ROOT / "docs" / "work" / "active"`. The E2.5 deferred arcs identified 17 hardcoded path patterns that should use `ConfigLoader.get_path()`. Additionally, arcs and chapters are stored as filesystem hierarchy (directories) rather than flat files with metadata relationships — the recurring E2.3 -> E2.5 -> E2.7 pattern of moving to flat + metadata.

**Root cause:** `ConfigLoader` exists and `haios.yaml` has a `paths:` section, but most code bypasses it with hardcoded `Path()` construction. Arc/chapter storage uses directory nesting (`arcs/{arc_name}/ARC.md`) instead of flat metadata-linked files.

**Evidence:** scaffold.py has `PROJECT_ROOT / "docs" / "work" / "active"` in 5+ locations. work_engine.py, validate.py, and modules have similar patterns. EPOCH.md exit criteria explicitly require "ConfigLoader used for all path resolution."

**Scope (narrowed S393):**
1. Audit all hardcoded path patterns (grep for PROJECT_ROOT /)
2. Migrate each pattern to ConfigLoader.get_path()
3. Add missing path keys to haios.yaml paths section

**Out of scope (spawned separately):**
- Flat metadata storage for arcs/chapters (investigation needed first)

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

- [ ] Audit of all hardcoded path patterns (grep for `PROJECT_ROOT /`)
- [ ] All paths migrated to `ConfigLoader.get_path()` calls
- [ ] New path keys added to haios.yaml as needed
- [ ] Tests for ConfigLoader path resolution
- [ ] No regressions in existing test suite

---

## History

### 2026-02-17 - Created (Session 392)
- Spawned from CH-046 FlatMetadataMigration (composability arc, E2.7)
- REQ-CONFIG-001, REQ-CONFIG-003 traceability
- Unblocks CH-048 RecipeRationalization

---

## References

- @.claude/haios/epochs/E2_7/arcs/composability/ARC.md
- @.claude/haios/epochs/E2_7/EPOCH.md
- @.claude/haios/config/haios.yaml
- @.claude/haios/manifesto/L4/functional_requirements.md
