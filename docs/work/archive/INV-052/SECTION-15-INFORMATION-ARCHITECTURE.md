# generated: 2025-12-30
# System Auto: last updated on: 2026-01-02T21:44:10
# Section 15: Information Architecture

Generated: 2025-12-30 (Session 152)
Updated: 2026-01-02 (Session 156) - Aligned with Manifesto Corpus L0-L4
Purpose: Document context levels, token budgets, and loading priorities
Status: DESIGN

---

## Gaps Identified (S152 Analysis)

| Gap | Description | Target Fix |
|-----|-------------|------------|
| **Token budgets not enforced** | L0-L3 sizes are guidelines, not limits | Add budget validation to coldstart |
| **Loading priority implicit** | Coldstart loads in order but priority not explicit | Define priority + fallback |
| **No context overflow handling** | At 100% context, no graceful degradation | Define what to drop first |

---

## Target Architecture: Context Level Hierarchy (Manifesto Corpus)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    INFORMATION ARCHITECTURE (L0-L4 Manifesto Corpus)                 │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ═══════════════════════════════ IMMUTABLE BOUNDARY ════════════════════════════   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  L0: TELOS (~800 tokens)                                                     │   │
│  │  ─────────────────────────────────────────────────────────────────────────── │   │
│  │  WHY HAIOS exists. Agency Engine, Prime Directive, Companion Vessel.         │   │
│  │  NEVER dropped. If L0 is lost, agent is ungrounded.                          │   │
│  │                                                                              │   │
│  │  File: .claude/haios/manifesto/L0-telos.md                                   │   │
│  │  Mutability: IMMUTABLE                                                       │   │
│  │  Priority: CRITICAL                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  L1: PRINCIPAL (~600 tokens)                                                 │   │
│  │  ─────────────────────────────────────────────────────────────────────────── │   │
│  │  WHO the operator is. Constraints, success definition, cognitive style.      │   │
│  │  Dropped only in extreme context pressure.                                   │   │
│  │                                                                              │   │
│  │  File: .claude/haios/manifesto/L1-principal.md                               │   │
│  │  Mutability: IMMUTABLE                                                       │   │
│  │  Priority: CRITICAL                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  L2: INTENT (~500 tokens)                                                    │   │
│  │  ─────────────────────────────────────────────────────────────────────────── │   │
│  │  WHAT serving means. Goals, trade-offs, success criteria.                    │   │
│  │                                                                              │   │
│  │  File: .claude/haios/manifesto/L2-intent.md                                  │   │
│  │  Mutability: IMMUTABLE                                                       │   │
│  │  Priority: HIGH                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  L3: REQUIREMENTS (~1000 tokens)                                             │   │
│  │  ─────────────────────────────────────────────────────────────────────────── │   │
│  │  HOW to behave. 7 principles, boundaries, LLM nature.                        │   │
│  │                                                                              │   │
│  │  File: .claude/haios/manifesto/L3-requirements.md                            │   │
│  │  Mutability: IMMUTABLE                                                       │   │
│  │  Priority: HIGH                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ═══════════════════════════════ DYNAMIC BOUNDARY ══════════════════════════════   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  L4: IMPLEMENTATION (variable tokens)                                        │   │
│  │  ─────────────────────────────────────────────────────────────────────────── │   │
│  │  Current state. Status, roadmap, checkpoints, work files, memory.            │   │
│  │  First to drop. Can be regenerated or re-queried.                            │   │
│  │                                                                              │   │
│  │  Files: epistemic_state.md, roadmap.md, haios-status.json, checkpoints/      │   │
│  │  Mutability: DYNAMIC                                                         │   │
│  │  Priority: MEDIUM-LOW (recoverable)                                          │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Token Budget Allocation (Manifesto Corpus)

| Level | Name | Target | Max | Drop Order |
|-------|------|--------|-----|------------|
| L0 | Telos | 800 | 1000 | NEVER |
| L1 | Principal | 600 | 800 | NEVER |
| L2 | Intent | 500 | 700 | Last |
| L3 | Requirements | 1000 | 1500 | Last |
| L4 | Implementation | Variable | Remaining | First |

**Total manifesto budget (L0-L3):** ~3000 tokens (immutable)
**Working context (L4):** Remaining ~145k-195k tokens (depending on model)

---

## Context Pressure Response

```
Context % | Action
──────────┼────────────────────────────────────────────────────
< 80%     | Normal operation
80-90%    | Warn: "Consider checkpoint"
90-94%    | Suggest: "Checkpoint now"
94-98%    | MUST: Create checkpoint before continuing
> 98%     | EMERGENCY: Save state, prepare for compaction
```

---

## Loading Priority Matrix (Manifesto Corpus)

| File | Level | Required | Fallback if Missing |
|------|-------|----------|---------------------|
| L0-telos.md | L0 | YES | HALT - ungrounded agent |
| L1-principal.md | L1 | YES | HALT - no operator context |
| L2-intent.md | L2 | YES | HALT - no goals defined |
| L3-requirements.md | L3 | YES | HALT - no behavior rules |
| CLAUDE.md | (bootstrap) | YES (CLI default) | Error - broken setup |
| epistemic_state.md | L4 | NO | Use haios-status.json |
| roadmap.md | L4 | NO | Use epistemic_state.md |
| haios-status-slim.json | L4 | NO | Generate fresh |
| Latest checkpoint | L4 | NO | Start with blank context |
| Memory query | L4 | NO | Proceed without strategies |

---

## Information Flow

```
                    WRITE                          READ
                      │                              │
                      ▼                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         HAIOS CORE FILES                             │
│                                                                     │
│  L0: north-star.md        ◄──── Rarely (operator)                   │
│  L1: invariants.md        ◄──── Rarely (operator)                   │
│                                                                     │
│  L2: epistemic_state.md   ◄──── Per-epoch (milestone changes)       │
│  L2: haios-status.json    ◄──── just update-status                  │
│                                                                     │
│  L3: checkpoints/*.md     ◄──── checkpoint-cycle                    │
│  L3: WORK.md              ◄──── PostToolUse hook                    │
│  L3: memory queries       ◄──── MCP (read-only for context)         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                      │
                      ▼
              coldstart / prompts
                      │
                      ▼
              AGENT CONTEXT
```

---

## Portable Plugin Context Structure (Manifesto Corpus)

```yaml
# .claude/haios/config/context-levels.yaml
levels:
  L0:
    name: telos
    files: [manifesto/L0-telos.md]
    token_budget: 800
    drop_order: never
    mutability: immutable

  L1:
    name: principal
    files: [manifesto/L1-principal.md]
    token_budget: 600
    drop_order: never
    mutability: immutable

  L2:
    name: intent
    files: [manifesto/L2-intent.md]
    token_budget: 500
    drop_order: last
    mutability: immutable

  L3:
    name: requirements
    files: [manifesto/L3-requirements.md]
    token_budget: 1000
    drop_order: last
    mutability: immutable

  L4:
    name: implementation
    sources: [config/roadmap.md, epistemic_state.md, haios-status.json, checkpoints, work_files, memory]
    token_budget: remaining
    drop_order: first
    mutability: dynamic
```

---

## Related

- **SECTION-14:** Bootstrap Architecture (loading sequence)
- **SECTION-16:** Scaffold Templates (how templates map to levels)
- **UserPromptSubmit hook:** Context % monitoring

---

*Scaffolded Session 152, Updated Session 156*
