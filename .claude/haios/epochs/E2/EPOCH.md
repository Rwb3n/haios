# generated: 2026-01-06
# System Auto: last updated on: 2026-01-15T00:02:05
# STATUS: STUB - Copy-paste from INV-052. Refined through work item implementation.
# Session 178: Chapters replace Milestones. Epoch→Chapter→Arc→Work Item is the hierarchy.
# Epoch 2: Governance Suite

## L4 Object Definition

**Epoch ID:** E2
**Name:** Governance Suite
**Status:** Active
**Started:** 2025-10 (approximate)
**Architecture Source:** INV-052

---

## Purpose

Build the trust infrastructure that enables autonomous agent operation with human oversight. Transform HAIOS from manual orchestration to governed automation.

---

## Architectural Foundation

**REQUIRED READING** for all work in this epoch:

| Document | Location | Content |
|----------|----------|---------|
| Modular Architecture | `architecture/S17-modular-architecture.md` | 5 Chariot modules, interfaces, boundaries |
| Skills Taxonomy | `architecture/S10-skills-taxonomy.md` | Cycles, bridges, utilities with pressure patterns |
| Invocation Paradigm | `architecture/S12-invocation-paradigm.md` | 7-layer stack, when to use which layer |
| Bootstrap Architecture | `architecture/S14-bootstrap-architecture.md` | L0-L4 hierarchy, coldstart sequence |
| Information Architecture | `architecture/S15-information-architecture.md` | Token budgets, context levels |
| Skill/Work Unification | `architecture/S19-skill-work-unification.md` | Decomposition, category-driven routing |
| **Pressure Dynamics** | `architecture/S20-pressure-dynamics.md` | **FOUNDATIONAL** - Inhale/exhale rhythm |
| **Cognitive Notation** | `architecture/S21-cognitive-notation.md` | **FOUNDATIONAL** - RFC 2119, operators as signals |
| **Skill Patterns** | `architecture/S22-skill-patterns.md` | **FOUNDATIONAL** - Composable patterns (zoom, scaffold, checklist) |
| Work Item Universe | `architecture/S2C-work-item-directory.md` | Self-contained universes with portals |
| Lifecycle Diagrams | `architecture/S2-lifecycle-diagram.md` | Session and work item lifecycles |

---

## Key Architectural Decisions

| Decision | Choice | Reference |
|----------|--------|-----------|
| Module location | `.claude/haios/modules/` | S17, ADR-040 |
| State ownership | WORK.md is single source of truth | S3 |
| Portal system | `references/REFS.md` in work items | S2C |
| Context hierarchy | L0-L4 Manifesto Corpus | S14, S15 |
| Pressure dynamics | Phases alternate [MAY]→[MUST] | S20 |
| Cognitive notation | RFC 2119 + operators as signals | S21 |
| Skill decomposition | Smaller containers, harder boundaries | S19, S20 |
| Category-driven routing | Work category, not ID prefix | S19 |

---

## Chapters

### Epoch 2.0-2.1: The Building (Complete)

| Chapter | Name | Status | Work Items |
|---------|------|--------|------------|
| C1 | HookMigration | Complete | E2-001 through E2-120 |
| C2 | MemoryIntegration | Complete | E2-121 through E2-180 |

### Epoch 2.2: The Refinement (Active)

Distill the sprawling governance suite into leaner architecture.

| Chapter | Name | Theme | Status |
|---------|------|-------|--------|
| **Chariot** | Module Architecture | 5 modules, boundaries, wiring | Active |
| **Breath** | Pressure Dynamics | Rhythm, inhale/exhale, phase design | Active |
| **Tongue** | Cognitive Notation | RFC 2119, operators, pidgin | Planned |
| **Form** | Skill Decomposition | Smaller containers, category routing | Active |
| **Ground** | Context Loading | ground-cycle, portals, provenance | Active |

**Pressure pattern:** Chapters are [volumous] - thematic exploration. Arcs within are [tight] - bounded delivery.

---

## Epoch Completion Criteria

- [ ] All 5 Chariot modules have runtime consumers
- [x] Portal system implemented in work items (E2-277, S179)
- [ ] ground-cycle operational
- [ ] ContextLoader traverses epoch architecture
- [ ] Memory auto-linking via MemoryBridge

---

## Session 181 Observations (2026-01-08)

### Agent Behavioral Anti-Patterns

| Anti-Pattern | Description | Instance |
|--------------|-------------|----------|
| **Investigation as concept-matching** | Finding similar patterns and declaring equivalence without testing if they solve the problem | INV-060 mapped "staging" to existing concepts, didn't verify they work |
| **Capitulation over verification** | Accepting operator challenge without examining if the challenge is valid | Immediately agreed "memory_refs isn't the gap" without evidence |
| **Premature closure** | Rushing to conclusion before dwelling in ambiguity | INV-060 concluded in one pass, skipped [volumous] exploration |

**Needed:** Ambient anti-pattern harness after every action. Agent must breathe.

---

### System State: Accumulation vs Retirement

**What's bloated and stale:**
- Justfile recipes (unknown how many are actually used)
- Backlog items (40+ READY) orphaned from chapter structure
- Memory concepts from months ago that contradict current architecture
- CLAUDE.md with implementation details that drift
- Milestones (M7, M8) that predate chapter hierarchy

**What's working:**
- Epoch → Chapter → Arc → Work Item hierarchy
- Architecture docs (S14, S17, S20-S24)
- Manifesto corpus (L0-L3 immutable)
- Work items as self-contained universes with portals
- One read of epoch directory = L4 context

**The tension:**
- Concepts deprecated/superseded/retired too slowly for context to track
- Advance fast, suffer amnesia, rediscover same ground
- Cleanup not keeping pace with building - accumulating debt

**Needed:** Retirement cadence for stale artifacts. Chapter-aligned work selection.

---

### Untapped Value

Archived work items contain valuable info:
- memory_refs (links to reasoning)
- problem statement (what was being solved)
- deliverables (what was produced)

Could be synthesized into durable knowledge, but currently just accumulating.

---

### Key Insight

The epoch directory structure IS working - one read = L4 context. The peripheral artifacts (recipes, backlog, memory) bloat while chapters provide clarity.

---

## Session 182 Survey (2026-01-08)

### Module Architecture Review

Reviewed all 5 Chariot modules in depth. Key findings:

| Module | Lines | Issue |
|--------|-------|-------|
| `context_loader.py` | 195 | Not doing enough. Loads but doesn't survey/pause. |
| `governance_layer.py` | 302 | Delegates to lib/. Portability broken. |
| `memory_bridge.py` | 484 | Complex. Memory = Epoch 3 scope. |
| `work_engine.py` | 1195 | Too big. Cascade, portal, spawn tree all in one. |
| `cycle_runner.py` | 220 | Right direction. Thin. Validates gates. |

### Portability Problem

All modules import from `.claude/lib/`. If you copy `.claude/haios/` to another project, it breaks. The modules are facades, not standalone implementations.

**Decision needed:** Move lib dependencies into haios/ or make modules truly standalone.

### Decomposition Candidates

**WorkEngine (1195 lines)** should split into:
- `WorkEngine` - WORK.md CRUD only
- `CascadeEngine` - unblock/related/milestone
- `PortalManager` - REFS.md portal system
- `SpawnTree` - tree traversal and backfill

**ContextLoader** should split into:
- `ContextLoader` - load files (inhale)
- `ContextSurveyor` - present options (pause)
- `ContextRouter` - choose pattern (exhale)

### Missing Capabilities

1. **No SURVEY phase** at session level
2. **No meta-choice** - "choose how to choose"
3. **No rhythm enforcement** - S20 pressure dynamics not programmatically enforced
4. **No multiple passes** - one-shot instead of layered
5. **No multiple perspectives** - single view instead of triangulation

### Session Flow Problem

Current: `coldstart → pick work → chain chain chain chain → done`

All exhale. No inhale at the routing level.

Needed:
```
SURVEY [volumous] → CHOOSE [tight] → EXECUTE [mixed] → SURVEY [volumous]
```

### Epoch 2.2 Scope Clarification

- **Memory integration = Epoch 3.** Don't bloat E2.2.
- **Governance must be tight and svelte.** Smaller modules, hard boundaries.
- **Hooks are the beat.** They harness both operator and agent. They're the actual runtime.

### Epoch 2.2 Constraints and Realistic Value (Session 188)

**The Hard Truth:** Within Claude Code, Skill() invocation is not hookable. Claude reads markdown instructions - nothing enforces compliance. Hard enforcement requires SDK migration (Epoch 4).

**What Epoch 2.2 Work Actually Provides:**

| Work | Value Now (E2.2) | Value Later (E4) |
|------|------------------|------------------|
| session_state tracking (E2-286/287/288) | Warnings, observability | SDK harness reads same state |
| Skill simplification (Form chapter) | Marginally better compliance | Easier to port to SDK custom tools |
| Module boundaries (Chariot chapter) | Clean architecture | Direct mapping to SDK tools |
| Context loading (Ground chapter) | Better agent grounding | Same patterns in SDK harness |

**Soft Enforcement Strategy:**
- UserPromptSubmit injects warnings when work outside cycle
- Creates **affordances for patience**, not forcing it
- Agent may comply; at minimum we have observability

**The Bridge:** See `architecture/S25-sdk-path-to-autonomy.md` for technical path to Epoch 4.

---

## Session 190 Observation: Untapped Just Recipe Potential

**Observation:** Just recipes are underutilized as an execution layer.

`just session-start` works reliably because it's called at a predictable point in coldstart. The same pattern could apply more broadly:

- `just set-cycle` / `just clear-cycle` could be wired into entry-point skills (coldstart, /implement, /close)
- Recipes are the actual execution - skills are just prompts
- Pattern: "If it needs to reliably happen, make it a recipe call in a skill step"

**Current gap:** E2-288 built the recipes, but they're not yet wired into skills. Integration deferred.

**Future consideration:** Audit which skill steps should be recipe calls vs prose instructions.

---

## References

- @docs/work/archive/INV-052/README.md (source investigation)
- @.claude/haios/manifesto/ (L0-L3 foundation)
- @docs/epistemic_state.md (current status)
