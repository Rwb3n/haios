---
template: architecture_decision_record
status: accepted
date: 2026-01-15
adr_id: ADR-042
title: Hierarchy Rename Chapter to Arc
author: Hephaestus
session: 191
lifecycle_phase: decide
decision: accepted
spawned_by: INV-064
memory_refs:
- 81366
- 81367
version: '1.1'
generated: 2026-01-15
last_updated: '2026-01-15T19:48:47'
---
# ADR-042: Hierarchy Rename Chapter to Arc

@docs/README.md
@docs/work/active/INV-064/investigations/001-work-hierarchy-rename-and-queue-architecture.md

> **Status:** Accepted
> **Date:** 2026-01-15
> **Decision:** Approved (Session 191)

---

## Context

Current HAIOS hierarchy naming (Epoch → Chapter → Arc → Work Item) inverts universal storytelling semantics. Investigation INV-064 confirmed:

- In TV, manga, books: **arcs span multiple chapters**
- Wikipedia: "Series of 30+ chapters usually have multiple arcs"
- HAIOS has chapters containing arcs (inverted)

This creates cognitive dissonance for anyone familiar with narrative structures.

---

## Decision Drivers

- Universal story semantics: arcs > chapters in containment hierarchy
- Cognitive load reduction for humans and LLMs
- Pressure pattern must be preserved (alternating [volumous]/[tight])
- ~15 files need updates - manageable migration

---

## Considered Options

### Option A: Keep Current Naming
**Description:** Maintain Epoch → Chapter → Arc → Work Item

**Pros:**
- No migration work
- Existing docs/code unchanged

**Cons:**
- Semantic inversion persists
- Cognitive load remains
- Counter to universal convention

### Option B: Swap Chapter ↔ Arc
**Description:** Rename to Epoch → Arc → Chapter → Work Item

**Pros:**
- Aligns with universal story semantics
- Reduces cognitive load
- Pressure pattern preserved (just label swap)

**Cons:**
- ~15 files need updates
- Config keys change
- One-time migration effort

---

## Decision

**Adopt Option B: Swap Chapter ↔ Arc**

The hierarchy becomes:

```
CURRENT: Epoch [tight] → Chapter [volumous] → Arc [tight] → Work Item [volumous]
    ↓
PROPOSED: Epoch [tight] → Arc [volumous] → Chapter [tight] → Work Item [volumous]
```

The pressure alternation is preserved. Only terminology aligns with universal understanding.

---

## Consequences

**Positive:**
- Universal semantic alignment
- Reduced cognitive load
- Easier onboarding for new agents/operators

**Negative:**
- One-time migration effort (~15 files)
- Config keys change (active_chapters → active_arcs)

**Neutral:**
- Pressure dynamics unchanged
- Hierarchy depth unchanged

---

## Implementation

- [ ] E2-289: Execute hierarchy rename (spawned by INV-064)
  - Rename `chapters/` → `arcs/`
  - Rename `CHAPTER.md` → `ARC.md` (6 files)
  - Rename nested `arcs/` → `chapters/`
  - Update config keys in haios.yaml
  - Update architecture docs (EPOCH.md, S20, L4, etc.)
- [ ] Update memory search patterns (if any hardcoded)
- [ ] Test that coldstart loads correctly after rename

---

## References

- INV-064: Work Hierarchy Rename and Queue Architecture (source investigation)
- Memory 81366-81367: Investigation findings
- S20: Pressure Dynamics (pattern preserved)
- Session 179: Original hierarchy decision (superseded by this ADR)
