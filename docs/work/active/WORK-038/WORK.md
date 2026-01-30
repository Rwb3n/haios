---
template: work_item
id: WORK-038
title: Fix Content Truncation Bug in Ingester
type: implementation
status: active
owner: Hephaestus
created: 2026-01-30
spawned_by: OBS-263-003
chapter: null
arc: null
closed: null
priority: high
effort: low
traces_to:
- REQ-MEMORY-001
requirement_refs: []
source_files:
- haios_etl/agents/ingester.py
- haios_etl/database.py
acceptance_criteria:
- New ingestions store full content (no truncation)
- Existing truncated concepts recovered from source_adr
- Memory search returns full content
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-30 19:40:37
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-30
last_updated: '2026-01-30T19:41:03'
---
# WORK-038: Fix Content Truncation Bug in Ingester

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Content ingested via `ingester_ingest` is truncated at 100 characters.

**Root Cause:** In `haios_etl/agents/ingester.py:167`:
```python
name=concept.get("content", "")[:100],  # BUG: Truncates content
```

The truncated `name` is then mapped to the `content` column in the database, while the full content goes to `source_adr` (wrong column).

**Impact:**
- 1,298 concepts have exactly 100 character content
- Memory search/retrieval returns truncated snippets
- Session 262 BUILD insights lost key details
- Violates REQ-MEMORY-001 (store learnings with provenance)

**Good News:** Full content is preserved in `source_adr` column - recoverable.

---

## Deliverables

- [x] Fix `haios_etl/agents/ingester.py:167` - remove [:100] truncation
- [ ] Run data migration to recover 1,298 truncated concepts
- [ ] Verify memory search returns full content
- [ ] Add test to prevent regression

---

## Implementation Notes

### Code Fix (1 line)

`haios_etl/agents/ingester.py:167`:
```python
# Before:
name=concept.get("content", "")[:100],

# After:
name=concept.get("content", ""),
```

### Data Migration

```sql
-- Recover truncated concepts from source_adr
UPDATE concepts
SET content = source_adr
WHERE LENGTH(content) = 100
AND source_adr IS NOT NULL
AND LENGTH(source_adr) > 100;
```

### Verification

```sql
-- Should return 0 after migration
SELECT COUNT(*) FROM concepts
WHERE LENGTH(content) = 100
AND source_adr IS NOT NULL
AND LENGTH(source_adr) > 100;
```

---

## History

### 2026-01-30 - Created (Session 263)
- Discovered while reviewing Session 262 memories for BUILD phase insights
- Content truncated mid-sentence in concepts 82639-82641
- Root cause traced to ingester.py:167
- OBS-263-003 created with detailed analysis

---

## References

- @.claude/haios/epochs/E2_3/observations/OBS-263-003-content-truncation-bug-in-ingester.md
- @haios_etl/agents/ingester.py (bug location)
- @haios_etl/database.py (insert_concept mapping)
- Session 262 checkpoint (affected memories)
