# generated: 2025-09-22
# System Auto: last updated on: 2025-12-20 20:48:49
# last updated on: 2025-01-20 16:24:00
# PostToolUse Hook - Auto-Timestamp for File Edits with Generation Tracking
#
# DESCRIPTION:
#   Automatically adds both a "generated" date (once, on first edit) and a "last updated"
#   timestamp to the top of files when they are modified using Claude Code's Edit,
#   MultiEdit, or Write tools. Uses appropriate comment syntax for each file type.
#
# FEATURES:
#   - File-extension-specific comment formats (// for JS, # for Python, etc.)
#   - Removes old timestamps to prevent duplicates
#   - Supports 20+ file extensions with proper comment syntax
#   - Silent error handling to avoid breaking workflows
#
# CONFIGURATION:
#   Add to .claude/settings.local.json:
#   {
#     "hooks": {
#       "PostToolUse": [
#         {
#           "matcher": "Edit|MultiEdit|Write", 
#           "hooks": [
#             {
#               "type": "command",
#               "command": "powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/PostToolUse.ps1"
#             }
#           ]
#         }
#       ]
#     }
#   }
#
# SUPPORTED FILE TYPES:
#   JavaScript/TypeScript (.js, .ts, .jsx, .tsx) -> // comment
#   C/C++/Java/C#/Go/Rust (.c, .cpp, .java, .cs, .go, .rs) -> // comment  
#   Python/Shell/PowerShell (.py, .sh, .ps1) -> # comment
#   HTML files (.html, .htm) -> <!-- comment -->
#   CSS/SCSS/SASS/LESS (.css, .scss, .sass, .less) -> /* comment */
#   Batch files (.bat, .cmd) -> REM comment
#   SQL files (.sql) -> -- comment
#   Ruby/R/Perl (.rb, .r, .pl) -> # comment
#   Default fallback -> # comment
#
# JSON INPUT FORMAT:
#   PostToolUse hooks receive JSON via stdin with structure:
#   {
#     "tool_name": "Edit|MultiEdit|Write",
#     "tool_input": { "file_path": "..." },
#     "tool_response": { "filePath": "..." }
#   }
#
# AUTHOR: Claude Code Hook System
# VERSION: 1.0 - Production Ready

# Read JSON input from stdin
$jsonInput = [Console]::In.ReadToEnd()

try {
    # Parse the JSON input
    $hookData = $jsonInput | ConvertFrom-Json
    
    # Only process file editing tools
    if (($hookData.tool_name -eq "Edit" -or $hookData.tool_name -eq "MultiEdit" -or $hookData.tool_name -eq "Write")) {
        # Get file path based on tool type
        if ($hookData.tool_name -eq "Write") {
            $filePath = $hookData.tool_input.file_path
        } else {
            $filePath = $hookData.tool_response.filePath
        }
        
        # Check if file exists and is not empty
        if (Test-Path $filePath -PathType Leaf) {
            # Skip JSON files as they don't support comments
            $extension = [System.IO.Path]::GetExtension($filePath).ToLower()
            if ($extension -eq ".json" -or $extension -eq ".jsonc") {
                exit 0
            }
            
            # Read current file content
            $content = Get-Content $filePath -Raw -ErrorAction SilentlyContinue
            
            if ($content) {
                # Get current timestamp
                $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                
                # Parse existing lines to check for YAML and timestamps
                $lines = $content -split "`r?`n"
                $hasGenerated = $false
                $generatedLine = ""
                $hasYamlHeader = $false
                $yamlEndIndex = -1
                $contentStartIndex = 0

                # Check if file starts with YAML front matter
                if ($lines.Count -gt 0 -and $lines[0] -eq "---") {
                    $hasYamlHeader = $true
                    # Find the closing ---
                    for ($i = 1; $i -lt $lines.Count; $i++) {
                        if ($lines[$i] -eq "---") {
                            $yamlEndIndex = $i
                            break
                        }
                    }
                }

                # Determine where to look for timestamps (after YAML if present)
                $timestampSearchStart = if ($yamlEndIndex -gt 0) { $yamlEndIndex + 1 } else { 0 }
                $contentStartIndex = $timestampSearchStart

                # Check for existing timestamps
                if ($timestampSearchStart -lt $lines.Count) {
                    # Check for "generated:" line (matches real dates OR {{DATE}} placeholder for templates)
                    if ($lines[$timestampSearchStart] -match "^(//|#|REM|--|<!--|\s*/\*).*generated:\s*(\d{4}-\d{2}-\d{2}|\{\{DATE\}\})") {
                        $hasGenerated = $true
                        $generatedLine = $lines[$timestampSearchStart]
                        $contentStartIndex = $timestampSearchStart + 1

                        # Check if next line is "System Auto:" and skip it
                        if ($contentStartIndex -lt $lines.Count -and $lines[$contentStartIndex] -match "^(//|#|REM|--|<!--|\s*/\*).*System Auto:.*last updated on:.*") {
                            $contentStartIndex++
                        }
                    }
                    # If no generated line, check if current line is "System Auto:" and skip it
                    elseif ($lines[$timestampSearchStart] -match "^(//|#|REM|--|<!--|\s*/\*).*System Auto:.*last updated on:.*") {
                        $contentStartIndex = $timestampSearchStart + 1
                    }
                }

                # Extract the remaining content
                $remainingContent = if ($contentStartIndex -lt $lines.Count) {
                    ($lines[$contentStartIndex..$($lines.Count - 1)]) -join "`n"
                } else {
                    ""
                }
                
                # Determine comment syntax based on file extension
                $extension = [System.IO.Path]::GetExtension($filePath).ToLower()
                
                # Handle special multi-part comment formats
                $isMultiLineComment = $false
                $commentPrefix = ""
                $commentSuffix = ""
                
                switch ($extension) {
                    ".html" { 
                        $isMultiLineComment = $true
                        $commentPrefix = "<!-- "
                        $commentSuffix = " -->"
                    }
                    ".htm" { 
                        $isMultiLineComment = $true
                        $commentPrefix = "<!-- "
                        $commentSuffix = " -->"
                    }
                    ".css" { 
                        $isMultiLineComment = $true
                        $commentPrefix = "/* "
                        $commentSuffix = " */"
                    }
                    ".scss" { 
                        $isMultiLineComment = $true
                        $commentPrefix = "/* "
                        $commentSuffix = " */"
                    }
                    ".sass" { 
                        $isMultiLineComment = $true
                        $commentPrefix = "/* "
                        $commentSuffix = " */"
                    }
                    ".less" { 
                        $isMultiLineComment = $true
                        $commentPrefix = "/* "
                        $commentSuffix = " */"
                    }
                    ".js" { $commentPrefix = "// " }
                    ".ts" { $commentPrefix = "// " }
                    ".jsx" { $commentPrefix = "// " }
                    ".tsx" { $commentPrefix = "// " }
                    ".cs" { $commentPrefix = "// " }
                    ".java" { $commentPrefix = "// " }
                    ".cpp" { $commentPrefix = "// " }
                    ".c" { $commentPrefix = "// " }
                    ".go" { $commentPrefix = "// " }
                    ".rs" { $commentPrefix = "// " }
                    ".php" { $commentPrefix = "// " }
                    ".py" { $commentPrefix = "# " }
                    ".sh" { $commentPrefix = "# " }
                    ".ps1" { $commentPrefix = "# " }
                    ".rb" { $commentPrefix = "# " }
                    ".r" { $commentPrefix = "# " }
                    ".pl" { $commentPrefix = "# " }
                    ".bat" { $commentPrefix = "REM " }
                    ".cmd" { $commentPrefix = "REM " }
                    ".sql" { $commentPrefix = "-- " }
                    default { $commentPrefix = "# " }
                }
                
                # Prepare timestamp lines
                $currentDate = Get-Date -Format "yyyy-MM-dd"

                # Build appropriate comment format
                if ($isMultiLineComment) {
                    if (-not $hasGenerated) {
                        $generatedLine = "${commentPrefix}generated: ${currentDate}${commentSuffix}"
                    }
                    $timestampLine = "${commentPrefix}System Auto: last updated on: ${timestamp}${commentSuffix}"
                } else {
                    if (-not $hasGenerated) {
                        $generatedLine = "${commentPrefix}generated: $currentDate"
                    }
                    $timestampLine = "${commentPrefix}System Auto: last updated on: $timestamp"
                }

                # Build final content preserving YAML structure
                if ($hasYamlHeader) {
                    # Preserve YAML header, add timestamps after it
                    $yamlHeader = ($lines[0..$yamlEndIndex]) -join "`n"

                    if ($remainingContent) {
                        $updatedContent = "$yamlHeader`n$generatedLine`n$timestampLine`n$remainingContent"
                    } else {
                        $updatedContent = "$yamlHeader`n$generatedLine`n$timestampLine"
                    }
                } else {
                    # No YAML header, timestamps go at the top
                    if ($remainingContent) {
                        $updatedContent = "$generatedLine`n$timestampLine`n$remainingContent"
                    } else {
                        $updatedContent = "$generatedLine`n$timestampLine"
                    }
                }
                
                # Write back to file
                Set-Content -Path $filePath -Value $updatedContent -NoNewline

                Write-Output "Added timestamp to: $filePath"

                # Template Validation Integration
                # Check if this is a template file that should be validated
                $shouldValidate = $false
                $templateDirs = @("templates", "directives", "plans", "reports", "checkpoints")

                # Check if file is in one of the template directories
                foreach ($dir in $templateDirs) {
                    if ($filePath -like "*\$dir\*.md" -or $filePath -like "*/$dir/*.md") {
                        $shouldValidate = $true
                        break
                    }
                }

                # Run validation if appropriate
                if ($shouldValidate -and $extension -eq ".md") {
                    Write-Host "[DEBUG] Should validate: $shouldValidate, Extension: $extension, Dir: $directory" -ForegroundColor Magenta

                    # Path to validation script
                    $validatorPath = Join-Path $PSScriptRoot "ValidateTemplate.ps1"

                    if (Test-Path $validatorPath) {
                        Write-Host "[DEBUG] Found validator at: $validatorPath" -ForegroundColor Magenta
                        try {
                            # Run validation with JSON output for structured results
                            $validationJson = & powershell.exe -ExecutionPolicy Bypass -File $validatorPath -FilePath $filePath -JsonOutput 2>$null

                            if ($validationJson) {
                                $validationResult = $validationJson | ConvertFrom-Json

                                # Format and display validation results
                                $fileName = Split-Path $filePath -Leaf

                                if ($validationResult.IsValid) {
                                    Write-Host "[TEMPLATE VALIDATION] " -NoNewline -ForegroundColor Cyan
                                    Write-Host "✅ Valid: $fileName" -ForegroundColor Green
                                } else {
                                    Write-Host "[TEMPLATE VALIDATION] " -NoNewline -ForegroundColor Cyan
                                    Write-Host "⚠️ Issues in ${fileName}:" -ForegroundColor Yellow

                                    foreach ($err in $validationResult.Errors) {
                                        Write-Host "  - $err" -ForegroundColor Yellow
                                    }
                                }
                            }
                        } catch {
                            # Silent fail - validation is advisory only
                        }
                    }
                }

                # ============================================================
                # DISCOVERABLE ARTIFACT REFRESH (INV-012)
                # Auto-refresh status when skills/agents/commands are modified
                # ============================================================
                $discoverablePaths = @(
                    "\.claude[\\/]skills[\\/]",
                    "\.claude[\\/]agents[\\/]",
                    "\.claude[\\/]commands[\\/]"
                )
                $isDiscoverable = $false
                foreach ($pattern in $discoverablePaths) {
                    if ($filePath -match $pattern) {
                        $isDiscoverable = $true
                        break
                    }
                }
                if ($isDiscoverable) {
                    $updateStatusPath = Join-Path $PSScriptRoot "UpdateHaiosStatus.ps1"
                    if (Test-Path $updateStatusPath) {
                        try {
                            & powershell.exe -ExecutionPolicy Bypass -File $updateStatusPath 2>$null
                            Write-Host "[STATUS] Refreshed discoverable artifacts" -ForegroundColor Cyan
                        } catch {
                            # Silent fail
                        }
                    }
                }

                # ============================================================
                # CASCADE DETECTION (E2-076e)
                # Trigger cascade on status changes to complete/accepted
                # ============================================================
                if ($hasYamlHeader -and $extension -eq ".md") {
                    try {
                        # Parse status and backlog_id from YAML frontmatter
                        $yamlContent = ($lines[0..$yamlEndIndex]) -join "`n"

                        $docStatus = $null
                        $backlogId = $null

                        if ($yamlContent -match 'status:\s*(\S+)') {
                            $docStatus = $Matches[1].Trim().ToLower()
                        }
                        if ($yamlContent -match 'backlog_id:\s*(\S+)') {
                            $backlogId = $Matches[1].Trim()
                        }

                        # Trigger cascade on completion statuses
                        $cascadeTriggers = @("complete", "completed", "done", "closed", "accepted")
                        if ($docStatus -and $backlogId -and $docStatus -in $cascadeTriggers) {
                            $cascadePath = Join-Path $PSScriptRoot "CascadeHook.ps1"
                            if (Test-Path $cascadePath) {
                                Write-Host ""
                                $cascadeOutput = & powershell.exe -ExecutionPolicy Bypass -Command "& '$cascadePath' -FilePath '$filePath' -BacklogId '$backlogId' -NewStatus '$docStatus'" 2>&1
                                if ($cascadeOutput) {
                                    Write-Host $cascadeOutput
                                }
                            }
                        }
                    } catch {
                        # Silent fail - cascade is advisory only
                    }
                }

                # ============================================================
                # CYCLE TRANSITION DETECTION (E2-097)
                # Log events when cycle_phase changes in plan files
                # ============================================================
                if ($hasYamlHeader -and $extension -eq ".md" -and $filePath -like "*plans*PLAN-*") {
                    try {
                        $yamlContent = ($lines[0..$yamlEndIndex]) -join "`n"

                        # Extract cycle_phase and backlog_id from YAML
                        $cyclePhase = $null
                        $backlogId = $null

                        if ($yamlContent -match 'lifecycle_phase:\s*(\S+)') {
                            $cyclePhase = $Matches[1].Trim().ToUpper()
                        }
                        if ($yamlContent -match 'backlog_id:\s*(\S+)') {
                            $backlogId = $Matches[1].Trim()
                        }

                        if ($cyclePhase -and $backlogId) {
                            $eventsPath = ".claude/haios-events.jsonl"
                            $fromPhase = $null

                            # Find last cycle_transition for this backlog_id
                            if (Test-Path $eventsPath) {
                                $lastEvent = Get-Content $eventsPath -ErrorAction SilentlyContinue |
                                    Where-Object { $_ -match '"type":\s*"cycle_transition"' -and $_ -match "`"backlog_id`":\s*`"$backlogId`"" } |
                                    Select-Object -Last 1

                                if ($lastEvent -and $lastEvent -match '"to_phase":\s*"([^"]+)"') {
                                    $fromPhase = $Matches[1]
                                }
                            }

                            # Only log if phase changed or no previous event
                            if ($fromPhase -ne $cyclePhase) {
                                # Get current session from haios-status.json
                                # BUG FIX (Session 89): Was reading session_delta.current_session (slim file)
                                # but main status file uses pm.last_session
                                $sessionNum = 0
                                $statusPath = ".claude/haios-status.json"
                                if (Test-Path $statusPath) {
                                    $statusJson = Get-Content $statusPath -Raw | ConvertFrom-Json
                                    if ($statusJson.pm.last_session) {
                                        $sessionNum = $statusJson.pm.last_session
                                    }
                                }

                                # Create and log the event
                                $event = @{
                                    ts = (Get-Date -Format "o")
                                    type = "cycle_transition"
                                    backlog_id = $backlogId
                                    from_phase = $fromPhase
                                    to_phase = $cyclePhase
                                    session = $sessionNum
                                    source = "PostToolUse"
                                } | ConvertTo-Json -Compress

                                Add-Content -Path $eventsPath -Value $event
                                Write-Host "[CYCLE] $backlogId : $fromPhase -> $cyclePhase" -ForegroundColor Magenta
                            }
                        }
                    } catch {
                        # Silent fail - cycle events are advisory only
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