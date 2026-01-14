# generated: 2025-12-16
# System Auto: last updated on: 2025-12-16 21:16:17
# Test script for vitals injection
$cwd = "D:\PROJECTS\haios"
$slimPath = Join-Path $cwd ".claude\haios-status-slim.json"

Write-Host "Slim path: $slimPath"
Write-Host "Exists: $(Test-Path $slimPath)"

if (Test-Path $slimPath) {
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

    # Infrastructure summary
    if ($slim.infrastructure) {
        if ($slim.infrastructure.commands) {
            $vitals += "Commands: /new-*, /close, /validate, /status"
        }
        if ($slim.infrastructure.skills) {
            $vitals += "Skills: $($slim.infrastructure.skills -join ', ')"
        }
        if ($slim.infrastructure.agents) {
            $vitals += "Agents: $($slim.infrastructure.agents -join ', ')"
        }
        if ($slim.infrastructure.mcps) {
            $mcpList = @()
            foreach ($mcp in $slim.infrastructure.mcps) {
                $mcpList += "$($mcp.name)($($mcp.tools))"
            }
            $vitals += "MCPs: $($mcpList -join ', ')"
        }
    }

    $vitals += "---"

    Write-Host ""
    Write-Host ($vitals -join "`n")
}
