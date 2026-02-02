# generated: 2026-02-02
# System Auto: last updated on: 2026-02-02T20:22:18
# S27: The Breath Model

**Status:** Principle (foundational)
**Source:** Session 292 operator-agent dialogue
**Memory Refs:** 83240-83249

---

## The Insight

Work phases follow inhale/exhale rhythm in pairs:

```
EXPLORE     [inhale]  - gather, see what's there
INVESTIGATE [exhale]  - commit: hypotheses, verdicts, findings

EPISTEMY    [inhale]  - reflect: what do I know, infer, not know
DESIGN      [exhale]  - commit: architecture, interfaces, decisions

PLAN        [inhale]  - gather: tests, steps, dependencies
IMPLEMENT   [exhale]  - commit: code, artifacts
```

Each pair is a breath cycle. **Inhale gathers. Exhale commits.**

---

## The Pauses

The gate between each exhale and the next inhale is where ceremonies live - **the pause between breaths**.

```
INVESTIGATE → [pause: epistemic review] → EPISTEMY
DESIGN      → [pause: critique]         → PLAN
IMPLEMENT   → [pause: check/validate]   → DONE
```

The pauses are ceremonies. They force the transition from one breath to the next to be conscious, not automatic.

---

## The Full Sequence

```
Breath 1: Discovery
  EXPLORE [inhale] → INVESTIGATE [exhale] → [epistemic review pause]

Breath 2: Architecture
  EPISTEMY [inhale] → DESIGN [exhale] → [critique pause]

Breath 3: Execution
  PLAN [inhale] → IMPLEMENT [exhale] → [validation pause] → DONE
```

---

## What This Reframes

| Old Understanding | New Understanding |
|-------------------|-------------------|
| Investigation spawns implementation | Investigation spawns epistemy/design |
| Plan is first phase | Plan is third breath |
| Epistemic review is new ceremony | Epistemic review is pause between breaths |
| Design phase is missing | Design is exhale after epistemy inhale |
| Ceremonies are checkpoints | Ceremonies are the pauses between breaths |

---

## Work Item Type Mapping

| Type | Breath | Phase |
|------|--------|-------|
| `investigation` | Discovery | EXPLORE → INVESTIGATE |
| `design` | Architecture | EPISTEMY → DESIGN |
| `implementation` | Execution | PLAN → IMPLEMENT |

---

## Spawning Rules

Each exhale spawns work for the next breath (or loops back):

| After | If Ready | Spawns | If Not Ready | Spawns |
|-------|----------|--------|--------------|--------|
| INVESTIGATE | Epistemic state clear | Design work | Unknowns significant | More investigations |
| DESIGN | Spec complete | Implementation work | Gaps in design | Back to epistemy or investigation |
| IMPLEMENT | Validation passes | DONE | Validation fails | Back to implement or plan |

---

## Alignment

- **S20 (Pressure Dynamics):** Inhale = volumous (low pressure), Exhale = tight (high pressure)
- **L3.1 (Certainty Ratchet):** Each breath moves toward certainty
- **L3.2 (Evidence Over Assumption):** Pauses force epistemic distinction
- **E2.4 (Critique as Hard Gate):** Pauses are the gates

---

## References

- S20: Pressure Dynamics (inhale/exhale origin)
- S24: Context Assembly (inhale pattern)
- S23: Files as Context (exhale pattern)
- Memory: 83240-83249 (this discovery)

---

*S27 documents the breath model discovered through Session 292 operator-agent dialogue. It should inform all future cycle and ceremony design.*
