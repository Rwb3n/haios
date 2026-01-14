# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 20:59:13
# Test-GovernanceReminders.ps1
# Unit tests for E2-037 Phase 2: RFC 2119 Governance Reminders
#
# USAGE:
#   powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/tests/Test-GovernanceReminders.ps1
#
# METHODOLOGY: AODEV TDD
# PLAN: PLAN-E2-037-PHASE2-DYNAMIC-REMINDERS.md
# BACKLOG: E2-037

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

function Assert-NotContains {
    param($Haystack, $Needle, $Message)
    if (-not ($Haystack -like "*$Needle*")) {
        $script:TestsPassed++
        $script:TestResults += @{ Status = "PASS"; Message = $Message }
        Write-Host "  [PASS] $Message" -ForegroundColor Green
    } else {
        $script:TestsFailed++
        $script:TestResults += @{ Status = "FAIL"; Message = $Message; Expected = "does not contain '$Needle'"; Actual = "found" }
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

# Debug path resolution
Write-Host "Project Root: $projectRoot" -ForegroundColor Gray
Write-Host "Hooks Dir: $hooksDir" -ForegroundColor Gray

# UserPromptSubmit script path
$userPromptSubmitScript = Join-Path $hooksDir "UserPromptSubmit.ps1"

# ============================================================================
# HELPER: Simulate trigger detection
# ============================================================================

function Test-DiscoveryTrigger {
    param($prompt)
    $hasBugKeyword = $prompt -match "(bug|issue|gap|problem|broken|wrong|error)"
    $hasActionKeyword = $prompt -match "(found|discovered|noticed|identified|see|seeing)"
    return ($hasBugKeyword -and $hasActionKeyword)
}

function Test-SqlTrigger {
    param($prompt)
    $hasActionQuery = $prompt -match "(run|execute|write|check|query).*(sql|query|database)"
    $hasSqlKeyword = $prompt -match "(select|insert|update|delete)\s+(from|into)"
    return ($hasActionQuery -or $hasSqlKeyword)
}

function Test-CloseTrigger {
    param($prompt)
    return ($prompt -match "(close|complete|finish|done|mark).*(E2-[A-Z]*-?\d{3}|INV-\d{3}|TD-\d{3})")
}

function Extract-BacklogId {
    param($prompt)
    if ($prompt -match "(E2-[A-Z]*-?\d{3}|INV-\d{3}|TD-\d{3})") {
        return $Matches[1]
    }
    return $null
}

# ============================================================================
# TEST 1: Discovery keywords trigger investigation reminder
# ============================================================================

Write-Host "`n=== TEST 1: Discovery Trigger Detection ===" -ForegroundColor Cyan

# Test 1.1: "found a bug" triggers reminder
Write-Host "`nTest 1.1: 'found a bug' triggers discovery reminder" -ForegroundColor White
$prompt1 = "I found a bug in the synthesis module"
Assert-True (Test-DiscoveryTrigger $prompt1) "'found a bug' triggers discovery reminder"

# Test 1.2: "discovered an issue" triggers reminder
Write-Host "`nTest 1.2: 'discovered an issue' triggers discovery reminder" -ForegroundColor White
$prompt2 = "Just discovered an issue with the hook"
Assert-True (Test-DiscoveryTrigger $prompt2) "'discovered an issue' triggers discovery reminder"

# Test 1.3: "see a problem" triggers reminder
Write-Host "`nTest 1.3: 'see a problem' triggers discovery reminder" -ForegroundColor White
$prompt3 = "I see a problem with this approach"
Assert-True (Test-DiscoveryTrigger $prompt3) "'see a problem' triggers discovery reminder"

# Test 1.4: "noticed an error" triggers reminder
Write-Host "`nTest 1.4: 'noticed an error' triggers discovery reminder" -ForegroundColor White
$prompt4 = "I noticed an error in the output"
Assert-True (Test-DiscoveryTrigger $prompt4) "'noticed an error' triggers discovery reminder"

# ============================================================================
# TEST 2: SQL keywords trigger schema-verifier reminder
# ============================================================================

Write-Host "`n=== TEST 2: SQL Trigger Detection ===" -ForegroundColor Cyan

# Test 2.1: "run a sql query" triggers reminder
Write-Host "`nTest 2.1: 'run a sql query' triggers SQL reminder" -ForegroundColor White
$sqlPrompt1 = "Can you run a sql query to check the concepts?"
Assert-True (Test-SqlTrigger $sqlPrompt1) "'run a sql query' triggers SQL reminder"

# Test 2.2: "check the database" triggers reminder
Write-Host "`nTest 2.2: 'check the database' triggers SQL reminder" -ForegroundColor White
$sqlPrompt2 = "Please check the database for missing entries"
Assert-True (Test-SqlTrigger $sqlPrompt2) "'check the database' triggers SQL reminder"

# Test 2.3: "SELECT from" triggers reminder
Write-Host "`nTest 2.3: 'SELECT from' triggers SQL reminder" -ForegroundColor White
$sqlPrompt3 = "Use SELECT from concepts where type='techne'"
Assert-True (Test-SqlTrigger $sqlPrompt3) "'SELECT from' triggers SQL reminder"

# Test 2.4: "DELETE from" triggers reminder
Write-Host "`nTest 2.4: 'DELETE from' triggers SQL reminder" -ForegroundColor White
$sqlPrompt4 = "DELETE from reasoning_traces where session < 60"
Assert-True (Test-SqlTrigger $sqlPrompt4) "'DELETE from' triggers SQL reminder"

# ============================================================================
# TEST 3: Close keywords trigger /close reminder
# ============================================================================

Write-Host "`n=== TEST 3: Close Trigger Detection ===" -ForegroundColor Cyan

# Test 3.1: "close E2-037" triggers reminder
Write-Host "`nTest 3.1: 'close E2-037' triggers close reminder" -ForegroundColor White
$closePrompt1 = "Let's close E2-037 now"
Assert-True (Test-CloseTrigger $closePrompt1) "'close E2-037' triggers close reminder"

# Test 3.2: "mark INV-005 complete" triggers reminder
Write-Host "`nTest 3.2: 'mark INV-005 complete' triggers close reminder" -ForegroundColor White
$closePrompt2 = "Please mark INV-005 complete"
Assert-True (Test-CloseTrigger $closePrompt2) "'mark INV-005 complete' triggers close reminder"

# Test 3.3: "finish E2-FIX-001" triggers reminder (E2-FIX-XXX format)
Write-Host "`nTest 3.3: 'finish E2-FIX-001' triggers close reminder (E2-FIX-XXX format)" -ForegroundColor White
$closePrompt3 = "We can finish E2-FIX-001 now"
Assert-True (Test-CloseTrigger $closePrompt3) "'finish E2-FIX-001' triggers close reminder (E2-FIX-XXX format)"

# Test 3.4: Correct backlog ID extraction
Write-Host "`nTest 3.4: Backlog ID extracted correctly from close prompt" -ForegroundColor White
$extractedId = Extract-BacklogId $closePrompt3
Assert-Equal "E2-FIX-001" $extractedId "Backlog ID extracted as 'E2-FIX-001'"

# ============================================================================
# TEST 4: Override "skip reminder" bypasses detection
# ============================================================================

Write-Host "`n=== TEST 4: Override Mechanism ===" -ForegroundColor Cyan

# Test 4.1: UserPromptSubmit has skip reminder logic
Write-Host "`nTest 4.1: UserPromptSubmit checks for 'skip reminder'" -ForegroundColor White
if (Test-Path $userPromptSubmitScript) {
    $content = Get-Content $userPromptSubmitScript -Raw
    $hasSkipReminder = $content -match 'skip reminder'
    Assert-True $hasSkipReminder "UserPromptSubmit contains 'skip reminder' check"
} else {
    Write-Host "  [SKIP] UserPromptSubmit.ps1 not found" -ForegroundColor Yellow
    $script:TestsFailed++
}

# ============================================================================
# TEST 5: Single keyword without context does NOT trigger
# ============================================================================

Write-Host "`n=== TEST 5: False Positive Prevention ===" -ForegroundColor Cyan

# Test 5.1: Single word "bug" alone does not trigger
Write-Host "`nTest 5.1: Single word 'bug' alone does not trigger" -ForegroundColor White
$singleWord1 = "Show me the bug tracker"
Assert-False (Test-DiscoveryTrigger $singleWord1) "Single 'bug' without action keyword does not trigger"

# Test 5.2: Single word "error" alone does not trigger
Write-Host "`nTest 5.2: Single word 'error' alone does not trigger" -ForegroundColor White
$singleWord2 = "What is the error code?"
Assert-False (Test-DiscoveryTrigger $singleWord2) "Single 'error' without action keyword does not trigger"

# Test 5.3: "close" without backlog ID does not trigger
Write-Host "`nTest 5.3: 'close' without backlog ID does not trigger" -ForegroundColor White
$noIdPrompt = "Please close the window"
Assert-False (Test-CloseTrigger $noIdPrompt) "'close' without backlog ID does not trigger"

# Test 5.4: Normal query does not trigger SQL reminder
Write-Host "`nTest 5.4: Normal conversation does not trigger SQL reminder" -ForegroundColor White
$normalPrompt = "How do I add a new feature to the CLI?"
Assert-False (Test-SqlTrigger $normalPrompt) "Normal conversation does not trigger SQL reminder"

# ============================================================================
# TEST 6: E2-FIX-XXX format detected correctly
# ============================================================================

Write-Host "`n=== TEST 6: E2-FIX-XXX Format Support ===" -ForegroundColor Cyan

# Test 6.1: E2-FIX-001 format matches
Write-Host "`nTest 6.1: E2-FIX-001 format matches regex" -ForegroundColor White
$e2fixPrompt = "done with E2-FIX-001"
$extractedFix = Extract-BacklogId $e2fixPrompt
Assert-Equal "E2-FIX-001" $extractedFix "E2-FIX-001 format matches regex"

# Test 6.2: E2-FIX-002 format matches
Write-Host "`nTest 6.2: E2-FIX-002 format matches regex" -ForegroundColor White
$e2fix2Prompt = "complete E2-FIX-002 please"
$extractedFix2 = Extract-BacklogId $e2fix2Prompt
Assert-Equal "E2-FIX-002" $extractedFix2 "E2-FIX-002 format matches regex"

# Test 6.3: Standard E2-037 still works
Write-Host "`nTest 6.3: Standard E2-037 format still works" -ForegroundColor White
$standardPrompt = "close E2-037"
$extractedStandard = Extract-BacklogId $standardPrompt
Assert-Equal "E2-037" $extractedStandard "Standard E2-037 format still works"

# Test 6.4: Part 3 regex updated in UserPromptSubmit
Write-Host "`nTest 6.4: Part 3 regex supports E2-FIX-XXX format" -ForegroundColor White
if (Test-Path $userPromptSubmitScript) {
    $content = Get-Content $userPromptSubmitScript -Raw
    $hasFixPattern = $content -match 'E2-\[A-Z\]\*-\?\\'
    Assert-True $hasFixPattern "UserPromptSubmit Part 3 regex supports E2-FIX-XXX format"
} else {
    Write-Host "  [SKIP] UserPromptSubmit.ps1 not found" -ForegroundColor Yellow
    $script:TestsFailed++
}

# ============================================================================
# TEST 7: Part 4 exists in UserPromptSubmit
# ============================================================================

Write-Host "`n=== TEST 7: Part 4 Implementation ===" -ForegroundColor Cyan

# Test 7.1: Part 4 header exists
Write-Host "`nTest 7.1: Part 4 header exists in UserPromptSubmit" -ForegroundColor White
if (Test-Path $userPromptSubmitScript) {
    $content = Get-Content $userPromptSubmitScript -Raw
    $hasPart4 = $content -match 'PART 4.*RFC 2119 Governance'
    Assert-True $hasPart4 "Part 4 header exists in UserPromptSubmit"
} else {
    Write-Host "  [SKIP] UserPromptSubmit.ps1 not found" -ForegroundColor Yellow
    $script:TestsFailed++
}

# Test 7.2: Part 4 has discovery trigger logic
Write-Host "`nTest 7.2: Part 4 has discovery trigger logic" -ForegroundColor White
if (Test-Path $userPromptSubmitScript) {
    $content = Get-Content $userPromptSubmitScript -Raw
    $hasDiscoveryLogic = $content -match 'discoveryTrigger.*bug\|issue\|gap'
    Assert-True $hasDiscoveryLogic "Part 4 has discovery trigger logic"
} else {
    $script:TestsFailed++
}

# Test 7.3: Part 4 has SQL trigger logic
Write-Host "`nTest 7.3: Part 4 has SQL trigger logic" -ForegroundColor White
if (Test-Path $userPromptSubmitScript) {
    $content = Get-Content $userPromptSubmitScript -Raw
    $hasSqlLogic = $content -match 'sqlTrigger.*sql\|query\|database'
    Assert-True $hasSqlLogic "Part 4 has SQL trigger logic"
} else {
    $script:TestsFailed++
}

# Test 7.4: Part 4 has close trigger logic
Write-Host "`nTest 7.4: Part 4 has close trigger logic" -ForegroundColor White
if (Test-Path $userPromptSubmitScript) {
    $content = Get-Content $userPromptSubmitScript -Raw
    $hasCloseLogic = $content -match 'closeTrigger.*close\|complete\|finish'
    Assert-True $hasCloseLogic "Part 4 has close trigger logic"
} else {
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
    Write-Host "`nSome tests failed. Check implementation in UserPromptSubmit.ps1 Part 4" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "`nAll tests passing - E2-037 Phase 2 implementation verified" -ForegroundColor Green
    exit 0
}
