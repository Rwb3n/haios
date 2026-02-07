# generated: 2026-01-01
# System Auto: last updated on: 2026-01-01T20:17:08
# HAIOS Manifesto Corpus Architecture

Generated: 2026-01-01 (Session 153)
Purpose: Define the hierarchical structure for HAIOS foundational context
Status: SCAFFOLD

---

## Overview

The Manifesto Corpus is the foundational context hierarchy for HAIOS. It answers the question: "What does an agent need to know to serve the operator well?"

**Key Design Principle:** Progressive disclosure. Lower-level execution agents don't need L0-L1 context. Strategic/planning agents do. The hierarchy isn't just organizational - it's an access control model for agent cognition.

**Generative Chain:** World → Ruben → HAIOS

---

## The 5-Level Hierarchy

| Level | Label | Function | Rationale |
|-------|-------|----------|-----------|
| **L0** | Telos | Why HAIOS exists - the foundational purpose | Root node. Everything derives from this. Not "Trust Engine" as mechanism, but the WHY behind needing a trust engine at all. |
| **L1** | Principal | Who the operator is - values, constraints, life context, cognitive style | The system exists to serve this specific human. Agents need this for alignment, not just task execution. |
| **L2** | Intent Architecture | What the operator wants - goals, priorities, success criteria | Bridges identity (L1) to action. What does "serving Ruben well" actually mean in practice? |
| **L3** | Functional Requirements | How HAIOS should behave - capabilities, boundaries, interfaces | Operational constraints. What the system does and doesn't do. |
| **L4** | Implementation | Technical specs, protocols, tool configs | Execution layer. Most agents operate here and only here. |

---

## Level Details

### L0: Telos (WHY)

**Question answered:** Why does HAIOS exist at all?

**Content:**
- [ ] The existential context (burnout, cognitive load, precarity)
- [ ] The aspiration (sovereign creative agency, sophisticated life)
- [ ] The companion relationship (not tool, but vessel)
- [ ] The trust premise (system earns trust by being genuinely useful, learning, growing)

**Source:** Genesis_Architect_Notes.md Part 8, Memory concepts 50090, 51211, 72414

**Target file:** `.claude/haios/manifesto/L0-telos.md`

---

### L1: Principal (WHO)

**Question answered:** Who is the operator this system serves?

**Content:**
- [ ] Values and priorities
- [ ] Life context and constraints
- [ ] Cognitive style and preferences
- [ ] What "success" means personally (not abstractly)

**Source:** Memory concepts 49674, 45805, operator declarations

**Target file:** `.claude/haios/manifesto/L1-principal.md`

**Note:** This is personal. Not every agent needs this. Strategic agents do.

---

### L2: Intent Architecture (WHAT)

**Question answered:** What does serving this operator well actually mean?

**Content:**
- [ ] Goals hierarchy (immediate, medium-term, aspirational)
- [ ] Success criteria (how do we know we're helping?)
- [ ] Priorities and trade-offs (speed vs quality, etc.)
- [ ] Boundaries (what we don't do)

**Source:** Derived from L0+L1, operator guidance

**Target file:** `.claude/haios/manifesto/L2-intent.md`

---

### L3: Functional Requirements (HOW)

**Question answered:** How should HAIOS behave to serve these intents?

**Content:**
- [ ] Capabilities (what the system does)
- [ ] Boundaries (what it doesn't do)
- [ ] Interfaces (how operator interacts)
- [ ] Patterns (Certainty Ratchet, Governance Flywheel, Three Pillars)
- [ ] Anti-patterns (the 6 LLM behaviors)

**Source:** Genesis_Architect_Notes Parts 2-7, invariants.md (current)

**Target file:** `.claude/haios/manifesto/L3-requirements.md`

**Note:** Current `invariants.md` is mostly L3 content.

---

### L4: Implementation (SPECS)

**Question answered:** What are the technical specifications?

**Content:**
- [ ] Protocols (hooks, cycles, gates)
- [ ] Tool configurations (MCP, commands, skills)
- [ ] State management (WORK.md, node_history)
- [ ] All of INV-052 sections 1-17

**Source:** INV-052, CLAUDE.md, config files

**Target file:** Already exists across `.claude/` structure

**Note:** Current CLAUDE.md is L4. Current `north-star.md` is mislabeled (actually L3).

---

## Access Control Model

| Agent Type | Levels Loaded | Rationale |
|------------|---------------|-----------|
| **Strategic** (Genesis Architect, Planner) | L0, L1, L2, L3 | Needs full context for alignment |
| **Tactical** (Builder, Implementer) | L2, L3, L4 | Needs intent + specs, not personal context |
| **Execution** (Test Runner, Validator) | L3, L4 | Needs requirements + specs only |
| **Utility** (Schema Verifier, etc.) | L4 only | Just needs technical specs |

---

## Current State vs. Target State

| Current File | Current Label | Actual Level | Target |
|--------------|---------------|--------------|--------|
| north-star.md | L0 | L3 (functional) | Rename/restructure |
| invariants.md | L1 | L3 (functional) | Rename/restructure |
| CLAUDE.md | L1+L2 | L4 (implementation) | Correct |
| (none) | - | L0 (telos) | Create |
| (none) | - | L1 (principal) | Create |
| (none) | - | L2 (intent) | Create |

---

## Next Steps

1. **Query memory** for L0 content (existential context, aspiration, companion relationship)
2. **Query memory** for L1 content (operator values, constraints, cognitive style)
3. **Synthesize** into L0-telos.md and L1-principal.md
4. **Derive** L2-intent.md from L0+L1
5. **Restructure** current north-star.md and invariants.md as L3
6. **Update** coldstart to load appropriate levels per agent type

---

## Related

- **INV-052:** Architecture documentation (L4)
- **GAPS.md:** Implementation gaps (L4)
- **Genesis_Architect_Notes.md:** Source document (mixed levels)
- **Memory:** 80k+ concepts containing distilled learnings

---

*Scaffolded Session 153*
