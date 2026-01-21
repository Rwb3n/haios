---
template: architecture_decision_record
status: accepted
date: 2026-01-21
adr_id: ADR-044
title: L4 Stateless Principle
author: Hephaestus
session: 222
lifecycle_phase: decide
decision: accepted
spawned_by: WORK-005
memory_refs: []
version: '1.0'
generated: 2026-01-21
last_updated: '2026-01-21T21:42:20'
---
# ADR-044: L4 Stateless Principle

@docs/README.md
@docs/epistemic_state.md

> **Status:** Accepted
> **Date:** 2026-01-21
> **Decision:** L4 files MUST NOT contain temporal state

---

## Context

L4-implementation.md grew to 650+ lines mixing:
- Stable content (principles, module specs, requirements)
- Volatile content (current epoch, active arcs, what's complete)

Every epoch graduation or arc completion caused drift. The file became a changelog rather than a requirements spec.

Session 222 observation: the L4/ directory structure (project_requirements.md, agent_user_requirements.md, technical_requirements.md) remained stable because it describes *capabilities*, not *status*.

---

## Decision Drivers

- L4-implementation.md drifts every epoch graduation
- "Current Epoch: 2.2" became stale when we moved to E2.3
- "Active Arcs" section listed arcs that no longer exist
- Requirements (what system must do) are stable; status (what's done) is volatile

---

## Considered Options

### Option A: Delete L4-implementation.md
**Description:** Remove the file entirely, rely on L4/ directory.

**Pros:**
- No more drift
- Single source of truth in L4/

**Cons:**
- Loses module specs, Chariot architecture, recovery patterns
- L4/ directory doesn't have that detail

### Option B: L4 Stateless Principle
**Description:** Keep L4 files but enforce no temporal state. Status belongs in EPOCH.md and ARC.md.

**Pros:**
- Preserves valuable specs (Module-First, Chariot, recovery)
- Requirements stay stable
- Status tracked where it belongs (epoch/arc files)

**Cons:**
- Must refactor L4-implementation.md to extract status content
- Two places to look (L4 for spec, EPOCH for status)

---

## Decision

**Option B: L4 files MUST NOT contain temporal state.**

| Content Type | Belongs In | Example |
|--------------|------------|---------|
| Principles | L4 (or L3) | Module-First, Content Injection |
| Requirements | L4 | "must allow Builder to load work item" |
| Architecture specs | L4 or architecture/ | Chariot modules, function signatures |
| Current epoch | EPOCH.md | "E2.3 - The Pipeline" |
| Active arcs | EPOCH.md / ARC.md | "Configuration (CH-002, CH-003 complete)" |
| What's built/not built | EPOCH.md or ARC.md | Status tables |

---

## Consequences

**Positive:**
- L4 files remain stable across epoch boundaries
- Epoch/arc files own status (single source of truth)
- Less drift, fewer stale sections
- Requirements stay requirements

**Negative:**
- Must refactor L4-implementation.md to extract status content
- Two places to look (L4 for spec, EPOCH for status)

**Neutral:**
- L4/ directory structure already follows this pattern

---

## Implementation

- [ ] Extract "Current Epoch" and "Active Arcs" sections from L4-implementation.md
- [ ] Extract "What's Built vs Needed" tables to EPOCH.md or technical_requirements.md
- [ ] Keep module specs, principles, recovery patterns in L4-implementation.md
- [ ] Update technical_requirements.md with current component status

---

## References

- Session 222 discussion
- L4-implementation.md (the file that drifted)
- L4/ directory (the structure that didn't)
- EPOCH.md (where status belongs)
