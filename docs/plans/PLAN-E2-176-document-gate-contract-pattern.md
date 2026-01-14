---
template: implementation_plan
status: complete
date: 2025-12-25
backlog_id: E2-176
title: Document Gate Contract Pattern
author: Hephaestus
lifecycle_phase: plan
session: 116
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-25T14:38:27'
---
# Implementation Plan: Document Gate Contract Pattern

@docs/README.md
@docs/epistemic_state.md

---

## Goal

The Gate Contract Pattern (Entry + Guardrails + Exit) will be formally documented in the skills README, providing clear guidance for authoring cycle skills.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/skills/README.md` |
| Lines to add | ~30 | Gate Contract section |
| New files to create | 0 | N/A |
| Tests to write | 0 | Documentation only |
| Dependencies | 0 | Self-contained |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Documentation only |
| Risk of regression | Low | Additive content |
| External dependencies | Low | None |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Add Gate Contract section | 10 min | High |
| **Total** | 10 min | |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/skills/README.md (lines 19-30)

## Skill Types (INV-033)

**Cycle Skills:** Multi-phase workflows with gate contracts (entry conditions, guardrails, exit criteria)
- `implementation-cycle`
- `investigation-cycle`
- `work-creation-cycle`

**Utility Skills:** Single-purpose recipe cards
- `audit`
- etc.
```

**Behavior:** Mentions "gate contracts" but doesn't define the pattern.

**Result:** Authors don't know how to structure cycle skills.

### Desired State

```markdown
## Gate Contract Pattern (INV-033)

Each phase in a Cycle Skill SHOULD define:

### Entry Conditions
- Prerequisites that must be true to enter the phase
- File existence checks, status checks, prior phase completion

### Guardrails (Runtime)
- **MUST rules:** Absolute requirements (L3/L4 mechanical enforcement)
- **SHOULD rules:** Strong recommendations (L2 prompt-based)

### Exit Criteria
- Checklist items that must be satisfied before phase transition
- Memory integration points (query at start, store at end)
- Command invocations (/close, /validate)

### Example (implementation-cycle PLAN phase)

**Entry Conditions:**
- Plan file exists at `docs/plans/PLAN-{backlog_id}-*.md`
- Plan has filled-in sections (not template placeholders)
- Status is not `draft` (or fill in design first)

**Guardrails:**
- None for PLAN phase (design is flexible)

**Exit Criteria:**
- [ ] Plan file exists with complete design
- [ ] Tests defined in "Tests First" section
- [ ] Current/Desired state documented
```

**Behavior:** Full pattern documented with example.

**Result:** Authors can structure new cycle skills correctly.

---

## Tests First (TDD)

**SKIPPED:** Pure documentation task, no executable code to test.

---

## Detailed Design

### Exact Content to Add

**File:** `.claude/skills/README.md`
**Location:** After "Skill Types (INV-033)" section (after line 30)

**Content to insert:**

```markdown
## Gate Contract Pattern (INV-033)

Each phase in a Cycle Skill SHOULD define three components:

### 1. Entry Conditions
Prerequisites that must be true to enter the phase:
- File existence checks (plan/investigation file exists)
- Status checks (not draft, is active)
- Prior phase completion

### 2. Guardrails (Runtime Constraints)
Rules enforced during phase execution:
- **MUST rules:** Absolute requirements (e.g., "Write tests first")
- **SHOULD rules:** Strong recommendations (e.g., "One change at a time")

Enforcement levels:
- L3/L4: Mechanical (hooks, scripts)
- L2: Prompt-based (skill instructions)

### 3. Exit Criteria
Conditions that must be satisfied before phase transition:
- Checklist items (tests pass, docs updated)
- Memory integration (query at start, store at end)
- Command invocations (/close, /validate)

### Example: implementation-cycle DO Phase

**Entry:** PLAN phase exit criteria met

**Guardrails:**
- MUST write tests before implementation code
- SHOULD create file manifest before writing
- SHOULD pause for confirmation if >3 files

**Exit:**
- [ ] Tests written BEFORE implementation
- [ ] File manifest complete and followed
- [ ] Implementation matches Detailed Design
```

---

## Implementation Steps

### Step 1: Add Gate Contract Section
- [ ] Edit `.claude/skills/README.md`
- [ ] Insert Gate Contract Pattern section after Skill Types
- [ ] Include Entry/Guardrails/Exit definitions and example

### Step 2: Verify Content
- [ ] Read back the file to confirm insertion
- [ ] Check formatting is correct

---

## Verification

- [ ] Gate Contract Pattern section exists in README
- [ ] Pattern includes three components (Entry, Guardrails, Exit)
- [ ] Example provided

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/README.md` | Contains "## Gate Contract Pattern" section | [ ] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Gate Contract section added
- [ ] WHY captured (reasoning stored to memory)
- [ ] Ground Truth Verification complete

---

## References

- INV-033: Skill as Node Entry Gate Formalization
- Memory 78899, 78918: Gate Contract specification

---
