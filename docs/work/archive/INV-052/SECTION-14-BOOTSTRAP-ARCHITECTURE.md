# generated: 2025-12-30
# System Auto: last updated on: 2026-01-02T21:42:25
# Section 14: Bootstrap Architecture

Generated: 2025-12-30 (Session 152)
Updated: 2026-01-02 (Session 156) - Aligned with Manifesto Corpus
Purpose: Document L0-L4 context hierarchy and coldstart grounding sequence
Status: DESIGN

---

## Gaps Identified (S152 Analysis) - RESOLVED S154-156

| Gap | Description | Status |
|-----|-------------|--------|
| **Bootstrap files not in portable plugin** | north-star.md, invariants.md in .claude/config/ | RESOLVED: Manifesto Corpus in .claude/haios/manifesto/ |
| **CLAUDE.md is hand-maintained** | Should be generated from HAIOS core | FUTURE: Generate from L0-L3 templates |
| **No LLM abstraction for bootstrap** | Only Claude CLI format exists | DESIGNED: S18 Portable Plugin Spec |

---

## Target Architecture: Manifesto Corpus (S154-155)

```
.claude/haios/manifesto/            <- HAIOS CORE (LLM-agnostic, immutable)
├── L0-telos.md                     <- WHY HAIOS exists (Agency Engine, Prime Directive)
├── L1-principal.md                 <- WHO the operator is (constraints, success)
├── L2-intent.md                    <- WHAT serving means (goals, trade-offs)
├── L3-requirements.md              <- HOW to behave (7 principles, boundaries)
│
.claude/config/
└── roadmap.md                      <- L4: Strategic direction (mutable)
        │
        │  coldstart loads L0-L3...
        ▼
Agent grounded with foundational context
```

**Key Insight (S154):** L0-L3 are IMMUTABLE (rarely change). L4 is DYNAMIC (changes frequently).
Legacy files (north-star.md, invariants.md) are SUPERSEDED.

---

## L0-L4 Context Hierarchy (Manifesto Corpus)

| Level | File | Question Answered | Mutability |
|-------|------|-------------------|------------|
| **L0** | L0-telos.md | WHY does HAIOS exist? | IMMUTABLE |
| **L1** | L1-principal.md | WHO is the operator? | IMMUTABLE |
| **L2** | L2-intent.md | WHAT does serving mean? | IMMUTABLE |
| **L3** | L3-requirements.md | HOW should system behave? | IMMUTABLE |
| **L4** | roadmap.md, status files | WHAT are current specs? | DYNAMIC |

**Immutability Boundary:** L0-L3 are foundational (rarely change). L4 is implementation (changes frequently).

---

## Coldstart Grounding Sequence (Updated S155)

```
/coldstart
    │
    ├─► 1. Load CLAUDE.md (Agent Instructions)
    │
    ├─► 2. Load Manifesto Corpus (L0-L3 IMMUTABLE)
    │   ├── L0-telos.md       "Agency Engine, Prime Directive..."
    │   ├── L1-principal.md   "Operator constraints, success definition..."
    │   ├── L2-intent.md      "Goals, trade-offs, criteria..."
    │   └── L3-requirements.md "7 principles, boundaries..."
    │
    ├─► 3. Load L4: epistemic_state.md (WHERE)
    │       "Epoch 2, M7b at 54%..."
    │
    ├─► 4. Load L4: roadmap.md (STRATEGIC)
    │       "5 epochs, current milestones..."
    │
    ├─► 5. Load L4: haios-status-slim.json (WHAT)
    │       "Session 156, active items..."
    │
    ├─► 6. Load Session: Latest checkpoint (PRIOR)
    │       "Session 155 completed X, Y, Z..."
    │
    ├─► 7. Query memory (STRATEGIES)
    │       "Prior approaches to similar work..."
    │
    └─► 8. Route to work (ACTION)
            "just ready → invoke cycle"
```

---

## Manifesto Corpus File Anatomy (S154)

### L0-telos.md (WHY)

```markdown
## The Existential Context
1. Existential Oscillation - creation vs survival tension
2. Cognitive Overload - manual context synchronization
3. Opaque Systems - extract value vs enable agency
4. Urgency Without Clarity - pressure without structure

## The Aspiration
Self-aware symbiotic system that compounds cognition.

## Prime Directive
Protect the operator from context loss, decision fatigue, and misaligned action.
```

### L1-principal.md (WHO)

```markdown
## Operator Constraints
- Limited time, high cognitive load
- No network effect, single human
- Burnout threshold is real and close

## Success Definition
- Health through leverage (not depletion)
- Freedom of movement (meatspace navigation)
- Capacity to give (surplus, not deficit)
```

### L3-requirements.md (HOW)

```markdown
## 7 Core Behavioral Principles
1. Certainty Ratchet - state moves toward clarity
2. Evidence Over Assumption - verify, don't guess
3. Context Must Persist - memory across sessions
4. Duties Are Separated - operator strategy, agent execution
5. Reversibility By Default - rollback is safe
6. Graceful Degradation - failures don't cascade
7. Traceability - all decisions auditable
```

---

## CLAUDE.md Generation (Target)

```yaml
# .claude/haios/bootstrap/agent-bootstrap.yaml
template: agent-bootstrap.md.j2
outputs:
  - format: claude_cli
    path: CLAUDE.md
    includes:
      - L1 rules (MUST/SHOULD)
      - L2 quick reference tables
      - Tool preference hierarchy
      - Governance triggers
  - format: gemini
    path: GEMINI.md
    includes:
      - Same content, different syntax
```

---

## Bootstrap vs Runtime Context

| Aspect | Bootstrap (coldstart) | Runtime (prompt) |
|--------|----------------------|------------------|
| When | Session start | Every prompt |
| Source | L0-L2 files, checkpoint | UserPromptSubmit hook |
| Content | Full grounding | Vitals, context % |
| Size | ~5-10k tokens | ~200 tokens |

---

## Key Insight: Grounding Enables Autonomy

The bootstrap sequence isn't just "loading files" - it's **grounding the prompt cascade**.

Without L0-L3 grounding:
- routing-gate has no principles to apply
- Cycles have no DoD to enforce
- Gates have no anti-patterns to check
- Agent has no understanding of operator's WHY

The Manifesto Corpus IS the trust engine initialization.

---

## Related

- **SECTION-15:** Information Architecture (context level details)
- **SECTION-16:** Scaffold Templates (how templates enforce IA)
- **coldstart.md:** The command that executes this sequence

---

*Scaffolded Session 152, Updated Session 156*
