# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 22:25:34
# E2-007: Error Capture Hook
#
# DESCRIPTION:
#   Detects tool errors from PostToolUse JSON and stores them to memory
#   for pattern detection across sessions.
#
# TRIGGERS ON:
#   - Bash tool with non-zero exit code
#   - Tool response containing error indicators (Error, Exception, failed, Traceback)
#
# CONFIGURATION:
#   Add to .claude/settings.local.json PostToolUse array:
#   {
#     "type": "command",
#     "command": "powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/ErrorCapture.ps1"
#   }
#
# JSON INPUT FORMAT:
#   {
#     "tool_name": "Bash|Read|Write|...",
#     "tool_input": { ... },
#     "tool_response": "..." or { "content": "...", "exit_code": N }
#   }
#
# AUTHOR: Hephaestus (Session 69)
# VERSION: 1.0

param()

# Read JSON input from stdin
$jsonInput = [Console]::In.ReadToEnd()

# Error patterns to detect (case-insensitive)
$errorPatterns = @(
    'error:',
    'Error:',
    'ERROR:',
    'Exception:',
    'Traceback',
    'FAILED',
    'failed to',
    'No such file',
    'Permission denied',
    'command not found',
    'syntax error',
    'TypeError:',
    'ValueError:',
    'KeyError:',
    'AttributeError:',
    'ImportError:',
    'ModuleNotFoundError:'
)

function Test-IsError {
    param([string]$Response, [string]$ToolName, $ToolInput)

    # Check for exit code (Bash tool)
    if ($ToolName -eq "Bash") {
        # Bash responses may have exit code info
        if ($Response -match 'Exit code (\d+)' -or $Response -match 'exit code (\d+)') {
            $exitCode = [int]$Matches[1]
            if ($exitCode -ne 0) {
                return $true
            }
        }
    }

    # Check for error patterns in response
    foreach ($pattern in $errorPatterns) {
        if ($Response -match [regex]::Escape($pattern)) {
            return $true
        }
    }

    return $false
}

function Get-ErrorMessage {
    param([string]$Response)

    # Try to extract meaningful error message
    # Look for common error formats
    $lines = $Response -split "`n"

    foreach ($line in $lines) {
        foreach ($pattern in $errorPatterns) {
            if ($line -match [regex]::Escape($pattern)) {
                # Return this line and next few for context
                $idx = [Array]::IndexOf($lines, $line)
                $endIdx = [Math]::Min($idx + 3, $lines.Count - 1)
                return ($lines[$idx..$endIdx] -join "`n").Trim()
            }
        }
    }

    # Fallback: return first 200 chars
    if ($Response.Length -gt 200) {
        return $Response.Substring(0, 200) + "..."
    }
    return $Response
}

function Get-InputSummary {
    param($ToolInput, [string]$ToolName)

    try {
        switch ($ToolName) {
            "Bash" {
                if ($ToolInput.command) {
                    $cmd = $ToolInput.command
                    if ($cmd.Length -gt 100) {
                        return $cmd.Substring(0, 100) + "..."
                    }
                    return $cmd
                }
            }
            "Read" {
                if ($ToolInput.file_path) {
                    return "file: $($ToolInput.file_path)"
                }
            }
            "Write" {
                if ($ToolInput.file_path) {
                    return "file: $($ToolInput.file_path)"
                }
            }
            "Edit" {
                if ($ToolInput.file_path) {
                    return "file: $($ToolInput.file_path)"
                }
            }
            "Grep" {
                if ($ToolInput.pattern) {
                    return "pattern: $($ToolInput.pattern)"
                }
            }
            default {
                # Generic: stringify and truncate
                $str = $ToolInput | ConvertTo-Json -Compress -Depth 2
                if ($str.Length -gt 100) {
                    return $str.Substring(0, 100) + "..."
                }
                return $str
            }
        }
    } catch {
        return "[input unavailable]"
    }

    return ""
}

try {
    # Parse JSON input
    $hookData = $jsonInput | ConvertFrom-Json

    $toolName = $hookData.tool_name
    $toolInput = $hookData.tool_input
    $toolResponse = $hookData.tool_response

    # Convert response to string if it's an object
    if ($toolResponse -is [PSCustomObject]) {
        $responseStr = $toolResponse | ConvertTo-Json -Compress -Depth 5
    } else {
        $responseStr = [string]$toolResponse
    }

    # Check if this is an error
    if (Test-IsError -Response $responseStr -ToolName $toolName -ToolInput $toolInput) {
        # Extract error details
        $errorMessage = Get-ErrorMessage -Response $responseStr
        $inputSummary = Get-InputSummary -ToolInput $toolInput -ToolName $toolName

        # Call Python script to store error
        $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
        $pythonScript = Join-Path $scriptDir "error_capture.py"

        if (Test-Path $pythonScript) {
            # Escape arguments for command line
            $escapedTool = $toolName -replace '"', '\"'
            $escapedError = $errorMessage -replace '"', '\"' -replace "`n", " " -replace "`r", ""
            $escapedInput = $inputSummary -replace '"', '\"' -replace "`n", " " -replace "`r", ""

            # Run Python script
            $result = python $pythonScript $escapedTool $escapedError $escapedInput 2>&1

            # Log result (don't output to user - silent operation)
            # Write-Host "[ERROR CAPTURE] Stored error for $toolName" -ForegroundColor Yellow
        }
    }

} catch {
    # Silent fail - don't break the workflow
    # Errors in error capture should not affect the user
}

# Always exit successfully
exit 0
