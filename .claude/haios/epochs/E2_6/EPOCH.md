# generated: 2026-02-10
# System Auto: last updated on: 2026-02-14T17:26:00
# Epoch 2.6: Foundations

## L4 Object Definition

**Epoch ID:** E2.6
**Name:** Foundations
**Status:** Active
**Started:** 2026-02-14 (Session 365)
**Prior:** E2.5 (Independent Lifecycles)
**Next:** E2.7 (Composability)

---

## Purpose

Reinforce the four -ilities before building on them: traceability, referenceability, discoverability, observability. The system works (E2.5 proved it) but agents can't efficiently find, reference, trace, or observe what exists.

**The Mission:**
```
Can the agent find what it needs?       (discoverability)
Can it reference what it found?         (referenceability)
Can it trace decisions to requirements? (traceability)
Can it observe the system's state?      (observability)
```

**The Paradigm Shift:**
- From: Agent knows paths because CLAUDE.md tells it
- To: Agent discovers, references, traces, and observes through infrastructure

---

## What We Carry Forward

### Across All Epochs (Accumulated Wisdom)

**Proven Patterns (KEEP):**
| Pattern | Origin | Evidence |
|---------|--------|----------|
| TDD RED-GREEN = zero-debug | E2.5 | 6+ sessions, 100% first-pass rate |
| Critique agent before every DO | E2.5 | 10+ sessions catching real issues |
| Plan(sonnet) + Critique(haiku) model allocation | E2.5 | Cost-efficient, zero-iteration impl |
| Pressure dynamics (inhale/exhale rhythm) | E2 (S20) | Fractal across all levels |
| Breath model (pause = valid completion) | E2.4 (S27) | Ceremonies are pauses between breaths |
| Pure additive hook extension | E2.5 | Cleanest integration pattern |
| Batch bug capture -> batch fix | E2.5 | 4 bugs in ~15 min (S330) |
| stub:true frontmatter | E2.5 | Prevents agents treating stubs as functional |
| Critique-then-defer for scope control | E2.5 | Traceability without scope creep |

**Anti-Patterns (STOP):**
| Anti-Pattern | Origin |
|-------------|--------|
| Reading mutable state for computable values | E2.5 |
| Over-investigating known bugs | E2.5 |
| Skipping MUST gates without logging | E2.5 |
| Working outside governance cycles | E2.5 |
| Letting status rot (chapter, arc, epoch) | E2.5 |
| Full ceremony chain for trivial fixes | E2.5 |
| Hardcoding epoch/arc paths | E2.5, E2.4 |
| Scope inflation (6 arcs, completed 3) | E2.5 |

**Architectural Principles (FOUNDATION):**
| Principle | Origin | Status |
|-----------|--------|--------|
| Five-layer hierarchy (Principles->WoW->Ceremonies->Activities->Assets) | E2.4 | Designed, partially implemented |
| Lifecycles as pure functions (Q->F, R->S, S->A, A*S->V, [I]->[PI]) | E2.5 | Implemented |
| Queue orthogonal to lifecycle | E2.5 | Implemented |
| Ceremonies = side-effect boundaries (WHEN not WHAT) | E2.5 | Implemented |
| Four-dimensional work state (lifecycle+queue+cycle+activity) | E2.4 | Designed |
| Module-first principle (commands->cli->modules->lib) | E2.3 | Partially enforced |
| Agent as stateless identity (Dragon Quest class / A2A Agent Card) | E2.6 | NEW |

### From Prior Epochs — NOT YET BUILT

| Item | Origin | Why It Matters for Foundations |
|------|--------|-------------------------------|
| Provenance arc (ingester provenance, relationship capture) | E2.3 | Traceability of knowledge origin |
| Migration arc (recipe audit, architecture triage) | E2.3 | Discoverability — know what's stale |
| API documentation (CH-007) | E2 | Referenceability of module interfaces |
| Tool discoverability (CH-008) | E2 | Discoverability — 70+ recipes undocumented |
| Feedback arc (review ceremonies, status cascade) | E2.5 | Observability of work state |
| Portability arc (ConfigLoader for all paths) | E2.5 | Referenceability — paths as constants |
| Gate skip logging | E2.5 | Observability of governance violations |
| Scaffold output lint | E2.5 | Observability of template quality |

---

## Scope

E2.6 is focused and narrow: the four -ilities applied to what we already have.

### Arc Decomposition (Session 366)

4 arcs, 3 chapters each = 12 chapters total. Spawn-deferral policy: investigation outputs not serving E2.6 exit criteria defer to E2.7+.

**ARC: discoverability** (CH-032 to CH-034)
| CH | Title | Work Items | Requirements |
|----|-------|-----------|-------------|
| CH-032 | EntryPointInventory | WORK-020 | REQ-DISCOVER-001 |
| CH-033 | ThreeTierArchitecture | WORK-020 | REQ-DISCOVER-002 |
| CH-034 | DiscoveryMechanism | WORK-020 | REQ-DISCOVER-003 |

**ARC: referenceability** (CH-035 to CH-037)
| CH | Title | Work Items | Requirements |
|----|-------|-----------|-------------|
| CH-035 | SchemaLocationStrategy | WORK-067 | REQ-REFERENCE-001 |
| CH-036 | TemplateBootstrapPattern | WORK-067 | REQ-REFERENCE-002 |
| CH-037 | ManifestDriftPrevention | WORK-135 | REQ-PORTABLE-001 |

**ARC: traceability** (CH-038 to CH-040)
| CH | Title | Work Items | Requirements |
|----|-------|-----------|-------------|
| CH-038 | DecompositionAndMappings | WORK-097, WORK-104 | REQ-ASSET-003, REQ-LIFECYCLE-001 |
| CH-039 | L4CoverageAudit | WORK-075 | REQ-TRACE-005 |
| CH-040 | GateSkipLogging | WORK-146 | REQ-OBSERVE-005 |

**ARC: observability** (CH-041 to CH-043)
| CH | Title | Work Items | Requirements |
|----|-------|-----------|-------------|
| CH-041 | EpistemicReviewAndUXDoD | WORK-082, WORK-096 | REQ-CEREMONY-004, REQ-CEREMONY-003 |
| CH-042 | AgentCards | WORK-144 | REQ-DISCOVER-004 |
| CH-043 | LegacyCleanup | WORK-145 | REQ-CONFIG-003 |

### Work Items (11 total)

| ID | Title | Arc | Chapter | Priority |
|----|-------|-----|---------|----------|
| WORK-020 | Discoverability Architecture | discoverability | CH-032 | medium (COMPLETE S368) |
| WORK-067 | Portable Schema Architecture | referenceability | CH-035 | high (COMPLETE S367) |
| WORK-075 | System Audit as L4 Traceability | traceability | CH-039 | medium |
| WORK-082 | Epistemic Review Ceremony | observability | CH-041 | medium (COMPLETE S372) |
| WORK-096 | Agent UX Test in DoD Validation | observability | CH-041 | low |
| WORK-097 | Plan Decomposition Traceability | traceability | CH-038 | medium (COMPLETE S368) |
| WORK-104 | Validation/Triage Cycle Mappings | traceability | CH-038 | low |
| WORK-135 | Manifest Auto-Sync | referenceability | CH-037 | low |
| WORK-144 | Agent Capability Cards | observability | CH-042 | medium |
| WORK-145 | Legacy Duplication Cleanup | observability | CH-043 | low |
| WORK-146 | Gate Skip Violation Logging | traceability | CH-040 | medium |
| WORK-147 | Schema Registry Implementation | referenceability | CH-036 | medium (spawned by WORK-067) |
| WORK-148 | Remove Stub and Deprecated Skills | discoverability | CH-034 | low (spawned by WORK-020) |
| WORK-149 | Three-Tier Entry Point Architecture ADR | discoverability | CH-034 | medium (spawned by WORK-020) |
| WORK-150 | Plan Decomposition Traceability ADR | traceability | CH-038 | medium (spawned by WORK-097) |
| WORK-151 | Implement Epistemic Review in CONCLUDE | observability | CH-041 | medium (spawned by WORK-082) |

---

## Exit Criteria

- [ ] Agent can discover all skills, agents, recipes, templates via infrastructure (not CLAUDE.md) — WORK-020 designed three-tier model; commands+skills+agents already auto-discovered by Claude Code; recipe hiding + capability cards needed for completion
- [ ] All agent definitions include capability cards (A2A-inspired Agent Card pattern)
- [ ] L4 requirements traceable to work items bidirectionally
- [ ] Plan decomposition traceable to source requirements — WORK-097 designed spawn_type + decomposition_map pattern; ADR (WORK-150) pending
- [ ] System status observable without manual file reads (status, audit, metrics)
- [ ] Legacy duplication resolved (lib/ orphans, deprecated artifacts)
- [ ] MUST gate violations logged to governance events

---

## Epoch Sequence (Planned at S365)

```
E2.6  Foundations       — traceability, referenceability, discoverability, observability
E2.7  Composability     — flat metadata, engine functions, recipe rationalization
E2.8  Agent UX          — agents spend tokens on work, not bookkeeping
E2.9  Governance        — proportional governance, review ceremonies, scope management
E3    TBD               — determined by investigation (SDK? Autonomy? Product?)
E4    Cognitive Memory   — three-paradigm memory, FORESIGHT, autonomous operation
```

Each epoch is serialized. Each builds on the last. Scope inflation addressed by keeping epochs small and planning ahead.

---

## Supporting Artifacts

- `system-audit-S365.md` — Full archaeological audit (20 sections, all building blocks inventoried)
- `retro-synthesis.md` — Cross-epoch retrospective trend analysis (90+ memory entries)

---

## References

- @.claude/haios/epochs/E2_5/EPOCH.md (prior epoch)
- @.claude/haios/epochs/E2_6/system-audit-S365.md (system audit)
- @.claude/haios/epochs/E2_6/retro-synthesis.md (trend analysis)
- @.claude/haios/epochs/E2_7/EPOCH.md (next epoch)
- @docs/work/active/WORK-020/WORK.md (discoverability)
- @docs/work/active/WORK-067/WORK.md (portable schema)
- @docs/work/active/WORK-075/WORK.md (L4 traceability)
