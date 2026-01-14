# generated: 2026-01-01
# System Auto: last updated on: 2026-01-03T13:48:35
# HAIOS Manifesto Corpus

## What This Is

The foundational context hierarchy for HAIOS. Answers: "What does an agent need to know to serve the operator well?"

## The Full Stack (8 Levels)

```
L0: TELOS         - Why HAIOS exists           - IMMUTABLE  - Forever
L1: PRINCIPAL     - Who is served              - IMMUTABLE  - Forever
L2: INTENT        - What serving means         - IMMUTABLE  - Forever
L3: REQUIREMENTS  - How to behave              - IMMUTABLE  - Forever
────────────────────────────────────────────────────────────────────
L4: IMPLEMENTATION- What to build              - DYNAMIC    - Epoch
L5: EXECUTION     - What's active              - EPHEMERAL  - Days/weeks
L6: SESSION       - What's this session        - EPHEMERAL  - Hours
L7: PROMPT        - What's this command        - EPHEMERAL  - Seconds
```

## The Hierarchy

### Soul (Immutable)

| Level | File | Question | Lifespan |
|-------|------|----------|----------|
| **L0** | `L0-telos.md` | Why does HAIOS exist? | Forever |
| **L1** | `L1-principal.md` | Who is being served? | Forever |
| **L2** | `L2-intent.md` | What does serving mean? | Forever |
| **L3** | `L3-requirements.md` | How should HAIOS behave? | Forever |

### Blueprint (Dynamic)

| Level | File | Question | Lifespan |
|-------|------|----------|----------|
| **L4** | `L4-implementation.md` | What are we building? | Epoch |

### Runtime (Ephemeral)

| Level | File | Question | Lifespan |
|-------|------|----------|----------|
| **L5** | `L5-execution.md` | What's on my plate? | Days-weeks |
| **L6** | `L6-session.md` | What has this horse done? | Hours |
| **L7** | `L7-prompt.md` | What's the immediate task? | Seconds |

## The Chariot Metaphor

```
L0-L3: THE SOUL      - Why, who, what, how (never changes)
L4:    THE BLUEPRINT - Technical design (changes per epoch)
L5:    THE WORKBENCH - Active work (changes per task)
L6:    THE HORSE     - Session state (changes per context clear)
L7:    THE REINS     - Current command (changes per prompt)
```

## Design Principle

**Progressive Disclosure.** The hierarchy is an access control model for agent cognition.

| Agent Type | Levels Loaded |
|------------|---------------|
| Strategic (Planner, Architect) | L0, L1, L2, L3 |
| Tactical (Builder, Implementer) | L2, L3, L4 |
| Execution (Validator, Test Runner) | L3, L4, L5 |
| Utility (Schema Verifier) | L4, L5 only |
| Runtime (All agents during execution) | L5, L6, L7 |

## Generative Chain

```
World → Ruben → HAIOS → Agents → Artifacts
         ↑
    L1 Principal
```

The system exists to serve this specific human. Not abstract "users."

## Current State

| Level | Status | Last Updated |
|-------|--------|--------------|
| **L0** | COMPLETE | S154 - Core telos documented |
| **L1** | COMPLETE | S154 - Success definition complete |
| **L2** | COMPLETE | S154 - Goals, criteria, trade-offs |
| **L3** | COMPLETE | S155 - 7 principles, boundaries |
| **L4** | COMPLETE | S158 - Epoch 2.2 Chariot architecture |
| **L5** | COMPLETE | S158 - Execution framework |
| **L6** | COMPLETE | S158 - Session framework |
| **L7** | COMPLETE | S158 - Prompt framework |

## Key Insight (S158)

L5-L7 are not static files - they're **frameworks for understanding ephemeral state**:

- **L5** describes how `docs/work/active/` works (the workbench)
- **L6** describes how sessions work (the horse)
- **L7** describes how prompts work (the reins)

The files document the *semantics*, not the *content* (which is ephemeral).

## Related

- `docs/work/archive/INV-052/` - Architecture documentation (17 sections)
- `docs/work/archive/INV-053/` - Architecture review (simplification)
- `.claude/commands/coldstart.md` - Loading sequence (L0-L4)

---

*Created Session 153. Extended to 8 levels Session 158.*
