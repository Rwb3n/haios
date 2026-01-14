# generated: 2025-12-09
# System Auto: last updated on: 2026-01-14T21:12:24
# Epistemic State: Operational Self-Awareness

> **Purpose:** Surface known behavioral patterns and knowledge gaps. Not a history log.
> **Philosophy:** These patterns are FEATURES of the architecture, not bugs. Leverage them, don't fight them.

---

## Current Status

**Epoch:** 2.2 - The Refinement
**Sessions:** 190 (October 2025 - January 2026)
**Focus:** Skill decomposition, pressure dynamics, context loading

### Active Chapters

| Chapter | Theme | Status |
|---------|-------|--------|
| **Chariot** | Module Architecture (9 modules) | Active |
| **Breath** | Pressure Dynamics (inhale/exhale rhythm) | Active |
| **Form** | Skill Decomposition (smaller containers) | Active |
| **Ground** | Context Loading (session manifests) | Active |

---

## Known Behavioral Patterns (Anti-Patterns)

> **L1 Anti-Patterns:** See `.claude/haios/manifesto/L3-requirements.md` for 6 fundamental LLM patterns. Those are architectural truths that apply universally.

| Pattern | Description | Mitigation |
|---------|-------------|------------|
| Assume over verify | LLM predicts, doesn't verify | External verification required |
| Generate over retrieve | Creates by default | Retrieval must be enforced |
| Move fast | No internal friction | External gates required |
| Optimistic confidence | Pattern-matches | Edge cases need explicit handling |
| Ceremonial completion | Completes literally | Integration needs explicit checking |
| Context loss | No episodic memory | External memory required |

---

## Architecture Principles

| Principle | Implementation |
|-----------|----------------|
| **Certainty Ratchet** | State moves only toward clarity, never backward |
| **Evidence Over Assumption** | Decisions require evidence, not predictions |
| **Context Must Persist** | Knowledge compounds via files and memory |
| **Files as Context Windows** | Every gate output is input for next node |
| **Pressure Dynamics** | Phases alternate [volumous] → [tight] |

---

## Key Constraints

| Constraint | Implication |
|------------|-------------|
| Claude Code hooks can't track session state | Soft enforcement only (warnings, not blocks) |
| Skill() invocation not hookable | Hard enforcement requires SDK (Epoch 4) |
| LLM context is ephemeral | Files are the only durable memory |

---

## References

- **Manifesto:** `.claude/haios/manifesto/` (L0-L4)
- **Epoch Definition:** `.claude/haios/epochs/E2/EPOCH.md`
- **Architecture:** `.claude/haios/epochs/E2/architecture/`
- **Work Tracking:** `docs/work/` (active items in `active/`, completed in `archive/`)
- **Session History:** `docs/checkpoints/`

---

**Last Updated:** 2026-01-14 (Session 190)
**Current Phase:** Epoch 2.2 - The Refinement
