---
id: OBS-263-003
title: Content truncation bug in ingester - 1298 concepts affected
session: 263
date: 2026-01-30
work_id: null
dimension: infrastructure
priority: high
status: pending
generated: 2026-01-30
last_updated: '2026-01-30T19:38:59'
---
# OBS-263-003: Content truncation bug in ingester - 1298 concepts affected

## What Happened

Discovered 1,298 concepts in haios_memory.db have content truncated at exactly 100 characters.

**Discovery trigger:** Reviewing Session 262 memories for BUILD phase insights - found content truncated mid-sentence.

## Root Cause Analysis

### Bug Location

**File 1:** `haios_etl/agents/ingester.py:165-168`
```python
concept_id = self.db_manager.insert_concept(
    type=concept.get("type", classification),
    name=concept.get("content", "")[:100],    # BUG: Truncates at 100
    description=concept.get("content", "")     # Full content passed here
)
```

**File 2:** `haios_etl/database.py:190-191`
```python
cursor.execute("INSERT INTO concepts (type, content, source_adr) VALUES (?, ?, ?)",
               (type, name, description))  # name -> content, description -> source_adr
```

### Data Flow

1. Ingester extracts concept with full content
2. `name` parameter gets content[:100] (TRUNCATED)
3. `description` parameter gets full content
4. Database maps:
   - `name` (truncated) → `content` column (WHAT WE QUERY!)
   - `description` (full) → `source_adr` column (wrong column - meant for ADR refs)

### Impact

- **1,298 concepts** have exactly 100 character content
- **Full content IS preserved** - just in wrong column (`source_adr`)
- Search/retrieval queries `content` column, so we search truncated data
- Memory refs show truncated snippets

## Evidence

```sql
-- Count truncated concepts
SELECT LENGTH(content) as len, COUNT(*) as cnt
FROM concepts
GROUP BY LENGTH(content)
ORDER BY cnt DESC LIMIT 1;
-- Result: len=100, cnt=1298

-- Session 262 BUILD insights example:
SELECT id, content, source_adr FROM concepts WHERE id = 82640;
-- content (truncated): "Pattern: BuildOrchestrator module that transforms plan's Detailed Design into code scaffolding (test"
-- source_adr (full): "Pattern: BuildOrchestrator module that transforms plan's Detailed Design into code scaffolding (test stubs, function signatures). Agent's role in DO phase becomes \"fill in generated skeletons\" rather than \"start from scratch.\""
```

## Fix Required

### Immediate Fix

Change `ingester.py:167` from:
```python
name=concept.get("content", "")[:100],
```
To:
```python
name=concept.get("content", ""),  # Don't truncate!
```

### Data Migration

Option A: Query `source_adr` to recover truncated concepts:
```sql
UPDATE concepts
SET content = source_adr
WHERE LENGTH(content) = 100
AND source_adr IS NOT NULL
AND LENGTH(source_adr) > 100;
```

Option B: Leave as-is, fix only new ingestions.

### Recommended

- Fix the code (prevents future truncation)
- Run migration to recover existing data (1,298 concepts)
- Verify search quality improves

## Related

- Session 262 memories lost BUILD phase details
- CH-004-builder-interface.md has full context (file preserved)
- Memory retrieval may have been returning incomplete results
