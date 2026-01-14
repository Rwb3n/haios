# generated: 2026-01-06
# System Auto: last updated on: 2026-01-06T22:01:01
# Section 21: Cognitive Notation

Generated: 2026-01-06 (Session 179)
Source: Operator-Agent dialogue + external research (pidgin investigation)
Status: PRINCIPLE (foundational)
Depends: S20 (Pressure Dynamics)

---

## The Insight

Pressure dynamics (S20) defines WHAT rhythm the agent needs: inhale/exhale, volumous/tight.

Cognitive notation defines HOW to signal that rhythm in a way the model reliably understands.

**The model has training priors on certain notations. Use them.**

---

## RFC 2119 as Pressure Signals

The RFC 2119 keywords aren't documentation style - they're **cognitive scaffolding**:

| Keyword | Pressure | Model Prior | Meaning to Agent |
|---------|----------|-------------|------------------|
| `MUST` | Tight/high | Very strong | Gate. Binary. Cannot proceed without. |
| `MUST NOT` | Tight/high | Very strong | Hard boundary. Do not cross. |
| `SHOULD` | Medium | Strong | Prefer this. Flex exists but justify deviation. |
| `SHOULD NOT` | Medium | Strong | Avoid this. Flex exists but justify. |
| `MAY` | Volumous/low | Strong | Optional. Space to explore. No pressure. |

**Usage in phase definitions:**

```markdown
## EXPLORE Phase [MAY]
Query memory. Read files. Notice what's there.
No required output. Space to discover.

## COMMIT Phase [MUST]
Write exactly one finding.
Gate: output is non-empty.
```

The `[MAY]` and `[MUST]` annotations tell the model what kind of pressure this phase has.

---

## Operators as Flow Signals

From programming languages, the model has strong priors on flow operators:

| Operator | Origin | Meaning | Use in HAIOS |
|----------|--------|---------|--------------|
| `\|>` | F# | Pipe: output flows to input | Phase chaining |
| `>>` | Haskell | Compose, discard context | Stateless handoff |
| `>>=` | Haskell | Bind, carry context | Stateful handoff |
| `\|\|\|` | F#/Erlang | Parallel execution | Concurrent phases |
| `??` | C# | Fallback on null/failure | Error recovery |
| `?:` | C | Ternary conditional | Branch |

**Usage in cycle definitions:**

```
RECALL [MAY] |> NOTICE [MAY] |> COMMIT [MUST]
```

Reads as: "Output of RECALL flows to NOTICE flows to COMMIT. First two are low pressure, last is gate."

---

## Mathematical Notation as Quantifiers

The model has strong priors on mathematical symbols:

| Symbol | Meaning | Use in HAIOS |
|--------|---------|--------------|
| `∀` | For all | Apply to every item |
| `∃` | There exists | Find at least one |
| `Σ` | Sum/aggregate | Collect results |
| `∈` | Member of | Check containment |
| `→` | Implies/leads to | Causal chain |
| `∧` `∨` `¬` | And/or/not | Boolean gates |

**Usage:**

```
∀ work_item ∈ active: validate(item) → archive(item)
```

Reads as: "For all work items in active set, validation leads to archive."

---

## Tier 1 Operators (Very High Confidence)

These have saturated training data and stable semantics. Safe to use.

| Operator | Origin | Meaning |
|----------|--------|---------|
| `\|>` | F# | Sequential pipe |
| `??` | C# | Fallback on failure |
| `\|\|\|` | F#/Erlang | Parallel execution |
| `∀` `∃` `Σ` | Math | Quantifiers |
| `→` | Math/Logic | Implies |
| `∧` `∨` `¬` | Logic | Boolean |
| `MUST` `SHOULD` `MAY` | RFC 2119 | Obligation modals |

---

## Collision Risks

Some symbols have multiple meanings. Avoid or disambiguate:

| Symbol | Conflicts |
|--------|-----------|
| `\|` | Bash pipe, regex alternation, BNF choice |
| `!` | Chess good, Ruby force, Rust unwrap, factorial |
| `?` | Chess dubious, regex optional, Swift optional |
| `*` | Regex, multiply, pointer, glob |
| `#` | Chess checkmate, bash comment, markdown header |

**Rule:** Use unambiguous Tier 1 operators. Avoid collision-prone symbols.

---

## Application to HAIOS Skills

### Current (Natural Language Prose)

```markdown
### 2. OBSERVE Phase

**Goal:** Capture observations while work item is still in active/.

**Guardrails (MUST follow):**
1. **MUST create/populate observations.md**
2. **MUST validate observations gate**

**Actions:**
1. Check if observations.md exists...
```

### Target (Cognitive Notation)

```markdown
### 2. OBSERVE [MAY → MUST]

scaffold_observations |> populate [MAY] |> validate [MUST]

- scaffold: Create observations.md if not exists
- populate: Answer three questions (volumous, explore)
- validate: Gate - at least one answer non-empty (tight, binary)
```

The notation compresses 20 lines to 5, and the model understands it better.

---

## Phase Pressure Annotation

Every phase should be annotated with its pressure type:

```
[MAY]      - Volumous. Explore. No required output.
[SHOULD]   - Medium. Expected but flexible.
[MUST]     - Tight. Gate. Binary pass/fail.
```

Well-designed cycles alternate:

```
[MAY] |> [MAY] |> [MUST] |> [MAY] |> [MUST]
inhale   inhale   exhale   inhale   exhale
```

---

## The Pidgin Hypothesis

**Hypothesis:** Symbolic notation degrades slower than natural language as instruction complexity increases.

**Rationale:**
- Operators have precise, consistent semantics in training data
- The syntax IS the structure - no interpretation needed
- Each operator boundary is discrete, not fuzzy like "and then"

**Evidence needed:** Empirical testing (see INV-PIDGIN-001 for methodology)

**Implication for HAIOS:** If confirmed, skill definitions should migrate from prose to notation.

---

## Connection to Anti-Patterns

| Anti-pattern | NL Failure | Notation Counter |
|--------------|------------|------------------|
| Move fast | "then" chains blur together | `\|>` creates discrete boundaries |
| Ceremonial completion | Checkboxes blend | `[MUST]` gates are binary |
| Skip reflection | Prose invites skimming | `[MAY]` signals "pause here" |
| Lose sequence | Long NL degrades | Operators preserve order |

---

## Implementation Path

1. **Annotate existing skills** with `[MAY]` / `[SHOULD]` / `[MUST]` pressure markers
2. **Add flow notation** to cycle diagrams: `phase1 |> phase2 |> phase3`
3. **Test comprehension** - does the model follow notation better than prose?
4. **Migrate incrementally** - don't rewrite everything, evolve

---

## Related

- S20: Pressure Dynamics (the rhythm this notation expresses)
- S19: Skill and Work Item Unification (decomposition enables notation)
- L3: Functional Requirements (anti-patterns this counters)
- INV-PIDGIN-001: Empirical investigation of notation vs NL degradation
- RFC 2119: Source of obligation modals

---

*This document defines a notation system for expressing pressure dynamics in a form the model reliably understands. It bridges biological metaphor (S20) to implementation.*
