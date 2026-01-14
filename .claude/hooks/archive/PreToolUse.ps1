# generated: 2025-12-07
# System Auto: last updated on: 2025-12-13 21:53:56
# PreToolUse Hook - Governance Enforcement for Template Files and SQL
#
# DESCRIPTION:
#   Intercepts Write/Edit operations to governed paths and suggests
#   appropriate slash commands instead of raw file creation.
#   Also validates that plans have required backlog_id field (E2-015).
#   E2-020: Blocks SQL queries without schema verification.
#   E2-021: Warns on missing memory_refs for investigation-spawned backlog items.
#
# GOVERNED PATHS:
#   docs/checkpoints/*.md -> Use /new-checkpoint command
#   docs/plans/PLAN-*.md -> Use /new-plan command (REQUIRES backlog_id)
#   docs/handoff/*.md -> Use /new-handoff command
#   docs/reports/*.md -> Use /new-report command
#   docs/ADR/ADR-*.md -> Use /new-adr command (E2-003)
#
# SQL GOVERNANCE (E2-020):
#   Bash commands with SQL keywords -> Use Task(schema-verifier) first
#
# MEMORY REFERENCE GOVERNANCE (E2-021):
#   docs/pm/backlog.md edits with spawned_by: INV-* -> Warn if no memory_refs
#
# OUTPUT FORMAT (required by Claude Code):
#   {
#     "hookSpecificOutput": {
#       "hookEventName": "PreToolUse",
#       "permissionDecision": "allow|deny|ask",
#       "permissionDecisionReason": "explanation"
#     }
#   }

# Read JSON input from stdin
$jsonInput = [Console]::In.ReadToEnd()

try {
    $hookData = $jsonInput | ConvertFrom-Json

    # E2-020: Check Bash tool for SQL queries
    if ($hookData.tool_name -eq "Bash") {
        $command = $hookData.tool_input.command
        if ($command) {
            # Detect SQL keywords with FROM (to avoid false positives)
            # Pattern: SELECT/INSERT/UPDATE/DELETE followed by FROM or INTO
            $sqlPattern = '(?i)(SELECT\s+.+\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)'

            if ($command -match $sqlPattern) {
                # Allow safe patterns:
                # 1. PRAGMA commands (schema verification itself)
                # 2. .tables command
                # 3. Python using DatabaseManager (abstraction layer)
                # 4. pytest (tests)
                $safePatterns = @(
                    '(?i)PRAGMA\s+table_info',
                    '(?i)\.tables',
                    '(?i)\.schema',
                    '(?i)sqlite3.*--version',
                    '(?i)sqlite_master',
                    '(?i)PRAGMA\s+table_list',
                    '(?i)from\s+haios_etl',
                    '(?i)DatabaseManager',
                    '(?i)pytest',
                    '(?i)python\s+-m\s+haios_etl'
                )

                $isSafe = $false
                foreach ($pattern in $safePatterns) {
                    if ($command -match $pattern) {
                        $isSafe = $true
                        break
                    }
                }

                if (-not $isSafe) {
                    $reason = "BLOCKED: Direct SQL not allowed. Run this instead: Task(prompt='<your query intent>', subagent_type='schema-verifier')"
                    $output = @{
                        hookSpecificOutput = @{
                            hookEventName            = "PreToolUse"
                            permissionDecision       = "deny"
                            permissionDecisionReason = $reason
                        }
                    }
                    $output | ConvertTo-Json -Depth 10 -Compress
                    exit 0
                }
            }
        }
        # Bash command without SQL - allow
        exit 0
    }

    # Check Write and Edit tools for governance
    if ($hookData.tool_name -notin @("Write", "Edit")) {
        exit 0
    }

    # Get file path from tool input
    $filePath = $hookData.tool_input.file_path
    if (-not $filePath) {
        exit 0
    }

    # Normalize path separators
    $normalizedPath = $filePath -replace "\\", "/"

    # E2-015: For PLAN files, check backlog_id even on edits
    if ($normalizedPath -like "*docs/plans/PLAN-*") {
        $content = $hookData.tool_input.content
        if ($content) {
            # Check if content has backlog_id in YAML frontmatter
            if ($content -notmatch 'backlog_id:\s*E2-\d{3}') {
                $reason = "BLOCKED: Plans require backlog_id field in YAML frontmatter. Use '/new-plan <backlog_id> <title>' command."
                $output = @{
                    hookSpecificOutput = @{
                        hookEventName            = "PreToolUse"
                        permissionDecision       = "deny"
                        permissionDecisionReason = $reason
                    }
                }
                $output | ConvertTo-Json -Depth 10 -Compress
                exit 0
            }
        }
    }

    # E2-021: Memory Reference Governance for backlog.md
    # Warn (not block) when investigation-spawned items lack memory_refs
    if ($normalizedPath -like "*docs/pm/backlog.md*") {
        $content = $hookData.tool_input.content
        $oldString = $hookData.tool_input.old_string
        $newString = $hookData.tool_input.new_string

        # For Edit tool, check new_string; for Write, check content
        $textToCheck = if ($newString) { $newString } else { $content }

        if ($textToCheck) {
            # Check if adding/editing an item with spawned_by: INV-* or spawned_by: INVESTIGATION-*
            # Supports both plain YAML and markdown bold format (**spawned_by:**)
            if ($textToCheck -match '(\*\*)?spawned_by:(\*\*)?\s*(INV-\d{3}|INVESTIGATION-\S+)') {
                # Check if memory_refs is present (supports markdown bold format)
                if ($textToCheck -notmatch '(\*\*)?memory_refs:(\*\*)?') {
                    # WARN but ALLOW - soft governance
                    $reason = "WARNING: Investigation-spawned backlog item should include memory_refs. " +
                              "Add 'memory_refs: [concept IDs]' to link to source insights. " +
                              "(RFC 2119 SHOULD per E2-021)"
                    $output = @{
                        hookSpecificOutput = @{
                            hookEventName            = "PreToolUse"
                            permissionDecision       = "allow"
                            permissionDecisionReason = $reason
                        }
                    }
                    $output | ConvertTo-Json -Depth 10 -Compress
                    exit 0
                }
            }
        }
    }

    # Allow edits to existing files - only block NEW file creation for path governance
    if (Test-Path $filePath) {
        exit 0
    }

    # Define governed paths and their commands
    $governedPaths = @{
        "docs/checkpoints/" = @{
            command = "/new-checkpoint"
            pattern = "*.md"
        }
        "docs/plans/"       = @{
            command = "/new-plan"
            pattern = "PLAN-*.md"
        }
        "docs/handoff/"     = @{
            command = "/new-handoff"
            pattern = "*.md"
        }
        "docs/reports/"     = @{
            command = "/new-report"
            pattern = "*.md"
        }
        "docs/ADR/"         = @{
            command = "/new-adr"
            pattern = "ADR-*.md"
        }
    }

    # Check if path matches any governed location
    foreach ($govPath in $governedPaths.Keys) {
        if ($normalizedPath -like "*$govPath*") {
            $config = $governedPaths[$govPath]
            $fileName = Split-Path $normalizedPath -Leaf

            # Check if file matches pattern
            if ($fileName -like $config.pattern) {
                # This is a governed file - BLOCK and enforce command usage
                $reason = "BLOCKED: Governed path. Use '$($config.command)' command instead of raw Write/Edit."

                $output = @{
                    hookSpecificOutput = @{
                        hookEventName            = "PreToolUse"
                        permissionDecision       = "deny"
                        permissionDecisionReason = $reason
                    }
                }

                $output | ConvertTo-Json -Depth 10 -Compress
                exit 0
            }
        }
    }

    # Not a governed path - allow silently
    exit 0

}
catch {
    # On error, allow the operation to proceed
    exit 0
}
