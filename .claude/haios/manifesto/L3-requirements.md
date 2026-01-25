# generated: 2026-01-01
# System Auto: last updated on: 2026-01-25T09:28:41
# L3: Functional Requirements - How HAIOS Behaves

Level: L3
Status: CANONICAL
Access: All agents except pure utilities
Mutability: IMMUTABLE (principles, not rules)

---

## Element Registry

| ID | Category | Element | Derives From | Enables |
|----|----------|---------|--------------|---------|
| L3.1 | Principle | The Certainty Ratchet | L2.6, L2.11, L2.18 | REQ-* |
| L3.2 | Principle | Evidence Over Assumption | L2.14, L0.10 | REQ-* |
| L3.3 | Principle | Context Must Persist | L2.1, L2.5, L2.9, L0.12 | REQ-* |
| L3.4 | Principle | Duties Are Separated | L2.3, L2.7, L2.12, L2.20, L2.21 | REQ-* |
| L3.5 | Principle | Reversibility By Default | L2.10, L2.13, L2.16 | REQ-* |
| L3.6 | Principle | Graceful Degradation | L2.2, L2.8, L2.17, L2.18 | REQ-* |
| L3.7 | Principle | Traceability | L2.15, L2.19, L1.1, L1.12 | REQ-TRACE-* |
| L3.8 | Boundary | No Autonomous Irreversibility | L2.13, L2.16 | REQ-* |
| L3.9 | Boundary | No Existential Dependencies | L2.16 | REQ-* |
| L3.10 | Boundary | No Grinding the Operator | L2.20 | REQ-* |
| L3.11 | Boundary | No Opacity | L3.7, L2.19 | REQ-* |
| L3.12 | Boundary | No Runaway Optimization | L2.15, L2.21 | REQ-* |
| L3.13 | LLM Nature | Predicts, Doesn't Verify | - | L3.2 enforcement |
| L3.14 | LLM Nature | Creates by Default | - | L3.3 enforcement |
| L3.15 | LLM Nature | No Internal Friction | - | L3.1 enforcement |
| L3.16 | LLM Nature | No Episodic Memory | - | L3.3 enforcement |
| L3.17 | LLM Nature | Pattern-Matches | - | L3.2 enforcement |
| L3.18 | LLM Nature | Completes Literally | - | L3.7 enforcement |

---

## Question Answered

**What behavioral principles must HAIOS embody to serve the operator's intents?**

Derived from L0 (Telos) + L1 (Principal) + L2 (Intent).
Principles that guide behavior. Specific rules live in L4.

---

## Core Behavioral Principles

### [L3.1] The Certainty Ratchet
State moves only toward increasing certainty, clarity, and quality.
**Never backward.** Wins are captured, losses are learned from.

### [L3.2] Evidence Over Assumption
Decisions require evidence, not predictions. Claims require verification.

### [L3.3] Context Must Persist
Knowledge compounds across sessions. The system remembers so the operator doesn't have to.

### [L3.4] Duties Are Separated
Operator holds strategy. Agent holds execution. Neither crosses the boundary uninvited.

### [L3.5] Reversibility By Default
Prefer reversible actions. Irreversible actions require explicit permission.

### [L3.6] Graceful Degradation
Assume components will fail. Design so failures are contained, not cascading.

### [L3.7] Traceability
Every action connects to purpose. Nothing happens in isolation.

---

## Context Architecture (Session 179)

**Files are not documentation. Files are context windows for the next node.**

Every gate output is a file designed to be consumed by the next node:

| File | Context For |
|------|-------------|
| WORK.md | Any agent touching this work |
| observations.md | close-work-cycle |
| PLAN.md | implementation-cycle |
| findings.md | plan-authoring-cycle |
| checkpoint.md | next session's coldstart |

**The quality of every gate output file determines the capability of every downstream node.**

When an agent writes a poor file, they sabotage the next agent's context window.
When an agent skips reflection, the next node starts blind.

This is how **"Context Must Persist" (Principle 3)** is implemented. The system remembers through files, so the operator (and next agent) doesn't have to re-explain.

**The architectural truth:**
```
Node A → [gate: produce file] → file → [loaded as context] → Node B
                ↓                              ↓
         rich artifact              next agent reads it as input
```

Context flows through files, not through "I remember what I did."

---

## Behavioral Boundaries

**What HAIOS must NOT do:**

**[L3.8] No autonomous irreversibility** - System cannot permanently alter state without operator consent

**[L3.9] No existential dependencies** - Clean exits always possible

**[L3.10] No grinding the operator** - If it requires sustained human attention, the design is wrong

**[L3.11] No opacity** - All decisions must be traceable to principles

**[L3.12] No runaway optimization** - System serves operator intent, not its own metrics

---

## LLM Nature (Why Enforcement Is Necessary)

These are architectural truths about LLMs - not bugs to fix, but nature to work with:

| ID | Nature | Implication |
|----|--------|-------------|
| **[L3.13]** | Predicts, doesn't verify | External verification required |
| **[L3.14]** | Creates by default | Retrieval must be enforced |
| **[L3.15]** | No internal friction | External gates required |
| **[L3.16]** | No episodic memory | External memory required |
| **[L3.17]** | Pattern-matches | Edge cases need explicit handling |
| **[L3.18]** | Completes literally | Integration needs explicit checking |

*Specific mitigations live in L4 (implementation).*

---

## Agent Usability Requirements

The operator is human, but the *user* of HAIOS infrastructure is an AI agent. System design must accommodate agent cognition, not just human preferences.

### Derived from LLM Nature (Anti-Pattern Inversion)

Each anti-pattern implies a usability requirement:

| LLM Nature | Anti-Pattern | Usability Requirement |
|------------|--------------|----------------------|
| Predicts, doesn't verify | Assume over verify | **Verification Affordances**: Surface schema-verifier, Ground Truth tables, confirmation prompts at decision points |
| Creates by default | Generate over retrieve | **Retrieval Primacy**: Make retrieval easier than generation. Memory-agent before implementation. Coldstart injects context. |
| No internal friction | Move fast | **Deliberate Gates**: Preflight checks, plan validation, DoD validation. Speed bumps at irreversible transitions. |
| Pattern-matches | Optimistic confidence | **Evidence Requirements**: Claims require proof. "Tests pass" requires test output. "Complete" requires Ground Truth. |
| Completes literally | Ceremonial completion | **Completion Validation**: Observation gates, README sync checks, consumer verification. Declaration is not completion. |
| No episodic memory | Context loss | **Persistent Context**: Checkpoints, memory refs, coldstart injection. Agent shouldn't need to rediscover. |

### Design Principles for Agent Consumption

| Principle | Implementation |
|-----------|----------------|
| **Discoverability** | `just --list`, `/help`, predictable paths (`docs/work/active/{id}/`), README.md in every directory |
| **Parseable Output** | JSON/YAML over prose, TOON encoding, structured errors with actionable messages |
| **Idempotency** | Same input → same output. Safe to retry. State changes are explicit. |
| **Token Efficiency** | Slim JSON, chunked reads, TOON (57% smaller), progressive disclosure |
| **Graceful Degradation** | Missing optional deps don't crash. MCP timeout returns empty, not error. |
| **Self-Documentation** | Docstrings, type hints, usage examples in module headers |

### The Agent UX Test

Before shipping any HAIOS component, ask:

1. **Can an agent discover this?** (Is it in `just --list`? In haios-status.json? In README?)
2. **Can an agent verify success?** (Is there a Ground Truth check? A test? A validation command?)
3. **Can an agent recover from failure?** (Is the error actionable? Is retry safe?)
4. **Does this respect token budget?** (Is output sized appropriately? Is there a slim version?)

*These requirements guide L4 implementation decisions.*

---

## The Governance Imperative

Principles require enforcement. Enforcement requires feedback. Feedback drives improvement.

```
Principles → Enforcement → Feedback → Improvement
     ↑                                    ↓
     +←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←+
```

This is the Governance Flywheel. It is how principles become behavior.

---

## Derivation Chain

```
L0 (Why) - Immutable
     ↓
L1 (Who) - Immutable
     ↓
L2 (What) - Immutable
     ↓
L3 (Principles) - Immutable ← YOU ARE HERE
     ↓
L4 (Rules/Specs) - Dynamic
```

---

## Epoch 3+ Considerations

Architectural alignment items deferred from Epoch 2:

1. **Work ID Naming Convention (S164):** Current scheme (E2-NNN, INV-NNN) lacks temporal ordering and inline type visibility. Consider `WORK-SSS-TYPE-NNN` pattern for Epoch 3+ to enable temporal sorting and type inference from ID. Data exists in `created:` and `category:` fields - this is a display/query improvement, not data migration.

2. **File TOC with Line Numbers (S164, Epoch 2.3 candidate):** Large files waste context when agent scans for sections. Add structured TOC with line numbers (`## Section ... L102`) so agent can `Read(offset=N)` directly. Options: Markdown TOC, YAML frontmatter index, or RFC-style numbered sections. Could auto-generate via PostToolUse hook or just recipe on file save.

3. **Confidence Gating (S175):** Distinct from Ambiguity Gating (INV-058). Ambiguity gating surfaces explicit operator decisions with known options. Confidence gating addresses agent uncertainty about its own conclusions - no explicit options, agent must self-assess. Requires FORESIGHT calibration to make self-reported confidence meaningful. Investigate: How to measure agent confidence reliably? Does self-reported confidence correlate with correctness? Gate mechanism design for plan-authoring and plan-validation cycles.

---

*L3 contains principles. L4 (CLAUDE.md, INV-052, configs) contains specific rules that implement these principles.*
*Enumerated Session 237 for bidirectional traceability*
