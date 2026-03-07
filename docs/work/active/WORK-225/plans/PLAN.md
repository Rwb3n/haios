---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-25
backlog_id: WORK-225
title: "Migrate Skill Consumers from Just Recipes to MCP Operations Tools"
author: Hephaestus
lifecycle_phase: plan
session: 456
generated: 2026-02-25
last_updated: 2026-02-25T15:45:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-225/WORK.md"
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
# Implementation Plan: Migrate Skill Consumers from Just Recipes to MCP Operations Tools

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

Migrate 9 skill/command markdown files to reference MCP tool names (e.g., `cycle_set`, `hierarchy_close_work`, `coldstart_orchestrator`) instead of `just` recipe names for Tier 2 agent operations, completing CH-066 exit criterion 2.

---

## Open Decisions

<!-- No operator_decisions field in WORK.md — no unresolved decisions. -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| git-backed operations in checkpoint-cycle | Keep `just commit-session` / `just session-end` OR migrate to MCP | Keep `just commit-session` — no MCP equivalent exists for git commit | WORK.md deliverable 7 explicitly notes: "just commit-session remains (git — no MCP equivalent)". The MCP server has no git tooling. |
| `just set-queue` in survey-cycle | Migrate or skip | Skip — not in migration map | `just set-queue` is not in the WORK.md migration map. It is a queue queue-selection concern separate from the 8 targeted operations. |
| `just checkpoint-latest` in session-start-ceremony | Migrate or skip | Skip — no MCP equivalent | Same rationale as `just commit-session`: git/checkpoint filesystem operations have no MCP equivalent in current server. Retain as Tier 3. |

---

## Layer 0: Inventory

<!-- MUST complete before any design work. Map the blast radius.
     Producer: plan-author agent
     Consumer: all downstream agents (DO, CHECK, critique) -->

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/commands/coldstart.md` | MODIFY | 2 |
| `.claude/skills/survey-cycle/SKILL.md` | MODIFY | 2 |
| `.claude/skills/close-work-cycle/SKILL.md` | MODIFY | 2 |
| `.claude/skills/checkpoint-cycle/SKILL.md` | MODIFY | 2 |
| `.claude/skills/implementation-cycle/phases/DO.md` | MODIFY | 2 |
| `.claude/skills/implementation-cycle/phases/CHECK.md` | MODIFY | 2 |
| `.claude/skills/implementation-cycle/phases/DONE.md` | MODIFY | 2 |
| `.claude/skills/session-start-ceremony/SKILL.md` | MODIFY | 2 |
| `.claude/skills/session-end-ceremony/SKILL.md` | MODIFY | 2 |

### Consumer Files

<!-- These markdown files ARE the skill definitions agents read. No separate runtime consumers.
     Tests reference just commands only through these skill files — no Python test files migrate.
     No README updates needed: skill files are self-contained references. -->

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| N/A — skill files are terminal consumers | — | — | — |

**SKIPPED:** Consumer file table is N/A. These markdown files are themselves the consumer artifact. Agents read them directly. There are no Python importers or downstream runtime code paths that reference the specific `just` commands being replaced.

### Test Files

**SKIPPED:** This is a text-only migration of markdown files. No Python code changes. No new test files required. Verification is via grep (no `just` strings remaining in the 9 target files for the 8 mapped operations). The constraint "No regressions: all existing tests pass" is verified by running the full pytest suite unchanged.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | No new files |
| Files to modify | 9 | Primary Files table (all MODIFY rows) |
| Tests to write | 0 | Text-only migration, no Python changes |
| Total blast radius | 9 | 9 markdown files |

---

## Layer 1: Specification

<!-- The contract that the DO agent implements.
     This is a text-substitution migration. For each file, the spec shows:
     - Which `just` references to replace
     - The exact MCP tool call to substitute -->

### Current State

**Behavior:** Skills and commands call `just` recipes directly in their instruction text (bash code blocks and prose). Agents reading these skills execute `just` recipes as their Tier 2 operations.

**Problem:** ADR-045 establishes MCP tools as Tier 2 (agent interface). `just` recipes are Tier 3 (terminal/orchestration). Agents should use MCP tools exclusively for Tier 2 operations. CH-066 exit criterion 2 requires "Just recipes retired for agent use — MCP tools replace Tier 2 operations."

### Desired State

**Behavior:** Skills and commands reference MCP tool names (e.g., `cycle_set(...)`, `hierarchy_close_work(...)`) in their instruction text. Where bash blocks showed `just <recipe>`, they now show the MCP invocation pattern.

**Result:** Agents reading the migrated skills invoke MCP tools natively. No `just` subprocess overhead for Tier 2 operations.

---

### File-by-File Specification

#### File 1 (MODIFY): `.claude/commands/coldstart.md`

**Changes:**

**Change 1a — Step 2 main coldstart call:**

Current:
```bash
just coldstart-orchestrator
```

Target:
```
mcp__haios-operations__coldstart_orchestrator()
```

**Change 1b — Step 2 tier-explicit calls:**

Current:
```bash
just coldstart-orchestrator --tier full     # New epoch/arc work, first session after transition
just coldstart-orchestrator --tier light    # Continuation of prior session work
just coldstart-orchestrator --tier minimal  # Housekeeping (doc fixes, drift correction)
```

Target:
```
mcp__haios-operations__coldstart_orchestrator(tier="full")    # New epoch/arc work, first session after transition
mcp__haios-operations__coldstart_orchestrator(tier="light")   # Continuation of prior session work
mcp__haios-operations__coldstart_orchestrator(tier="minimal") # Housekeeping (doc fixes, drift correction)
```

**Change 1c — Step 4 session-start:**

Current:
```bash
just session-start {N}
```

Target:
```
mcp__haios-operations__session_start(session_number=N)
```

**Change 1d — Step 6 survey-cycle reference:** No change needed. The Skill() invocation is not a just recipe.

**Change 1e — Escape Hatch section:**

Current:
```bash
just coldstart-orchestrator --extend epoch operations
```

Target:
```
mcp__haios-operations__coldstart_orchestrator(tier="full")
```
(Note: `--extend` is not yet implemented. Update prose to indicate `--extend` was a Tier 3 flag; use the MCP tool with `tier="full"` as the workaround.)

---

#### File 2 (MODIFY): `.claude/skills/survey-cycle/SKILL.md`

**Changes:**

**Change 2a — Logic step 2, just ready reference:**

Current (line 25):
```
   - Alternatively: `just ready` for flat unordered list (backward compat)
```

Target:
```
   - Alternatively: `mcp__haios-operations__queue_ready()` for flat unordered list (backward compat)
```

**Change 2b — just queue reference:**

Current (line 24):
```
   - Run `just queue [name]` for ordered items (default: "default" queue)
```

Target:
```
   - Run `mcp__haios-operations__queue_list(queue_name="{queue_name}")` for ordered items (default: "default")
```

**Change 2c — Frontmatter `recipes:` field:**

Current (lines 8-9):
```yaml
recipes:
- ready
- queue
```

Target: Remove `ready` and `queue` entries from the `recipes:` list. No skill frontmatter schema exists (`.claude/haios/schemas/` has no skill schema file), so no `mcp_tools:` field is added. Simply delete the two list items, leaving `recipes: []` (empty list). The `recipes:` key is retained for forward compatibility.

**Note on `just set-queue`:** Line 32 `just set-queue {queue_name}` is intentionally left unchanged per Open Decisions — it is not in the WORK.md migration map and has no direct MCP equivalent in the current server.

---

#### File 3 (MODIFY): `.claude/skills/close-work-cycle/SKILL.md`

**Changes:**

**Change 3a — VALIDATE On Entry:**

Current:
```bash
just set-cycle close-work-cycle VALIDATE {work_id}
```

Target:
```
mcp__haios-operations__cycle_set(cycle="close-work-cycle", phase="VALIDATE", work_id="{work_id}")
```

**Change 3b — ARCHIVE On Entry:**

Current:
```bash
just set-cycle close-work-cycle ARCHIVE {work_id}
```

Target:
```
mcp__haios-operations__cycle_set(cycle="close-work-cycle", phase="ARCHIVE", work_id="{work_id}")
```

**Change 3c — ARCHIVE delegation prompt (line 185):**

Current (in Task subagent prompt):
```
    1. Run: just close-work {work_id}
```

Target:
```
    1. Run: mcp__haios-operations__hierarchy_close_work(work_id="{work_id}")
```

**Change 3d — ARCHIVE Actions step 1 (just close-work):**

Current:
```bash
   just close-work {id}
```

Target:
```
   mcp__haios-operations__hierarchy_close_work(work_id="{id}")
```

Also update the prose note: "Run atomic close-work recipe:" → "Run atomic hierarchy_close_work MCP tool:"

**Change 3e — CHAIN On Entry:**

Current:
```bash
just set-cycle close-work-cycle CHAIN {work_id}
```

Target:
```
mcp__haios-operations__cycle_set(cycle="close-work-cycle", phase="CHAIN", work_id="{work_id}")
```

**Change 3f — CHAIN delegation prompt (just ready):**

Current (in Task subagent prompt, line 252):
```
    2. Run: just ready
```

Target:
```
    2. Run: mcp__haios-operations__queue_ready()
```

**Change 3g — CHAIN route step 3 (just ready):**

Current:
```
3. Query next work: `just ready`
```

Target:
```
3. Query next work: `mcp__haios-operations__queue_ready()`
```

**Change 3h — On Complete (just clear-cycle):**

Current:
```bash
just clear-cycle
```

Target:
```
mcp__haios-operations__cycle_clear()
```

**Change 3i — Quick Reference table (Archive row):**

Current:
```
| ARCHIVE | Is work file archived? | Run `just close-work` |
```

Target:
```
| ARCHIVE | Is work file archived? | Run `mcp__haios-operations__hierarchy_close_work(work_id)` |
```

**Change 3j — Quick Reference table (CHAIN row):**

Current:
```
| CHAIN | Is next work identified? | Run `just ready` |
```

Target:
```
| CHAIN | Is next work identified? | Run `mcp__haios-operations__queue_ready()` |
```

**Change 3k — Composition Map (ARCHIVE row):**

Current:
```
| ARCHIVE | Bash(just close-work) | - |
```

Target:
```
| ARCHIVE | mcp__haios-operations__hierarchy_close_work | - |
```

**Change 3l — CHAIN Tools line:**

Current:
```
**Tools:** Bash(just ready), Read, Skill(checkpoint-cycle, routing-gate)
```

Target:
```
**Tools:** mcp__haios-operations__queue_ready, Read, Skill(checkpoint-cycle, routing-gate)
```

**Change 3m — Update-status reference in ARCHIVE:**

The prose note "- Run update-status" inside `just close-work` description:

Current text (explaining what `just close-work` does atomically):
```
   - Run update-status
```

Target (since `hierarchy_close_work` absorbs both close and cascade):
```
   - Run StatusPropagator cascade (absorbed into hierarchy_close_work)
```

---

#### File 4 (MODIFY): `.claude/skills/checkpoint-cycle/SKILL.md`

**Changes:**

**Change 4a — CAPTURE phase commit block:**

Current:
```bash
just commit-session {session} "{title}"
just session-end {session}
```

Target:
```bash
just commit-session {session} "{title}"
mcp__haios-operations__session_end(session_number={session})
```

**Rationale:** `just commit-session` is a git operation (no MCP equivalent). Only `just session-end` has an MCP equivalent (`session_end` tool). Keep git command, replace only the session-end.

---

#### File 5 (MODIFY): `.claude/skills/implementation-cycle/phases/DO.md`

**Changes:**

**Change 5a — On Entry block:**

Current:
```bash
just set-cycle implementation-cycle DO {work_id}
```

Target:
```
mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="DO", work_id="{work_id}")
```

---

#### File 6 (MODIFY): `.claude/skills/implementation-cycle/phases/CHECK.md`

**Changes:**

**Change 6a — On Entry block:**

Current:
```bash
just set-cycle implementation-cycle CHECK {work_id}
```

Target:
```
mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="CHECK", work_id="{work_id}")
```

**Change 6b — `just update-status` reference in discoverable artifacts section:**

Current (line 56):
```
- Run `just update-status-slim`
```

Target (note: `just update-status-slim` is a Tier 3 slim-status refresh, not directly mapped; leave as-is per scope boundary):

**SKIPPED:** `just update-status-slim` is NOT in the WORK.md migration map. It is a status refresh utility distinct from `just update-status` (which is absorbed into `hierarchy_close_work`). Leave unchanged.

---

#### File 7 (MODIFY): `.claude/skills/implementation-cycle/phases/DONE.md`

**Changes:**

**Change 7a — On Entry block:**

Current:
```bash
just set-cycle implementation-cycle DONE {work_id}
```

Target:
```
mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="DONE", work_id="{work_id}")
```

---

#### File 8 (MODIFY): `.claude/skills/session-start-ceremony/SKILL.md`

**Changes:**

**Change 8a — Step 3 session-start execution:**

Current:
```
- Execute: `just session-start {N}`
- This invokes `governance_events.log_session_start(session, "Hephaestus")`
```

Target:
```
- Execute: `mcp__haios-operations__session_start(session_number=N)`
- This invokes `governance_events.log_session_start(session, "Hephaestus")` internally
```

**Change 8b — SKIP: `just checkpoint-latest` in Step 6:**

`just checkpoint-latest` in Step 6 is intentionally retained unchanged — no MCP equivalent exists (per Open Decisions row 3). DO agent MUST NOT modify this line.

**Change 8c — Integration with Coldstart section:**

Current:
```
  -> just session-start N          (this ceremony: state change + event log)
```

Target:
```
  -> mcp__haios-operations__session_start(session_number=N)   (this ceremony: state change + event log)
```

---

#### File 9 (MODIFY): `.claude/skills/session-end-ceremony/SKILL.md`

**Changes:**

**Change 9a — Step 3 session-end execution:**

Current:
```
- Execute: `just session-end {N}`
- This invokes `governance_events.log_session_end(session, "Hephaestus")`
```

Target:
```
- Execute: `mcp__haios-operations__session_end(session_number=N)`
- This invokes `governance_events.log_session_end(session, "Hephaestus")` internally
```

---

### Tests

**SKIPPED:** No Python code changes. Tests are grep-based verification (see Ground Truth Verification). The full pytest suite runs unchanged to verify no regressions.

### Call Chain

```
Agent reads skill/command file
    |
    +-> Encounters `just <recipe>` reference   [BEFORE]
    |       -> shell subprocess via Bash tool
    |
    +-> Encounters `mcp__haios-operations__<tool>()` reference   [AFTER]
            -> direct MCP tool call (no subprocess)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| MCP invocation syntax | `mcp__haios-operations__<tool>(args)` | Matches existing MCP call syntax agents already use for memory tools. Consistent with how agents call `mcp__haios-memory__memory_search_with_experience`. |
| `just commit-session` retention | Keep as `just commit-session` | Git commit has no MCP equivalent. WORK.md deliverable 7 explicitly notes this: "just commit-session remains (git — no MCP equivalent)". |
| `just update-status-slim` retention in CHECK.md | Keep unchanged | Not in the WORK.md migration map. Distinct from `just update-status` (status propagation). Slim-status refresh is a Tier 3 utility. |
| `just set-queue` in survey-cycle | Keep unchanged | Not in WORK.md migration map. No direct MCP equivalent in current server. |
| Text-only approach, no Python changes | Markdown edit only | WORK.md context confirms: "This is a text-only migration of skill/command markdown files". No Python code touched. |
| Replace prose references too, not just code blocks | Both code blocks and prose updated | Consistency: agents read full text. If prose still says `just ready`, agents may be confused. Replace all occurrences in each file. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| `just commit-session` in checkpoint-cycle | Keep — no MCP equivalent | Ground Truth: verify this line was NOT changed |
| `just update-status-slim` in CHECK.md | Keep — not in migration scope | Ground Truth: verify file only lost `cycle_set` line |
| `just set-queue` in survey-cycle | Keep — not in scope | Ground Truth: count of `just` refs after migration |
| `just checkpoint-latest` in session-start-ceremony | Keep — no MCP equivalent | Ground Truth: verify this line was NOT changed |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Over-migration: removing `just` calls that have no MCP equivalent | M | Scope boundary enforced by WORK.md migration map. Only 8 mapped operations replaced. |
| Inconsistent MCP syntax (wrong tool name or args) | H | Cross-reference mcp_server.py function signatures for exact names and param names before editing |
| Missing occurrences: `just` command appears in prose AND code blocks | M | Grep each file after edit for remaining `just <mapped-recipe>` patterns to catch misses |
| Survey-cycle `just queue` vs `just ready` — both need migration | L | Both addressed in File 2 specification above |

---

## Layer 2: Implementation Steps

### Step 1: Migrate coldstart.md (coldstart-orchestrator + session-start)
- **spec_ref:** Layer 1 > File-by-File Specification > File 1
- **input:** `.claude/commands/coldstart.md` exists and is readable
- **action:** Apply changes 1a through 1e: replace 3 occurrences of `just coldstart-orchestrator` (with and without flags) with `mcp__haios-operations__coldstart_orchestrator(tier=...)`, replace `just session-start {N}` with `mcp__haios-operations__session_start(session_number=N)`
- **output:** `coldstart.md` updated, no `just coldstart-orchestrator` or `just session-start` remaining
- **verify:** `grep "just coldstart-orchestrator\|just session-start" .claude/commands/coldstart.md` returns 0 matches

### Step 2: Migrate survey-cycle SKILL.md (queue_ready + queue_list)
- **spec_ref:** Layer 1 > File-by-File Specification > File 2
- **input:** `.claude/skills/survey-cycle/SKILL.md` exists
- **action:** Apply changes 2a-2c: replace `just ready` with `mcp__haios-operations__queue_ready()`, replace `just queue [name]` with `mcp__haios-operations__queue_list(queue_name="{queue_name}")`, update frontmatter `recipes:` field to remove stale `ready`/`queue` entries
- **output:** `survey-cycle/SKILL.md` updated; `just set-queue` intentionally left unchanged; frontmatter updated
- **verify:** `grep "just ready\|just queue " .claude/skills/survey-cycle/SKILL.md` returns 0 matches

### Step 3: Migrate close-work-cycle SKILL.md (cycle_set + hierarchy_close_work + queue_ready + cycle_clear)
- **spec_ref:** Layer 1 > File-by-File Specification > File 3
- **input:** `.claude/skills/close-work-cycle/SKILL.md` exists
- **action:** Apply changes 3a through 3m: replace all `just set-cycle` with `cycle_set`, `just close-work` with `hierarchy_close_work`, `just ready` with `queue_ready()`, `just clear-cycle` with `cycle_clear()`
- **output:** All 4 mapped operations replaced; prose and code blocks consistent
- **verify:** `grep "just set-cycle\|just close-work\|just clear-cycle" .claude/skills/close-work-cycle/SKILL.md` returns 0 matches; `grep "just ready" .claude/skills/close-work-cycle/SKILL.md` returns 0 matches

### Step 4: Migrate checkpoint-cycle SKILL.md (session_end only)
- **spec_ref:** Layer 1 > File-by-File Specification > File 4
- **input:** `.claude/skills/checkpoint-cycle/SKILL.md` exists
- **action:** Apply change 4a: replace `just session-end {session}` with `mcp__haios-operations__session_end(session_number={session})`; leave `just commit-session` unchanged
- **output:** `checkpoint-cycle/SKILL.md` updated; `just commit-session` retained
- **verify:** `grep "just session-end" .claude/skills/checkpoint-cycle/SKILL.md` returns 0 matches; `grep "just commit-session" .claude/skills/checkpoint-cycle/SKILL.md` returns 1 match (retained)

### Step 5: Migrate implementation-cycle phase files (DO, CHECK, DONE — cycle_set)
- **spec_ref:** Layer 1 > File-by-File Specification > Files 5, 6, 7
- **input:** All three phase files exist
- **action:** Apply changes 5a, 6a, 7a: replace `just set-cycle implementation-cycle DO/CHECK/DONE {work_id}` with `mcp__haios-operations__cycle_set(cycle="implementation-cycle", phase="DO/CHECK/DONE", work_id="{work_id}")` in respective files
- **output:** All three phase files updated
- **verify:** `grep "just set-cycle" .claude/skills/implementation-cycle/phases/DO.md .claude/skills/implementation-cycle/phases/CHECK.md .claude/skills/implementation-cycle/phases/DONE.md` returns 0 matches

### Step 6: Migrate session-start-ceremony SKILL.md (session_start)
- **spec_ref:** Layer 1 > File-by-File Specification > File 8
- **input:** `.claude/skills/session-start-ceremony/SKILL.md` exists
- **action:** Apply changes 8a and 8c: replace `just session-start {N}` with `mcp__haios-operations__session_start(session_number=N)` in Step 3 and Integration section. SKIP `just checkpoint-latest` in Step 6 (Change 8b — retain unchanged, no MCP equivalent)
- **output:** All `just session-start` references replaced
- **verify:** `grep "just session-start" .claude/skills/session-start-ceremony/SKILL.md` returns 0 matches

### Step 7: Migrate session-end-ceremony SKILL.md (session_end)
- **spec_ref:** Layer 1 > File-by-File Specification > File 9
- **input:** `.claude/skills/session-end-ceremony/SKILL.md` exists
- **action:** Apply change 9a: replace `just session-end {N}` with `mcp__haios-operations__session_end(session_number=N)`
- **output:** `just session-end` replaced
- **verify:** `grep "just session-end" .claude/skills/session-end-ceremony/SKILL.md` returns 0 matches

### Step 8: Full regression check
- **spec_ref:** Ground Truth Verification > Tests
- **input:** All 7 steps complete
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
| coldstart migrated: coldstart-orchestrator | `grep "just coldstart-orchestrator" .claude/commands/coldstart.md` | 0 matches |
| coldstart migrated: session-start | `grep "just session-start" .claude/commands/coldstart.md` | 0 matches |
| session-start-ceremony migrated | `grep "just session-start" .claude/skills/session-start-ceremony/SKILL.md` | 0 matches |
| session-end-ceremony migrated | `grep "just session-end" .claude/skills/session-end-ceremony/SKILL.md` | 0 matches |
| survey-cycle migrated: queue_ready | `grep "just ready" .claude/skills/survey-cycle/SKILL.md` | 0 matches |
| close-work-cycle migrated: hierarchy_close_work | `grep "just close-work" .claude/skills/close-work-cycle/SKILL.md` | 0 matches |
| close-work-cycle migrated: cycle_set | `grep "just set-cycle" .claude/skills/close-work-cycle/SKILL.md` | 0 matches |
| close-work-cycle migrated: cycle_clear | `grep "just clear-cycle" .claude/skills/close-work-cycle/SKILL.md` | 0 matches |
| implementation-cycle DO migrated: cycle_set | `grep "just set-cycle" .claude/skills/implementation-cycle/phases/DO.md` | 0 matches |
| implementation-cycle CHECK migrated: cycle_set | `grep "just set-cycle" .claude/skills/implementation-cycle/phases/CHECK.md` | 0 matches |
| implementation-cycle DONE migrated: cycle_set | `grep "just set-cycle" .claude/skills/implementation-cycle/phases/DONE.md` | 0 matches |
| checkpoint-cycle: session_end migrated | `grep "just session-end" .claude/skills/checkpoint-cycle/SKILL.md` | 0 matches |
| checkpoint-cycle: commit-session retained (git — no MCP equiv) | `grep "just commit-session" .claude/skills/checkpoint-cycle/SKILL.md` | 1 match (retained) |
| session-start-ceremony: checkpoint-latest retained (no MCP equiv) | `grep "just checkpoint-latest" .claude/skills/session-start-ceremony/SKILL.md` | 1 match (retained) |
| MCP tool names correct in coldstart.md | `grep "coldstart_orchestrator\|session_start" .claude/commands/coldstart.md` | 2+ matches |
| MCP tool names correct in close-work-cycle | `grep "hierarchy_close_work\|cycle_set\|cycle_clear\|queue_ready" .claude/skills/close-work-cycle/SKILL.md` | 4+ matches |

### MCP Tool Name Cross-Check

| Command | Expected |
|---------|----------|
| `grep -cE "def (hierarchy_close_work|cycle_set|cycle_clear|queue_ready|queue_list|session_start|session_end|coldstart_orchestrator)\b" .claude/haios/haios_ops/mcp_server.py` | 8 (all 8 mapped tools exist in server) |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| No stale `just set-cycle` in target skill files | `grep -r "just set-cycle" .claude/skills/close-work-cycle/ .claude/skills/implementation-cycle/phases/` | 0 matches |
| No stale `just close-work` (bare recipe) in target files | `grep "just close-work[^-]" .claude/skills/close-work-cycle/SKILL.md` | 0 matches |
| No stale `just session-start` across all target files | `grep -r "just session-start" .claude/commands/coldstart.md .claude/skills/session-start-ceremony/` | 0 matches |
| No stale `just session-end` across all target files | `grep -r "just session-end" .claude/skills/checkpoint-cycle/ .claude/skills/session-end-ceremony/` | 0 matches |
| `just set-queue` NOT touched (out of scope) | `grep "just set-queue" .claude/skills/survey-cycle/SKILL.md` | 1 match (retained, intentional) |
| survey-cycle frontmatter: stale recipes removed | `grep -A2 "^recipes:" .claude/skills/survey-cycle/SKILL.md` | `recipes: []` (no `ready` or `queue` entries) |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 8 verify — no pytest regressions)
- [ ] All WORK.md deliverables verified (table above — 0 stale `just` matches for each mapped operation)
- [ ] `just commit-session` retained in checkpoint-cycle (git has no MCP equivalent)
- [ ] `just set-queue` retained in survey-cycle (out of migration scope)
- [ ] `just update-status-slim` retained in CHECK.md (out of migration scope, distinct from `just update-status`)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> For this text migration: "grep returns 0" proves old patterns removed. "grep returns 1+" proves new patterns inserted.

---

## References

- `docs/work/active/WORK-225/WORK.md` — Work item with migration map and deliverables
- `.claude/haios/haios_ops/mcp_server.py` — MCP tool implementations (function signatures verified)
- `docs/ADR/ADR-045-three-tier-entry-point-architecture.md` — Tier 2 = MCP tools architectural rationale
- `docs/work/active/WORK-224/WORK.md` — Phase 3 parent (session 454 audit that identified this gap)
- `.claude/haios/epochs/E2_8/arcs/call/chapters/CH-066-MCPOperationsServer/CHAPTER.md` — Exit criterion 2 source

---
