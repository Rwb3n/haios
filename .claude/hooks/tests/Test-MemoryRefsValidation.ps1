# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 21:52:43
# Test-MemoryRefsValidation.ps1
# Tests for E2-021 memory_refs governance in PreToolUse.ps1

$ErrorActionPreference = "Stop"

# Colors for output
function Write-TestResult {
    param([string]$Name, [bool]$Passed, [string]$Details = "")
    if ($Passed) {
        Write-Host "  [PASS] $Name" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $Name" -ForegroundColor Red
        if ($Details) { Write-Host "         $Details" -ForegroundColor Yellow }
    }
}

$testsRun = 0
$testsPassed = 0

Write-Host "`n=== E2-021 Memory Refs Validation Tests ===" -ForegroundColor Cyan

# Test 1: Investigation-spawned item WITHOUT memory_refs should WARN
$testsRun++
$testInput = @{
    tool_name = "Edit"
    tool_input = @{
        file_path = "docs/pm/backlog.md"
        old_string = "old content"
        new_string = @"
### [HIGH] E2-999: Test Item
- **Status:** pending
- **spawned_by:** INV-005
- **Context:** Test item spawned from investigation
"@
    }
} | ConvertTo-Json -Depth 10

$result = $testInput | powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/PreToolUse.ps1 2>$null
$parsed = $result | ConvertFrom-Json -ErrorAction SilentlyContinue

if ($parsed.hookSpecificOutput.permissionDecision -eq "allow" -and
    $parsed.hookSpecificOutput.permissionDecisionReason -like "*WARNING*memory_refs*") {
    Write-TestResult "INV-spawned without memory_refs warns" $true
    $testsPassed++
} else {
    Write-TestResult "INV-spawned without memory_refs warns" $false "Got: $result"
}

# Test 2: Investigation-spawned item WITH memory_refs should silently allow
$testsRun++
$testInput = @{
    tool_name = "Edit"
    tool_input = @{
        file_path = "docs/pm/backlog.md"
        old_string = "old content"
        new_string = @"
### [HIGH] E2-999: Test Item
- **Status:** pending
- **spawned_by:** INV-005
- **memory_refs:** 64653-64669
- **Context:** Test item spawned from investigation
"@
    }
} | ConvertTo-Json -Depth 10

$result = $testInput | powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/PreToolUse.ps1 2>$null

# Should exit 0 with no output (silent allow)
if (-not $result -or $result.Trim() -eq "") {
    Write-TestResult "INV-spawned with memory_refs silently allows" $true
    $testsPassed++
} else {
    $parsed = $result | ConvertFrom-Json -ErrorAction SilentlyContinue
    if ($parsed.hookSpecificOutput.permissionDecision -eq "allow" -and
        $parsed.hookSpecificOutput.permissionDecisionReason -notlike "*WARNING*") {
        Write-TestResult "INV-spawned with memory_refs silently allows" $true
        $testsPassed++
    } else {
        Write-TestResult "INV-spawned with memory_refs silently allows" $false "Got: $result"
    }
}

# Test 3: Non-investigation item should silently allow (no warning)
$testsRun++
$testInput = @{
    tool_name = "Edit"
    tool_input = @{
        file_path = "docs/pm/backlog.md"
        old_string = "old content"
        new_string = @"
### [HIGH] E2-999: Test Item
- **Status:** pending
- **Context:** Regular item not from investigation
"@
    }
} | ConvertTo-Json -Depth 10

$result = $testInput | powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/PreToolUse.ps1 2>$null

if (-not $result -or $result.Trim() -eq "") {
    Write-TestResult "Non-investigation item silently allows" $true
    $testsPassed++
} else {
    Write-TestResult "Non-investigation item silently allows" $false "Got: $result"
}

# Test 4: INVESTIGATION- prefix (full name) also triggers warning
$testsRun++
$testInput = @{
    tool_name = "Edit"
    tool_input = @{
        file_path = "docs/pm/backlog.md"
        old_string = "old content"
        new_string = @"
### [HIGH] E2-999: Test Item
- **Status:** pending
- **spawned_by:** INVESTIGATION-E2-037-phase3
- **Context:** Test item with full investigation name
"@
    }
} | ConvertTo-Json -Depth 10

$result = $testInput | powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/PreToolUse.ps1 2>$null
$parsed = $result | ConvertFrom-Json -ErrorAction SilentlyContinue

if ($parsed.hookSpecificOutput.permissionDecision -eq "allow" -and
    $parsed.hookSpecificOutput.permissionDecisionReason -like "*WARNING*memory_refs*") {
    Write-TestResult "INVESTIGATION- prefix triggers warning" $true
    $testsPassed++
} else {
    Write-TestResult "INVESTIGATION- prefix triggers warning" $false "Got: $result"
}

# Test 5: Other files not affected
$testsRun++
$testInput = @{
    tool_name = "Edit"
    tool_input = @{
        file_path = "docs/other/random.md"
        old_string = "old content"
        new_string = @"
### Random content
- **spawned_by:** INV-005
"@
    }
} | ConvertTo-Json -Depth 10

$result = $testInput | powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/PreToolUse.ps1 2>$null

if (-not $result -or $result.Trim() -eq "") {
    Write-TestResult "Other files not affected" $true
    $testsPassed++
} else {
    Write-TestResult "Other files not affected" $false "Got: $result"
}

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Tests: $testsPassed / $testsRun passed" -ForegroundColor $(if ($testsPassed -eq $testsRun) { "Green" } else { "Yellow" })

if ($testsPassed -eq $testsRun) {
    Write-Host "All E2-021 memory_refs validation tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Some tests failed." -ForegroundColor Red
    exit 1
}
