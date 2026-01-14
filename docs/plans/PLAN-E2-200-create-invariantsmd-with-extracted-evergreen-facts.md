---
template: implementation_plan
status: complete
date: 2025-12-26
backlog_id: E2-200
title: Create invariants.md with Extracted Evergreen Facts
author: Hephaestus
lifecycle_phase: plan
session: 121
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-26T11:17:33'
---
# Implementation Plan: Create invariants.md with Extracted Evergreen Facts

@docs/README.md
@docs/epistemic_state.md

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: New feature, no existing code to show current state"
     - "SKIPPED: Pure documentation task, no code changes"
     - "SKIPPED: Trivial fix, single line change doesn't warrant detailed design"

     This prevents silent section deletion and ensures conscious decisions.
-->

---

## Goal

Agent coldstart will have access to core philosophical invariants (Certainty Ratchet, Three Pillars, Governance Flywheel, etc.) extracted from buried archives into a dedicated L1 context file.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/config/README.md` |
| Lines of code affected | 0 | Pure documentation |
| New files to create | 1 | `.claude/config/invariants.md` |
| Tests to write | 0 | No code, N/A |
| Dependencies | 0 | No code imports |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single new file, no code integration |
| Risk of regression | Low | No existing code affected |
| External dependencies | Low | None |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Extract evergreen facts | 15 min | High |
| Format for agent consumption | 10 min | High |
| Update README | 5 min | High |
| **Total** | 30 min | High |

---

## Current State vs Desired State

### Current State

**Files in `.claude/config/`:**
- `README.md` - Configuration reference
- `template_versions.yaml` - Template versioning
- No invariants file exists

**Behavior:** Evergreen philosophical invariants (Certainty Ratchet, Three Pillars, etc.) are buried in:
- `_archive/test_phase2/Genesis_Architect_Notes.md`
- `deprecated_AGENT.md`
- `HAIOS-RAW/system/canon/ADR/ADR-OS-*.md`

**Result:** Agent lacks core system philosophy at coldstart. Rediscovers basic facts each session.

### Desired State

**Files in `.claude/config/`:**
- `README.md` - Updated to reference invariants.md
- `template_versions.yaml` - Unchanged
- `invariants.md` - NEW: Extracted evergreen facts

**Behavior:** Core philosophical invariants surfaced in dedicated L1 context file.

**Result:** Agent has immediate access to foundational system philosophy. E2-201 can then add to coldstart.

---

## Tests First (TDD)

**SKIPPED:** Pure documentation task (markdown file creation). No code, no pytest tests.

### Manual Verification Instead:
1. File exists: `.claude/config/invariants.md`
2. Contains required sections: Philosophy, Patterns, Rules
3. Contains key invariants: Certainty Ratchet, Three Pillars, Governance Flywheel
4. README updated to reference new file

---

## Detailed Design

### File Structure

**New File:** `.claude/config/invariants.md`

```markdown
# HAIOS Core Invariants (L1 Context)

> Evergreen philosophical and operational facts. Load at coldstart for agent grounding.
> Source: INV-037 extraction from Genesis_Architect_Notes.md, deprecated_AGENT.md, HAIOS-RAW ADRs

---

## Philosophy (WHY HAIOS Exists)

### Certainty Ratchet
HAIOS ensures project state moves only toward increasing certainty, clarity, and quality.

### Agency Engine
System telos is "sovereign creative agency" - reducing operator cognitive load while maintaining quality.

### SDD Framework (Specification-Driven Development)
70% effort on specification, 30% on implementation. Specification is the deliverable.

---

## Architectural Patterns (HOW HAIOS Works)

### Three Pillars
1. **Evidence-Based:** Decisions require evidence, not assumptions
2. **Durable Context:** Knowledge persists across sessions via memory
3. **Separation of Duties:** Operator (strategy) vs Agent (execution)

### Governance Flywheel
Principles → Enforcement → Feedback → Improvement (closed loop)
Every success and failure results in durable system improvement.

### Golden Thread
Traceability from request through analysis, initiative, and execution.

---

## Operational Rules (WHAT HAIOS Requires)

### Universal Idempotency
All mutable operations MUST be idempotent. Re-running is always safe.

### Structured Mistrust
Assume agents will fail in predictable ways. Design for graceful degradation.

### 5-Phase Operational Loop
ANALYZE → BLUEPRINT → CONSTRUCT → VALIDATE → IDLE

### Work Before Plan
Work file MUST exist before creating implementation plan.

---

## Key Recipes

| Recipe | Purpose |
|--------|---------|
| `just ready` | Show unblocked work items |
| `just node <id> <node>` | Move work item to DAG node |
| `just cascade <id> <status>` | Cascade status to dependents |
| `just update-status` | Refresh haios-status.json |

---

*Extracted: Session 121 from INV-037*
*Sources: Genesis_Architect_Notes.md, deprecated_AGENT.md, HAIOS-RAW ADRs 001-043*
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| File location | `.claude/config/invariants.md` | Alongside other config files; `.claude/` is agent-facing |
| Section structure | Philosophy/Patterns/Rules | Maps to WHY/HOW/WHAT hierarchy |
| Concise format | Bullet points, not prose | Agent consumption optimized for token efficiency |
| Include key recipes | Yes | Operational knowledge alongside philosophy |

---

## Implementation Steps

### Step 1: Create invariants.md
- [ ] Create `.claude/config/invariants.md` with content from Detailed Design
- [ ] Verify file contains Philosophy, Patterns, Rules sections

### Step 2: Update config README
- [ ] Update `.claude/config/README.md` to list invariants.md
- [ ] Add description of file purpose

### Step 3: Manual Verification
- [ ] Read file and verify all key invariants present
- [ ] Verify formatting is agent-friendly (concise, structured)

---

## Verification

- [ ] File exists: `.claude/config/invariants.md`
- [ ] Contains: Certainty Ratchet, Three Pillars, Governance Flywheel
- [ ] README updated: `.claude/config/README.md`

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Missing invariants | Low | Review against INV-037 H2 findings |
| Format too verbose | Low | Keep concise; iterate if needed |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/config/invariants.md` | Contains Philosophy, Patterns, Rules sections | [ ] | |
| `.claude/config/README.md` | Lists invariants.md with description | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Contains Certainty Ratchet? | [Yes/No] | |
| Contains Three Pillars? | [Yes/No] | |
| Contains Governance Flywheel? | [Yes/No] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass (N/A - pure docs)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** README updated in `.claude/config/`
- [ ] Ground Truth Verification completed above

---

## References

- INV-037: Context Level Architecture and Source Optimization
- E2-201: Update Coldstart to Load invariants.md (blocked by this)

---
