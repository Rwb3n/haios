# generated: 2025-12-26
# System Auto: last updated on: 2026-01-02T19:44:41
# HAIOS Core Invariants (L1 Context)

> **SUPERSEDED:** This file is replaced by `.claude/haios/manifesto/L3-requirements.md`
> Content here was L3 (operational requirements) mislabeled as L1 (principal identity).
> See Manifesto Corpus for correct hierarchy. Retained for historical reference only.

---

> Evergreen operational patterns and anti-patterns. Load at coldstart for agent grounding.
> **L0 prerequisite:** See `north-star.md` for WHY (mission, purpose, principles).
> Source: INV-037 extraction from Genesis_Architect_Notes.md, deprecated_AGENT.md, HAIOS-RAW ADRs

---

## Philosophy (WHY HAIOS Exists)

### Certainty Ratchet
HAIOS ensures project state moves only toward increasing certainty, clarity, and quality.

### Agency Engine
System telos is "sovereign creative agency" - reducing operator cognitive load while maintaining quality.

### SDD Framework (Specification-Driven Development)
70% effort on specification, 30% on implementation. Specification is the deliverable.

---

## Architectural Patterns (HOW HAIOS Works)

### Three Pillars
1. **Evidence-Based:** Decisions require evidence, not assumptions
2. **Durable Context:** Knowledge persists across sessions via memory
3. **Separation of Duties:** Operator (strategy) vs Agent (execution)

### Governance Flywheel
Principles -> Enforcement -> Feedback -> Improvement (closed loop)
Every success and failure results in durable system improvement.

### Golden Thread
Traceability from request through analysis, initiative, and execution.

---

## Operational Rules (WHAT HAIOS Requires)

### Universal Idempotency
All mutable operations MUST be idempotent. Re-running is always safe.

### Structured Mistrust
Assume agents will fail in predictable ways. Design for graceful degradation.

### 5-Phase Operational Loop
ANALYZE -> BLUEPRINT -> CONSTRUCT -> VALIDATE -> IDLE

### Work Before Document
Work file MUST exist before creating:
- Implementation plans (`/new-plan` → `just plan`)
- Investigations (`/new-investigation` → `just inv`)

Flow: `/new-work` → `work-creation-cycle` → `/new-plan` or `/new-investigation`

### Subagent Isolation
High-risk operations MUST be delegated to isolated subagents.
Subagent boundaries prevent cascading failures and enable focused validation.

### Definition of Done (ADR-033)
A work item is complete when:
- **Tests pass** - Verification that implementation works
- **WHY captured** - Reasoning stored to memory
- **Docs current** - CLAUDE.md, READMEs updated if behavior changed

### WHY Primacy
WHY is most important. Tests verify WHAT works. Docs explain HOW.
But WHY - the reasoning behind decisions - compounds across sessions.

### Irreversible Operations Require Permission
Agent **MUST NOT** perform irreversible operations without explicit operator permission:
- **MUST NOT** kill long-running processes (synthesis, background tasks)
- **MUST NOT** delete data or files without confirmation
- **MUST NOT** force-push or rewrite git history
- **MUST NOT** drop database tables or truncate data

When in doubt about reversibility, ASK. Stalled processes may be sleeping, not dead.

---

## LLM Anti-Patterns (WHY Governance Exists)

These are fundamental LLM behaviors - architectural, not fixable:

| Pattern | Truth | Mitigation |
|---------|-------|------------|
| **Assume over verify** | LLMs predict likely values, don't verify | Gates force verification |
| **Generate over retrieve** | Creation is default mode | Glob/Read before Write |
| **Move fast** | No internal friction mechanism | Blockers > suggestions |
| **Optimistic confidence** | No episodic memory for failures | External memory systems |
| **Pattern-match solutions** | Edge cases underrepresented | DoD requires edge case testing |
| **Ceremonial completion** | Literal task, not integration | DoD requires integration test |

---

## Context Levels (INV-037)

Context layers for token budget management:

| Level | Name | Content | Change Rate |
|-------|------|---------|-------------|
| **L1** | Invariants | This file (pure L1) | Rarely (evergreen) |
| **L1+L2** | Bootstrap | CLAUDE.md (CLI default: L1 rules + L2 reference tables) | Mixed |
| **L2** | Operational | haios-status.json, epistemic_state.md | Per-session |
| **L3** | Session | Checkpoints, memory queries | Every session |

CLAUDE.md is CLI bootstrap (always loaded, contains both invariant MUST rules and operational quick-reference).
This file is pure L1 (evergreen philosophy/patterns). L2/L3 are session-specific via coldstart.

---

*Extracted: Session 121 from INV-037, enhanced Sessions 122-123*
*Sources: Genesis_Architect_Notes.md, deprecated_AGENT.md, HAIOS-RAW ADRs, ADR-033*
