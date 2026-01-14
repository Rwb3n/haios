---
template: architecture_decision_record
status: accepted
date: 2025-12-09
adr_id: ADR-032
title: "Memory-Linked Work Governance"
author: Hephaestus
session: 50
lifecycle_phase: decide
decision: accepted
memory_refs: [64641-64652, 64653-64669]
---
# generated: 2025-12-09
# System Auto: last updated on: 2025-12-09 18:40:12
# ADR-032: Memory-Linked Work Governance

@docs/README.md
@docs/epistemic_state.md

> **Status:** Accepted
> **Date:** 2025-12-09
> **Decision:** Accepted

---

## Context

Session 50 investigation of the HAIOS memory learning system revealed that while infrastructure exists (64,640 concepts, 623 reasoning traces, 2,082 synthesis clusters), the system is not learning effectively:

1. **Strategy quality is poor** - Top strategies are meta-level ("Leverage Default Hybrid Search" 21x) not domain-specific
2. **Backlog items lack memory linkage** - No traceable connection between work items and supporting knowledge
3. **No closed learning loop** - Investigations produce insights that don't flow back into future work

The current state is a **leaky bucket** - knowledge goes in but doesn't compound.

---

## Decision Drivers

- **Knowledge Compounding:** Each session should build on previous learnings, not rediscover them
- **Traceability:** Should be able to answer "what memory supports this decision?" and "what work uses this concept?"
- **Mechanism Leverage:** Use existing hooks/skills/commands infrastructure, don't add new code paths
- **Friction Reduction:** "Make right way easy" - correct behavior should be the path of least resistance

---

## Considered Options

### Option A: Manual Documentation Only
**Description:** Document memory references in backlog items manually, no enforcement.

**Pros:**
- No implementation work
- Flexible

**Cons:**
- Will decay over time (already happening)
- No feedback loop
- Inconsistent application

### Option B: Full Automation
**Description:** Automatically extract and link memory references via hooks.

**Pros:**
- Zero manual effort
- Consistent application

**Cons:**
- Complex to implement
- May create low-quality links
- Black box behavior

### Option C: Governed Workflow with Rhythm (Recommended)
**Description:** Enforce memory linkage via governance mechanisms + periodic review cycle.

**Pros:**
- Leverages existing hook/skill/command infrastructure
- Human-in-the-loop for quality
- Creates virtuous cycle

**Cons:**
- Some manual effort required
- Needs discipline to maintain rhythm

---

## Decision

**Adopt Option C: Governed Workflow with Rhythm**

Establish a closed-loop pattern for memory-linked work:

```
Investigation -> Memory Storage -> Backlog Item -> Implementation -> Memory Storage
     ^                                                                    |
     +--------------------------------------------------------------------+
```

### Core Principles

1. **Investigation MUST produce memory references**
   - Use `ingester_ingest` to store findings as concepts
   - Record concept IDs for linkage

2. **Backlog items MUST link to memory**
   - Add `Memory:` field with concept references
   - PreToolUse hook warns (not blocks) on missing references

3. **Mechanisms layered appropriately**
   - Hook: Detect intent, inject context, warn on gaps
   - Skill: On-demand deep retrieval and analysis
   - Command: Explicit user-triggered actions

4. **Periodic rhythm maintains quality**
   - `/memory-audit` command surfaces unlinked items
   - Weekly review of memory coverage stats

---

## Consequences

**Positive:**
- Knowledge compounds across sessions
- Decisions are traceable to supporting evidence
- Future sessions can query "what do we know about X?"
- Backlog items have context, not just tasks

**Negative:**
- Overhead for storing memory references
- Risk of low-quality links if done carelessly
- Requires discipline to maintain

**Neutral:**
- Changes workflow slightly (must store to memory after investigations)
- Adds `Memory:` field to backlog item convention

---

## Implementation

Tracked via backlog items:

- [ ] **E2-021:** Memory Reference Governance + Rhythm (HIGH)
  - Add `memory_refs` field validation
  - Create `/memory-audit` command
  - Integrate with `/workspace`

- [ ] **E2-020:** Schema Discovery via Mechanisms (MEDIUM)
  - Demonstrates mechanism layering pattern
  - Hook + Skill + Command for schema access

- [ ] **INV-003:** Strategy Extraction Quality Audit (HIGH)
  - Validates memory system is learning useful things
  - May lead to extraction prompt revision

---

## Related Decisions

- **ADR-030:** Document Taxonomy and Lifecycle Classification (foundation)
- **ADR-031:** Workspace Awareness (enables `/workspace` integration)
- **DD-050-01 to DD-050-03:** Session 50 design decisions (source material)

---

## Memory References

This ADR is supported by:
- **Concepts 64641-64652:** Session 50 investigation findings
- **Concepts 64653-64669:** Session 50 design decisions (DD-050-01 to DD-050-03)

---

**Session:** 50
**Date:** 2025-12-09
**Status:** ACCEPTED
