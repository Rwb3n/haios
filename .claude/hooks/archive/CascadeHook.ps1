# generated: 2025-12-16
# System Auto: last updated on: 2025-12-17 22:14:26
# CascadeHook.ps1
# Heartbeat mechanism - propagates status changes through dependency graph
#
# TRIGGERS:
#   - Plan status: complete/completed/done
#   - ADR status: accepted
#   - Investigation status: complete
#
# CASCADE TYPES:
#   1. UNBLOCK - Items blocked by completed item, check if now ready
#   2. RELATED - Items related to completed item, may need review
#   3. MILESTONE - Recalculate milestone progress
#   4. SUBSTANTIVE - CLAUDE.md/README references need update
#   5. REVIEW_PROMPT - Stale unblocked plans need review
#
# USAGE:
#   powershell.exe -ExecutionPolicy Bypass -Command "& '.claude/hooks/CascadeHook.ps1' -FilePath 'path' -BacklogId 'E2-xxx' -NewStatus 'complete'"
#
# VERSION: 1.0
# SESSION: 81
# PLAN: E2-076e

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath,

    [Parameter(Mandatory=$true)]
    [string]$BacklogId,

    [Parameter(Mandatory=$true)]
    [string]$NewStatus,

    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$statusFile = Join-Path $projectRoot ".claude\haios-status.json"
$eventsFile = Join-Path $projectRoot ".claude\haios-events.jsonl"

# ============================================================================
# HELPER: Load haios-status.json
# ============================================================================
function Get-HaiosStatus {
    if (Test-Path $statusFile) {
        try {
            return Get-Content $statusFile -Raw | ConvertFrom-Json
        } catch {
            return $null
        }
    }
    return $null
}

# ============================================================================
# HELPER: Check if a backlog item is complete
# ============================================================================
function Test-ItemComplete {
    param([string]$ItemId)

    # Check plan files
    $planPattern = Join-Path $projectRoot "docs\plans\PLAN-$ItemId*.md"
    $planFiles = Get-ChildItem -Path $planPattern -ErrorAction SilentlyContinue
    foreach ($plan in $planFiles) {
        $content = Get-Content $plan.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -match 'status:\s*(complete|completed|done|closed)') {
            return $true
        }
    }

    # Check backlog for CLOSED
    $backlogPath = Join-Path $projectRoot "docs\pm\backlog.md"
    if (Test-Path $backlogPath) {
        $backlogContent = Get-Content $backlogPath -Raw
        if ($backlogContent -match "\[CLOSED\].*$ItemId|$ItemId.*\[CLOSED\]") {
            return $true
        }
    }

    return $false
}

# ============================================================================
# CASCADE 1: UNBLOCK - Find items that were blocked by completed item
# ============================================================================
function Get-UnblockedItems {
    param([string]$CompletedId)

    $results = @()
    $planPath = Join-Path $projectRoot "docs\plans"

    if (-not (Test-Path $planPath)) { return $results }

    $planFiles = Get-ChildItem -Path $planPath -Filter "*.md" -File -ErrorAction SilentlyContinue
    foreach ($file in $planFiles) {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }

        # Parse YAML frontmatter
        if ($content -match '^---\s*\r?\n([\s\S]*?)\r?\n---') {
            $yaml = $Matches[1]

            # Check if has blocked_by containing our completed ID
            if ($yaml -match 'blocked_by:\s*\[([^\]]+)\]') {
                $blockedByStr = $Matches[1]
                $blockers = $blockedByStr -split ',' | ForEach-Object { $_.Trim().Trim('"', "'") }

                # Only process if this item was blocked by our completed item
                if ($CompletedId -notin $blockers) { continue }

                # Get this item's ID and status
                $itemId = if ($yaml -match 'backlog_id:\s*(\S+)') { $Matches[1].Trim() } else { $null }
                $itemStatus = if ($yaml -match 'status:\s*(\S+)') { $Matches[1].Trim() } else { "unknown" }

                if (-not $itemId) { continue }

                # Skip if already complete
                if ($itemStatus -in @("complete", "completed", "done", "closed")) { continue }

                # Check if ALL blockers are now complete
                $remainingBlockers = @()
                foreach ($blocker in $blockers) {
                    if (-not $blocker) { continue }
                    if ($blocker -eq $CompletedId) { continue }  # This one is now complete

                    if (-not (Test-ItemComplete -ItemId $blocker)) {
                        $remainingBlockers += $blocker
                    }
                }

                # Get last updated session for review prompt
                $lastSession = if ($yaml -match 'session:\s*(\d+)') { [int]$Matches[1] } else { 0 }

                if ($remainingBlockers.Count -eq 0) {
                    $results += @{
                        id = $itemId
                        status = "READY"
                        message = "$itemId is now READY (was blocked_by: $CompletedId)"
                        last_session = $lastSession
                    }
                } else {
                    $results += @{
                        id = $itemId
                        status = "STILL_BLOCKED"
                        remaining = $remainingBlockers
                        message = "$itemId still blocked by [$($remainingBlockers -join ', ')]"
                        last_session = $lastSession
                    }
                }
            }
        }
    }

    return $results
}

# ============================================================================
# CASCADE 2: RELATED - Find items with bidirectional related relationship
# Session 82: Fixed to check BOTH directions of related arrays
# ============================================================================
function Get-RelatedItems {
    param([string]$CompletedId)

    $results = @()
    $seenIds = @{}  # Prevent duplicates
    $planPath = Join-Path $projectRoot "docs\plans"

    if (-not (Test-Path $planPath)) { return $results }

    $planFiles = Get-ChildItem -Path $planPath -Filter "*.md" -File -ErrorAction SilentlyContinue

    # DIRECTION 1: Find items that list CompletedId in THEIR related array
    foreach ($file in $planFiles) {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }

        if ($content -match '^---\s*\r?\n([\s\S]*?)\r?\n---') {
            $yaml = $Matches[1]

            if ($yaml -match 'related:\s*\[([^\]]+)\]') {
                $relatedStr = $Matches[1]
                $relatedItems = $relatedStr -split ',' | ForEach-Object { $_.Trim().Trim('"', "'") }

                if ($CompletedId -in $relatedItems) {
                    $itemId = if ($yaml -match 'backlog_id:\s*(\S+)') { $Matches[1].Trim() } else { $null }
                    $itemStatus = if ($yaml -match 'status:\s*(\S+)') { $Matches[1].Trim() } else { "unknown" }

                    if ($itemId -and $itemId -ne $CompletedId -and $itemStatus -notin @("complete", "completed", "done", "closed")) {
                        if (-not $seenIds.ContainsKey($itemId)) {
                            $seenIds[$itemId] = $true
                            $results += @{
                                id = $itemId
                                direction = "inbound"
                                reason = "lists $CompletedId in its related array"
                            }
                        }
                    }
                }
            }
        }
    }

    # DIRECTION 2: Find items that CompletedId lists in ITS related array
    $completedPlanPattern = Join-Path $planPath "PLAN-$CompletedId*.md"
    $completedPlanFiles = Get-ChildItem -Path $completedPlanPattern -ErrorAction SilentlyContinue

    foreach ($completedPlan in $completedPlanFiles) {
        $content = Get-Content $completedPlan.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }

        if ($content -match '^---\s*\r?\n([\s\S]*?)\r?\n---') {
            $yaml = $Matches[1]

            if ($yaml -match 'related:\s*\[([^\]]+)\]') {
                $relatedStr = $Matches[1]
                $relatedIds = $relatedStr -split ',' | ForEach-Object { $_.Trim().Trim('"', "'") }

                foreach ($relatedId in $relatedIds) {
                    if (-not $relatedId -or $relatedId -eq $CompletedId) { continue }
                    if ($seenIds.ContainsKey($relatedId)) { continue }

                    # Check if this related item exists and is active
                    # Use exact pattern with separator to avoid E2-076 matching E2-076d
                    $relatedPlanPattern = Join-Path $planPath "PLAN-$relatedId-*.md"
                    $relatedPlanFiles = Get-ChildItem -Path $relatedPlanPattern -ErrorAction SilentlyContinue

                    # Also check for exact match (PLAN-E2-076.md)
                    $exactPattern = Join-Path $planPath "PLAN-$relatedId.md"
                    $exactFile = Get-ChildItem -Path $exactPattern -ErrorAction SilentlyContinue
                    if ($exactFile) {
                        $relatedPlanFiles = @($relatedPlanFiles) + @($exactFile)
                    }

                    foreach ($relatedPlan in $relatedPlanFiles) {
                        $relatedContent = Get-Content $relatedPlan.FullName -Raw -ErrorAction SilentlyContinue
                        if (-not $relatedContent) { continue }

                        if ($relatedContent -match '^---\s*\r?\n([\s\S]*?)\r?\n---') {
                            $relatedYaml = $Matches[1]
                            $relatedStatus = if ($relatedYaml -match 'status:\s*(\S+)') { $Matches[1].Trim() } else { "unknown" }

                            if ($relatedStatus -notin @("complete", "completed", "done", "closed")) {
                                $seenIds[$relatedId] = $true
                                $results += @{
                                    id = $relatedId
                                    direction = "outbound"
                                    reason = "$CompletedId listed it in related array"
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    return $results
}

# ============================================================================
# CASCADE 3: MILESTONE - Calculate progress delta
# ============================================================================
function Get-MilestoneDelta {
    param(
        [string]$CompletedId,
        [PSObject]$HaiosStatus
    )

    if (-not $HaiosStatus -or -not $HaiosStatus.milestones) { return $null }

    # Find which milestone contains this item
    foreach ($prop in $HaiosStatus.milestones.PSObject.Properties) {
        $milestone = $prop.Value
        $items = @($milestone.items)

        if ($CompletedId -in $items) {
            $priorProgress = if ($milestone.prior_progress) { $milestone.prior_progress } else { 0 }
            $currentProgress = if ($milestone.progress) { $milestone.progress } else { 0 }

            # Calculate new progress (item is now complete)
            $completeItems = @($milestone.complete)
            if ($CompletedId -notin $completeItems) {
                $completeItems += $CompletedId
            }
            $totalItems = $items.Count
            $newProgress = if ($totalItems -gt 0) { [math]::Round(($completeItems.Count / $totalItems) * 100) } else { 0 }

            return @{
                milestone = $prop.Name
                name = $milestone.name
                old = $currentProgress
                new = $newProgress
                delta = $newProgress - $currentProgress
            }
        }
    }

    return $null
}

# ============================================================================
# CASCADE 4: SUBSTANTIVE - Check CLAUDE.md and READMEs for references
# ============================================================================
function Get-SubstantiveReferences {
    param([string]$CompletedId)

    $results = @()

    # Files to check for substantive references
    $checkFiles = @(
        (Join-Path $projectRoot "CLAUDE.md"),
        (Join-Path $projectRoot "README.md"),
        (Join-Path $projectRoot "docs\README.md")
    )

    foreach ($file in $checkFiles) {
        if (Test-Path $file) {
            $content = Get-Content $file -Raw -ErrorAction SilentlyContinue
            if ($content -and $content -match $CompletedId) {
                # Check if reference is in body (not just frontmatter)
                $relativePath = $file.Replace($projectRoot, "").TrimStart("\", "/")
                $results += @{
                    file = $relativePath
                    type = "substantive"
                    message = "$relativePath references $CompletedId -> Consider update"
                }
            }
        }
    }

    return $results
}

# ============================================================================
# CASCADE 5: REVIEW PROMPT - Stale unblocked plans
# ============================================================================
function Get-ReviewPrompts {
    param(
        [array]$UnblockedItems,
        [int]$CurrentSession
    )

    $results = @()
    $staleThreshold = 3  # Sessions since last update = extra urgency

    foreach ($item in $UnblockedItems) {
        # ALL READY items get review prompt - blocker implementation may have changed landscape
        if ($item.status -eq "READY") {
            $sessionsSinceUpdate = 0
            $urgency = ""

            if ($item.last_session -gt 0) {
                $sessionsSinceUpdate = $CurrentSession - $item.last_session
                if ($sessionsSinceUpdate -ge $staleThreshold) {
                    $urgency = " (STALE: $sessionsSinceUpdate sessions ago)"
                }
            }

            $results += @{
                id = $item.id
                last_session = $item.last_session
                sessions_ago = $sessionsSinceUpdate
                message = "SHOULD review $($item.id) before implementation - blocker work may affect plan$urgency"
            }
        }
    }

    return $results
}

# ============================================================================
# FORMAT: Build cascade message
# ============================================================================
function Format-CascadeMessage {
    param(
        [string]$CompletedId,
        [string]$NewStatus,
        [array]$UnblockedItems,
        [array]$RelatedItems,
        [hashtable]$MilestoneDelta,
        [array]$SubstantiveRefs,
        [array]$ReviewPrompts
    )

    $lines = @()
    $lines += "--- Cascade (Heartbeat) ---"
    $lines += "$CompletedId status: $NewStatus"
    $lines += ""

    $effects = @()

    # UNBLOCK section - wrap in @() to ensure array even with single item
    $readyItems = @($UnblockedItems | Where-Object { $_.status -eq "READY" })
    $stillBlocked = @($UnblockedItems | Where-Object { $_.status -eq "STILL_BLOCKED" })

    if ($readyItems.Count -gt 0 -or $stillBlocked.Count -gt 0) {
        $lines += "[UNBLOCK]"
        foreach ($item in $readyItems) {
            $lines += "  - $($item.message)"
            $effects += "unblock:$($item.id)"
        }
        foreach ($item in $stillBlocked) {
            $lines += "  - $($item.message)"
        }
        $lines += ""
    }

    # REVIEW PROMPT section
    if ($ReviewPrompts.Count -gt 0) {
        $lines += "[REVIEW PROMPT]"
        foreach ($item in $ReviewPrompts) {
            $lines += "  - $($item.message)"
        }
        $lines += ""
    }

    # RELATED section - Session 82: Strengthened to MUST review
    if ($RelatedItems.Count -gt 0) {
        $lines += "[RELATED - REVIEW REQUIRED]"
        $lines += "  Implementation may have drifted from plan. MUST review for:"
        $lines += "    - Scope overlap (did completed work partially fulfill this?)"
        $lines += "    - Changed assumptions (does completed work affect approach?)"
        $lines += "    - New patterns (should this follow patterns established?)"
        $lines += ""
        foreach ($item in $RelatedItems) {
            $directionLabel = if ($item.direction -eq "outbound") { "outbound" } else { "inbound" }
            $lines += "  [$directionLabel] $($item.id)"
            $lines += "    Reason: $($item.reason)"
        }
        $lines += ""
        $effects += "related:$($RelatedItems.Count)"
    }

    # MILESTONE section
    if ($MilestoneDelta -and $MilestoneDelta.delta -gt 0) {
        $lines += "[MILESTONE]"
        $lines += "  - $($MilestoneDelta.name): $($MilestoneDelta.old)% -> $($MilestoneDelta.new)% (+$($MilestoneDelta.delta)%)"
        $effects += "milestone:+$($MilestoneDelta.delta)"
        $lines += ""
    }

    # SUBSTANTIVE section
    if ($SubstantiveRefs.Count -gt 0) {
        $lines += "[SUBSTANTIVE]"
        foreach ($ref in $SubstantiveRefs) {
            $lines += "  - $($ref.message)"
        }
        $lines += ""
    }

    # Next action
    if ($readyItems.Count -gt 0) {
        $nextItem = $readyItems[0].id
        $lines += "Action: $nextItem is next in sequence."
    } elseif ($UnblockedItems.Count -eq 0 -and $RelatedItems.Count -eq 0) {
        $lines += "No dependents affected."
    }

    $lines += "--- End Cascade ---"

    return @{
        message = $lines -join "`n"
        effects = $effects
    }
}

# ============================================================================
# EVENT LOGGING (E2-081 Integration)
# ============================================================================
function Write-CascadeEvent {
    param(
        [string]$SourceId,
        [array]$Effects
    )

    $event = @{
        ts = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        type = "cascade"
        source = $SourceId
        effects = $Effects
    }

    $eventJson = $event | ConvertTo-Json -Compress
    Add-Content -Path $eventsFile -Value $eventJson -Encoding UTF8
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

# Only trigger on completion statuses
$triggerStatuses = @("complete", "completed", "done", "closed", "accepted")
if ($NewStatus.ToLower() -notin $triggerStatuses) {
    if ($Verbose) { Write-Host "Status '$NewStatus' does not trigger cascade" }
    exit 0
}

# Load current status
$haiosStatus = Get-HaiosStatus

# Get current session number from PM
$currentSession = 81  # Default
if ($haiosStatus -and $haiosStatus.pm -and $haiosStatus.pm.last_session) {
    $currentSession = $haiosStatus.pm.last_session
}

# Run all cascade checks
$unblockedItems = Get-UnblockedItems -CompletedId $BacklogId
$relatedItems = Get-RelatedItems -CompletedId $BacklogId
$milestoneDelta = Get-MilestoneDelta -CompletedId $BacklogId -HaiosStatus $haiosStatus
$substantiveRefs = Get-SubstantiveReferences -CompletedId $BacklogId
$reviewPrompts = Get-ReviewPrompts -UnblockedItems $unblockedItems -CurrentSession $currentSession

# Format message
$result = Format-CascadeMessage `
    -CompletedId $BacklogId `
    -NewStatus $NewStatus `
    -UnblockedItems $unblockedItems `
    -RelatedItems $relatedItems `
    -MilestoneDelta $milestoneDelta `
    -SubstantiveRefs $substantiveRefs `
    -ReviewPrompts $reviewPrompts

# Output cascade message
Write-Output $result.message

# Write event log (E2-081)
if ($result.effects.Count -gt 0 -and -not $DryRun) {
    Write-CascadeEvent -SourceId $BacklogId -Effects $result.effects
}

# Refresh haios-status.json to reflect new state
if (-not $DryRun) {
    $updateScript = Join-Path $PSScriptRoot "UpdateHaiosStatus.ps1"
    if (Test-Path $updateScript) {
        & $updateScript
    }
}
