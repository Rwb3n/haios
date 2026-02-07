---
template: implementation_plan
status: complete
date: 2025-12-14
backlog_id: E2-076
title: "DAG Governance Architecture ADR"
author: Hephaestus
lifecycle_phase: plan
session: 75
spawned_by: INV-016
related: [E2-069, E2-037, E2-079, INV-011, INV-012]
children: [E2-076b, E2-076d, E2-076e, E2-078, E2-079]
absorbs: [E2-074]
enables: [E2-081, E2-082, E2-083, E2-084]
execution_layer: E2-080
version: "1.1"
---
# generated: 2025-12-14
# System Auto: last updated on: 2025-12-17 22:25:25
# Implementation Plan: DAG Governance Architecture ADR

@docs/README.md
@docs/epistemic_state.md
@docs/investigations/INVESTIGATION-INV-016-haios-operational-infrastructure-audit.md

---

## Goal

Formalize the Directed Acyclic Graph (DAG) architecture for HAIOS governance, where documents are nodes, dependencies are edges, and state changes cascade via heartbeat mechanisms.

---

## Current State vs Desired State

### Current State

**Structure:**
- Documents are files in directories
- Dependencies are prose references (`Related:`, `Spawned By:`)
- haios-status.json is a flat snapshot
- Hooks fire but don't cascade

**Behavior:** Manual tracking of relationships. Status updates require human intervention. Context loading is all-or-nothing.

**Result:** Complexity exceeds cognitive capacity. Items get lost. Dependencies are invisible.

### Desired State

**Structure:**
- Documents are **nodes** in a DAG
- Dependencies are **edges** (machine-traversable)
- haios-status represents **graph state**
- Hooks trigger **cascading updates**

**Behavior:** State changes propagate. Context loads progressively. Relationships are queryable.

**Result:** System self-awareness at scale. "What depends on X?" is answerable.

---

## Detailed Design

### Core Concepts

#### 1. DAG Structure (Memory: 50372, 71375)

```
NODES (Documents):
- Checkpoints, Plans, Investigations, ADRs, Backlog Items
- Each has frontmatter with: id, status, relationships

EDGES (Dependencies):
- spawned_by: parent -> child
- blocked_by: blocker -> blocked
- related: bidirectional reference
- milestone: item -> milestone
```

#### 2. Heartbeat Mechanism

When a node state changes (e.g., plan completes):
1. **Validate** - Check DoD criteria
2. **Update** - Change node status
3. **Cascade** - Notify dependent nodes (three types)
4. **Refresh** - Update haios-status graph state

```
Plan COMPLETE ->
  |
  +-- [UNBLOCK CASCADE] blocked_by: this-plan
  |     |-- Find items with blocked_by: this-plan
  |     +-- Surface: "E2-077 is now unblocked"
  |
  +-- [RELATED CASCADE] related: this-plan
  |     |-- Find items with related: this-plan
  |     +-- Surface: "Heads up: E2-069 may need review"
  |
  +-- [MILESTONE CASCADE] milestone: M2
  |     |-- Recalculate milestone progress
  |     +-- Surface: "M2-Governance: 75% -> 80%"
  |
  +-- [SUBSTANTIVE CHECK] docs referencing this-plan
  |     |-- Mechanical update? → Auto-update (status, dates)
  |     +-- Substantive update? → Spawn work item
  |
  +-- Store WHY to memory
```

#### 2b. Cascade Types

| Type | Trigger | Action | Example |
|------|---------|--------|---------|
| **Unblock** | `blocked_by` edge | Mark dependent as READY | E2-076e blocked by E2-076d → unblock |
| **Related** | `related` edge | Surface awareness message | E2-069 related to E2-076 → "may need review" |
| **Milestone** | `milestone` edge | Recalculate progress % | E2-076 in M2 → M2 progress updated |
| **Substantive** | Content reference | Spawn update work item | CLAUDE.md references E2-076 → E2-UPDATE-xxx |

#### 2c. Mechanical vs Substantive Updates

| Update Type | Characteristics | Action |
|-------------|-----------------|--------|
| **Mechanical** | Field changes, status, dates, counts | Auto-update via hook |
| **Substantive** | New sections, rewrites, semantic changes | Spawn work item |

**Detection heuristic:**
- Status field change → Mechanical
- Frontmatter field change → Mechanical
- Body content reference → Substantive (spawn work item)

#### 2d. Fork on Insight (Horizontal Spawning)

When an insight surfaces mid-lifecycle:

```
E2-076 DISCOVERY phase
    |
    💡 INSIGHT: "Need Vitals before memory"
    |
    +-- Agent flags insight
    |
    +-- /new-investigation or direct backlog entry
    |
    +-- E2-076d created with:
    |     spawned_by: E2-076
    |     related: [E2-076]
    |
    +-- E2-076 continues OR blocks on E2-076d
```

**Fork decision:**
- Independent insight → `related` only, parallel execution
- Blocking insight → `blocked_by` added, sequential execution

#### 3. Progressive Context Loading (Information Architecture)

| Level | Source | Content | Token Cost |
|-------|--------|---------|------------|
| L1: Vitals | UserPromptSubmit | Active: commands, skills, agents, MCPs, milestone>epic>item | ~50 |
| L2: Graph State | haios-status-slim.json | Node counts, edge counts, active nodes list | ~100 |
| L3: Active Detail | haios-status.json | Frontmatter + relationships of active nodes | ~500 |
| L4: Full Detail | On-demand Read | Complete document content | Variable |

#### 4. UserPromptSubmit Vitals Injection

Always inject at prompt time:
```
--- HAIOS Vitals ---
Milestone: M2-Governance (75% complete)
Active: E2-076, E2-069, INV-016
Commands: /new-*, /close, /validate
Skills: memory-agent, extract-content
Agents: schema-verifier
MCPs: haios-memory (13 tools), context7 (2 tools)
---
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Graph storage | Frontmatter + haios-status.json | No new database; leverage existing structures |
| Cascade trigger | Hooks (PostToolUse, ValidateTemplate) | Already wired, just need cascade logic |
| Progressive loading | Slim/Full split | Balances awareness vs token cost |
| Edge types | spawned_by, blocked_by, related, milestone | Covers 90% of relationships observed |

### HAIOS Song Mapping (from INV-016)

| Metaphor | Component | DAG Role |
|----------|-----------|----------|
| **Keys** | Commands | Entry nodes (start traversal) |
| **Chords** | Skills | Path patterns (multi-node operations) |
| **Strings** | Hooks | Edge validators (trigger on changes) |
| **Chains** | Workflows | Defined traversal paths |
| **Heartbeat** | Cascade mechanism | Propagates state through graph |

---

## Implementation Steps

### Step 0: Justfile Execution Layer (E2-080)
- **Backlog:** E2-080 (Justfile as Claude's Execution Toolkit)
- **Why First:** All subsequent steps use PowerShell scripts. Justfile wraps them into clean `just <recipe>` invocations.
- [ ] Install `just` command runner
- [ ] Create `justfile` at project root with core recipes:
  ```just
  # Governance
  validate file:             # wraps ValidateTemplate.ps1
  scaffold type id title:    # wraps ScaffoldTemplate.ps1
  cascade id status:         # wraps CascadeHook.ps1
  update-status:             # wraps UpdateHaiosStatus.ps1

  # ETL
  status:                    # python -m haios_etl.cli status
  synthesis:                 # python -m haios_etl.cli synthesis run
  ```
- [ ] Verify: `just --list` shows available recipes

**Pattern:** "Slash commands are prompts, just recipes are execution"

### Step 1: Write ADR-038 (DAG Governance Architecture)
- **Subplan:** `E2-076a` (to be created)
- [ ] Create ADR with `/new-adr 038 DAG-Governance-Architecture`
- [ ] Document: Context, Decision, Consequences
- [ ] Include: Node types, Edge types, Cascade rules, Progressive loading

### Step 2: Update Frontmatter Schema (E2-076b) - COMPLETE
- **Subplan:** `docs/plans/PLAN-E2-076b-frontmatter-schema.md`
- **Status:** COMPLETE (Session 79)
- [x] Add `spawned_by`, `blocked_by`, `related`, `milestone` to all template OptionalFields
- [x] Add `parent_plan` to implementation_plan for subplan linking
- [x] Update template files with edge field placeholders
- [x] Added hierarchy fields: `children`, `absorbs`, `enables`, `execution_layer`
- **Note:** ADR-038 skipped per Session 78 decision - edge semantics documented in E2-076 parent plan

### Step 3: Implement L1/L2 Progressive Context (E2-076d) - COMPLETE
- **Subplan:** `docs/plans/PLAN-E2-076d-vitals-injection.md`
- **Status:** COMPLETE (Session 80)
- [x] L1: Vitals block in UserPromptSubmit (~50 tokens)
- [x] L2: haios-status-slim.json (50 lines)
- [x] Disabled memory injection (replaced by vitals)
- [x] Updated /coldstart to reference slim file
- [x] Milestone progress with delta indicator working
- **Child E2-078:** Delta calculation deferred - vitals show progress % and source

### Step 3b: Progressive Static Context (E2-079)
- **Backlog:** E2-079 (CLAUDE.md De-bloat)
- [ ] Audit CLAUDE.md sections by usage frequency
- [ ] Split into Core (~150 lines) + Reference (on-demand)
- [ ] Create `.claude/REFS/` directory
- [ ] Mirrors L1→L4 philosophy for static files

### Step 4: Implement Cascade Hooks (E2-076e) - UNBLOCKED
- **Subplan:** `docs/plans/PLAN-E2-076e-cascade-hooks.md`
- **Blocked By:** ~~E2-076b~~ (COMPLETE), ~~E2-076d~~ (COMPLETE) - **NOW UNBLOCKED**
- [ ] Create CascadeHook.ps1 with cascade type handlers
- [ ] PostToolUse detects status: complete/accepted
- [ ] **Unblock cascade:** Find items with `blocked_by` → surface unblock message
- [ ] **Related cascade:** Find items with `related` → surface awareness message
- [ ] **Milestone cascade:** Recalculate milestone progress → surface delta
- [ ] **Substantive check:** Detect if spawning update work item needed
- [ ] Format cascade message with all effects

---

## Verification

- [ ] ADR-038 accepted
- [ ] Frontmatter schema updated
- [ ] Slim status file working
- [ ] Vitals injection visible
- [ ] Cascade tested (complete a plan, verify unblock)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Complexity creep | High | Implement incrementally; each step must work standalone |
| Performance (cascade loops) | Medium | DAG constraint prevents cycles; validate on edge creation |
| Token overhead (vitals) | Low | Keep vitals under 100 tokens; measure |
| Adoption friction | Medium | Make it automatic; hooks do the work |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 75 | 2025-12-14 | - | Draft | Plan created from INV-016 findings |
| 78 | 2025-12-16 | SESSION-78 | In Progress | E2-080 Justfile complete, Symphony architecture designed |
| 79 | 2025-12-16 | SESSION-79 | In Progress | E2-076b Frontmatter Schema complete |
| 80 | 2025-12-16 | SESSION-80 | In Progress | E2-076d Vitals Injection complete, E2-076e unblocked |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `docs/ADR/ADR-038-dag-governance-architecture.md` | ADR exists, status: accepted | [ ] | |
| `.claude/hooks/ValidateTemplate.ps1` | Recognizes spawned_by, blocked_by, milestone | [ ] | |
| `.claude/haios-status-slim.json` | Slim version exists, <100 lines | [ ] | |
| `.claude/hooks/UserPromptSubmit.ps1` | Vitals injection present | [ ] | |

**Verification Commands:**
```bash
# Check slim file size
wc -l .claude/haios-status-slim.json
# Expected: <100 lines

# Check vitals injection (look for "HAIOS Vitals" in hook output)
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| ADR-038 accepted? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] ADR-038 accepted
- [ ] WHY captured (reasoning stored to memory)
- [ ] Documentation current (CLAUDE.md, epistemic_state.md)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- **Memory:** Concepts 50372, 50388, 71375 (DAG architecture)
- **Investigations:** INV-016, INV-011, INV-012
- **Related Backlog:** E2-069, E2-074, E2-037
- **ADRs:** ADR-035 (RFC 2119), ADR-034 (Ontology)

---
