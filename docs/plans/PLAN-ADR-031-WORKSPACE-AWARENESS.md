---
template: implementation_plan
status: complete
date: 2025-12-07
backlog_id: PLAN-ADR-031-WORKSPACE-AWARENESS
title: "ADR-031 Workspace Awareness"
author: Hephaestus
lifecycle_phase: complete
version: "1.0"
completed_session: 47
---
# generated: 2025-12-07
# System Auto: last updated on: 2025-12-10 22:04:30
# Implementation Plan: ADR-031 Workspace Awareness

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Create ADR-031 to define **Workspace Awareness** - the ability for HAIOS to enumerate and query what documents exist in the workspace. This is the foundational governance layer that enables all subsequent governance (file lifecycle, work cycle, hook framework).

---

## Context

Session 44 identified a governance bootstrap problem:
- 57 legacy ADRs exist in HAIOS-RAW/system/canon/ADR/
- Only ADR-030 exists in docs/ADR/ (Epoch 2)
- No mechanism to enumerate or query documents
- haios-status.json has partial awareness (live_files) but not queryable
- /coldstart and /status don't surface inventory

---

## Problem Statement

HAIOS cannot answer "what exists?" without manual Glob/Grep searches. This prevents:
1. Knowing what ADRs already exist before creating new ones
2. Tracking file lifecycle across document types
3. Enabling work cycle governance
4. Building the hook framework properly

---

## Proposed Changes

### 1. Draft ADR-031: Workspace Awareness
- [ ] Review legacy ADRs for conflicts (esp. ADR-OS-033, 035, 041, 052)
- [ ] Define workspace index schema (JSON structure)
- [ ] Define enumeration mechanism (script or hook)
- [ ] Define query interface (/workspace command)
- [ ] Define migration path for legacy ADRs

### 2. ADR-031 Content Scope
- [ ] Workspace index schema (adrs, plans, checkpoints, handoffs, backlog)
- [ ] Indexing trigger (SessionStart hook or UpdateHaiosStatus)
- [ ] Storage location (haios-status.json extension or separate file)
- [ ] Query commands (/workspace, /workspace adrs, etc.)

### 3. After ADR Acceptance
- [ ] Implement workspace indexer
- [ ] Create /workspace command
- [ ] Integrate with /coldstart
- [ ] Update /status to show inventory counts

---

## Verification

- [ ] ADR-031 drafted and reviewed
- [ ] No conflicts with legacy ADRs
- [ ] Operator approval obtained
- [ ] Implementation plan created (separate from this ADR plan)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep | High | ADR defines schema only, implementation separate |
| Legacy conflict | Medium | Review HAIOS-RAW ADRs before drafting |
| Performance | Low | Index built incrementally, not full scan |
| Bootstrap paradox | Medium | Accept ADR-031 as foundational, retrofit later |

---

## Dependencies

This ADR enables:
- ADR-032: File Lifecycle Governance
- ADR-033: Work Cycle Governance (OADEV)
- E2-013: Hook Framework

---

## References

- Memory Concept 64601: Session 44 Governance Gap Analysis
- docs/ADR/ADR-030-document-taxonomy.md (existing Epoch 2 ADR)
- HAIOS-RAW/system/canon/ADR/ (57 legacy ADRs)

---
