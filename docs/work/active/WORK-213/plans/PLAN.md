---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-24
backlog_id: WORK-213
title: "Retro-Cycle Phase Reordering"
author: Hephaestus
lifecycle_phase: plan
session: 440
generated: 2026-02-24
last_updated: 2026-02-24T11:13:25

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-213/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete code blocks, not pseudocode"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: Retro-Cycle Phase Reordering

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

Reorder retro-cycle phases from REFLECT→DERIVE→EXTRACT→COMMIT to REFLECT→DERIVE→COMMIT→EXTRACT so that observations and K/S/S are persisted to memory immediately after synthesis (at COMMIT), and EXTRACT can reference live memory concept IDs when storing its classifications.

---

## Open Decisions

<!-- No operator_decisions field in WORK.md frontmatter — all decisions resolved via S439
     operator directive (memory refs 88137-88143). -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Phase order | EXTRACT before COMMIT vs COMMIT before EXTRACT | COMMIT before EXTRACT | S439 operator directive: COMMIT stores complete cognitive outputs (observations + K/S/S) immediately; EXTRACT then classifies with concept IDs traceable from birth |
| EXTRACT no-auto-spawn | Preserve or drop REQ-LIFECYCLE-004 | Preserve | REQ-LIFECYCLE-004 unchanged: extracted items stored to memory only, surfaced at triage |
| Context alert threshold | 19% (current) vs 15% (target) | 15% | S439 operator directive: 15% alert, 10% close territory, 5% emergency stop — in SKILL.md prose |
| EXTRACT input change | Pass reflect_findings vs pass reflect_findings + concept_ids | Pass reflect_findings + concept_ids | After reordering, COMMIT runs first and produces concept_ids; EXTRACT delegation prompt should include them for traceability |

---

## Layer 0: Inventory

<!-- MUST complete before any design work. Map the blast radius.
     Producer: plan-author agent
     Consumer: all downstream agents (DO, CHECK, critique) -->

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/skills/retro-cycle/SKILL.md` | MODIFY | 1 |

### Consumer Files

<!-- Files that reference retro-cycle phases or phase numbers/names.
     Consumers checked: close-work-cycle, session-end-ceremony, observation-triage-cycle,
     process-review-cycle, session-review-cycle, README.md -->

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `.claude/skills/close-work-cycle/SKILL.md` | Phase sequence string at lines 67-68, 81, 325 | `REFLECT->DERIVE->EXTRACT->COMMIT` | UPDATE to `REFLECT->DERIVE->COMMIT->EXTRACT` |
| `.claude/skills/README.md` | Phase sequence string at line 21 | `(REFLECT->DERIVE->EXTRACT->COMMIT)` | UPDATE to `(REFLECT->DERIVE->COMMIT->EXTRACT)` |
| `.claude/commands/close.md` | Phase sequence string at lines 77, 298 | `REFLECT -> DERIVE -> EXTRACT -> COMMIT` | UPDATE to `REFLECT -> DERIVE -> COMMIT -> EXTRACT` |

### Test Files

**SKIPPED:** This is a documentation/prose-only change to a SKILL.md file. No Python modules or code are modified. The acceptance criteria are verified via grep/read commands, not pytest. The existing skill test suite (`tests/test_existing_skills_not_marked_stub`) does not assert on phase ordering or percentage thresholds; it checks for `stub: true` markers.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | No new files |
| Files to modify | 4 | `.claude/skills/retro-cycle/SKILL.md`, `.claude/skills/close-work-cycle/SKILL.md`, `.claude/skills/README.md`, `.claude/commands/close.md` |
| Tests to write | 0 | Prose-only change, no code logic |
| Total blast radius | 4 | Primary SKILL.md + 3 consumer files |

---

## Layer 1: Specification

<!-- The contract that the DO agent implements.
     Producer: plan-author agent
     Consumer: DO agent -->

### Current State

The retro-cycle SKILL.md at `.claude/skills/retro-cycle/SKILL.md` has the following phase order and structure:

```
# Current phase numbering (lines 83-99 in The Cycle section):
Phase 0: SCALE ASSESSMENT
Phase 1: REFLECT    (inline)
Phase 2: DERIVE     (inline)
Phase 3: EXTRACT    (delegate haiku)  <-- classification first
Phase 4: COMMIT     (delegate haiku)  <-- persistence last

# Current Composition Map (lines 449-456):
| Phase 3: EXTRACT | classification from REFLECT | - | extracted_items list |
| Phase 4: COMMIT  | ingester_ingest             | 3 typed stores + closure summary | memory_concept_ids list |

# Current EXTRACT delegation prompt (lines 248-255):
Task(
  subagent_type='general-purpose',
  model='haiku',
  prompt='Execute retro-cycle EXTRACT phase for {work_id}.
    REFLECT findings ... {reflect_findings_text}
    Classify each actionable item. Output format per SKILL.md Phase 3 Classification table.
    Return: extracted_items list in YAML format.'
)

# Current COMMIT delegation prompt (lines 323-335):
Task(
  subagent_type='general-purpose',
  model='haiku',
  prompt='Execute retro-cycle COMMIT phase for {work_id}.
    reflect_findings: {reflect_findings_json}
    kss_directives: {kss_directives_json}
    extracted_items: {extracted_items_json}
    scaling: {scaling}
    Store each per SKILL.md Phase 4 Provenance Tags. Return: memory_concept_ids list.
    Verify: after each ingester_ingest ...'
)

# Current "Phase timeout" escape hatch (line 430):
| Phase timeout | Agent context approaching limits | Complete current phase, skip remaining, COMMIT what we have |

# No context threshold percentage currently in SKILL.md prose.
```

**Behavior:** REFLECT captures observations → DERIVE synthesizes K/S/S → EXTRACT classifies observations into typed items → COMMIT stores everything (REFLECT + K/S/S + EXTRACT items) to memory.

**Problem:** COMMIT runs last, meaning EXTRACT cannot reference memory concept IDs when classifying. K/S/S (complete cognitive outputs) sit unprotected in working memory while EXTRACT runs its 37K-token / 14-tool-call haiku delegation. Context exhaustion before COMMIT loses ALL stored signal. Context alert threshold is undocumented as a percentage.

---

### Desired State

The changes are confined to `.claude/skills/retro-cycle/SKILL.md`. The following sections require modification:

#### Change 1: Frontmatter description — update phase sequence string

**Location:** Line 6 (frontmatter `description` field)

**Current:**
```yaml
description: "Multi-step autonomous reflection with typed provenance for work closure.
  Replaces observation-capture-cycle with structured pipeline: REFLECT->DERIVE->EXTRACT->COMMIT."
```

**Target:**
```yaml
description: "Multi-step autonomous reflection with typed provenance for work closure.
  Replaces observation-capture-cycle with structured pipeline: REFLECT->DERIVE->COMMIT->EXTRACT."
```

---

#### Change 2: The Cycle diagram — swap Phase 3 and Phase 4

**Location:** Lines 83-99, "The Cycle" section

**Current:**
```
  |     +-> Phase 3: EXTRACT (Bugs, Features, Refactors, Upgrades)
  |     |     Confidence-tagged, priority-suggested, NO auto-spawn
  |     |
  |     +-> Phase 4: COMMIT (All to memory)
  |           Typed provenance: retro-reflect, retro-kss, retro-extract
  |           Also stores closure summary (absorbs MEMORY phase)
```

**Target:**
```
  |     +-> Phase 3: COMMIT (observations + K/S/S to memory)
  |     |     Typed provenance: retro-reflect, retro-kss
  |     |     Returns concept_ids for EXTRACT traceability
  |     |
  |     +-> Phase 4: EXTRACT (Bugs, Features, Refactors, Upgrades)
  |           Confidence-tagged, priority-suggested, NO auto-spawn
  |           Stores to memory with concept_ids from COMMIT
```

---

#### Change 3: Why 4 Phases table — swap EXTRACT and COMMIT rows

**Location:** Lines 110-113, "Why 4 Phases?" table

**Current:**
```markdown
| EXTRACT | Classification (what type of action?) | Bug/feature/refactor/upgrade with priority signal |
| COMMIT | Persistence (store with provenance) | Memory writes with typed tags |
```

**Target:**
```markdown
| COMMIT | Persistence (store with provenance) | Memory writes with typed tags — observations and K/S/S are complete, persist immediately |
| EXTRACT | Classification (what type of action?) | Bug/feature/refactor/upgrade with priority signal — references concept_ids from COMMIT |
```

---

#### Change 4: Phase 3 section — rename from EXTRACT to COMMIT, update content

**Location:** Lines 239-312, "## Phase 3: EXTRACT" section becomes "## Phase 3: COMMIT"

**Current heading and execution context:**
```markdown
## Phase 3: EXTRACT

> **Execution Context: DELEGATE to haiku subagent (S436 operator directive)**
> EXTRACT is mechanical classification — takes REFLECT observations and assigns type
> (bug/feature/refactor/upgrade), confidence, priority. No live session context required;
> the observations are written output from Phase 1. Delegate to save main-agent tokens.

**Delegation pattern:**
```

**Target heading and execution context:**
```markdown
## Phase 3: COMMIT

> **Execution Context: DELEGATE to haiku subagent (S436 operator directive)**
> COMMIT is mechanical persistence — calls ingester_ingest with structured outputs
> from REFLECT and DERIVE phases. No cognitive context required. Delegate to save
> main-agent tokens. Runs BEFORE EXTRACT so that observations and K/S/S are persisted
> immediately (complete cognitive outputs). EXTRACT receives the resulting concept_ids
> for traceability.
```

The Phase 3 body is replaced with the current Phase 4 COMMIT content (lines 315-418 in current file), with one modification to the delegation prompt: `extracted_items` is removed from COMMIT's inputs (EXTRACT has not run yet). Updated COMMIT delegation prompt:

```
Task(
  subagent_type='general-purpose',
  model='haiku',
  prompt='Execute retro-cycle COMMIT phase for {work_id}.
    reflect_findings: {reflect_findings_json}
    kss_directives: {kss_directives_json}
    scaling: {scaling}
    Store reflect_findings per retro-reflect provenance tag.
    Store kss_directives per retro-kss provenance tag.
    Store closure summary per closure:{work_id} provenance tag.
    Return: memory_concept_ids list (reflect_ids, kss_ids, closure_id).
    Verify: after each ingester_ingest, confirm concept_ids is non-empty (S407 silent-drop check).'
)
```

Note: `retro-extract` provenance store moves to Phase 4 EXTRACT (see Change 5).

The COMMIT "Provenance Tags" table is updated to remove the `retro-extract` row (it moves to EXTRACT):

**Current Provenance Tags table (3 rows):**
```markdown
| retro-reflect | `retro-reflect:{work_id}` | Raw 5-dimensional observations with evidence anchors | techne |
| retro-kss | `retro-kss:{work_id}` | Keep/Stop/Start directives with traceability | techne |
| retro-extract | `retro-extract:{work_id}` | Bug/feature/refactor/upgrade items with confidence, severity, and suggested priority | techne |
```

**Target Provenance Tags table (2 rows + note):**
```markdown
| retro-reflect | `retro-reflect:{work_id}` | Raw 5-dimensional observations with evidence anchors | techne |
| retro-kss | `retro-kss:{work_id}` | Keep/Stop/Start directives with traceability | techne |

Note: `retro-extract` provenance store runs in Phase 4 EXTRACT (after concept_ids available from COMMIT).
```

The "Storage Implementation" subsection retains the `retro-reflect` and `retro-kss` detail requirements. The `retro-extract` detail requirements move to Phase 4 EXTRACT.

The "Closure Summary" subsection is updated: remove `Extractions: {count}` from the template (EXTRACT has not run yet at COMMIT time). The closure summary template becomes:
```
content="Closure: {work_id} - {title}\nScale: {trivial|substantial}\nReflections: {count}\nK/S/S: {count}\nDoD-relevant: {count}"
```
Note: extraction count is no longer in the closure summary since COMMIT precedes EXTRACT. If extraction count is needed, it can be stored separately by Phase 4 EXTRACT.

---

#### Change 5: Phase 4 section — rename from COMMIT to EXTRACT, update content

**Location:** Lines 315-418 (current "## Phase 4: COMMIT") becomes "## Phase 4: EXTRACT"

**Target heading and execution context:**
```markdown
## Phase 4: EXTRACT

> **Execution Context: DELEGATE to haiku subagent (S436 operator directive)**
> EXTRACT is mechanical classification — takes REFLECT observations and assigns type
> (bug/feature/refactor/upgrade), confidence, priority. No live session context required;
> the observations are written output from Phase 1. Runs AFTER COMMIT so that
> extracted items can reference memory concept_ids from COMMIT for traceability.
> Delegate to save main-agent tokens.
```

Updated EXTRACT delegation prompt (adds `concept_ids` from COMMIT):
```
Task(
  subagent_type='general-purpose',
  model='haiku',
  prompt='Execute retro-cycle EXTRACT phase for {work_id}.
    REFLECT findings (summary, not full text — chunk if >2000 tokens): {reflect_findings_text}
    commit_concept_ids: {commit_concept_ids_json}
    Classify each actionable item. Output format per SKILL.md Phase 4 Classification table.
    Store each item with ingester_ingest using retro-extract:{work_id} source_path.
    Include commit_concept_ids in content for traceability.
    Return: extracted_items list in YAML format + extract_concept_ids list.'
)
```

The Phase 4 EXTRACT body retains the Classification table, Output Format, Suggested Priority, No Auto-Spawn, Proportional Scaling, and Degradation subsections from the current Phase 3 EXTRACT.

Add a "Storage" subsection to Phase 4 EXTRACT (moved from COMMIT Provenance Tags):
```markdown
### Storage

Store extracted items using `retro-extract` provenance:
```
ingester_ingest(
  content="<FULL structured output — see retro-extract detail requirements below>",
  source_path="retro-extract:{work_id}",
  content_type_hint="techne"
)
```

**retro-extract content MUST include for each item:**
- Type (bug/feature/refactor/upgrade)
- Title
- File path(s) affected
- Reproduction steps (bugs), implementation scope (features), structural target (refactors), or enhancement target (upgrades)
- Confidence level with rationale
- Severity level (bugs only)
- Source dimension (WWW/WCBB/WSY/WDN/WMI)
- Suggested priority (now/next/later) with rationale
- commit_concept_ids: list of concept IDs from COMMIT phase (for cross-reference traceability)
```

---

#### Change 6: Add context alert threshold to Phase timeout escape hatch

**Location:** Line 430, Escape Hatches table

**Current:**
```markdown
| Phase timeout | Agent context approaching limits | Complete current phase, skip remaining, COMMIT what we have |
```

**Target:**
```markdown
| Phase timeout | Context usage reaches 15% remaining (alert); 10% = close territory; 5% = emergency stop | Complete current phase, skip remaining, COMMIT what we have |
```

Also add a note in the "## Escape Hatches" section header prose (after the table):

```markdown
**Context Alert Thresholds (S439 operator directive):**
- **15% remaining:** Alert — complete current phase and trigger graceful wind-down
- **10% remaining:** Close territory — skip to COMMIT immediately if not already there
- **5% remaining:** Emergency stop — COMMIT whatever is complete, return partial results
```

---

#### Change 7: Update Composition Map table — swap Phase 3 and Phase 4

**Location:** Lines 449-456, "## Composition Map" table

**Current:**
```markdown
| Phase 3: EXTRACT | (classification from REFLECT output) | - | extracted_items list |
| Phase 4: COMMIT | ingester_ingest | 3 typed stores + closure summary | memory_concept_ids list |
```

**Target:**
```markdown
| Phase 3: COMMIT | ingester_ingest | 2 typed stores (reflect+kss) + closure summary | memory_concept_ids list (reflect+kss) |
| Phase 4: EXTRACT | ingester_ingest (retro-extract) | classification from REFLECT + concept_ids from COMMIT | extracted_items list + extract_concept_ids |
```

---

#### Change 8: Update Quick Reference table — swap Phase 3 and Phase 4 rows

**Location:** Lines 462-471, "## Quick Reference" table

**Current:**
```markdown
| Phase 3 | Are there actionable items? | Empty list (valid outcome) |
| Phase 4 | Did memory stores succeed? | Log failure, continue |
```

**Target:**
```markdown
| Phase 3 | Did memory stores succeed? | Log failure, continue |
| Phase 4 | Are there actionable items? | Empty list (valid outcome) |
```

---

#### Change 9: Update Key Design Decisions table — update 4-phase rationale row

**Location:** Lines 476-489, "## Key Design Decisions" table

**Current:**
```markdown
| 4 phases not 1 | REFLECT/DERIVE/EXTRACT/COMMIT | Observation != synthesis != classification != persistence |
```

**Target:**
```markdown
| 4 phases not 1 | REFLECT/DERIVE/COMMIT/EXTRACT | Observation != synthesis != persistence != classification. COMMIT before EXTRACT: observations and K/S/S are complete cognitive outputs — persist immediately. EXTRACT runs after with concept_ids for traceable cross-referencing. S439 operator directive. |
```

Also add a new row documenting the threshold change:
```markdown
| Context alert threshold | 15% remaining (was undocumented) | S439 operator directive: 15% alert, 10% close territory, 5% emergency stop — graduated response to context pressure |
```

---

#### Change 10: Update output_contract frontmatter — EXTRACT semantic change

**Location:** Lines 35-38, frontmatter `output_contract` section

The `extracted_items` output_contract description is already accurate ("Bug/feature/refactor/upgrade items with confidence tags and suggested priority"). However, the `memory_concept_ids` description should clarify that COMMIT concept IDs come first and EXTRACT concept IDs are separate:

**Current:**
```yaml
  - field: memory_concept_ids
    type: list
    guaranteed: on_success
    description: "Concept IDs from all COMMIT stores"
```

**Target:**
```yaml
  - field: memory_concept_ids
    type: list
    guaranteed: on_success
    description: "Concept IDs from COMMIT stores (reflect + kss + closure summary)"
  - field: extract_concept_ids
    type: list
    guaranteed: on_success
    description: "Concept IDs from EXTRACT store (retro-extract provenance)"
```

---

#### Change 11: Update Empty REFLECT escape hatch row (critique A7)

**Location:** Line 428, Escape Hatches table, "Empty REFLECT" row

**Current:**
```markdown
| Empty REFLECT | No observations surfaced | Skip DERIVE and EXTRACT, COMMIT stores empty summary |
```

**Target:**
```markdown
| Empty REFLECT | No observations surfaced | Skip DERIVE, COMMIT stores empty summary, skip EXTRACT |
```

Rationale: After reorder, COMMIT is Phase 3. When REFLECT is empty, DERIVE (Phase 2) is skipped, COMMIT (Phase 3) still stores the empty closure summary (it always runs — "never blocks closure"), and EXTRACT (Phase 4) is skipped since there are no observations to classify. The key change: COMMIT is NOT skipped — it was incorrectly listed as what runs after the skips in the old order.

---

#### Change 12: Move RetroCycleCompleted governance event to Phase 4 EXTRACT (critique A8)

**Location:** Lines 405-410, Governance Event subsection (currently in Phase 4 COMMIT, moving to Phase 4 EXTRACT)

The `RetroCycleCompleted` governance event log includes `extract_count: N`. After reorder, COMMIT (Phase 3) runs before EXTRACT (Phase 4), so `extract_count` is not available at COMMIT time.

**Resolution:** Move the `RetroCycleCompleted` event to Phase 4 EXTRACT (after extract_count is known). If EXTRACT is skipped (empty REFLECT or context exhaustion), COMMIT fires a partial event:

```
RetroCycleCommitted: {work_id}, scaling: {trivial|substantial}, reflect_count: N, kss_count: N
```

Phase 4 EXTRACT fires the full event:
```
RetroCycleCompleted: {work_id}, scaling: {trivial|substantial}, reflect_count: N, kss_count: N, extract_count: N
```

This ensures `extract_count` is always accurate when present, and governance telemetry still fires even when EXTRACT is skipped.

---

### Tests

**SKIPPED:** No Python code changes. Verification is via grep/read commands in Ground Truth layer. The existing `test_existing_skills_not_marked_stub` test in `tests/` checks for `stub: true` markers only and is not affected by prose changes to SKILL.md.

---

### Design

#### File 1 (MODIFY): `.claude/skills/retro-cycle/SKILL.md`

This is a pure prose modification — no Python, no YAML config logic, no code. The DO agent applies 10 targeted edits described in Changes 1-10 above. Each edit uses the Edit tool with the exact `old_string` from the current SKILL.md and the `new_string` target.

The complete set of changes is self-contained in one file. No imports, no module patterns to verify.

---

### Call Chain

```
/close {work_id}
  |
  +-> retro-cycle (MODIFIED)
        Phase 0: Scale Assessment (unchanged)
        Phase 1: REFLECT (unchanged — inline)
        Phase 2: DERIVE (unchanged — inline)
        Phase 3: COMMIT (was Phase 4 — now runs before EXTRACT)
        |   Returns: memory_concept_ids (reflect_ids + kss_ids + closure_id)
        |
        Phase 4: EXTRACT (was Phase 3 — now runs after COMMIT)
            Input: reflect_findings + commit_concept_ids
            Returns: extracted_items + extract_concept_ids
```

---

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| COMMIT before EXTRACT | Swap phases 3 and 4 | S439 operator directive: K/S/S are complete cognitive outputs after DERIVE — no reason to hold them in memory while EXTRACT runs. Protects against context exhaustion losing signal. |
| EXTRACT receives commit_concept_ids | Pass concept_ids in delegation prompt | Enables traceability from birth — extracted items reference the memory IDs of the observations they classify. |
| retro-extract store moves to Phase 4 | EXTRACT stores its own output | COMMIT can no longer store extracted_items (EXTRACT hasn't run). Cleaner ownership: each phase stores its own outputs. |
| Closure summary stays in COMMIT (minus Extractions count) | Remove Extractions:{count} from template | COMMIT runs before EXTRACT — extraction count unavailable. Closure summary records reflect+kss+dod counts only. |
| Context threshold in prose | Add to Escape Hatches section | WORK.md says "prose, not code" — threshold lives in SKILL.md text, not in hook files or haios.yaml. |
| output_contract split | Separate memory_concept_ids and extract_concept_ids | Callers (close-work-cycle) can now distinguish "observations persisted" (memory_concept_ids) from "extractions persisted" (extract_concept_ids) — better observable output contract. |
| close-work-cycle does NOT propagate extract_concept_ids | Intentional omission | close-work-cycle callers need success signal and dod_relevant_findings, not memory ID breakdown. extract_concept_ids is an internal retro-cycle detail, not a close-work-cycle output. (Critique A6 — deliberate, not oversight.) |
| Governance event split | RetroCycleCommitted (Phase 3) + RetroCycleCompleted (Phase 4) | extract_count must be accurate when present. COMMIT fires partial event; EXTRACT fires full event. If EXTRACT skipped, partial event still provides telemetry. |

---

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| REFLECT produces no actionable items | EXTRACT produces empty list (valid outcome) — unchanged behavior | Verified via SKILL.md Phase 4 Degradation section |
| COMMIT fails (memory store error) | Log failure, continue. EXTRACT runs but cannot populate commit_concept_ids — passes empty list | Verified via SKILL.md Phase 3 Degradation section |
| Context hits 5% during Phase 3 COMMIT | Emergency stop — return partial results with whatever concept_ids stored | Phase timeout escape hatch (updated in Change 6) |
| EXTRACT delegation receives empty commit_concept_ids | EXTRACT still stores items — commit_concept_ids field is empty list, not null | No change to existing EXTRACT output format |

---

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Callers expect old output shape (memory_concept_ids includes extract) | M | output_contract updated (Change 10). close-work-cycle reads retro output — verify it only reads `success` and `dod_relevant_findings`, not concept_ids breakdown |
| EXTRACT delegation prompt references old "Phase 3" in output format comment | L | Change 5 updates delegation prompt with new phase number |
| Existing retro observations stored under retro-extract provenance pre-reorder | L | No migration needed — historical entries are already stored, new entries will have commit_concept_ids field |

---

## Layer 2: Implementation Steps

<!-- Ordered steps. Each step is a sub-agent delegation unit. -->

### Step 1: Apply Changes 1-3 (Frontmatter + Cycle Diagram + Why 4 Phases)

- **spec_ref:** Layer 1 > Desired State > Change 1, Change 2, Change 3
- **input:** `.claude/skills/retro-cycle/SKILL.md` read (DO agent MUST read before editing)
- **action:** Edit frontmatter description, The Cycle diagram, Why 4 Phases table using Edit tool
- **output:** Description shows COMMIT->EXTRACT order; diagram shows Phase 3 COMMIT / Phase 4 EXTRACT; table rows swapped with updated rationale text
- **verify:** `grep "REFLECT->DERIVE->COMMIT->EXTRACT" .claude/skills/retro-cycle/SKILL.md` returns 1 match

### Step 2: Apply Change 4 (Phase 3 becomes COMMIT)

- **spec_ref:** Layer 1 > Desired State > Change 4
- **input:** Step 1 complete
- **action:** Replace "## Phase 3: EXTRACT" section heading, execution context box, and delegation prompt. Remove `extracted_items` from COMMIT delegation inputs. Update Provenance Tags table to remove retro-extract row. Update closure summary template: remove `Extractions: {count}` (EXTRACT has not run yet at COMMIT time).
- **output:** Phase 3 section is COMMIT with 2-store delegation prompt (reflect + kss + closure); closure summary template omits extraction count
- **verify:** `grep "## Phase 3: COMMIT" .claude/skills/retro-cycle/SKILL.md` returns 1 match; `grep "extracted_items.*json" .claude/skills/retro-cycle/SKILL.md` returns 0 matches in Phase 3 delegation block

### Step 3: Apply Change 5 (Phase 4 becomes EXTRACT)

- **spec_ref:** Layer 1 > Desired State > Change 5
- **input:** Step 2 complete
- **action:** Replace "## Phase 4: COMMIT" section heading with EXTRACT, update execution context, update delegation prompt to include commit_concept_ids, add Storage subsection with retro-extract ingester_ingest call and detail requirements.
- **output:** Phase 4 section is EXTRACT with commit_concept_ids in delegation prompt and its own storage logic
- **verify:** `grep "## Phase 4: EXTRACT" .claude/skills/retro-cycle/SKILL.md` returns 1 match; `grep "commit_concept_ids" .claude/skills/retro-cycle/SKILL.md` returns 2+ matches (delegation prompt + storage subsection)

### Step 4: Apply Change 6 (Context Alert Threshold)

- **spec_ref:** Layer 1 > Desired State > Change 6
- **input:** Step 3 complete
- **action:** Update Phase timeout row in Escape Hatches table; add Context Alert Thresholds prose block after the table
- **output:** SKILL.md contains "15% remaining" threshold text in Escape Hatches section
- **verify:** `grep "15% remaining" .claude/skills/retro-cycle/SKILL.md` returns 1+ matches

### Step 5: Apply Changes 7-9 (Composition Map + Quick Reference + Key Design Decisions)

- **spec_ref:** Layer 1 > Desired State > Changes 7, 8, 9
- **input:** Step 4 complete
- **action:** Update Composition Map table rows for Phase 3/4; update Quick Reference table Phase 3/4 rows; update Key Design Decisions "4 phases not 1" row and add threshold row
- **output:** All three tables reflect COMMIT (Phase 3) before EXTRACT (Phase 4)
- **verify:** `grep "Phase 3: COMMIT" .claude/skills/retro-cycle/SKILL.md` returns 2+ matches (diagram + composition map)

### Step 6: Apply Change 10 (output_contract frontmatter)

- **spec_ref:** Layer 1 > Desired State > Change 10
- **input:** Step 5 complete
- **action:** Edit frontmatter output_contract to split memory_concept_ids description and add extract_concept_ids field
- **output:** Frontmatter has both memory_concept_ids (reflect+kss) and extract_concept_ids fields
- **verify:** `grep "extract_concept_ids" .claude/skills/retro-cycle/SKILL.md` returns 2+ matches (frontmatter definition + Phase 4 return value)

### Step 7: Apply Change 11 (Empty REFLECT escape hatch — critique A7)

- **spec_ref:** Layer 1 > Desired State > Change 11
- **input:** Step 6 complete
- **action:** Update Empty REFLECT escape hatch row in the Escape Hatches table: "Skip DERIVE and EXTRACT, COMMIT stores empty summary" → "Skip DERIVE, COMMIT stores empty summary, skip EXTRACT"
- **output:** Escape hatch correctly reflects that COMMIT (Phase 3) runs but EXTRACT (Phase 4) is skipped
- **verify:** `grep "Skip DERIVE, COMMIT" .claude/skills/retro-cycle/SKILL.md` returns 1 match; `grep "Skip DERIVE and EXTRACT" .claude/skills/retro-cycle/SKILL.md` returns 0 matches

### Step 8: Apply Change 12 (Governance event — critique A8)

- **spec_ref:** Layer 1 > Desired State > Change 12
- **input:** Step 7 complete
- **action:** Move `RetroCycleCompleted` event from Phase 3 COMMIT to Phase 4 EXTRACT. Add `RetroCycleCommitted` partial event to Phase 3 COMMIT. Update governance event format in EXTRACT to include `extract_count`.
- **output:** COMMIT fires partial event; EXTRACT fires full event with accurate extract_count
- **verify:** `grep "RetroCycleCompleted" .claude/skills/retro-cycle/SKILL.md` appears in Phase 4 EXTRACT section (not Phase 3 COMMIT); `grep "RetroCycleCommitted" .claude/skills/retro-cycle/SKILL.md` returns 1 match in Phase 3 COMMIT section

### Step 9: Update Consumer Files (close-work-cycle + README + close.md)

- **spec_ref:** Layer 0 > Consumer Files (critique A2, A3, A5)
- **input:** Steps 1-8 complete (primary file done)
- **action:** Update `.claude/skills/close-work-cycle/SKILL.md` phase sequence strings at lines 67-68, 81, and 325 (Composition Map table): `REFLECT->DERIVE->EXTRACT->COMMIT` → `REFLECT->DERIVE->COMMIT->EXTRACT`. Update `.claude/skills/README.md` line 21: same substitution. Update `.claude/commands/close.md` at lines 77 and 298: `REFLECT -> DERIVE -> EXTRACT -> COMMIT` → `REFLECT -> DERIVE -> COMMIT -> EXTRACT`.
- **output:** All 3 consumer files reference new phase order
- **verify:** `grep "REFLECT->DERIVE->COMMIT->EXTRACT" .claude/skills/close-work-cycle/SKILL.md` returns 2+ matches; `grep "REFLECT->DERIVE->COMMIT->EXTRACT" .claude/skills/README.md` returns 1 match; `grep "REFLECT.*DERIVE.*COMMIT.*EXTRACT" .claude/commands/close.md` returns 2 matches; `grep "REFLECT->DERIVE->EXTRACT->COMMIT" .claude/skills/close-work-cycle/SKILL.md` returns 0 matches

### Step 10: Verify Full File Consistency

- **spec_ref:** Layer 0 > Primary Files + Consumer Files + Ground Truth Verification
- **input:** Steps 1-9 complete
- **action:** Read full SKILL.md, scan for any remaining references to old phase order (EXTRACT before COMMIT in Phase 3), any leftover "Phase 3: EXTRACT" headings, any "Phase 4: COMMIT" headings. Verify consumer files have no stale sequences.
- **output:** Zero inconsistencies — all phase references use new order across all 4 files
- **verify:** `grep "Phase 3: EXTRACT" .claude/skills/retro-cycle/SKILL.md` returns 0 matches; `grep "Phase 4: COMMIT" .claude/skills/retro-cycle/SKILL.md` returns 0 matches; `grep "REFLECT->DERIVE->EXTRACT->COMMIT" .claude/skills/close-work-cycle/SKILL.md .claude/skills/README.md` returns 0 matches; `grep "REFLECT.*DERIVE.*EXTRACT.*COMMIT" .claude/commands/close.md` returns 0 matches

---

## Ground Truth Verification

<!-- Computable verification protocol.
     Every line has a command and expected output.
     The CHECK agent runs these mechanically — no judgment needed. -->

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/ -v --tb=short 2>&1 \| tail -5` | 0 new failures vs pre-change baseline (skill is prose-only) |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| Phase order is REFLECT→DERIVE→COMMIT→EXTRACT | `grep "REFLECT->DERIVE->COMMIT->EXTRACT" .claude/skills/retro-cycle/SKILL.md` | 1 match |
| Phase 3 section is COMMIT | `grep "^## Phase 3: COMMIT" .claude/skills/retro-cycle/SKILL.md` | 1 match |
| Phase 4 section is EXTRACT | `grep "^## Phase 4: EXTRACT" .claude/skills/retro-cycle/SKILL.md` | 1 match |
| COMMIT stores observations + K/S/S, returns concept IDs | `grep "reflect_ids\|kss_ids\|memory_concept_ids" .claude/skills/retro-cycle/SKILL.md` | 2+ matches |
| EXTRACT stores to memory with concept IDs | `grep "commit_concept_ids" .claude/skills/retro-cycle/SKILL.md` | 2+ matches |
| EXTRACT has no auto-spawn | `grep "No Auto-Spawn" .claude/skills/retro-cycle/SKILL.md` | 1 match |
| Context alert threshold 15% in prose | `grep "15% remaining" .claude/skills/retro-cycle/SKILL.md` | 1+ matches |
| output_contract has extract_concept_ids | `grep "extract_concept_ids" .claude/skills/retro-cycle/SKILL.md` | 2+ matches |
| No old Phase 3 EXTRACT heading remains | `grep "^## Phase 3: EXTRACT" .claude/skills/retro-cycle/SKILL.md` | 0 matches |
| No old Phase 4 COMMIT heading remains | `grep "^## Phase 4: COMMIT" .claude/skills/retro-cycle/SKILL.md` | 0 matches |
| Empty REFLECT escape hatch updated | `grep "Skip DERIVE, COMMIT" .claude/skills/retro-cycle/SKILL.md` | 1 match |
| Old escape hatch text gone | `grep "Skip DERIVE and EXTRACT" .claude/skills/retro-cycle/SKILL.md` | 0 matches |
| Governance event split (COMMIT partial) | `grep "RetroCycleCommitted" .claude/skills/retro-cycle/SKILL.md` | 1 match |
| Governance event full in EXTRACT | `grep "RetroCycleCompleted" .claude/skills/retro-cycle/SKILL.md` | 1+ matches |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| close-work-cycle still references retro-cycle correctly | `grep -c "retro-cycle" .claude/skills/close-work-cycle/SKILL.md` | 1+ matches |
| close-work-cycle phase sequence updated | `grep "REFLECT->DERIVE->COMMIT->EXTRACT" .claude/skills/close-work-cycle/SKILL.md` | 2+ matches |
| close-work-cycle no stale phase sequence | `grep "REFLECT->DERIVE->EXTRACT->COMMIT" .claude/skills/close-work-cycle/SKILL.md` | 0 matches |
| No broken phase references in close-work-cycle | `grep "Phase 3.*EXTRACT\|Phase 4.*COMMIT" .claude/skills/close-work-cycle/SKILL.md` | 0 matches |
| README.md phase sequence updated | `grep "REFLECT->DERIVE->COMMIT->EXTRACT" .claude/skills/README.md` | 1 match |
| README.md no stale phase sequence | `grep "REFLECT->DERIVE->EXTRACT->COMMIT" .claude/skills/README.md` | 0 matches |
| SKILL.md frontmatter description updated | `grep "REFLECT->DERIVE->COMMIT->EXTRACT" .claude/skills/retro-cycle/SKILL.md` | 1 match |
| Closure summary no Extractions count | `grep "Extractions:" .claude/skills/retro-cycle/SKILL.md` | 0 matches |
| close.md phase sequence updated | `grep "REFLECT.*DERIVE.*COMMIT.*EXTRACT" .claude/commands/close.md` | 2 matches |
| close.md no stale phase sequence | `grep "REFLECT.*DERIVE.*EXTRACT.*COMMIT" .claude/commands/close.md` | 0 matches |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 10 verify — 0 new pytest failures)
- [ ] All WORK.md deliverables verified (table above — all grep commands return expected counts)
- [ ] Runtime consumer exists: close-work-cycle invokes retro-cycle (unchanged invocation)
- [ ] No stale references: no "Phase 3: EXTRACT" or "Phase 4: COMMIT" headings remain
- [ ] Consumer files updated: close-work-cycle, README.md, and close.md have new phase sequence
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `.claude/skills/retro-cycle/SKILL.md` — primary source file (read in full during plan authoring)
- Memory refs 88137-88143 — S439 operator directive on phase reordering
- REQ-LIFECYCLE-004 — chaining is caller choice (no auto-spawn, preserved by this change)
- REQ-CEREMONY-002 — ceremony contract requirement (traced in WORK.md)
- S399 operator directive — retro-cycle COMMIT phase MUST store full detail (preserved by this change)
- S436 operator directive — REFLECT/DERIVE inline, EXTRACT/COMMIT delegated to haiku (delegation model preserved, phase order changes)
- Memory 87398 — implementation-cycle SKILL.md fractured successfully (retro-cycle is monolithic, no fracturing in scope)

---
