---
template: work_item
id: WORK-020
title: Discoverability Architecture
type: investigation
status: complete
owner: Hephaestus
created: 2026-01-26
spawned_by: obs-222-001
chapter: CH-032
arc: discoverability
closed: '2026-02-14'
priority: medium
effort: medium
traces_to:
- REQ-DISCOVER-001
- REQ-DISCOVER-002
- REQ-DISCOVER-003
requirement_refs: []
source_files: []
acceptance_criteria:
- Complete inventory of all entry points (151 catalogued)
- Friction map showing overlaps and gaps (7 friction points documented)
- Proposed three-tier architecture (Tier 1 commands, Tier 2 skills+agents, Tier 3
  recipes)
- Discovery mechanism design (Claude Code auto-discovery + capability cards)
- Spawned implementation work items (5 spawns identified)
blocked_by: []
blocks: []
enables:
- WORK-148
- WORK-149
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-26 19:31:51
  exited: '2026-02-14T14:41:47.247580'
artifacts: []
cycle_docs: {}
memory_refs:
- 85302
- 85303
- 71797
- 81378
- 82201
- 82302
- 85156
- 85210
- 84638
extensions:
  epoch: E2.6
version: '2.0'
generated: 2026-01-26
last_updated: '2026-02-14T14:41:47.251742'
queue_history:
- position: ready
  entered: '2026-02-14T14:27:49.705561'
  exited: '2026-02-14T14:27:49.736059'
- position: working
  entered: '2026-02-14T14:27:49.736059'
  exited: '2026-02-14T14:41:47.247580'
- position: done
  entered: '2026-02-14T14:41:47.247580'
  exited: null
queue_position: done
cycle_phase: done
---
# WORK-020: Discoverability Architecture

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** HAIOS has **151 entry points** (revised from initial estimate of 125) spread across 4 systems with no unified discovery:
- 87 justfile recipes (was 77)
- 34 skills (was 19)
- 19 commands (was 20)
- 11 agents (was 9)

**Friction points:**
1. Agent doesn't know when to use `just X` vs `/command` vs `Skill(skill="X")`
2. Some recipes wrap skills, some call cli.py, some are standalone
3. No `just help` or categorized listing
4. Multiple paths to same action (checkpoint creation: 4 paths; work creation: 4 layers)
5. Skills are in agent's system prompt but recipes require discovery
6. Commands and skills overlap (e.g., `/close` invokes `close-work-cycle` skill)
7. 4 stub skills + 1 deprecated skill in system prompt doing nothing
8. Naming inconsistency across systems (verb vs noun, prefix conventions)

**Root cause:** Organic growth without unified discovery layer. Each system was added to solve specific problems but the aggregate creates cognitive overhead.

---

## Hypotheses

| ID | Hypothesis | Verdict | Confidence |
|----|-----------|---------|------------|
| H1 | Three-tier boundaries can reduce cognitive overhead by 60%+ | **Confirmed** | 0.85 |
| H2 | Capability registry can replace CLAUDE.md hardcoding | **Partially Confirmed** | 0.65 |
| H3 | Orphan recipes classifiable as promote/deprecate/hide | **Confirmed** | 0.90 |
| H4 | Lazy discovery reduces token cost | **Inconclusive** | 0.40 |

### H1: Three-Tier Boundary Clarification (Confirmed, 0.85)

The command→skill→recipe chain already works for 6 core workflows. 35 recipes (40%) are pure Tier 3 implementation details. Enforcing tiers drops agent decision space from 151 → ~40.

### H2: Capability Registry (Partially Confirmed, 0.65)

Claude Code plugin system already auto-discovers commands, skills, and agents. The gap is narrower than expected: (a) recipes have no discovery mechanism, (b) no intent-based matching exists. A lightweight registry would close this.

### H3: Orphan Recipe Classification (Confirmed, 0.90)

Every orphan recipe classifiable: 35 = Tier 3 internals (hide), 18 = Tier 2 agent-useful (some already wrapped), 15 = operator-only tools, remainder = aliases/chains.

### H4: System Prompt Lazy Discovery (Inconclusive, 0.40)

Claude Code plugin system injects all discovered items into system prompt. Configurability unknown. Removing stubs/deprecated is low-hanging fruit. True lazy discovery deferred to E2.8.

---

## Scope

**In Scope:**
- Inventory all entry points
- Identify overlap/redundancy
- Design unified discovery pattern
- Recommend consolidation strategy

**Out of Scope:**
- Implementing all consolidation (spawn follow-up work to E2.7)
- Removing working infrastructure
- Token optimization (E2.8)

---

## Deliverables

- [x] Complete inventory of all entry points (recipes, skills, commands, agents)
- [x] Friction map showing overlaps and gaps
- [x] Proposed three-tier architecture
- [x] Discovery mechanism design
- [ ] Spawn implementation work items (see below)

---

## Findings

### 1. Full Entry Point Inventory (Session 368)

**87 Justfile Recipes by Category:**

| Category | Count | Examples |
|----------|-------|---------|
| Governance | 27 | scaffold, validate, node, link, close-work, observations, status |
| Rhythm | 11 | session-start/end, set-cycle/clear-cycle, events, heartbeat |
| ETL | 9 | status, synthesis, process, ingest, embeddings |
| Plan Tree | 9 | tree, ready, queue, queue-prioritize/commit/unpark/park |
| Loader | 5 | identity, coldstart, session-context, work-options, coldstart-orchestrator |
| Memory | 5 | memory-stats, memory-query, context-load, cycle-phases, pipeline-run |
| Audit | 4 | audit-sync, audit-gaps, audit-stale, audit-decision-coverage |
| Utility | 4 | git-status, git-log, health, checkpoint-latest |
| Git | 4 | commit-session, commit-close, stage-governance, chapter-status |
| Test | 3 | test, test-cov, test-file |

**Implementation patterns:** Python inline (38), cli.py (17), haios_etl (7), scripts (5), shell (8), recipe chains (12).

**34 Skills by Category:**

| Category | Count | Items |
|----------|-------|-------|
| Ceremony (closure) | 4 | close-work-cycle, close-chapter, close-arc, close-epoch |
| Ceremony (feedback) | 4 | arc/chapter/epoch/requirements-review (ALL STUBS) |
| Ceremony (memory) | 4 | retro-cycle, memory-commit, observation-capture (DEPRECATED), observation-triage |
| Ceremony (queue) | 4 | intake, prioritize, commit, unpark |
| Ceremony (session) | 3 | start, checkpoint, end |
| Ceremony (spawn) | 1 | spawn-work |
| Lifecycle | 5 | implementation, investigation, plan-authoring, survey, work-creation |
| Validation | 3 | design-review, dod, plan |
| Utility | 6 | audit, extract-content, ground-cycle, memory-agent, routing-gate, schema-ref |

**19 Commands:** /close, /coldstart, /critique, /haios, /implement, /new-adr, /new-checkpoint, /new-handoff, /new-investigation, /new-plan, /new-report, /new-work, /ready, /reason, /schema, /status, /tree, /validate, /workspace

**11 Agents:** anti-pattern-checker, close-work-cycle-agent, critique-agent, implementation-cycle-agent, investigation-agent, investigation-cycle-agent, preflight-checker, schema-verifier, test-runner, validation-agent, why-capturer

### 2. Cross-System Dependency Map

**Command → Skill → Recipe chains (6 complete):**
- `/close` → retro-cycle + close-work-cycle → `just close-work`, `just update-status`
- `/implement` → implementation-cycle → `just node`, `just set-cycle`
- `/new-work` → work-creation-cycle → `just work` → `just scaffold work_item`
- `/new-plan` → plan-authoring-cycle → `just plan` → `just scaffold implementation_plan`
- `/new-investigation` → investigation-cycle → `just inv` → `just scaffold investigation`
- `/coldstart` → survey-cycle → `just coldstart-orchestrator`, `just ready`, `just queue`

**Skill → Skill chains:**
- close-work-cycle → retro-cycle (prerequisite), dod-validation-cycle, routing-gate, checkpoint-cycle
- implementation-cycle → plan-validation-cycle, design-review-validation, routing-gate, memory-agent
- investigation-cycle → routing-gate
- routing-gate → implementation-cycle / investigation-cycle / work-creation-cycle

### 3. Tier Classification

| Tier | Definition | Count | Discovery Mechanism |
|------|-----------|-------|-------------------|
| **Tier 1: Commands** | Human-invocable, operator-facing | 19 | Claude Code auto-discovery (`.claude/commands/`) |
| **Tier 2: Skills** | Agent-invocable, workflow logic | 34 (29 active) | Claude Code auto-discovery (`.claude/skills/`) |
| **Tier 2: Agents** | Subagent capabilities | 11 | Claude Code auto-discovery (`.claude/agents/`) |
| **Tier 3: Recipes** | Implementation details, never direct-invoked | 35 | None needed (invisible to agent) |
| **Tier 3: Operator recipes** | Maintenance/ETL, human-only | 15 | `just --list` for operator |
| **Tier 2: Unwrapped recipes** | Agent-useful but no skill wrapper | 18 | **GAP: no discovery** |

### 4. Friction Map

| Friction | Severity | Root Cause |
|----------|----------|------------|
| Multiple paths to same action | High | Aliasing + layering without hiding lower layers |
| Agent uses `just X` directly instead of skill | High | Recipes visible at same level as skills |
| 5 useless skills in system prompt (4 stubs + 1 deprecated) | Medium | No cleanup after deprecation |
| Naming inconsistency | Medium | Organic growth, no naming convention |
| 18 unwrapped recipes in agent decision space | Medium | Missing Tier 2 wrappers |
| No intent-based discovery | Low | Would require new infrastructure |
| docs/README.md stale (says 125 entry points, Epoch 2.2) | Low | No auto-sync |

### 5. Three-Tier Architecture Design

```
TIER 1: COMMANDS (human-invocable)
  /close, /coldstart, /implement, /new-*, /status, /haios, /validate, etc.
  Discovery: Claude Code system prompt injection (automatic)
  Audience: Operator types these; agent sees them in system prompt

TIER 2: SKILLS + AGENTS (agent-invocable)
  Skills: lifecycle cycles, ceremonies, validation bridges, utilities
  Agents: critique, preflight, schema-verifier, validation, test-runner, etc.
  Discovery: Claude Code system prompt injection (automatic)
  Audience: Agent invokes via Skill() or Task() tool

TIER 3: RECIPES (implementation details)
  Internal: scaffold, set-cycle, node, link, cascade, etc.
  Operator-only: ETL, git commit helpers, migration
  Discovery: Not needed for agent; `just --list` for operator
  Audience: Called by skills/commands, never by agent directly
```

**Key design decisions:**
1. **Recipes are invisible to agents.** Skills that need recipes call them internally. Agent never runs `just X` directly.
2. **Commands are thin wrappers.** `/close` invokes retro-cycle + close-work-cycle. The command is the entry point, the skill is the logic.
3. **18 unwrapped recipes need promotion.** Either wrap in existing skills or create new thin skills.
4. **Remove 5 useless system prompt entries.** Delete 4 stub skills, remove deprecated observation-capture-cycle.

### 6. Discovery Mechanism Design

**Current state (already working):**
- Commands: auto-discovered from `.claude/commands/`
- Skills: auto-discovered from `.claude/skills/`
- Agents: auto-discovered from `.claude/agents/`

**Gap: recipes have no agent-facing discovery.** But if we enforce Tier 3 (recipes are implementation details), no recipe discovery is needed.

**Remaining gap: intent-based discovery ("what tool handles validation?").**
Options:
1. **Agent Capability Cards (WORK-144):** Already planned in E2.6 observability arc. Each agent gets a structured capability card. This closes the agent discovery gap.
2. **Skill categorization in frontmatter:** Add `category:` field to skill frontmatter. Enables `discover(category="ceremony")` queries. Deferred to E2.7.
3. **Recipe consolidation:** Promote 18 unwrapped recipes to skills or wrap in existing skills. This is implementation work for E2.7.

**Recommended approach for E2.6:**
- Agent Capability Cards (WORK-144, already planned)
- Remove stubs and deprecated skills (cleanup)
- Document the three-tier model in an ADR

**Deferred to E2.7 Composability:**
- Recipe consolidation (wrap 18 orphans)
- Skill categorization frontmatter
- Recipe namespace hiding (e.g., `just _internal-scaffold` prefix convention)

---

## Spawned Work Items

| Spawn | Title | Type | Arc | Deferred To |
|-------|-------|------|-----|-------------|
| SPAWN-1 | Remove Stub and Deprecated Skills | cleanup | discoverability | E2.6 (low effort) |
| SPAWN-2 | Three-Tier Architecture ADR | design | discoverability | E2.6 |
| SPAWN-3 | Recipe Consolidation (18 orphans) | implementation | discoverability | E2.7 |
| SPAWN-4 | Skill Categorization Frontmatter | design | discoverability | E2.7 |
| SPAWN-5 | docs/README.md Refresh | cleanup | observability | E2.6 (low effort) |

---

## History

### 2026-02-14 - Investigation Complete (Session 368)
- Full inventory: 151 entry points (87 recipes, 34 skills, 19 commands, 11 agents)
- Cross-system dependency map built
- Three-tier architecture designed
- 4 hypotheses tested: 2 confirmed, 1 partial, 1 inconclusive
- 5 spawned work items identified

### 2026-01-28 - Populated (Session 256)
- Filled in context with friction analysis
- Defined hypotheses and scope
- Created exploration plan

### 2026-01-26 - Created (Session 244)
- Initial creation from obs-222-001

---

## References

- @.claude/haios/epochs/E2_3/observations/obs-222-001.md (spawn source)
- @.claude/haios/epochs/E2_6/arcs/discoverability/ARC.md
- Memory: 71797, 81378, 82201, 82302 (recipe architecture)
- Memory: 85156, 85210 (agent discoverability gap)
- Memory: 84638 (command/skill location pattern)
