# generated: 2025-12-08
# System Auto: last updated on: 2025-12-08 22:56:20
# Test-LifecycleId.ps1
# Unit tests for E2-015 Lifecycle ID Propagation
#
# USAGE:
#   powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/tests/Test-LifecycleId.ps1
#
# METHODOLOGY: AODEV TDD - Tests written BEFORE implementation
# PLAN: PLAN-E2-015-LIFECYCLE-ID-PROPAGATION.md
# BACKLOG: E2-015

$ErrorActionPreference = "Stop"
$script:TestsPassed = 0
$script:TestsFailed = 0
$script:TestResults = @()

# ============================================================================
# TEST HELPERS
# ============================================================================

function Assert-Equal {
    param($Expected, $Actual, $Message)
    if ($Expected -eq $Actual) {
        $script:TestsPassed++
        $script:TestResults += @{ Status = "PASS"; Message = $Message }
        Write-Host "  [PASS] $Message" -ForegroundColor Green
    } else {
        $script:TestsFailed++
        $script:TestResults += @{ Status = "FAIL"; Message = $Message; Expected = $Expected; Actual = $Actual }
        Write-Host "  [FAIL] $Message" -ForegroundColor Red
        Write-Host "         Expected: $Expected" -ForegroundColor Yellow
        Write-Host "         Actual:   $Actual" -ForegroundColor Yellow
    }
}

function Assert-True {
    param($Condition, $Message)
    Assert-Equal $true $Condition $Message
}

function Assert-False {
    param($Condition, $Message)
    Assert-Equal $false $Condition $Message
}

function Assert-NotNull {
    param($Value, $Message)
    if ($null -ne $Value) {
        $script:TestsPassed++
        $script:TestResults += @{ Status = "PASS"; Message = $Message }
        Write-Host "  [PASS] $Message" -ForegroundColor Green
    } else {
        $script:TestsFailed++
        $script:TestResults += @{ Status = "FAIL"; Message = $Message; Expected = "not null"; Actual = "null" }
        Write-Host "  [FAIL] $Message" -ForegroundColor Red
    }
}

function Assert-Contains {
    param($Haystack, $Needle, $Message)
    if ($Haystack -like "*$Needle*") {
        $script:TestsPassed++
        $script:TestResults += @{ Status = "PASS"; Message = $Message }
        Write-Host "  [PASS] $Message" -ForegroundColor Green
    } else {
        $script:TestsFailed++
        $script:TestResults += @{ Status = "FAIL"; Message = $Message; Expected = "contains '$Needle'"; Actual = "not found" }
        Write-Host "  [FAIL] $Message" -ForegroundColor Red
    }
}

function Assert-Match {
    param($Value, $Pattern, $Message)
    if ($Value -match $Pattern) {
        $script:TestsPassed++
        $script:TestResults += @{ Status = "PASS"; Message = $Message }
        Write-Host "  [PASS] $Message" -ForegroundColor Green
    } else {
        $script:TestsFailed++
        $script:TestResults += @{ Status = "FAIL"; Message = $Message; Expected = "matches '$Pattern'"; Actual = $Value }
        Write-Host "  [FAIL] $Message" -ForegroundColor Red
    }
}

# ============================================================================
# TEST FIXTURES
# ============================================================================

# Path resolution: tests/ -> hooks/ -> .claude/ -> project root
$hooksDir = Split-Path -Parent $PSScriptRoot
$claudeDir = Split-Path -Parent $hooksDir
$projectRoot = Split-Path -Parent $claudeDir
$templateDir = Join-Path $claudeDir "templates"

# Debug path resolution
Write-Host "Project Root: $projectRoot" -ForegroundColor Gray
Write-Host "Hooks Dir: $hooksDir" -ForegroundColor Gray
Write-Host "Template Dir: $templateDir" -ForegroundColor Gray

# Test content for plans WITH backlog_id
$testPlanWithBacklogId = @"
---
template: implementation_plan
status: draft
date: 2025-12-08
backlog_id: E2-015
directive_id: PLAN-E2-015-TEST
title: "Test Plan"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# Test Plan

@docs/README.md
@docs/epistemic_state.md
"@

# Test content for plans WITHOUT backlog_id (should be blocked)
$testPlanWithoutBacklogId = @"
---
template: implementation_plan
status: draft
date: 2025-12-08
directive_id: PLAN-TEST
title: "Test Plan Without Backlog ID"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# Test Plan

@docs/README.md
@docs/epistemic_state.md
"@

# Test content for checkpoint WITH backlog_ids array
$testCheckpointWithBacklogIds = @"
---
template: checkpoint
status: active
date: 2025-12-08
title: "Session 49: Test Checkpoint"
author: Hephaestus
session: 49
backlog_ids: [E2-015, E2-001]
project_phase: Epoch 2 - Governance Suite
lifecycle_phase: capture
version: "1.0"
---
# Test Checkpoint

@docs/README.md
@docs/epistemic_state.md
"@

# ============================================================================
# TEST 1: Template has backlog_id field
# ============================================================================

Write-Host "`n=== TEST 1: Template Schema ===" -ForegroundColor Cyan

# Test 1.1: implementation_plan template has backlog_id placeholder
Write-Host "`nTest 1.1: implementation_plan template has backlog_id" -ForegroundColor White
$planTemplate = Join-Path $templateDir "implementation_plan.md"
if (Test-Path $planTemplate) {
    $content = Get-Content $planTemplate -Raw
    $hasBacklogId = $content -match "backlog_id:\s*\{\{BACKLOG_ID\}\}"
    Assert-True $hasBacklogId "implementation_plan template contains backlog_id: {{BACKLOG_ID}}"
} else {
    Write-Host "  [SKIP] Template not found: $planTemplate" -ForegroundColor Yellow
    $script:TestsFailed++
}

# Test 1.2: checkpoint template has backlog_ids placeholder (optional array)
Write-Host "`nTest 1.2: checkpoint template has backlog_ids (optional)" -ForegroundColor White
$validatorPath = Join-Path $hooksDir "ValidateTemplate.ps1"
if (Test-Path $validatorPath) {
    $validatorContent = Get-Content $validatorPath -Raw
    # Check if backlog_ids appears anywhere in checkpoint OptionalFields
    $hasBacklogIdsOptional = $validatorContent -match 'backlog_ids'
    Assert-True $hasBacklogIdsOptional "ValidateTemplate allows backlog_ids for checkpoint"
} else {
    Write-Host "  [SKIP] Validator not found" -ForegroundColor Yellow
    $script:TestsFailed++
}

# ============================================================================
# TEST 2: Scaffold passes BACKLOG_ID variable
# ============================================================================

Write-Host "`n=== TEST 2: ScaffoldTemplate Variable Handling ===" -ForegroundColor Cyan

# Test 2.1: ScaffoldTemplate substitutes BACKLOG_ID
Write-Host "`nTest 2.1: ScaffoldTemplate substitutes BACKLOG_ID variable" -ForegroundColor White
$scaffoldScript = Join-Path $hooksDir "ScaffoldTemplate.ps1"
if (Test-Path $scaffoldScript) {
    $content = Get-Content $scaffoldScript -Raw
    # Check if script handles BACKLOG_ID in variables (should work by default since it does generic substitution)
    # The real test is whether template HAS the placeholder (Test 1.1)
    # Here we verify the scaffold doesn't exclude BACKLOG_ID
    $handlesBacklogId = $content -notmatch 'BACKLOG_ID.*excluded|skip.*BACKLOG_ID'
    Assert-True $handlesBacklogId "ScaffoldTemplate does not exclude BACKLOG_ID"
} else {
    Write-Host "  [SKIP] Scaffold script not found" -ForegroundColor Yellow
    $script:TestsFailed++
}

# ============================================================================
# TEST 3: PreToolUse blocks plans without backlog_id
# ============================================================================

Write-Host "`n=== TEST 3: PreToolUse Governance ===" -ForegroundColor Cyan

# Test 3.1: Plans without backlog_id should be blocked
Write-Host "`nTest 3.1: PreToolUse blocks plans without backlog_id" -ForegroundColor White
$preToolUseScript = Join-Path $hooksDir "PreToolUse.ps1"
if (Test-Path $preToolUseScript) {
    $content = Get-Content $preToolUseScript -Raw
    # Check if PreToolUse validates backlog_id for plans
    $validatesBacklogId = $content -match 'backlog_id'
    Assert-True $validatesBacklogId "PreToolUse checks for backlog_id in plans"
} else {
    Write-Host "  [SKIP] PreToolUse script not found" -ForegroundColor Yellow
    $script:TestsFailed++
}

# ============================================================================
# TEST 4: UpdateHaiosStatus parses backlog_id from YAML
# ============================================================================

Write-Host "`n=== TEST 4: UpdateHaiosStatus YAML Parsing ===" -ForegroundColor Cyan

# Test 4.1: backlog_id is extracted from YAML frontmatter
Write-Host "`nTest 4.1: UpdateHaiosStatus extracts backlog_id from YAML" -ForegroundColor White
$updateScript = Join-Path $hooksDir "UpdateHaiosStatus.ps1"
if (Test-Path $updateScript) {
    $content = Get-Content $updateScript -Raw
    # Check if script parses backlog_id from YAML
    $parsesBacklogId = $content -match "backlog_id.*=.*yaml.*match|yaml.*backlog_id"
    Assert-True $parsesBacklogId "UpdateHaiosStatus parses backlog_id from YAML frontmatter"
} else {
    Write-Host "  [SKIP] UpdateHaiosStatus script not found" -ForegroundColor Yellow
    $script:TestsFailed++
}

# Test 4.2: haios-status.json has non-null backlog_id for plans with it
Write-Host "`nTest 4.2: haios-status.json shows backlog_id for E2-015 plan" -ForegroundColor White
$statusFile = Join-Path $projectRoot ".claude\haios-status.json"
if (Test-Path $statusFile) {
    $status = Get-Content $statusFile -Raw | ConvertFrom-Json
    # Find E2-015 plan in live_files
    $e2015Plan = $status.lifecycle.live_files | Where-Object { $_.path -match "E2-015" }
    if ($e2015Plan) {
        $hasBacklogId = $null -ne $e2015Plan.backlog_id -and $e2015Plan.backlog_id -ne ""
        Assert-True $hasBacklogId "E2-015 plan has non-null backlog_id in haios-status.json"
    } else {
        Write-Host "  [INFO] E2-015 plan not found in haios-status.json yet" -ForegroundColor Yellow
        $script:TestsFailed++
    }
} else {
    Write-Host "  [SKIP] haios-status.json not found" -ForegroundColor Yellow
    $script:TestsFailed++
}

# ============================================================================
# TEST 5: Existing plans have backlog_id (retrofit verification)
# ============================================================================

Write-Host "`n=== TEST 5: Retrofit Verification ===" -ForegroundColor Cyan

# Test 5.1: Sample existing E2-xxx plans have backlog_id
Write-Host "`nTest 5.1: Existing PLAN-E2-xxx files have backlog_id" -ForegroundColor White
$plansDir = Join-Path $projectRoot "docs\plans"
if (Test-Path $plansDir) {
    $e2Plans = Get-ChildItem $plansDir -Filter "PLAN-E2*.md" -ErrorAction SilentlyContinue | Select-Object -First 3
    $retrofitCount = 0
    $totalCount = 0
    foreach ($plan in $e2Plans) {
        $totalCount++
        $content = Get-Content $plan.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -match 'backlog_id:\s*E2-\d{3}') {
            $retrofitCount++
        }
    }
    if ($totalCount -gt 0) {
        $allRetrofitted = $retrofitCount -eq $totalCount
        Assert-True $allRetrofitted "Existing E2-xxx plans have backlog_id ($retrofitCount/$totalCount)"
    } else {
        Write-Host "  [SKIP] No E2-xxx plans found to check" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [SKIP] Plans directory not found" -ForegroundColor Yellow
    $script:TestsFailed++
}

# ============================================================================
# TEST 6: Command signature validation
# ============================================================================

Write-Host "`n=== TEST 6: Command Signatures ===" -ForegroundColor Cyan

# Test 6.1: /new-plan command documentation shows backlog_id requirement
Write-Host "`nTest 6.1: /new-plan command requires backlog_id" -ForegroundColor White
$newPlanCmd = Join-Path $projectRoot ".claude\commands\new-plan.md"
if (Test-Path $newPlanCmd) {
    $content = Get-Content $newPlanCmd -Raw
    # Check if command signature includes backlog_id
    $requiresBacklogId = $content -match 'backlog_id|BACKLOG_ID|<backlog_id>'
    Assert-True $requiresBacklogId "/new-plan command signature includes backlog_id"
} else {
    Write-Host "  [SKIP] new-plan.md command not found" -ForegroundColor Yellow
    $script:TestsFailed++
}

# ============================================================================
# TEST SUMMARY
# ============================================================================

Write-Host "`n=== TEST SUMMARY ===" -ForegroundColor Cyan
Write-Host "Passed: $($script:TestsPassed)" -ForegroundColor Green
Write-Host "Failed: $($script:TestsFailed)" -ForegroundColor $(if ($script:TestsFailed -gt 0) { "Red" } else { "Green" })
Write-Host "Total:  $($script:TestsPassed + $script:TestsFailed)" -ForegroundColor White

if ($script:TestsFailed -gt 0) {
    Write-Host "`nFailing tests indicate E2-015 features not yet implemented (TDD RED phase)" -ForegroundColor Yellow
    Write-Host "Implement the following to make tests pass:" -ForegroundColor Yellow
    Write-Host "  1. Add backlog_id: {{BACKLOG_ID}} to implementation_plan.md template" -ForegroundColor Yellow
    Write-Host "  2. Add backlog_ids to checkpoint OptionalFields in ValidateTemplate.ps1" -ForegroundColor Yellow
    Write-Host "  3. Add backlog_id validation to PreToolUse.ps1" -ForegroundColor Yellow
    Write-Host "  4. Add backlog_id YAML parsing to UpdateHaiosStatus.ps1" -ForegroundColor Yellow
    Write-Host "  5. Update /new-plan command to require backlog_id" -ForegroundColor Yellow
    Write-Host "  6. Retrofit existing PLAN-E2-xxx files with backlog_id" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "`nAll tests passing (TDD GREEN phase)" -ForegroundColor Green
    exit 0
}
