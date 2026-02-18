# generated: 2026-02-14
# System Auto: last updated on: 2026-02-17T20:50:00
# Epoch 2.8: Agent UX

## L4 Object Definition

**Epoch ID:** E2.8
**Name:** Agent UX
**Status:** Active
**Started:** 2026-02-17 (Session 393)
**Prior:** E2.7 (Composability)
**Next:** E2.9 (Governance)

---

## Purpose

The headline epoch. With foundations solid (E2.6) and building blocks composable (E2.7), now make the agent experience efficient. Agents spend tokens on work, not bookkeeping.

**The Mission:**
```
The agent should not read what it can call.
The agent should not search what it can query.
The agent should not guess what it can discover.
```

**The Prime Directive Connection:**
L0 says: "reduce the Operator's cognitive load, resolve existential oscillation, and provide the leverage necessary to achieve sovereign agency." E2.8 implements this at the architectural level:
- **Call** (not read) = reduce agent cognitive load (tokens on work, not ceremony navigation)
- **Query** (not search) = provide leverage via infrastructure (engine functions over file reads)
- **Discover** (not guess) = resolve oscillation through certainty (infrastructure-driven capability discovery)

**The Structural Problem (mem:85390):**
Full ceremony chain consumes ~104% of 200k context budget. The system literally cannot complete a full governed lifecycle in a single session. This is not overhead — it is architectural mismatch. E2.8 resolves this by migrating mechanical governance from "agent reads SKILL.md" to "hook/module executes automatically."

**The Three Governance Mechanisms:**
| Mechanism | Token Cost | Examples |
|-----------|-----------|----------|
| Hooks (PreToolUse, PostToolUse, UserPromptSubmit) | ~0 | Time injection, write blocks, SQL blocks — the FIRST governance primitives |
| Python modules (lib/, modules/) | ~0 | queue_ceremonies.py, status_propagator.py, hierarchy_engine.py |
| Ceremony skills (SKILL.md) | 100% agent tokens | implementation-cycle, retro-cycle, close-work-cycle |

E2.8 moves what it can from Tier 3 (SKILL.md) to Tier 1/2 (hooks/modules).

**Depends on E2.7:** Composable engine functions and ConfigLoader paths are prerequisites. Both delivered S393.

---

## What We Carry Forward

### The Core Problem (E2.5 S339 Finding)
Governance works but costs ~40% of tokens. Ceremony overhead is disproportionate for small work items (mem:84332). Full chain = 13 ceremonies = 104% context budget (mem:85390).

### From E2.7 (Composability)
- HierarchyQueryEngine: get_arcs(), get_chapters(), get_work(), get_hierarchy() (WORK-157)
- ConfigLoader for all path resolution — zero hardcoded paths (WORK-158)
- Status cascades automatically via StatusPropagator (WORK-034)
- Typed lifecycle assets composable (WORK-093)
- Recipes rationalized and documented (WORK-159, ADR-045)

### From E2.5/E2.6 Trend Analysis
| Trend | Evidence | Relevance |
|-------|----------|-----------|
| Ceremony overhead ~104% of context | mem:85390, 85606 | CRITICAL — structural impossibility |
| Session boundary gap ungoverned | mem:85609, 85385, 85387 | HIGH — last 2-3 ceremonies never run |
| Coldstart overkill for housekeeping | mem:84835, 84836 | HIGH — full load for doc fixes |
| Batch fixes avoid ceremony overhead | mem:84928, 84963 | HIGH — validated pattern |
| Ceremonies are markdown (agent is runtime) | mem:84857, 84996 | ARCHITECTURAL — token cost = SKILL.md size |

### Foundational Insight (S393)
The first governance primitives (time hooks, write blocks, SQL blocks) cost zero agent tokens. The most recent (ceremony skills) cost 100%. The path forward is clear: move mechanical governance back toward the hook/module layer where judgment isn't needed.

### Inspiration: A2A Agent Cards + Dragon Quest Classes
Each agent has a stateless identity card: role, capabilities, tools, triggers, what it produces. Agents discover each other through infrastructure, not hardcoded knowledge. (Google A2A Protocol, operator vision S365, mem:85154, 85155)

---

## Arcs (Decomposed S393)

### Arc 1: call — "The agent should not read what it can call"

Move mechanical ceremony phases from SKILL.md (agent reads) to hooks/modules (auto-execute). Proportional scaling for phases that require judgment. **Coldstart must inject all operational context — zero Read instructions. The orchestrator output IS the agent's operating knowledge.**

| CH-ID | Title | Work Items | Requirements | Dependencies | Status |
|-------|-------|------------|--------------|--------------|--------|
| CH-058 | ProportionalGovernanceDesign | WORK-101 | REQ-CEREMONY-001 | None | Planning |
| CH-059 | CeremonyAutomation-CritiqueAsHook | New | REQ-CEREMONY-002 | CH-058 | Planning |
| CH-060 | SessionBoundaryFix | WORK-161 | REQ-CEREMONY-001 | None | Complete |
| CH-061 | ColdstartContextInjection | New | REQ-CONFIG-001, L3.3 | None | Planning |
| CH-066 | MCPOperationsServer | New | REQ-DISCOVER-002, REQ-CONFIG-001 | CH-061 | Planning |

**Exit criteria:**
- [ ] Governance overhead measurably reduced (target: perceptible improvement over E2.5 baseline)
- [ ] Trivial items skip heavy ceremony phases (computable predicates, extending retro-cycle Phase 0 pattern)
- [ ] Mechanical ceremony phases migrated to hooks/modules (session-end, checkpoint population, cycle_phase advancement)
- [x] Session boundary gap governed (post-closure transition runs reliably) (WORK-161, S396)
- [ ] Coldstart injects ALL operational context (zero manual Read steps in coldstart skill)
- [ ] Minimum viable context contract enforced: identity + mission + prior + work + operational HOW
- [ ] haios-operations MCP server exposes work/hierarchy/session/scaffold tools as agent-native interface
- [ ] Just recipes retired for agent use — MCP tools replace Tier 2 operations, just remains Tier 3 (operator terminal only)

**Principle: Critique is the inhale-to-exhale transition gate.** Every transition from exploring/planning to committing/executing should have assumption surfacing. The weight scales with commitment: none (trivial) → checklist (hook-injected) → full (critique-agent subagent) → operator (design dialogue). Detection is a PreToolUse hook (zero agent tokens). The predicate is computable from work item type, plan existence, and transition type. This answers the breath-architecture-handover.md open question: the critique pattern IS the phase transition mechanism.

**Principle: Coldstart produces an operational agent, not an informed one.** After `/coldstart`, the agent must be able to execute work without reading any additional files. The orchestrator output is the captain's briefing packet — standing orders (hooks) are already active, the briefing provides everything else.

**S393/S394 evidence:** 200k agent failed to operate because coldstart injected WHO and WHAT but not HOW. Agent wrote raw Python imports (4 failures) instead of using `just ready`. Coldstart "succeeded" but produced a non-operational agent.

**Evidence:** mem:84332, 85390, 85606 (104% problem), 85609/85385/85387 (session boundary gap), 85607/85363 (retro Phase 0 prototype), 85915-85922 (200k agent bypass observation), 85923-85924 (minimum viable context)

---

### Arc 2: query — "The agent should not search what it can query"

Extend engine functions for context loading. Memory-first retrieval. Progressive disclosure in contracts.

| CH-ID | Title | Work Items | Requirements | Dependencies | Status |
|-------|-------|------------|--------------|--------------|--------|
| CH-062 | ProgressiveContracts | New | REQ-ASSET-001 | None | Planning |

**Exit criteria:**
- [ ] Lightweight coldstart variant exists for housekeeping sessions (tiered: full vs quick)
- [ ] Contracts designed for progressive disclosure (agent reads what it needs, not everything)
- [ ] Context loading uses engine functions and memory before file reads

**Evidence:** mem:84835, 84836 (coldstart overhead), 85459 (most tokens on context loading), 85815 (Dimension 2: context switching)

---

### Arc 3: discover — "The agent should not guess what it can discover"

Agent Cards for infrastructure-driven capability discovery. Agents find each other via typed interfaces, not CLAUDE.md.

| CH-ID | Title | Work Items | Requirements | Dependencies | Status |
|-------|-------|------------|--------------|--------------|--------|
| CH-063 | AgentCards | New | REQ-DISCOVER-002, REQ-DISCOVER-003 | None | Planning |
| CH-064 | InfrastructureCeremonies | New | REQ-CEREMONY-001, REQ-CEREMONY-002 | None | Planning |

**Exit criteria:**
- [ ] All agents have structured capability cards discoverable via infrastructure
- [ ] Open-epoch-ceremony skill exists (mirror of close-epoch-ceremony)
- [ ] Agents not hardcoded in CLAUDE.md — discovered via infrastructure

**Evidence:** mem:85154, 85210 (agents not discoverable), 85098/85108 (WORK-143 triage consumer), 85476 (capability card query tool)

---

### Arc 4: infrastructure — "Fix what's broken"

Bug fixes and deferred items. Clean foundation for the UX arcs.

| CH-ID | Title | Work Items | Requirements | Dependencies | Status |
|-------|-------|------------|--------------|--------------|--------|
| CH-065 | BugBatch-E28 | WORK-166 | REQ-CEREMONY-001 | None | Complete |

**Exit criteria:**
- [x] All confirmed bugs from E2.7 triage resolved (85712, 85557, 85795, 85573, 85132) (WORK-166, S395)
- [x] Checkpoint same-session sort bug fixed (session_loader.py:120) (WORK-166, S395)
- [x] Queue state machine admin cleanup transition added (backlog->done) (WORK-166, S395)

**Evidence:** Direct from retro extractions + S393 coldstart observation. Batch pattern validated (mem:84963).

---

### Completed (carry-forward satisfied)

| ID | Title | Notes |
|----|-------|-------|
| WORK-143 | Retro-Triage Consumer Update | Closed prior to E2.8. Triage reads retro-* provenance tags. |

### Deferred (not E2.8)

| Item | Destination | Rationale |
|------|-------------|-----------|
| Flat metadata storage for arcs/chapters | E2.9+ | Needs investigation, architectural scope |
| Batch mode for trivial operations | Folds into Arc 1 CH-058 | Proportional scaling subsumes batch |
| Full memory system overhaul | E4 (Cognitive Memory) | Three-paradigm memory, FORESIGHT |
| WORK-071 Pre-Decomposition Review Gate | E2.9 (Governance) | Governance-themed, parked |
| WORK-101 Proportional Governance Design | E2.9 if not completed in E2.8 | Unparked S393, assigned to CH-058, queue: backlog |
| WORK-102 Session/Process Review Ceremonies | E2.9 (Governance) | Governance-themed, backlog |

---

## Exit Criteria

- [ ] Governance overhead measurably reduced (target: perceptible improvement over E2.5 baseline)
- [ ] Lightweight coldstart variant exists for housekeeping sessions
- [ ] Mechanical ceremony phases migrated to hooks/modules
- [ ] Contracts designed for progressive disclosure
- [ ] All agents have structured capability cards
- [x] Open-epoch-ceremony skill exists (full ceremony loop standardized) (S393)
- [x] Confirmed bugs from E2.7/E2.8 triage resolved (checkpoint sort, queue state machine) (WORK-166, S395)
- [ ] Coldstart produces accurate context after epoch transition (no stale epoch, no stale checkpoint)
- [ ] haios-operations MCP server replaces just recipes as agent-native Tier 2 interface
- [ ] Just recipes retired for agent use (Tier 3 operator-terminal only)

---

## Observations Feeding This Epoch

| Source | Key Finding |
|--------|-------------|
| mem:85390 | Full ceremony chain = ~104% of 200k context budget |
| mem:85609 | Session boundary gap ungoverned (last 2-3 ceremonies never run) |
| mem:84857 | Ceremony skills are markdown — agent is the runtime (token cost = SKILL.md size) |
| mem:84332 | ~40% tokens on governance for small items |
| mem:84836 | Coldstart overhead overkill for doc fixes |
| mem:85154 | Dragon Quest class pattern for agent identity |
| mem:85098 | WORK-143 triage consumer update needed for retro-* tags |
| mem:85809-85819 | S393 observations: two UX dimensions (weight + context switching) |

---

## Architecture

- `architecture/breath-architecture-handover.md` — Opinionated vs delegative design, breath metaphor as fractal system pattern. Three open questions on phase transitions. (Operator design session, filed S365)

---

## References

- @.claude/haios/epochs/E2_7/EPOCH.md (prior epoch)
- @.claude/haios/epochs/E2_9/EPOCH.md (next epoch)
- @.claude/haios/epochs/E2_6/retro-synthesis.md (trend analysis)
- @.claude/haios/epochs/E2_8/architecture/breath-architecture-handover.md (breath architecture)
- @docs/work/active/WORK-101/WORK.md (proportional governance)
- @docs/ADR/ADR-045-three-tier-entry-point-architecture.md (three-tier model)
- Memory: 85390 (104% problem), 85609 (session gap), 84857 (ceremony=markdown), 85154 (agent cards), 85809-85819 (S393 observations)
