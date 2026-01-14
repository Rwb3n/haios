---
template: implementation_plan
status: approved
date: 2025-11-27
title: Refinement Layer Stage 4: Validation
directive_id: PLAN-REFINEMENT-S4
version: 1.0
---
# generated: 2025-11-27
# System Auto: last updated on: 2025-11-27

# Refinement Layer Stage 4: Validation

> **Navigation:** [Meta-Plan](refinement-layer-meta-plan.md) | [Stage 3: Proposal](refinement-layer-S3-proposal.md)

## 1. Executive Summary

Stage 4 stress-tested the "Refinement Loop" proposal against real-world scenarios, edge cases, and performance constraints. The validation confirms the approach is sound but highlights the need for **strict confidence thresholds** and **batch optimization** to avoid performance bottlenecks and "concept explosion".

---

## 2. Scenario Testing

We simulated the refinement logic against actual database content.

### Scenario A: The Directive
**Input:** "Use `sqlite-vec` for vector search." (Directive)
**Analysis:**
-   **Classification:** Doxa (Project Decision).
-   **Extraction:** "Vector Search" (Episteme), "SQLite Extension" (Techne).
-   **Result:** ✅ Correctly separates the *decision* (Doxa) from the *capability* (Episteme).

### Scenario B: The Critique
**Input:** "The `find_similar_reasoning_traces` function returns empty list." (Critique)
**Analysis:**
-   **Classification:** Doxa (Observation).
-   **Extraction:** "Reasoning Trace Retrieval" (Episteme).
-   **Result:** ✅ Links the bug report to the underlying concept.

### Scenario C: The Vague Instruction (Edge Case)
**Input:** "Ensure code is clean." (Directive)
**Analysis:**
-   **Classification:** Doxa.
-   **Extraction:** "Code Cleanliness" (Episteme?).
-   **Risk:** "Code Cleanliness" is too vague to be a useful node.
-   **Mitigation:** **Confidence Threshold.** If LLM confidence < 0.8, do not create new Episteme. Tag as Doxa only.

---

## 3. Performance Validation

**Volume:** ~18,000 Directives.
**Estimated Concepts:** ~3 per Directive = 54,000 extractions.
**Vector Search Cost:** 54,000 searches.

**Risk:** N+1 Query problem if doing 1 search per extraction.
**Mitigation:**
1.  **Local Cache:** Load all existing Episteme embeddings into memory (approx 200-500 vectors) for fast local similarity check.
2.  **Batching:** Process 100 items at a time, dedup locally, then write.

---

## 4. Human-in-the-Loop Feasibility

**Problem:** Reviewing 18,000 links is impossible.
**Solution:**
-   **Review only L1 (Episteme) creation.**
-   Expected L1 nodes: ~200-500.
-   Reviewing 500 nodes is feasible (approx 2-4 hours).
-   Links (Doxa -> Episteme) can be implicitly trusted if confidence is high.

---

## 5. Schema Compatibility Check

-   `memory_metadata` table supports JSON values? **Yes.**
-   `memory_relationships` table supports custom types? **Yes** (Check constraint might need update).
    -   *Check:* `CHECK(relationship_type IN ('supports', 'contradicts', ...))`
    -   *Finding:* The constraint is hardcoded in `memory_db_schema_v2.sql`.
    -   *Action:* We need to **ALTER** the check constraint or use existing types (`derived_from` is in the list).
    -   *Verification:* `derived_from` IS in the list. `implements` is NOT.
    -   *Adjustment:* Use `derived_from` for Doxa->Episteme. Use `supports` for Techne->Episteme? Or add `implements` via migration?
    -   *Decision:* **Add `implements` and `justifies` via Migration 004.**

---

## 6. Adjustments to Proposal

1.  **Migration 004:** Update `memory_relationships` check constraint to include `implements` and `justifies`.
2.  **Caching Strategy:** Explicitly require "Episteme Cache" in Refinement Agent.
3.  **Confidence Threshold:** Set default to 0.85.

---

## 7. Handover Status

**Stage 4 Complete.**
Ready for **Stage 5: Specification** to generate the final TRD and Migration Script.
