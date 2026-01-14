---
template: implementation_plan
status: complete
date: 2025-12-08
backlog_id: E2-015
title: "E2-015 Lifecycle ID Propagation"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-08
# System Auto: last updated on: 2025-12-08 22:57:20
# Implementation Plan: E2-015 Lifecycle ID Propagation

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Enable traceable linkage from backlog items (E2-xxx) through all lifecycle documents (plans, checkpoints, reports, handoffs) via explicit `backlog_id` field propagation.

---

## Problem Statement

**Session 48 Discovery:** haios-status.json shows `backlog_id: null` for ALL files.

**Root Cause Analysis:**
1. UpdateHaiosStatus.ps1 extracts backlog IDs (E2-xxx) from backlog.md correctly
2. Matching logic at line 395 only runs for `status in ("proposed", "draft")` or `lifecycle_phase in ("decide", "plan")`
3. Approved/complete plans are never matched
4. PM section provides counts but no actionable traceability

**Impact:**
- Cannot answer: "What plans exist for E2-001?"
- Cannot answer: "What backlog item does this checkpoint relate to?"
- Cannot detect: "All work for E2-001 complete?"

**Evolution Context:** Previous project used manual lifecycle ID propagation. HAIOS should automate via scaffold commands, templates, and validation hooks.

---

## AODEV TDD Methodology

```
OBSERVE -> ANALYZE -> DECIDE -> EXECUTE -> VERIFY
           (tests)            (impl)    (green)
```

**Key Principle:** Write tests BEFORE implementation. Block on missing backlog_id.

---

## Phase 1: OBSERVE - Current State

### 1.1 Command Signatures
| Command | Current | Target |
|---------|---------|--------|
| `/new-plan` | `<name>` | `<backlog_id> <title>` |
| `/new-checkpoint` | `<session> <title>` | `<session> <title> [backlog_ids]` |

### 1.2 Template Fields
| Template | Current | Target |
|----------|---------|--------|
| `implementation_plan.md` | `directive_id` | `backlog_id` + `directive_id` |
| `checkpoint.md` | `session` | `backlog_ids` array + `session` |

### 1.3 Affected Files
| File | Change Type |
|------|-------------|
| `.claude/commands/new-plan.md` | Command signature |
| `.claude/commands/new-checkpoint.md` | Command signature |
| `.claude/templates/implementation_plan.md` | Add field |
| `.claude/templates/checkpoint.md` | Add field |
| `.claude/hooks/ScaffoldTemplate.ps1` | Variable handling |
| `.claude/hooks/PreToolUse.ps1` | Validation rule |
| `.claude/hooks/UpdateHaiosStatus.ps1` | YAML parsing |
| `docs/plans/PLAN-E2-*.md` (existing) | Retrofit |

---

## Phase 2: ANALYZE - Test Specifications (TDD RED)

### 2.1 Template Tests
```powershell
# Test: implementation_plan template has backlog_id field
Describe "Implementation Plan Template" {
    It "Should have backlog_id in RequiredFields" {
        $schema = Get-TemplateSchema "implementation_plan"
        $schema.RequiredFields | Should -Contain "backlog_id"
    }
}

# Test: checkpoint template has backlog_ids field
Describe "Checkpoint Template" {
    It "Should have backlog_ids in OptionalFields" {
        $schema = Get-TemplateSchema "checkpoint"
        $schema.OptionalFields | Should -Contain "backlog_ids"
    }
}
```

### 2.2 Scaffold Tests
```powershell
# Test: ScaffoldTemplate passes BACKLOG_ID variable
Describe "ScaffoldTemplate" {
    It "Should substitute BACKLOG_ID in output" {
        $result = Invoke-ScaffoldTemplate -Template "implementation_plan" `
            -Variables @{BACKLOG_ID='E2-015'; TITLE='Test'}
        $result | Should -Match "backlog_id: E2-015"
    }
}
```

### 2.3 Validation Tests
```powershell
# Test: PreToolUse blocks plans without backlog_id
Describe "PreToolUse Governance" {
    It "Should block plan creation without backlog_id" {
        $result = Test-GovernedPath "docs/plans/PLAN-TEST.md" -Content "no backlog_id"
        $result.blocked | Should -Be $true
        $result.reason | Should -Match "backlog_id required"
    }
}
```

### 2.4 Aggregation Tests
```powershell
# Test: UpdateHaiosStatus parses backlog_id from YAML
Describe "UpdateHaiosStatus" {
    It "Should extract backlog_id from plan frontmatter" {
        # Given a plan with backlog_id: E2-015
        $status = Get-HaiosStatus
        $plan = $status.lifecycle.live_files | Where-Object { $_.path -match "E2-015" }
        $plan.backlog_id | Should -Be "E2-015"
    }
}
```

---

## Phase 3: DECIDE - Design Decisions

### DD-015-01: Command Signature Change
**Decision:** `/new-plan <backlog_id> <title>` - backlog_id is REQUIRED first argument.
**Rationale:** Explicit is better than implicit. Forces linkage at creation time.
**Alternative Rejected:** Infer from context - too fragile, sessions cover multiple items.

### DD-015-02: Checkpoint Backlog IDs
**Decision:** `backlog_ids` is an ARRAY (optional), not single value.
**Rationale:** Sessions frequently cover multiple backlog items. E.g., Session 48 covered E2-001 (MCP consolidation) and E2-015 (this plan).
**Format:** YAML array `backlog_ids: [E2-001, E2-015]`

### DD-015-03: Validation Strictness
**Decision:** BLOCK plans missing backlog_id. WARN for checkpoints missing backlog_ids.
**Rationale:** Plans are deliberate artifacts that should always trace to backlog. Checkpoints may capture exploratory work.
**Enforcement:** PreToolUse.ps1 returns `{ "decision": "block", "reason": "backlog_id required for plans" }`

### DD-015-04: Retrofit Strategy
**Decision:** Update all existing PLAN-E2-xxx files to add backlog_id field.
**Files:** ~15 plans with E2-xxx in filename.
**Approach:** Script to extract E2-xxx from filename, add to frontmatter.

### DD-015-05: Aggregation Source
**Decision:** Parse `backlog_id` from YAML frontmatter, NOT filename.
**Rationale:** Filename matching was fragile (current broken state). Frontmatter is authoritative.
**Implementation:** UpdateHaiosStatus.ps1 line ~212 add YAML extraction.

---

## Phase 4: EXECUTE - Implementation

### 4.1 Update Templates

**`.claude/templates/implementation_plan.md`:**
```yaml
---
template: implementation_plan
status: draft
date: {{DATE}}
backlog_id: {{BACKLOG_ID}}
title: "{{TITLE}}"
```

**`.claude/templates/checkpoint.md`:**
```yaml
---
template: checkpoint
status: active
date: {{DATE}}
session: {{SESSION}}
backlog_ids: {{BACKLOG_IDS}}
title: "{{TITLE}}"
```

### 4.2 Update Commands

**`.claude/commands/new-plan.md`:**
```markdown
Arguments: $ARGUMENTS
Parse: <backlog_id> <title>

powershell.exe -ExecutionPolicy Bypass -Command "& '.claude/hooks/ScaffoldTemplate.ps1' -Template 'implementation_plan' -Output 'docs/plans/PLAN-<backlog_id>-<slug>.md' -Variables @{BACKLOG_ID='<backlog_id>'; TITLE='<title>'; DATE='yyyy-mm-dd'; ID='PLAN-<backlog_id>-<SLUG>'}"
```

**`.claude/commands/new-checkpoint.md`:**
```markdown
Arguments: $ARGUMENTS
Parse: <session> <title> [backlog_ids]

If backlog_ids not provided, prompt: "What backlog items did this session cover?"
```

### 4.3 Update ScaffoldTemplate.ps1

Add BACKLOG_ID and BACKLOG_IDS to variable substitution.

### 4.4 Update PreToolUse.ps1

Add validation rule:
```powershell
# Plans require backlog_id
if ($filePath -match "docs[/\\]plans[/\\]PLAN-" -and $tool -in @("Write", "Edit")) {
    if ($content -notmatch "backlog_id:\s*\S+") {
        return @{ decision = "block"; reason = "Plans require backlog_id in frontmatter. Use /new-plan <backlog_id> <title>" }
    }
}
```

### 4.5 Update UpdateHaiosStatus.ps1

Replace filename matching with YAML parsing:
```powershell
# Line ~212: Extract backlog_id from YAML
$backlogId = if ($yaml -match 'backlog_id:\s*(.+)') { $Matches[1].Trim() } else { $null }
$liveFiles += @{
    ...
    backlog_id = $backlogId
}
```

### 4.6 Retrofit Existing Plans

Script to update ~15 files:
```powershell
Get-ChildItem docs/plans/PLAN-E2-*.md | ForEach-Object {
    if ($_.Name -match 'PLAN-(E2-\d{3})') {
        $backlogId = $Matches[1]
        # Add backlog_id to frontmatter
    }
}
```

---

## Phase 5: VERIFY - Validation

### 5.1 Test Execution
- [ ] Template schema tests pass
- [ ] Scaffold variable tests pass
- [ ] Validation blocking tests pass
- [ ] Aggregation parsing tests pass

### 5.2 Manual Verification
- [ ] `/new-plan E2-015 Test Plan` creates file with `backlog_id: E2-015`
- [ ] `/new-checkpoint 48 Test` prompts for backlog_ids
- [ ] Writing plan without backlog_id is BLOCKED
- [ ] `haios-status.json` shows populated `backlog_id` for plans

### 5.3 Integration Check
- [ ] Existing retrofitted plans have backlog_id
- [ ] PM section shows useful traceability data
- [ ] Forward trace query works: "files for E2-001"

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing workflows | High | Retrofit first, then enable blocking |
| Command signature confusion | Medium | Clear error messages, documentation |
| Over-strict validation | Medium | Block plans only, warn checkpoints |
| Retrofit misses files | Low | Script + manual review |

---

## Success Criteria

| Criterion | Metric |
|-----------|--------|
| Plans linked | 100% of PLAN-E2-xxx have backlog_id |
| Blocking works | Cannot create plan without backlog_id |
| Aggregation works | haios-status.json shows non-null backlog_ids |
| Traceability works | Can query "files for E2-015" |

---

## References

- Backlog Item: E2-015 (docs/pm/backlog.md)
- Related: E2-001 (Memory-Governance Integration)
- Session 48 Discovery: PM section broken, all backlog_id null
- Prior Art: Manual lifecycle ID propagation in previous project

---

**Status:** COMPLETE
**Completed:** Session 49 (2025-12-08)
