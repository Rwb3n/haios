# generated: 2025-12-16
# System Auto: last updated on: 2025-12-16 21:50:02
# Setup HAIOS Heartbeat Scheduled Task
# Run as Administrator if needed

$taskName = "HAIOS-Heartbeat"
$justPath = "C:\Users\Ruben\AppData\Local\Microsoft\WinGet\Packages\Casey.Just_Microsoft.Winget.Source_8wekyb3d8bbwe\just.exe"
$workDir = "D:\PROJECTS\haios"

# Check if task exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Task '$taskName' already exists. Removing and recreating..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create action
$action = New-ScheduledTaskAction -Execute $justPath -Argument "heartbeat" -WorkingDirectory $workDir

# Create trigger - every hour, indefinitely (365 days, will auto-renew)
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)

# Create settings
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Register task
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "HAIOS hourly heartbeat - runs synthesis and status update" -ErrorAction Stop
    Write-Host "Task '$taskName' created successfully!" -ForegroundColor Green
    Write-Host "Trigger: Every hour" -ForegroundColor Cyan
    Write-Host "Action: $justPath heartbeat" -ForegroundColor Cyan
    Write-Host "Working Directory: $workDir" -ForegroundColor Cyan
} catch {
    Write-Host "Error creating task: $_" -ForegroundColor Red
    Write-Host "You may need to run this as Administrator." -ForegroundColor Yellow
}

# Show task status
Write-Host ""
Write-Host "Task Status:" -ForegroundColor Cyan
Get-ScheduledTask -TaskName $taskName | Format-Table TaskName, State, TaskPath
