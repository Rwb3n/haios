# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:12:49
# Critique Report: Ceremonies Arc (CH-011 through CH-017)

## Executive Summary

The Ceremonies arc contains 7 chapters defining the governance boundary for side-effects in HAIOS. Overall coherent and well-structured, but surfaces **23 implicit assumptions** with blocking issues around ceremony nesting, state change definition, and missing interface specifications.

**Overall Verdict: REVISE**

---

## Assumptions Registry

| ID | Chapter | Statement | Confidence | Risk if Wrong |
|----|---------|-----------|------------|---------------|
| A1 | CH-011 | All 19 ceremonies exist and are enumerable | medium | Contract applied to phantom ceremonies |
| A2 | CH-011 | YAML frontmatter parsing available in skill context | high | Skills cannot parse contracts |
| A3 | CH-011 | Input validation happens synchronously | medium | Async allows invalid starts |
| A4 | CH-011 | Pattern field uses regex syntax | low | Ambiguous interpretation |
| A5 | CH-012 | in_ceremony_context() works at any call depth | medium | Deep calls can't verify |
| A6 | CH-012 | Ceremony context is single-threaded | high | Concurrent ceremonies corrupt |
| A7 | CH-012 | "warn" mode is temporary for migration | medium | May persist indefinitely |
| A8 | CH-012 | Protected operations list is complete | low | New ops may bypass |
| A9 | CH-013 | CeremonyRunner and CycleRunner can coexist | high | Import conflicts |
| A10 | CH-013 | "No state changes in lifecycles" is enforceable | low | Lifecycles write artifacts |
| A11 | CH-013 | "-cycle" files can be renamed safely | medium | Hardcoded refs break |
| A12 | CH-014 | SessionState type is defined | medium | Ceremony can't pass state |
| A13 | CH-014 | Git commit in checkpoint succeeds | medium | Failure leaves inconsistent |
| A14 | CH-014 | Orphan work detection has clear definition | medium | False positives |
| A15 | CH-014 | /coldstart can use ceremony wrapper | high | Breaking change |
| A16 | CH-015 | DoD validation has access to required state | medium | Silent failures |
| A17 | CH-015 | "All work complete" is deterministic | medium | Lifecycle-specific completion |
| A18 | CH-015 | Review ceremonies are defined | low | Triggers undefined ceremony |
| A19 | CH-015 | Archive directory exists | high | Close fails |
| A20 | CH-016 | ingester_ingest function exists | medium | Memory commit fails |
| A21 | CH-016 | Four required questions enforced | medium | Incomplete observations |
| A22 | CH-016 | Observation IDs are unique | high | Collision breaks triage |
| A23 | CH-017 | Parent work is in valid spawn state | medium | Orphan chain created |

---

## Blocking Assumptions

- **A5** (Medium): ceremony_context() detection mechanism
- **A10** (Low): "state change" definition unclear

---

## Critical Conflict: Ceremony Nesting

**Chapters:** CH-012, CH-015, CH-016

- CH-012 Non-Goal: "Ceremony nesting (ceremonies don't nest)"
- CH-015: Close-work triggers observation-capture AND memory-commit
- CH-016: Integration shows close_work_ceremony invoking both

**This is implicit nesting.** Must resolve:
- Option A: Allow ceremony composition
- Option B: Restructure closure as single ceremony with steps

---

## Critical Conflict: Artifact vs State Change

**Chapters:** CH-013, CH-014

- CH-013: "Ceremonies produce state changes, not artifacts"
- CH-014: Checkpoint ceremony produces CheckpointDoc (an artifact)

**Resolution:** Clarify "artifact" means work output (code, spec), while ceremonies may produce governance artifacts (checkpoints, logs).

---

## Chapter-Specific Issues

### CH-011: Ceremony Contracts

**Gaps:**
- Contract versioning (migration path?)
- Validation error reporting format
- Partial contract satisfaction handling

### CH-012: Side Effect Boundaries

**Gaps:**
- Ceremony context failure handling
- Nested ceremony error handling
- "All ceremony skills use ceremony_context()" but skills are markdown

### CH-013: Ceremony Lifecycle Distinction

**Gaps:**
- "State changes" needs sharper definition
- Ceremony invocation from lifecycle interface undefined

**Issue:** CH-014 Checkpoint produces CheckpointDoc - is document an artifact?

### CH-014: Session Ceremonies

**Gaps:**
- Session recovery undefined
- Multiple session protection undefined
- Orphan work criteria undefined

### CH-015: Closure Ceremonies

**Gaps:**
- Partial closure handling undefined
- Memory commit integration unclear (nesting issue)
- Reopen capability missing

### CH-016: Memory Ceremonies

**Gaps:**
- Memory failure handling
- Observation schema validation
- Ceremony invocation order enforcement

### CH-017: Spawn Ceremony

**Gaps:**
- "Valid spawn point" undefined
- traces_to validation against L4
- WorkEngine.get_work_lineage() not in L4 spec

---

## Missing Interface Definitions

| Type | Needed By |
|------|-----------|
| SessionState | CH-014 |
| CeremonyResult | All ceremonies |
| DoDResult | CH-015 |
| Observation | CH-016 |
| Lineage | CH-017 |
| ceremony_runner instantiation | All |

---

## Recommendations

### Must Address Before Implementation

1. Resolve ceremony nesting conflict
2. Define SessionState schema
3. Clarify "state change" definition (governance vs artifacts)
4. Specify ceremony_context() thread-local pattern
5. Define orphan work criteria

### Should Address

6. Add ceremony inventory as CH-011 precondition
7. Define error/failure handling for each ceremony
8. Add graceful degradation for haios-memory unavailability
9. Align WorkEngine spec with lineage query
10. Add ceremony versioning strategy

---

*Critique generated: 2026-02-03*
*Verdict: REVISE*
