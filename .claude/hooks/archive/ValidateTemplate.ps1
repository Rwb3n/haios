# generated: 2025-09-22
# System Auto: last updated on: 2025-12-20 21:48:24
# Template Validation Hook
# Validates markdown templates against required structure
#
# FEATURES:
#   - Validates YAML header presence and structure
#   - Checks required fields based on template type
#   - Verifies status values against allowed enums
#   - Counts @ references (minimum 2 required)
#   - Returns validation results or errors
#
# VERSION: 1.0
# AUTHOR: Claude (per Directive D-20250922-01)
# DATE: 2025-09-22

param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath,

    [Parameter(Mandatory=$false)]
    [switch]$VerboseOutput,

    [Parameter(Mandatory=$false)]
    [switch]$JsonOutput
)

# Template Type Registry
# Defines validation rules for each template type
# E2-030 Cleanup (Session 70): Reduced from 14 types to 7 core types
# Removed: directive, verification, implementation_report, meta_template, guide, handoff, handoff_investigation, proposal
$templateRegistry = @{
    # E2-076b: Added DAG edge fields (Session 79)
    "checkpoint" = @{
        RequiredFields = @("template", "status", "date", "version", "author", "project_phase")
        OptionalFields = @(
            "previous_checkpoint", "directive_id", "title", "session", "lifecycle_phase", "subtype", "backlog_ids", "parent_id",
            # DAG edge fields (E2-076b) - Session 90: Removed spawned_by, checkpoints are session records not spawn sources
            "blocked_by", "related", "milestone",
            # Session continuity
            "prior_session", "memory_refs"
        )
        AllowedStatus = @("draft", "active", "complete", "archived")
    }
    # E2-076b: Added DAG edge fields (Session 79)
    "implementation_plan" = @{
        RequiredFields = @("template", "status", "date", "directive_id")
        OptionalFields = @(
            "version", "author", "plan_id", "title", "session", "priority", "lifecycle_phase", "subtype", "backlog_id", "parent_id", "completed_session", "completion_note",
            # DAG edge fields (E2-076b)
            "spawned_by", "blocked_by", "related", "milestone", "parent_plan",
            # Plan hierarchy fields
            "children", "absorbs", "enables", "execution_layer"
        )
        AllowedStatus = @("draft", "approved", "rejected", "complete")
    }
    # ADR-033: Added backlog_ids and memory_refs for traceability (Session 57)
    # Session 72: Added spawned_by, backlog_id (singular) for spawning mechanism consistency
    # E2-076b: Added DAG edge fields (Session 79)
    "architecture_decision_record" = @{
        RequiredFields = @("template", "status", "date", "adr_id")
        OptionalFields = @(
            "version", "author", "title", "session", "decision", "approved_by", "approved_date", "lifecycle_phase", "subtype", "backlog_id", "backlog_ids", "memory_refs", "spawned_by", "spawns",
            # DAG edge fields (E2-076b)
            "blocked_by", "related", "milestone"
        )
        AllowedStatus = @("proposed", "accepted", "rejected", "superseded", "deprecated")
    }
    # ADR-034: New canonical DISCOVERY phase template (Session 62)
    # E2-076b: Added DAG edge fields (Session 79)
    "investigation" = @{
        RequiredFields = @("template", "status", "date", "backlog_id")
        OptionalFields = @(
            "title", "author", "session", "lifecycle_phase", "subtype", "spawned_by", "spawns",
            # DAG edge fields (E2-076b)
            "blocked_by", "related", "milestone"
        )
        AllowedStatus = @("draft", "active", "pending", "closed", "complete", "archived")
    }
    # E2-076b: Added DAG edge fields (Session 79)
    "report" = @{
        RequiredFields = @("template", "status", "date")
        OptionalFields = @(
            "title", "author", "session", "tags", "lifecycle_phase", "subtype", "backlog_ids", "directive_id", "report_id", "version",
            # DAG edge fields (E2-076b)
            "spawned_by", "blocked_by", "related", "milestone"
        )
        AllowedStatus = @("draft", "active", "complete", "archived", "final", "reviewed", "disputed")
    }
    # E2-076b: Added DAG edge fields (Session 79) - readme gets spawned_by, related only
    "readme" = @{
        RequiredFields = @("template", "status", "date", "component")
        OptionalFields = @(
            "version", "owner", "author", "title", "lifecycle_phase", "subtype",
            # DAG edge fields (E2-076b) - limited set for readme
            "spawned_by", "related"
        )
        AllowedStatus = @("draft", "active", "deprecated", "archived")
    }
    # E2-021: Added memory_refs for memory reference governance (Session 68)
    # E2-076b: Added DAG edge fields (Session 79)
    "backlog_item" = @{
        RequiredFields = @("template", "status", "date", "backlog_id", "priority", "complexity", "category")
        OptionalFields = @(
            "version", "author", "title", "lifecycle_phase", "subtype", "spawned_by", "blocks", "blocked_by", "memory_refs",
            # DAG edge fields (E2-076b)
            "related", "milestone"
        )
        AllowedStatus = @("proposed", "researching", "ready", "implementing", "cancelled", "complete")
        AllowedPriority = @("critical", "high", "medium", "low")
        AllowedComplexity = @("small", "medium", "large", "unknown")
        AllowedCategory = @("enhancement", "technical_debt", "bug", "research", "documentation")
    }
}

# Initialize validation result
$validationResult = @{
    IsValid = $true
    TemplatePath = $FilePath
    TemplateType = $null
    Errors = @()
    Warnings = @()
    Metadata = @{}
    ReferenceCount = 0
    ValidationTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

# Function to extract YAML header from file
function Get-YamlHeader {
    param([string]$Content)

    $lines = $Content -split "`r?`n"
    $inYaml = $false
    $yamlLines = @()
    $yamlStart = -1
    $yamlEnd = -1

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]

        if ($line -eq "---" -and -not $inYaml) {
            $inYaml = $true
            $yamlStart = $i
        }
        elseif ($line -eq "---" -and $inYaml) {
            $yamlEnd = $i
            break
        }
        elseif ($inYaml) {
            # Skip timestamp lines added by PostToolUse hook
            if ($line -notmatch "^#\s*(generated:|System Auto:)") {
                $yamlLines += $line
            }
        }
    }

    if ($yamlStart -ge 0 -and $yamlEnd -gt $yamlStart) {
        return $yamlLines -join "`n"
    }

    return $null
}

# Function to parse YAML into hashtable
function ConvertFrom-SimpleYaml {
    param([string]$YamlText)

    $result = @{}
    $lines = $YamlText -split "`r?`n"

    foreach ($line in $lines) {
        if ($line -match '^\s*([a-zA-Z_]+):\s*(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()

            # Remove quotes if present
            if ($value -match '^"(.*)"$' -or $value -match "^'(.*)'$") {
                $value = $matches[1]
            }

            $result[$key] = $value
        }
    }

    return $result
}

# Function to count @ references in content
function Get-ReferenceCount {
    param([string]$Content)

    $pattern = '@[a-zA-Z0-9_./\\:\-]+'
    $matches = [regex]::Matches($Content, $pattern)
    return $matches.Count
}

# Main validation logic
try {
    # Check if file exists
    if (-not (Test-Path $FilePath)) {
        $validationResult.IsValid = $false
        $validationResult.Errors += "ERROR: File not found: $FilePath"

        if ($JsonOutput) {
            Write-Output (ConvertTo-Json $validationResult -Depth 3)
        } else {
            Write-Host "❌ Validation Failed" -ForegroundColor Red
            foreach ($err in $validationResult.Errors) {
                Write-Host "  $err" -ForegroundColor Red
            }
        }
        exit 1
    }

    # Read file content
    $content = Get-Content $FilePath -Raw

    if (-not $content) {
        $validationResult.IsValid = $false
        $validationResult.Errors += "ERROR: File is empty"
    }
    else {
        # Extract YAML header
        $yamlContent = Get-YamlHeader -Content $content

        if (-not $yamlContent) {
            $validationResult.IsValid = $false
            $validationResult.Errors += "ERROR: Missing YAML header in template"
        }
        else {
            # Parse YAML
            $metadata = ConvertFrom-SimpleYaml -YamlText $yamlContent
            $validationResult.Metadata = $metadata

            # Validate template type
            if (-not $metadata.ContainsKey("template")) {
                $validationResult.IsValid = $false
                $validationResult.Errors += "ERROR: Missing 'template' field in YAML header"
            }
            else {
                $templateType = $metadata["template"]
                $validationResult.TemplateType = $templateType

                if (-not $templateRegistry.ContainsKey($templateType)) {
                    $validTypes = ($templateRegistry.Keys | Sort-Object) -join ", "
                    $validationResult.IsValid = $false
                    $validationResult.Errors += "ERROR: Unknown template type '$templateType'. Valid types: $validTypes"
                }
                else {
                    $rules = $templateRegistry[$templateType]

                    # Check required fields
                    $missingFields = @()
                    foreach ($field in $rules.RequiredFields) {
                        if (-not $metadata.ContainsKey($field)) {
                            $missingFields += $field
                        }
                    }

                    if ($missingFields.Count -gt 0) {
                        $validationResult.IsValid = $false
                        $fieldList = $missingFields -join ", "
                        $validationResult.Errors += "ERROR: Missing required fields: $fieldList"
                    }

                    # Validate status enum
                    if ($metadata.ContainsKey("status")) {
                        $status = $metadata["status"]
                        if ($status -notin $rules.AllowedStatus) {
                            $validationResult.IsValid = $false
                            $allowedList = $rules.AllowedStatus -join ", "
                            $validationResult.Errors += "ERROR: Invalid status '$status' for $templateType template. Allowed: $allowedList"
                        }
                    }

                    # Validate additional enums for backlog_item templates
                    if ($templateType -eq "backlog_item") {
                        # Validate priority
                        if ($metadata.ContainsKey("priority")) {
                            $priority = $metadata["priority"]
                            if ($priority -notin $rules.AllowedPriority) {
                                $validationResult.IsValid = $false
                                $allowedList = $rules.AllowedPriority -join ", "
                                $validationResult.Errors += "ERROR: Invalid priority '$priority' for backlog_item template. Allowed: $allowedList"
                            }
                        }

                        # Validate complexity
                        if ($metadata.ContainsKey("complexity")) {
                            $complexity = $metadata["complexity"]
                            if ($complexity -notin $rules.AllowedComplexity) {
                                $validationResult.IsValid = $false
                                $allowedList = $rules.AllowedComplexity -join ", "
                                $validationResult.Errors += "ERROR: Invalid complexity '$complexity' for backlog_item template. Allowed: $allowedList"
                            }
                        }

                        # Validate category
                        if ($metadata.ContainsKey("category")) {
                            $category = $metadata["category"]
                            if ($category -notin $rules.AllowedCategory) {
                                $validationResult.IsValid = $false
                                $allowedList = $rules.AllowedCategory -join ", "
                                $validationResult.Errors += "ERROR: Invalid category '$category' for backlog_item template. Allowed: $allowedList"
                            }
                        }
                    }

                    # Check for unknown fields (warnings only)
                    foreach ($key in $metadata.Keys) {
                        if ($key -notin $rules.RequiredFields -and $key -notin $rules.OptionalFields) {
                            $validationResult.Warnings += "WARNING: Unknown field '$key' for $templateType template"
                        }
                    }
                }
            }
        }

        # Count @ references
        $refCount = Get-ReferenceCount -Content $content
        $validationResult.ReferenceCount = $refCount

        # Minimum 2 references required for all templates
        if ($refCount -lt 2) {
            $validationResult.IsValid = $false
            $validationResult.Errors += "ERROR: Only $refCount @ reference(s) found (minimum 2 required)"
        }
    }

    # Output results
    if ($JsonOutput) {
        Write-Output (ConvertTo-Json $validationResult -Depth 3)
    }
    else {
        if ($validationResult.IsValid) {
            Write-Host "✅ Template Validation Passed" -ForegroundColor Green
            Write-Host "  Type: $($validationResult.TemplateType)" -ForegroundColor Gray
            Write-Host "  References: $($validationResult.ReferenceCount)" -ForegroundColor Gray

            if ($VerboseOutput) {
                Write-Host "`nMetadata:" -ForegroundColor Cyan
                foreach ($key in $validationResult.Metadata.Keys) {
                    Write-Host "  $key : $($validationResult.Metadata[$key])" -ForegroundColor Gray
                }
            }
        }
        else {
            Write-Host "❌ Template Validation Failed" -ForegroundColor Red
            Write-Host "  File: $FilePath" -ForegroundColor Gray

            foreach ($err in $validationResult.Errors) {
                Write-Host "  $err" -ForegroundColor Red
            }
        }

        if ($validationResult.Warnings.Count -gt 0) {
            Write-Host "`nWarnings:" -ForegroundColor Yellow
            foreach ($warning in $validationResult.Warnings) {
                Write-Host "  $warning" -ForegroundColor Yellow
            }
        }
    }

    # Exit with appropriate code
    if ($validationResult.IsValid) {
        exit 0
    } else {
        exit 1
    }
}
catch {
    $validationResult.IsValid = $false
    $validationResult.Errors += "ERROR: Unexpected error - $_"

    if ($JsonOutput) {
        Write-Output (ConvertTo-Json $validationResult -Depth 3)
    } else {
        Write-Host "❌ Validation Error: $_" -ForegroundColor Red
    }

    exit 1
}