---
template: implementation_plan
status: complete
date: 2025-12-25
backlog_id: E2-182
title: plan-authoring-cycle skill
author: Hephaestus
lifecycle_phase: plan
session: 117
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-25T17:26:54'
---
# Implementation Plan: plan-authoring-cycle skill

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

After this plan is complete, the plan-authoring-cycle skill will guide agents through populating implementation plan sections (Goal, Current/Desired State, Tests, Design) after scaffolding, ensuring plans are complete before entering the DO phase.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/skills/README.md` |
| Lines of code affected | ~10 | Add skill to list |
| New files to create | 2 | `.claude/skills/plan-authoring-cycle/SKILL.md`, `README.md` |
| Tests to write | 0 | Skill is markdown/prompt, verification is runtime discovery |
| Dependencies | 0 | No code dependencies |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Standalone skill, optional for implementation-cycle |
| Risk of regression | Low | New skill, no existing behavior to break |
| External dependencies | Low | None |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Create SKILL.md | 20 min | High |
| Update READMEs | 5 min | High |
| Verify runtime | 5 min | High |
| **Total** | 30 min | |

---

## Current State vs Desired State

### Current State

```markdown
# implementation-cycle PLAN phase - Current behavior
1. Read the plan file
2. Verify plan has filled-in sections (not template placeholders)
3. Check status: draft -> if so, fill in design first
# Agent fills in manually with no structured guidance
```

**Behavior:** implementation-cycle's PLAN phase detects empty plans but provides no structured workflow for populating them. Agent fills in ad-hoc.

**Result:** Inconsistent plan quality - some sections skipped, effort estimation guessed, design incomplete.

### Desired State

```markdown
# plan-authoring-cycle - Target behavior
1. ANALYZE: Read plan, identify empty sections
2. AUTHOR: Guide through each section systematically
3. VALIDATE: Verify all required sections complete
# Optional skill that can be invoked when plan needs population
```

**Behavior:** plan-authoring-cycle provides structured ANALYZE→AUTHOR→VALIDATE workflow to populate plan sections.

**Result:** Consistent plan quality with complete sections.

---

## Tests First (TDD)

**SKIPPED:** Skill is markdown prompt injection, not Python code. Verification is runtime discovery.

### Verification Criteria (replaces pytest)

1. **Skill file exists:** `.claude/skills/plan-authoring-cycle/SKILL.md` file present
2. **Frontmatter valid:** Has `name`, `description`, `generated`, `last_updated` fields
3. **Runtime discovery:** Skill appears in `haios-status-slim.json` under `infrastructure.skills`

```bash
# Verification commands
just update-status-slim
python -c "import json; d=json.load(open('.claude/haios-status-slim.json')); print('plan-authoring-cycle' in d['infrastructure']['skills'])"
# Expected: True
```

---

## Detailed Design

### Skill File Structure

**File:** `.claude/skills/plan-authoring-cycle/SKILL.md`

```markdown
---
name: plan-authoring-cycle
description: HAIOS Plan Authoring Cycle for structured plan population. Use when
  filling in implementation plan sections. Guides ANALYZE->AUTHOR->VALIDATE workflow.
generated: 2025-12-25
last_updated: 2025-12-25
---
# Plan Authoring Cycle

This skill defines the ANALYZE-AUTHOR-VALIDATE cycle for populating implementation plan
sections after scaffolding. It ensures plans have complete Goal, Design, and Tests
sections before entering the DO phase.

## When to Use

**Manual invocation:** `Skill(skill="plan-authoring-cycle")` when a plan has placeholder content.
**Called from:** implementation-cycle PLAN phase when plan needs population.

---

## The Cycle

```
ANALYZE --> AUTHOR --> VALIDATE
```

### 1. ANALYZE Phase

**Goal:** Read plan and identify sections needing population.

**Actions:**
1. Read the plan file: `docs/plans/PLAN-{backlog_id}-*.md`
2. Check each section for placeholder text:
   - Goal: `[One sentence: ...]`
   - Effort Estimation: `[N]` placeholders
   - Current/Desired State: `[What the system...]`
   - Tests First: `test_[descriptive_name]`
   - Detailed Design: `[path/to/file.py]`
3. Create checklist of sections to populate

**Exit Criteria:**
- [ ] Plan file read
- [ ] Empty sections identified
- [ ] Checklist created

**Tools:** Read

---

### 2. AUTHOR Phase

**Goal:** Systematically populate each section with real content.

**Guardrails (MUST follow):**
1. **Goal section MUST be one sentence** - Clear, measurable outcome
2. **Effort Estimation MUST reference real files** - Glob for file counts, wc for lines
3. **Current/Desired State MUST show actual code** - Read files, copy snippets
4. **Tests MUST be written before design** - TDD mindset

**Section Order:**
1. **Goal** - What capability will exist?
2. **Effort Estimation** - Count files, estimate time
3. **Current State** - What exists now?
4. **Desired State** - What should exist?
5. **Tests First** - What tests verify success?
6. **Detailed Design** - How to implement?
7. **Implementation Steps** - Ordered checklist

**Actions:**
1. For each empty section:
   - Read relevant source files
   - Query memory for prior patterns
   - Write concrete content (not placeholders)
2. Update plan status to `approved` when complete

**Exit Criteria:**
- [ ] Goal is one clear sentence
- [ ] Effort Estimation has real numbers from file analysis
- [ ] Current/Desired State shows actual code
- [ ] Tests section has concrete test definitions
- [ ] Design section has implementation details
- [ ] Steps section has actionable checklist

**Tools:** Read, Glob, Grep, Edit, memory_search_with_experience

---

### 3. VALIDATE Phase

**Goal:** Verify plan is ready for implementation.

**Actions:**
1. Re-read plan file
2. Check no placeholder text remains (`[...]` patterns)
3. Verify section completeness:
   - Goal: >20 characters, no placeholders
   - Effort: All metrics have values
   - Design: Has file paths and code snippets
   - Tests: Has at least one concrete test
4. Update plan status: `approved`

**Exit Criteria:**
- [ ] No placeholder text remains
- [ ] All required sections populated
- [ ] Plan status is `approved`

**Tools:** Read, Edit

---

## Composition Map

| Phase | Primary Tool | Memory Integration |
|-------|--------------|-------------------|
| ANALYZE | Read | - |
| AUTHOR | Read, Edit, Glob | Query for prior patterns |
| VALIDATE | Read, Edit | - |

---

## Quick Reference

| Phase | Question to Ask | If NO |
|-------|-----------------|-------|
| ANALYZE | Is plan read? | Read plan file |
| ANALYZE | Are empty sections identified? | Scan for placeholders |
| AUTHOR | Is Goal complete? | Write one-sentence goal |
| AUTHOR | Is Effort estimated? | Count files, estimate time |
| AUTHOR | Is Design complete? | Write implementation details |
| VALIDATE | Are all sections complete? | Return to AUTHOR |
| VALIDATE | Is status approved? | Update frontmatter |
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Three phases | ANALYZE → AUTHOR → VALIDATE | Matches work-creation-cycle pattern |
| Optional skill | Not required by implementation-cycle | Some plans may come pre-filled |
| Section order | Goal → Effort → State → Tests → Design | Logical progression from abstract to concrete |
| TDD before Design | Tests defined before implementation details | Enforces test-first thinking |

### Edge Cases

| Case | Handling |
|------|----------|
| Plan already complete | ANALYZE detects no empty sections, skip to VALIDATE |
| Partial population | ANALYZE identifies remaining sections |
| Complex design | AUTHOR may need multiple passes |

---

## Implementation Steps

### Step 1: Create skill directory and SKILL.md
- [ ] Create directory: `.claude/skills/plan-authoring-cycle/`
- [ ] Create SKILL.md with content from Detailed Design
- [ ] Verify frontmatter includes required fields (`name`, `description`, `generated`, `last_updated`)

### Step 2: Create skill README
- [ ] Create `.claude/skills/plan-authoring-cycle/README.md`
- [ ] Document skill purpose and usage

### Step 3: Update parent skills README
- [ ] Add plan-authoring-cycle to `.claude/skills/README.md` skill list
- [ ] Add to Cycle Skills section
- [ ] Add to directory structure

### Step 4: Verify runtime discovery
- [ ] Run `just update-status-slim`
- [ ] Check skill appears in `haios-status-slim.json`
- [ ] Verify via: `python -c "import json; d=json.load(open('.claude/haios-status-slim.json')); print('plan-authoring-cycle' in d['infrastructure']['skills'])"`

---

## Verification

- [ ] Skill file exists: `.claude/skills/plan-authoring-cycle/SKILL.md`
- [ ] Runtime discovery: skill in `haios-status-slim.json`
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Skill not discovered | Low | Run `just update-status` and verify JSON |
| Over-complexity | Low | Keep phases simple, optional use |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 117 | 2025-12-25 | - | In Progress | Plan created |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/plan-authoring-cycle/SKILL.md` | Has frontmatter + 3 phases | [ ] | |
| `.claude/haios-status-slim.json` | Lists plan-authoring-cycle in skills | [ ] | |
| `.claude/skills/plan-authoring-cycle/README.md` | Exists, describes skill | [ ] | |
| `.claude/skills/README.md` | Lists plan-authoring-cycle | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
just update-status-slim
python -c "import json; d=json.load(open('.claude/haios-status-slim.json')); print('plan-authoring-cycle' in d['infrastructure']['skills'])"
# Expected: True
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [ ] | |
| Runtime discovery verified? | [ ] | |
| Any deviations from plan? | [ ] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Skill file exists and has valid content
- [ ] Runtime discovery works
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated
- [ ] Ground Truth Verification completed above

---

## References

- INV-033: Skill as Node Entry Gate Formalization
- INV-035: Skill Architecture Refactoring
- E2-180: work-creation-cycle skill (parallel pattern)
- E2-181: close-work-cycle skill (parallel pattern)

---
