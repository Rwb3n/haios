---
template: work_item
id: E2-238
title: memory_refs Auto-Linking
status: complete
owner: Hephaestus
created: 2025-12-30
closed: '2026-01-05'
milestone: M7b-WorkInfra
priority: high
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: INV-052
blocked_by: []
blocks: []
enables: []
related:
- E2-161
- INV-052
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-30 21:40:22
  exited: null
cycle_docs: {}
memory_refs:
- 80789
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-30
last_updated: '2026-01-05T20:24:36'
---
# WORK-E2-238: memory_refs Auto-Linking

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** When `ingester_ingest` stores content to memory, the returned concept_ids are not automatically added to the source work item's `memory_refs` field. Agents must manually update WORK.md, which is error-prone and often forgotten.

**Root cause:** No PostToolUse handler detects MCP ingestion results and auto-updates work files.

**Evidence:** E2-269 observation - WHY captured to memory (80762-80771) but WORK.md memory_refs stayed empty.

**Source:** INV-052 SECTION-8-MEMORY-INTEGRATION.md gap analysis

---

## Current State

Work item in BACKLOG node. Ready for implementation.

---

## Deliverables

- [ ] PostToolUse handler: detect `ingester_ingest` tool completion
- [ ] Extract work_id from source_path (pattern: `docs/work/active/{id}/...` or `closure:{id}`)
- [ ] Call WorkEngine.add_memory_refs(work_id, concept_ids) to update WORK.md
- [ ] Handle edge cases: source_path not containing work_id, work file not found
- [ ] Tests for auto-linking logic

---

## Design Notes

**Flow (from SECTION-8):**
```
ingester_ingest(content, source_path="docs/work/active/E2-150/...")
    │
    ▼
Store concept → get concept_id
    │
    ▼
PostToolUse detects MCP ingest result
    │
    ▼
Extract work_id from source_path (E2-150)
    │
    ▼
Update WORK.md: memory_refs: [..., concept_id]
```

**Module integration:**
- MemoryBridge already has `auto_link(work_id, concept_ids)` interface
- WorkEngine has `add_memory_refs(id, concept_ids)` function
- PostToolUse hook needs handler to connect them

---

## History

### 2025-12-30 - Created (Session 151)
- Initial creation (incorrect title: "Gates Registry Config File")

### 2026-01-05 - Fixed (Session 173)
- Corrected title to "memory_refs Auto-Linking" per INV-052 SECTIONS-INDEX.md
- Added context, deliverables, design notes from SECTION-8 gap analysis
- Updated priority to high, milestone to M7b-WorkInfra

---

## References

- INV-052 SECTION-8-MEMORY-INTEGRATION.md (gap analysis source)
- INV-052 SECTION-17-MODULAR-ARCHITECTURE.md (PostToolUse handler list)
- E2-269 observations.md (evidence of gap)
- E2-161: Auto-link Documents to Work File (related but different scope)
