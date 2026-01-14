---
template: implementation_plan
status: approved
date: 2025-11-27
title: Refinement Layer Stage 3: Proposal
directive_id: PLAN-REFINEMENT-S3
version: 1.0
---
# generated: 2025-11-27
# System Auto: last updated on: 2025-11-27

# Refinement Layer Stage 3: Proposal

> **Navigation:** [Meta-Plan](refinement-layer-meta-plan.md) | [Stage 2: Analysis](refinement-layer-S2-analysis.md)

## 1. Executive Summary

We propose implementing a **Metadata-Driven Refinement Loop** that transforms raw project artifacts (Doxa) into a structured knowledge graph of Principles (Episteme) and Patterns (Techne). This approach requires **zero schema migrations** and leverages the existing `sqlite-vec` infrastructure for semantic deduplication.

---

## 2. Architecture: The Refinement Loop

The Refinement Layer is not a new database, but a **process** that runs on top of the existing one.

### Component Diagram

```mermaid
graph TD
    A[Raw Memory (Doxa)] -->|Input| B[Refinement Agent]
    B -->|LLM Analysis| C{Classification}
    C -->|Episteme/Techne| D[Vector Deduplication]
    C -->|Doxa| E[Metadata Tagging]
    D -->|Match Found| F[Link to Existing]
    D -->|No Match| G[Create New Concept]
    G --> H[Human Validation Queue]
```

---

## 3. Schema Strategy (Zero-Migration)

We will utilize the flexible `memory_metadata` and `memory_relationships` tables.

### Metadata Schema
```json
{
  "knowledge_type": "episteme | techne | doxa",
  "refinement_status": "raw | processed | validated",
  "refinement_confidence": 0.95,
  "refinement_model": "gemini-1.5-pro"
}
```

### Relationship Types
-   `derived_from`: Links a Directive (Doxa) to a Principle (Episteme).
-   `implements`: Links a Code Snippet (Techne) to a Pattern (Techne).
-   `justifies`: Links a Principle (Episteme) to a Decision (Doxa).

---

## 4. Tooling & Implementation

### 1. New CLI Command
`haios refinement run [options]`
-   `--limit <n>`: Process N items.
-   `--type <type>`: Filter by raw type (e.g., 'Directive').
-   `--dry-run`: Show what would be created/linked without committing.

### 2. New MCP Tool
`memory_refine(memory_id, classification, extracted_concepts)`
-   Allows agents to perform refinement on-the-fly or in batches.

### 3. Refinement Logic (Python)
```python
def refine_memory(memory):
    # 1. LLM Extraction
    analysis = llm.analyze(memory.content)
    
    # 2. Update Metadata
    db.update_metadata(memory.id, {
        "knowledge_type": analysis.type,
        "refinement_status": "processed"
    })
    
    # 3. Process Extracted Concepts
    for concept in analysis.concepts:
        # Vector Search for duplicates
        matches = db.search_vectors(concept.embedding, threshold=0.9)
        
        if matches:
            # Link to existing
            db.add_relationship(memory.id, matches[0].id, "derived_from")
        else:
            # Create new Episteme Memory
            new_id = db.create_memory(concept.content, type="Concept")
            db.update_metadata(new_id, {"knowledge_type": "episteme"})
            db.add_relationship(memory.id, new_id, "derived_from")
```

---

## 5. Phased Rollout Plan

### Phase 1: Foundation (Current Sprint)
-   Implement `haios refinement` CLI.
-   Implement `RefinementManager` class.
-   Run on small sample (ADRs) to validate prompts.

### Phase 2: Batch Processing
-   Run on full corpus of Directives (18k items).
-   Human review of created Episteme concepts.

### Phase 3: Continuous Refinement
-   Integrate into Ingestion Pipeline (auto-refine on insert).
-   Expose via MCP for agent-driven gardening.

---

## 6. Success Criteria

1.  **Taxonomy Coverage:** >50% of "Directives" classified as Doxa/Techne.
2.  **Principle Extraction:** Creation of a "Core Principles" graph (approx. 100-200 nodes).
3.  **Deduplication:** "Idempotency" appears as 1 Episteme node, linked to N Directives.
4.  **Queryability:** Ability to answer "What are our core architectural principles?" using only Episteme nodes.

---

## 7. Handover Status

**Stage 3 Complete.**
Ready for **Stage 4: Validation** to stress-test this proposal against edge cases and operator constraints.
