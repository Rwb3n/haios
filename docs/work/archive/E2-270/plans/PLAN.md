---
template: implementation_plan
status: complete
date: 2026-01-05
backlog_id: E2-270
title: Command PowerShell Elimination
author: Hephaestus
lifecycle_phase: plan
session: 174
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-05T21:12:32'
---
# Implementation Plan: Command PowerShell Elimination

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

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Replace all PowerShell invocations in command files with cross-platform `just` recipes to enable HAIOS commands to work on macOS and Linux.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | `validate.md`, `new-handoff.md`, `status.md` |
| Lines of code affected | ~30 | Mostly line replacements |
| New files to create | 0 | Using existing just recipes |
| Tests to write | 0 | Commands are prompts, no code tests |
| Dependencies | 2 | `just validate`, `just scaffold` recipes |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Commands are standalone prompts |
| Risk of regression | Low | Simple text replacement |
| External dependencies | Low | Only requires `just` |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Update commands | 15 min | High |
| Verify recipes work | 5 min | High |
| **Total** | 20 min | High |

---

## Current State vs Desired State

### Current State

**File 1: `.claude/commands/validate.md` (line 19)**
```bash
powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/ValidateTemplate.ps1 -FilePath "$1"
```

**File 2: `.claude/commands/new-handoff.md` (line 22)**
```bash
powershell.exe -ExecutionPolicy Bypass -Command "& '.claude/hooks/ScaffoldTemplate.ps1' -Template 'handoff_investigation' -Output '...' -Variables @{...}"
```

**File 3: `.claude/commands/status.md` (lines 18-19, 22)**
```python
from haios_etl.health_checks import HealthChecker  # Deprecated module
from haios_etl.job_registry import JobRegistry      # Deprecated module
```

**Behavior:** Commands only work on Windows due to PowerShell dependency.

**Result:** Cross-platform portability broken.

### Desired State

**File 1: `.claude/commands/validate.md`**
```bash
just validate $1
```

**File 2: `.claude/commands/new-handoff.md`**
```bash
just scaffold handoff_investigation <id> "<title>"
```

**File 3: `.claude/commands/status.md`**
```bash
just health
# Or use Python from .claude/lib/ directly
```

**Behavior:** Commands work on Windows, macOS, and Linux via cross-platform `just` recipes.

**Result:** Full cross-platform portability.

---

## Tests First (TDD)

**SKIPPED:** Command files are markdown prompts, not executable code. No automated tests applicable. Verification is manual via `just <recipe>` execution.

---

## Detailed Design

### Change 1: validate.md

**File:** `.claude/commands/validate.md`
**Location:** Lines 13-19

**Current Code:**
```markdown
Ref: @.claude/hooks/ValidateTemplate.ps1

## Logic
1. If NO arguments are provided:
   - Run the validation script on the ACTIVE active document (if known) or ask user for target.
2. If Argument is provided:
   - Run: `powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/ValidateTemplate.ps1 -FilePath "$1"`
```

**Changed Code:**
```markdown
Ref: `just validate` recipe (justfile line 16-17)

## Logic
1. If NO arguments are provided:
   - Ask user for target file path.
2. If Argument is provided:
   - Run: `just validate <file_path>`
```

### Change 2: new-handoff.md

**File:** `.claude/commands/new-handoff.md`
**Location:** Lines 17-23

**Current Code:**
```markdown
Run the scaffold script to create a new handoff from template.

**IMPORTANT:** Use `-Command` not `-File` to pass hashtables through bash:

```bash
powershell.exe -ExecutionPolicy Bypass -Command "& '.claude/hooks/ScaffoldTemplate.ps1' -Template 'handoff_investigation' -Output 'docs/handoff/yyyy-mm-dd-{{NN}}-<TYPE>-<name>.md' -Variables @{TITLE='<name>'; DATE='yyyy-mm-dd'}"
```
```

**Changed Code:**
```markdown
Run the scaffold recipe to create a new handoff from template:

```bash
just scaffold handoff_investigation <id> "<title>"
```

Where `<id>` is a unique identifier and `<title>` is the handoff title.
```

### Change 3: status.md

**File:** `.claude/commands/status.md`
**Location:** Lines 17-23

**Current Code:**
```markdown
5. **Health Check:** Run Python health check:
   ```
   python -c "from haios_etl.health_checks import HealthChecker; ..."
   ```
6. **Background Jobs:** Check for active jobs:
   ```
   python -c "from haios_etl.job_registry import JobRegistry; ..."
   ```
```

**Changed Code:**
```markdown
5. **Health Check:** Run health check:
   ```
   just health
   ```
6. **Background Jobs:** (Deprecated - job registry no longer used)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Use `just` recipes | Yes | Already exist (`just validate`, `just scaffold`), tested, cross-platform |
| Remove haios_etl references | Yes | haios_etl is deprecated per CLAUDE.md - use .claude/lib/ or modules/ |
| Keep command semantics | Yes | Only change invocation method, not behavior |
| Remove job registry check | Yes | job_registry was part of deprecated haios_etl, no longer used |

### Edge Cases

| Case | Handling | Notes |
|------|----------|-------|
| `just` not installed | Error message | User needs to install just |
| Missing arguments | Original behavior | Commands still prompt for missing args |
| Invalid file paths | Passed to recipe | Recipe handles validation |

---

## Implementation Steps

### Step 1: Update validate.md
- [ ] Replace PowerShell invocation with `just validate`
- [ ] Update Ref line to point to justfile
- [ ] Verify: `just validate docs/checkpoints/2026-01-05-01-*.md`

### Step 2: Update new-handoff.md
- [ ] Replace PowerShell command with `just scaffold`
- [ ] Simplify argument passing
- [ ] Verify: `just scaffold handoff_investigation TEST "Test Title"`

### Step 3: Update status.md
- [ ] Replace haios_etl imports with `just health`
- [ ] Remove deprecated job registry check
- [ ] Verify: `just health`

### Step 4: Consumer Verification
- [ ] **MUST:** Grep for remaining PowerShell references in commands
- [ ] **MUST:** Grep for remaining haios_etl references
- [ ] **MUST:** Verify no stale .ps1 references

**Consumer Discovery Pattern:**
```bash
Grep(pattern="powershell|\.ps1|haios_etl", path=".claude/commands", glob="*.md")
```

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| `just` not installed on target machine | Low | Document dependency; just is cross-platform |
| Scaffold recipe lacks handoff_investigation type | Medium | Verify recipe supports type; add if missing |
| Commands README references stale scripts | Low | Update README as part of implementation |
| Other commands still use PowerShell | Low | Grep for all .ps1 references after changes |

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
| `.claude/commands/validate.md` | No PowerShell, uses `just validate` | [ ] | |
| `.claude/commands/new-handoff.md` | No PowerShell, uses `just scaffold` | [ ] | |
| `.claude/commands/status.md` | No haios_etl, uses `just health` | [ ] | |
| `Grep: powershell\|\.ps1` in commands | Zero matches | [ ] | |
| `Grep: haios_etl` in commands | Zero matches | [ ] | |

**Verification Commands:**
```bash
# Verify no PowerShell references remain
Grep(pattern="powershell|\.ps1", path=".claude/commands", glob="*.md")
# Expected: No matches found

# Verify no haios_etl references remain
Grep(pattern="haios_etl", path=".claude/commands", glob="*.md")
# Expected: No matches found
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Grep verification completed? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.

---

## References

- INV-057: Commands Skills Templates Portability investigation
- E2-120: PowerShell Elimination (completed hook migration)
- ADR-033: Work Item Lifecycle Governance

---
