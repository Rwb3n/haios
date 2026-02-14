# generated: 2026-02-14
# System Auto: last updated on: 2026-02-14T11:28:00
# HAIOS: Breath Architecture — Design Handover

status: inhale
origin: operator design session, February 2026
filed: S365 (E2.6 planning session)
relates_to:
  - L3.4 (Duties Separated)
  - L3.10 (No Grinding the Operator)
  - S27-breath-model.md (E2.4 foundational)
  - WORK-101 (Proportional Governance)

---

## Context

This document captures a design session exploring how HAIOS should manage the tension between agent autonomy and system control. Two complementary framings emerged: an engineering vocabulary (opinionated/delegative) and an experiential metaphor (breath). These operate at different abstraction layers and should be preserved as a dual vocabulary.

## Core Concept: Opinionated vs. Delegative

In software design, an **opinionated** system enforces strong defaults and conventions — it has views about how things should be done. A **delegative** (sometimes called "unopinionated") system defers decisions to the operator, offering configurability at the cost of requiring more choices.

Key principles of opinionated design:

- **Convention over configuration** — sensible defaults; opt out rather than opt in
- **One right way** — the system endorses a preferred path per task
- **Coherence over choice** — integrated whole over interchangeable parts
- **Guardrails as features** — constraints are intentional design decisions
- **Reduced cognitive load** — the system absorbs decisions so the operator focuses on work
- **Strong defaults, weak locks** — overridable, but the default path is good enough that most don't bother

Most mature systems are **mixed**: opinionated in some layers, delegative in others. Common patterns include opinionated core with extensible edges, layered opinion depth, and opinionated workflows over unopinionated data.

## The Breath Metaphor

HAIOS operates in two alternating phases:

### Inhale (Delegative Phase)

The system explores, surveys, researches, designs, and generates options. Agents have latitude. The system is expanding its possibility space.

- Divergent
- Exploratory
- Autonomy-granting
- Option-generating

### Exhale (Opinionated Phase)

The system commits. Contracts are populated, critiqued, validated, and handed over. The system enforces structure, quality gates, and handover protocols.

- Convergent
- Committal
- Convention-enforcing
- Delivery-oriented

### How the Two Framings Relate

| Layer | Framing | Purpose |
|-------|---------|---------|
| Engineering / Architecture | Opinionated vs. Delegative | Precise vocabulary for system behaviour at each phase |
| Communication / Experience | Inhale vs. Exhale | Captures the rhythm — the alternation and transition between phases |

The breath metaphor adds something the engineering vocabulary doesn't: the idea that these phases are **cyclical and rhythmic**, not just a binary toggle. The system breathes.

This maps to established design patterns: the double diamond (diverge → converge → diverge → converge) and the explore/exploit tradeoff.

## Fractal Application (S365 Analysis)

The breath pattern is fractal — same pattern at every level:

```
Session level:     coldstart (inhale) → work (exhale) → checkpoint (pause)
Lifecycle level:   EXPLORE (inhale) → DO/CHECK (exhale) → DONE (pause)
Epoch level:       planning (inhale) → implementation (exhale) → close (pause)
Epoch sequence:    E2.6-E2.7 (inhale: foundations, composability) → E2.8-E2.9 (exhale: agent UX, governance)
```

## Open Design Questions

### 1. What triggers the phase transition?

What causes the system to move from inhale to exhale? Candidates:

- **Time-based** — a deadline or duration threshold
- **Threshold-based** — enough options explored, diminishing returns detected
- **Operator-explicit** — the user says "commit now"
- **Hybrid** — the system recommends transition, operator confirms

This is a critical decision because it determines **where the system's opinion about its own rhythm lives**.

### 2. Who has authority over the trigger?

Is the transition decision itself opinionated (the system decides when to stop exploring) or delegative (the operator decides)? Or is it mixed — the system surfaces a recommendation and the operator ratifies?

### 3. Is there a third state?

Does the system ever **hold its breath**? A suspension state where it is neither exploring nor committing, but waiting for something external — a dependency, a human decision, an event. If so, what are the entry/exit conditions for this state?

**S365 finding:** Yes. The third state already exists: `parked` in queue, `stub: true` in skills, `blocked_by` in work items. These are all "held breath" states. Not yet named as such.

## Design Status

This is an **inhale-phase** document. It surveys the conceptual space and surfaces questions. The next phase of work should converge on answers to the three open questions above before committing to implementation.

## Implications for E2.8 (Agent UX)

- "Agents spend tokens on work not bookkeeping" = make the exhale phase more opinionated
- Proportional governance (WORK-101) = detect "shallow breath" and right-size ceremony
- Dynamic ceremony composition (obs-313) = configurable breath depth per work item complexity

---

*Captured from operator design session — February 2026*
*Filed in E2.8/architecture by Hephaestus, S365*
