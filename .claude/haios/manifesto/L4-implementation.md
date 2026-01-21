# generated: 2026-01-01
# System Auto: last updated on: 2026-01-21T18:01:49
# L4: Implementation - Technical Specifications

Level: L4
Status: ACTIVE
Access: All agents
Mutability: DYNAMIC (changes frequently)

---

## Question Answered

**What are the current technical specifications and temporal goals?**

Execution layer. Contains rules, configs, and time-bound objectives.

---

## The Mission (Session 206 Strategic Review)

**What HAIOS actually is:**

```
INPUT:  Corpus of documents (specs, designs, requirements)
PROCESS: Multi-agent operational framework
OUTPUT: Functional product (aligned to L0-L2 manifesto)
```

**The portability test:**
> Can you drop `.claude/haios/` into a fresh workspace with a corpus of docs and have it produce a working product?

Today: **No.** The plugin assumes HAIOS context, not arbitrary projects. We've built PM infrastructure that tracks itself.

**What's required for "let it rip":**

| Capability | Purpose | Current State |
|------------|---------|---------------|
| **Corpus Loader** | Read arbitrary docs, not hardcoded paths | No - ContextLoader is HAIOS-specific |
| **Requirement Extractor** | Parse docs → actionable work items | No - manual operator extraction |
| **Planner Agent** | Decompose requirements → ordered tasks | No - operator writes plans |
| **Builder Agent** | Execute tasks → produce code/artifacts | Partial - cycles guide, but need steering |
| **Validator Agent** | Check output against source specs | No - manual review |
| **Orchestrator** | Route between agents, manage state | Partial - CycleRunner exists |

**What we've built that's reusable:**
- Memory system (store/retrieve learnings)
- Work item structure (WORK.md, lifecycle)
- Hooks (governance enforcement)
- Session state tracking

**What's HAIOS-specific cruft:**
- L0-L4 manifesto (our corpus, not the framework)
- Epochs/Arcs/Chapters (PM for HAIOS development)
- Many recipes (HAIOS-specific operations)

**The pivot (Session 206):**
> Stop building PM infrastructure for HAIOS development.
> Start building the **doc-to-product pipeline** that HAIOS *is*.

**Architecture:** See `architecture/S26-pipeline-architecture.md` for full pipeline design.

---

## Module-First Principle (Session 218 - MUST)

**Commands and skills MUST call modules, not instruct agents to read files manually.**

We have 11 modules in `.claude/haios/modules/`. They must be used.

### The Correct Layer Stack

```
┌─────────────────────────────────────────┐
│  Commands/Skills (prose)                │  Orchestration, user interaction
│  - .claude/commands/*.md                │  MUST call: cli.py or just recipes
│  - .claude/skills/*/*.md                │  MUST NOT: instruct file reads
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│  CLI / Just Recipes                     │  Command dispatch
│  - .claude/haios/modules/cli.py         │  MUST call: modules/*.py
│  - justfile                             │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│  Modules                                │  Business logic
│  - .claude/haios/modules/*.py           │  MUST call: lib/*.py, files
│  (11 modules: WorkEngine, ContextLoader,│
│   GovernanceLayer, MemoryBridge, etc.)  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│  Library                                │  Utilities, low-level ops
│  - .claude/lib/*.py                     │
└─────────────────────────────────────────┘
```

### Anti-Pattern (MUST NOT)

```markdown
# coldstart.md (WRONG)
## Step 8: Session Start
Read `.claude/session` to get session number...
```

Agent interprets prose → reads file manually → bypasses ContextLoader.

### Correct Pattern (MUST)

```markdown
# coldstart.md (RIGHT)
## Step 8: Session Start
Run: `just coldstart` or `python -m cli context-load`
```

Agent calls cli.py → cli.py calls ContextLoader → module does the work.

### Why This Matters

| Without Module-First | With Module-First |
|---------------------|-------------------|
| 11 modules collecting dust | Modules are runtime consumers |
| Prose duplicates code | Prose orchestrates code |
| No testability | Modules are unit-testable |
| Agent re-interprets on every run | Behavior is deterministic |

### Enforcement

Every chapter, arc, skill, and command design MUST answer:

> **"Which module does the work? If none, why not?"**

If the answer is "agent reads files manually" - the design is wrong.

---

## Current Goals (Temporal)

### Current Epoch: Epoch 2.2 - The Refinement
*Chapters replace Milestones (Session 179)*

**Theme:** Distill sprawling governance suite into leaner architecture

**What Changed (Session 179, updated Session 191 ADR-042):**
> Milestones replaced by Arcs (ADR-042: hierarchy renamed for universal story semantics).
> Arcs are [volumous] - thematic exploration. Chapters within are [tight] - bounded delivery.
> This matches the fractal pressure pattern: Epoch[tight] → Arc[volumous] → Chapter[tight] → Work[volumous] → Phase[tight]

**Active Arcs:**
| Arc | Theme | Status |
|-----|-------|--------|
| **Chariot** | 5 modules, boundaries, wiring | Active |
| **Breath** | Pressure dynamics, rhythm | Active |
| **Form** | Skill decomposition, category routing | Active |
| **Ground** | Context loading, portals, provenance | Active |

**Exit Criteria (Epoch 2.2):**
- All 5 Chariot modules have runtime consumers
- Skills decomposed into single-responsibility units
- Context Architecture implemented (files as context windows)
- Config-driven generation (`just apply` regenerates from haios.yaml)

### Architecture Evolution (Session 179)

**What Was (Epoch 2.0-2.1: The Building):**
- Milestones: M7b-WorkInfra, M7c-Governance, M7e-Hygiene, M8-Memory
- 17 sections in INV-052
- Monolithic skills (5-phase cycles)
- Prose-based skill definitions
- Files as documentation

**What Is Now (Epoch 2.2: The Refinement):**
- Chapters: Chariot, Breath, Tongue, Form, Ground
- Foundational architecture: S20, S21, S22, S23
- Smaller containers, harder boundaries
- Cognitive notation ([MAY]/[MUST], operators)
- **Files as context windows** (L3 principle)

**Why It Changed:**
> "The architecture gives me space. I refuse to take it." - Session 179
> Agent steamrolls through volumous phases, checks boxes without reflecting.
> Solution: Pressure dynamics (S20), composable patterns (S22), context architecture (S23).

### Previous Work (Epoch 2.0-2.1)

*Preserved for historical context - these were completed before the refinement:*

**Module Implementation (S159-164):**
- ~~E2-246 Config MVP~~ (consolidate 7→3 files)
- ~~E2-240 GovernanceLayer~~ (built, integrated)
- ~~E2-241 MemoryBridge~~ (**STUB ONLY** - needs MCP integration)
- ~~E2-242 WorkEngine~~ (built)
- ~~E2-250-255~~ (various module work)

**Key Learnings:**
> **S162:** "Tests pass" ≠ "Code is used". Modules without runtime consumers are prototypes.
> **S164:** Delegation pattern works - wrap existing lib/ functions rather than copy.
> **S179:** Files are context windows, not documentation. Quality of output determines downstream capability.

---

## Epoch Roadmap

| Epoch | Name | Theme | Status |
|-------|------|-------|--------|
| 1 | Foundation | Core infrastructure, memory, engine v1→v3 | Complete |
| 2 | Governance Suite | Hooks, commands, workflows | **Current** |
| 3 | FORESIGHT | SIMULATE, INTROSPECT, ANTICIPATE, UPDATE | Planned |
| 4 | AUTONOMY | Perpetual loop, headless spawn, human-out-of-loop | Vision |
| 5 | REVENUE | Self-sustaining economics, FinTech modules | Vision |

---

## Epoch 4: AUTONOMY (Vision)

*Requires Epoch 2-3 infrastructure. Multi-agent layer architecture.*

**Theme:** Human moves from L5-L7 operator to L0-L2 principal

**The Layer Transition:**

| Current (Epoch 2) | Future (Epoch 4) |
|-------------------|------------------|
| Human ↔ Single Agent | Human at L0-L2 |
| Manual layer steering | Orchestrator Agent at L3-L4 |
| One context thread | Worker Agents at L5-L7 |

**Architecture:**
```
Human (L0-L2: Telos, Principal, Intent)
         ↓
Orchestrator Agent (L3-L4: Architecture, Principles)
         ↓
Worker Agents (L5-L7: Work items, Execution)
```

**Inter-Agent Protocol:**
- L5-L7 signals: "stuck", "doesn't fit", "found something"
- L3-L4 receives, decides: handle or escalate
- L0-L2 receives only what requires human judgment
- Decisions flow down through context (S23/S24)

**Why Epoch 2 Matters:**
What we build now becomes inter-agent infrastructure:
- S23/S24 context architecture = how agents pass context
- memory_refs = reasoning persists across agent boundaries
- Portals = work items reference each other across agents

### Enabling Technology: Claude Agent SDK (Session 188 Discovery)

**The Problem (INV-062):** Within Claude Code, Skill() invocation is not hookable - Claude reads markdown instructions, but nothing enforces compliance. Hard enforcement of cycles/phases is architecturally impossible without API changes.

**The Solution:** The Claude Agent SDK provides the harness control needed for Epoch 4:

| Epoch 2 Constraint | SDK Capability |
|-------------------|----------------|
| Skill() unhookable | Custom tools run in-process, fully controllable |
| Hooks can't check session state | Hooks have full context access |
| CycleRunner must be stateless | Your harness owns execution loop |
| Soft enforcement only (warnings) | PreToolUse can deny any action |

**SDK Architecture Pattern:**
```python
# In-process custom tools = controllable agent actions
@tool("execute_cycle", "Execute a HAIOS cycle", {"cycle_name": str, "work_id": str})
async def execute_cycle(args):
    session_state["active_cycle"] = args["cycle_name"]
    result = await harness.run_cycle(args["cycle_name"], args["work_id"])
    session_state["active_cycle"] = None
    return result
```

**Alignment with Epoch 4 Vision:**
- Harness controls execution (not relying on Claude to follow markdown)
- Files as substrate (SDK works with filesystem, inbox/outbox pattern)
- LLM is swappable (SDK is wrapper, backend can change)
- Full traceability (hooks see every action)

**Reference:** See `epoch4_vision/` corpus for detailed architecture vision, `S25-sdk-path-to-autonomy.md` for technical path.

**Exit Criteria (Draft):**
- Orchestrator agent can run session without human intervention
- Worker agents can execute work items autonomously
- Human intervention only for L0-L2 decisions (telos, principal changes)
- SDK-based harness enforces cycle compliance

---

## Epoch 5: REVENUE (Vision)

*Requires Epoch 2-4 infrastructure. The ultimate manifestation of the Agency Engine.*

**Theme:** Self-sustaining economics through FinTech modules

**Guiding Principles:**

| Principle | Meaning |
|-----------|---------|
| **Zero Liability** | No inventory, refunds, customer service. Pure information arbitrage. Clean exits. |
| **Self-Sustaining Economics** | System pays for its own infrastructure. Break-even: 1-2 streams at £300-900/month. |
| **Specialist Factory** | Claude designs, fine-tuned specialists execute. 270M param models, runs locally, £0 cost. |
| **Biomimetic Architecture** | Scout (surveillance), Gate (apoptosis), Execution (somatic), Maintenance (homeostasis), Human (consciousness) |
| **Evolutionary Learning** | Event ledger captures all. Failures inform improvement. Success promotes to Maintenance. |

**Exit Criteria (Draft):**
- First revenue stream deployed and generating £300+/month
- System infrastructure costs covered by revenue
- Operator time commitment < 5 hours/week for maintenance

---

## Epoch 2.2: The Chariot Architecture (INV-053)

*Session 158: Reviewed and simplified INV-052 design.*

### The Chariot Metaphor

```
                    ┌─────────────────────────────┐
                    │         OPERATOR            │
                    │    (holds the reins)        │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │          CHARIOT            │
                    │  .claude/haios/             │
                    │  ├── config/ (3 files)      │
                    │  └── modules/ (5 black boxes)│
                    └──────────────┬──────────────┘
                                   │
     ┌─────────────┬───────────────┼───────────────┬─────────────┐
  Claude 1     Claude 2       Claude 3       Claude N      ...

Horses (Claudes) are STATELESS. Chariot (HAIOS) is STATEFUL.
Any horse can be swapped. The chariot persists.
```

### 9 Module Architecture (E2-279 Decomposition)

| Module | Purpose | Swap Point For |
|--------|---------|----------------|
| **GovernanceLayer** | Policy, gates, transitions | Compliance regimes |
| **MemoryBridge** | MCP wrapper, query modes | Memory backends |
| **WorkEngine** | WORK.md owner, core CRUD (~585 lines) | PM paradigms |
| **CascadeEngine** | Completion cascade, unblock | Cascade strategies |
| **PortalManager** | REFS.md management | Reference systems |
| **SpawnTree** | Spawn tree traversal | Visualization |
| **BackfillEngine** | Backlog content backfill | Migration tools |
| **ContextLoader** | L0-L3 loading, bootstrap | Grounding strategies |
| **CycleRunner** | Phase execution, chaining | Methodologies |

*E2-279: WorkEngine decomposed from 1197 to 585 lines. CascadeEngine, PortalManager, SpawnTree, BackfillEngine extracted as satellites with lazy delegation.*

### 3-File Config (Simplified from 7)

| File | Consolidates | Content |
|------|--------------|---------|
| `haios.yaml` | manifest + toggles + thresholds | Plugin identity, runtime toggles |
| `cycles.yaml` | node-bindings (cycles + gates added by E2-240) | Node lifecycle bindings |
| `components.yaml` | skills + agents + hooks (populated by E2-240) | Component registries |

### Key Decisions (INV-053)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Module count | Keep 5 | Natural swap points at concern boundaries |
| Config files | 7→3 | Current 3 files prove minimal works |
| Event bus | Defer | Callbacks sufficient; only 2 multi-consumer events |
| External adopt | Build HAIOS | No replacement for Trust Engine niche |

### Implementation Sequence

```
E2-246 (Config MVP)
    │
    └──► E2-240 (GovernanceLayer) ← Phase 1: No deps
              │
              └──► E2-241 (MemoryBridge) ← Phase 2: MCP wrapper
                        │
                        └──► E2-242 (WorkEngine) ← Phase 3: State owner
```

**Deferred:** ContextLoader, CycleRunner (evaluate after core modules)

---

## Functional Requirements Summary

*What each module MUST do. Agent uses this to verify implementation.*

### GovernanceLayer (E2-240)

**Purpose:** Policy enforcement, gate checks, transition validation.

| Function | Input | Output | Acceptance Test |
|----------|-------|--------|-----------------|
| `check_gate(gate_id, context)` | Gate ID + work context | `GateResult(allowed, reason)` | Returns deny for incomplete DoD |
| `validate_transition(from_node, to_node)` | DAG nodes | `bool` | Blocks invalid transitions (e.g., backlog→complete) |
| `load_handlers(config_path)` | Path to components.yaml | Handler registry | Loads all registered handlers |
| `on_event(event_type, payload)` | Event + data | Side effects | Routes to correct handlers |

**Invariants:**
- MUST NOT modify work files directly (that's WorkEngine's job)
- MUST log all gate decisions for audit
- MUST be stateless (no internal state between calls)

### MemoryBridge (E2-241)

**Purpose:** Wrap haios-memory MCP, provide query modes, auto-link.

| Function | Input | Output | Acceptance Test |
|----------|-------|--------|-----------------|
| `query(query, mode)` | Search string + mode | List of concepts | Returns relevant concepts for "session recovery" |
| `store(content, source_path)` | Content + provenance | Concept IDs | Creates concepts with correct classification |
| `auto_link(work_id, concept_ids)` | Work ID + refs | Updated WORK.md | Adds memory_refs to frontmatter |

**Query Modes:**
- `semantic`: Pure similarity search
- `session_recovery`: Excludes synthesis, for coldstart
- `knowledge_lookup`: Filters to episteme/techne

**Invariants:**
- MUST handle MCP timeout gracefully (retry once, then warn)
- MUST parse work_id from source_path for auto-linking
- MUST NOT block on MCP failure (degrade gracefully)

### WorkEngine (E2-242)

**Purpose:** Own WORK.md, manage lifecycle, single source of truth.

| Function | Input | Output | Acceptance Test |
|----------|-------|--------|-----------------|
| `get_work(id)` | Work ID | WorkState object | Returns parsed WORK.md |
| `create_work(id, title, ...)` | Work item data | Created file path | Creates directory + WORK.md |
| `transition(id, to_node)` | Work ID + target node | Updated WorkState | Updates current_node, appends node_history |
| `get_ready()` | None | List of unblocked items | Returns items where blocked_by is empty |
| `archive(id)` | Work ID | Archived path | Moves to docs/work/archive/ |

**Invariants:**
- MUST be the ONLY writer to WORK.md files
- MUST validate transitions via GovernanceLayer
- MUST update node_history with timestamps on every transition
- MUST call MemoryBridge.auto_link after memory operations

### Config MVP (E2-246)

**Purpose:** Consolidate existing 3 config files into unified loader with domain organization.

| File | Required Sections | Acceptance Test |
|------|-------------------|-----------------|
| `haios.yaml` | manifest, toggles, thresholds | Loads without error, toggles accessible |
| `cycles.yaml` | node_bindings | Node bindings parseable (cycle defs deferred to E2-240) |
| `components.yaml` | skills, agents, hooks | Empty placeholders (registries populated by E2-240) |

**Scope Clarification (INV-053 Decision, S158):**
- cycles.yaml starts with node_bindings ONLY (migrating existing node-cycle-bindings.yaml)
- Cycle definitions and gates are E2-240 (GovernanceLayer) responsibility
- This matches "consolidate existing config" scope, not "create new config"

**Invariants:**
- MUST be valid YAML (schema validation on load)
- MUST return empty dict on missing files (graceful degradation, matches current behavior)
- MUST support hot-reload (future, not MVP)

---

## Testing Requirements

*How to verify modules work correctly.*

### Unit Tests (per module)

| Module | Test File | Key Tests |
|--------|-----------|-----------|
| GovernanceLayer | `tests/test_governance_layer.py` | Gate blocking, transition validation |
| MemoryBridge | `tests/test_memory_bridge.py` | Query modes, auto-link parsing |
| WorkEngine | `tests/test_work_engine.py` | CRUD, transitions, node_history |
| Config | `tests/test_config.py` | YAML loading, schema validation |

### Integration Tests

| Test | Modules | Scenario |
|------|---------|----------|
| `test_work_lifecycle.py` | All | Create → transition → archive |
| `test_memory_integration.py` | MemoryBridge + WorkEngine | Store → auto-link → verify refs |
| `test_governance_gates.py` | GovernanceLayer + WorkEngine | Transition blocked by gate |

### Acceptance Criteria (DoD per module)

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] **Runtime consumer exists** (something outside tests imports/calls the code)
- [ ] No direct SQL queries (use MemoryBridge)
- [ ] No direct WORK.md writes outside WorkEngine
- [ ] Typed interfaces (Protocol classes)
- [ ] Docstrings on public methods

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Modules without consumers are prototypes, not complete work.

---

## System Health (Observability)

*How to know the chariot is working.*

### Health Indicators

| Indicator | Check | Healthy | Degraded | Failed |
|-----------|-------|---------|----------|--------|
| Memory MCP | `mcp__haios-memory__memory_stats` | Responds < 2s | Responds > 5s | Timeout/error |
| Work files | `just ready` | Returns list | Empty (may be OK) | Parse error |
| Status gen | `just update-status` | Completes | Warnings | Errors |
| Tests | `pytest` | All pass | Some skip | Failures |
| Git | `git status` | Clean or staged | Uncommitted | Conflicts |

### Observability Locations

| What | Where | Purpose |
|------|-------|---------|
| Session events | `.claude/haios-events.jsonl` | Audit trail |
| Status snapshot | `.claude/haios-status.json` | System state |
| Gate decisions | Memory (via GovernanceLayer logging) | Policy audit |
| Cycle transitions | WORK.md `node_history` | Work item audit |

### Quick Health Check

```bash
just health   # Runs tests + git status
just status   # Shows ETL pipeline status
/status       # Shows hooks/memory/validation/git
```

---

## Recovery Patterns

*What to do when things break.*

### Module Failure Recovery

| Module | Failure Mode | Recovery |
|--------|--------------|----------|
| **GovernanceLayer** | Gate check throws | Log error, DEFAULT DENY (safe) |
| **MemoryBridge** | MCP timeout | Retry once, then continue without memory (degraded) |
| **WorkEngine** | WORK.md parse error | Stop operation, report to operator, don't corrupt file |
| **Config** | YAML invalid | Fail fast on startup, use last known good |

### Session Recovery

| Problem | Symptom | Recovery |
|---------|---------|----------|
| Context exhausted | "~90% used" warning | `/new-checkpoint` then `/clear` then `/coldstart` |
| Session crashed | No checkpoint for work done | `just ready` shows last known state, continue |
| Work item stuck | `in_progress` but nothing happening | Manual transition via WorkEngine or edit WORK.md |
| Memory corrupted | Queries return garbage | Restore from backup, re-ingest from docs |

### Session Handoff Contract (E2-281/E2-282)

The session boundary is a **loading manifest**, not an activity log:

```
/close → /new-checkpoint → /clear → /coldstart
           ↓                           ↓
    Creates manifest              Loads manifest
```

**Checkpoint manifest fields:**
| Field | Purpose |
|-------|---------|
| `load_principles` | Files coldstart MUST read (default: S20, S22) |
| `load_memory_refs` | Concept IDs coldstart MUST query |
| `pending` | Work items for next session |
| `drift_observed` | Principle violations to surface as warnings |

**Operator responsibility:** `/clear` and `/coldstart` only
**System responsibility:** Everything after coldstart - manifest ensures right context loaded

### Data Recovery Priority

```
1. Git (source of truth for code/docs)
2. WORK.md files (source of truth for work state)
3. haios_memory.db (can be rebuilt from docs if needed)
4. haios-status.json (regenerated on demand)
5. Session context (ephemeral, accept loss)
```

### The Nuclear Option

If everything is broken:
1. `git stash` any uncommitted changes
2. Delete `.claude/haios-status.json` (will regenerate)
3. Run `just update-status`
4. Run `/coldstart`
5. Check `just ready` for work state

Memory can be rebuilt by re-ingesting docs if corrupted.

---

## Technical Documentation

L4 content exists across:

| Location | Content |
|----------|---------|
| `CLAUDE.md` | Agent bootstrap, quick reference |
| `.claude/config/` | Current configuration (3 files) |
| `.claude/haios/config/` | Target configuration (Epoch 2.2) |
| `.claude/haios/modules/` | Black box modules (Epoch 2.2) |
| `.claude/lib/` | Python implementation (current) |
| `.claude/hooks/` | Hook handlers |
| `.claude/skills/` | Skill definitions |
| `.claude/agents/` | Subagent definitions |
| `.claude/commands/` | Slash commands |
| `docs/work/archive/INV-052/` | Architecture documentation (17 sections) |
| `docs/work/archive/INV-053/` | Architecture review (simplification) |

---

## INV-052 Section Map

| Section | Content |
|---------|---------|
| S1A-1B | Hooks (current and target) |
| S2A-2G | Lifecycles (session, work, cycles) |
| S3-4 | State storage, data flow |
| S5-7 | Session number, config, recipes |
| S8-13 | Memory, commands, skills, agents, invocation, MCP |
| S14-16 | Bootstrap, information architecture, templates |
| S17 | Modular architecture (5 modules, 7 config files) |
| S17.11-17.15 | Gap resolutions (config, events, errors, migration) |
| S18 | Portable plugin specification |

---

## Derivation Chain

```
L0 (Why) - Immutable
     ↓
L1 (Who) - Immutable
     ↓
L2 (What) - Immutable
     ↓
L3 (Principles) - Immutable
     ↓
L4 (Rules/Specs) - Dynamic ← YOU ARE HERE
```

---

*L4 is dynamic. Updated as implementation evolves.*
*Session 154: Added temporal goals and FinTech principles from L1/L2.*
