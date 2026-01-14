# generated: 2025-12-05
# System Auto: last updated on: 2025-12-05 23:33:47
# Stop Hook - Reasoning Extraction (Closes the ReasoningBank Loop)
#
# DESCRIPTION:
#   Session 33 Implementation:
#   Extracts learnings from completed Claude Code sessions and stores them
#   as reasoning traces for future retrieval.
#
#   The ReasoningBank Loop:
#     RETRIEVE (UserPromptSubmit) -> INJECT -> EXECUTE -> EXTRACT (Stop) -> STORE
#                                                               ^
#                                                               |
#                                                          THIS HOOK
#
# HOOK EVENT: Stop
#   Runs when Claude Code finishes responding.
#
# JSON INPUT FORMAT:
#   {
#     "session_id": "...",
#     "transcript_path": "~/.claude/projects/.../xxxxx.jsonl",
#     "permission_mode": "default",
#     "hook_event_name": "Stop",
#     "stop_hook_active": true  <-- CRITICAL: Check to prevent infinite loops
#   }
#
# IMPORTANT:
#   - Check stop_hook_active to prevent infinite loop if this hook produces output
#   - The transcript_path contains the full session JSONL
#   - Extraction only happens for substantive sessions (not trivial queries)

# Read JSON input from stdin
$jsonInput = [Console]::In.ReadToEnd()

try {
    # Parse the JSON input
    $hookData = $jsonInput | ConvertFrom-Json

    # CRITICAL: Check stop_hook_active to prevent infinite loops
    # If true, a previous stop hook already ran - don't chain
    if ($hookData.stop_hook_active -eq $true) {
        # Silent exit - don't chain stop hooks
        exit 0
    }

    # Get the transcript path
    $transcriptPath = $hookData.transcript_path

    if (-not $transcriptPath -or -not (Test-Path $transcriptPath)) {
        # No transcript available - silent exit
        exit 0
    }

    # Find the extraction script
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $pythonScript = Join-Path $scriptDir "reasoning_extraction.py"

    if (-not (Test-Path $pythonScript)) {
        # Script not found - silent exit
        exit 0
    }

    # Call Python script with the transcript path
    try {
        $pinfo = New-Object System.Diagnostics.ProcessStartInfo
        $pinfo.FileName = "python"
        $pinfo.Arguments = "`"$pythonScript`" `"$transcriptPath`""
        $pinfo.RedirectStandardOutput = $true
        $pinfo.RedirectStandardError = $true
        $pinfo.UseShellExecute = $false
        $pinfo.CreateNoWindow = $true
        $pinfo.WorkingDirectory = $scriptDir

        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $pinfo

        # Set timeout (10 seconds max for extraction)
        $timeout = 10000

        $process.Start() | Out-Null

        # Wait for completion with timeout
        if ($process.WaitForExit($timeout)) {
            $stdout = $process.StandardOutput.ReadToEnd()
            $stderr = $process.StandardError.ReadToEnd()

            # Only output if extraction was successful and produced output
            if ($process.ExitCode -eq 0 -and $stdout.Trim()) {
                # Output goes to Claude as context (but Stop doesn't inject like UserPromptSubmit)
                # This is more for logging/verification
                Write-Output $stdout.Trim()
            }
        }
        # If timeout, silently continue (fail graceful)

    } catch {
        # Silent fail - don't break the workflow
    }

    # Exit successfully
    exit 0

} catch {
    # Silent fail on any error
    exit 0
}
