# generated: 2025-12-07
# System Auto: last updated on: 2025-12-20 21:34:47
# UpdateHaiosStatus.ps1
# Auto-updates .claude/haios-status.json from multiple data sources
#
# DATA SOURCES:
#   1. ValidateTemplate.ps1 - valid template types
#   2. haios-memory MCP - memory statistics (via Python)
#   3. docs/pm/backlog.md - active items and priorities
#   4. Governed paths - live files in lifecycle transit
#
# USAGE:
#   powershell.exe -ExecutionPolicy Bypass -File .claude/hooks/UpdateHaiosStatus.ps1
#
# VERSION: 2.0
# SESSION: 47
# ADR: ADR-030 (Option D - Hybrid Taxonomy), ADR-031 (Operational Self-Awareness)

param(
    [switch]$DryRun,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$statusFile = Join-Path $projectRoot ".claude\haios-status.json"
$slimFile = Join-Path $projectRoot ".claude\haios-status-slim.json"

# Initialize result structure
$status = @{
    hooks = @{
        PreToolUse = @{
            scripts = @("PreToolUse.ps1")
            features = @("governance_enforcement")
        }
        UserPromptSubmit = @{
            scripts = @("UserPromptSubmit.ps1")
            features = @("date_time", "memory_injection")
        }
        PostToolUse = @{
            matcher = "Edit|Write|MultiEdit"
            scripts = @("PostToolUse.ps1", "ValidateTemplateHook.ps1")
            features = @("auto_timestamp", "template_validation")
        }
        Stop = @{
            scripts = @("Stop.ps1")
            features = @("reasoning_extraction")
        }
    }
    auto_features = @{
        timestamps = $true
        validation = $true
        min_references = 2
    }
    valid_templates = @()
    memory = @{
        mcp_server = "haios-memory"
        tools_count = 13
    }
    skills = @()  # Populated by Get-Skills
    agents = @()  # Populated by Get-Agents
    commands = @()  # Populated by Get-Commands
    pm = @{
        backlog_path = "docs/pm/backlog.md"
        active_count = 0
        last_session = 0
        by_priority = @{
            urgent = 0
            high = 0
            medium = 0
            low = 0
        }
    }
    lifecycle = @{
        live_files = @()
        counts_by_status = @{}
        counts_by_phase = @{}
        alignment_issues = @()
    }
    workspace = @{
        outstanding = @{
            checkpoints = @()
            handoffs = @()
            plans = @()
        }
        stale = @{
            items = @()
        }
        summary = @{
            incomplete_checkpoints = 0
            pending_handoffs = 0
            approved_not_started = 0
            stale_items = 0
        }
    }
    # ADR-036: work_items removed - /close now queries at runtime
    # E2-076d: Milestones - loaded from existing status, then updated
    milestones = @{}
    # E2-110: Spawn tracking - maps parent ID to children spawned
    spawn_map = @{}
    last_updated = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
}

# ============================================================================
# SOURCE 1: Valid Templates from ValidateTemplate.ps1
# ============================================================================
function Get-ValidTemplates {
    $validatorPath = Join-Path $projectRoot ".claude\hooks\ValidateTemplate.ps1"
    if (Test-Path $validatorPath) {
        $content = Get-Content $validatorPath -Raw
        # Extract template names - look for "name" = @{ pattern
        $templateMatches = [regex]::Matches($content, '^\s*"([a-z_]+)"\s*=\s*@\{', [System.Text.RegularExpressions.RegexOptions]::Multiline)
        $templates = @()
        foreach ($match in $templateMatches) {
            $templates += $match.Groups[1].Value
        }
        return $templates | Sort-Object -Unique
    }
    return @()
}

# ============================================================================
# SOURCE 1b: Agents Discovery from .claude/agents/
# ============================================================================
function Get-Agents {
    $agentsDir = Join-Path $projectRoot ".claude\agents"
    $agents = @()

    if (Test-Path $agentsDir) {
        $agentFiles = Get-ChildItem -Path $agentsDir -Filter "*.md" -File -ErrorAction SilentlyContinue
        foreach ($file in $agentFiles) {
            # Skip README
            if ($file.Name -eq "README.md") { continue }

            $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
            if ($content -and $content -match '(?s)^---\s*\r?\n.*?name:\s*([^\r\n]+)') {
                $agentName = $Matches[1].Trim()
                if ($agentName) {
                    $agents += $agentName
                }
            }
        }
    }

    return $agents | Sort-Object
}

# ============================================================================
# SOURCE 1c: Commands Discovery from .claude/commands/
# ============================================================================
function Get-Commands {
    $commandsDir = Join-Path $projectRoot ".claude\commands"
    $commands = @()

    if (Test-Path $commandsDir) {
        $commandFiles = Get-ChildItem -Path $commandsDir -Filter "*.md" -File -ErrorAction SilentlyContinue
        foreach ($file in $commandFiles) {
            # Skip README
            if ($file.Name -eq "README.md") { continue }

            # Command name is filename without extension, prefixed with /
            $cmdName = "/" + $file.BaseName
            $commands += $cmdName
        }
    }

    return $commands | Sort-Object
}

# ============================================================================
# SOURCE 1d: Skills Discovery from .claude/skills/
# ============================================================================
function Get-Skills {
    $skillsDir = Join-Path $projectRoot ".claude\skills"
    $skills = @()

    if (Test-Path $skillsDir) {
        $skillDirs = Get-ChildItem -Path $skillsDir -Directory -ErrorAction SilentlyContinue
        foreach ($dir in $skillDirs) {
            $skillFile = Join-Path $dir.FullName "SKILL.md"
            if (Test-Path $skillFile) {
                $content = Get-Content $skillFile -Raw -ErrorAction SilentlyContinue
                if ($content -and $content -match '(?s)^---\s*\r?\n.*?name:\s*([^\r\n]+)') {
                    $skillName = $Matches[1].Trim()
                    if ($skillName) {
                        $skills += $skillName
                    }
                }
            }
        }
    }

    return $skills | Sort-Object
}

# ============================================================================
# SOURCE 2: Memory Stats via Python subprocess
# ============================================================================
function Get-MemoryStats {
    try {
        $dbPath = Join-Path $projectRoot "haios_memory.db"
        $pythonCmd = "import sys; sys.path.insert(0, r'$projectRoot'); from haios_etl.database import DatabaseManager; db = DatabaseManager(r'$dbPath'); stats = db.get_stats(); import json; print(json.dumps(stats))"
        $result = & python -c $pythonCmd 2>$null
        if ($result) {
            return $result | ConvertFrom-Json
        }
    } catch {
        if ($Verbose) { Write-Host "Memory stats unavailable: $_" -ForegroundColor Yellow }
    }
    return $null
}

# ============================================================================
# SOURCE 3: Backlog Analysis
# ============================================================================
function Get-BacklogStats {
    $backlogPath = Join-Path $projectRoot "docs\pm\backlog.md"
    $stats = @{
        active_count = 0
        last_session = 0
        by_priority = @{ urgent = 0; high = 0; medium = 0; low = 0 }
        items = @()
    }

    if (Test-Path $backlogPath) {
        $content = Get-Content $backlogPath -Raw

        # Count by priority
        $stats.by_priority.urgent = ([regex]::Matches($content, '\[URGENT\]')).Count
        $stats.by_priority.high = ([regex]::Matches($content, '\[HIGH\]')).Count
        $stats.by_priority.medium = ([regex]::Matches($content, '\[MEDIUM\]')).Count
        $stats.by_priority.low = ([regex]::Matches($content, '\[LOW\]')).Count

        # Total active (non-closed)
        $closedCount = ([regex]::Matches($content, '\[CLOSED\]')).Count
        $totalItems = $stats.by_priority.urgent + $stats.by_priority.high + $stats.by_priority.medium + $stats.by_priority.low
        $stats.active_count = $totalItems - $closedCount

        # Extract session numbers
        $sessionMatches = [regex]::Matches($content, 'Session[:\s]*(\d+)')
        if ($sessionMatches.Count -gt 0) {
            $sessions = $sessionMatches | ForEach-Object { [int]$_.Groups[1].Value }
            $stats.last_session = ($sessions | Measure-Object -Maximum).Maximum
        }

        # Extract backlog IDs for alignment checking
        # E2-036: Support E2-FIX-XXX format in addition to E2-XXX
        $idMatches = [regex]::Matches($content, '(E2-[A-Z]*-?\d{3}|TD-\d{3}|INV-\d{3})')
        $stats.items = $idMatches | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique
    }

    return $stats
}

# ============================================================================
# SOURCE 4: Live Files Scan
# ============================================================================
function Get-LiveFiles {
    $governedPaths = @(
        "docs\checkpoints"
        "docs\plans"
        "docs\ADR"
        "docs\reports"
        "docs\handoff"
    )

    $liveFiles = @()
    $statusCounts = @{}
    $phaseCounts = @{
        observe = 0
        capture = 0
        decide = 0
        plan = 0
        verify = 0
        complete = 0
        untagged = 0
    }

    foreach ($relPath in $governedPaths) {
        $fullPath = Join-Path $projectRoot $relPath
        if (Test-Path $fullPath) {
            $files = Get-ChildItem -Path $fullPath -Filter "*.md" -File -ErrorAction SilentlyContinue
            foreach ($file in $files) {
                # Skip README files
                if ($file.Name -eq "README.md") { continue }

                $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
                if (-not $content) { continue }

                # Parse YAML front matter
                if ($content -match '^---\s*\r?\n([\s\S]*?)\r?\n---') {
                    $yaml = $Matches[1]

                    $template = if ($yaml -match 'template:\s*(.+)') { $Matches[1].Trim() } else { "unknown" }
                    $fileStatus = if ($yaml -match 'status:\s*(.+)') { $Matches[1].Trim() } else { "unknown" }
                    $date = if ($yaml -match 'date:\s*(.+)') { $Matches[1].Trim() } else { "" }
                    $phase = if ($yaml -match 'lifecycle_phase:\s*(.+)') { $Matches[1].Trim() } else { "" }
                    # E2-015: Parse backlog_id from YAML frontmatter (not filename)
                    # E2-036: Support E2-FIX-XXX format in addition to E2-XXX
                    $backlogId = if ($yaml -match 'backlog_id:\s*(E2-[A-Z]*-?\d{3})') { $Matches[1].Trim() } else { $null }

                    # Skip completed/archived files (only track truly live files)
                    $terminalStatuses = @("completed", "archived", "done", "complete", "closed", "final")
                    if ($terminalStatuses -contains $fileStatus.ToLower()) { continue }

                    # Count by status
                    if (-not $statusCounts.ContainsKey($fileStatus)) {
                        $statusCounts[$fileStatus] = 0
                    }
                    $statusCounts[$fileStatus]++

                    # Count by lifecycle phase
                    if ($phase -and $phaseCounts.ContainsKey($phase)) {
                        $phaseCounts[$phase]++
                    } elseif (-not $phase) {
                        $phaseCounts["untagged"]++
                    }

                    # Build relative path
                    $relativePath = $file.FullName.Replace($projectRoot, "").TrimStart("\", "/")

                    $liveFiles += @{
                        path = $relativePath
                        template = $template
                        status = $fileStatus
                        lifecycle_phase = $phase
                        date = $date
                        backlog_id = $backlogId  # E2-015: From YAML frontmatter
                    }
                }
            }
        }
    }

    return @{
        files = $liveFiles
        counts_by_status = $statusCounts
        counts_by_phase = $phaseCounts
    }
}

# ============================================================================
# SOURCE 5: Outstanding Items (ADR-031)
# Detects unchecked boxes in "Pending Work" sections
# ============================================================================
function Get-OutstandingItems {
    param(
        [string]$FilePath
    )

    $result = @{
        path = $FilePath
        pending_items = @()
    }

    if (-not (Test-Path $FilePath)) { return $result }

    $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
    if (-not $content) { return $result }

    # Look for unchecked items after "Pending Work" or "Pending" section header
    # DD-031-01: Outstanding item = unchecked `- [ ]` in "Pending Work" section
    $inPendingSection = $false
    $lines = $content -split "`n"

    foreach ($line in $lines) {
        # Detect pending section start
        if ($line -match '^#{1,3}\s*(Pending|Pending Work|TODO|Next Steps)') {
            $inPendingSection = $true
            continue
        }

        # Detect next section (exit pending section)
        if ($inPendingSection -and $line -match '^#{1,3}\s+[^#]') {
            $inPendingSection = $false
        }

        # Collect unchecked items in pending section
        if ($inPendingSection -and $line -match '^\s*-\s*\[\s*\]\s*(.+)') {
            $result.pending_items += $Matches[1].Trim()
        }
    }

    return $result
}

# ============================================================================
# SOURCE 6: Stale Items Detection (ADR-031)
# DD-031-02: Stale threshold = 3 days for handoffs, 7 days for plans
# ============================================================================
function Get-StaleItems {
    param(
        [string]$FilePath,
        [string]$Type,
        [int]$ThresholdDays = 3
    )

    $result = @{
        path = $FilePath
        type = $Type
        is_stale = $false
        age_days = 0
        status = ""
    }

    if (-not (Test-Path $FilePath)) { return $result }

    $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
    if (-not $content) { return $result }

    # Parse YAML front matter for date
    if ($content -match '^---\s*\r?\n([\s\S]*?)\r?\n---') {
        $yaml = $Matches[1]
        $dateStr = if ($yaml -match 'date:\s*(\d{4}-\d{2}-\d{2})') { $Matches[1] } else { $null }
        $fileStatus = if ($yaml -match 'status:\s*(.+)') { $Matches[1].Trim() } else { "unknown" }

        $result.status = $fileStatus

        if ($dateStr) {
            try {
                $fileDate = [DateTime]::ParseExact($dateStr, "yyyy-MM-dd", $null)
                $result.age_days = ((Get-Date) - $fileDate).Days

                # Check staleness based on type and threshold
                if ($result.age_days -gt $ThresholdDays) {
                    # Only mark stale if not in terminal status
                    $terminalStatuses = @("completed", "done", "resolved", "closed", "archived", "accepted")
                    if ($terminalStatuses -notcontains $fileStatus.ToLower()) {
                        $result.is_stale = $true
                    }
                }
            } catch {
                # Date parsing failed, not stale
            }
        }
    }

    return $result
}

# ============================================================================
# SOURCE 7: Workspace Summary (ADR-031)
# Aggregates counts from outstanding and stale data
# ============================================================================
function Get-WorkspaceSummary {
    param(
        [hashtable]$WorkspaceData
    )

    $summary = @{
        incomplete_checkpoints = 0
        pending_handoffs = 0
        approved_not_started = 0
        stale_items = 0
    }

    if ($WorkspaceData.outstanding) {
        $summary.incomplete_checkpoints = @($WorkspaceData.outstanding.checkpoints | Where-Object { $_.pending_items.Count -gt 0 }).Count
        $summary.pending_handoffs = @($WorkspaceData.outstanding.handoffs).Count
        $summary.approved_not_started = @($WorkspaceData.outstanding.plans).Count
    }

    if ($WorkspaceData.stale -and $WorkspaceData.stale.items) {
        $summary.stale_items = @($WorkspaceData.stale.items).Count
    }

    return $summary
}

# ============================================================================
# ALIGNMENT CHECK: Match live files to backlog items
# ============================================================================
function Check-Alignment {
    param($liveFiles, $backlogItems)

    $issues = @()

    # Check: Files in decide/plan phase should have backlog items
    foreach ($file in $liveFiles) {
        if ($file.status -in @("proposed", "draft") -or $file.lifecycle_phase -in @("decide", "plan")) {
            # Try to find matching backlog item by filename pattern
            $matched = $false
            foreach ($item in $backlogItems) {
                if ($file.path -match $item) {
                    $file.backlog_id = $item
                    $matched = $true
                    break
                }
            }

            # ADRs in proposed status need tracking
            if (-not $matched -and $file.template -eq "architecture_decision_record" -and $file.status -eq "proposed") {
                $issues += "ADR without backlog: $($file.path)"
            }
        }
    }

    # Check: in_progress backlog items should have corresponding activity
    # (This is informational - not all backlog items need files)

    return $issues
}

# ============================================================================
# SOURCE 8: Work Item Trees - REMOVED (ADR-036)
# /close command now queries documents at runtime via grep
# ============================================================================

# ============================================================================
# SOURCE 9: Milestone Progress Calculation (E2-076d)
# ============================================================================
function Get-MilestoneProgress {
    param(
        [hashtable]$ExistingMilestones
    )

    if (-not $ExistingMilestones) { return @{} }

    $result = @{}
    $backlogPath = Join-Path $projectRoot "docs\pm\backlog.md"
    $backlogContent = ""
    if (Test-Path $backlogPath) {
        $backlogContent = Get-Content $backlogPath -Raw
    }

    foreach ($key in $ExistingMilestones.Keys) {
        $milestone = $ExistingMilestones[$key]
        $items = @($milestone.items)
        $completeItems = @()

        # Check each item's status in backlog.md
        foreach ($item in $items) {
            # Look for [CLOSED] status for this item
            if ($backlogContent -match "$item.*\[CLOSED\]") {
                $completeItems += $item
            }
            # Also check plans for complete status
            $planPattern = Join-Path $projectRoot "docs\plans\PLAN-$item*.md"
            $planFiles = Get-ChildItem -Path $planPattern -ErrorAction SilentlyContinue
            foreach ($plan in $planFiles) {
                $planContent = Get-Content $plan.FullName -Raw -ErrorAction SilentlyContinue
                if ($planContent -match 'status:\s*(complete|completed|done)') {
                    if ($item -notin $completeItems) {
                        $completeItems += $item
                    }
                }
            }
        }

        $totalItems = $items.Count
        $completedCount = $completeItems.Count
        $newProgress = if ($totalItems -gt 0) { [math]::Round(($completedCount / $totalItems) * 100) } else { 0 }

        # Track delta
        $priorProgress = if ($milestone.progress) { $milestone.progress } else { 0 }
        $deltaSource = $null
        if ($newProgress -gt $priorProgress -and $completeItems.Count -gt 0) {
            # Find the newly completed item
            $priorComplete = @($milestone.complete)
            foreach ($c in $completeItems) {
                if ($c -notin $priorComplete) {
                    $deltaSource = $c
                    break
                }
            }
        }

        $result[$key] = @{
            name = $milestone.name
            items = $items
            complete = $completeItems
            progress = $newProgress
            prior_progress = $priorProgress
            delta_source = $deltaSource
        }
    }

    return $result
}

# ============================================================================
# SOURCE 10: Blocked Items Detection (E2-076d)
# Items with blocked_by in frontmatter that reference incomplete items
# ============================================================================
function Get-BlockedItems {
    $blocked = @()
    $planPath = Join-Path $projectRoot "docs\plans"

    if (Test-Path $planPath) {
        $planFiles = Get-ChildItem -Path $planPath -Filter "*.md" -File -ErrorAction SilentlyContinue
        foreach ($file in $planFiles) {
            $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
            if (-not $content) { continue }

            # Parse YAML frontmatter
            if ($content -match '^---\s*\r?\n([\s\S]*?)\r?\n---') {
                $yaml = $Matches[1]

                # Check if has blocked_by field
                if ($yaml -match 'blocked_by:\s*\[([^\]]+)\]') {
                    $blockedByStr = $Matches[1]
                    $blockers = $blockedByStr -split ',' | ForEach-Object { $_.Trim().Trim('"', "'") }

                    # Get this item's ID
                    $backlogId = if ($yaml -match 'backlog_id:\s*(\S+)') { $Matches[1].Trim() } else { $null }
                    $fileStatus = if ($yaml -match 'status:\s*(\S+)') { $Matches[1].Trim() } else { "unknown" }

                    # Skip if already complete
                    if ($fileStatus -in @("complete", "completed", "done", "closed")) { continue }

                    # Check if any blockers are still incomplete
                    $unresolvedBlockers = @()
                    foreach ($blocker in $blockers) {
                        if (-not $blocker) { continue }
                        # Check if blocker is complete
                        $blockerPlanPattern = Join-Path $projectRoot "docs\plans\PLAN-$blocker*.md"
                        $blockerPlans = Get-ChildItem -Path $blockerPlanPattern -ErrorAction SilentlyContinue
                        $blockerComplete = $false
                        foreach ($bp in $blockerPlans) {
                            $bpContent = Get-Content $bp.FullName -Raw -ErrorAction SilentlyContinue
                            if ($bpContent -match 'status:\s*(complete|completed|done)') {
                                $blockerComplete = $true
                                break
                            }
                        }
                        if (-not $blockerComplete) {
                            $unresolvedBlockers += $blocker
                        }
                    }

                    if ($unresolvedBlockers.Count -gt 0 -and $backlogId) {
                        $blocked += @{
                            id = $backlogId
                            blocked_by = $unresolvedBlockers
                        }
                    }
                }
            }
        }
    }

    return $blocked
}

# ============================================================================
# SOURCE 12: Spawn Tracking (E2-110)
# Maps spawned_by values to their children for spawn tree visualization
# ============================================================================
function Get-SpawnMap {
    $spawnMap = @{}

    # Scan plans, investigations, ADRs for spawned_by field
    $searchPaths = @(
        (Join-Path $projectRoot "docs\plans"),
        (Join-Path $projectRoot "docs\investigations"),
        (Join-Path $projectRoot "docs\ADR")
    )

    foreach ($searchPath in $searchPaths) {
        if (-not (Test-Path $searchPath)) { continue }
        $files = Get-ChildItem -Path $searchPath -Filter "*.md" -File -ErrorAction SilentlyContinue

        foreach ($file in $files) {
            $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
            if (-not $content) { continue }

            # Parse YAML frontmatter
            if ($content -match '^---\s*\r?\n([\s\S]*?)\r?\n---') {
                $yaml = $Matches[1]

                # Extract spawned_by
                if ($yaml -match 'spawned_by:\s*(\S+)') {
                    $parent = $Matches[1].Trim()

                    # Extract this item's ID (backlog_id or from filename)
                    $childId = if ($yaml -match 'backlog_id:\s*(\S+)') {
                        $Matches[1].Trim()
                    } elseif ($file.Name -match '(E2-\d{3}[a-z]?|E2-FIX-\d{3}|INV-\d{3}|ADR-\d{3})') {
                        $Matches[1]
                    } else { $null }

                    if ($childId -and $parent) {
                        if (-not $spawnMap.ContainsKey($parent)) {
                            $spawnMap[$parent] = @()
                        }
                        if ($childId -notin $spawnMap[$parent]) {
                            $spawnMap[$parent] += $childId
                        }
                    }
                }
            }
        }
    }

    return $spawnMap
}

# ============================================================================
# SOURCE 13: Session Delta Calculation (E2-078)
# Compares last 2 checkpoints to calculate momentum delta
# ============================================================================
function Get-SessionDelta {
    $checkpointPath = Join-Path $projectRoot "docs\checkpoints"
    $delta = @{
        prior_session = $null
        current_session = $null
        prior_date = $null
        completed = @()
        added = @()
        milestone_delta = $null
    }

    if (-not (Test-Path $checkpointPath)) { return $delta }

    # Get checkpoint files sorted by name (which includes date and session)
    $checkpointFiles = Get-ChildItem -Path $checkpointPath -Filter "*.md" -File |
        Where-Object { $_.Name -ne "README.md" -and $_.Name -match "SESSION-\d+" } |
        Sort-Object Name -Descending |
        Select-Object -First 2

    if ($checkpointFiles.Count -lt 2) {
        if ($Verbose) { Write-Host "  Session delta: fewer than 2 checkpoints found" -ForegroundColor Yellow }
        return $delta
    }

    $currentCheckpoint = $checkpointFiles[0]
    $priorCheckpoint = $checkpointFiles[1]

    # Parse YAML frontmatter from both checkpoints
    $currentData = Get-CheckpointData -FilePath $currentCheckpoint.FullName
    $priorData = Get-CheckpointData -FilePath $priorCheckpoint.FullName

    if (-not $currentData -or -not $priorData) { return $delta }

    $delta.current_session = $currentData.session
    $delta.prior_session = $priorData.session
    $delta.prior_date = $priorData.date

    # Calculate added items: in current but not in prior
    $currentIds = @($currentData.backlog_ids)
    $priorIds = @($priorData.backlog_ids)

    foreach ($id in $currentIds) {
        if ($id -and $priorIds -notcontains $id) {
            $delta.added += $id
        }
    }

    # Calculate completed items: items that were in prior checkpoint
    # and now have complete status in plans or backlog
    $planPath = Join-Path $projectRoot "docs\plans"
    $backlogPath = Join-Path $projectRoot "docs\pm\backlog.md"
    $backlogContent = ""
    if (Test-Path $backlogPath) {
        $backlogContent = Get-Content $backlogPath -Raw
    }

    foreach ($id in $priorIds) {
        if (-not $id) { continue }

        # Check if item is now complete
        $isComplete = $false

        # Check plan status
        $planPattern = Join-Path $planPath "PLAN-$id*.md"
        $planFiles = Get-ChildItem -Path $planPattern -ErrorAction SilentlyContinue
        foreach ($plan in $planFiles) {
            $planContent = Get-Content $plan.FullName -Raw -ErrorAction SilentlyContinue
            if ($planContent -match 'status:\s*(complete|completed|done)') {
                $isComplete = $true
                break
            }
        }

        # Check backlog status if not found in plans
        if (-not $isComplete -and $backlogContent) {
            # Look for [COMPLETE] or [CLOSED] near the item ID
            if ($backlogContent -match "$id[^\[]*\[(COMPLETE|CLOSED)\]") {
                $isComplete = $true
            }
        }

        if ($isComplete -and $delta.completed -notcontains $id) {
            $delta.completed += $id
        }
    }

    if ($Verbose) {
        Write-Host "  Session delta: $($delta.prior_session) -> $($delta.current_session), +$($delta.completed.Count) done, +$($delta.added.Count) new" -ForegroundColor Gray
    }

    return $delta
}

function Get-CheckpointData {
    param([string]$FilePath)

    if (-not (Test-Path $FilePath)) { return $null }

    $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
    if (-not $content) { return $null }

    $data = @{
        session = $null
        date = $null
        backlog_ids = @()
    }

    # Parse YAML frontmatter
    if ($content -match '^---\s*\r?\n([\s\S]*?)\r?\n---') {
        $yaml = $Matches[1]

        # Extract session number
        if ($yaml -match 'session:\s*(\d+)') {
            $data.session = [int]$Matches[1]
        }

        # Extract date
        if ($yaml -match 'date:\s*(\d{4}-\d{2}-\d{2})') {
            $data.date = $Matches[1]
        }

        # Extract backlog_ids array
        # Format: backlog_ids: [E2-076e, E2-084, E2-088]
        if ($yaml -match 'backlog_ids:\s*\[([^\]]*)\]') {
            $idsStr = $Matches[1]
            $ids = $idsStr -split ',' | ForEach-Object {
                $_.Trim().Trim('"', "'", ' ')
            } | Where-Object { $_ }
            $data.backlog_ids = @($ids)
        }
    }

    return $data
}

# ============================================================================
# SLIM FILE GENERATION (E2-076d)
# Generates compact haios-status-slim.json for L2 progressive context
# ============================================================================
function Write-SlimStatus {
    param(
        [hashtable]$FullStatus,
        [string]$OutputPath
    )

    # Get active work items (first 5 high-priority items)
    $activeWork = @()
    $backlogPath = Join-Path $projectRoot "docs\pm\backlog.md"
    if (Test-Path $backlogPath) {
        $content = Get-Content $backlogPath -Raw
        # Get HIGH and URGENT items
        $matches = [regex]::Matches($content, '(E2-[A-Z]*-?\d{3}|INV-\d{3}|TD-\d{3}).*\[(HIGH|URGENT)\]')
        foreach ($m in $matches) {
            if ($activeWork.Count -lt 5) {
                $activeWork += $m.Groups[1].Value
            }
        }
    }

    # Get blocked items
    $blockedItems = Get-BlockedItems

    # Get session delta (E2-078)
    $sessionDelta = Get-SessionDelta

    # Get milestone data (E2-098: select highest-progress non-complete milestone)
    $milestoneData = $null
    if ($FullStatus.milestones -and $FullStatus.milestones.Keys.Count -gt 0) {
        $selectedKey = $null
        $selectedProgress = -1

        # First pass: find highest-progress milestone that isn't 100%
        foreach ($key in $FullStatus.milestones.Keys) {
            $m = $FullStatus.milestones[$key]
            $prog = if ($m.progress) { $m.progress } else { 0 }
            if ($prog -lt 100 -and $prog -gt $selectedProgress) {
                $selectedKey = $key
                $selectedProgress = $prog
            }
        }

        # Fallback: if all complete, pick first one
        if (-not $selectedKey) {
            $selectedKey = @($FullStatus.milestones.Keys)[0]
        }

        $m = $FullStatus.milestones[$selectedKey]
        $milestoneData = @{
            id = $selectedKey
            name = $m.name
            progress = $m.progress
            prior_progress = $m.prior_progress
            delta_source = $m.delta_source
        }
    }

    # Build session_delta object for slim (E2-078)
    $sessionDeltaSlim = $null
    if ($sessionDelta.prior_session) {
        # Calculate milestone delta if available
        $milestoneDeltaStr = $null
        if ($milestoneData -and $milestoneData.prior_progress -and $milestoneData.progress) {
            $mdelta = $milestoneData.progress - $milestoneData.prior_progress
            if ($mdelta -ne 0) {
                $sign = if ($mdelta -gt 0) { "+" } else { "" }
                $milestoneDeltaStr = "$sign$mdelta%"
            }
        }

        $sessionDeltaSlim = @{
            prior_session = $sessionDelta.prior_session
            current_session = $sessionDelta.current_session
            prior_date = $sessionDelta.prior_date
            completed = $sessionDelta.completed
            completed_count = $sessionDelta.completed.Count
            added = $sessionDelta.added
            added_count = $sessionDelta.added.Count
            milestone_delta = $milestoneDeltaStr
        }
    }

    $slim = @{
        generated = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
        milestone = $milestoneData
        session_delta = $sessionDeltaSlim
        active_work = $activeWork
        blocked_items = $blockedItems
        counts = @{
            concepts = $FullStatus.memory.concepts_count
            entities = $FullStatus.memory.entities_count
            backlog_pending = $FullStatus.pm.active_count
        }
        infrastructure = @{
            commands = $FullStatus.commands
            skills = $FullStatus.skills
            agents = $FullStatus.agents
            mcps = @(
                @{ name = "haios-memory"; tools = $FullStatus.memory.tools_count }
                @{ name = "context7"; tools = 2 }
            )
        }
    }

    $slim | ConvertTo-Json -Depth 4 | Set-Content $OutputPath -Encoding UTF8
    return $slim
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if ($Verbose) { Write-Host "Updating haios-status.json..." -ForegroundColor Cyan }

# Gather data from all sources
$status.valid_templates = Get-ValidTemplates
if ($Verbose) { Write-Host "  Templates: $($status.valid_templates.Count) found" -ForegroundColor Gray }

$status.agents = Get-Agents
if ($Verbose) { Write-Host "  Agents: $($status.agents.Count) found" -ForegroundColor Gray }

$status.skills = Get-Skills
if ($Verbose) { Write-Host "  Skills: $($status.skills.Count) found" -ForegroundColor Gray }

$status.commands = Get-Commands
if ($Verbose) { Write-Host "  Commands: $($status.commands.Count) found" -ForegroundColor Gray }

$memoryStats = Get-MemoryStats
if ($memoryStats) {
    $status.memory.concepts_count = $memoryStats.concepts
    $status.memory.entities_count = $memoryStats.entities
    $status.memory.artifacts_count = $memoryStats.artifacts
    $status.memory.reasoning_traces = $memoryStats.reasoning_traces
    if ($Verbose) { Write-Host "  Memory: $($memoryStats.concepts) concepts" -ForegroundColor Gray }
}

$backlogStats = Get-BacklogStats
$status.pm.active_count = $backlogStats.active_count
$status.pm.last_session = $backlogStats.last_session
$status.pm.by_priority = $backlogStats.by_priority
if ($Verbose) { Write-Host "  Backlog: $($backlogStats.active_count) active items" -ForegroundColor Gray }

$liveFilesResult = Get-LiveFiles
$status.lifecycle.live_files = $liveFilesResult.files
$status.lifecycle.counts_by_status = $liveFilesResult.counts_by_status
$status.lifecycle.counts_by_phase = $liveFilesResult.counts_by_phase
if ($Verbose) { Write-Host "  Live files: $($liveFilesResult.files.Count) in transit" -ForegroundColor Gray }

# Alignment check
$alignmentIssues = Check-Alignment -liveFiles $status.lifecycle.live_files -backlogItems $backlogStats.items
$status.lifecycle.alignment_issues = $alignmentIssues
if ($alignmentIssues.Count -gt 0 -and $Verbose) {
    Write-Host "  Alignment issues: $($alignmentIssues.Count)" -ForegroundColor Yellow
}

# ============================================================================
# WORK ITEM TREES - REMOVED (ADR-036)
# /close command now queries documents at runtime via grep
# ============================================================================

# ============================================================================
# WORKSPACE ANALYSIS (ADR-031)
# ============================================================================
if ($Verbose) { Write-Host "  Analyzing workspace..." -ForegroundColor Gray }

# Analyze checkpoints for outstanding items
$checkpointPath = Join-Path $projectRoot "docs\checkpoints"
if (Test-Path $checkpointPath) {
    $checkpointFiles = Get-ChildItem -Path $checkpointPath -Filter "*.md" -File | Where-Object { $_.Name -ne "README.md" }
    foreach ($file in $checkpointFiles) {
        $outstanding = Get-OutstandingItems -FilePath $file.FullName
        if ($outstanding.pending_items.Count -gt 0) {
            $relativePath = $file.FullName.Replace($projectRoot, "").TrimStart("\", "/")
            $status.workspace.outstanding.checkpoints += @{
                path = $relativePath
                pending_items = $outstanding.pending_items
            }
        }
    }
}

# Analyze handoffs for pending status and staleness
$handoffPath = Join-Path $projectRoot "docs\handoff"
if (Test-Path $handoffPath) {
    $handoffFiles = Get-ChildItem -Path $handoffPath -Filter "*.md" -File | Where-Object { $_.Name -ne "README.md" }
    foreach ($file in $handoffFiles) {
        $staleInfo = Get-StaleItems -FilePath $file.FullName -Type "handoff" -ThresholdDays 3
        $relativePath = $file.FullName.Replace($projectRoot, "").TrimStart("\", "/")

        # Add to outstanding if pending/open status
        $pendingStatuses = @("pending", "open", "in_progress", "ready")
        if ($pendingStatuses -contains $staleInfo.status.ToLower()) {
            $status.workspace.outstanding.handoffs += @{
                path = $relativePath
                status = $staleInfo.status
                age_days = $staleInfo.age_days
            }
        }

        # Add to stale if threshold exceeded
        if ($staleInfo.is_stale) {
            $status.workspace.stale.items += @{
                path = $relativePath
                type = "handoff"
                age_days = $staleInfo.age_days
                status = $staleInfo.status
            }
        }
    }
}

# Analyze plans for approved-not-started
$planPath = Join-Path $projectRoot "docs\plans"
if (Test-Path $planPath) {
    $planFiles = Get-ChildItem -Path $planPath -Filter "*.md" -File | Where-Object { $_.Name -ne "README.md" }
    foreach ($file in $planFiles) {
        $staleInfo = Get-StaleItems -FilePath $file.FullName -Type "plan" -ThresholdDays 7
        $relativePath = $file.FullName.Replace($projectRoot, "").TrimStart("\", "/")

        # DD-031-03: Approved-not-started = status: approved with no corresponding checkpoint
        if ($staleInfo.status.ToLower() -eq "approved") {
            # Check if there's recent activity (checkpoint mentioning this plan)
            $planName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
            $hasRecentActivity = $false

            if (Test-Path $checkpointPath) {
                $recentCheckpoints = Get-ChildItem -Path $checkpointPath -Filter "*.md" -File |
                    Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) }
                foreach ($cp in $recentCheckpoints) {
                    $cpContent = Get-Content $cp.FullName -Raw -ErrorAction SilentlyContinue
                    if ($cpContent -and $cpContent -match $planName) {
                        $hasRecentActivity = $true
                        break
                    }
                }
            }

            if (-not $hasRecentActivity) {
                $status.workspace.outstanding.plans += @{
                    path = $relativePath
                    status = $staleInfo.status
                    not_started = $true
                    age_days = $staleInfo.age_days
                }
            }
        }

        # Add to stale if threshold exceeded for draft plans
        if ($staleInfo.is_stale -and $staleInfo.status.ToLower() -eq "draft") {
            $status.workspace.stale.items += @{
                path = $relativePath
                type = "plan"
                age_days = $staleInfo.age_days
                status = $staleInfo.status
            }
        }
    }
}

# Calculate summary
$status.workspace.summary = Get-WorkspaceSummary -WorkspaceData $status.workspace
if ($Verbose) {
    Write-Host "  Workspace: $($status.workspace.summary.incomplete_checkpoints) incomplete checkpoints, $($status.workspace.summary.pending_handoffs) pending handoffs" -ForegroundColor Gray
}

# ============================================================================
# MILESTONE PROGRESS (E2-076d)
# Load existing milestones from status file, calculate progress
# ============================================================================
if ($Verbose) { Write-Host "  Calculating milestone progress..." -ForegroundColor Gray }

# Load existing milestones from current status file
$existingMilestones = @{}
if (Test-Path $statusFile) {
    try {
        $existingStatus = Get-Content $statusFile -Raw | ConvertFrom-Json
        if ($existingStatus.milestones) {
            # Convert PSObject to hashtable
            foreach ($prop in $existingStatus.milestones.PSObject.Properties) {
                $existingMilestones[$prop.Name] = @{
                    name = $prop.Value.name
                    items = @($prop.Value.items)
                    complete = @($prop.Value.complete)
                    progress = $prop.Value.progress
                    prior_progress = $prop.Value.prior_progress
                    delta_source = $prop.Value.delta_source
                }
            }
        }
    } catch {
        if ($Verbose) { Write-Host "  Could not load existing milestones: $_" -ForegroundColor Yellow }
    }
}

# Calculate updated progress
$status.milestones = Get-MilestoneProgress -ExistingMilestones $existingMilestones
if ($Verbose -and $status.milestones.Keys.Count -gt 0) {
    $firstKey = @($status.milestones.Keys)[0]
    Write-Host "  Milestone: $($status.milestones[$firstKey].name) at $($status.milestones[$firstKey].progress)%" -ForegroundColor Gray
}

# E2-110: Populate spawn map
$status.spawn_map = Get-SpawnMap
if ($Verbose) { Write-Host "  Spawn map: $($status.spawn_map.Keys.Count) parents tracked" -ForegroundColor Gray }

# Output
if ($DryRun) {
    Write-Host "`nDry run - would write:" -ForegroundColor Yellow
    $status | ConvertTo-Json -Depth 5
} else {
    $status | ConvertTo-Json -Depth 5 | Set-Content $statusFile -Encoding UTF8
    Write-Host "Updated: $statusFile" -ForegroundColor Green

    # Generate slim file (E2-076d)
    $slimResult = Write-SlimStatus -FullStatus $status -OutputPath $slimFile
    Write-Host "Updated: $slimFile" -ForegroundColor Green
}
