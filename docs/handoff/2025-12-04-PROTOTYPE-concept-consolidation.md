---
template: handoff
version: 1.0
type: prototype
date: 2025-12-04
author: Hephaestus (Builder)
status: ready
priority: high
estimated_effort: 4 hours
references:
  - "@docs/reports/2025-12-04-REPORT-multi-index-architecture.md"
  - "@docs/reports/2025-12-04-REPORT-validation-agent.md"
  - "@docs/vision/2025-11-30-VISION-INTERPRETATION-SESSION.md"
generated: 2025-12-04
last_updated: 2025-12-04T21:56:23
---

# Prototype Handoff: Concept Consolidation (Transformation MVP)

## Objective

Build the smallest possible "transformation" to prove the Epoch N -> N+1 concept works. Focus: **Consolidate duplicate concepts** - find concepts that say the same thing differently and merge them.

---

## Cold Start Context

**Read these first:**
1. `CLAUDE.md` - Project context and key reference locations
2. `docs/specs/memory_db_schema_v3.sql` - Database schema (authoritative)
3. `docs/reports/2025-12-04-REPORT-validation-agent.md` - NCCR/IUR metrics explained

**Key locations:**
| Resource | Path |
|----------|------|
| Database | `haios_memory.db` (project root) |
| Schema | `docs/specs/memory_db_schema_v3.sql` |
| ETL code | `haios_etl/` |
| Database operations | `haios_etl/database.py` |
| Embedding search | `haios_etl/extraction.py` (uses sqlite-vec) |

**Current state (as of 2025-12-04):**
| Table | Count |
|-------|-------|
| artifacts | 570 |
| embeddings | 572 |
| entities | 7,575 |
| concepts | 60,446 |

**Technical constraint:**
```
Concepts do NOT have embeddings (0 of 60,446).
Only artifacts have embeddings (572).
```

**Implication for prototype:**
Cannot use embedding similarity directly on concepts. Options:
1. **Generate concept embeddings first** (adds scope)
2. **Use text similarity** (fuzzy string matching on content)
3. **Group by artifact** (find concepts from same source, likely related)

**Recommended approach for prototype:** Option 2 or 3 (simpler, learning-focused)

**Output directory:** `output/` (for prototype artifacts)

---

## Why This Prototype

This is the simplest transformation that exercises the full pipeline:
1. **Identify** - Find candidates for consolidation
2. **Decide** - Determine merge logic
3. **Transform** - Create consolidated output
4. **Validate** - Verify quality (using NCCR/IUR concepts)

What we learn here informs what research we actually need.

---

## Scope

**In Scope:**
- Find 3-5 concept pairs that are semantically similar but textually different
- Define merge rules for this specific case
- Produce a consolidated concept
- Verify the consolidation didn't lose information

**Out of Scope:**
- Full automation (manual selection is fine)
- Entity consolidation (concepts only)
- Cross-workspace consolidation (single workspace)
- Production-ready code (learning prototype)

---

## Implementation Spec

### Step 1: Identify Candidates

**Option A: Text similarity (recommended for prototype)**
```sql
-- Find concepts with similar content (simple approach)
-- Look for exact or near-duplicate content
SELECT c1.id, c1.content, c2.id, c2.content
FROM concepts c1, concepts c2
WHERE c1.id < c2.id
  AND c1.type = c2.type  -- Same type likely to be duplicates
  AND LENGTH(c1.content) > 50  -- Skip trivial concepts
ORDER BY c1.type, c1.content
LIMIT 100;
```

**Option B: Group by source artifact**
```sql
-- Find concepts from the same artifact (likely related)
SELECT a.file_path, c.id, c.type, c.content
FROM concepts c
JOIN artifacts a ON c.source_adr LIKE '%' || a.file_path || '%'
GROUP BY a.id, c.type
HAVING COUNT(*) > 1
LIMIT 50;
```

**Manual review:** From results, pick 3-5 pairs that a human would say "these are the same idea."

### Step 2: Define Merge Rules

For each pair, answer:
- Which is the "canonical" version? (clearer, more complete)
- What information exists in the non-canonical that should be preserved?
- Should provenance (source_adr) be merged or kept separate?

**Document the decisions.** This IS the learning.

### Step 3: Execute Transformation

Create a new "consolidated concept" that:
- Uses the canonical content (possibly enhanced)
- Preserves provenance from both sources
- Links back to original concepts (DERIVED_FROM relationship)

### Step 4: Validate

Apply Validation Agent concepts (simplified):
- **Consistency check:** Ask 3 variations about the consolidated concept. Are answers stable?
- **Information preservation:** Can we still answer questions that the originals could answer?

---

## Success Criteria

- [ ] 3-5 concept pairs identified as consolidation candidates
- [ ] Merge rules documented (decisions, not just outcomes)
- [ ] At least 1 consolidated concept created
- [ ] Validation pass on consolidated concept
- [ ] **Learning document:** What did we discover about transformation?

---

## Learning Questions

This prototype should answer:

1. **How do we identify duplicates?** (Embedding similarity threshold? Manual review?)
2. **What's the merge logic?** (Keep best? Synthesize new? Preserve both with link?)
3. **What metadata matters?** (Provenance, confidence, Greek Triad classification?)
4. **What validation is sufficient?** (NCCR? Manual review? Both?)
5. **What's missing?** (This becomes the research backlog)

---

## Output Expected

1. **Consolidation log:** Which concepts, why merged, decisions made
2. **Consolidated concepts:** The actual output artifacts
3. **Validation results:** Did consolidation preserve quality?
4. **Gap analysis:** What do we now know we need to research?

---

## Connection to Vision

From VISION_ANCHOR.md:
> "We store WHAT HAPPENED, not WHAT WE LEARNED"

This prototype is the first step toward storing WHAT WE LEARNED:
- Raw concepts = what happened (extraction output)
- Consolidated concepts = what we learned (transformation output)

---

## Next Steps (After Prototype)

Based on what we learn:
- If merge logic is unclear → Research: Consolidation Patterns
- If classification is unclear → Research: Classification Patterns
- If we need more transformation types → Research: Refactoring Patterns

**Research follows gaps, not assumptions.**
