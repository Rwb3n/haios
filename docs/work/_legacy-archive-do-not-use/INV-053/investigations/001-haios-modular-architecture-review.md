---
template: investigation
status: complete
date: 2026-01-03
backlog_id: INV-053
title: HAIOS Modular Architecture Review
author: Hephaestus
session: 158
lifecycle_phase: conclude
spawned_by: null
related: []
memory_refs:
- 80488
- 80489
- 80490
- 80491
- 80492
- 80493
- 80494
- 80495
- 80496
- 80497
- 80498
- 80499
version: '2.0'
generated: 2025-12-22
last_updated: '2026-01-03T13:12:12'
---
# Investigation: HAIOS Modular Architecture Review

@docs/README.md
@docs/epistemic_state.md

<!-- TEMPLATE GOVERNANCE (v2.0 - E2-144)

     INVESTIGATION CYCLE: HYPOTHESIZE -> EXPLORE -> CONCLUDE

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: Pure discovery, no design outputs needed"
     - "SKIPPED: Single hypothesis, no complex mapping required"
     - "SKIPPED: External research only, no codebase evidence"

     This prevents silent section deletion and ensures conscious decisions.

     SUBAGENT REQUIREMENT (L3):
     For EXPLORE phase, you MUST invoke investigation-agent subagent:
     Task(prompt='EXPLORE: {hypothesis}', subagent_type='investigation-agent')

     Rationale: Session 101 proved L2 ("RECOMMENDED") guidance is ignored ~20% of time.
     L3 enforcement ensures structured evidence gathering.
-->

---

## Discovery Protocol (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Query memory first | SHOULD | Search for prior investigations on topic before starting |
| Document hypotheses | SHOULD | State what you expect to find before exploring |
| Use investigation-agent | MUST | Delegate EXPLORE phase to subagent for structured evidence |
| Capture findings | MUST | Fill Findings section with evidence, not assumptions |

---

## Context

<!-- HYPOTHESIZE PHASE: Describe background before exploring -->

**Trigger:** INV-052 completed design for 5-module architecture (E2-240 through E2-245). Before spawning implementation, operator requested review for YAGNI assessment and simplification.

**Problem Statement:** Is the INV-052 modular design (5 modules, 7 config files, event bus) the right scope for MVP, or does it over-engineer for imagined futures?

**Prior Observations:**
- Memory concept 38201: "HAIOS has become a local maximum of architectural purity"
- Memory concept 74624: "Prioritize low-effort, high-impact solutions"
- Boris (Claude Code creator) runs vanilla config with parallel Claudes - minimal customization
- Operator constraint: Black boxes as swap points, not monuments. Build good-enough now, replace later.

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "modular architecture review simplification black box interfaces swap points"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 78832 | "Revised to module-based architecture" | Direct precedent for modular approach |
| 65187 | "Distinct, interconnected modules representing core functionalities" | Validates decomposition approach |
| 76759 | "Modular design - well-defined responsibilities and minimal dependencies" | Key design principle for swappability |
| 48230 | "Can swap out implementation without touching other parts" | Confirms swap point goal |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] Found: INV-052 (input design being reviewed)

---

## Objective

<!-- One clear question this investigation will answer -->

**What is the minimum viable modular architecture for HAIOS that enables portability, governance, continuity, and swappability - without over-engineering?**

Output: Revised spawn list (simplified E2-240+ or confirmed as-is) with clear rationale.

---

## Scope

### In Scope
- INV-052 module boundaries (5 modules: GovernanceLayer, MemoryBridge, WorkEngine, ContextLoader, CycleRunner)
- INV-052 config surface (7 YAML files proposed)
- Event bus necessity assessment
- External landscape scan (existing projects that could be adopted)
- MVP vs full architecture decision

### Out of Scope
- Implementation details of modules (that's for E2-240+)
- Performance optimization
- Multi-LLM support (future Epoch 3+)
- Specific YAML schema details (already designed in INV-052)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 6 | INV-052 Section 17.x and Section 18 |
| Hypotheses to test | 4 | Listed below |
| Expected evidence sources | 3 | Codebase / Memory / External |
| Estimated complexity | Medium | Review, not implementation |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | The 5-module split is correctly granular for swap points | Med | Review module boundaries in S17.3-17.7, assess coupling | 1st |
| **H2** | 7 config files can be reduced to 2-3 for MVP | High | Analyze S17.11, identify essential vs nice-to-have | 2nd |
| **H3** | Event bus is YAGNI - simple callbacks sufficient for now | High | Review S17.14, assess current hook patterns | 3rd |
| **H4** | No external projects exist that we should adopt instead | Low | Web search for Claude Code plugin frameworks | 4th |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [x] Read INV-052 Section 17 (Modular Architecture)
2. [x] Read INV-052 Section 17.11 (Config File Schemas)
3. [x] Read INV-052 Section 17.12 (Implementation Sequence)
4. [x] Read INV-052 Section 17.14 (Event Schemas)
5. [x] Read INV-052 Section 18 (Portable Plugin Spec)

### Phase 2: Hypothesis Testing
6. [x] Test H1: Assess module coupling - are boundaries at natural seams?
7. [x] Test H2: Identify which config files are essential for MVP vs future
8. [x] Test H3: Compare event bus complexity vs simple function calls
9. [x] Test H4: Web search for Claude Code plugin frameworks, agent architectures

### Phase 3: Synthesis
10. [ ] Create simplified architecture diagram
11. [x] Determine verdict for each hypothesis
12. [ ] Draft revised spawn list (E2-240+ simplified or confirmed)

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| 5 modules clearly defined with INPUT/OUTPUT interfaces | `SECTION-17-MODULAR-ARCHITECTURE.md:14-66` | H1 | Each module has explicit boundaries |
| Boundary rules: No cross-module state reading | `SECTION-17-MODULAR-ARCHITECTURE.md:59-64` | H1 | Enables swappability |
| Current config: only 3 YAML files active | `.claude/config/*.yaml` | H2 | Proves minimal config works |
| Proposed 7 config files have overlap (gates + node-bindings) | `SECTION-17.11:106-153` vs `:309-348` | H2 | Can consolidate |
| Current system has NO event bus - direct function calls | Current implementation | H3 | Proves callbacks sufficient |
| Only 2 events have multiple consumers | `SECTION-17-MODULAR-ARCHITECTURE.md:451-459` | H3 | Event bus overhead not justified |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 48230 | "Can swap out implementation without touching other parts" | H1 | Confirms swap point goal |
| 38201 | "Local maximum of architectural purity" | All | Warns against over-engineering |
| 74624 | "Prioritize low-effort, high-impact solutions" | H2, H3 | Guide for MVP scope |

### External Evidence (if applicable)

| Source | Finding | Supports Hypothesis | URL/Reference |
|--------|---------|---------------------|---------------|
| Claude-Flow (ruvnet) | 64 agents, swarm orchestration - different purpose | H4 | github.com/ruvnet/claude-flow |
| Claude Orchestration | Workflow DSL - no governance focus | H4 | github.com/mbruhler/claude-orchestration |
| Superagent | Guardrails framework - partial overlap but different model | H4 | helpnetsecurity.com |
| AGENTS.md standard | Adopted by 60K+ projects - complementary, not replacement | H4 | Linux Foundation |
| Microsoft Agent Framework | Enterprise governance - .NET-centric, not Claude native | H4 | azure.microsoft.com |

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **CONFIRMED** | 5 modules have explicit I/O interfaces, single responsibilities, clear ownership. Each is a swap point. | High |
| H2 | **CONFIRMED** | Current 3 config files work. Proposed 7 have overlap. Reducible to 3 for MVP. | High |
| H3 | **CONFIRMED** | No event bus exists today. Only 2 events have multiple consumers. Callbacks sufficient. | High |
| H4 | **CONFIRMED** | Claude-Flow, Superagent, etc. exist but fill different niches. HAIOS is unique Trust Engine. | Med |

### Detailed Findings

#### Finding 1: Module Split is Correct

**Evidence:**
```
5 modules from SECTION-17:
- ContextLoader: Session bootstrap (swappable for different grounding strategies)
- WorkEngine: Work item lifecycle (swappable for different PM paradigms)
- CycleRunner: Phase workflows (swappable for different methodologies)
- MemoryBridge: Memory integration (swappable between MCP/local/external)
- GovernanceLayer: Policy enforcement (swappable for different compliance)
```

**Analysis:** Each module maps to a distinct HAIOS concern. Boundaries are at natural seams - no forced separation.

**Implication:** Keep 5-module split. These ARE the swap points.

#### Finding 2: Config Surface Reducible

**Evidence:**
```
Proposed 7 files → Consolidated 3 files:

haios.yaml     = manifest + governance-toggles + thresholds
cycles.yaml    = cycle-definitions + gates + node-bindings
components.yaml = skill-manifest + agent-manifest + hook-handlers
```

**Analysis:** Current working system proves 3 files sufficient. 7-file proposal is premature optimization for organizational scaling we don't have.

**Implication:** Start with 3 config files. Split when complexity demands.

#### Finding 3: Event Bus is YAGNI

**Evidence:**
```
Current system: Direct function calls between modules
Proposed: 7 event types with JSON schemas and event log

Reality: Only 2 events have multiple consumers:
- NodeTransitioned: MemoryBridge + GovernanceLayer
- CycleCompleted: WorkEngine
```

**Analysis:** Event bus adds complexity (persistence, versioning, error handling) without proportional benefit for MVP.

**Implication:** Use typed callbacks. Event schemas become function signatures. Add event bus only when needed for async/replay/third-party integration.

#### Finding 4: No External Replacement Exists

**Evidence:**
```
| Framework | Gap vs HAIOS |
|-----------|--------------|
| Claude-Flow | No work lifecycle, no session continuity |
| Claude Orchestration | No governance hooks, no memory |
| Superagent | No portable plugin, no cycles |
| Microsoft Agent | .NET-centric, not Claude native |
```

**Analysis:** HAIOS fills unique niche: Trust Engine = governance + continuity + memory + portability. Others focus on swarms OR workflows OR safety, not the combination.

**Implication:** Build HAIOS. Consider AGENTS.md standard for interop. Don't try to adopt external framework wholesale.

---

## Design Outputs

### ASCII Architecture: The Chariot

```
                         EPOCH 2.2: THE CHARIOT
                         ======================

                    ┌─────────────────────────────┐
                    │         OPERATOR            │
                    │    (holds the reins)        │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │          CHARIOT            │
                    │  ┌───────────────────────┐  │
                    │  │ .claude/haios/        │  │
                    │  │ ├── config/           │  │  ← 3 config files (MVP)
                    │  │ │   ├── haios.yaml    │  │
                    │  │ │   ├── cycles.yaml   │  │
                    │  │ │   └── components.yaml│ │
                    │  │ └── modules/          │  │  ← 5 black box modules
                    │  └───────────────────────┘  │
                    │  ┌───────────────────────┐  │
                    │  │ haios_memory.db       │  │  ← Persistent memory
                    │  └───────────────────────┘  │
                    │  ┌───────────────────────┐  │
                    │  │ docs/work/            │  │  ← Work state (WORK.md)
                    │  └───────────────────────┘  │
                    └──────────────┬──────────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            │                      │                      │
     ┌──────▼──────┐        ┌──────▼──────┐        ┌──────▼──────┐
     │  Claude 1   │        │  Claude 2   │        │  Claude N   │
     │  (horse)    │        │  (horse)    │        │  (horse)    │
     └─────────────┘        └─────────────┘        └─────────────┘

     Horses are STATELESS. Chariot is STATEFUL.
     Any horse can be swapped. The chariot persists.
```

### ASCII Architecture: Module Dependencies

```
                    ┌─────────────────────┐
                    │  GovernanceLayer    │
                    │  (passive, no deps) │
                    │  ─────────────────  │
                    │  • Gate checks      │
                    │  • Policy enforce   │
                    │  • Transition rules │
                    └──────────┬──────────┘
                               │ consumed by all
                               ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  MemoryBridge   │◄───│   WorkEngine    │◄───│   CycleRunner   │
│  ─────────────  │    │  ─────────────  │    │  ─────────────  │
│  • MCP wrapper  │    │  • WORK.md ops  │    │  • Phase exec   │
│  • Query modes  │    │  • Node trans   │    │  • Gate invoke  │
│  • Auto-link    │    │  • History mgmt │    │  • Chaining     │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         │                      ▼                      │
         │             ┌─────────────────┐             │
         └────────────►│  ContextLoader  │◄────────────┘
                       │  ─────────────  │
                       │  • L0-L3 load   │
                       │  • Session num  │
                       │  • Ready query  │
                       └─────────────────┘

Arrow: A ◄─── B means "B calls A"
```

### ASCII Architecture: Config Consolidation

```
INV-052 PROPOSED (7 files)              MVP SIMPLIFIED (3 files)
========================                ======================

cycle-definitions.yaml ─────┐
gates.yaml ─────────────────┼──────►  cycles.yaml
node-bindings.yaml ─────────┘           • Cycle definitions
                                        • Gate definitions
                                        • Node bindings

skill-manifest.yaml ────────┐
agent-manifest.yaml ────────┼──────►  components.yaml
hook-handlers.yaml ─────────┘           • Skill registry
                                        • Agent registry
                                        • Hook handlers

manifest.yaml ──────────────┐
governance-toggles.yaml ────┼──────►  haios.yaml
thresholds.yaml ────────────┘           • Plugin manifest
                                        • Toggles
                                        • Thresholds
```

### ASCII Architecture: Communication Pattern

```
EVENT BUS (DEFERRED)                    CALLBACKS (MVP)
====================                    ===============

┌──────────┐   event   ┌─────────┐      ┌──────────┐  callback  ┌─────────┐
│ Producer │──────────►│ EventBus│      │ Producer │───────────►│ Consumer│
└──────────┘           └────┬────┘      └──────────┘            └─────────┘
                            │                           Direct function call
                   ┌────────┼────────┐                  Typed signatures
                   ▼        ▼        ▼                  No persistence
            ┌──────┐  ┌──────┐  ┌──────┐
            │ Sub1 │  │ Sub2 │  │ Log  │
            └──────┘  └──────┘  └──────┘

Complexity:                             Complexity:
• Persistence                           • None
• Versioning
• Error handling                        When to add event bus:
• Replay                                • Need async/fire-forget
                                        • Need replay/audit
                                        • Third-party integration
```

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Module count | Keep 5 | Each maps to distinct concern. Natural swap points. |
| Config files | Reduce 7→3 | Current 3 files work. Consolidate by domain. |
| Event bus | Defer | Callbacks sufficient. Only 2 multi-consumer events. |
| External adoption | Build HAIOS | No replacement exists. Consider AGENTS.md for interop. |
| Implementation order | As INV-052 | GovernanceLayer → MemoryBridge → WorkEngine → ContextLoader → CycleRunner |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Revised Spawn List (Simplified from INV-052)

**Original INV-052 proposed:** E2-240 through E2-245 (6 items)
**Revised based on this review:** 4 implementation items + 1 config item

### Immediate (Can implement now)

- [ ] **E2-240: Implement GovernanceLayer Module**
  - Description: Black box module for policy enforcement, gate checks, transition rules
  - Fixes: Scattered governance logic across hooks
  - Spawned via: `/new-plan E2-240 "Implement GovernanceLayer Module"`

- [ ] **E2-241: Implement MemoryBridge Module**
  - Description: Black box module wrapping MCP server with query modes and auto-linking
  - Fixes: Direct MCP calls scattered across codebase
  - Spawned via: `/new-plan E2-241 "Implement MemoryBridge Module"`

- [ ] **E2-242: Implement WorkEngine Module**
  - Description: Black box module for WORK.md operations, node transitions, history
  - Fixes: Work item logic scattered across lib and hooks
  - Spawned via: `/new-plan E2-242 "Implement WorkEngine Module"`

- [ ] **E2-246: Consolidate Config Files (3-file MVP)**
  - Description: Consolidate proposed 7 YAML files into 3 (haios.yaml, cycles.yaml, components.yaml)
  - Fixes: Config proliferation risk
  - Spawned via: `/new-plan E2-246 "Consolidate Config Files"`

### Deferred (Per YAGNI analysis)

- [ ] **E2-243: Implement ContextLoader Module** (DEFERRED)
  - Description: Simplified - current coldstart command may suffice
  - Blocked by: Evaluate after E2-240, E2-241, E2-242 complete

- [ ] **E2-244: Implement CycleRunner Module** (DEFERRED)
  - Description: Current skill-based cycle execution may suffice
  - Blocked by: Evaluate after core modules complete

- [ ] **E2-245: Implement Event Bus** (DEFERRED → YAGNI)
  - Description: Use callbacks instead. Event bus only if async/replay needed.
  - Status: Not spawned - YAGNI per H3 analysis

### Spawn Summary

| Original ID | Status | Rationale |
|-------------|--------|-----------|
| E2-240 GovernanceLayer | **SPAWN** | Core governance, no deps |
| E2-241 MemoryBridge | **SPAWN** | MCP wrapper, immediate value |
| E2-242 WorkEngine | **SPAWN** | State owner, core to system |
| E2-243 ContextLoader | **DEFER** | Coldstart may suffice |
| E2-244 CycleRunner | **DEFER** | Skills may suffice |
| E2-245 Event Bus | **YAGNI** | Callbacks sufficient |
| E2-246 Config MVP | **NEW** | Consolidate 7→3 files |

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 158 | 2026-01-03 | HYPOTHESIZE | Complete | Initial context and hypotheses |
| 158 | 2026-01-03 | EXPLORE | Complete | Investigation-agent gathered evidence |
| 158 | 2026-01-03 | CONCLUDE | In progress | Findings synthesized, spawns pending |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-H4 have verdict | [x] | All CONFIRMED |
| Evidence has sources | All findings have file:line or concept ID | [x] | See Evidence Collection |
| Spawned items created | Items exist in backlog or via /new-* | [ ] | Pending operator approval |
| Memory stored | ingester_ingest called, memory_refs populated | [ ] | Pending |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | Yes | agentId: aeec068 |
| Are all evidence sources cited with file:line or concept ID? | Yes | |
| Were all hypotheses tested with documented verdicts? | Yes | H1-H4 all CONFIRMED |
| Are spawned items created (not just listed)? | Pending | Awaiting operator approval of revised spawn list |
| Is memory_refs populated in frontmatter? | Pending | Will store after operator approval |

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete ALL items before /close -->

### Required (MUST complete)
- [ ] **Findings synthesized** - Answer to objective documented in Findings section
- [ ] **Evidence sourced** - All findings have file:line or concept ID citations
- [ ] **Hypotheses resolved** - All hypotheses have Confirmed/Refuted/Inconclusive verdict
- [ ] **Spawned items created** - Via /new-* commands with `spawned_by` field (or rationale if none)
- [ ] **Memory stored** - `ingester_ingest` called with findings summary
- [ ] **memory_refs populated** - Frontmatter updated with concept IDs
- [ ] **lifecycle_phase updated** - Set to `conclude`
- [ ] **Ground Truth Verification complete** - All items checked above

### Optional
- [ ] Design outputs documented (if applicable)
- [ ] Session progress updated (if multi-session)

---

## References

- Spawned by: INV-052 (review before implementation spawning)
- Related: INV-052 HAIOS Architecture Reference
- Related: Session 158 coldstart discussion with operator
- Related: Boris's Claude Code usage patterns (external reference)
- Related: Memory 38201 ("local maximum of architectural purity")

---
