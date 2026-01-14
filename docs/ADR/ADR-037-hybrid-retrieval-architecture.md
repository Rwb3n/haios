---
template: architecture_decision_record
status: accepted
date: 2025-12-14
adr_id: ADR-037
title: "Hybrid Retrieval Architecture"
author: Hephaestus
session: 72
lifecycle_phase: decide
decision: accepted
backlog_id: E2-045
spawned_by: INV-010
---
# generated: 2025-12-14
# System Auto: last updated on: 2025-12-14 13:31:04
# ADR-037: Hybrid Retrieval Architecture

@docs/README.md
@docs/epistemic_state.md

> **Status:** Accepted
> **Date:** 2025-12-14
> **Decision:** Implement retrieval modes for use-case-specific memory search

---

## Context

INV-010 investigation revealed that memory retrieval returns philosophically-related content instead of task-relevant content. Coldstart needs "what was I working on?" but gets "what is HAIOS?"

**Root Causes (all confirmed):**
- H1: Static query formulation - no dynamic refinement
- H2: Semantic similarity bias - `filters` parameter exists but UNUSED in SQL
- H3: No temporal weighting - recent and old content equal priority
- H4: Embedding distribution skewed - recent 0.5%, older 99.5%
- H5: Synthesis dilution - 98.6% of recent content is SynthesizedInsight

The core problem: a single retrieval algorithm cannot serve multiple use cases. Session recovery needs recent non-synthesis content. Knowledge lookup needs episteme/techne types. Strategy injection needs reasoning traces.

---

## Decision Drivers

- **Coldstart context bloat:** 60k tokens consumed with low signal-to-noise ratio
- **Use-case mismatch:** Pure semantic search optimizes for similarity, not relevance
- **Synthesis dilution:** SynthesizedInsight concepts (philosophical generalizations) crowd out specific technical decisions
- **Backward compatibility:** Default behavior must not break existing queries

---

## Considered Options

### Option A: Temporal Decay Weighting
**Description:** Apply time-based decay factor to similarity scores (newer = higher weight)

**Pros:**
- Simple to implement (multiply score by decay function)
- Naturally surfaces recent content

**Cons:**
- Doesn't solve synthesis dilution
- May penalize legitimately relevant older content
- Single dimension (time) may not match use case needs

### Option B: Retrieval Modes (SELECTED)
**Description:** Add `mode` parameter with predefined filters for different use cases

**Pros:**
- Explicit control per use case
- Backward compatible (default mode = current behavior)
- Extensible (add new modes without changing API)
- Addresses synthesis dilution directly via type filtering

**Cons:**
- Requires callers to know which mode to use
- Modes are predefined, not dynamic

### Option C: Query Expansion/Rewriting
**Description:** LLM-based query refinement before search

**Pros:**
- Dynamic adaptation to query intent
- Could learn optimal reformulations

**Cons:**
- Adds latency and cost (LLM call per query)
- Non-deterministic results
- Complex to implement and test

---

## Decision

**Implement Option B: Retrieval Modes**

Add `mode` parameter to `search_memories()` with three predefined modes:

| Mode | Filter | Use Case |
|------|--------|----------|
| `semantic` | None (default) | General similarity search, backward compatible |
| `session_recovery` | Exclude `SynthesizedInsight` | Coldstart - get actual session work |
| `knowledge_lookup` | Include only `episteme`, `techne`, `Critique`, `Decision`, `Directive`, `Proposal` | Targeted knowledge retrieval |

**Implementation locations:**
- `haios_etl/database.py:search_memories()` - Core filtering logic
- `haios_etl/retrieval.py:search()` and `search_with_experience()` - Pass mode through
- `haios_etl/mcp_server.py:memory_search_with_experience()` - Expose to MCP clients
- `.claude/commands/coldstart.md` - Use `mode='session_recovery'`

---

## Consequences

**Positive:**
- Coldstart retrieves actual session work instead of philosophical synthesis
- Callers have explicit control over retrieval behavior
- No breaking changes to existing queries (default = `semantic`)
- Foundation for future modes (e.g., `strategy_injection`, `entity_focused`)

**Negative:**
- Callers must choose appropriate mode (mild cognitive load)
- Mode definitions are hardcoded, not configurable

**Neutral:**
- Does not address embedding distribution skew (99.5% older content)
- Does not implement temporal weighting (deferred to future work)

---

## Implementation

- [x] Step 1: Write 5 failing tests (TDD)
- [x] Step 2: Add `mode` parameter to `database.py:search_memories()`
- [x] Step 3: Implement `session_recovery` SQL filter (exclude SynthesizedInsight)
- [x] Step 4: Implement `knowledge_lookup` SQL filter (type whitelist)
- [x] Step 5: Update `retrieval.py` methods with mode passthrough
- [x] Step 6: Update `mcp_server.py` MCP tool with mode parameter
- [x] Step 7: Update `coldstart.md` to use `mode='session_recovery'`
- [x] Step 8: Verify all 202 tests pass

**Tests:** `tests/test_database.py` (4 new tests), `tests/test_mcp.py` (1 new test)

---

## References

- **Investigation:** `docs/investigations/INVESTIGATION-INV-010-memory-retrieval-architecture-mismatch.md`
- **Plan:** `docs/plans/PLAN-ADR-037-HYBRID-RETRIEVAL-ARCHITECTURE.md`
- **Session 72 Checkpoint:** `docs/checkpoints/2025-12-14-01-SESSION-72-adr037-hybrid-retrieval.md`
- **Memory:** Concepts 71410-71421

---
