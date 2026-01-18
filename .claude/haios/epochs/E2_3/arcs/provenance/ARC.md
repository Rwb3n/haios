# generated: 2026-01-18
# System Auto: last updated on: 2026-01-18T16:51:08
# Arc: Provenance

## Arc Definition

**Arc ID:** Provenance
**Epoch:** E2.3 (The Pipeline)
**Name:** Source Traceability
**Status:** Planned
**Pressure:** [volumous] - thematic exploration

---

## Theme

Fix ingestion to capture source links. Every concept must trace back to its origin.

**The Problem:**
- File ingestion populates `concept_occurrences` (70k linked)
- Session ingestion via `ingester_ingest` does NOT (10k unlinked)
- `memory_relationships` is empty (no concept→concept graph)

**The Goal:**
```
Concept → Artifact (file) → Line number
Concept → Concept (relationship)
Decision → Rationale (WHY)
```

---

## Chapters

| Chapter | Name | Status | Purpose |
|---------|------|--------|---------|
| CH-001 | IngesterProvenance | Planned | Wire `ingester_ingest` to create artifact + occurrence |
| CH-002 | RelationshipCapture | Planned | Populate `memory_relationships` during ingestion |
| CH-003 | RationaleLink | Planned | Decision concepts link to Rationale concepts |

---

## Evidence

| Finding | Source |
|---------|--------|
| Concepts 71527+ have no occurrences | Session 206 DB query |
| memory_relationships has 0 rows | Session 206 DB query |
| 70,920 occurrences exist (file ingestion works) | Session 206 DB query |

---

## Exit Criteria

- [ ] `ingester_ingest` creates artifact and occurrence records
- [ ] All new concepts have provenance
- [ ] Relationship types defined and populated

---

## References

- @.claude/haios/epochs/E2_3/observations/SESSION-206.md (OBS-206-002)
- @docs/specs/memory_db_schema_v3.sql
