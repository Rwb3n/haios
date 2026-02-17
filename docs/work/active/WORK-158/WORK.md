---
template: work_item
id: WORK-158
title: "Flat Metadata Migration and ConfigLoader"
type: feature
status: active
owner: Hephaestus
created: 2026-02-17
spawned_by: null
spawned_children: []
chapter: CH-046
arc: composability
closed: null
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
- "ConfigLoader.get_path() used for all path resolution (zero hardcoded PROJECT_ROOT / 'docs' patterns)"
- "Arc and chapter metadata stored in flat files with metadata relationships (not filesystem hierarchy)"
- "Existing arc/chapter/work queries work with flat storage"
- "17 hardcoded path patterns identified and migrated to ConfigLoader"
- "Tests for ConfigLoader path resolution"
- "No regressions in existing test suite"
blocked_by: []
blocks:
- CH-048
enables:
- CH-048
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-17T08:22:37
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.7
version: "2.0"
generated: 2026-02-17
last_updated: 2026-02-17T08:22:37
---
# WORK-158: Flat Metadata Migration and ConfigLoader

---

## Context

**Problem:** Path resolution is scattered across modules using hardcoded patterns like `PROJECT_ROOT / "docs" / "work" / "active"`. The E2.5 deferred arcs identified 17 hardcoded path patterns that should use `ConfigLoader.get_path()`. Additionally, arcs and chapters are stored as filesystem hierarchy (directories) rather than flat files with metadata relationships — the recurring E2.3 -> E2.5 -> E2.7 pattern of moving to flat + metadata.

**Root cause:** `ConfigLoader` exists and `haios.yaml` has a `paths:` section, but most code bypasses it with hardcoded `Path()` construction. Arc/chapter storage uses directory nesting (`arcs/{arc_name}/ARC.md`) instead of flat metadata-linked files.

**Evidence:** scaffold.py has `PROJECT_ROOT / "docs" / "work" / "active"` in 5+ locations. work_engine.py, validate.py, and modules have similar patterns. EPOCH.md exit criteria explicitly require "ConfigLoader used for all path resolution."

**Scope:**
1. Migrate all hardcoded path patterns to `ConfigLoader.get_path()`
2. Design flat metadata storage for arcs/chapters (may spawn investigation first)

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
- [ ] Flat metadata storage design for arcs and chapters
- [ ] Migration of existing arc/chapter files to flat storage
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
