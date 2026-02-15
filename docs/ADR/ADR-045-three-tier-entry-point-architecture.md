---
template: architecture_decision_record
status: accepted
date: 2026-02-15
adr_id: ADR-045
title: "Three-Tier Entry Point Architecture"
author: Hephaestus
session: 378
lifecycle_phase: decide
decision: accepted
spawned_by: WORK-149
traces_to:
- REQ-DISCOVER-002
- REQ-DISCOVER-003
memory_refs: [85302, 85303, 82302]
version: "1.1"
generated: 2026-02-15
last_updated: '2026-02-15T22:35:00'
---
# ADR-045: Three-Tier Entry Point Architecture

@docs/work/active/WORK-020/WORK.md
@docs/work/active/WORK-149/WORK.md

> **Status:** Accepted
> **Date:** 2026-02-15
> **Decision:** All HAIOS entry points are classified into three tiers with enforced boundaries

---

## Decision Criteria (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Document alternatives | MUST | 3 options documented in Considered Options |
| Explain WHY | MUST | Rationale in Decision section |
| Link to memory | SHOULD | Memory 85302, 85303, 82302 |
| Get operator approval | MUST | Accepted (this session) |

---

## Context

HAIOS has **151 entry points** (as of Session 368) spread across four systems with no unified discovery model:

| System | Count | Location |
|--------|-------|----------|
| Justfile recipes | 87 | `justfile` |
| Skills | 34 (29 active + 4 stubs + 1 deprecated) | `.claude/skills/` |
| Commands | 19 | `.claude/commands/` |
| Agents | 11 | `.claude/agents/` |

Investigation WORK-020 (Session 368) identified **8 friction points** caused by organic growth without unified discovery:

1. **Multiple paths to same action** (High) -- e.g., checkpoint creation has 4 paths
2. **Agent uses `just X` directly instead of skill** (High) -- recipes visible at same level as skills
3. **5 useless skills in system prompt** (Medium) -- 4 stubs + 1 deprecated doing nothing
4. **Naming inconsistency** (Medium) -- verb vs noun, prefix conventions vary
5. **18 unwrapped recipes in agent decision space** (Medium) -- missing Tier 2 wrappers
6. **Commands and skills overlap** (Medium) -- e.g., `/close` invokes `close-work-cycle` skill
7. **No intent-based discovery** (Low) -- agent cannot ask "what handles validation?"
8. **docs/README.md stale** (Low) -- says 125 entry points from Epoch 2.2

**Root cause:** Each system was added to solve specific problems, but the aggregate creates cognitive overhead. The agent's decision space is 151 options when it should be ~40.

---

## Decision Drivers

- Agent decision space too large (151 undifferentiated options)
- No enforced boundary between operator-facing, agent-facing, and internal entry points
- Multiple paths to the same action create confusion and inconsistency
- Claude Code plugin system already auto-discovers commands, skills, and agents -- the mechanism exists but tier boundaries do not

---

## Considered Options

### Option A: Flat Namespace (Status Quo)

**Description:** Keep all 151 entry points at the same level. Agent chooses from full set.

**Pros:**
- No migration work
- Maximum flexibility

**Cons:**
- 151 options in agent decision space
- No clear guidance on when to use `just X` vs `Skill()` vs `/command`
- Friction points persist and grow with each new entry point

### Option B: Two-Tier (Commands + Everything Else)

**Description:** Split into human-invocable commands and everything else.

**Pros:**
- Simple model
- Clear human/agent boundary

**Cons:**
- "Everything else" still contains 132 items (skills + agents + recipes)
- No distinction between agent-invocable skills and internal implementation recipes
- Agent still sees too many options

### Option C: Three-Tier (Commands, Skills+Agents, Recipes)

**Description:** Commands for humans, skills+agents for the agent, recipes as hidden implementation details.

**Pros:**
- Agent decision space drops from 151 to ~40 (Tier 1 + Tier 2)
- Clear audience for each tier
- Leverages existing Claude Code auto-discovery for Tiers 1 and 2
- Recipes become invisible to agent -- called only by skills/commands internally

**Cons:**
- 18 unwrapped recipes need promotion to Tier 2 (migration work)
- Must enforce "agent never calls `just X` directly" discipline

---

## Decision

**Option C: Three-tier entry point architecture.**

All HAIOS entry points are classified into exactly one of three tiers based on audience and invocation pattern.

### Tier Definitions

| Tier | Name | Audience | Invocation | Count (S368) | Discovery Mechanism |
|------|------|----------|------------|--------------|---------------------|
| **1** | **Commands** | Human (operator) | Operator types `/command` | 19 | Claude Code auto-discovery from `.claude/commands/` |
| **2** | **Skills + Agents** | Agent | `Skill(skill="X")` or `Task(subagent_type="X")` | 45 (34 skills + 11 agents) | Claude Code auto-discovery from `.claude/skills/` and `.claude/agents/` |
| **3** | **Recipes** | Internal | Called by Tier 1/2 code only | 87 | None needed -- not surfaced to agent via auto-discovery |

This architecture directly satisfies **REQ-DISCOVER-003** (agent discovers capabilities via infrastructure, not CLAUDE.md): Tiers 1 and 2 use Claude Code's built-in auto-discovery mechanism, which reads `.claude/commands/`, `.claude/skills/`, and `.claude/agents/` directories at startup and injects discovered items into the agent's system prompt. No hardcoded paths in CLAUDE.md are needed for the agent to find available commands, skills, or agents.

### Tier Assignment Criteria

To determine which tier a new entry point belongs to, apply these rules in order:

| Rule | Tier | Rationale |
|------|------|-----------|
| Is it typed by the operator in the Claude Code chat? | **Tier 1 (Command)** | Commands are the operator's in-conversation interface |
| Is it invoked by the agent via `Skill()` or `Task()`? | **Tier 2 (Skill/Agent)** | Skills and agents are the agent's interface |
| Is it called only by other code (skills, commands, modules)? | **Tier 3 (Recipe)** | Recipes are implementation details |
| Does it wrap a Tier 3 recipe for agent use? | **Tier 2 (Skill)** | Thin skill wrappers expose recipe functionality to the agent |
| Is it an operator-only maintenance tool (terminal, not chat)? | **Tier 3 (Recipe)** | Operator uses `just X` in terminal directly; agent does not |

**Note on operator context:** Tier 1 commands are operator entry points *within the agent conversation* (Claude Code chat). Tier 3 recipes used by the operator *outside the conversation* (e.g., `just test` in a terminal) remain Tier 3 — they are tools the operator uses independently of the agent.

**Key rule:** The agent MUST NOT run `just X` directly. All recipe functionality accessed by the agent goes through Tier 2 skill wrappers. Enforcement: the existing PreToolUse governance hook blocks unauthorized `just` commands; additional Tier 3 enforcement is deferred to the recipe namespace hiding work (E2.7).

### Tier 2 Subcategories (Skills)

| Category | Count | Examples |
|----------|-------|---------|
| Ceremony (closure) | 4 | close-work-cycle, close-chapter, close-arc, close-epoch |
| Ceremony (feedback) | 4 | arc/chapter/epoch/requirements-review (stubs) |
| Ceremony (memory) | 3 | retro-cycle, memory-commit, observation-triage |
| Ceremony (queue) | 4 | intake, prioritize, commit, unpark |
| Ceremony (session) | 3 | start, checkpoint, end |
| Ceremony (spawn) | 1 | spawn-work |
| Lifecycle | 5 | implementation, investigation, plan-authoring, survey, work-creation |
| Validation | 3 | design-review, dod, plan |
| Utility | 6 | audit, extract-content, ground-cycle, memory-agent, routing-gate, schema-ref |

### Tier 3 Subcategories (Recipes)

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

### Complete Cross-System Dependency Chains

Six complete command-to-recipe chains exist:

```
/close       -> retro-cycle + close-work-cycle -> just close-work, just update-status
/implement   -> implementation-cycle           -> just node, just set-cycle
/new-work    -> work-creation-cycle            -> just work -> just scaffold work_item
/new-plan    -> plan-authoring-cycle           -> just plan -> just scaffold implementation_plan
/new-inv     -> investigation-cycle            -> just inv -> just scaffold investigation
/coldstart   -> survey-cycle                   -> just coldstart-orchestrator, just ready, just queue
```

These chains demonstrate the pattern: **Command (Tier 1) -> Skill (Tier 2) -> Recipe (Tier 3)**.

### Full Tier Assignment

This ADR defines the tier model and assignment criteria. The complete per-entry-point tier assignment for all 151 entry points is documented in WORK-020 (docs/work/active/WORK-020/WORK.md), Section 3 ("Tier Classification") and Section 1 ("Full Entry Point Inventory"). WORK-020 is the authoritative source for individual assignments. REQ-DISCOVER-002's acceptance test ("each entry point assigned to exactly one tier") is satisfied by WORK-020's classification combined with this ADR's criteria for future entry points.

---

## Consequences

**Positive:**
- Agent decision space reduced from 151 to ~40 first-class entry points
- Clear boundaries for where new entry points belong
- Leverages Claude Code's existing auto-discovery mechanism for Tiers 1 and 2
- Tier 3 recipes are not surfaced to the agent via auto-discovery, eliminating "should I use `just X` or `Skill()`?" confusion (note: recipes remain readable via justfile if the agent looks; enforcement via hooks and namespace hiding closes this gap)
- Satisfies REQ-DISCOVER-002 (three-tier model with clear boundaries)
- Satisfies REQ-DISCOVER-003 (agent discovers via infrastructure, not CLAUDE.md hardcoding)

**Negative:**
- 18 unwrapped recipes currently in agent decision space need promotion to Tier 2 (skill wrappers) or demotion to Tier 3 (hide from agent)
- Discipline required: agent must never call `just X` directly; enforcement relies on PreToolUse hooks and future namespace hiding
- Recipe naming does not currently signal "internal" status (no prefix convention)
- Multiple paths to the same action still exist (e.g., `/close` -> skill -> recipe chain); tiering clarifies which path is canonical for each audience but does not eliminate path multiplicity

**Neutral:**
- Agent Capability Cards (WORK-144, complete S375) complement this decision by enabling intent-based discovery within Tier 2
- Skill categorization frontmatter (deferred to E2.7) would further improve Tier 2 discoverability
- CLAUDE.md currently contains a hardcoded Agents table (11 entries with models and requirements); this partially contradicts REQ-DISCOVER-003's intent. Removing CLAUDE.md hardcoding is a separate migration step, not addressed by this ADR

---

## Implementation

- [x] Three-tier model defined (this ADR)
- [x] Tier assignment criteria documented (this ADR)
- [x] Agent Capability Cards designed (WORK-144, complete S375)
- [ ] Remove stub and deprecated skills (WORK-148, E2.6)
- [ ] Tier 3 enforcement hook -- extend PreToolUse to block agent `just X` calls for Tier 3 recipes (E2.7)
- [ ] Recipe consolidation -- 18 unwrapped recipes (E2.7)
- [ ] Skill categorization frontmatter (E2.7)
- [ ] Recipe namespace hiding (E2.7)
- [ ] Remove CLAUDE.md hardcoded agent table in favor of infrastructure discovery (E2.8)

---

## References

- WORK-020: Discoverability Architecture investigation (S368) -- source findings and full tier assignment
- WORK-149: This ADR's work item
- WORK-144: Agent Capability Cards (S375, complete)
- WORK-148: Remove Stub and Deprecated Skills (E2.6, pending)
- REQ-DISCOVER-002: Three-tier entry point model with clear boundaries
- REQ-DISCOVER-003: Agent discovers capabilities via infrastructure, not CLAUDE.md
- Memory: 85302 (agents should never run `just X` directly)
- Memory: 85303 (tiering drops decision space from 151 to ~40)
- Memory: 82302 (justfile recipes -> cli.py -> modules is the correct layer stack)

---
