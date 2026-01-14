---
template: investigation
status: active
date: 2026-01-04
backlog_id: INV-056
title: Hook-to-Module Migration for Epoch 2.2 Completion
author: Hephaestus
session: 168
lifecycle_phase: hypothesize
spawned_by: null
related: []
memory_refs: []
version: '2.0'
generated: 2025-12-22
last_updated: '2026-01-04T19:21:26'
---
# Investigation: Hook-to-Module Migration for Epoch 2.2 Completion

@docs/README.md
@docs/epistemic_state.md

<!-- TEMPLATE GOVERNANCE (v2.0 - E2-144)

     INVESTIGATION CYCLE: HYPOTHESIZE -> EXPLORE -> CONCLUDE

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: Pure discovery, no design outputs needed"
     - "SKIPPED: Single hypothesis, no complex mapping required"
     - "SKIPPED: External research only, no codebase evidence"

     This prevents silent section deletion and ensures conscious decisions.

     SUBAGENT REQUIREMENT (L3):
     For EXPLORE phase, you MUST invoke investigation-agent subagent:
     Task(prompt='EXPLORE: {hypothesis}', subagent_type='investigation-agent')

     Rationale: Session 101 proved L2 ("RECOMMENDED") guidance is ignored ~20% of time.
     L3 enforcement ensures structured evidence gathering.
-->

---

## Discovery Protocol (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Query memory first | SHOULD | Search for prior investigations on topic before starting |
| Document hypotheses | SHOULD | State what you expect to find before exploring |
| Use investigation-agent | MUST | Delegate EXPLORE phase to subagent for structured evidence |
| Capture findings | MUST | Fill Findings section with evidence, not assumptions |

---

## Context

<!-- HYPOTHESIZE PHASE: Describe background before exploring -->

**Trigger:** Operator directive (Session 168): "no optionals. everything must become 2.2" - Epoch 2.2 requires Strangler Fig completion, not parallel paths.

**Problem Statement:** Hooks import from `.claude/lib/` directly instead of using Chariot modules, violating Epoch 2.2 Strangler Fig pattern where modules REPLACE implementations.

**Prior Observations:**
- All 5 Chariot modules built and tested (E2-240 through E2-255)
- Justfile recipes migrated to use cli.py -> modules (E2-250)
- Hooks still use lib/config.py, lib/node_cycle.py, lib/validate.py, lib/status.py, lib/error_capture.py
- Memory 80601: "Chariot modules marked complete but had ZERO runtime consumers...hooks still used old .claude/lib/ code paths"

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "hook migration module architecture strangler fig lib dependencies epoch 2.2 chariot"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 80601 | Chariot modules had zero runtime consumers, hooks used lib/ | Direct problem statement |
| 80530 | Strangler fig: module alongside existing, migrate incrementally | Pattern to follow |
| 80532 | Module exists but consumers not yet migrated | Current state |
| 76936 | E2-085 pattern migrated 4 hooks with 22 tests | Prior successful migration |
| 80640 | Hook migration deferred | Why gap exists |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] Found: INV-052 (full architecture), INV-053 (simplified 5-module design), E2-085 (PowerShell→Python hook migration)

---

## Objective

<!-- One clear question this investigation will answer -->

**What specific changes are needed to make hooks import from Chariot modules instead of `.claude/lib/`, completing Epoch 2.2 Strangler Fig migration?**

Output: Mapping of each hook's lib/ imports to module equivalents, plus spawned work items (E2-259+).

---

## Scope

### In Scope
- All 4 hook files: user_prompt_submit.py, pre_tool_use.py, post_tool_use.py, stop.py
- Each lib/ module imported by hooks
- Mapping to existing Chariot modules or identifying new module needs
- Design for hook→module import path

### Out of Scope
- Rewriting hooks (preserve behavior, just change imports)
- Performance optimization
- New hook functionality
- haios_etl/ migration (separate concern)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 4 | .claude/hooks/hooks/*.py |
| lib/ modules used | 5 | config, node_cycle, validate, status, error_capture |
| Chariot modules | 5 | GovernanceLayer, MemoryBridge, WorkEngine, ContextLoader, CycleRunner |
| Hypotheses to test | 3 | Listed below |
| Estimated complexity | Medium | Import rewiring, not rewrite |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | Most lib/ imports can map to existing Chariot modules | High | Read each lib/ file, identify equivalent in modules/ | 1st |
| **H2** | Some lib/ functions need to be added to modules (extend, not new module) | Med | Compare lib/ functions used by hooks vs module interfaces | 2nd |
| **H3** | A new module (StatusModule or ErrorCapture) may be needed for unmapped functions | Low | Identify any lib/ functions with no module home | 3rd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [ ] Inventory all lib/ imports in each hook file
2. [ ] Read each lib/ module to understand its functions
3. [ ] Read each Chariot module to understand its interface

### Phase 2: Hypothesis Testing
4. [ ] Test H1: Create mapping table (lib/ function → module equivalent)
5. [ ] Test H2: Identify functions hooks need that modules don't expose
6. [ ] Test H3: Identify lib/ functions with no natural module home

### Phase 3: Synthesis
7. [ ] Design import path architecture (hooks → modules)
8. [ ] Determine which modules need extension
9. [ ] Spawn implementation work items (E2-259+)

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Complete lib/ Import Mapping

| Hook | lib/ Import | Function Used | Module Equivalent | Gap? |
|------|-------------|---------------|-------------------|------|
| user_prompt_submit.py | `status` | `generate_slim_status()` | None | **YES** |
| pre_tool_use.py | `config.ConfigLoader` | `.toggles` access | GovernanceLayer (partial) | **YES** - toggles |
| pre_tool_use.py | `node_cycle` | `detect_node_exit_attempt()`, `check_exit_criteria()` | CycleRunner.check_phase_exit() | Partial |
| post_tool_use.py | `error_capture` | `is_actual_error()`, `store_error()` | None | **YES** |
| post_tool_use.py | `validate` | `validate_file()` | GovernanceLayer.validate_template() | **NO** |
| post_tool_use.py | `status` | `generate_slim_status()` | None | **YES** |
| post_tool_use.py | `node_cycle` | `build_scaffold_command()`, `check_doc_exists()` | GovernanceLayer.scaffold_template() | Partial |
| stop.py | subprocess | `reasoning_extraction.py` | MemoryBridge.store() | **YES** |

### Gap Summary

| Gap | lib/ Function | Module Target | Priority |
|-----|---------------|---------------|----------|
| Status generation | `status.generate_slim_status()` | ContextLoader | HIGH |
| Toggle access | `config.ConfigLoader.toggles` | GovernanceLayer | MED |
| Error capture | `error_capture.is_actual_error()` | MemoryBridge | MED |
| Reasoning extraction | `reasoning_extraction.py` | MemoryBridge | MED |
| Scaffold helpers | `node_cycle.build_scaffold_command()` | CycleRunner | LOW |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 80601 | Chariot modules had zero runtime consumers | H1 | Confirms gap exists |
| 80530 | Strangler fig: migrate incrementally | H1, H2 | Extend modules, not replace |
| 76936 | E2-085 migrated 4 hooks with 22 tests | H1 | Pattern to follow |

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **CONFIRMED** | 1 of 5 lib/ imports (validate) already maps to module; 2 more (node_cycle, config) have partial coverage | High |
| H2 | **CONFIRMED** | 4 gaps require extending existing modules (ContextLoader, GovernanceLayer, MemoryBridge, CycleRunner) | High |
| H3 | **REFUTED** | All gaps can map to existing modules - no new module needed | High |

### Detailed Findings

#### Finding 1: validate.py Already Migrated
**Evidence:** GovernanceLayer.validate_template() delegates to lib/validate.py (governance_layer.py:222-238)
**Analysis:** Pattern exists: module wraps lib/ function, hooks can import from module
**Implication:** Apply same delegation pattern to remaining lib/ functions

#### Finding 2: Status Generation is Biggest Gap
**Evidence:** 2 hooks use `status.generate_slim_status()` with no module equivalent
**Analysis:** Status generation is operational (runtime), fits ContextLoader scope
**Implication:** Add `generate_status()` and `write_status()` to ContextLoader

#### Finding 3: Error Capture Needs Home
**Evidence:** post_tool_use.py uses `is_actual_error()`, `store_error()` for tool failure handling
**Analysis:** Error classification + storage is memory-adjacent, fits MemoryBridge
**Implication:** Add `capture_error()` method to MemoryBridge

#### Finding 4: Toggles Access Missing
**Evidence:** pre_tool_use.py accesses `ConfigLoader.get().toggles` for block_powershell
**Analysis:** GovernanceLayer already loads config but doesn't expose toggles
**Implication:** Add `get_toggle(name)` method to GovernanceLayer

---

## Design Outputs

<!-- If investigation produces architectural designs, document them here
     SKIP this section if investigation is pure discovery with no design outputs -->

### Schema Design (if applicable)

```yaml
# [Name of schema]
field_name: type
  description: [What this field does]
```

### Mapping Table (if applicable)

| Source | Target | Relationship | Notes |
|--------|--------|--------------|-------|
| [A] | [B] | [How A relates to B] | |

### Mechanism Design (if applicable)

```
TRIGGER: [What initiates the mechanism]

ACTION:
    1. [Step 1]
    2. [Step 2]
    3. [Step 3]

OUTCOME: [What results from the mechanism]
```

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| [Decision point] | [What was chosen] | [Why this choice - most important part] |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

- [ ] **E2-259: ContextLoader Status Generation**
  - Description: Add `generate_status()`, `write_status()` methods to ContextLoader
  - Fixes: Gap 1 - status.py has no module equivalent
  - Spawned via: `/new-work E2-259 "ContextLoader Status Generation"`

- [ ] **E2-260: GovernanceLayer Toggle Access**
  - Description: Add `get_toggle(name)` method to GovernanceLayer
  - Fixes: Gap 2 - ConfigLoader.toggles not exposed via module
  - Spawned via: `/new-work E2-260 "GovernanceLayer Toggle Access"`

- [ ] **E2-261: MemoryBridge Error Capture**
  - Description: Add `capture_error()` method to MemoryBridge
  - Fixes: Gap 3 - error_capture.py has no module equivalent
  - Spawned via: `/new-work E2-261 "MemoryBridge Error Capture"`

- [ ] **E2-262: MemoryBridge Reasoning Extraction**
  - Description: Add `extract_learnings()` method to MemoryBridge
  - Fixes: Gap 4 - reasoning_extraction.py subprocess call
  - Spawned via: `/new-work E2-262 "MemoryBridge Reasoning Extraction"`

- [ ] **E2-263: CycleRunner Scaffold Helpers**
  - Description: Add `build_scaffold_command()`, `check_doc_exists()` to CycleRunner
  - Fixes: Gap 5 - node_cycle scaffold functions not in module
  - Spawned via: `/new-work E2-263 "CycleRunner Scaffold Helpers"`

- [ ] **E2-264: Hook Import Migration**
  - Description: Rewrite hooks to import from modules instead of lib/
  - Fixes: Final step - completes Epoch 2.2 Strangler Fig
  - Blocked by: E2-259 through E2-263
  - Spawned via: `/new-work E2-264 "Hook Import Migration"`

### Future (Requires more work first)

None - all work can proceed immediately with E2-259-263 in parallel, then E2-264

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 168 | 2026-01-04 | HYPOTHESIZE | Started | Initial context and hypotheses |
| - | - | - | - | No additional sessions yet |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-HN have verdict | [ ] | |
| Evidence has sources | All findings have file:line or concept ID | [ ] | |
| Spawned items created | Items exist in backlog or via /new-* | [ ] | |
| Memory stored | ingester_ingest called, memory_refs populated | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | [Yes/No] | |
| Are all evidence sources cited with file:line or concept ID? | [Yes/No] | |
| Were all hypotheses tested with documented verdicts? | [Yes/No] | |
| Are spawned items created (not just listed)? | [Yes/No] | |
| Is memory_refs populated in frontmatter? | [Yes/No] | |

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete ALL items before /close -->

### Required (MUST complete)
- [ ] **Findings synthesized** - Answer to objective documented in Findings section
- [ ] **Evidence sourced** - All findings have file:line or concept ID citations
- [ ] **Hypotheses resolved** - All hypotheses have Confirmed/Refuted/Inconclusive verdict
- [ ] **Spawned items created** - Via /new-* commands with `spawned_by` field (or rationale if none)
- [ ] **Memory stored** - `ingester_ingest` called with findings summary
- [ ] **memory_refs populated** - Frontmatter updated with concept IDs
- [ ] **lifecycle_phase updated** - Set to `conclude`
- [ ] **Ground Truth Verification complete** - All items checked above

### Optional
- [ ] Design outputs documented (if applicable)
- [ ] Session progress updated (if multi-session)

---

## References

- [Spawned by: Session/Investigation/Work item that triggered this]
- [Related investigation 1]
- [Related ADR or spec]

---
