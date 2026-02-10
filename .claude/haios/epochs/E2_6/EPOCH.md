# generated: 2026-02-10
# System Auto: last updated on: 2026-02-10T22:36:00
# Epoch 2.6: Agent UX

## L4 Object Definition

**Epoch ID:** E2.6
**Name:** Agent UX
**Status:** Planning
**Started:** TBD
**Prior:** E2.5 (Independent Lifecycles)

---

## Purpose

Reduce agent cognitive overhead by replacing filesystem-hierarchy-driven governance with metadata-driven, function-callable governance. The agent should spend tokens on work, not bookkeeping.

**The Mission:**
```
Less file reading, more function calling.
Flat storage, metadata relationships.
Composable, configurable, discoverable.
```

**The Paradigm Shift:**
- From: Hierarchy encoded in filesystem (epochs/E2_5/arcs/ceremonies/CH-012.md)
- To: Hierarchy encoded in metadata (flat files, frontmatter relationships, engine queries)

---

## What We Learned (E2.5)

### Session 339 Retrospective Findings

#### What Went Well (Carry Forward)
| Pattern | Evidence | Sessions |
|---------|----------|----------|
| Critique agent before every DO | Caught 3-10 genuine issues per review | 332-336 |
| TDD RED-GREEN = zero-debug | 15/15, 19/19, 17/17, 13/13 first pass | 317-338 |
| Plan(sonnet) + critique(haiku) | Cost-efficient model allocation | 317+ |
| Operator retros at phase boundaries | Early issue detection | 314, 332 |
| Structured bug capture -> batch fix | 4 bugs in ~15 min | 330 |
| Critique-then-defer | Traceability without scope creep | 333-334 |
| Pure additive hook extension | Cleanest integration pattern found | 335 |
| stub:true frontmatter | Prevents agents treating stubs as functional | 333 |

#### Could've Gone Better (Address in E2.6)
| Issue | Evidence | Proposed Fix |
|-------|----------|-------------|
| Test infra: _load_module fragility | ContextVar divergence (84783-84795) | WORK-117 (conftest.py unification) |
| Checkpoint prior_session stale | Scaffolds wrong value (84276, 84799) | Fix in scaffold.py |
| Template {{TYPE}} unsubstituted | No scaffold output lint (obs-330) | Add lint test |
| stage-governance recipe stale | Missing skill/command dirs (obs-330) | Update justfile |
| MUST gates skipped without logging | 3 instances across 3 sessions | Gate skip logging |
| Ceremony overhead disproportionate | ~40% tokens governance vs ~30% impl (84332) | Proportional governance |
| Closure doesn't cascade to parents | Chapter/arc status stale (84215, 84255) | Status cascade |
| Chapter files do double-duty | Design spec + status tracker (84227) | Separate concerns |
| Coldstart shows wrong epoch | Identity loader bug (84245) | Fix identity_loader |
| Greek Triad taxonomy dead | 0 doxa, 14 episteme (all old), auto-classifier diverged | Investigate or accept |

#### Stop Doing
| Anti-pattern | Evidence |
|-------------|----------|
| Reading mutable state for computable values | session-start non-idempotent bug |
| Over-investigating known bugs | Broad grep when source file known |
| Skipping MUST gates without logging | 3 instances (84265, 84271, 84330) |
| Working outside governance cycles | S333 governance bypass irony |
| Letting chapter status rot | 4 queue chapters showed Planned despite Complete |

#### Start Doing
| Practice | Rationale |
|----------|-----------|
| Scaffold output lint | Assert no {{ remains after scaffold |
| Auto-detect missing plan | Route to plan-authoring if no plan exists |
| Gate skip logging | Log to governance-events.jsonl on MUST violation |
| Status cascade on closure | close-work -> update chapter; close-chapter -> update arc |
| just chapter-status {arc} | Quick chapter completion view |

### E2.5 Scope Lessons

| Observation | Detail |
|-------------|--------|
| **Epoch scope inflation** | 6 arcs scoped at creation, 2 completed, 1 in progress, 3 never started |
| **No mid-epoch scope trim** | No formal mechanism to adjust scope after creation |
| **Arc carryover undefined** | Unfinished arcs sit as "Planned" with no deferral ceremony |
| **Missing ceremonies** | Session Review, Process Review, Batch Scope Triage, System Evolution - all operator-initiated, top-down |

---

## Core Architecture Decision: Flat Storage + Metadata Relationships

### The Pattern (Recurring)

| Epoch | What Moved | From | To |
|-------|-----------|------|-----|
| E2.3 | Work items | Nested directories | Flat + metadata |
| E2.5 queue | Queue position | Filesystem location (active/ vs archive/) | queue_position: frontmatter |
| **E2.6** | **Arcs, chapters** | **Filesystem hierarchy** | **Flat directories + metadata** |

### Proposed Structure

```
Current (hierarchy in filesystem):
  epochs/E2_5/
    arcs/
      ceremonies/
        CH-011.md
        CH-012.md
    observations/

Proposed (hierarchy in metadata):
  epochs/
    E2_5.md               # epoch definition
    E2_6.md
  arcs/
    ceremonies.md          # arc: epoch: E2.5 in frontmatter
    feedback.md            # arc: epoch: E2.6 (re-assigned, no file move)
    agent-ux.md            # new arc
  chapters/
    CH-011.md              # chapter: arc: ceremonies in frontmatter
    CH-012.md
  work/                    # already flat
    WORK-111/
    WORK-117/
```

### What This Enables

| Capability | Current | With Flat + Metadata |
|------------|---------|---------------------|
| Move arc between epochs | Move files between directories | Change `epoch:` in frontmatter |
| Park an arc | No mechanism | `status: parked` in frontmatter |
| Find all arcs for epoch | Directory listing | Query: `arc.epoch == E2.5` |
| Agent resolves chapter | Read nested path | `get_chapters(arc="ceremonies")` |
| Just recipe discovers arcs | Hardcoded paths | `just arcs --epoch E2.5` (metadata query) |

---

## Arcs

### New Arcs

| Arc | Theme | Requirements |
|-----|-------|-------------|
| **structural-migration** | Flat storage + metadata relationships for arcs/chapters | Foundation for all other arcs |
| **recipe-composability** | Just recipes as thin wrappers over engine functions | Composable, configurable, discoverable |
| **agent-ux** | Less reading, more calling. Agent spends tokens on work not bookkeeping | The user-facing goal |
| **epoch-governance** | Scope trim, arc carryover, epoch review ceremonies | Missing ceremonies from S339 findings |

### Carryover Arcs (Re-evaluate at E2.6 Planning)

| Arc | Origin | Fit with Agent UX? | Recommendation |
|-----|--------|---------------------|----------------|
| **feedback** | E2.5 | Yes - agent learns from work, status cascades | Absorb - directly serves agent awareness |
| **assets** | E2.5 | Partial - typed assets help agent but versioning is orthogonal | Selective - absorb schema/provenance, park versioning |
| **portability** | E2.5 | Yes - flat metadata IS portability enablement | Absorb - structural-migration arc directly serves this |
| **ceremonies** (CH-013 to CH-017) | E2.5 | Partial - CeremonyRunner fits, but renaming all skills is churn | Re-evaluate per chapter |

### Parked Work Items (Inherited)

| ID | Title | E2.6 Fit? |
|----|-------|-----------|
| WORK-101 | Proportional Governance Design | Yes - directly serves ceremony overhead reduction |
| WORK-102 | Session and Process Review Ceremonies | Yes - missing ceremonies identified in S339 |
| WORK-117 | Conftest.py unification | Yes - tactical, unblocks test work |

---

## Exit Criteria (Draft - Refine at Planning)

- [ ] Arcs and chapters stored flat with metadata relationships (not filesystem hierarchy)
- [ ] Engine functions for arc/chapter/epoch queries (no manual path resolution)
- [ ] Just recipes composable and config-driven (not hardcoded paths)
- [ ] Agent token spend on governance < 20% of session (down from ~40%)
- [ ] Mid-epoch scope trim mechanism exists
- [ ] Arc carryover ceremony defined and used
- [ ] Operator-initiated review ceremonies formalized (Session/Process/Scope)

---

## Implementation Priority (Preliminary)

1. **structural-migration** (foundation - everything else depends on flat metadata)
2. **recipe-composability** (depends on engine functions from structural-migration)
3. **epoch-governance** (can parallel with recipe work)
4. **agent-ux** (depends on 1+2, measures success)
5. **Carryover arcs** (absorbed into above or executed independently)

---

## Observations Feeding This Epoch

| Source | Key Finding |
|--------|-------------|
| obs-313 | Ceremonies need dynamic composition, not static skills |
| obs-314 | Missing operator-initiated system evolution ceremony chain (4 gaps) |
| obs-317 | Plan agent exemplar workflow (100k plan + mechanical builder) |
| obs-330 | Bug fix batch sessions high-ROI, scaffold lint missing |
| S339 retro | Greek Triad taxonomy dead, epoch scope inflation, arc carryover undefined |
| obs-339 | System assessment: governance works but expensive, filesystem hierarchy wrong permanent structure, memory underutilized, scope inflation is the biggest risk |
| mem:84332 | Ceremony overhead ~40% of tokens for small work items |
| mem:84227 | Chapter files do double-duty (design + status) |
| mem:84331 | Implementation-cycle should auto-detect missing plan |

---

## Memory Refs

Session 339 observation review: TBD (to be committed at session end)
- Session 339 retrospective findings across S314-S338
- Flat storage + metadata architecture proposal
- E2.6 epoch planning discussion

---

## References

- @.claude/haios/epochs/E2_5/EPOCH.md (prior epoch)
- @.claude/haios/epochs/E2_5/observations/obs-314-operator-initiated-system-evolution.md
- @.claude/haios/epochs/E2_5/observations/obs-313-ceremony-composition-gap.md
- @.claude/haios/epochs/E2_5/observations/obs-330-session-bugfixes.md
- @docs/work/active/WORK-101/WORK.md (proportional governance)
- @docs/work/active/WORK-102/WORK.md (review ceremonies)
- @.claude/haios/epochs/E2_5/observations/obs-339-system-assessment.md (system hot take)
