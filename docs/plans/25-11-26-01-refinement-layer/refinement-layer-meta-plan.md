---
template: implementation_plan
status: approved
date: 2025-11-26
title: Knowledge Refinement Layer Meta-Plan
directive_id: PLAN-REFINEMENT-001
version: 1.1
---
# generated: 2025-11-27
# System Auto: last updated on: 2025-11-27 22:34:30

# HAIOS Knowledge Refinement Layer - Meta-Plan

> **Navigation:** [Strategic Overview](@docs/epistemic_state.md) | [System Spec](@docs/COGNITIVE_MEMORY_SYSTEM_SPEC.md) | [ETL Package](@haios_etl/README.md)

## Grounding References

- System Vision: @docs/COGNITIVE_MEMORY_SYSTEM_SPEC.md
- Current State: @docs/epistemic_state.md
- Database Schema: @docs/specs/memory_db_schema_v2.sql
- ETL Implementation: @haios_etl/database.py
- Retrieval (stubbed): @haios_etl/retrieval.py
- Session Checkpoint: @docs/checkpoints/2025-11-26-SESSION-13b-ground-truth-and-meta-plan.md

---

## Mission

Build the refinement layer that transforms extracted Epoch 1 concepts into a validated, classified knowledge foundation - separating time-tested conventions from bastardized re-inventions and genuine novelty.

## 5-Stage Planning Process

Each stage produces a handover document. No implementation until Stage 5 is complete and approved.

### Stage 1: INVESTIGATION
**Goal:** Gather facts about what exists
**Output:** `docs/plans/refinement-layer-S1-investigation.md`

**Questions to answer:**
- What does @docs/COGNITIVE_MEMORY_SYSTEM_SPEC.md say about refinement/classification?
- What concept types currently exist in the database?
- What's the distribution of extracted concepts?
- Are there existing patterns in the ADRs that hint at taxonomy?
- What industry-standard knowledge classification approaches exist?

**Handover contents:**
- Inventory of existing spec coverage
- Database content summary
- External reference patterns identified
- Open questions for Analysis

---

### Stage 2: ANALYSIS
**Goal:** Interpret facts, identify gaps and opportunities
**Output:** `docs/plans/refinement-layer-S2-analysis.md`

**Questions to answer:**
- What's the gap between spec vision and current implementation?
- What taxonomy makes sense? (episteme/technos/doxa/primitive/foundation/principle)
- What's the minimum viable refinement schema?
- What workflows are needed for multi-pass validation?
- What are the risks of each approach?

**Handover contents:**
- Gap analysis (spec vs reality)
- Proposed taxonomy with rationale
- Workflow requirements
- Risk register
- Trade-offs identified

---

### Stage 3: PROPOSAL
**Goal:** Recommend specific approach
**Output:** `docs/plans/refinement-layer-S3-proposal.md`

**Deliverables:**
- Recommended schema changes
- Recommended pipeline architecture
- Recommended tooling (MCP tools, CLI commands)
- Phased rollout plan
- Success criteria

**Handover contents:**
- Single recommended approach (not alternatives)
- Clear rationale
- Dependencies and prerequisites
- Estimated scope

---

### Stage 4: VALIDATION
**Goal:** Stress-test assumptions before committing
**Output:** `docs/plans/refinement-layer-S4-validation.md`

**Activities:**
- Challenge proposal against edge cases
- Verify taxonomy works for sample concepts
- Check industry conventions aren't being re-invented
- Operator review and feedback
- Identify what could go wrong

**Handover contents:**
- Validation results
- Adjustments made
- Residual risks accepted
- Go/no-go recommendation

---

### Stage 5: SPECIFICATION
**Goal:** Detailed technical design ready for implementation
**Output:** `docs/specs/TRD-REFINEMENT-v1.md`

**Deliverables:**
- Database schema changes (SQL)
- API/tool specifications
- Test requirements
- Migration plan from current state
- Acceptance criteria

**Handover:** Ready for implementation phase

---

## Current Status

| Phase | Status | Notes |
|-------|--------|-------|
| Stage 1: Investigation | COMPLETE | @docs/plans/refinement-layer-S1-investigation.md |
| Stage 2: Analysis | COMPLETE | @docs/plans/refinement-layer-S2-analysis.md |
| Stage 3: Proposal | COMPLETE | @docs/plans/refinement-layer-S3-proposal.md |
| Stage 4: Validation | COMPLETE | @docs/plans/refinement-layer-S4-validation.md |
| Stage 5: Specification | COMPLETE | @docs/specs/TRD-REFINEMENT-v1.md |
| Implementation | COMPLETE | Migration 004, RefinementManager, CLI commands |

**Known Issues:**
- Latent bug in `_get_or_create_episteme()` - references `artifacts.content` which doesn't exist
- LLM integration is mocked - not connected to real API
- Phase 4 (ReasoningBank) still incomplete - experience learning non-functional

---

## Implementation Summary (Phase 8)

### Delivered Components
| Component | Location | Status |
|-----------|----------|--------|
| Migration 004 | `haios_etl/migrations/004_add_refinement_tables.sql` | Applied |
| RefinementManager | `haios_etl/refinement.py` | 134 lines |
| CLI Commands | `haios_etl/cli.py` | `refinement run/stats` |
| metadata table | `memory_metadata` | 9 rows verified |
| relationships table | `memory_relationships` | Created |

### Gap Summary (Updated 2025-11-27)
| Capability | Status |
|------------|--------|
| Concept classification metadata | IMPLEMENTED (memory_metadata table) |
| Concept relationships | IMPLEMENTED (memory_relationships table) |
| Epistemic taxonomy support | IMPLEMENTED (Greek Triad: Episteme/Techne/Doxa) |
| Concept versioning/history | NOT IMPLEMENTED |
| Multi-model provenance | NOT IMPLEMENTED |
| LLM classification | MOCKED - needs API integration |

---

## Document History

| Date | Change | Author |
|------|--------|--------|
| 2025-11-26 | Created meta-plan from Session 13b discussion | Hephaestus |
| 2025-11-27 | Stages 1-5 completed, implementation delivered | Implementer |
| 2025-11-27 | Updated status to reflect ground truth | Hephaestus |
