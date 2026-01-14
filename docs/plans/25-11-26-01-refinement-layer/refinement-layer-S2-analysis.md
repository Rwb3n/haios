---
template: implementation_plan
status: approved
date: 2025-11-27
title: Refinement Layer Stage 2: Analysis
directive_id: PLAN-REFINEMENT-S2
version: 1.0
---
# generated: 2025-11-27
# System Auto: last updated on: 2025-11-27

# Refinement Layer Stage 2: Analysis

> **Navigation:** [Meta-Plan](refinement-layer-meta-plan.md) | [Stage 1: Investigation](refinement-layer-S1-investigation.md)

## 1. Executive Summary

Stage 1 revealed a database dominated by **Doxa** (process artifacts). Stage 2 analyzes how to transform this into a structured knowledge base. The analysis concludes that a **metadata-driven approach** using the existing schema is sufficient for the MVP, but a **multi-pass refinement workflow** is required to distill Episteme and Techne from the raw Doxa.

---

## 2. Gap Analysis

| Feature | Spec Vision | Current Reality | Gap |
| :--- | :--- | :--- | :--- |
| **Taxonomy** | Structured Knowledge | Flat list of "types" (Critique, Directive) | **Critical:** No distinction between signal (Truth) and noise (Process). |
| **Schema** | `memory_metadata` | Unused for classification | **Low:** Schema exists, just need to populate it. |
| **Workflow** | Ingestion -> Retrieval | Ingestion -> Storage | **High:** Missing the "Refinement" step to process stored data. |
| **Deduplication** | Semantic Dedup | Exact Hash Dedup | **High:** "Idempotency" concept appears hundreds of times. |

---

## 3. Proposed Taxonomy: The "Greek Triad"

We will adopt the **Episteme-Techne-Doxa** taxonomy as the core classification system.

| Level | Type | Description | Handling Strategy |
| :--- | :--- | :--- | :--- |
| **L1** | **Episteme** | Universal Truth / Principle | **Global Deduplication:** Only one "CAP Theorem" should exist. |
| **L2** | **Techne** | Pattern / Method / Skill | **Pattern Matching:** Group similar implementations (e.g., "Retry Logic"). |
| **L3** | **Doxa** | Decision / Constraint / Opinion | **Contextual:** Keep linked to specific projects/spaces. |

**Mapping Current Types:**
-   `Critique` -> **Doxa**
-   `Directive` -> **Doxa** (or **Techne** if generalized)
-   `Proposal` -> **Doxa**
-   `ADR` -> **Doxa** (containing **Episteme** justifications)
-   `Concept` -> **Episteme** (mostly)

---

## 4. Minimum Viable Refinement Schema

We do **not** need new tables. We will use `memory_metadata` and `memory_relationships`.

### Metadata Keys
-   `knowledge_type`: `episteme`, `techne`, `doxa`
-   `refinement_status`: `raw`, `pending_review`, `refined`
-   `confidence_score`: `0.0` - `1.0`

### Relationships
-   `Doxa` **derived_from** `Episteme`
-   `Techne` **implements** `Episteme`
-   `Doxa` **uses** `Techne`

---

## 5. Workflow: The Refinement Loop

We propose a **Refinement Agent** (batch process) that runs periodically:

1.  **Scan:** Find memories with `refinement_status = 'raw'` (or null).
2.  **Analyze:** Use LLM to:
    -   Classify as Episteme/Techne/Doxa.
    -   Extract underlying principles (if Doxa).
3.  **Deduplicate:** Check if extracted principles already exist (Vector Search).
4.  **Link/Create:**
    -   If exists: Link current item to existing Episteme.
    -   If new: Create new Episteme memory.
5.  **Update:** Set `refinement_status = 'refined'`.

---

## 6. Risks & Mitigations

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| **Concept Explosion** | 1000s of duplicate "principles" | Strict vector similarity threshold for creating new Episteme. |
| **Hallucination** | LLM inventing fake principles | Human-in-the-loop validation for L1 (Episteme) creation. |
| **Cost** | High token usage for re-processing | Batch processing; prioritize high-value artifacts (ADRs) first. |

---

## 7. Handover Status

**Stage 2 Complete.**
Ready for **Stage 3: Proposal** to define the specific implementation details (Prompts, Tools, Scripts).
