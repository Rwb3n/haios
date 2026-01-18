# generated: 2026-01-18
# System Auto: last updated on: 2026-01-18T21:46:09
# E2 → E2.3 Migration Manifest

**Session:** 208
**Work Item:** WORK-002
**Date:** 2026-01-18

---

## Purpose

This manifest documents all triage decisions for E2 artifacts migrating to E2.3 (The Pipeline). Each decision includes rationale aligned with E2.3's mission: build a doc-to-product pipeline.

**Triage Categories:**
| Category | Meaning | Action |
|----------|---------|--------|
| **Pipeline-relevant** | Supports doc-to-product pipeline directly | Transfer concept/principles to E2.3 |
| **Reusable-infra** | Generic infrastructure usable in any project | Keep in place, reference from E2.3 |
| **HAIOS-specific** | PM infrastructure for HAIOS development | Archive (remains in E2, not transferred) |
| **Obsolete** | Completed or superseded | Dismiss (no further action) |

---

## Arc Triage (6 arcs)

| Arc | Theme | Disposition | Rationale |
|-----|-------|-------------|-----------|
| **chariot** | Module Architecture (9 modules) | Transfer principles | Modules ARE pipeline agents. Module boundaries, interfaces, breath mapping transfer to pipeline stages. E2 work items are HAIOS-specific. |
| **breath** | Pressure Dynamics (S20) | Transfer S20 | Inhale/exhale pattern IS the pipeline pattern - corpus loading (inhale) → processing → output (exhale). FOUNDATIONAL. |
| **form** | Skill Decomposition | Archive | Skills are HAIOS implementation details. "Smaller containers" principle transfers, but E2-283/284/285 work is HAIOS-specific. |
| **ground** | Context Loading | Transfer concept | Context loading = corpus loading. Ground-cycle pattern, portal system, checkpoint-as-manifest directly map to pipeline's corpus loader. |
| **tongue** | Cognitive Notation | Archive | RFC 2119 and operators are notation for HAIOS skills. Not relevant to generic doc-to-product pipeline. |
| **workinfra** | Work Infrastructure | Archive | WorkEngine, portals implemented. Structure transfers to universal work items, but E2-specific wiring is complete. |

**Summary:** 3 transfer (chariot, breath, ground), 3 archive (form, tongue, workinfra)

---

## Architecture Doc Classification (16 docs)

| Doc | Content | Classification | Rationale |
|-----|---------|----------------|-----------|
| **S2** | Lifecycle diagrams | Reusable-infra | Generic session/work lifecycles applicable anywhere |
| **S2C** | Work item directory | Reusable-infra | Portal system is generic reference pattern |
| **S10** | Skills taxonomy | HAIOS-specific | Skill types for HAIOS cycles, not pipeline |
| **S12** | Invocation paradigm | HAIOS-specific | 7-layer stack for HAIOS, not pipeline |
| **S14** | Bootstrap architecture (L0-L4) | Reusable-infra | Context loading patterns apply to any corpus |
| **S15** | Information architecture | Reusable-infra | Token budget patterns are LLM-generic |
| **S17** | Modular architecture | Pipeline-relevant | 9 modules = pipeline agent architecture |
| **S19** | Skill/work unification | HAIOS-specific | HAIOS category routing, not pipeline |
| **S20** | Pressure dynamics | Pipeline-relevant | FOUNDATIONAL - inhale/exhale is pipeline rhythm |
| **S21** | Cognitive notation | HAIOS-specific | RFC 2119 for HAIOS skills |
| **S22** | Skill patterns | Pipeline-relevant | Composable patterns (zoom, scaffold) transfer |
| **S23** | Files as context | Pipeline-relevant | Context architecture for any agent system |
| **S24** | Staging pattern | Pipeline-relevant | Pipeline staging (draft→live) |
| **S25** | SDK path to autonomy | Pipeline-relevant | Epoch 4 architecture (SDK harness) |
| **S26-skill-recipe** | Skill/recipe binding | HAIOS-specific | HAIOS implementation binding |
| **S26-pipeline** | Pipeline architecture | Pipeline-relevant | FOUNDATIONAL - defines what HAIOS is |

**Summary:**
- **Pipeline-relevant:** S17, S20, S22, S23, S24, S25, S26-pipeline (7 docs)
- **Reusable-infra:** S2, S2C, S14, S15 (4 docs)
- **HAIOS-specific:** S10, S12, S19, S21, S26-skill-recipe (5 docs)

---

## Work Item Triage (59 items)

### Keep Active (2 items)

| ID | Title | Rationale |
|----|-------|-----------|
| **WORK-001** | Universal Work Item Structure | E2.3 WorkUniversal arc - actively defining universal schema |
| **WORK-002** | E2.3 Triage | Current work item (this manifest) |

### Transfer - Pipeline Relevant (14 items)

These items contain concepts/patterns valuable for the pipeline. They should be reviewed when building pipeline stages.

| ID | Title | Rationale |
|----|-------|-----------|
| E2-072 | Critique Subagent | Validation agent concept for pipeline VALIDATE stage |
| E2-179 | Scaffold Recipe Optional Args | Generic scaffolding pattern |
| E2-235 | Earlier Context Warning | Generic session management |
| E2-236 | Orphan Session Detection | Generic session recovery |
| E2-249 | Agent UX Test in DoD | Generic DoD pattern for agents |
| E2-293 | set-queue Recipe | Generic queue infrastructure |
| INV-017 | Observability Gap | Generic observability patterns |
| INV-019 | Requirements Synthesis | Pipeline PLAN stage - extracting requirements! |
| INV-021 | Work Item Taxonomy | Universal work items - direct E2.3 relevance |
| INV-041 | Path Constants Architecture | Generic path management pattern |
| INV-066 | Plan Decomposition Trace | Generic traceability pattern |
| INV-068 | Cycle Delegation Architecture | Subagent execution pattern for pipeline stages |
| TD-001 | TOON Serializer | Generic serialization for token efficiency |
| TD-002 | Validation Agent Prototype | Pipeline VALIDATE stage prototype! |

### Archive - HAIOS-Specific (28 items)

These items are HAIOS development PM overhead. They remain in docs/work/active but are not transferred to E2.3 work.

| ID | Title | Rationale |
|----|-------|-----------|
| E2-017 | Concept Embedding Completion | Memory system internal |
| E2-018 | Entity Embedding Generation | Memory system internal |
| E2-019 | Concept Type Normalization | Memory system internal |
| E2-028 | Greek Triad Classification Gap | Memory classification |
| E2-087 | Plan Forward-Maintenance | HAIOS PM automation |
| E2-106 | FORESIGHT Preparation | Epoch 3 scope, not E2.3 |
| E2-124 | Synthesis Safety Measures | Memory system internal |
| E2-127 | Bidirectional Doc Automation | HAIOS doc system |
| E2-139 | Insight Crystallization Trigger | Memory system internal |
| E2-161 | Auto-link Documents | HAIOS PM linking |
| E2-164 | Coldstart L1 Context Review | HAIOS coldstart specific |
| E2-213 | Investigation Subtype Field | HAIOS work types |
| E2-214 | Report Subtype Field | HAIOS work types |
| E2-231 | Add validate-refs Recipe | HAIOS refs validation |
| E2-237 | Cycle Definitions Config | HAIOS cycle config |
| E2-289 | Hierarchy Rename | HAIOS naming convention |
| E2-294 | Wire impl/inv cycles | HAIOS cycle wiring |
| E2-295 | Wire survey/close cycles | HAIOS cycle wiring |
| INV-014 | Memory Context Injection | Memory system internal |
| INV-015 | Retrieval Algorithm | Memory system internal |
| INV-016 | HAIOS Operational Audit | HAIOS-specific audit |
| INV-023 | ReasoningBank Feedback | Memory system internal |
| INV-045 | Memory Retrieval UX | Memory system internal |
| INV-048 | Investigation Spawn Gate | HAIOS investigations |
| INV-051 | Skill Chain Pausing | HAIOS skill behavior |
| INV-054 | Validation Cycle Fitness | HAIOS validation cycle |
| INV-064 | Work Hierarchy Rename | HAIOS naming |
| TD-003 | Multi-Index Architecture | Memory system internal |

### Dismiss - Complete/Invalid (15 items)

These items are already complete or invalid. No further action needed.

| ID | Title | Status | Rationale |
|----|-------|--------|-----------|
| E2-234 | Auto Session-Start | complete | Work done |
| E2-279 | WorkEngine Decomposition | complete | Work done |
| E2-291 | Wire Queue into Survey | complete | Work done |
| E2-292 | Wire set-cycle Recipes | deferred | Superseded by E2-293/294/295 |
| E2-296 | Observation Triage Batch | complete | Work done |
| E2-298 | Consumer Migration | complete | Work done |
| E2-299 | WORK.md Typo Fix | complete | Work done |
| E2-300 | ContextLoader Spec Align | invalid | Invalid work item |
| E2-301 | Update S17 Spec | complete | Work done |
| E2-302 | Update S2 Lifecycle | complete | Work done |
| E2-303 | Update S2 Config Diagram | complete | Work done |
| INV-065 | Session State Cascade | complete | Work done |
| INV-067 | Observation Backlog Verify | complete | Work done |
| INV-069 | Architecture File Audit | complete | Work done |
| INV-070 | Queue Ready Filter Bug | complete | Work done |

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Keep active | 2 |
| Transfer (pipeline-relevant) | 14 |
| Archive (HAIOS-specific) | 28 |
| Dismiss (complete/invalid) | 15 |
| **Total** | 59 |

---

## Queue Cleanup Instructions

Remove the following from `just queue default`:

1. **All "Dismiss" items** - complete or invalid, no longer relevant
2. **All "Archive" items** - HAIOS-specific, not pipeline work

Keep in queue:
1. **WORK-001** - Universal Work Item Structure
2. **WORK-002** - E2.3 Triage (current)
3. **Transfer items** - May be relevant for pipeline stages (review individually)

---

## References

- @.claude/haios/epochs/E2_3/EPOCH.md (E2.3 mission)
- @.claude/haios/epochs/E2/EPOCH.md (E2 source)
- @.claude/haios/epochs/E2_3/arcs/migration/ARC.md (Migration arc)
- @docs/work/active/WORK-002/plans/PLAN.md (Triage plan)

---

*Generated by Session 208, WORK-002 implementation*
