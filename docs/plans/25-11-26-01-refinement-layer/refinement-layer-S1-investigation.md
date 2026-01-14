---
template: implementation_plan
status: approved
date: 2025-11-27
title: Refinement Layer Stage 1: Investigation
directive_id: PLAN-REFINEMENT-S1
version: 1.0
---
# generated: 2025-11-27
# System Auto: last updated on: 2025-11-27

# Refinement Layer Stage 1: Investigation Findings

> **Navigation:** [Meta-Plan](refinement-layer-meta-plan.md) | [System Spec](../COGNITIVE_MEMORY_SYSTEM_SPEC.md)

## 1. Executive Summary

The investigation confirms a significant gap between the *process-heavy* content currently in the database (Critiques, Directives) and the *knowledge-rich* vision of the Refinement Layer. The current extraction captures "what happened" (Doxa) but fails to distill "what is true" (Episteme) or "how to do it" (Techne).

**Key Finding:** The database contains **19,706 Critiques** and **18,281 Directives**, but only **763 Concepts**. We are capturing the *noise of collaboration* rather than the *signal of knowledge*.

---

## 2. Spec Analysis (`COGNITIVE_MEMORY_SYSTEM_SPEC.md`)

-   **Taxonomy Gap:** The spec defines the *machinery* (tables, routing, metadata) but **does not define an epistemic taxonomy**.
-   **Metadata Support:** The `memory_metadata` table (lines 215-224) is flexible enough to store classification tags (`episteme`, `techne`, `doxa`) without schema changes.
-   **Relationships:** The `memory_relationships` table supports types like `derived_from` and `supersedes`, which are essential for linking Doxa (decisions) to Episteme (principles).
-   **Missing Layer:** There is no explicit "Refinement Service" in the Service Layer specifications, only "Ingestion" and "Retrieval".

---

## 3. Database Content Inventory

Analysis of `haios_memory.db` reveals a distribution heavily skewed towards process artifacts:

| Concept Type | Count | Category (Inferred) |
| :--- | :--- | :--- |
| **Critique** | 19,706 | **Doxa** (Opinion/Review) |
| **Directive** | 18,281 | **Doxa** (Instruction/Command) |
| **Proposal** | 11,121 | **Doxa** (Suggestion) |
| **Decision** | 3,221 | **Doxa** (Project Reality) |
| **Concept** | 763 | **Episteme/Techne** (Potential) |
| **AntiPattern** | 33 | **Techne** (Negative Knowledge) |

**Interpretation:**
-   **98%** of the current "Concepts" are actually **Doxa** (opinions, directives, critiques).
-   True **Episteme** (principles) and **Techne** (patterns) are buried or misclassified.
-   The "Refinement Layer" must act as a **filter and distiller**, promoting valid Doxa into Techne/Episteme and discarding the noise.

---

## 4. Taxonomy Framework

Based on the Meta-Plan's hints and standard philosophical frameworks, the proposed taxonomy for the Refinement Layer is:

### 1. Episteme (The "Why" / Truth)
-   **Definition:** Universal principles, invariants, theoretical knowledge.
-   **Examples:** "CAP Theorem", "Separation of Concerns", "Idempotency".
-   **Properties:** Context-independent, timeless, high reuse.

### 2. Techne (The "How" / Craft)
-   **Definition:** Practical skills, patterns, implementation guides, "know-how".
-   **Examples:** "Factory Pattern", "Prometheus Configuration", "Error Handling Strategy".
-   **Properties:** Context-dependent, pragmatic, actionable.

### 3. Doxa (The "What" / Opinion)
-   **Definition:** Project-specific decisions, constraints, beliefs, critiques.
-   **Examples:** "Use Gemini 2.5", "Max file size 1MB", "This code is messy".
-   **Properties:** Highly context-specific, subjective, transient.

---

## 5. Open Questions for Analysis (Stage 2)

1.  **Distillation Logic:** How do we algorithmically or heuristically promote a `Directive` (Doxa) into a `Techne` (Pattern)?
2.  **Schema Impact:** Do we need a new `knowledge_type` column, or is `memory_metadata` sufficient?
3.  **Workflow:** Should refinement be a separate "pass" over the database (batch job) or continuous?
4.  **Provenance:** How do we link a `Techne` back to the `Doxa` (ADRs/Directives) that justified it?

---

## 6. Handover Status

**Stage 1 Complete.**
Ready for **Stage 2: Analysis** to design the taxonomy application and refinement workflow.
