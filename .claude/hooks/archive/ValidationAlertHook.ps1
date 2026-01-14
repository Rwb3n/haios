# generated: 2025-09-23
# System Auto: last updated on: 2025-09-24 13:14:13
# Validation Alert Hook with Persistence
# Displays pending validation alerts and maintains them until fixed
#
# DESCRIPTION:
#   Shows validation failures on each user message until resolved
#   Re-validates files to determine if alerts should persist
#
# CONFIGURATION:
#   Add to .claude/settings.local.json under UserPromptSubmit hooks

try {
    # Check for pending alerts file
    $alertFile = "$PSScriptRoot\..\pending-alerts.json"

    if (Test-Path $alertFile) {
        # Read and parse alerts
        $alerts = Get-Content $alertFile -Raw | ConvertFrom-Json

        # Display validation issues to user
        Write-Host "`nTemplate Validation Issues:" -ForegroundColor Yellow
        Write-Host "-------------------------------------" -ForegroundColor DarkGray

        # Track files that are still invalid
        $persistentAlerts = @{
            timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            validation_failures = @()
        }

        foreach ($failure in $alerts.validation_failures) {
            # Get relative path for cleaner display
            $fileName = Split-Path $failure.file -Leaf
            $dirName = Split-Path (Split-Path $failure.file -Parent) -Leaf

            Write-Host "  $dirName/$fileName" -ForegroundColor Cyan
            Write-Host "     Type: $($failure.type)" -ForegroundColor Gray

            # Display errors (handle both array and single string)
            if ($failure.errors -is [array]) {
                foreach ($err in $failure.errors) {
                    Write-Host "     - $err" -ForegroundColor Red
                }
            } else {
                Write-Host "     - $($failure.errors)" -ForegroundColor Red
            }
            Write-Host ""

            # Re-validate the file to check if it's still invalid
            if (Test-Path $failure.file) {
                $validatorPath = "$PSScriptRoot\ValidateTemplate.ps1"
                if (Test-Path $validatorPath) {
                    try {
                        $validationOutput = & powershell.exe -ExecutionPolicy Bypass -File $validatorPath `
                            -FilePath $failure.file -JsonOutput 2>&1
                        $validationJson = $validationOutput -join ""

                        if ($validationJson) {
                            $currentValidation = $validationJson | ConvertFrom-Json

                            if (-not $currentValidation.IsValid) {
                                # Still invalid, keep in persistent alerts
                                $persistentAlerts.validation_failures += @{
                                    file = $failure.file
                                    type = $currentValidation.TemplateType
                                    errors = $currentValidation.Errors
                                }
                            }
                            # If valid, don't add to persistent alerts (auto-clears)
                        } else {
                            # Validation failed, keep original alert
                            $persistentAlerts.validation_failures += $failure
                        }
                    } catch {
                        # Error during validation, keep original alert
                        $persistentAlerts.validation_failures += $failure
                    }
                } else {
                    # Validator not found, keep original alert
                    $persistentAlerts.validation_failures += $failure
                }
            }
            # File doesn't exist anymore, don't persist alert
        }

        # Update or remove alerts based on validation status
        if ($persistentAlerts.validation_failures.Count -gt 0) {
            # Some files still have errors, update alert file
            $persistentAlerts | ConvertTo-Json -Depth 3 |
                Out-File $alertFile -Encoding UTF8

            Write-Host "  Note: $($persistentAlerts.validation_failures.Count) file(s) still have validation errors" -ForegroundColor Yellow
            Write-Host "  Alerts will persist until all errors are resolved" -ForegroundColor DarkYellow
            Write-Host ""
            Write-Host "  Reminder: Error comments with timestamps remain in files" -ForegroundColor Cyan
            Write-Host "  Clean up old error comments manually after fixing issues" -ForegroundColor Cyan
        } else {
            # All validation errors resolved, remove alert file
            Remove-Item $alertFile -Force
            Write-Host "  All validation errors have been resolved!" -ForegroundColor Green
            Write-Host ""
            Write-Host "  Reminder: Error comments with timestamps remain in files" -ForegroundColor Cyan
            Write-Host "  Clean up old error comments manually from the fixed files" -ForegroundColor Cyan
        }

        Write-Host "-------------------------------------" -ForegroundColor DarkGray
        Write-Host ""
    }

    # Silent exit - don't interfere with user prompt
    exit 0

} catch {
    # Silent fail - don't break workflow
    # But try to clean up if there was an error
    if (Test-Path $alertFile) {
        try {
            Remove-Item $alertFile -Force -ErrorAction SilentlyContinue
        } catch {}
    }
    exit 0
}