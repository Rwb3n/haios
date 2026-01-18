---
template: implementation_plan
status: complete
date: 2026-01-18
backlog_id: E2-301
title: Update S17 Modular Architecture Spec
author: Hephaestus
lifecycle_phase: plan
session: 203
version: '2.0'
generated: 2025-12-21
last_updated: '2026-01-18T11:59:51'
---
# Implementation Plan: Update S17 Modular Architecture Spec

@docs/README.md
@docs/epistemic_state.md
@.claude/haios/epochs/E2/architecture/S17-modular-architecture.md
@.claude/haios/modules/context_loader.py

---

<!-- TEMPLATE GOVERNANCE (v1.4) - Sections marked SKIPPED with rationale -->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | N/A | Pure documentation task, no code changes |
| Query prior work | DONE | INV-069 findings provide complete issue list |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

S17-modular-architecture.md will accurately reflect the current 9-module architecture, correct GroundedContext schema, and valid config paths after Epoch 2.2 evolution.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/haios/epochs/E2/architecture/S17-modular-architecture.md` |
| Lines affected | ~50 | Lines 14, 122-129, 134-139, 436-446 |
| New files to create | 0 | - |
| Tests to write | 0 | Documentation task |
| Dependencies | 0 | No code consumers |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Pure documentation |
| Risk of regression | None | No code changes |
| External dependencies | None | - |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Update S17.1 module count | 5 min | High |
| Update S17.3 GroundedContext | 10 min | High |
| Update S17.8 config ownership | 5 min | High |
| **Total** | 20 min | High |

---

## Current State vs Desired State

### Current State (S17 Stale)

**S17.1 Line 14:**
```
Purpose: Restructure INV-052 findings into 5 discrete modules
```

**S17.3 Lines 122-129 (GroundedContext):**
```
l0_north_star: str           # Mission, principles
l1_invariants: str           # Patterns, anti-patterns
l2_operational: dict         # Status, phase, milestone
l3_session: dict             # Checkpoint, work context
```

**S17.3 Lines 134-139 (Owned State):**
```
| `.claude/config/north-star.md` | L0 context (read-only) |
| `.claude/config/invariants.md` | L1 context (read-only) |
| `.claude/config/roadmap.md` | Strategic direction |
```

**Problem:** These specs don't match implementation reality.

### Desired State (Match Implementation)

**S17.1 Line 14:**
```
Purpose: Restructure INV-052 findings into 9 discrete modules (5 core + 4 satellites from E2-279)
```

**S17.3 Lines 122-129 (GroundedContext) - from context_loader.py:30-34:**
```
l0_telos: str           # WHY - Mission, Prime Directive
l1_principal: str       # WHO - Operator constraints
l2_intent: str          # WHAT - Goals, trade-offs
l3_requirements: str    # HOW - Principles, boundaries
l4_implementation: str  # WHAT to build - Architecture
```

**S17.3 Owned State - from actual manifesto location:**
```
| `.claude/haios/manifesto/L0-telos.md` | L0 WHY context |
| `.claude/haios/manifesto/L1-principal.md` | L1 WHO context |
| `.claude/haios/manifesto/L2-intent.md` | L2 WHAT context |
| `.claude/haios/manifesto/L3-requirements.md` | L3 HOW context |
| `.claude/haios/manifesto/L4-implementation.md` | L4 BUILD context |
```

**Result:** S17 matches actual implementation.

---

## Tests First (TDD)

**SKIPPED:** Pure documentation task, no code changes. Verification is manual reading.

---

## Detailed Design

**SKIPPED:** Pure documentation task. This section shows exact text changes, not code changes.

### Change 1: S17.1 Module Count (Line 6)

**Current:**
```markdown
Purpose: Restructure INV-052 findings into 5 discrete modules with explicit I/O contracts
```

**Changed:**
```markdown
Purpose: Restructure INV-052 findings into 9 discrete modules (5 core + 4 WorkEngine satellites from E2-279) with explicit I/O contracts
```

### Change 2: S17.1 Module Overview Diagram (Lines 14-15)

**Current:**
```markdown
Per ADR-040, HAIOS is decomposed into 5 black-box modules:
```

**Changed:**
```markdown
Per ADR-040, HAIOS is decomposed into 9 black-box modules (5 core modules + 4 WorkEngine satellites from E2-279 decomposition):

| Module | Type | Purpose |
|--------|------|---------|
| ContextLoader | Core | L0-L4 bootstrap |
| WorkEngine | Core | WORK.md CRUD |
| CycleRunner | Core | Phase execution |
| MemoryBridge | Core | MCP wrapper |
| GovernanceLayer | Core | Policy enforcement |
| CascadeEngine | Satellite | Completion cascade |
| PortalManager | Satellite | REFS.md management |
| SpawnTree | Satellite | Tree traversal |
| BackfillEngine | Satellite | Backlog backfill |
```

### Change 3: S17.3 GroundedContext Interface (Lines 122-129)

**Current:**
```
OUTPUT:
  GroundedContext:
    session_number: int
    prior_session: int | null
    l0_north_star: str           # Mission, principles
    l1_invariants: str           # Patterns, anti-patterns
    l2_operational: dict         # Status, phase, milestone
    l3_session: dict             # Checkpoint, work context
    strategies: list[Strategy]   # From memory query
    ready_work: list[WorkItem]   # From `just ready`
```

**Changed (matching context_loader.py:24-38):**
```
OUTPUT:
  GroundedContext:
    session_number: int
    prior_session: int | null
    l0_telos: str                # WHY - Mission, Prime Directive
    l1_principal: str            # WHO - Operator constraints
    l2_intent: str               # WHAT - Goals, trade-offs
    l3_requirements: str         # HOW - Principles, boundaries
    l4_implementation: str       # WHAT to build - Architecture
    checkpoint_summary: str      # Latest checkpoint content
    strategies: list[Strategy]   # From memory query
    ready_work: list[WorkItem]   # From `just ready`
```

### Change 4: S17.3 Owned State (Lines 134-139)

**Current:**
```markdown
| File | Description |
|------|-------------|
| `.claude/config/north-star.md` | L0 context (read-only) |
| `.claude/config/invariants.md` | L1 context (read-only) |
| `.claude/config/roadmap.md` | Strategic direction |
| `docs/checkpoints/*.md` | Session history (read for session number) |
```

**Changed (matching actual manifesto paths):**
```markdown
| File | Description |
|------|-------------|
| `.claude/haios/manifesto/L0-telos.md` | L0 WHY - Mission, Prime Directive (read-only) |
| `.claude/haios/manifesto/L1-principal.md` | L1 WHO - Operator constraints (read-only) |
| `.claude/haios/manifesto/L2-intent.md` | L2 WHAT - Goals, trade-offs (read-only) |
| `.claude/haios/manifesto/L3-requirements.md` | L3 HOW - Principles, boundaries (read-only) |
| `.claude/haios/manifesto/L4-implementation.md` | L4 BUILD - Architecture (read-only) |
| `.claude/haios-status.json` | Session number source |
| `docs/checkpoints/*.md` | Session history |
```

### Change 5: S17.8 Configuration Ownership (Lines 436-446)

**Current:**
```markdown
| Config File | Owning Module |
|-------------|---------------|
| north-star.md | ContextLoader |
| invariants.md | ContextLoader |
| roadmap.md | ContextLoader |
| governance-toggles.yaml | GovernanceLayer |
| hook-handlers.yaml | GovernanceLayer |
| gates.yaml | GovernanceLayer |
| node-bindings.yaml | GovernanceLayer |
| cycle-definitions.yaml | CycleRunner |
| thresholds.yaml | GovernanceLayer |
```

**Changed (matching haios.yaml consolidation):**
```markdown
| Config File | Owning Module | Notes |
|-------------|---------------|-------|
| `.claude/haios/manifesto/L0-L4-*.md` | ContextLoader | Manifesto corpus |
| `.claude/haios/config/haios.yaml` | GovernanceLayer | Toggles + thresholds |
| `.claude/haios/config/cycles.yaml` | CycleRunner | Node bindings |
| `.claude/haios/config/components.yaml` | GovernanceLayer | Registries |
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Keep 9-module count in diagram | Update diagram text, not ASCII art | ASCII art is effort-intensive; text annotation sufficient |
| Add module table | New table after line 15 | Clearer than updating complex ASCII diagram |
| L0-L4 naming | Match context_loader.py exactly | Implementation is ground truth |
| Config consolidation | Reference haios.yaml | Matches E2-246 config consolidation |

### Open Questions

**Q: Should we update the ASCII diagram (lines 16-65)?**

No - adding a table summary below the diagram is cleaner and the diagram's basic flow is still accurate. The satellite modules (CascadeEngine, etc.) are internal to WorkEngine and don't appear in the inter-module diagram.

---

## Open Decisions (MUST resolve before implementation)

**None.** All decisions resolved during INV-069 investigation.

---

## Implementation Steps

### Step 1: Update S17.1 Header and Module Overview
- [ ] Change line 6 from "5 discrete modules" to "9 discrete modules"
- [ ] Add module summary table after line 15

### Step 2: Update S17.3 GroundedContext Interface
- [ ] Replace lines 122-129 with L0-L4 naming from context_loader.py

### Step 3: Update S17.3 Owned State
- [ ] Replace lines 134-139 with actual manifesto paths

### Step 4: Update S17.8 Configuration Ownership
- [ ] Replace lines 436-446 with consolidated config file structure

### Step 5: Verification
- [ ] Read updated S17 and verify all changes applied
- [ ] Verify S17 matches context_loader.py implementation

---

## Verification

- [ ] S17.1 shows 9 modules
- [ ] S17.3 GroundedContext matches context_loader.py:24-38
- [ ] S17.3 Owned State references actual manifesto paths
- [ ] S17.8 Configuration matches haios.yaml consolidation

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| S17 consumers reference old naming | Low | Search for S17 references in other docs |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 203 | 2026-01-18 | - | In Progress | Plan created, ready for DO phase |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Update GroundedContext schema (lines 125-129) | [ ] | Read S17:122-129 |
| Update module count from 5 to 9 | [ ] | Read S17:6,14-15 |
| Update config file paths | [ ] | Read S17:134-139, 436-446 |
| Verify all interface definitions match | [ ] | Compare to context_loader.py |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `S17-modular-architecture.md` | Updated with all 5 changes | [ ] | |
| `context_loader.py` | Unchanged (ground truth) | [ ] | Verify only |

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| S17:6 says "9 discrete modules"? | [Yes/No] | |
| S17:122-129 uses l0_telos/l1_principal/etc? | [Yes/No] | |
| S17:134-139 references .claude/haios/manifesto/? | [Yes/No] | |
| S17:436-446 references haios.yaml? | [Yes/No] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] N/A - Tests pass (no code changes)
- [ ] **MUST:** All WORK.md deliverables verified complete
- [ ] N/A - Runtime consumer (documentation task)
- [ ] WHY captured (reasoning stored to memory)
- [ ] N/A - READMEs (no structural changes)
- [ ] Ground Truth Verification completed above

---

## References

- INV-069: Architecture File Consistency Audit (source investigation)
- @.claude/haios/modules/context_loader.py (implementation ground truth)
- @.claude/haios/manifesto/L4-implementation.md (9-module architecture)

---
