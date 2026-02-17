# generated: 2026-02-14
# System Auto: last updated on: 2026-02-16T19:05:00
# Epoch 2.7: Composability

## L4 Object Definition

**Epoch ID:** E2.7
**Name:** Composability
**Status:** Complete
**Started:** 2026-02-16 (Session 382)
**Completed:** 2026-02-17 (Session 393)
**Prior:** E2.6 (Foundations)
**Next:** E2.8 (Agent UX)

---

## Purpose

Make the system's building blocks composable. Flat storage with metadata relationships replaces filesystem hierarchy. Engine functions replace manual file reads. Recipes become thin wrappers over callable functions.

**The Mission:**
```
Hierarchy in metadata, not directories.
Functions over file reads.
Compose, don't concatenate.
```

**Depends on E2.6:** Discoverability infrastructure tells us what exists. Composability makes those things work together.

---

## What We Carry Forward

### From E2.6 (Foundations)
- Agent Cards for all agents (discoverability)
- L4 traceability verified
- Legacy duplication resolved
- MUST gate logging operational

### Recurring Pattern (E2.3 -> E2.5 -> E2.7)
| Epoch | What Moved to Flat + Metadata |
|-------|-------------------------------|
| E2.3 | Work items |
| E2.5 | Queue position |
| **E2.7** | **Arcs, chapters, epoch hierarchy** |

### From E2.5 Deferred Arcs
- **Portability** — ConfigLoader for all paths (17 hardcoded identified)
- **Assets** — Typed lifecycle outputs (Findings, Specification, Artifact, Verdict, PriorityList)

---

## Arcs (Decomposed S384)

### Arc 1: engine-functions — "Functions over file reads" (COMPLETE - S393)

| CH-ID | Title | Work Items | Status |
|-------|-------|------------|--------|
| CH-044 | HierarchyQueryEngine | WORK-157 | Complete |
| CH-045 | StatusCascade | WORK-034 | Complete |

### Arc 2: composability — "Compose, don't concatenate" (COMPLETE - S393)

| CH-ID | Title | Work Items | Status |
|-------|-------|------------|--------|
| CH-046 | FlatMetadataMigration | WORK-158 | Complete |
| CH-047 | TemplateComposability | WORK-152, WORK-155 | Complete |
| CH-048 | RecipeRationalization | WORK-159 | Complete |

### Arc 3: infrastructure — "Clean the house first"

| CH-ID | Title | Work Items | Status |
|-------|-------|------------|--------|
| CH-049 | BugBatch | WORK-153 | Complete |
| CH-050 | EpochTransition | WORK-154 | Complete |
| CH-051 | StalenessDetection | WORK-136, WORK-156 | Complete |

### Deferred to E2.9 (Governance)

| ID | Title | Rationale |
|----|-------|-----------|
| WORK-071 | Pre-Decomposition Review Gate | Governance-themed, not composability |
| WORK-101 | Proportional Governance Design | Governance-themed, not composability |
| WORK-102 | Session/Process Review Ceremonies | Governance-themed, not composability |

### Completed (carry-forward satisfied)

| ID | Title | Notes |
|----|-------|-------|
| WORK-093 | Implement Lifecycle Asset Types | Closed 2026-02-15, typed I/O exit criterion satisfied |

---

## Exit Criteria

- [~] Arcs and chapters stored flat with metadata relationships — DEFERRED to E2.8 (architectural investigation needed)
- [x] Engine functions for hierarchy queries (Arc 1: CH-044, WORK-157 closed S393)
- [x] Status cascades automatically on work/chapter/arc closure (Arc 1: CH-045, WORK-034 closed S386)
- [x] Lifecycle asset types implemented with typed I/O (WORK-093, closed 2026-02-15)
- [x] ConfigLoader used for all path resolution (Arc 2: CH-046, WORK-158 closed S393)
- [x] Recipe surface area rationalized (Arc 2: CH-048, WORK-159 closed S393)
- [x] Known bugs from E2.6 triage resolved (Arc 3: CH-049, WORK-153 closed S384)
- [x] Epoch transition validation operational (Arc 3: CH-050, WORK-154 closed S385)

---

## References

- @.claude/haios/epochs/E2_6/EPOCH.md (prior epoch)
- @.claude/haios/epochs/E2_8/EPOCH.md (next epoch)
- @.claude/haios/epochs/E2_7/arcs/engine-functions/ARC.md
- @.claude/haios/epochs/E2_7/arcs/composability/ARC.md
- @.claude/haios/epochs/E2_7/arcs/infrastructure/ARC.md
- @docs/work/active/WORK-034/WORK.md (status propagation)
- @docs/work/active/WORK-093/WORK.md (lifecycle assets — complete)
- @docs/work/active/WORK-136/WORK.md (staleness detection)
- @docs/work/active/WORK-152/WORK.md (plan template fracturing)
- @docs/work/active/WORK-153/WORK.md (bug batch)
- @docs/work/active/WORK-154/WORK.md (epoch transition)
- @docs/work/active/WORK-155/WORK.md (lifecycle type-awareness)
- @docs/work/active/WORK-157/WORK.md (hierarchy query engine)
- @docs/work/active/WORK-158/WORK.md (ConfigLoader path migration)
- @docs/work/active/WORK-159/WORK.md (recipe rationalization)
