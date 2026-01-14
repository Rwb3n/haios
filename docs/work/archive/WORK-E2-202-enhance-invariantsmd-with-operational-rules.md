---
template: work_item
id: E2-202
title: Enhance invariants.md with Operational Rules
status: complete
owner: Hephaestus
created: 2025-12-26
closed: 2025-12-26
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: INV-037
spawned_by_investigation: INV-037
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
- node: backlog
  entered: 2025-12-26 11:53:15
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-26
last_updated: '2025-12-26T13:57:20'
---
# WORK-E2-202: Enhance invariants.md with Operational Rules

@docs/README.md
@docs/epistemic_state.md

---

## Context

INV-037 created invariants.md to surface L1 context (evergreen philosophical facts) extracted from buried archives. However, second pass review revealed invariants.md captures **philosophy** but not **operational rules**:

**Missing content identified:**
1. Subagent isolation rules (schema-verifier MUST, preflight-checker REQUIRED)
2. Work lifecycle invariants (ADR-033 DoD: tests + WHY + docs)
3. Memory governance (ingester_ingest > memory_store)
4. Anti-pattern catalog (Static Registration, Ceremonial Completion)

These are true invariants - rules that MUST NOT change between sessions - but they're scattered across CLAUDE.md where they're mixed with session-specific guidance that evolves.

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

**Updated based on INV-038 findings:**

- [x] Add "Subagent Isolation" principle to Operational Rules (principle, not specific names)
- [x] Add "Definition of Done" to Operational Rules (Tests + WHY + Docs)
- [x] Add "WHY Primacy" to Operational Rules (reasoning compounds across sessions)
- [x] Add "LLM Anti-Patterns" section (6 evergreen patterns from epistemic_state.md)
- [x] Verify invariants.md remains <100 lines (L1 should be compact) - exactly 100 lines

**Rationale from INV-038:**
- Subagent names (schema-verifier, preflight-checker) are L2 - stay in CLAUDE.md
- DoD and WHY Primacy are true L1 invariants from ADR-033
- 6 anti-patterns are fundamental LLM truths, not implementation-specific
- Memory governance details are L2 - stay in CLAUDE.md

---

## History

### 2025-12-26 - Created (Session 122)
- Initial creation
- Work-creation-cycle: VERIFY, POPULATE, READY complete
- Context: INV-037 second pass identified missing operational rules
- Deliverables: 5 specific enhancements to invariants.md

### 2025-12-26 - Updated (Session 122)
- INV-038 completed - validated and refined scope
- Updated deliverables based on investigation findings
- Clarified L1 vs L2 distinction for each item

### 2025-12-26 - Implemented (Session 122)
- Added Subagent Isolation, DoD, WHY Primacy to Operational Rules
- Added LLM Anti-Patterns section with 6 patterns
- invariants.md now exactly 100 lines

---

## References

- INV-037: Context Level Architecture (spawned this work)
- E2-200: Original invariants.md creation
- ADR-033: Work Item Lifecycle Governance (DoD criteria to extract)
- INV-012: Static Registration Anti-Pattern (anti-pattern to document)
- E2-105: Ceremonial Completion (anti-pattern to document)
