# generated: 2025-12-06
# System Auto: last updated on: 2025-12-20 22:56:30
# Scaffold Template Script
# Creates new files from templates with variable substitution
#
# FEATURES:
#   - Copies template file to destination
#   - Replaces {{VARIABLE}} placeholders with provided values
#   - Supports checkpoint, implementation_plan, investigation, report, architecture_decision_record templates
#   - Auto-generates output path from BacklogId and Title (Session 86 enhancement)
#   - No LLM required - pure text substitution
#
# USAGE (new - preferred):
#   ScaffoldTemplate.ps1 -Template "investigation" -BacklogId "INV-017" -Title "Observability Gap"
#   # Auto-generates: docs/investigations/INVESTIGATION-INV-017-observability-gap.md
#
# USAGE (legacy - still supported):
#   ScaffoldTemplate.ps1 -Template "checkpoint" -Output "path/to/file.md" -Variables @{SESSION="36"; TITLE="my-title"}
#
# VERSION: 1.1
# AUTHOR: Hephaestus
# DATE: 2025-12-06
# UPDATED: 2025-12-19 (Session 86 - BacklogId/Title auto-path generation)

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("checkpoint", "implementation_plan", "handoff_investigation", "investigation", "report", "architecture_decision_record")]
    [string]$Template,

    [Parameter(Mandatory = $false)]
    [string]$Output,

    [Parameter(Mandatory = $false)]
    [string]$BacklogId,

    [Parameter(Mandatory = $false)]
    [string]$Title,

    [Parameter(Mandatory = $false)]
    [hashtable]$Variables = @{}
)

# Get project root (two levels up from hooks directory)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$TemplateDir = Join-Path $ScriptDir "..\templates"

# =============================================================================
# AUTO-GENERATE OUTPUT PATH (Session 86 Enhancement)
# When -BacklogId and -Title provided, auto-compute -Output
# For report/handoff: only -Title is required (no backlog ID)
# =============================================================================
$noBacklogIdTemplates = @("report", "handoff_investigation")
if (-not $Output -and $Title -and ($BacklogId -or ($Template -in $noBacklogIdTemplates))) {
    # Create slug from title (lowercase, replace spaces with hyphens, remove special chars)
    $slug = $Title.ToLower() -replace '[^a-z0-9\s-]', '' -replace '\s+', '-' -replace '-+', '-'
    $slug = $slug.Trim('-')
    $today = Get-Date -Format "yyyy-MM-dd"

    # Map template type to directory and prefix
    switch ($Template) {
        "investigation" {
            $dir = "docs/investigations"
            $prefix = "INVESTIGATION"
            $Output = "$dir/$prefix-$BacklogId-$slug.md"
        }
        "implementation_plan" {
            $dir = "docs/plans"
            $prefix = "PLAN"
            $Output = "$dir/$prefix-$BacklogId-$slug.md"
        }
        "checkpoint" {
            $dir = "docs/checkpoints"
            # Checkpoints use date-NN-SESSION-N-title format
            $Output = "$dir/$today-{{NN}}-SESSION-$BacklogId-$slug.md"
        }
        "report" {
            $dir = "docs/reports"
            $prefix = "REPORT"
            $Output = "$dir/$today-$prefix-$slug.md"
        }
        "architecture_decision_record" {
            $dir = "docs/ADR"
            $prefix = "ADR"
            # BacklogId for ADRs is the ADR number (e.g., "038")
            $Output = "$dir/$prefix-$BacklogId-$slug.md"
        }
        "handoff_investigation" {
            $dir = "docs/handoff"
            $prefix = "HANDOFF"
            $Output = "$dir/$today-$prefix-$slug.md"
        }
        default {
            Write-Error "Unknown template type for auto-path: $Template"
            exit 1
        }
    }

    # Auto-populate Variables from BacklogId and Title
    if (-not $Variables.ContainsKey("BACKLOG_ID")) {
        $Variables["BACKLOG_ID"] = $BacklogId
    }
    if (-not $Variables.ContainsKey("TITLE")) {
        $Variables["TITLE"] = $Title
    }
    # For checkpoints, BacklogId IS the session number (E2-118 fix)
    if ($Template -eq "checkpoint" -and $BacklogId -and -not $Variables.ContainsKey("SESSION")) {
        $Variables["SESSION"] = $BacklogId
    }
}

# Validate we have an output path
if (-not $Output) {
    Write-Error "Either -Output or both -BacklogId and -Title must be provided"
    exit 1
}

# =============================================================================
# END AUTO-GENERATE OUTPUT PATH
# =============================================================================

# Build template path
$TemplatePath = Join-Path $TemplateDir "$Template.md"

if (-not (Test-Path $TemplatePath)) {
    Write-Error "Template not found: $TemplatePath"
    exit 1
}

# Read template content
$content = Get-Content $TemplatePath -Raw

# Add default variables
$today = Get-Date -Format "yyyy-MM-dd"
if (-not $Variables.ContainsKey("DATE")) {
    $Variables["DATE"] = $today
}

# Auto-compute PREV_SESSION from haios-status.json
if (-not $Variables.ContainsKey("PREV_SESSION")) {
    $statusPath = Join-Path $ProjectRoot ".claude\haios-status.json"
    if (Test-Path $statusPath) {
        try {
            $statusJson = Get-Content $statusPath -Raw | ConvertFrom-Json
            $lastSession = $statusJson.pm.last_session
            if ($lastSession) {
                $Variables["PREV_SESSION"] = $lastSession.ToString()
            }
        } catch {
            $Variables["PREV_SESSION"] = "??"
        }
    } else {
        $Variables["PREV_SESSION"] = "??"
    }
}

# Format BACKLOG_IDS as YAML array
if (-not $Variables.ContainsKey("BACKLOG_IDS")) {
    $Variables["BACKLOG_IDS"] = "[]"
} else {
    # If provided as comma-separated string, convert to YAML array format
    $ids = $Variables["BACKLOG_IDS"]
    if ($ids -and $ids -ne "[]" -and $ids -ne "") {
        # Split by comma, trim, format as YAML array
        $idList = $ids -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
        if ($idList.Count -gt 0) {
            $Variables["BACKLOG_IDS"] = "[" + ($idList -join ", ") + "]"
        } else {
            $Variables["BACKLOG_IDS"] = "[]"
        }
    } else {
        $Variables["BACKLOG_IDS"] = "[]"
    }
}

# Perform variable substitution
foreach ($key in $Variables.Keys) {
    $placeholder = "{{$key}}"
    $value = $Variables[$key]
    $content = $content -replace [regex]::Escape($placeholder), $value
}

# Remove any auto-generated timestamp lines (from when template was created)
$content = $content -replace "# generated: .*`r?`n", ""
$content = $content -replace "# System Auto: last updated on: .*`r?`n", ""

# Ensure output directory exists
$OutputDir = Split-Path -Parent $Output
if ($OutputDir -and -not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Handle {{NN}} auto-numbering sequence
if ($Output -match "\{\{NN\}\}") {
    $todayDate = Get-Date -Format "yyyy-MM-dd"
    # Pattern to match: yyyy-mm-dd-NN-...
    $filePattern = "$todayDate-??-*" 
    
    $existingFiles = Get-ChildItem -Path $OutputDir -Filter $filePattern -ErrorAction SilentlyContinue | 
    Where-Object { $_.Name -match "^$todayDate-(\d{2})-" }
    
    $maxNum = 0
    foreach ($file in $existingFiles) {
        if ($file.Name -match "^$todayDate-(\d{2})-") {
            $num = [int]$matches[1]
            if ($num -gt $maxNum) { $maxNum = $num }
        }
    }
    
    $nextNum = ($maxNum + 1).ToString("00")
    $Output = $Output.Replace("{{NN}}", $nextNum)
}

# Write output file
$content | Out-File -FilePath $Output -Encoding UTF8 -NoNewline

# Return the output path
Write-Output "Created: $Output"
exit 0
