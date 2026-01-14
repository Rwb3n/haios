# generated: 2025-09-23
# System Auto: last updated on: 2025-09-23 18:20:01
# Validation Summary Tool
# Provides statistics on template validation history
#
# USAGE:
#   powershell .claude/tools/Get-ValidationSummary.ps1 [-Period today|hour|week|all]
#
# EXAMPLES:
#   powershell .claude/tools/Get-ValidationSummary.ps1
#   powershell .claude/tools/Get-ValidationSummary.ps1 -Period hour
#   powershell .claude/tools/Get-ValidationSummary.ps1 -Period week

param(
    [ValidateSet("hour", "today", "week", "all")]
    [string]$Period = "today"
)

# Check for validation log
$logFile = "$PSScriptRoot\..\validation.jsonl"

if (-not (Test-Path $logFile)) {
    Write-Host "`n📊 Validation Summary" -ForegroundColor Cyan
    Write-Host "─────────────────────" -ForegroundColor DarkGray
    Write-Host "  No validation history found." -ForegroundColor Gray
    Write-Host "  Templates will be validated as you edit them." -ForegroundColor Gray
    Write-Host ""
    exit
}

# Read and parse validation entries
$entries = @()
Get-Content $logFile | ForEach-Object {
    if ($_.Trim()) {
        $entries += ($_ | ConvertFrom-Json)
    }
}

if ($entries.Count -eq 0) {
    Write-Host "`n📊 Validation Summary" -ForegroundColor Cyan
    Write-Host "─────────────────────" -ForegroundColor DarkGray
    Write-Host "  No validation entries found." -ForegroundColor Gray
    Write-Host ""
    exit
}

# Filter by time period
$filtered = $entries | Where-Object {
    $date = [DateTime]$_.timestamp
    $now = Get-Date

    switch ($Period) {
        "hour" { $date -gt $now.AddHours(-1) }
        "today" { $date.Date -eq $now.Date }
        "week" { $date -gt $now.AddDays(-7) }
        "all" { $true }
    }
}

# Calculate statistics
$totalCount = $filtered.Count
$validCount = ($filtered | Where-Object { $_.valid -eq $true }).Count
$invalidCount = $totalCount - $validCount

# Group by template type
$byType = $filtered | Group-Object type | Sort-Object Name

# Get recent failures
$recentFailures = $filtered | Where-Object { $_.valid -eq $false } | Select-Object -Last 3

# Display summary
Write-Host "`n📊 Validation Summary ($Period)" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════" -ForegroundColor DarkGray

# Overall stats
Write-Host "`n📈 Overall Statistics:" -ForegroundColor White
Write-Host "  Total Validations: $totalCount" -ForegroundColor Gray
Write-Host "  ✅ Valid: $validCount" -ForegroundColor Green
Write-Host "  ❌ Invalid: $invalidCount" -ForegroundColor Red

if ($validCount -gt 0) {
    $successRate = [Math]::Round(($validCount / $totalCount) * 100, 1)
    Write-Host "  📊 Success Rate: $successRate%" -ForegroundColor Cyan
}

# By template type
if ($byType.Count -gt 0) {
    Write-Host "`n📁 By Template Type:" -ForegroundColor White
    foreach ($typeGroup in $byType) {
        $typeName = if ($typeGroup.Name) { $typeGroup.Name } else { "unknown" }
        $typeValid = ($typeGroup.Group | Where-Object { $_.valid -eq $true }).Count
        $typeTotal = $typeGroup.Count
        Write-Host "  $typeName`: $typeValid/$typeTotal valid" -ForegroundColor Gray
    }
}

# Recent failures
if ($recentFailures.Count -gt 0) {
    Write-Host "`n⚠️ Recent Validation Failures:" -ForegroundColor Yellow
    foreach ($failure in $recentFailures) {
        $fileName = Split-Path $failure.file -Leaf
        Write-Host "  📄 $fileName" -ForegroundColor Cyan
        foreach ($error in $failure.errors) {
            Write-Host "     - $error" -ForegroundColor Red
        }
    }
}

# Time range info
Write-Host "`n⏰ Time Range:" -ForegroundColor White
$firstDate = [DateTime]($filtered[0].timestamp)
$lastDate = [DateTime]($filtered[-1].timestamp)

switch ($Period) {
    "hour" { Write-Host "  Last hour" -ForegroundColor Gray }
    "today" { Write-Host "  Today ($(Get-Date -Format 'yyyy-MM-dd'))" -ForegroundColor Gray }
    "week" { Write-Host "  Last 7 days" -ForegroundColor Gray }
    "all" {
        Write-Host "  From: $($firstDate.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor Gray
        Write-Host "  To:   $($lastDate.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor Gray
    }
}

Write-Host "══════════════════════════════════════" -ForegroundColor DarkGray
Write-Host ""