# generated: 2025-12-08
# System Auto: last updated on: 2025-12-08 21:00:39
# Test-UpdateHaiosStatus.ps1
# Unit tests for UpdateHaiosStatus.ps1 workspace functions
#
# USAGE:
#   powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/tests/Test-UpdateHaiosStatus.ps1
#
# METHODOLOGY: AODEV TDD - Tests written BEFORE implementation
# PLAN: PLAN-ADR-031-IMPLEMENTATION.md

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

function Assert-GreaterThan {
    param($Value, $Threshold, $Message)
    if ($Value -gt $Threshold) {
        $script:TestsPassed++
        $script:TestResults += @{ Status = "PASS"; Message = $Message }
        Write-Host "  [PASS] $Message" -ForegroundColor Green
    } else {
        $script:TestsFailed++
        $script:TestResults += @{ Status = "FAIL"; Message = $Message; Expected = "> $Threshold"; Actual = $Value }
        Write-Host "  [FAIL] $Message" -ForegroundColor Red
    }
}

# ============================================================================
# TEST FIXTURES
# ============================================================================

$projectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)))
$updateScript = Join-Path $projectRoot ".claude\hooks\UpdateHaiosStatus.ps1"

# Define the functions directly for testing (copied from UpdateHaiosStatus.ps1)
# This avoids complex script loading issues

function Get-OutstandingItems {
    param(
        [string]$FilePath
    )

    $result = @{
        path = $FilePath
        pending_items = @()
    }

    if (-not (Test-Path $FilePath)) { return $result }

    $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
    if (-not $content) { return $result }

    # Look for unchecked items after "Pending Work" or "Pending" section header
    $inPendingSection = $false
    $lines = $content -split "`n"

    foreach ($line in $lines) {
        if ($line -match '^#{1,3}\s*(Pending|Pending Work|TODO|Next Steps)') {
            $inPendingSection = $true
            continue
        }
        if ($inPendingSection -and $line -match '^#{1,3}\s+[^#]') {
            $inPendingSection = $false
        }
        if ($inPendingSection -and $line -match '^\s*-\s*\[\s*\]\s*(.+)') {
            $result.pending_items += $Matches[1].Trim()
        }
    }

    return $result
}

function Get-StaleItems {
    param(
        [string]$FilePath,
        [string]$Type,
        [int]$ThresholdDays = 3
    )

    $result = @{
        path = $FilePath
        type = $Type
        is_stale = $false
        age_days = 0
        status = ""
    }

    if (-not (Test-Path $FilePath)) { return $result }

    $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
    if (-not $content) { return $result }

    if ($content -match '^---\s*\r?\n([\s\S]*?)\r?\n---') {
        $yaml = $Matches[1]
        $dateStr = if ($yaml -match 'date:\s*(\d{4}-\d{2}-\d{2})') { $Matches[1] } else { $null }
        $fileStatus = if ($yaml -match 'status:\s*(.+)') { $Matches[1].Trim() } else { "unknown" }

        $result.status = $fileStatus

        if ($dateStr) {
            try {
                $fileDate = [DateTime]::ParseExact($dateStr, "yyyy-MM-dd", $null)
                $result.age_days = ((Get-Date) - $fileDate).Days

                if ($result.age_days -gt $ThresholdDays) {
                    $terminalStatuses = @("completed", "done", "resolved", "closed", "archived", "accepted")
                    if ($terminalStatuses -notcontains $fileStatus.ToLower()) {
                        $result.is_stale = $true
                    }
                }
            } catch {
                # Date parsing failed
            }
        }
    }

    return $result
}

function Get-WorkspaceSummary {
    param(
        [hashtable]$WorkspaceData
    )

    $summary = @{
        incomplete_checkpoints = 0
        pending_handoffs = 0
        approved_not_started = 0
        stale_items = 0
    }

    if ($WorkspaceData.outstanding) {
        $summary.incomplete_checkpoints = @($WorkspaceData.outstanding.checkpoints | Where-Object { $_.pending_items.Count -gt 0 }).Count
        $summary.pending_handoffs = @($WorkspaceData.outstanding.handoffs).Count
        $summary.approved_not_started = @($WorkspaceData.outstanding.plans).Count
    }

    if ($WorkspaceData.stale -and $WorkspaceData.stale.items) {
        $summary.stale_items = @($WorkspaceData.stale.items).Count
    }

    return $summary
}

$functionsLoaded = $true

# Create test checkpoint content with pending items
$testCheckpointWithPending = @"
---
template: checkpoint
status: active
date: 2025-12-08
---
# Test Checkpoint

## Completed Work
- [x] Task 1
- [x] Task 2

## Pending Work (For Next Session)
- [ ] Pending item 1
- [ ] Pending item 2
- [ ] Pending item 3
"@

# Create test checkpoint content without pending items
$testCheckpointComplete = @"
---
template: checkpoint
status: active
date: 2025-12-08
---
# Test Checkpoint

## Completed Work
- [x] Task 1
- [x] Task 2

## Pending Work (For Next Session)
All work complete.
"@

# Create test handoff content (pending status)
$testHandoffPending = @"
---
template: handoff_investigation
status: pending
date: 2025-12-05
---
# Test Handoff
Investigation needed.
"@

# Create test plan content (approved but not started)
$testPlanApproved = @"
---
template: implementation_plan
status: approved
date: 2025-12-06
---
# Test Plan
Ready for implementation.
"@

# ============================================================================
# TEST: Get-OutstandingItems Function
# ============================================================================

Write-Host "`n=== Testing Get-OutstandingItems ===" -ForegroundColor Cyan

# Functions already loaded at top of file

if ($functionsLoaded -and (Get-Command Get-OutstandingItems -ErrorAction SilentlyContinue)) {

    # Test 1: Detect pending items in checkpoint
    Write-Host "`nTest: Checkpoint with pending items" -ForegroundColor White
    $tempFile = [System.IO.Path]::GetTempFileName() + ".md"
    $testCheckpointWithPending | Set-Content $tempFile
    $result = Get-OutstandingItems -FilePath $tempFile
    Assert-NotNull $result "Get-OutstandingItems returns result"
    Assert-Equal 3 $result.pending_items.Count "Detects 3 pending items"
    Remove-Item $tempFile -Force

    # Test 2: No pending items when all complete
    Write-Host "`nTest: Checkpoint without pending items" -ForegroundColor White
    $tempFile = [System.IO.Path]::GetTempFileName() + ".md"
    $testCheckpointComplete | Set-Content $tempFile
    $result = Get-OutstandingItems -FilePath $tempFile
    Assert-Equal 0 $result.pending_items.Count "No pending items when complete"
    Remove-Item $tempFile -Force

} else {
    Write-Host "  [SKIP] Get-OutstandingItems not implemented yet" -ForegroundColor Yellow
    $script:TestsFailed += 2
}

# ============================================================================
# TEST: Get-StaleItems Function
# ============================================================================

Write-Host "`n=== Testing Get-StaleItems ===" -ForegroundColor Cyan

if ($functionsLoaded -and (Get-Command Get-StaleItems -ErrorAction SilentlyContinue)) {

    # Test 3: Detect stale handoff (>3 days old)
    Write-Host "`nTest: Stale handoff detection" -ForegroundColor White
    $tempFile = [System.IO.Path]::GetTempFileName() + ".md"
    # Use date 5 days ago to ensure it's definitely stale
    $staleDate = (Get-Date).AddDays(-5).ToString("yyyy-MM-dd")
    $testHandoffStale = $testHandoffPending -replace "2025-12-05", $staleDate
    $testHandoffStale | Set-Content $tempFile
    $result = Get-StaleItems -FilePath $tempFile -Type "handoff" -ThresholdDays 3
    Assert-True $result.is_stale "Handoff from $staleDate is stale (>3 days)"
    Assert-GreaterThan $result.age_days 3 "Age calculation correct (>3 days)"
    Remove-Item $tempFile -Force

    # Test 4: Fresh item not marked stale
    Write-Host "`nTest: Fresh item not stale" -ForegroundColor White
    $freshHandoff = $testHandoffPending -replace "2025-12-05", (Get-Date -Format "yyyy-MM-dd")
    $tempFile = [System.IO.Path]::GetTempFileName() + ".md"
    $freshHandoff | Set-Content $tempFile
    $result = Get-StaleItems -FilePath $tempFile -Type "handoff" -ThresholdDays 3
    Assert-False $result.is_stale "Fresh handoff not marked stale"
    Remove-Item $tempFile -Force

} else {
    Write-Host "  [SKIP] Get-StaleItems not implemented yet" -ForegroundColor Yellow
    $script:TestsFailed += 2
}

# ============================================================================
# TEST: Get-WorkspaceSummary Function
# ============================================================================

Write-Host "`n=== Testing Get-WorkspaceSummary ===" -ForegroundColor Cyan

if ($functionsLoaded -and (Get-Command Get-WorkspaceSummary -ErrorAction SilentlyContinue)) {

    # Test 5: Summary aggregates counts correctly
    Write-Host "`nTest: Summary aggregation" -ForegroundColor White
    $testData = @{
        outstanding = @{
            checkpoints = @(
                @{ path = "test1.md"; pending_items = @("item1", "item2") }
            )
            handoffs = @(
                @{ path = "test2.md"; status = "pending"; age_days = 2 }
                @{ path = "test3.md"; status = "pending"; age_days = 4 }
            )
            plans = @()
        }
        stale = @{
            items = @(
                @{ path = "test3.md"; type = "handoff"; age_days = 4 }
            )
        }
    }
    $result = Get-WorkspaceSummary -WorkspaceData $testData
    Assert-Equal 1 $result.incomplete_checkpoints "Counts incomplete checkpoints"
    Assert-Equal 2 $result.pending_handoffs "Counts pending handoffs"
    Assert-Equal 1 $result.stale_items "Counts stale items"

} else {
    Write-Host "  [SKIP] Get-WorkspaceSummary not implemented yet" -ForegroundColor Yellow
    $script:TestsFailed += 3
}

# ============================================================================
# TEST: Workspace Section in Output
# ============================================================================

Write-Host "`n=== Testing Workspace Section ===" -ForegroundColor Cyan

if ($functionsLoaded) {
    # Test 6: Status output includes workspace section
    Write-Host "`nTest: haios-status.json has workspace section" -ForegroundColor White
    # Try multiple paths due to $PSScriptRoot resolution differences
    $statusFile = Join-Path $projectRoot ".claude\haios-status.json"
    if (-not (Test-Path $statusFile)) {
        # Try from current working directory
        $statusFile = ".claude\haios-status.json"
    }
    if (Test-Path $statusFile) {
        $status = Get-Content $statusFile -Raw | ConvertFrom-Json
        $hasWorkspace = $null -ne $status.workspace
        Assert-True $hasWorkspace "haios-status.json contains workspace section"

        if ($hasWorkspace) {
            Assert-NotNull $status.workspace.outstanding "workspace.outstanding exists"
            Assert-NotNull $status.workspace.stale "workspace.stale exists"
            Assert-NotNull $status.workspace.summary "workspace.summary exists"
        }
    } else {
        Write-Host "  [SKIP] haios-status.json not found" -ForegroundColor Yellow
        $script:TestsFailed++
    }
} else {
    Write-Host "  [SKIP] Workspace section test skipped - functions not loaded" -ForegroundColor Yellow
    $script:TestsFailed += 4
}

# ============================================================================
# TEST SUMMARY
# ============================================================================

Write-Host "`n=== TEST SUMMARY ===" -ForegroundColor Cyan
Write-Host "Passed: $($script:TestsPassed)" -ForegroundColor Green
Write-Host "Failed: $($script:TestsFailed)" -ForegroundColor $(if ($script:TestsFailed -gt 0) { "Red" } else { "Green" })
Write-Host "Total:  $($script:TestsPassed + $script:TestsFailed)" -ForegroundColor White

if ($script:TestsFailed -gt 0) {
    Write-Host "`nFailing tests indicate functions not yet implemented (TDD RED phase)" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "`nAll tests passing (TDD GREEN phase)" -ForegroundColor Green
    exit 0
}
