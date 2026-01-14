---
template: architecture_decision_record
status: accepted
date: 2025-12-18
adr_id: ADR-038
title: M2-Governance Symphony Architecture
author: Hephaestus
session: 83
lifecycle_phase: decide
decision: accepted
spawned_by: Session-78
related:
- ADR-033
- ADR-034
- ADR-035
- ADR-037
milestone: M2-Governance
backlog_id: E2-076
memory_refs:
- 71926-71934
version: '1.1'
generated: '2025-12-29'
last_updated: '2025-12-29T10:09:49'
---
# ADR-038: M2-Governance Symphony Architecture

@docs/README.md
@docs/epistemic_state.md

> **Status:** Accepted
> **Date:** 2025-12-18
> **Decision:** Implement governance as a "Symphony" - coordinated components working in harmony

---

## Context

HAIOS needed a governance system that guides agents toward correct workflows without hard blocking. The system needed to be:
- Observable (know what's happening)
- Enforceable (prevent mistakes)
- Learnable (compound knowledge across sessions)
- Non-brittle (degrade gracefully)

Previous approaches (Epoch 1) were ad-hoc: hooks existed but weren't coordinated, commands existed but weren't connected, memory stored but wasn't retrieved.

---

## Decision Drivers

- **Doing right should be easy:** The governance system should guide, not block
- **Observable state:** Agents need awareness of system state (vitals, milestones, blocked items)
- **Learning compounds:** Knowledge from past sessions should inform current work
- **Composition over monoliths:** Build from existing primitives (hooks, commands, skills, justfiles)
- **Progressive disclosure:** L1/L2/L3 layers of detail as needed

---

## Considered Options

### Option A: Hard Enforcement
**Description:** Hooks strictly block all non-conforming actions.

**Pros:**
- Guarantees compliance
- No deviation possible

**Cons:**
- Brittle - edge cases break workflows
- Frustrating UX for agents
- Can't handle legitimate exceptions

### Option B: Pure Cultural Convention
**Description:** Document best practices, rely on agent discipline.

**Pros:**
- Flexible
- No infrastructure needed

**Cons:**
- Inconsistent execution
- No observability
- Learning doesn't compound

### Option C: Symphony Pattern (Chosen)
**Description:** Coordinated components work together - hooks enforce boundaries, commands scaffold structure, memory stores/retrieves learnings, vitals provide awareness.

**Pros:**
- Balanced enforcement (soft prompts + hard gates)
- Observable via vitals/events
- Learnable via memory loop
- Composable from existing primitives

**Cons:**
- More complex than alternatives
- Requires coordination between components

---

## Decision

Implement **M2-Governance as a Symphony** with four coordinated movements:

### 1. RHYTHM (Heartbeat)
**Component:** Hooks + Justfile + haios-status.json

| Element | Purpose | Implementation |
|---------|---------|----------------|
| UserPromptSubmit | Inject vitals, reminders | E2-076d |
| PostToolUse | Auto-timestamps, cascade triggers | E2-076e |
| UpdateHaiosStatus | Refresh system state | E2-081 |
| `just heartbeat` | Periodic status update | E2-081 |

### 2. DYNAMICS (Thresholds)
**Component:** UserPromptSubmit threshold signals

| Threshold | Condition | Signal |
|-----------|-----------|--------|
| APPROACHING | milestone > 90% | Excitement toward completion |
| BOTTLENECK | blocked > 3 | Systemic dependency issues |
| ATTENTION | stale > 5 | Items need review |
| MOMENTUM | completed > 3 | Celebrate progress |

### 3. LISTENING (Memory Loop)
**Component:** Commands + Memory MCP

| Phase | Implementation |
|-------|----------------|
| Store | Stop hook extracts reasoning, ingester stores |
| Retrieve | Commands query memory before action (E2-083) |
| Compound | Targeted queries using backlog_ids + focus |

### 4. RESONANCE (Events)
**Component:** haios-events.jsonl

| Event | Trigger | Purpose |
|-------|---------|---------|
| session_start | Coldstart | Track session boundaries |
| session_end | Session end | Close session |
| item_complete | Cascade | Track completions |
| milestone_progress | UpdateHaiosStatus | Track momentum |

### Component Map

```
                         SYMPHONY
                            |
        +-------------------+-------------------+
        |                   |                   |
     RHYTHM              DYNAMICS           LISTENING
   (Heartbeat)         (Thresholds)      (Memory Loop)
        |                   |                   |
   +---------+         +---------+         +---------+
   |Vitals   |         |APPROACH |         |Store    |
   |Cascade  |         |BOTTLENCK|         |Retrieve |
   |Events   |         |ATTENTION|         |Compound |
   +---------+         |MOMENTUM |         +---------+
                       +---------+
                            |
                       RESONANCE
                        (Events)
```

### DAG Topology (E2-076 Addendum - Session 142)

The Symphony architecture is implemented as a Directed Acyclic Graph:

**Nodes (Documents):**
| Node Type | Location | Purpose |
|-----------|----------|---------|
| Work Items | `docs/work/active/{id}/WORK.md` | Work tracking |
| Plans | `docs/work/active/{id}/plans/PLAN.md` | Implementation design |
| Investigations | `docs/investigations/INVESTIGATION-*.md` | Research |
| Checkpoints | `docs/checkpoints/*.md` | Session summaries |
| ADRs | `docs/ADR/ADR-*.md` | Architecture decisions |
| Status | `.claude/haios-status*.json` | System state |

**Edges (Dependencies):**
| Edge Type | Frontmatter Field | Cascade Behavior |
|-----------|-------------------|------------------|
| blocked_by | `blocked_by: [id]` | Blocks until dependency complete |
| spawned_by | `spawned_by: id` | Provenance tracking |
| enables | `enables: [id]` | Unblocks on completion |
| related | `related: [id]` | Informational |
| backlog_ids | `backlog_ids: [id]` | Checkpoint→Work link |

**Cascading Updates:**
| Trigger | Hook | Action |
|---------|------|--------|
| Work status change | PostToolUse | Run `just cascade {id} {status}` |
| YAML edit | PostToolUse | Update `last_updated` timestamp |
| Session start | UserPromptSubmit | Inject vitals from status files |
| Validation outcome | Cycle Skills | Log to governance-events.jsonl |

**Progressive Context Loading:**
| Layer | File | Lines | When |
|-------|------|-------|------|
| L0 Vitals | UserPromptSubmit injection | ~10 | Every prompt |
| L1 Slim | haios-status-slim.json | ~50 | Coldstart |
| L2 Full | haios-status.json | ~500 | On demand |
| L3 Source | Individual files | Varies | Deep dive |

### Enforcement Spectrum

| Level | Description | M2 Examples |
|-------|-------------|-------------|
| L0: None | No enforcement | - |
| L1: Observable | Log, don't enforce | Events, vitals |
| L2: Prompted | Soft reminders | RFC 2119 in UserPromptSubmit |
| L3: Gated | Block invalid actions | PreToolUse governed paths |
| L4: Automated | System drives | PostToolUse auto-timestamps |

---

## Consequences

**Positive:**
- Agents have operational awareness (vitals in every prompt)
- Milestone progress is visible and motivating
- Learning compounds via targeted memory queries
- Governance feels supportive, not restrictive

**Negative:**
- Context overhead (~50 lines vitals per prompt)
- Requires multiple components to work together
- Some cultural discipline still required (cycles not mechanistically enforced)

**Neutral:**
- Sets foundation for M3-Cycles (formalizing the implementation cycle)
- Memory grows continuously (requires synthesis to manage)

---

## Implementation (Complete)

- [x] E2-076: DAG Governance Architecture ADR
- [x] E2-076b: Frontmatter Schema (DAG edge fields)
- [x] E2-076d: Vitals Injection (L1/L2 progressive static context)
- [x] E2-076e: Cascade Hooks (heartbeat mechanism)
- [x] E2-078: Coldstart Work Delta (momentum awareness)
- [x] E2-079: CLAUDE.md De-bloat (L1/L3 REFS architecture)
- [x] E2-080: Justfile Execution Toolkit
- [x] E2-081: Heartbeat Scheduler
- [x] E2-082: Dynamic Thresholds
- [x] E2-083: Proactive Memory Query
- [x] E2-084: Event Log Foundation

**Milestone M2-Governance: 100% Complete (Session 83)**

---

## References

- **ADR-033:** Work Item Lifecycle (DoD)
- **ADR-034:** Document Ontology (lifecycle phases)
- **ADR-035:** RFC 2119 Governance Signaling
- **ADR-037:** Hybrid Retrieval Architecture (memory modes)
- **Session 78:** Symphony design origin
- **Session 83:** M2 completion

---
