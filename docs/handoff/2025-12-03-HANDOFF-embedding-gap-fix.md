# generated: 2025-12-03
# System Auto: last updated on: 2025-12-03 22:42:16
# HANDOFF: Embedding Gap Fix

**Date:** 2025-12-03
**From:** Session 23
**Priority:** HIGH - Quick Fix

---

## Problem

- Artifacts: 728
- Embeddings: 519
- Gap: 209 (29% invisible to semantic search)

## Root Cause

Embedding generation script exists but wasn't run after recent ingestion batches.

## Solution

```bash
# Verify gap count
python scripts/generate_embeddings.py --dry-run

# Fill all missing embeddings (~21 seconds at 10 req/sec)
python scripts/generate_embeddings.py

# Verify fix
python -c "import sqlite3; c=sqlite3.connect('haios_memory.db'); print('Embeddings:', c.execute('SELECT COUNT(*) FROM embeddings').fetchone()[0])"
```

## Key Files

| File | Purpose |
|------|---------|
| `scripts/generate_embeddings.py` | Batch embedding generator |
| `haios_etl/extraction.py:304-329` | `embed_content()` method |
| `haios_etl/database.py` | `insert_embedding()` storage |

## Technical Details

- Model: `text-embedding-004`
- Dimensions: 768
- Rate limit: 10 req/sec (0.1s delay)
- Max content: 25,000 chars (truncated)
- Storage: Binary float32 BLOB

## Expected Outcome

After running: 728 artifacts = 728 embeddings (100% coverage)

---

**Status:** READY TO EXECUTE
