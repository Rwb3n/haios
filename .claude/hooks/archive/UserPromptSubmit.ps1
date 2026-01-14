# generated: 2025-12-05
# System Auto: last updated on: 2025-12-18 21:39:45
# last updated on: 2025-12-05 22:17:00
# UserPromptSubmit Hook - Date/Time + Memory Context + Lifecycle + Governance
#
# DESCRIPTION:
#   1. Adds the current day, date, and time as context
#   2. Automatically retrieves relevant memory context (Session 32: ReasoningBank Integration)
#   3. Enforces lifecycle sequence (Session 63: E2-009) - guides agents to complete discovery before planning
#   4. RFC 2119 governance reminders (Session 67: E2-037) - injects MUST guidance for discoveries, SQL, closures
#   This makes memory injection AUTOMATIC, not optional (per Session 31 architectural decision)
#
# HOOK EVENT: UserPromptSubmit
#   Runs when the user submits a prompt, before Claude processes it.
#   The stdout output is added as context for Claude to see.
#
# JSON INPUT FORMAT:
#   {
#     "session_id": "...",
#     "transcript_path": "...",
#     "cwd": "...",
#     "hook_event_name": "UserPromptSubmit",
#     "prompt": "user's prompt text"
#   }

# Read JSON input from stdin
$jsonInput = [Console]::In.ReadToEnd()

try {
    # Parse the JSON input
    $hookData = $jsonInput | ConvertFrom-Json

    # === PART 1: Date/Time Context ===
    $currentDateTime = Get-Date
    $dateTime = $currentDateTime.ToString("yyyy-MM-dd h:mm tt")
    $dayOfWeek = $currentDateTime.DayOfWeek
    $contextMessage = "Today is $dayOfWeek, $dateTime"

    # Output date/time context
    Write-Output $contextMessage

    # === PART 1.5: HAIOS Vitals Injection (E2-076d) ===
    # Compact infrastructure awareness (~50 tokens)
    $cwd = $hookData.cwd
    $slimPath = Join-Path $cwd ".claude\haios-status-slim.json"

    if ($cwd -and (Test-Path $slimPath)) {
        try {
            $slim = Get-Content $slimPath -Raw | ConvertFrom-Json

            # Build vitals block
            $vitals = @()
            $vitals += "--- HAIOS Vitals ---"

            # Milestone with progress and delta
            if ($slim.milestone) {
                $milestoneStr = "$($slim.milestone.id) ($($slim.milestone.progress)%)"
                if ($slim.milestone.delta_source -and $slim.milestone.progress -gt $slim.milestone.prior_progress) {
                    $delta = $slim.milestone.progress - $slim.milestone.prior_progress
                    $milestoneStr += " [+$delta from $($slim.milestone.delta_source)]"
                }
                $vitals += "Milestone: $milestoneStr"
            }

            # Session delta (E2-078): Momentum awareness
            if ($slim.session_delta -and $slim.session_delta.prior_session) {
                $deltaStr = "Since S$($slim.session_delta.prior_session):"
                $deltaParts = @()
                if ($slim.session_delta.completed_count -gt 0) {
                    $deltaParts += "+$($slim.session_delta.completed_count) done"
                }
                if ($slim.session_delta.added_count -gt 0) {
                    $deltaParts += "+$($slim.session_delta.added_count) new"
                }
                if ($slim.session_delta.milestone_delta) {
                    $deltaParts += "$($slim.session_delta.milestone_delta)"
                }
                if ($deltaParts.Count -gt 0) {
                    $deltaStr += " " + ($deltaParts -join ", ")
                    $vitals += $deltaStr
                }
            }

            # Active work (top 5)
            if ($slim.active_work -and $slim.active_work.Count -gt 0) {
                $activeStr = ($slim.active_work | Select-Object -First 5) -join ", "
                $vitals += "Active: $activeStr"
            }

            # Blocked items (top 3)
            if ($slim.blocked_items -and $slim.blocked_items.Count -gt 0) {
                $blockedList = @()
                foreach ($item in ($slim.blocked_items | Select-Object -First 3)) {
                    $blockerStr = ($item.blocked_by -join ",")
                    $blockedList += "$($item.id)[$blockerStr]"
                }
                $vitals += "Blocked: $($blockedList -join ', ')"
            }

            # Infrastructure summary
            if ($slim.infrastructure) {
                # Commands (abbreviated)
                if ($slim.infrastructure.commands) {
                    $vitals += "Commands: /new-*, /close, /validate, /status"
                }
                # Skills
                if ($slim.infrastructure.skills) {
                    $vitals += "Skills: $($slim.infrastructure.skills -join ', ')"
                }
                # Agents
                if ($slim.infrastructure.agents) {
                    $vitals += "Agents: $($slim.infrastructure.agents -join ', ')"
                }
                # MCPs
                if ($slim.infrastructure.mcps) {
                    $mcpList = @()
                    foreach ($mcp in $slim.infrastructure.mcps) {
                        $mcpList += "$($mcp.name)($($mcp.tools))"
                    }
                    $vitals += "MCPs: $($mcpList -join ', ')"
                }
            }

            # Recipes hint
            $vitals += "Recipes: just --list"

            $vitals += "---"

            # Output vitals
            Write-Output ""
            Write-Output ($vitals -join "`n")

        } catch {
            # Silent fail - continue without vitals
        }
    }

    # === PART 1.6: Dynamic Thresholds (E2-082) ===
    # Inject urgency signals when system state crosses thresholds
    # Uses full haios-status.json for workspace.stale access
    $fullStatusPath = Join-Path $cwd ".claude\haios-status.json"
    if ($cwd -and (Test-Path $fullStatusPath)) {
        try {
            $fullStatus = Get-Content $fullStatusPath -Raw | ConvertFrom-Json
            $thresholdMessages = @()

            # APPROACHING: milestone > 90% but < 100% (100% = complete, not approaching)
            if ($fullStatus.milestones) {
                foreach ($prop in $fullStatus.milestones.PSObject.Properties) {
                    $progress = $prop.Value.progress
                    if ($progress -gt 90 -and $progress -lt 100) {
                        $remaining = $prop.Value.items.Count - $prop.Value.complete.Count
                        $thresholdMessages += "APPROACHING: $($prop.Name) at $progress% - $remaining items to completion"
                    }
                }
            }

            # BOTTLENECK: blocked > 3 (blocked_items is object, not array)
            if ($fullStatus.blocked_items) {
                $blockedCount = ($fullStatus.blocked_items.PSObject.Properties | Measure-Object).Count
                if ($blockedCount -gt 3) {
                    $thresholdMessages += "BOTTLENECK: $blockedCount items blocked - review dependencies"
                }
            }

            # ATTENTION: stale > 5 (path is workspace.stale.items)
            if ($fullStatus.workspace -and $fullStatus.workspace.stale -and $fullStatus.workspace.stale.items) {
                $staleCount = ($fullStatus.workspace.stale.items | Measure-Object).Count
                if ($staleCount -gt 5) {
                    $thresholdMessages += "ATTENTION: $staleCount stale items need review"
                }
            }

            # MOMENTUM: completed > 3 in last session (uses slim for session_delta)
            if ($slim -and $slim.session_delta -and $slim.session_delta.completed_count -gt 3) {
                $thresholdMessages += "MOMENTUM: +$($slim.session_delta.completed_count) items completed since S$($slim.session_delta.prior_session) - great progress!"
            }

            # Output threshold messages (after vitals block)
            if ($thresholdMessages.Count -gt 0) {
                foreach ($msg in $thresholdMessages) {
                    Write-Output $msg
                }
                Write-Output "---"
            }
        } catch {
            # Silent fail - continue without thresholds
        }
    }

    # === PART 2: Memory Context Injection ===
    # DISABLED Session 75 (E2-076d): Replaced by L1 Vitals injection.
    # Memory strategies remain in database for on-demand query via memory-agent skill.
    # Re-enable selectively if needed by uncommenting the block below.
    #
    # Get the user's prompt
    $userPrompt = $hookData.prompt
    #
    # # Only search memory for substantive prompts (not single words or commands)
    # if ($userPrompt -and $userPrompt.Length -gt 10 -and -not $userPrompt.StartsWith("/")) {
    #     # Find the memory retrieval script
    #     $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    #     $pythonScript = Join-Path $scriptDir "memory_retrieval.py"
    #
    #     if (Test-Path $pythonScript) {
    #         # Call Python script with the user prompt
    #         # Use Start-Process to capture output without blocking
    #         try {
    #             $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    #             $pinfo.FileName = "python"
    #             $pinfo.Arguments = "`"$pythonScript`" `"$userPrompt`""
    #             $pinfo.RedirectStandardOutput = $true
    #             $pinfo.RedirectStandardError = $true
    #             $pinfo.UseShellExecute = $false
    #             $pinfo.CreateNoWindow = $true
    #             $pinfo.WorkingDirectory = $scriptDir
    #
    #             $process = New-Object System.Diagnostics.Process
    #             $process.StartInfo = $pinfo
    #
    #             # Set timeout (8 seconds for memory retrieval)
    #             # Note: Script takes ~4s but process startup adds overhead
    #             # 5s was causing timeouts; increased to 8s (Session 35 fix)
    #             $timeout = 8000
    #
    #             $process.Start() | Out-Null
    #
    #             # Read output with timeout
    #             if ($process.WaitForExit($timeout)) {
    #                 $memoryOutput = $process.StandardOutput.ReadToEnd()
    #
    #                 if ($memoryOutput -and $memoryOutput.Trim().Length -gt 0) {
    #                     Write-Output ""
    #                     Write-Output $memoryOutput.Trim()
    #                 }
    #             }
    #             # If timeout, silently continue without memory (fail graceful)
    #
    #         } catch {
    #             # Silent fail - don't break the workflow if memory retrieval fails
    #         }
    #     }
    # }

    # === PART 3: Lifecycle Sequence Enforcement (E2-009, Session 63) ===
    # Detect plan-creation intent and check for prerequisite discovery/design documents
    # Soft enforcement: inject guidance, don't block

    if ($userPrompt) {
        # Check for override first
        $hasOverride = $userPrompt -match "skip discovery|skip investigation|trivial|quick fix"

        if (-not $hasOverride) {
            # Detect plan-creation intent
            $planIntent = $userPrompt -match "/new-plan|create.*plan|implement.*feature|add.*feature|build.*feature|start.*implement"

            # Also detect direct implementation intent for significant work
            $implIntent = $userPrompt -match "implement\s+E2-|implement\s+INV-|implement\s+TD-"

            if ($planIntent -or $implIntent) {
                # Try to extract backlog ID from prompt (E2-xxx, INV-xxx, TD-xxx)
                # E2-036: Updated regex to support E2-FIX-XXX format
                $backlogMatch = [regex]::Match($userPrompt, "(E2-[A-Z]*-?\d{3}|INV-\d{3}|TD-\d{3})")

                if ($backlogMatch.Success) {
                    $backlogId = $backlogMatch.Value

                    # Check for prerequisite documents
                    $cwd = $hookData.cwd
                    $hasDiscovery = $false
                    $hasDesign = $false

                    # Check docs/investigations/ for INVESTIGATION-<backlog_id>-*
                    $invPath = Join-Path $cwd "docs/investigations"
                    if (Test-Path $invPath) {
                        $invFiles = Get-ChildItem -Path $invPath -Filter "INVESTIGATION-$backlogId-*.md" -ErrorAction SilentlyContinue
                        if ($invFiles -and $invFiles.Count -gt 0) {
                            $hasDiscovery = $true
                        }
                    }

                    # Also check legacy docs/handoff/ for investigation-type files
                    $handoffPath = Join-Path $cwd "docs/handoff"
                    if ((-not $hasDiscovery) -and (Test-Path $handoffPath)) {
                        $handoffFiles = Get-ChildItem -Path $handoffPath -Filter "*INVESTIGATION*$backlogId*.md" -ErrorAction SilentlyContinue
                        if ($handoffFiles -and $handoffFiles.Count -gt 0) {
                            $hasDiscovery = $true
                        }
                    }

                    # Check docs/ADR/ for related ADR
                    $adrPath = Join-Path $cwd "docs/ADR"
                    if (Test-Path $adrPath) {
                        # Read haios-status.json to find ADRs linked to this backlog_id
                        $statusPath = Join-Path $cwd ".claude/haios-status.json"
                        if (Test-Path $statusPath) {
                            try {
                                $statusJson = Get-Content $statusPath -Raw | ConvertFrom-Json
                                $workItem = $statusJson.work_items.PSObject.Properties | Where-Object { $_.Name -eq $backlogId }
                                if ($workItem -and $workItem.Value.adrs -and $workItem.Value.adrs.Count -gt 0) {
                                    $hasDesign = $true
                                }
                            } catch {
                                # Silent fail - continue without status check
                            }
                        }
                    }

                    # If neither discovery nor design exists, inject guidance
                    if ((-not $hasDiscovery) -and (-not $hasDesign)) {
                        Write-Output ""
                        Write-Output "--- Lifecycle Guidance (ADR-034) ---"
                        Write-Output "No discovery/design document found for $backlogId."
                        Write-Output "Consider creating an INVESTIGATION-* to analyze the problem first."
                        Write-Output "Command: /new-investigation $backlogId <title>"
                        Write-Output "Override: Include 'skip discovery' in your message to proceed."
                        Write-Output "--- End Lifecycle Guidance ---"
                    }
                }
            }
        }
    }

    # === PART 4: RFC 2119 Governance Reminders (E2-037, Session 67) ===
    # Detect trigger keywords and inject MUST guidance
    # Design: Only MUST tier initially. SHOULD tier may be too noisy.
    # Override: Include "skip reminder" in message to bypass

    if ($userPrompt -and -not ($userPrompt -match "skip reminder")) {

        # MUST: Discovery -> /new-investigation
        # Trigger: discovery keywords + action keywords (reduces false positives)
        $discoveryTrigger = ($userPrompt -match "(bug|issue|gap|problem|broken|wrong|error)") -and
                           ($userPrompt -match "(found|discovered|noticed|identified|see|seeing)")
        if ($discoveryTrigger) {
            Write-Output ""
            Write-Output "--- RFC 2119 Governance (MUST) ---"
            Write-Output "Discovery detected. MUST use /new-investigation to document before fixing."
            Write-Output "Command: /new-investigation <backlog_id> <title>"
            Write-Output "Override: Include 'skip reminder' in your message."
            Write-Output "--- End Governance Reminder ---"
        }

        # MUST: SQL -> schema-verifier
        # Trigger: SQL action words or SQL keywords
        $sqlTrigger = ($userPrompt -match "(run|execute|write|check|query).*(sql|query|database)") -or
                      ($userPrompt -match "(select|insert|update|delete)\s+(from|into)")
        if ($sqlTrigger) {
            Write-Output ""
            Write-Output "--- RFC 2119 Governance (MUST) ---"
            Write-Output "SQL intent detected. MUST use schema-verifier subagent first."
            Write-Output "Command: Task(prompt='...', subagent_type='schema-verifier')"
            Write-Output "Override: Include 'skip reminder' in your message."
            Write-Output "--- End Governance Reminder ---"
        }

        # MUST: Close -> /close (E2-036 corrected regex)
        # Trigger: closure keywords + backlog ID
        $closeTrigger = $userPrompt -match "(close|complete|finish|done|mark).*(E2-[A-Z]*-?\d{3}|INV-\d{3}|TD-\d{3})"
        if ($closeTrigger) {
            $closeBacklogMatch = [regex]::Match($userPrompt, "(E2-[A-Z]*-?\d{3}|INV-\d{3}|TD-\d{3})")
            if ($closeBacklogMatch.Success) {
                Write-Output ""
                Write-Output "--- RFC 2119 Governance (MUST) ---"
                Write-Output "Work item closure detected. MUST use /close to validate DoD."
                Write-Output "Command: /close $($closeBacklogMatch.Value)"
                Write-Output "Override: Include 'skip reminder' in your message."
                Write-Output "--- End Governance Reminder ---"
            }
        }
    }

    # Exit successfully
    exit 0

} catch {
    # Silent fail - still output date/time if parsing fails
    try {
        $currentDateTime = Get-Date
        $dateTime = $currentDateTime.ToString("yyyy-MM-dd h:mm tt")
        Write-Output "Today is $($currentDateTime.DayOfWeek), $dateTime"
    } catch {}
    exit 0
}
