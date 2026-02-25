---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-25
backlog_id: WORK-230
title: "Migrate Scaffold Commands and Agent Files to MCP Operations Tools"
author: Hephaestus
lifecycle_phase: plan
session: 458
generated: 2026-02-25
last_updated: 2026-02-25T22:00:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-230/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete before/after text blocks, not pseudocode"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: Migrate Scaffold Commands and Agent Files to MCP Operations Tools

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

Migrate 11 command and agent markdown files to reference MCP tool names (e.g., `scaffold_plan`, `queue_ready`, `hierarchy_update_status`) instead of `just` recipe names for scaffold and status operations, completing the final consumer migration leg of CH-066 exit criterion 2.

---

## Open Decisions

<!-- No operator_decisions field in WORK.md — no unresolved decisions. -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| `just work` prerequisite step in new-plan.md and new-investigation.md | Migrate or keep | Migrate to `scaffold_work` MCP | The step shows the agent how to create a work item — since `scaffold_work` MCP exists, it should be the canonical instruction |
| `just ready` prose note in close.md (line 278) | Migrate or keep | Migrate to `queue_ready()` — the note references the tool by name for user context | Consistent with all other `just ready` replacements |
| `just update-status-slim` in validation-agent.md | Migrate to `hierarchy_update_status` or leave | Migrate — WORK.md acceptance criteria explicitly targets `hierarchy_update_status` for validation-agent | WORK.md AC: "validation-agent.md uses hierarchy_update_status MCP tool instead of just update-status-slim" |
| README.md Implementation column | Update references | Update `just plan/work/inv/adr` entries to reflect MCP equivalents | README.md is explicitly in scope per WORK.md deliverables |

---

## Layer 0: Inventory

<!-- MUST complete before any design work. Map the blast radius.
     Producer: plan-author agent
     Consumer: all downstream agents (DO, CHECK, critique) -->

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/commands/new-plan.md` | MODIFY | 2 |
| `.claude/commands/new-work.md` | MODIFY | 2 |
| `.claude/commands/new-investigation.md` | MODIFY | 2 |
| `.claude/commands/new-checkpoint.md` | MODIFY | 2 |
| `.claude/commands/new-adr.md` | MODIFY | 2 |
| `.claude/commands/close.md` | MODIFY | 2 |
| `.claude/commands/ready.md` | MODIFY | 2 |
| `.claude/commands/haios.md` | MODIFY | 2 |
| `.claude/agents/close-work-cycle-agent.md` | MODIFY | 2 |
| `.claude/agents/validation-agent.md` | MODIFY | 2 |
| `.claude/commands/README.md` | MODIFY | 2 |

### Consumer Files

<!-- These markdown files ARE the command/agent definitions agents read. No separate runtime consumers.
     No Python test files migrate — text-only changes. -->

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| N/A — command/agent files are terminal consumers | — | — | — |

**SKIPPED:** Consumer file table is N/A. These markdown files are themselves the consumer artifact. Agents read them directly. There are no Python importers or downstream runtime code paths that reference the specific `just` commands being replaced.

### Test Files

**SKIPPED:** This is a text-only migration of markdown files. No Python code changes. No new test files required. Verification is via grep (no `just` strings remaining in the 11 target files for the mapped operations). The constraint "No regressions: all existing tests pass" is verified by running the full pytest suite unchanged.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | No new files |
| Files to modify | 11 | Primary Files table (all MODIFY rows) |
| Tests to write | 0 | Text-only migration, no Python changes |
| Total blast radius | 11 | 11 markdown files |

---

## Layer 1: Specification

<!-- The contract that the DO agent implements.
     This is a text-substitution migration. For each file, the spec shows:
     - Which `just` references to replace
     - The exact MCP tool call to substitute -->

### Current State

**Behavior:** Commands and agent files call `just` recipes directly in their instruction text (bash code blocks and prose). Agents reading these commands execute `just` recipes as their scaffold operations.

**Problem:** ADR-045 establishes MCP tools as Tier 2 (agent interface). `just` recipes are Tier 3 (terminal/orchestration). Agents should use MCP tools exclusively for Tier 2 operations. WORK-228 audit found ~24 migratable `just` references across 11 command and agent files. CH-066 exit criterion 2 requires "Just recipes retired for agent use — MCP tools replace Tier 2 operations."

### Desired State

**Behavior:** Commands and agent files reference MCP tool names (e.g., `scaffold_plan(work_id, title)`, `queue_ready()`, `hierarchy_update_status(work_id, status)`) in their instruction text. Where bash blocks showed `just <recipe>`, they now show the MCP invocation pattern.

**Result:** Agents reading the migrated commands invoke MCP tools natively. No `just` subprocess overhead for scaffold or status operations.

---

### File-by-File Specification

#### File 1 (MODIFY): `.claude/commands/new-plan.md`

**Changes:**

**Change 1a — Prerequisite step 1 (just work for work item creation):**

Current (line 27):
```bash
just work <backlog_id> "<title>"
```

Target:
```
mcp__haios-operations__scaffold_work(title="<title>", work_id="<backlog_id>")
```

**Change 1b — Error message reference (line 35):**

Current:
```
If work file doesn't exist, `just plan` will fail with guidance to run `/new-work` first.
```

Target:
```
If work file doesn't exist, `scaffold_plan` will fail with guidance to run `/new-work` first.
```

**Change 1c — Create Plan section header and description (lines 48-52):**

Current:
```
## Create Plan

Run scaffolding via just recipe:

```bash
just plan <backlog_id> "<title>"
```
```

Target:
```
## Create Plan

Run scaffolding via MCP tool:

```
mcp__haios-operations__scaffold_plan(work_id="<backlog_id>", title="<title>")
```
```

**Change 1d — Example block (lines 55-58):**

Current:
```bash
just plan E2-094 "Test Runner Subagent"
# Creates: docs/work/active/E2-094/plans/PLAN.md
```

Target:
```
mcp__haios-operations__scaffold_plan(work_id="E2-094", title="Test Runner Subagent")
# Creates: docs/work/active/E2-094/plans/PLAN.md
```

---

#### File 2 (MODIFY): `.claude/commands/new-work.md`

**Changes:**

**Change 2a — Option 1 scaffold line (line 24):**

Current:
```bash
just work WORK-031 "New Feature Implementation"
```

Target:
```
mcp__haios-operations__scaffold_work(title="New Feature Implementation", work_id="WORK-031")
```

**Change 2b — Option 2 explicit ID (lines 28-30):**

Current:
```bash
just work WORK-031 "<title>"
```

Target:
```
mcp__haios-operations__scaffold_work(title="<title>", work_id="WORK-031")
```

**Change 2c — Example block (lines 33-36):**

Current:
```bash
just work WORK-031 "New Feature Implementation"
# Creates: docs/work/active/WORK-031/WORK.md
```

Target:
```
mcp__haios-operations__scaffold_work(title="New Feature Implementation", work_id="WORK-031")
# Creates: docs/work/active/WORK-031/WORK.md
```

---

#### File 3 (MODIFY): `.claude/commands/new-investigation.md`

**Changes:**

**Change 3a — Step 1 work item creation (line 32):**

Current:
```bash
just work WORK-031 "<title>"
```

Target:
```
mcp__haios-operations__scaffold_work(title="<title>", work_id="WORK-031")
```

**Change 3b — Step 4 investigation scaffolding (line 41):**

Current:
```bash
just inv WORK-031 "<title>"
```

Target:
```
mcp__haios-operations__scaffold_investigation(work_id="WORK-031", title="<title>")
```

**Change 3c — Error message reference (line 44):**

Current:
```
If work file doesn't exist, `just inv` will fail with guidance to run `/new-work` first.
```

Target:
```
If work file doesn't exist, `scaffold_investigation` will fail with guidance to run `/new-work` first.
```

**Change 3d — Create Investigation section (lines 60-62):**

Current:
```
## Create Investigation

Run scaffolding via just recipe:

```bash
just inv <backlog_id> "<title>"
```
```

Target:
```
## Create Investigation

Run scaffolding via MCP tool:

```
mcp__haios-operations__scaffold_investigation(work_id="<backlog_id>", title="<title>")
```
```

**Change 3e — Example block (lines 65-68):**

Current:
```bash
just inv WORK-031 "Observability Gap Analysis"
# Creates: docs/work/active/WORK-031/investigations/001-observability-gap-analysis.md
```

Target:
```
mcp__haios-operations__scaffold_investigation(work_id="WORK-031", title="Observability Gap Analysis")
# Creates: docs/work/active/WORK-031/investigations/001-observability-gap-analysis.md
```

---

#### File 4 (MODIFY): `.claude/commands/new-checkpoint.md`

**Changes:**

**Change 4a — Step 1 scaffold command (lines 17-19):**

Current:
```bash
just scaffold checkpoint <session_number> "<title>"
```

Target:
```
mcp__haios-operations__scaffold_checkpoint(session_number="<session_number>", title="<title>")
```

Also update the section header prose from "via just recipe" to "via MCP tool" if present.

---

#### File 5 (MODIFY): `.claude/commands/new-adr.md`

**Changes:**

**Change 5a — Run scaffolding section (lines 20-22):**

Current:
```bash
just adr <adr_number> "<title>"
```

Target:
```
mcp__haios-operations__scaffold_adr(adr_number="<adr_number>", title="<title>")
```

**Change 5b — Example block (lines 25-28):**

Current:
```bash
just adr 039 "Workflow State Machine"
# Creates: docs/ADR/ADR-039-workflow-state-machine.md
```

Target:
```
mcp__haios-operations__scaffold_adr(adr_number="039", title="Workflow State Machine")
# Creates: docs/ADR/ADR-039-workflow-state-machine.md
```

Also update surrounding prose: "Run scaffolding via just recipe:" → "Run scaffolding via MCP tool:"

---

#### File 6 (MODIFY): `.claude/commands/close.md`

**Changes:**

**Change 6a — Step 3d refresh status (lines 273-278):**

Current:
```
Run:
```bash
just update-status
```

> **Note (E2-190):** Must use full `update-status` (not slim) so `just ready` shows accurate data.
```

Target:
```
Run:
```
mcp__haios-operations__hierarchy_update_status(work_id="{backlog_id}", status="complete")
```

> **Note (E2-190):** Must use full `hierarchy_update_status` (not slim) so `queue_ready()` shows accurate data.
```

**Note:** The status update is part of the close sequence. Since `hierarchy_close_work` already handles closure atomically, but close.md has its own step-by-step process, the `just update-status` here refreshes the status JSON for display purposes. `hierarchy_update_status` is the correct MCP replacement per WORK.md acceptance criteria.

---

#### File 7 (MODIFY): `.claude/commands/ready.md`

**Changes:**

**Change 7a — Execution section (lines 23-25):**

Current:
```bash
just ready
```

Target:
```
mcp__haios-operations__queue_ready()
```

Also update surrounding prose: "Run the ready recipe:" → "Run the ready MCP tool:"

---

#### File 8 (MODIFY): `.claude/commands/haios.md`

**Changes:**

**Change 8a — Step 1 refresh status (lines 12-15):**

Current:
```
1. **Refresh Status** (auto-update from all sources):
   ```
   just update-status-slim
   ```
```

Target:
```
1. **Refresh Status** (update active work item status before reading):
   ```
   mcp__haios-operations__hierarchy_update_status(work_id="WORK-XXX", status="active")
   ```
   Replace `WORK-XXX` with the current work item ID and `active` with its current status.
```

**Note:** `just update-status-slim` was a lightweight bulk status refresh with no arguments. The MCP replacement `hierarchy_update_status` operates per-item (requires `work_id` and `status`). The step's purpose shifts from "refresh all statuses" to "ensure current work item status is up to date before reading the status JSON." The prose must reflect this narrower scope.

---

#### File 9 (MODIFY): `.claude/agents/close-work-cycle-agent.md`

**Changes:**

**Change 9a — Process step 3 ARCHIVE description (line 57):**

Current:
```
   - ARCHIVE: Run `just close-work {id}` to update status
```

Target:
```
   - ARCHIVE: Run `mcp__haios-operations__hierarchy_close_work(work_id="{id}")` to update status
```

**Change 9b — Governance Gates table (line 67):**

Current:
```
| ARCHIVE → CHAIN | status-updated | Verify `just close-work` succeeded |
```

Target:
```
| ARCHIVE → CHAIN | status-updated | Verify `mcp__haios-operations__hierarchy_close_work` succeeded |
```

**Change 9c — Edge Cases table (line 171):**

Current:
```
| `just close-work` fails | Return BLOCKED with error message |
```

Target:
```
| `mcp__haios-operations__hierarchy_close_work` fails | Return BLOCKED with error message |
```

---

#### File 10 (MODIFY): `.claude/agents/validation-agent.md`

**Changes:**

**Change 10a — Tips section (line 149):**

Current:
```
- Check for discoverable artifacts (run `just update-status-slim`)
```

Target:
```
- Check for discoverable artifacts (run `mcp__haios-operations__hierarchy_update_status(work_id, status)`)
```

---

#### File 11 (MODIFY): `.claude/commands/README.md`

**Changes:**

**Change 11a — Available Commands table, Implementation column (lines 24, 27, 29, 30):**

Current:
```
| `/new-plan <backlog_id> <title>` | Create plan → implementation-cycle | `just plan` → skill chain |
| `/new-checkpoint <session> <title>` | Create checkpoint from template | `just checkpoint` recipe |
| `/new-adr <number> <title>` | Create ADR from template | `just adr` recipe |
| `/new-work <backlog_id> <title>` | Create work item file | `just work` → work-creation-cycle skill |
| `/new-investigation <backlog_id> <title>` | Create investigation → investigation-cycle | `just inv` → skill chain |
```

Target:
```
| `/new-plan <backlog_id> <title>` | Create plan → implementation-cycle | `scaffold_plan` MCP → skill chain |
| `/new-checkpoint <session> <title>` | Create checkpoint from template | `scaffold_checkpoint` MCP tool |
| `/new-adr <number> <title>` | Create ADR from template | `scaffold_adr` MCP tool |
| `/new-work <backlog_id> <title>` | Create work item file | `scaffold_work` MCP → work-creation-cycle skill |
| `/new-investigation <backlog_id> <title>` | Create investigation → investigation-cycle | `scaffold_investigation` MCP → skill chain |
```

**Change 11b — Scaffold Commands section prose (lines 37-54):**

Update the Scaffold Commands section description to reflect that scaffolding now uses MCP tools (Tier 2) instead of `just scaffold` (Tier 3):

Current description line:
```
Scaffolding via `just scaffold` recipe (Python-based, cross-platform)
```

Target:
```
Scaffolding via MCP tools (Tier 2 agent interface, per ADR-045)
```

---

### Tests

**SKIPPED:** No Python code changes. Tests are grep-based verification (see Ground Truth Verification). The full pytest suite runs unchanged to verify no regressions.

### Call Chain

```
Agent reads command/agent file
    |
    +-> Encounters `just <recipe>` reference   [BEFORE]
    |       -> shell subprocess via Bash tool
    |
    +-> Encounters `mcp__haios-operations__<tool>(args)` reference   [AFTER]
            -> direct MCP tool call (no subprocess)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| MCP invocation syntax | `mcp__haios-operations__<tool>(args)` | Matches existing MCP call syntax agents already use (e.g., `mcp__haios-memory__memory_search_with_experience`). Consistent with WORK-225 migration pattern. |
| `just commit-session` in new-checkpoint.md | Keep — left untouched | The `just commit-session` in new-checkpoint.md Step 3 is a git operation; no MCP equivalent. Only `just scaffold checkpoint` in Step 1 is migrated. |
| `haios.md` `just update-status-slim` replacement | Replace with `hierarchy_update_status(work_id, status)` | WORK.md acceptance criteria explicitly states: "haios.md uses hierarchy_update_status MCP tool instead of just update-status-slim". The MCP tool serves a narrower purpose (per-work-item status) vs the old slim refresh (all items), but it is the designated replacement. |
| `close.md` Step 3d `just update-status` | Replace with `hierarchy_update_status(work_id, status)` | WORK.md acceptance criteria: "close.md uses hierarchy_update_status instead of just update-status". The step refreshes status as part of closure; MCP tool handles this per-item. |
| Text-only approach, no Python changes | Markdown edit only | WORK.md context confirms: "This is a text-only migration of .md command and agent files." No Python code touched. |
| Replace prose references too, not just code blocks | Both code blocks and prose updated | Consistency: agents read full text. If prose still says `just adr`, agents may be confused. Replace all occurrences in each file. |
| `just validate` in README.md | Keep — not in migration scope | `just validate` has no MCP equivalent in the current server. WORK.md does not list it in acceptance criteria. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| `just commit-session` in new-checkpoint.md Step 3 | Keep — no MCP equivalent | Ground Truth: verify this line was NOT changed |
| `just validate` in README.md | Keep — not in migration scope | Ground Truth: `just validate` retained in README |
| `haios.md` context for `hierarchy_update_status` args | Prose update clarifies work_id + status required | Ground Truth: `just update-status-slim` absent, `hierarchy_update_status` present |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Over-migration: removing `just` calls that have no MCP equivalent | M | Scope boundary enforced by WORK.md acceptance criteria. Only listed operations replaced. |
| Inconsistent MCP syntax (wrong tool name or args) | H | MCP signatures verified against mcp_server.py: `scaffold_plan(work_id, title)`, `scaffold_work(title, work_id=None)`, `scaffold_investigation(work_id, title)`, `scaffold_checkpoint(session_number, title)`, `scaffold_adr(adr_number, title)`, `queue_ready()`, `hierarchy_update_status(work_id, status)`, `hierarchy_close_work(work_id)` |
| Missing occurrences: `just` command appears in prose AND code blocks | M | Grep each file after edit for remaining `just <mapped-recipe>` patterns to catch misses |
| `haios.md` semantic gap: `update-status-slim` refreshed all items; `hierarchy_update_status` is per-item | L | Document clearly in prose update. The step's purpose shifts from "bulk refresh" to "ensure active item status is current." This is acceptable per WORK.md AC. |

---

## Layer 2: Implementation Steps

### Step 1: Migrate new-plan.md (scaffold_plan + scaffold_work)
- **spec_ref:** Layer 1 > File-by-File Specification > File 1
- **input:** `.claude/commands/new-plan.md` exists and is readable
- **action:** Apply changes 1a through 1d: replace `just work` with `scaffold_work` MCP in prerequisite, replace `just plan` references (3 occurrences) with `scaffold_plan` MCP, update error message, update section prose
- **output:** `new-plan.md` updated, no `just plan` or `just work` remaining
- **verify:** `grep "just plan\|just work" .claude/commands/new-plan.md` returns 0 matches

### Step 2: Migrate new-work.md (scaffold_work)
- **spec_ref:** Layer 1 > File-by-File Specification > File 2
- **input:** `.claude/commands/new-work.md` exists
- **action:** Apply changes 2a-2c: replace all 3 occurrences of `just work WORK-031` with `scaffold_work` MCP invocations
- **output:** `new-work.md` updated, no `just work` remaining
- **verify:** `grep "just work" .claude/commands/new-work.md` returns 0 matches

### Step 3: Migrate new-investigation.md (scaffold_investigation + scaffold_work)
- **spec_ref:** Layer 1 > File-by-File Specification > File 3
- **input:** `.claude/commands/new-investigation.md` exists
- **action:** Apply changes 3a-3e: replace `just work` with `scaffold_work` MCP in step 1, replace `just inv` references (4 occurrences: lines 41, 44, 61, 66) with `scaffold_investigation` MCP, update prose
- **output:** `new-investigation.md` updated, no `just inv` or `just work` remaining
- **verify:** `grep "just inv\|just work" .claude/commands/new-investigation.md` returns 0 matches

### Step 4: Migrate new-checkpoint.md (scaffold_checkpoint)
- **spec_ref:** Layer 1 > File-by-File Specification > File 4
- **input:** `.claude/commands/new-checkpoint.md` exists
- **action:** Apply change 4a: replace `just scaffold checkpoint` with `scaffold_checkpoint` MCP; leave `just commit-session` in Step 3 unchanged
- **output:** `new-checkpoint.md` updated; `just commit-session` retained
- **verify:** `grep "just scaffold checkpoint" .claude/commands/new-checkpoint.md` returns 0 matches; `grep "just commit-session" .claude/commands/new-checkpoint.md` returns 1 match (retained)

### Step 5: Migrate new-adr.md (scaffold_adr)
- **spec_ref:** Layer 1 > File-by-File Specification > File 5
- **input:** `.claude/commands/new-adr.md` exists
- **action:** Apply changes 5a-5b: replace `just adr` references (2 occurrences) with `scaffold_adr` MCP, update prose
- **output:** `new-adr.md` updated, no `just adr` remaining
- **verify:** `grep "just adr" .claude/commands/new-adr.md` returns 0 matches

### Step 6: Migrate close.md (hierarchy_update_status)
- **spec_ref:** Layer 1 > File-by-File Specification > File 6
- **input:** `.claude/commands/close.md` exists
- **action:** Apply change 6a: replace `just update-status` with `hierarchy_update_status` MCP in Step 3d, update prose note about `just ready` → `queue_ready()`
- **output:** `close.md` updated; no `just update-status` (bare) remaining
- **verify:** `grep "just update-status[^-]" .claude/commands/close.md` returns 0 matches

### Step 7: Migrate ready.md (queue_ready)
- **spec_ref:** Layer 1 > File-by-File Specification > File 7
- **input:** `.claude/commands/ready.md` exists
- **action:** Apply change 7a: replace `just ready` with `queue_ready()` MCP, update section prose
- **output:** `ready.md` updated; no `just ready` remaining
- **verify:** `grep "just ready" .claude/commands/ready.md` returns 0 matches

### Step 8: Migrate haios.md (hierarchy_update_status)
- **spec_ref:** Layer 1 > File-by-File Specification > File 8
- **input:** `.claude/commands/haios.md` exists
- **action:** Apply change 8a: replace `just update-status-slim` with `hierarchy_update_status` MCP invocation, update surrounding prose
- **output:** `haios.md` updated; no `just update-status-slim` remaining
- **verify:** `grep "just update-status-slim" .claude/commands/haios.md` returns 0 matches

### Step 9: Migrate close-work-cycle-agent.md (hierarchy_close_work)
- **spec_ref:** Layer 1 > File-by-File Specification > File 9
- **input:** `.claude/agents/close-work-cycle-agent.md` exists
- **action:** Apply changes 9a-9c: replace 3 occurrences of `just close-work` with `hierarchy_close_work` MCP in Process section, Governance Gates table, and Edge Cases table
- **output:** `close-work-cycle-agent.md` updated; no `just close-work` remaining
- **verify:** `grep "just close-work" .claude/agents/close-work-cycle-agent.md` returns 0 matches

### Step 10: Migrate validation-agent.md (hierarchy_update_status)
- **spec_ref:** Layer 1 > File-by-File Specification > File 10
- **input:** `.claude/agents/validation-agent.md` exists
- **action:** Apply change 10a: replace `just update-status-slim` with `hierarchy_update_status` MCP invocation in Tips section
- **output:** `validation-agent.md` updated; no `just update-status-slim` remaining
- **verify:** `grep "just update-status-slim" .claude/agents/validation-agent.md` returns 0 matches

### Step 11: Update README.md
- **spec_ref:** Layer 1 > File-by-File Specification > File 11
- **input:** `.claude/commands/README.md` exists
- **action:** Apply changes 11a-11b: update Available Commands table Implementation column for 5 scaffold commands, update Scaffold Commands section prose
- **output:** `README.md` updated; `just plan`, `just work`, `just inv`, `just adr`, `just checkpoint` recipe references updated to MCP tool names
- **verify:** `grep "just plan\|just work\|just inv\b\|just adr\b" .claude/commands/README.md` returns 0 matches for those targets; `just validate` and `just scaffold report` retained (not in scope)

### Step 12: Full regression check
- **spec_ref:** Ground Truth Verification > Tests
- **input:** All 11 steps complete
- **action:** Run full pytest suite
- **output:** All existing tests pass (no regressions from markdown-only changes)
- **verify:** `pytest tests/ -v --tb=short` exits 0 with 0 new failures

---

## Ground Truth Verification

<!-- Computable verification protocol.
     Every line has a command and expected output.
     The CHECK agent runs these mechanically — no judgment needed. -->

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/ -v --tb=short` | 0 new failures vs pre-migration baseline (markdown-only changes cannot break Python tests) |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| new-plan.md: scaffold_plan MCP | `grep "just plan" .claude/commands/new-plan.md` | 0 matches |
| new-work.md: scaffold_work MCP | `grep "just work" .claude/commands/new-work.md` | 0 matches |
| new-investigation.md: scaffold_investigation MCP | `grep "just inv" .claude/commands/new-investigation.md` | 0 matches |
| new-checkpoint.md: scaffold_checkpoint MCP | `grep "just scaffold checkpoint" .claude/commands/new-checkpoint.md` | 0 matches |
| new-adr.md: scaffold_adr MCP | `grep "just adr" .claude/commands/new-adr.md` | 0 matches |
| close.md: hierarchy_update_status MCP | `grep "just update-status[^-]" .claude/commands/close.md` | 0 matches |
| ready.md: queue_ready MCP | `grep "just ready" .claude/commands/ready.md` | 0 matches |
| haios.md: hierarchy_update_status MCP | `grep "just update-status-slim" .claude/commands/haios.md` | 0 matches |
| close-work-cycle-agent.md: hierarchy_close_work MCP | `grep "just close-work" .claude/agents/close-work-cycle-agent.md` | 0 matches |
| validation-agent.md: hierarchy_update_status MCP | `grep "just update-status-slim" .claude/agents/validation-agent.md` | 0 matches |
| README.md references updated | `grep "just plan\|just work\|just inv\b\|just adr\b\|just checkpoint" .claude/commands/README.md` | 0 matches for these Tier-2 scaffold ops |
| README.md Scaffold Commands prose updated | `grep "just scaffold.*recipe" .claude/commands/README.md` | 0 matches |
| close.md: `just ready` note migrated to `queue_ready()` | `grep "just ready" .claude/commands/close.md` | 0 matches |

### MCP Tool Name Cross-Check

| Command | Expected |
|---------|----------|
| `grep -cE "def (scaffold_plan\|scaffold_work\|scaffold_investigation\|scaffold_checkpoint\|scaffold_adr\|queue_ready\|hierarchy_update_status\|hierarchy_close_work)\b" .claude/haios/haios_ops/mcp_server.py` | 8 (all 8 mapped tools exist in server) |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| `just commit-session` retained in new-checkpoint.md (git — no MCP equiv) | `grep "just commit-session" .claude/commands/new-checkpoint.md` | 1 match (retained) |
| `just validate` retained in README (not in scope) | `grep "just validate" .claude/commands/README.md` | 1 match (retained) |
| MCP tool names present in new-plan.md | `grep "scaffold_plan\|scaffold_work" .claude/commands/new-plan.md` | 2+ matches |
| MCP tool names present in close-work-cycle-agent.md | `grep "hierarchy_close_work" .claude/agents/close-work-cycle-agent.md` | 3+ matches |
| MCP tool name present in validation-agent.md | `grep "hierarchy_update_status" .claude/agents/validation-agent.md` | 1+ match |
| MCP tool name present in haios.md | `grep "hierarchy_update_status" .claude/commands/haios.md` | 1+ match |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 12 verify — no pytest regressions)
- [ ] All WORK.md deliverables verified (table above — 0 stale `just` matches for each mapped operation)
- [ ] `just commit-session` retained in new-checkpoint.md (git has no MCP equivalent)
- [ ] `just validate` retained in README.md (not in migration scope)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> For this text migration: "grep returns 0" proves old patterns removed. "grep returns 1+" proves new patterns inserted.

---

## Memory Query Results

Queried memory for prior patterns on "MCP migration command agent markdown just recipe replacement". WORK-225 plan (completed S456) is the canonical prior pattern — it is directly referenced by WORK.md and was used as the template for this plan. Key patterns applied:

- Same 4-layer plan structure as WORK-225 plan
- Same "SKIPPED" rationale for consumer files and test files
- Same Open Decisions table pattern for scope boundary decisions
- Same grep-based Ground Truth Verification (not pytest-based, since .md files don't break Python tests)
- MCP invocation syntax `mcp__haios-operations__<tool>(args)` follows WORK-225 established pattern

No additional novel patterns found — WORK-225 is the sole relevant prior.

---

## References

- `docs/work/active/WORK-230/WORK.md` — Work item with migration map and deliverables
- `docs/work/active/WORK-225/WORK.md` — Prior migration (skills) — pattern to follow
- `docs/work/active/WORK-225/plans/PLAN.md` — Reference plan structure
- `docs/work/active/WORK-228/WORK.md` — Parent audit that identified these 11 files
- `.claude/haios/haios_ops/mcp_server.py` — MCP tool implementations (function signatures verified at lines 501, 535, 572, 602, 632, 248, 760, 808)
- `docs/ADR/ADR-045-three-tier-entry-point-architecture.md` — Tier 2 = MCP tools architectural rationale

---
