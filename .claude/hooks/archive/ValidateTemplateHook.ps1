# generated: 2025-09-23
# System Auto: last updated on: 2025-09-24 13:13:43
# ValidateTemplate Hook Wrapper
# Runs template validation on Write/Edit operations for template directories
#
# DESCRIPTION:
#   Validates templates when they are created or edited in template directories
#
# CONFIGURATION:
#   Add to .claude/settings.local.json under PostToolUse hooks

# Read JSON input from stdin
$jsonInput = [Console]::In.ReadToEnd()

try {
    # Parse the JSON input
    $hookData = $jsonInput | ConvertFrom-Json

    # Silently process hook - output suppressed by Claude Code

    # Only process file editing tools
    if ($hookData.tool_name -eq "Edit" -or $hookData.tool_name -eq "MultiEdit" -or $hookData.tool_name -eq "Write") {
        # Get file path based on tool type
        if ($hookData.tool_name -eq "Write") {
            $filePath = $hookData.tool_input.file_path
        } else {
            $filePath = $hookData.tool_response.filePath
        }

        # Get file path from hook data

        # Check if file exists and is markdown
        if ((Test-Path $filePath -PathType Leaf) -and ($filePath -like "*.md")) {
            # File exists and is markdown

            # Template directories that should trigger validation
            $templateDirs = @("templates", "directives", "plans", "reports", "checkpoints", "guides")

            # Check if file is in one of the template directories
            $shouldValidate = $false
            foreach ($dir in $templateDirs) {
                if ($filePath -like "*\$dir\*.md" -or $filePath -like "*/$dir/*.md") {
                    $shouldValidate = $true
                    # Found matching template directory
                    break
                }
            }

            # Also check for MCP guides
            if ($filePath -like "*\.claude\mcp\*.md" -or $filePath -like "*/.claude/mcp/*.md") {
                $shouldValidate = $true
                # MCP guide detected
            }

            # Check if validation needed

            if ($shouldValidate) {
                # Path to validation script
                $validatorPath = Join-Path $PSScriptRoot "ValidateTemplate.ps1"
                # Get validator script path

                if (Test-Path $validatorPath) {
                    try {
                        # Run validation with JSON output for structured results - capture as string array
                        $validationOutput = & powershell.exe -ExecutionPolicy Bypass -File $validatorPath -FilePath $filePath -JsonOutput 2>&1

                        # Join array elements into single string
                        $validationJson = $validationOutput -join ""

                        # Process validation output

                        if ($validationJson) {
                            # Parse validation result
                            $validationResult = $validationJson | ConvertFrom-Json

                            # 1. Add error comments to invalid templates
                            if (-not $validationResult.IsValid) {
                                $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                                $errorComment = "`n`n<!-- VALIDATION ERRORS ($timestamp):`n"
                                foreach ($err in $validationResult.Errors) {
                                    $errorComment += "  - $err`n"
                                }
                                $errorComment += "-->"
                                Add-Content -Path $filePath -Value $errorComment

                                # 2. Create or update pending alerts for UserPromptSubmit
                                $alertFile = "$PSScriptRoot\..\pending-alerts.json"

                                # Check if alerts already exist and merge
                                if (Test-Path $alertFile) {
                                    try {
                                        $existingAlerts = Get-Content $alertFile -Raw | ConvertFrom-Json

                                        # Check if this file is already in alerts
                                        $existingFiles = $existingAlerts.validation_failures | ForEach-Object { $_.file }

                                        if ($filePath -in $existingFiles) {
                                            # Update existing entry
                                            foreach ($failure in $existingAlerts.validation_failures) {
                                                if ($failure.file -eq $filePath) {
                                                    $failure.type = $validationResult.TemplateType
                                                    $failure.errors = $validationResult.Errors
                                                }
                                            }
                                        } else {
                                            # Add new entry
                                            $existingAlerts.validation_failures += @{
                                                file = $filePath
                                                type = $validationResult.TemplateType
                                                errors = $validationResult.Errors
                                            }
                                        }

                                        $existingAlerts.timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                                        $existingAlerts | ConvertTo-Json -Depth 3 | Out-File $alertFile -Encoding UTF8
                                    } catch {
                                        # If merge fails, create new
                                        $alert = @{
                                            timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                                            validation_failures = @(@{
                                                file = $filePath
                                                type = $validationResult.TemplateType
                                                errors = $validationResult.Errors
                                            })
                                        }
                                        $alert | ConvertTo-Json -Depth 3 | Out-File $alertFile -Encoding UTF8
                                    }
                                } else {
                                    # Create new alert file
                                    $alert = @{
                                        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                                        validation_failures = @(@{
                                            file = $filePath
                                            type = $validationResult.TemplateType
                                            errors = $validationResult.Errors
                                        })
                                    }
                                    $alert | ConvertTo-Json -Depth 3 | Out-File $alertFile -Encoding UTF8
                                }
                            }

                            # 3. Log all validations to history file
                            $logFile = "$PSScriptRoot\..\validation.jsonl"
                            $logEntry = @{
                                timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                                file = $filePath
                                valid = $validationResult.IsValid
                                type = $validationResult.TemplateType
                                errors = $validationResult.Errors
                                warnings = $validationResult.Warnings
                            }
                            $logEntry | ConvertTo-Json -Compress | Add-Content $logFile
                        } else {
                            # No validation output
                        }
                    } catch {
                        # Silently handle errors - don't break workflow
                    }
                }
            }
        }
    }
} catch {
    # Silent fail - don't break the workflow
    exit 0
}

# Exit successfully
exit 0