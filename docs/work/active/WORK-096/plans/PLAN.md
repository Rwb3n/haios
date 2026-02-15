---
template: implementation_plan
status: complete
date: 2026-02-15
backlog_id: WORK-096
title: "Agent UX Test in DoD Validation"
author: Hephaestus
lifecycle_phase: plan
session: 380
version: "1.5"
generated: 2026-02-15
last_updated: 2026-02-15T23:45:37
---
# Implementation Plan: Agent UX Test in DoD Validation

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

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

DoD validation will optionally run the L3 Agent UX Test (4-question checklist) when closing work items that produce agent-facing components (skills, agents, commands, modules), surfacing usability gaps as warnings.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | SKILL.md, ADR-033, README.md |
| Lines of code affected | ~30 | Markdown additions only |
| New files to create | 0 | N/A |
| Tests to write | 0 | Docs-only change, manual verification |
| Dependencies | 0 | No code imports affected |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Agent reads skill markdown at runtime |
| Risk of regression | Low | Additive content, no existing behavior changed |
| External dependencies | Low | None |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| SKILL.md edit | 10 min | High |
| ADR-033 edit | 5 min | High |
| README update | 5 min | High |
| **Total** | 20 min | High |

---

## Current State vs Desired State

### Current State

dod-validation-cycle SKILL.md VALIDATE phase (lines 53-106) checks 4 mandatory ADR-033 criteria:
1. Tests pass
2. WHY captured (memory_refs)
3. Docs current
4. Traced files complete

Plus Ground Truth Verification (machine-checkable items from plan).

No mention of Agent UX Test. ADR-033 has no optional criteria section.

**Result:** New agent-facing components (skills, agents, commands) can ship without any usability review.

### Desired State

VALIDATE phase includes an optional "Agent UX Test" sub-section that triggers when `source_files` match component paths. ADR-033 documents optional criteria alongside mandatory criteria.

**Result:** DoD validation surfaces usability gaps as WARN (non-blocking) when closing work items that produce agent-facing components.

---

## Tests First (TDD)

**SKIPPED:** Pure documentation/markdown task. No Python code changes. Manual verification defined below.

### Manual Verification Steps

1. SKILL.md contains "Agent UX Test" section within VALIDATE phase
2. SKILL.md contains all 4 L3 questions verbatim
3. SKILL.md specifies trigger condition (source_files path matching)
4. SKILL.md specifies WARN severity (non-blocking)
5. ADR-033 contains "Optional DoD Criteria" section after mandatory DoD
6. ADR-033 references Agent UX Test with trigger and severity
7. README.md mentions optional criteria

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does.
     Future agents should be able to implement from this section alone.
     This section bridges the gap between tests (WHAT) and steps (HOW).

     MUST INCLUDE (per Session 88 enhancement):
     1. Actual current code that will be changed (copy from source)
     2. Exact diff/change to be made
     3. Function signature details with context
     4. Input/output examples with REAL data from the system

     PATTERN VERIFICATION (E2-255 Learning):
     IF creating a new module that imports from siblings:
       - MUST read at least one sibling module for import/error patterns
       - Verify: try/except conditional imports? sys.path manipulation? error types?
       - Use the SAME patterns as existing siblings (consistency > preference)

     IF modifying existing module:
       - Follow existing patterns in that file

     IF creating module with no siblings (new directory):
       - Document chosen patterns in Key Design Decisions with rationale -->

### Change 1: SKILL.md — Add Agent UX Test to VALIDATE phase

**File:** `.claude/skills/dod-validation-cycle/SKILL.md`
**Location:** After the DoD Criteria table (ending at line 61 `| Traced files complete |`), before the `**Actions:**` heading (line 63). Insert between these two anchors.

**Insert after the DoD Criteria table and before "**Actions:**":**

```markdown
**Optional: Agent UX Test (L3 Agent Usability Requirements)**

Triggered when work item `source_files` include paths matching:
- `.claude/skills/`
- `.claude/agents/`
- `.claude/commands/`
- `modules/`

When triggered, evaluate these 4 questions:

| # | Question | Check |
|---|----------|-------|
| 1 | Can an agent discover this? | Listed in `just --list`, haios-status-slim.json, or README |
| 2 | Can an agent verify success? | Ground Truth check, test, or validation command exists |
| 3 | Can an agent recover from failure? | Error messages are actionable, retry is safe |
| 4 | Does this respect token budget? | Output is sized appropriately, slim version available |

**Verdict:**
- PASS: All 4 questions answered YES (with evidence)
- WARN: 1-2 questions answered NO (flag for operator)
- N/A: source_files don't match trigger paths

This is a SHOULD criterion — failure warns but does not block closure.
```

### Change 2: ADR-033 — Add Optional DoD Criteria section

**File:** `docs/ADR/ADR-033-work-item-lifecycle.md`
**Location:** After the "WHY is most important" paragraph (line 170) that concludes section 3, before "### 4. Status Normalization" (line 172). Insert between these two anchors to keep section 3's narrative intact.

**Insert:**

```markdown
### 3b. Optional DoD Criteria

Beyond mandatory criteria, these optional criteria apply when trigger conditions are met:

| Criterion | Trigger | Verification | Severity |
|-----------|---------|--------------|----------|
| Agent UX Test | source_files match component paths (.claude/skills/, .claude/agents/, .claude/commands/, modules/) | 4-question L3 checklist (L3-requirements.md, "The Agent UX Test" section) | WARN (non-blocking) |

Optional criteria produce warnings in DoD validation output but do not block closure. They surface quality gaps for operator awareness.
```

### Change 3: README.md — Mention optional criteria

**File:** `.claude/skills/dod-validation-cycle/README.md`
**Location:** After the DoD Criteria table (line 35), before "## Integration"

**Insert:**

```markdown

### Optional Criteria

| Criterion | Trigger | Severity |
|-----------|---------|----------|
| Agent UX Test | source_files match component paths | WARN (non-blocking) |

See SKILL.md VALIDATE phase for the 4-question checklist.
```

### Behavior Logic

```
VALIDATE phase reads WORK.md source_files
    |
    +-> Any path matches .claude/skills/ | .claude/agents/ | .claude/commands/ | modules/ ?
          ├─ YES → Run 4-question Agent UX Test → PASS or WARN
          └─ NO  → Skip (N/A)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Severity level | WARN (non-blocking) | UX quality is aspirational, not a closure gate. Blocking would slow all component work. |
| Trigger mechanism | source_files path matching | Agent reads WORK.md frontmatter — no automation needed. Simple prefix match. |
| Checklist source | L3-requirements.md verbatim | Single source of truth. If L3 changes, update SKILL.md to match. |
| Placement in VALIDATE | After mandatory DoD, before Ground Truth | Logical flow: mandatory first, optional second, verification last. |

### Input/Output Examples

**Example 1 — Trigger (WORK-096 itself):**
```
source_files: [.claude/skills/dod-validation-cycle/]
Match: .claude/skills/ → TRIGGERED
Agent UX Test: 4 questions evaluated
Verdict: PASS or WARN
```

**Example 2 — No trigger (WORK-150, ADR work):**
```
source_files: [docs/ADR/ADR-046-plan-decomposition-traceability.md]
Match: none → N/A
Agent UX Test: skipped
```

### Edge Cases

| Case | Handling |
|------|----------|
| source_files empty | N/A — skip test |
| source_files has mixed paths (e.g., skill + docs) | Trigger — any component match is sufficient |
| Work item has no source_files field | N/A — skip test |

### Open Questions

None — design is fully specified.

---

## Open Decisions (MUST resolve before implementation)

No open decisions. All design choices resolved in Key Design Decisions above.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Add Agent UX Test to SKILL.md VALIDATE phase
- [ ] Insert optional Agent UX Test section after DoD Criteria table
- [ ] Include trigger conditions, 4-question checklist, verdict levels
- [ ] Verify: Manual check 1-4

### Step 2: Add Optional DoD Criteria section to ADR-033
- [ ] Insert section 3b after mandatory DoD section
- [ ] Include criterion table with trigger, verification, severity
- [ ] Verify: Manual check 5-6

### Step 3: Update dod-validation-cycle README.md
- [ ] Add Optional Criteria table referencing SKILL.md
- [ ] Verify: Manual check 7

### Step 4: Update WORK-096 source_files
- [ ] Set source_files to actual modified files

### Step 5: Consumer Verification
**SKIPPED:** Additive-only markdown changes. No renames, no migrations, no moved code.

---

## Verification

- [ ] Tests pass — N/A (docs-only, no pytest)
- [ ] **MUST:** README.md updated for dod-validation-cycle
- [ ] Manual verification steps 1-7 all pass

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| L3 checklist changes | Low | SKILL.md references L3 line numbers; update if L3 changes |
| Agent ignores optional section | Low | WARN severity means no harm if skipped |

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

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-096/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Optional Agent UX Test criterion added to dod-validation-cycle | [ ] | Grep SKILL.md for "Agent UX Test" |
| Trigger conditions defined for new components | [ ] | Grep SKILL.md for "source_files" |
| 4-question checklist in validation output | [ ] | Grep SKILL.md for "Can an agent discover" |
| ADR-033 updated with optional criteria section | [ ] | Grep ADR-033 for "Optional DoD Criteria" |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/dod-validation-cycle/SKILL.md` | Agent UX Test section in VALIDATE phase | [ ] | |
| `docs/ADR/ADR-033-work-item-lifecycle.md` | Section 3b Optional DoD Criteria exists | [ ] | |
| `.claude/skills/dod-validation-cycle/README.md` | Optional Criteria table present | [ ] | |

**Verification Commands:**
```bash
# Grep checks for all 4 deliverables
Grep(pattern="Agent UX Test", path=".claude/skills/dod-validation-cycle/SKILL.md")
Grep(pattern="Optional DoD Criteria", path="docs/ADR/ADR-033-work-item-lifecycle.md")
Grep(pattern="Can an agent discover", path=".claude/skills/dod-validation-cycle/SKILL.md")
Grep(pattern="WARN.*non-blocking", path="docs/ADR/ADR-033-work-item-lifecycle.md")
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| All 4 grep checks pass? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- @.claude/haios/manifesto/L3-requirements.md (Agent UX Test, lines 169-176)
- @.claude/skills/dod-validation-cycle/SKILL.md (target file)
- @docs/ADR/ADR-033-work-item-lifecycle.md (target file)
- @docs/work/active/WORK-096/WORK.md (work item)

---
