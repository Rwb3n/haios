# generated: 2026-01-07
# System Auto: last updated on: 2026-01-18T15:31:36
# Section 24: Context Assembly (Inhale)

## Status

**VALIDATED** - INV-060 confirmed S24 is context assembly (distinct from staging/validation). Session 181.

---

## The Duality

**S23 (Files as Context) = EXHALE**
- Produce artifact for downstream node
- "The quality of every gate output file determines the capability of every downstream node"

**S24 (Context Assembly) = INHALE**
- Assemble context from upstream sources
- What must be loaded BEFORE the node can produce quality output

Together they complete the context architecture cycle.

---

## Origin

**Session 180 dialogue:**

1. Operator: "staging - like the military procedure"
2. Agent: Is this a new gate?
3. Operator: "is that really the whole question?"
4. Agent: Maybe it's about composition, not validation
5. Operator: "context architecture"
6. Agent: S23 is output (exhale), this is input (inhale)
7. Operator: "nailed it"

**The insight:** Staging is not a gate. It's context assembly. The military metaphor is about bringing disparate elements into a coherent unit before movement.

---

## The Full Cycle

```
INHALE (S24): Assemble context from upstream
  ├── Session context (L0-L3 manifesto, coldstart)
  ├── Architectural context (L4 epoch/chapter/arc, ground-cycle)
  └── Work context (memory_refs, portals, prior learnings)
          ↓
COGNITIVE WORK: Process with assembled context
          ↓
EXHALE (S23): Produce artifact for downstream
  └── File as context window for next node
```

---

## Context Layers

| Layer | What Gets Loaded | When | Mechanism |
|-------|------------------|------|-----------|
| L0-L3 | Manifesto (immutable) | Session start | coldstart |
| L4 | Epoch/Chapter/Arc definitions | Work start | ground-cycle |
| L5+ | Work item state, memory_refs, portals | Work start | **staging/assembly** |

**The gap identified:** We load session-level and architectural context, but work-level context assembly is not formalized:
- WORK.md state
- memory_refs (MUST query, not decorate)
- Portal references (spawned_from, related, blocks)
- Prior session's learnings for THIS work item

---

## Key Principle

**Agent capability is bounded by assembled context.**

- If memory_refs aren't queried, prior reasoning is lost
- If portals aren't traversed, relationships are invisible
- The composition moment where layers merge enables quality output

---

## Connection to Other Sections

| Section | Relationship |
|---------|--------------|
| S20 (Pressure) | Inhale/exhale rhythm matches [MAY]/[MUST] pattern |
| S21 (Notation) | Context structure IS the notation |
| S22 (Patterns) | Assembly could be a composable pattern |
| S23 (Files as Context) | **Direct counterpart** - output side of duality |

---

## Future: Multi-Agent Context (Epoch 4)

**Current constraint:** Single-threaded context, single operator, single agent.

**Future vision:** Multi-agent layer architecture where S23/S24 become inter-agent protocol:

```
Human (L0-L2: Telos, Principal, Intent)
         ↓
Orchestrator Agent (L3-L4: Architecture, Principles)  ← reads S23/S24 output from below
         ↓
Worker Agents (L5-L7: Work items, Execution)  ← produces S23 output, consumes S24 input
```

**What we build now matters:**
- S24 context assembly = how L5-L7 agents receive context from L3-L4
- S23 file output = how L5-L7 agents pass artifacts to L3-L4 for decisions
- memory_refs = reasoning persists across agent boundaries
- Portals = work items reference each other across agents

**The manual layer-switch today (operator says "is that really the question?") becomes the L3-L4 ↔ L5-L7 protocol tomorrow.**

See: L4-implementation.md → Epoch 4: AUTONOMY

---

## Investigation

**INV-060:** Staging Gate Concept Exploration
- Status: **Complete** (Session 181)
- Finding: Staging = validation, S24 = composition. Distinct but sequential.
- Outcome: No new staging gate needed. Extend ground-cycle with memory_refs (Breath CH-003).

---

## References

- S23: Files as Context (the exhale counterpart)
- INV-060: Investigation work item
- Memory: 81039-81051 (this insight)
- Memory: 7595, 24699, 18853, 37175, 75302 (prior readiness concepts)
- Memory: 81030-81038 (initial staging concept)
