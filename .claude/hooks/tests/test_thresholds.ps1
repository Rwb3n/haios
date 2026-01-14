# generated: 2025-12-17
# System Auto: last updated on: 2025-12-17 23:24:50
# Test script for E2-082 Dynamic Thresholds
# Tests each threshold condition

param(
    [ValidateSet("approaching", "bottleneck", "attention", "momentum", "all", "none")]
    [string]$TestCase = "none"
)

$projectRoot = "D:\PROJECTS\haios"
$statusPath = Join-Path $projectRoot ".claude\haios-status.json"
$slimPath = Join-Path $projectRoot ".claude\haios-status-slim.json"

# Read current status
$status = Get-Content $statusPath -Raw | ConvertFrom-Json
$slim = Get-Content $slimPath -Raw | ConvertFrom-Json

# Save originals for restore
$origProgress = $status.milestones.'M2-Governance'.progress
$origCompleted = $slim.session_delta.completed_count

Write-Host "=== E2-082 Threshold Test: $TestCase ===" -ForegroundColor Cyan
Write-Host "Original progress: $origProgress%"
Write-Host "Original completed_count: $origCompleted"
Write-Host ""

switch ($TestCase) {
    "approaching" {
        $status.milestones.'M2-Governance'.progress = 95
        Write-Host "Setting progress to 95% (threshold: >90)" -ForegroundColor Yellow
    }
    "momentum" {
        $slim.session_delta.completed_count = 5
        Write-Host "Setting completed_count to 5 (threshold: >3)" -ForegroundColor Yellow
    }
    "all" {
        $status.milestones.'M2-Governance'.progress = 95
        $slim.session_delta.completed_count = 5
        Write-Host "Setting all thresholds to trigger" -ForegroundColor Yellow
    }
    "none" {
        Write-Host "Using current values (no modification)" -ForegroundColor Green
    }
    default {
        Write-Host "Bottleneck and Attention require manual JSON edit (complex structures)" -ForegroundColor Red
        exit 1
    }
}

# Write modified files
$status | ConvertTo-Json -Depth 10 | Set-Content $statusPath
$slim | ConvertTo-Json -Depth 10 | Set-Content $slimPath

Write-Host ""
Write-Host "=== Running UserPromptSubmit Hook ===" -ForegroundColor Cyan

# Run the hook
$testInput = @{prompt="test threshold"; cwd=$projectRoot} | ConvertTo-Json
$testInput | powershell.exe -File "$projectRoot\.claude\hooks\UserPromptSubmit.ps1"

Write-Host ""
Write-Host "=== Restoring Original Values ===" -ForegroundColor Cyan

# Restore originals
$status.milestones.'M2-Governance'.progress = $origProgress
$slim.session_delta.completed_count = $origCompleted

$status | ConvertTo-Json -Depth 10 | Set-Content $statusPath
$slim | ConvertTo-Json -Depth 10 | Set-Content $slimPath

Write-Host "Restored progress: $origProgress%"
Write-Host "Restored completed_count: $origCompleted"
Write-Host "Done." -ForegroundColor Green
