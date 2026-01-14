# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 22:26:41
# Test-ErrorCapture.ps1 - Tests for E2-007 Error Capture Hook
#
# Run with: powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/tests/Test-ErrorCapture.ps1

$ErrorActionPreference = "Stop"
$script:TestsPassed = 0
$script:TestsFailed = 0

function Write-TestResult {
    param([string]$Name, [bool]$Passed, [string]$Details = "")
    if ($Passed) {
        Write-Host "[PASS] $Name" -ForegroundColor Green
        $script:TestsPassed++
    } else {
        Write-Host "[FAIL] $Name" -ForegroundColor Red
        if ($Details) {
            Write-Host "       $Details" -ForegroundColor Yellow
        }
        $script:TestsFailed++
    }
}

# Get script directory
$scriptDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$errorCaptureScript = Join-Path $scriptDir "ErrorCapture.ps1"

Write-Host "`n=== E2-007 Error Capture Hook Tests ===" -ForegroundColor Cyan
Write-Host "Script: $errorCaptureScript`n"

# Load the script to access its functions
. $errorCaptureScript

# Test 1: Bash error with non-zero exit code detected
$test1Input = @{
    tool_name = "Bash"
    tool_input = @{ command = "ls /nonexistent" }
    tool_response = "ls: cannot access '/nonexistent': No such file or directory`nExit code 1"
} | ConvertTo-Json

$test1Response = "ls: cannot access '/nonexistent': No such file or directory`nExit code 1"
$test1Result = Test-IsError -Response $test1Response -ToolName "Bash" -ToolInput @{ command = "ls /nonexistent" }
Write-TestResult -Name "Bash error with exit code detected" -Passed $test1Result

# Test 2: Python exception detected
$test2Response = "Traceback (most recent call last):`n  File `"test.py`", line 1`nTypeError: unsupported operand"
$test2Result = Test-IsError -Response $test2Response -ToolName "Bash" -ToolInput @{ command = "python test.py" }
Write-TestResult -Name "Python Traceback detected" -Passed $test2Result

# Test 3: Permission denied detected
$test3Response = "Permission denied: /etc/shadow"
$test3Result = Test-IsError -Response $test3Response -ToolName "Read" -ToolInput @{ file_path = "/etc/shadow" }
Write-TestResult -Name "Permission denied detected" -Passed $test3Result

# Test 4: Normal response NOT detected as error
$test4Response = "File contents here`nAll good`nNo problems"
$test4Result = Test-IsError -Response $test4Response -ToolName "Read" -ToolInput @{ file_path = "test.txt" }
$test4Pass = -not $test4Result
Write-TestResult -Name "Normal response not flagged as error" -Passed $test4Pass

# Test 5: Error message extraction
$test5Response = "Starting process...`nError: Connection refused`nCleaning up..."
$test5Message = Get-ErrorMessage -Response $test5Response
$test5Pass = $test5Message -match "Error: Connection refused"
Write-TestResult -Name "Error message extraction" -Passed $test5Pass -Details "Got: $test5Message"

# Test 6: Input summary for Bash command
$test6Summary = Get-InputSummary -ToolInput @{ command = "git status" } -ToolName "Bash"
$test6Pass = $test6Summary -eq "git status"
Write-TestResult -Name "Input summary for Bash" -Passed $test6Pass -Details "Got: $test6Summary"

# Test 7: Input summary for Read file
$test7Summary = Get-InputSummary -ToolInput @{ file_path = "/path/to/file.txt" } -ToolName "Read"
$test7Pass = $test7Summary -eq "file: /path/to/file.txt"
Write-TestResult -Name "Input summary for Read" -Passed $test7Pass -Details "Got: $test7Summary"

# Test 8: Long command truncation
$longCmd = "a" * 200
$test8Summary = Get-InputSummary -ToolInput @{ command = $longCmd } -ToolName "Bash"
$test8Pass = $test8Summary.Length -le 105  # 100 + "..."
Write-TestResult -Name "Long command truncated" -Passed $test8Pass -Details "Length: $($test8Summary.Length)"

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Passed: $script:TestsPassed" -ForegroundColor Green
Write-Host "Failed: $script:TestsFailed" -ForegroundColor $(if ($script:TestsFailed -gt 0) { "Red" } else { "Green" })

if ($script:TestsFailed -gt 0) {
    exit 1
}
exit 0
