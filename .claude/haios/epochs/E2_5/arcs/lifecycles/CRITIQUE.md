# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:11:49
# Critique Report: Lifecycles Arc (CH-001 through CH-006)

## Executive Summary

The six chapters in the Lifecycles Arc represent a coherent architectural refactoring from implicit lifecycle chaining to explicit pure-function semantics. However, the critique surfaces **23 implicit assumptions** across the chapters, with several cross-chapter conflicts and missing success criteria that should be addressed before implementation begins.

**Overall Verdict: REVISE**

---

## Assumptions Registry

| ID | Chapter | Statement | Confidence | Risk if Wrong |
|----|---------|-----------|------------|---------------|
| A1 | CH-001 | CycleRunner currently exists with a run() method that can be refactored | medium | Code structure doesn't match, requires larger rewrite |
| A2 | CH-001 | Typed output objects have defined schemas | low | Cannot return typed output without schema definition |
| A3 | CH-001 | "No auto-chaining" is the only behavior change needed | medium | Other implicit side effects may exist |
| A4 | CH-001 | All five lifecycles have same signature pattern | high | Validation has two inputs, others have one |
| A5 | CH-002 | Pause phases are always the final phase of each lifecycle | high | Mid-lifecycle pause breaks recognition logic |
| A6 | CH-002 | WorkEngine can determine lifecycle type from work item | medium | Lookup fails if lifecycle not stored |
| A7 | CH-002 | status: complete is appropriate for pause closure | medium | Users may expect different statuses |
| A8 | CH-002 | Pause always follows exhale phase | high | Validated by S27 |
| A9 | CH-003 | activity_matrix.yaml has single-item constraints to remove | medium | If constraints don't exist, nothing to change |
| A10 | CH-003 | Batch operations are sequential, not parallel | high | Stated in Non-Goals |
| A11 | CH-003 | Agent can context-switch between multiple designs | medium | Cognitive load may exceed benefit |
| A12 | CH-003 | Work items in batch share no dependencies | medium | Batch design breaks on dependencies |
| A13 | CH-004 | There is a single caller (operator or orchestrator) | low | Multiple callers cause conflicts |
| A14 | CH-004 | Output from one lifecycle is valid input to next | high | Validated in CH-001 |
| A15 | CH-004 | close-work-cycle currently auto-spawns | medium | If not, nothing to change |
| A16 | CH-004 | Prompting for next action is acceptable UX | medium | May feel like friction |
| A17 | CH-004 | Spawn ceremony (CH-017) ready before this chapter | low | Spawn option cannot be implemented |
| A18 | CH-005 | Templates currently have no contracts | medium | If they do, work is done |
| A19 | CH-005 | YAML frontmatter is parseable by governance | high | Standard pattern |
| A20 | CH-005 | Contract fields can be validated without running phase | medium | Some may need semantic validation |
| A21 | CH-005 | All work items have access to required input fields | low | Input contract may fail |
| A22 | CH-006 | Current templates are monolithic (200+ lines) | medium | If already fractured, work done |
| A23 | CH-006 | 30-50 lines is optimal template size | medium | May be too small/large |

---

## Blocking Assumptions

- **A2** (Low confidence): Typed output schemas not defined
- **A13** (Low confidence): Caller identity not defined
- **A17** (Low confidence): Spawn ceremony dependency
- **A21** (Low confidence): Input field availability

---

## Chapter-Specific Issues

### CH-001: Lifecycle Signature

**Gaps:**
- Missing schema definitions for output types
- No specification for lifecycle failure handling
- Return type vs side effects unclear

**Missing Success Criteria:**
- Output schema files exist and are validated
- Error cases return structured error types

### CH-002: Pause Semantics

**Gaps:**
- Pause vs Stop ambiguity (if closed at pause, how to continue?)
- S27 Breath Model phase names don't match lifecycle phases
- S27 shows multiple pauses, chapter shows one

**Missing Success Criteria:**
- Documentation explains pause closure vs resumption
- Mapping from S27 phases to lifecycle phases

### CH-003: Batch Mode

**Gaps:**
- Batch failure handling undefined
- Batch atomicity unclear (all-or-nothing?)
- Batch progress tracking undefined

**Missing Success Criteria:**
- Batch failure modes documented
- Dependency validation in batch operations

### CH-004: Caller Chaining

**Gaps:**
- Default behavior when no choice made
- Chaining vs piping distinction unclear
- Caller identity and authority undefined

**Missing Success Criteria:**
- Default behavior specified
- Timeout/blocking behavior specified

### CH-005: Phase Template Contracts

**Gaps:**
- Field storage location undefined
- Optional field handling undefined
- Contract evolution strategy missing

**Missing Success Criteria:**
- Field storage locations documented
- Contract versioning strategy

### CH-006: Template Fracturing

**Gaps:**
- Shared content handling undefined
- Phase name disambiguation needed
- Migration equivalence validation missing

**Missing Success Criteria:**
- Shared content strategy documented
- Migration validation approach

---

## Cross-Chapter Conflicts

### Conflict 1: CH-005/CH-006 Implementation Order

CH-006 depends on CH-005, but implementing contracts (CH-005) before fracturing (CH-006) means adding contracts twice.

**Recommendation:** Reverse dependency or implement in parallel.

### Conflict 2: S27 Terminology Mismatch

S27 shows INVESTIGATE, EPISTEMY, DESIGN phases. Lifecycle chapters show CONCLUDE, COMPLETE, DONE, REPORT, COMMIT.

**Recommendation:** Add explicit mapping table in CH-002.

---

## Recommendations

### Immediate (Before Implementation)

1. Define output schemas as prerequisite work item
2. Verify CycleRunner current API
3. Resolve CH-005/CH-006 order conflict
4. Add S27 mapping to CH-002

### Per-Chapter Prerequisites

- **CH-001:** Verify CycleRunner API, define output schemas
- **CH-002:** Create S27 mapping table
- **CH-003:** Verify activity_matrix.yaml, add batch failure modes
- **CH-004:** Define caller identity, verify close-work-cycle behavior
- **CH-005:** Audit existing templates, define field storage
- **CH-006:** Audit current template structure

---

*Critique generated: 2026-02-03*
*Verdict: REVISE*
