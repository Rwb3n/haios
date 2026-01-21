# generated: 2026-01-18
# System Auto: last updated on: 2026-01-21T21:18:25
# Epoch 2.3: The Pipeline

## L4 Object Definition

**Epoch ID:** E2.3
**Name:** The Pipeline
**Status:** Active
**Started:** 2026-01-18 (Session 206)
**Prior:** E2.2 (The Refinement)

---

## Purpose

Build the doc-to-product pipeline that HAIOS actually is.

**The Mission:**
```
INPUT:  Corpus of documents (specs, requirements, designs)
PROCESS: Multi-agent operational framework
OUTPUT: Functional product (aligned to source specs)
```

**The Portability Test:**
> Can you drop `.claude/haios/` into a fresh workspace with a corpus of docs and have it produce a working product?

---

## What We Learned (E2.0-2.2)

### What Works

| Component | Evidence | Reuse |
|-----------|----------|-------|
| Memory system | 81k concepts, semantic search works | Direct |
| File-based provenance | 70k concepts linked to source files | Direct |
| Work item structure | WORK.md lifecycle, node_history | Adapt |
| Hooks | PreToolUse governance enforces rules | Direct |
| Session state | haios-status.json tracks cycles | Direct |
| Pressure dynamics (S20) | Inhale/exhale pattern is sound | Direct |
| Checkpoint as manifest | Loading contract works | Direct |

### What Doesn't Work

| Problem | Evidence | Fix |
|---------|----------|-----|
| Session ingestion has no provenance | Concepts 71527+ have no file link | Wire `ingester_ingest` to `concept_occurrences` |
| memory_relationships empty | 0 rows in table | Capture relationships during ingestion |
| Mode overlap | Agent builds when should pause | Explicit strategic vs tactical gates |
| WHY not traced | Decisions exist without rationale lookup | Agent must query before deciding |
| Pipeline stages don't exist | INGEST/PLAN/BUILD/VALIDATE are concepts not code | Build them |

### What Could Work Better

| Area | Current | Target |
|------|---------|--------|
| Work item IDs | E2-XXX, INV-XXX (type in prefix) | WORK-XXX (type as field) |
| Provenance | File ingestion only | All ingestion paths |
| Relationships | Not captured | Graph of concept→concept |
| Retrieval habit | Agent doesn't query before deciding | Enforce via hooks or prompts |

---

## Arcs

| Arc | Theme | Status |
|-----|-------|--------|
| **Configuration** | Object-oriented, discoverable config system | Active (CH-002, CH-003 complete) |
| **Provenance** | Fix ingestion to capture source links | Planned |
| **Pipeline** | Build INGEST→PLAN→BUILD→VALIDATE stages | Planned |
| **WorkUniversal** | Universal work item structure | Active (CH-001-004 complete) |
| **Migration** | Triage E2 artifacts, archive stale | Planned |
| **Observations** | Three-phase observation lifecycle | Active |

---

## Key Decisions (With Rationale)

| Decision | Rationale | Source |
|----------|-----------|--------|
| Graduate from E2.2 | Mission reframed - pipeline not PM | Session 206 strategic review |
| Observations at epoch level | Capture learnings with traceability | OBS-206-002 (WHY not traced) |
| Universal work items | Portability requires generic structure | S26 pipeline requirements |
| Provenance first | Can't trace WHY without source links | Session 206 analysis |
| Module-First Principle | 11 modules unused - prose bypasses code | Session 218 |
| Content Injection | Loaders inject content, not filenames | Session 218 |
| Sequential work IDs | Type as field, not prefix | Session 218 TRD approval |

---

## Architecture Foundation

**Carries forward from E2:**
- S20: Pressure Dynamics
- S22: Skill Patterns
- S26: Pipeline Architecture (new, Session 206)

**New for E2.3:**
- TRD-WORK-ITEM-UNIVERSAL (**APPROVED** Session 218)
- Provenance wiring spec (needed)
- Pipeline stage specs (needed)

**Session 218 Principles (L4 MUST):**
- **Module-First:** Commands/skills MUST call modules via cli.py, not instruct manual file reads
- **Content Injection:** Loaders MUST inject extracted content, not just filenames
- **Design Gate:** "Which module does the work? If none, why not?"

---

## Exit Criteria

- [ ] Provenance works for all ingestion paths
- [ ] Universal work item structure implemented
- [ ] At least one pipeline stage (INGEST) functional
- [ ] Portability test: plugin loads in fresh workspace

---

## References

- @.claude/haios/manifesto/L4-implementation.md (Session 206 insight)
- @.claude/haios/epochs/E2_3/observations/SESSION-206.md
- @.claude/haios/epochs/E2/EPOCH.md (prior epoch)
