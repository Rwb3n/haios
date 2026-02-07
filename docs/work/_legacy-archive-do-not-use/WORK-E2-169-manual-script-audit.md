---
template: work_item
id: E2-169
title: "Manual Script Audit"
status: complete
owner: Hephaestus
created: 2025-12-24
closed: 2025-12-24
milestone: M7a-Recipes
priority: medium
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: implement
node_history:
  - node: implement
    entered: 2025-12-24T18:46:00
    exited: null
  - node: implement
    entered: 2025-12-24T18:46:00
    exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: "1.0"
generated: 2025-12-24
last_updated: 2025-12-24T18:48:44
---
# WORK-E2-169: Manual Script Audit

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Various operations still require direct Python script invocations. Not all discoverable via `just --list`.

**Solution:** Audit all manual scripts and convert to just recipes.

---

## Current State

Audit complete (Session 113). Findings documented below.

---

## Deliverables

- [x] Audit: Find all `python -m ...` and `python scripts/...` in docs, commands, hooks
- [x] List: Categorize by priority (frequently used vs rare)
- [x] Convert: Added 6 just recipes for high-priority items (Session 113)
- [x] Document: Findings documented in this work file (OPERATIONS.md update deferred)

---

## Audit Findings (Session 113)

### Already Have Just Recipes (Good)
| Operation | Recipe | Source |
|-----------|--------|--------|
| Validate template | `just validate <file>` | .claude/lib/validate.py |
| Scaffold document | `just scaffold <type> <id> <title>` | .claude/lib/scaffold.py |
| Update status | `just update-status` | .claude/lib/status.py |
| Cascade status | `just cascade <id> <status>` | .claude/lib/cascade.py |
| Backfill work | `just backfill <id>` | .claude/lib/backfill.py |
| Synthesis run | `just synthesis` | haios_etl.cli |
| Synthesis stats | `just synthesis-status` | haios_etl.cli (E2-168) |
| Synthesis full | `just synthesis-full` | haios_etl.cli (E2-168) |
| ETL status | `just status` | haios_etl.cli |
| Process corpus | `just process` | haios_etl.cli |
| Tests | `just test` | pytest |
| Memory stats | `just memory-stats` | haios_etl.database |
| Events | `just events` | haios-events.jsonl |
| Plan tree | `just tree`, `just ready` | scripts/plan_tree.py |
| Spawn tree | `just spawns <id>` | .claude/lib/spawn.py |

### HIGH PRIORITY - Need Recipes
| Script | Current Invocation | Proposed Recipe |
|--------|-------------------|-----------------|
| Ingest files | `python -m haios_etl.cli ingest <path>` | `just ingest <path>` |
| Embedding backfill | `python scripts/backfill_synthesis_embeddings.py` | `just embeddings-backfill` |
| Generate embeddings | `python scripts/generate_embeddings.py` | `just embeddings-generate` |
| Migrate backlog | `python scripts/migrate_backlog.py` | `just migrate-backlog` |

### MEDIUM PRIORITY - Occasional Use
| Script | Current Invocation | Notes |
|--------|-------------------|-------|
| Check status | `python scripts/check_status.py` | Maybe redundant with `just status` |
| Query progress | `python scripts/query_progress.py` | Historical ETL progress |
| Archive backlog | `python scripts/archive_completed_backlog.py` | One-time migration use |

### LOW PRIORITY - Debugging/One-Time
| Script | Purpose |
|--------|---------|
| apply_migration*.py | One-time schema migrations |
| investigate_*.py | Ad-hoc debugging |
| debug_extraction.py | Development debugging |
| load_test.py | Performance testing |
| benchmark_toon.py | TOON format benchmarking |

### Justfile Pattern Analysis
Current justfile uses `python -c "import sys; sys.path.insert(0, '.claude/lib'); ..."` pattern extensively.
This works but is verbose. Consider a wrapper script for cleaner invocations.

---

## History

### 2025-12-24 - Audit Complete (Session 113)
- Grepped docs/, commands/, hooks/, justfile for python invocations
- Found 20+ scripts in scripts/
- Categorized by priority: 4 HIGH, 3 MEDIUM, 6+ LOW
- Key gap: `just ingest` missing (frequently documented but no recipe)

### 2025-12-24 - Created (Session 105)
- Initial creation

---

## References

- E2-168: Synthesis Just Recipes (completed, added synthesis-status/synthesis-full)
- E2-167: Git Just Recipes (pending)
- E2-143: Audit Recipe Suite (pending)
