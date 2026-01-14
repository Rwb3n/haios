---
template: implementation_plan
status: complete
date: 2025-12-20
backlog_id: E2-110
title: "Spawn Field Governance"
author: Hephaestus
lifecycle_phase: do
session: 90
milestone: M4-Research
enables: [E2-114, E2-115]
version: "1.3"
---
# generated: 2025-12-20
# System Auto: last updated on: 2025-12-20 21:35:46
# Implementation Plan: Spawn Field Governance

@docs/pm/backlog.md
@.claude/hooks/UpdateHaiosStatus.ps1

---

## Goal

Validate and track `spawned_by` fields like we do for `blocked_by` - surface spawn relationships in haios-status.json for visibility.

---

## Current State vs Desired State

### Current State

**blocked_by governance (for comparison):**
- UpdateHaiosStatus.ps1:583-641 - `Get-BlockedItems` function extracts blocked_by, checks blocker status, surfaces in haios-status.json
- CascadeHook.ps1:106-153 - Detects unblock events when blocker completes
- PreToolUse.ps1 - No validation for blocked_by references

**spawned_by current state:**
- ValidateTemplate.ps1 - Field allowed in templates (lines 39, 51, 63, 74, 86, 96, 105)
- PreToolUse.ps1:138-140 - Warns if spawned_by: INV-* lacks memory_refs
- NO tracking in UpdateHaiosStatus.ps1
- NO visualization in haios-status.json
- NO validation that spawned_by references exist

**Behavior:** spawned_by is accepted but not tracked. Cannot query "what did INV-005 produce?"

**Result:** Spawn relationships invisible. M4-Research cannot trace investigation outputs.

### Desired State

**Add to UpdateHaiosStatus.ps1:**
```powershell
# SOURCE N: Spawn Tracking (E2-110)
function Get-SpawnRelationships {
    # Returns: { "INV-005": ["E2-037", "E2-038"], "INV-010": ["E2-048"] }
}
```

**Add to haios-status.json:**
```json
{
  "spawn_map": {
    "INV-005": ["E2-037", "E2-038"],
    "INV-010": ["E2-048", "E2-049"]
  }
}
```

**Behavior:** System tracks what each investigation spawned. Can query spawn tree.

**Result:** E2-114 (Spawn Tree Query) has data to visualize.

---

## Tests First (TDD)

This is a PowerShell hook addition - no pytest tests. Verification is manual via haios-status.json output.

### Test 1: Spawn Map Populated
```
Run: just update-status
Verify: haios-status.json contains "spawn_map" key
Verify: INV-017 maps to [E2-102, E2-103] (from real data above)
```

### Test 2: Session Spawns Tracked
```
Verify: Session-83 maps to [E2-091, E2-092, E2-093, E2-094, E2-095, E2-096, E2-097]
```

### Test 3: Plan Spawns Tracked
```
Verify: PLAN-E2-076 maps to [E2-076b, E2-076d, E2-076e]
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/hooks/UpdateHaiosStatus.ps1`
**Location:** After Get-BlockedItems (line ~641), before Get-SessionDelta

**New Function:**
```powershell
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
                    } elseif ($file.Name -match '(E2-\d{3}|INV-\d{3}|ADR-\d{3})') {
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
```

**Integration (in main output):**
```powershell
# After blocked_items, before session_delta
$spawnMap = Get-SpawnMap
# ...
$status = @{
    # ... existing fields ...
    spawn_map = $spawnMap
    # ...
}
```

### Call Chain Context

```
UpdateHaiosStatus.ps1 (main)
    |
    +-> Get-BlockedItems()
    |
    +-> Get-SpawnMap()       # <-- NEW
    |       Returns: @{ "INV-017" = @("E2-102", "E2-103") }
    |
    +-> Get-SessionDelta()
    |
    +-> Build final $status hashtable
    +-> ConvertTo-Json
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Where to add spawn_map | haios-status.json (full only) | Slim version stays compact; spawn tree is reference data |
| What to scan | plans/, investigations/, ADR/ | These are the sources that have spawned_by fields |
| Handle non-E2 parents | Keep as-is (Session-83) | Allows flexible spawn sources |

### Input/Output Examples (Real Data)

**Current haios-status.json:** No spawn_map field

**After fix:**
```json
{
  "spawn_map": {
    "INV-016": ["E2-076"],
    "INV-017": ["E2-102", "E2-103"],
    "PLAN-E2-076": ["E2-076b", "E2-076d", "E2-076e"],
    "Session-83": ["E2-091", "E2-092", "E2-093", "E2-094", "E2-095", "E2-096", "E2-097"],
    "INV-010": ["ADR-037"],
    "E2-076d": ["E2-078"],
    "E2-076": ["E2-079"]
  }
}
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No spawned_by field | Skip file | Implicit |
| Multiple children same parent | Append to array | Test 2 |
| Parent doesn't exist | Include anyway | Spawn map is data, not validation |

---

## Implementation Steps

### Step 1: Add Get-SpawnMap Function
- [ ] Add function after Get-BlockedItems (~line 641)
- [ ] Follow existing function style

### Step 2: Integrate into Main Output
- [ ] Call Get-SpawnMap before building $status
- [ ] Add spawn_map to $status hashtable

### Step 3: Verify Output
- [ ] Run just update-status
- [ ] Check haios-status.json for spawn_map
- [ ] Verify real data matches expectations

---

## Verification

- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| PowerShell hashtable JSON serialization | Low | Use ConvertTo-Json -Depth 4 |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 90 | 2025-12-20 | Pending | in_progress | Plan complete, starting DO |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/hooks/UpdateHaiosStatus.ps1` | Get-SpawnMap function exists | [ ] | |
| `.claude/haios-status.json` | spawn_map key populated | [ ] | |

**Verification Commands:**
```bash
just update-status
# Then check haios-status.json for spawn_map
```

---

**Completion Criteria (DoD per ADR-033):**
- [ ] spawn_map appears in haios-status.json
- [ ] WHY captured (reasoning stored to memory)
- [ ] Documentation current

---

## References

- ADR-033: Work Item Lifecycle
- E2-076b: Frontmatter Schema (spawned_by field defined)


<!-- VALIDATION ERRORS (2025-12-20 21:32:31):
  - ERROR: Missing required fields: directive_id
-->
