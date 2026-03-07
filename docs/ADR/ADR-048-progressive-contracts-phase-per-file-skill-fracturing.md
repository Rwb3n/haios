---
template: architecture_decision_record
status: accepted
date: 2026-02-22
adr_id: ADR-048
title: "Progressive Contracts - Phase-Per-File Skill Fracturing"
author: Hephaestus
session: 420
lifecycle_phase: decide
decision: accepted
spawned_by: WORK-163
related: [ADR-045, ADR-047]
backlog_id: WORK-163
memory_refs: [85815]
version: "1.1"
---
# ADR-048: Progressive Contracts - Phase-Per-File Skill Fracturing

> **Status:** Accepted
> **Date:** 2026-02-22
> **Decision:** Accepted

---

## Decision Criteria (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Document alternatives | MUST | List at least 2 options in Considered Options section |
| Explain WHY | MUST | Provide rationale for chosen option in Decision section |
| Link to memory | SHOULD | Store decision reasoning via `ingester_ingest` |
| Get operator approval | MUST | Update decision field from "pending" to "accepted/rejected" |

---

## Context

Lifecycle SKILL.md files (implementation-cycle, investigation-cycle, retro-cycle) are monolithic contracts ranging from 16K-21K characters. An agent executing a 30-line DONE phase loads all 468 lines of the implementation-cycle contract. This wastes tokens on phases the agent won't execute in the current invocation.

Memory 85815 identifies context-switching token cost as a key overhead dimension: "How many tokens are spent re-loading context?" Progressive disclosure — loading only the current phase's behavioral contract — directly reduces this.

**Audit (S420):**

| Skill | Chars | Lines | Category |
|-------|-------|-------|----------|
| implementation-cycle | 21,500 | 468 | lifecycle |
| retro-cycle | 20,057 | 455 | ceremony |
| investigation-cycle | 16,326 | 410 | lifecycle |
| close-work-cycle | 13,574 | 313 | lifecycle |
| plan-authoring-cycle | 13,494 | 336 | lifecycle |
| observation-triage-cycle | 11,811 | 300 | lifecycle |
| open-epoch-ceremony | 14,140 | 375 | ceremony |

The top 7 skills account for ~111K chars. The bottom 23 are all under 9K and do not need fracturing.

**Key structural observation:** Each SKILL.md contains (a) phase-specific behavioral contracts (gates, actions, exit criteria, tool lists), (b) shared reference material (Composition Map, Quick Reference, Key Design Decisions), and (c) routing boilerplate (cycle diagram, "When to Use"). An agent in the DO phase needs only (a-DO). Categories (b) and (c) are reference material loaded on demand.

**Note:** Existing fractured templates in `.claude/templates/implementation/{PLAN,DO,CHECK,DONE}.md` are NOT the same concern. Those are scaffolding templates for work artifacts. They are unwired (no consumer references them) and were created in a weak session. This ADR addresses the **orchestration contract** (SKILL.md), not the artifact template.

---

## Decision Drivers

- E2.8 exit criterion: "Governance overhead measurably reduced"
- L3.20 Proportional Governance: overhead scales with blast radius, not uniformly
- L1.6 Limited Time: maximize value per operator-hour (fewer wasted tokens = faster sessions)
- Memory 85815: context-switching token cost identified as key overhead dimension
- Agent only needs ONE phase contract at a time — other phases are dead weight

---

## Considered Options

### Option A: Phase-per-file fracturing with hook-based auto-injection (CHOSEN)

**Description:** Split each large SKILL.md into a slim router + per-phase contract files. Hooks auto-inject the current phase's contract:
- PostToolUse injects on phase transition (precise timing)
- UserPromptSubmit injects on every prompt (fallback/recovery)

**Directory structure:**
```
.claude/skills/implementation-cycle/
  SKILL.md              # ~80 lines: router, cycle diagram, phase table, "When to Use"
  phases/
    PLAN.md             # Full PLAN behavioral contract (gates, actions, exit criteria)
    DO.md               # Full DO behavioral contract
    CHECK.md            # Full CHECK behavioral contract
    DONE.md             # Full DONE behavioral contract
    CHAIN.md            # Full CHAIN behavioral contract
  reference/
    decisions.md        # Design decisions, rationale (load on demand)
    composition.md      # Composition map, quick ref (load on demand)
```

**Injection mechanism (belt and suspenders):**
1. PostToolUse on `Skill("implementation-cycle")`: after `advance_cycle_phase()`, read phase file and return as output
2. UserPromptSubmit: check `haios-status-slim.json` for `active_cycle` + `current_phase`, read phase file and inject

**Pros:**
- ~80% token reduction per phase invocation (21K -> ~3-4K)
- Zero agent cognitive overhead (hook auto-injects)
- Each phase file is self-contained and independently maintainable
- Reference material available on demand (not forced)
- Builds on existing hook infrastructure (advance_cycle_phase, additionalContext)

**Cons:**
- Hook infrastructure changes required (PostToolUse + UserPromptSubmit extensions)
- Phase files must be self-contained (no cross-references to other phases)
- Migration effort for each skill

### Option B: Engine-function phase loader

**Description:** Keep monolithic SKILL.md but add a Python function `get_phase_contract(skill, phase)` that extracts and returns only the current phase section. Agent calls the function instead of loading the full file.

**Pros:**
- No file restructuring needed
- Single source of truth (one file)

**Cons:**
- Requires new MCP tool or engine function
- Markdown section parsing is fragile (depends on heading structure)
- Monolithic file still hard to maintain and review
- Agent must remember to call the function (cognitive overhead)

### Option C: Inline collapsible sections (HTML details tags)

**Description:** Use `<details>` tags in SKILL.md to visually hide phase content. Agent sees summary line, expands on demand.

**Pros:**
- No restructuring, single file
- No infrastructure changes

**Cons:**
- Does NOT reduce token consumption — Claude loads the full file regardless of HTML structure
- Only a visual hint, not actual progressive disclosure
- **Rejected: fails to address the core problem (token waste)**

---

## Decision

**Option A: Phase-per-file fracturing with dual hook-based auto-injection.**

The agent never needs to explicitly load a phase contract. The system auto-injects the right contract at the right time:

1. **PostToolUse** fires after `advance_cycle_phase()` advances to a new phase. It reads `.claude/skills/{cycle}/phases/{new_phase}.md` and returns the content as hook output. The agent sees the contract exactly once per transition.

2. **UserPromptSubmit** fires on every prompt. If `haios-status-slim.json` shows an active lifecycle cycle, it reads the current phase's contract file and injects it. This provides recovery if the agent missed the PostToolUse output (e.g., after context compaction).

The slim SKILL.md router remains the skill description that Claude Code's skill system loads. It contains the cycle diagram and phase table — enough for the agent to understand the overall flow — but delegates phase-specific behavioral contracts to per-phase files.

**Self-containment rule:** Each phase file MUST include all information needed to execute that phase. No "see PLAN phase for..." cross-references. If two phases share a pattern (e.g., CHAIN routing), the shared content is duplicated in each phase file. Duplication is acceptable when the alternative is requiring multi-file reads.

---

## Consequences

**Positive:**
- ~80% token reduction per lifecycle skill invocation
- Phase contracts become independently reviewable and testable
- Hook-based injection means zero agent cognitive overhead
- Dual injection (PostToolUse + UserPromptSubmit) provides robustness
- Reference material (decisions, composition map) loaded only when needed
- Pattern reusable across all 7 large skills

**Negative:**
- Two hook handlers need modification (PostToolUse, UserPromptSubmit)
- Phase files must be self-contained (some content duplication, especially CHAIN)
- Existing tests that assert on SKILL.md content may need updating
- Migration is per-skill work (not automatic)

**Neutral:**
- The monolithic SKILL.md is replaced by a slim router, not deleted
- Fractured templates in `.claude/templates/implementation/` remain unwired (separate concern)
- Plan template (`implementation-v2.md`) is unaffected (loaded once, tightly coupled layers)

---

## Implementation

### Prototype (WORK-163 — this work item)
- [ ] Fracture implementation-cycle SKILL.md into router + 5 phase files + 2 reference files
- [ ] Extend PostToolUse to inject phase contract after advance_cycle_phase
- [ ] Extend UserPromptSubmit to inject current phase contract on every prompt
- [ ] Verify skill description still triggers correctly
- [ ] Measure token savings (before/after char count)

### Migration (follow-up work items)
- [ ] Fracture investigation-cycle
- [ ] Fracture retro-cycle
- [ ] Fracture close-work-cycle
- [ ] Fracture plan-authoring-cycle
- [ ] Fracture observation-triage-cycle
- [ ] Fracture open-epoch-ceremony
- [ ] Clean up unwired `.claude/templates/implementation/{PLAN,DO,CHECK,DONE}.md` files

---

## References

- Memory 85815: Context-switching token cost dimension
- WORK-163: Progressive Contracts (CH-062, query arc)
- ADR-045: Three-tier entry point architecture (skill loading)
- ADR-047: Tiered coldstart context injection (progressive loading precedent)
- WORK-168: Cycle phase auto-advancement (PostToolUse hook)
- WORK-064: State visibility in additionalContext (PreToolUse hook)

---
