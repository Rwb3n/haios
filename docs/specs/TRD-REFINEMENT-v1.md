---
template: implementation_plan
status: approved
date: 2025-11-27
title: Knowledge Refinement Layer Specification
directive_id: TRD-REFINEMENT-v1
version: 1.0
---
# generated: 2025-11-27
# System Auto: last updated on: 2025-11-27

# TRD-REFINEMENT-v1: Knowledge Refinement Layer

> **Navigation:** [System Spec](../COGNITIVE_MEMORY_SYSTEM_SPEC.md) | [Meta-Plan](../plans/refinement-layer-meta-plan.md)

## 1. Introduction

The **Knowledge Refinement Layer** is a post-ingestion process that transforms raw project artifacts (Doxa) into a structured knowledge graph of Principles (Episteme) and Patterns (Techne). It addresses the "signal-to-noise" problem in the current database, where process artifacts (Critiques, Directives) outnumber structured concepts by 50:1.

## 2. Taxonomy Definition

We adopt the **Greek Triad** for knowledge classification:

| Type | Description | Handling |
| :--- | :--- | :--- |
| **Episteme** | Universal Truths, Principles, Invariants. | Global Deduplication. High reuse. |
| **Techne** | Patterns, Methods, Skills, "How-To". | Pattern Matching. Context-aware reuse. |
| **Doxa** | Decisions, Constraints, Opinions, Project Reality. | Context-bound. Linked to Episteme/Techne. |

## 3. Schema Specifications

### 3.1 Metadata (Migration 004)
We create the `memory_metadata` table.

| Key | Value Domain | Description |
| :--- | :--- | :--- |
| `knowledge_type` | `episteme`, `techne`, `doxa` | The primary classification. |
| `refinement_status` | `raw`, `processed`, `validated` | Workflow state. |
| `refinement_confidence` | `0.0` - `1.0` | LLM confidence score. |
| `refinement_model` | String | Model used for refinement (e.g., `gemini-1.5-pro`). |

### 3.2 Relationships (Migration 004)
We create the `memory_relationships` table to support semantic links.

**Migration:** `004_add_refinement_tables.sql`
-   **Action:** Create `memory_metadata` and `memory_relationships` tables.
-   **Relationship Types:**
    -   `implements`: Techne -> Episteme (e.g., "Retry Logic" implements "Resilience").
    -   `justifies`: Episteme -> Doxa (e.g., "CAP Theorem" justifies "Use Cassandra").
    -   `derived_from`: Doxa -> Episteme (e.g., "Use Cassandra" derived from "High Availability").

## 4. Component Design

### 4.1 RefinementManager (`haios_etl/refinement.py`)
Core logic class.

-   `scan_raw_memories(limit: int) -> List[Memory]`
-   `refine_memory(memory: Memory) -> RefinementResult`
-   `deduplicate_concept(embedding: List[float]) -> Optional[Memory]`
-   `create_concept(content: str, type: str) -> int`
-   `link_memories(source: int, target: int, type: str)`

### 4.2 CLI (`haios_etl/cli.py`)
New command group.

-   `haios refinement run --limit <n> --dry-run`
-   `haios refinement stats`

### 4.3 MCP Tool (`haios_etl/mcp_server.py`)
-   `memory_refine(memory_id, classification, extracted_concepts)`

## 5. Refinement Algorithm

1.  **Load Cache:** Fetch all existing `Episteme` embeddings into local FAISS/Annoy index (or simple list) for speed.
2.  **Scan:** Select `memories` where `refinement_status` IS NULL LIMIT N.
3.  **Analyze (LLM):**
    -   Prompt: "Classify as Episteme/Techne/Doxa. Extract underlying principles."
4.  **Process Extractions:**
    -   For each extracted concept:
        -   **Vector Search:** Check against Cache (Threshold 0.9).
        -   **Match:** Link original memory to existing Episteme (`derived_from`).
        -   **No Match:** Create new Memory (Type='Concept', Metadata='Episteme'). Add to Cache. Link.
5.  **Update:** Set `refinement_status` = 'processed'.

## 6. Success Metrics

-   **Coverage:** >50% of `Directive` artifacts classified.
-   **Deduplication:** <5% duplication rate for `Episteme` nodes (e.g., "Idempotency" appears once).
-   **Graph Density:** Average `Episteme` node has >5 incoming links from `Doxa`.

## 7. Implementation Plan

1.  **Migration:** Create `004_add_refinement_relationships.sql`.
2.  **Core:** Implement `RefinementManager`.
3.  **CLI:** Implement `haios refinement` commands.
4.  **Validation:** Run on 100 sample items.
5.  **Scale:** Run on full corpus.

## 8. Test Requirements

### 8.1 Unit Tests (`tests/test_refinement_unit.py`)
-   **Mock LLM:** Verify `refine_memory` handles LLM responses correctly (valid JSON, error handling).
-   **Deduplication:** Verify `deduplicate_concept` returns match when similarity > threshold.
-   **Classification:** Verify logic for mapping LLM output to `knowledge_type`.

### 8.2 Integration Tests (`tests/test_refinement_integration.py`)
-   **Database:** Verify `create_concept` inserts correct metadata.
-   **Linking:** Verify `link_memories` creates correct `relationship_type` (including new types).
-   **Migration:** Verify `004` migration applies successfully and allows new relationship types.

### 8.3 Functional Tests
-   **CLI:** Verify `haios refinement run --dry-run` outputs expected plan without DB writes.
-   **End-to-End:** Run refinement on a known "Directive" and verify an "Episteme" is created and linked.

---
**Status:** Ready for Implementation.
