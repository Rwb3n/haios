# generated: 2026-02-14
# System Auto: last updated on: 2026-02-14T01:20:00
# Epoch 2.7: Composability

## L4 Object Definition

**Epoch ID:** E2.7
**Name:** Composability
**Status:** Future
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

## Scope

### Work Items Assigned

| ID | Title | Theme |
|----|-------|-------|
| WORK-034 | Upstream Status Propagation | Engine function: cascade on closure |
| WORK-093 | Implement Lifecycle Asset Types | Composable typed outputs |
| WORK-071 | Pre-Decomposition Review Gate | Composable review gate |

### Anticipated Work

| Theme | Description |
|-------|-------------|
| Flat metadata migration | Arcs/chapters as flat files with frontmatter relationships |
| Engine query functions | get_arcs(epoch=), get_chapters(arc=), get_work(chapter=) |
| Recipe rationalization | 71 recipes grouped, aliased, composed |
| ConfigLoader adoption | All 17 hardcoded paths migrated |
| Status cascade engine | close-work cascades to chapter/arc/epoch automatically |

---

## Exit Criteria

- [ ] Arcs and chapters stored flat with metadata relationships
- [ ] Engine functions for hierarchy queries (no manual path resolution)
- [ ] Status cascades automatically on work/chapter/arc closure
- [ ] Lifecycle asset types implemented with typed I/O
- [ ] ConfigLoader used for all path resolution (zero hardcoded paths)
- [ ] Recipe surface area rationalized (grouped, documented, composable)

---

## References

- @.claude/haios/epochs/E2_6/EPOCH.md (prior epoch)
- @.claude/haios/epochs/E2_8/EPOCH.md (next epoch)
- @docs/work/active/WORK-034/WORK.md (status propagation)
- @docs/work/active/WORK-093/WORK.md (lifecycle assets)
