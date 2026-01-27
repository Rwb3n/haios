---
template: work_item
id: WORK-024
title: Prune deprecated .claude/lib/ - consolidate to .claude/haios/lib/
type: investigation
status: complete
owner: Hephaestus
created: 2026-01-26
spawned_by: null
chapter: null
arc: migration
closed: '2026-01-27'
priority: high
effort: medium
traces_to: []
requirement_refs: []
source_files:
- .claude/lib/
- .claude/haios/lib/
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-26 23:22:37
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82513
- 82514
- 82515
- 82518
- 82519
- 82520
- 82521
- 82522
- 82523
- 82524
extensions: {}
version: '2.0'
generated: 2026-01-26
last_updated: '2026-01-27T00:07:43'
---
# WORK-024: Prune deprecated .claude/lib/ - consolidate to .claude/haios/lib/

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Two library locations exist causing confusion and bugs:
- `.claude/lib/` - marked DEPRECATED but still used by justfile recipes and tests
- `.claude/haios/lib/` - the target location but not consistently used

**Evidence:**
- Session 247: E2-306 plan specified wrong path, caught by critique-agent
- Session 245: Drift warning about test_governance_events.py importing from deprecated location
- 11+ justfile recipes use `.claude/lib/` pattern
- New functions (log_session_start, log_session_end) only exist in `.claude/haios/lib/`

**Impact:**
- Agent confusion about which path to use
- ImportError risk when functions exist in one location but not the other
- Technical debt accumulating

---

## Hypotheses

**H1:** The migration can be accomplished by updating import paths without functional changes.
- Rationale: Both directories contain similar modules with same interfaces
- Test: Compare function signatures between duplicate files

**H2:** A compatibility shim in `.claude/lib/__init__.py` can enable gradual migration.
- Rationale: Memory concept 82252 mentions "Compatibility shims with try/except re-exports enable gradual consumer migration"
- Test: Check if shim already exists

**H3:** Some files in `.claude/lib/` have no equivalent in `.claude/haios/lib/` and need copying.
- Rationale: Initial glob shows unequal file counts (30 vs 28)
- Test: Compare file lists to identify orphans

---

## Scope

**In Scope:**
- Inventory justfile recipes using deprecated path
- Inventory test files importing from deprecated path
- Identify unique files in each location
- Produce migration work items

**Out of Scope:**
- Actual migration (spawned work items)
- Blocking legacy ID patterns (separate concern)

---

## Deliverables

- [x] Inventory all consumers of `.claude/lib/` (justfile, tests, imports)
- [x] Inventory function differences between the two locations
- [x] Create migration plan (spawn work items for each migration step)
- [ ] ~~Block legacy ID patterns (E2-XXX, INV-XXX) in scaffold command~~ (removed - out of scope)

**Spawned Work Items:**
- WORK-025: Delete stale .claude/lib/*.py files
- WORK-026: Update justfile recipes
- WORK-027: Update test imports

---

## Exploration Plan

- [x] List files in `.claude/lib/`
- [x] List files in `.claude/haios/lib/`
- [x] Grep justfile for `.claude/lib/` imports
- [x] Grep tests for `.claude/lib/` imports
- [x] Check `.claude/lib/__init__.py` for compatibility shim
- [x] Compare function signatures in duplicate files
- [x] Identify migration order (dependencies)

---

## Findings

### F1: File Inventory (Session 249)

| Location | Count | Notable |
|----------|-------|---------|
| `.claude/lib/` | 30 files | Original location |
| `.claude/haios/lib/` | 28 files | Newer location |

**Files ONLY in `.claude/haios/lib/`:**
- `identity_loader.py` - coldstart identity loading
- `session_loader.py` - coldstart session loading
- `work_loader.py` - coldstart work loading
- `loader.py` - base loader class
- `coldstart_orchestrator.py` - orchestrates loaders

**Files ONLY in `.claude/lib/`:**
- `validate.py` - file validation
- `scaffold.py` - template scaffolding
- (Need to verify: `routing.py` may differ)

### F2: Justfile Consumers (Session 249)

**13 recipes using `.claude/lib/`:**
1. `obs-validate` - observations.validate_observations
2. `obs-scaffold` - observations.scaffold_observations
3. `obs-uncaptured` - observations.scan_uncaptured_observations
4. `obs-archived` - observations.scan_archived_observations
5. `obs-triage` - observations.mark_triaged
6. `gov-metrics` - governance_events.get_governance_metrics
7. `status-full` - status.generate_full_status
8. `status-debug` - status.generate_full_status
9. `status-slim` - status.generate_slim_status
10. `milestone` - reads haios-status-slim.json (indirect)
11. `audit-sync` - audit.audit_sync
12. `audit-gaps` - audit.audit_gaps
13. `audit-stale` - audit.audit_stale

**5 recipes using `.claude/haios/lib/`:**
1. `load-identity` - identity_loader
2. `load-session` - session_loader
3. `load-work` - work_loader
4. `session-start` - governance_events.log_session_start
5. `session-end` - governance_events.log_session_end

### F3: Test File Consumers (Session 249)

**20+ test files import from `.claude/lib/`:**
- test_governance_events.py (both paths)
- test_governance_layer.py
- test_config.py
- test_exit_gates.py
- test_error_capture.py
- test_backfill.py
- test_dependencies.py
- test_lib_spawn.py (11 occurrences)
- test_lib_scaffold.py
- test_lib_validate.py
- test_lib_status.py
- test_lib_retrieval.py
- test_lib_database.py
- test_lib_cascade.py
- test_lib_audit.py
- test_node_cycle.py
- test_observations.py
- test_work_item.py
- test_ground_truth_parser.py
- test_routing_gate.py

### F4: Memory Evidence (Session 249)

From memory search:
- **82459:** "Must use canonical .claude/haios/lib/ path, not deprecated .claude/lib/"
- **82246:** "Migration establishes .claude/haios/lib/ as the canonical location for new code"
- **82481:** "This is temporary inconsistency - .claude/lib is deprecated."
- **81124:** "PORTABILITY BROKEN: All modules import from .claude/lib/. Copying .claude/haios/ to another project fails."

### F5: Compatibility Shim Analysis (Session 249)

**Shim exists:** `.claude/lib/__init__.py` (WORK-006, Session 221)
- Emits `DeprecationWarning` on import
- Adds `.claude/haios/lib/` to `sys.path`
- Re-exports 16 modules via `from X import *`

**CRITICAL BUG:** Shim doesn't work for `sys.path.insert` pattern!

```python
# This pattern (used by 13+ justfile recipes) BYPASSES the shim:
sys.path.insert(0, '.claude/lib')
from governance_events import X  # Loads STALE .claude/lib/governance_events.py
```

**Evidence:** `log_session_start()` exists in `.claude/haios/lib/governance_events.py` but NOT in `.claude/lib/governance_events.py`. The stale file masks the shim's re-export.

### F6: File Comparison Results (Session 249)

| File | .claude/lib/ | .claude/haios/lib/ | Status |
|------|-------------|-------------------|--------|
| governance_events.py | Missing E2-236 functions | Has log_session_start, log_session_end, detect_orphan_session, scan_incomplete_work | DIVERGED |
| observations.py | Same functions | Same functions | PATH ONLY |
| status.py | INV-* prefix only | Uses `type` field (WORK-014) | DIVERGED |

### F7: Hypothesis Verdicts (Session 249)

**H1: Migration can be path-only** - PARTIALLY CONFIRMED
- Some files (observations.py) are identical except path
- Other files (governance_events.py, status.py) have diverged functionality

**H2: Compatibility shim enables gradual migration** - REFUTED
- Shim only works for `import lib` pattern
- `sys.path.insert` pattern (used by justfile) bypasses shim
- Stale `.py` files mask shim re-exports

**H3: Some files have no equivalent** - CONFIRMED
- 5 files only in `.claude/haios/lib/` (loaders, orchestrator)
- These are new additions, not migration gaps

---

## History

### 2026-01-27 - Session 249 CONCLUDE
- Investigation complete
- Spawned: WORK-025, WORK-026, WORK-027
- Stored findings to memory: 82513, 82514, 82515
- Critical finding: shim doesn't work for sys.path.insert pattern

### 2026-01-27 - Session 249 EXPLORE
- Ran investigation-agent for file comparison
- Discovered shim bypass bug
- Identified migration order

### 2026-01-27 - Session 249 HYPOTHESIZE
- Read all @ references
- Queried memory for prior context
- Completed file inventory (both directories)
- Completed consumer inventory (justfile + tests)
- Memory refs: 82459, 82246, 82481, 81124, 82252

### 2026-01-26 - Created (Session 247)
- Pattern keeps causing issues - time to fix systematically
- Operator requested investigation for next session

---

## References

- @docs/work/active/E2-306/observations.md (critique-agent findings)
- Memory: 82459, 82246, 82481, 81124, 82252
