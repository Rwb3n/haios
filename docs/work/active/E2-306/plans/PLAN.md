---
template: implementation_plan
status: complete
date: 2026-01-27
backlog_id: E2-306
title: Remove Legacy new-investigation Compound Recipe
author: Hephaestus
lifecycle_phase: plan
session: 252
version: '1.5'
generated: 2026-01-27
last_updated: '2026-01-27T22:46:19'
---
# Implementation Plan: Remove Legacy new-investigation Compound Recipe

@docs/work/active/E2-306/WORK.md

---

## Goal

The `new-investigation` compound recipe will be removed from the justfile, leaving `/new-investigation` command as the sole entry point.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `justfile` |
| Lines of code affected | 3 removed | Lines 32-36 in justfile |
| New files to create | 0 | - |
| Tests to write | 0 | No code logic — recipe removal verified by grep |
| Dependencies | 0 | No skill/module references this recipe |

---

## Current State vs Desired State

### Current State

```
# justfile:32-36
# Create work item + investigation document in one step (S193, ARC-008)
# Usage: just new-investigation INV-068 "My Investigation Title"
new-investigation id title:
    just work {{id}} "{{title}}"
    just inv {{id}} "{{title}}"
```

**Behavior:** Agents can call `just new-investigation` to bypass governance.

### Desired State

Lines 32-36 removed from justfile.

**Behavior:** `/new-investigation` command is the only path. E2-305's guard blocks `just new-investigation` at PreToolUse level as additional defense-in-depth.

---

## Tests First (TDD)

**SKIPPED:** Pure deletion task. No code logic to test. Verification is grep-based: confirm recipe absent from justfile and no runtime callers exist.

---

## Detailed Design

### Exact Code Change

**File:** `justfile`
**Location:** Lines 32-36

```diff
-# Create work item + investigation document in one step (S193, ARC-008)
-# Usage: just new-investigation INV-068 "My Investigation Title"
-new-investigation id title:
-    just work {{id}} "{{title}}"
-    just inv {{id}} "{{title}}"
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Remove vs deprecate | Remove entirely | Recipe has no runtime callers. E2-305 already blocks it at hook level. No reason to keep dead code. |

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | - | - | No open decisions |

---

## Implementation Steps

### Step 1: Remove recipe from justfile
- [ ] Delete lines 32-36 (comment + recipe)

### Step 2: Verify no runtime callers
- [ ] Grep for `just new-investigation` — only docs/history references expected

### Step 3: Verify `/new-investigation` command unaffected
- [ ] Confirm command file exists at `.claude/commands/new-investigation.md`

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Operator manually uses `just new-investigation` | Low | `/new-investigation` command is the replacement. E2-305 guard also blocks. |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Remove `new-investigation` recipe from justfile | [ ] | Recipe absent from justfile |
| Verify `/new-investigation` command still works | [ ] | Command file exists |
| Verify no skill/module references the removed recipe | [ ] | Grep shows only doc/history refs |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `justfile` | `new-investigation` recipe absent | [ ] | |

---

## References

- @docs/work/active/INV-070/WORK.md (parent investigation)
- @docs/work/active/E2-305/WORK.md (sibling — blocks recipe at hook level)

---
