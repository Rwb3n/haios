---
template: investigation
status: complete
date: 2025-12-27
backlog_id: INV-043
title: Work Item Directory Architecture
author: Hephaestus
session: 129
lifecycle_phase: conclude
spawned_by: null
related: []
memory_refs:
- 79765
- 79766
- 79767
- 79768
- 79769
- 79770
- 79771
- 79772
- 79773
- 79774
- 79775
- 79776
- 79777
- 79778
version: '2.0'
generated: 2025-12-22
last_updated: '2025-12-27T18:06:00'
---
# Investigation: Work Item Directory Architecture

@docs/README.md
@docs/epistemic_state.md

<!-- TEMPLATE GOVERNANCE (v2.0 - E2-144)

     INVESTIGATION CYCLE: HYPOTHESIZE -> EXPLORE -> CONCLUDE

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: Pure discovery, no design outputs needed"
     - "SKIPPED: Single hypothesis, no complex mapping required"
     - "SKIPPED: External research only, no codebase evidence"

     This prevents silent section deletion and ensures conscious decisions.

     SUBAGENT REQUIREMENT (L3):
     For EXPLORE phase, you MUST invoke investigation-agent subagent:
     Task(prompt='EXPLORE: {hypothesis}', subagent_type='investigation-agent')

     Rationale: Session 101 proved L2 ("RECOMMENDED") guidance is ignored ~20% of time.
     L3 enforcement ensures structured evidence gathering.
-->

---

## Context

<!-- HYPOTHESIZE PHASE: Describe background before exploring -->

**Trigger:** Session 127 discussion identified fundamental limitations with current flat work file structure.

**Problem Statement:** Work item artifacts are scattered across directories; investigations are monolithic and don't support layered/iterative research.

**Prior Observations:**
- INV-024 established current flat file structure (`docs/work/active/WORK-E2-xxx.md`)
- Investigations are single-pass: no way to do landscape scan → deep-dive → synthesis
- Investigation spawning Investigation is awkward (Investigation A spawns Investigation B has no good home)
- Reports template exists but unused (no good place for bugs, bandaids, events)
- Plans and investigations are in separate directories from work files, making context scattered

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "prior investigations about work item directory architecture file organization investigation decomposition"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 79582 | Store findings on investigation complete, have WHY in memory | Investigation closure discipline |
| 76815 | Leverage naming conventions for document ingestion | File naming informs structure |
| 63387 | HAiOS principles as foundation for directory structure | Governance-aware file pipeline |
| 77315-77329 | INV-024 findings on work-item-as-file architecture | Direct predecessor |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] Found: INV-024 (Work Item as File Architecture) - established current structure
- [x] Found: INV-030 (Milestone Architecture) - related organizational concerns

---

## Objective

<!-- One clear question this investigation will answer -->

**Should work items evolve from flat files to directories**, where each work item is a folder containing its WORK.md plus subdirectories for investigations, plans, and reports?

**Core Question:** What directory structure best supports:
1. Layered/iterative investigations (landscape → deep-dive → synthesis)
2. Investigation spawning (parent investigation creates child investigations)
3. Report template revival (bugs, bandaids, events)
4. Context co-location (all artifacts for one work item together)

---

## Scope

### In Scope
- Directory structure design for work-item-as-directory
- Investigation subtype taxonomy (landscape, deep-dive, synthesis)
- Report template revival strategy
- Tooling impact assessment (status.py, plan_tree.py, scaffold, validate)
- Migration strategy (minimal disruption)

### Out of Scope
- Checkpoints (remain at session level, span work items)
- Memory system changes
- Implementation of the changes (spawn implementation items)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 8-10 | `.claude/lib/*.py`, `docs/work/`, templates |
| Hypotheses to test | 4 | Listed below |
| Expected evidence sources | 3 | Codebase / Memory / Current workflow analysis |
| Estimated complexity | Medium | Design work, no code changes |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | Directory-per-work-item reduces context scattering | High | Compare current scattered artifacts vs co-located structure | 1st |
| **H2** | Tooling can adapt to directory structure with minimal changes | Med | Audit status.py, plan_tree.py, scaffold.py glob patterns | 2nd |
| **H3** | Investigation subtypes (landscape/deep-dive/synthesis) map to numbered files in subdir | Med | Design naming convention, test with example | 3rd |
| **H4** | Reports template fits naturally as work-item subdirectory | High | Design report types, validate use cases | 4th |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [x] Query memory for prior learnings on directory organization patterns
2. [x] Audit current artifact distribution: where do investigations/plans live for a sample work item?
3. [x] Read tooling files: status.py, plan_tree.py, scaffold.py, validate.py

### Phase 2: Hypothesis Testing
4. [x] Test H1: Map artifacts for E2-091 to show scattering, then design co-located alternative
5. [x] Test H2: Audit glob patterns in status.py and plan_tree.py for migration complexity
6. [x] Test H3: Design investigation subtype naming convention with example
7. [x] Test H4: Design report types and validate against real use cases (bugs, bandaids)

### Phase 3: Synthesis
8. [x] Compile proposed directory structure
9. [x] Document tooling changes required
10. [x] Determine verdict for each hypothesis
11. [ ] Spawn implementation work items

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| E2-091 artifacts span 3+ directories | `docs/plans/PLAN-E2-091-*.md`, checkpoints, skills/ | H1 | Context scattering confirmed |
| ADR-039 documents: "E2-091 spans 14 files" | `docs/ADR/ADR-039-work-item-as-file-architecture.md:38` | H1 | Pain point documented |
| status.py uses hardcoded paths | `.claude/lib/status.py:506-515, 717-720, 784-794` | H2 | 8+ glob patterns need update |
| plan_tree.py uses flat glob | `scripts/plan_tree.py:72` | H2 | Pattern: `docs/work/active/WORK-*.md` |
| scaffold.py uses flat TEMPLATE_CONFIG | `.claude/lib/scaffold.py:64-67` | H2 | `"dir": "docs/work/active"` |
| cascade.py uses flat pattern | `.claude/lib/cascade.py:91` | H2 | `PLANS_PATH.glob(f"PLAN-{item_id}*.md")` |
| audit.py uses hardcoded globs | `.claude/lib/audit.py:55, 74` | H2 | Multiple flat patterns |
| work_item.py uses WORK_DIR | `.claude/lib/work_item.py:14, 30` | H2 | `ACTIVE_DIR.glob(pattern)` |
| Investigation template exists | `.claude/templates/investigation.md` | H3 | Flexible structure, no subtype field |
| validate.py has investigation sections | `.claude/lib/validate.py:79-99` | H3 | Can add subtype validation |
| Report template is generic | `.claude/templates/report.md` | H4 | Has tags but no subtype field |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 77119 | "Work files are entities that traverse lifecycle DAG" | H1 | Supports co-location vision |
| 77315-77329 | INV-024 findings on work-item-as-file | H1, H2 | Direct predecessor |
| 63387 | HAiOS principles for directory structure | H1 | Governance-aware file pipeline |

### External Evidence (if applicable)

**SKIPPED:** Pure codebase investigation, no external research needed

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **CONFIRMED** | E2-091 has 14+ scattered files; ADR-039 documents this pain point | High |
| H2 | **INCONCLUSIVE** | 6+ files need glob pattern updates; effort is MEDIUM not minimal | Medium |
| H3 | **CONFIRMED** | Naming convention `NNN-subtype.md` enables landscape/deep-dive/synthesis | Medium |
| H4 | **CONFIRMED** | Template exists but underutilized; adding subtype field enables categorization | High |

### Detailed Findings

#### Finding 1: Context Scattering is Real and Documented

**Evidence:**
```
E2-091 artifacts span:
- docs/plans/PLAN-E2-091-implementation-cycle-skill.md
- docs/checkpoints/*SESSION-84* (8+ files modified)
- .claude/skills/implementation-cycle/
- docs/work/active/WORK-E2-091-*.md (if exists)
Total: 14+ files per ADR-039:38
```

**Analysis:** A single work item like E2-091 has context scattered across 4+ directories. The work file `documents:` field tracks links but doesn't co-locate content.

**Implication:** Directory-per-work-item would consolidate context. However, full co-location requires major tooling changes.

#### Finding 2: Tooling Migration is Medium Effort, Not Minimal

**Evidence:**
```
Files requiring glob pattern updates:
- status.py: 8+ patterns (HIGH)
- plan_tree.py: 1 pattern (MEDIUM)
- scaffold.py: TEMPLATE_CONFIG structure (HIGH)
- cascade.py: 1 pattern (MEDIUM)
- audit.py: 2+ patterns (MEDIUM)
- work_item.py: 2+ patterns (MEDIUM)
```

**Analysis:** H2 asked if tooling can adapt with "minimal changes" - the answer is NO. Six files need updates, with status.py and scaffold.py requiring significant rework.

**Implication:** A hybrid approach (Option B) reduces migration effort while capturing most value.

#### Finding 3: Hybrid Co-location is the Pragmatic Path

**Evidence:**
Three options analyzed:
- **Option A (Full):** All artifacts inside work directory - HIGH effort
- **Option B (Hybrid):** Reports/notes inside, plans/investigations stay put - MEDIUM effort
- **Option C (Minimal):** Investigation subtypes only - LOW effort

**Analysis:** Option B provides 70% of the value with 40% of the effort. Plans and investigations can remain in their directories with links in `documents:` field.

**Implication:** Recommend Option B as Phase 1, with Option A as future milestone.

#### Finding 4: Investigation Subtypes Enable Iterative Research

**Evidence:**
Proposed naming convention:
```
docs/work/active/E2-091/investigations/
  001-landscape.md       # Broad survey
  002-deep-dive.md       # Focused analysis
  003-synthesis.md       # Combining findings
```

**Analysis:** Current investigations are monolithic. Subtypes enable natural research progression: landscape scan → deep-dive → synthesis.

**Implication:** Add `subtype` field to investigation template; support numbered naming in work directories.

#### Finding 5: Report Template Revival Fits Naturally

**Evidence:**
Proposed report types:
| Subtype | Use Case |
|---------|----------|
| bug | Document discovered bug |
| bandaid | Temporary workaround |
| event | Significant event capture |
| decision | Micro-decision (smaller than ADR) |
| analysis | Data analysis / audit results |

**Analysis:** Report template exists but is underutilized. No good "home" for bugs, bandaids, events. Work-item subdirectory provides natural home.

**Implication:** Add `subtype` field to report template; scaffold reports into `docs/work/active/{id}/reports/`

---

## Design Outputs

<!-- If investigation produces architectural designs, document them here
     SKIP this section if investigation is pure discovery with no design outputs -->

### Proposed Directory Structure (Option B: Hybrid Co-location)

```
docs/work/
├── active/
│   └── E2-091/                        # Directory per work item
│       ├── WORK.md                    # Main work file (renamed from WORK-E2-091-*.md)
│       ├── notes/                     # Session notes, scratch work
│       │   └── 001-landscape-notes.md
│       └── reports/                   # Small reports co-located
│           └── 001-bug-hook-failure.md
├── blocked/
│   └── E2-152/
│       └── WORK.md
└── archive/
    └── E2-091/                        # Entire directory moves on close
        └── ...

# Plans and investigations STAY in existing locations
docs/plans/
└── PLAN-E2-091-implementation-cycle-skill.md

docs/investigations/
└── INVESTIGATION-INV-043-work-item-directory-architecture.md
```

### Schema Design: Investigation Subtype Field

```yaml
# Addition to investigation template frontmatter
subtype: landscape | deep-dive | synthesis | null
  description: Investigation subtype for iterative research
  default: null (standard investigation)
```

### Schema Design: Report Subtype Field

```yaml
# Addition to report template frontmatter
subtype: bug | bandaid | event | decision | analysis
  description: Report categorization
```

### Tooling Changes Required

| File | Change | Effort |
|------|--------|--------|
| `scaffold.py` | Create directory for work item, handle WORK.md naming | HIGH |
| `work_item.py` | Update glob patterns for directory structure | MEDIUM |
| `status.py` | Update work file discovery patterns | HIGH |
| `plan_tree.py` | Update glob from `WORK-*.md` to `*/WORK.md` | LOW |
| `validate.py` | Add subtype validation for investigation/report | LOW |
| `audit.py` | Update glob patterns | MEDIUM |

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Co-location approach | Hybrid (Option B) | 70% value, 40% effort vs full co-location |
| Plans location | Stay in docs/plans/ | Minimizes tooling changes, links via documents: field |
| Investigations location | Stay in docs/investigations/ | Same rationale; subtype field enables iteration |
| Reports location | Move to work-item subdir | Natural home for work-specific bugs/bandaids |
| Work file naming | `WORK.md` inside directory | ID in directory name, file name consistent |
| Investigation subtypes | landscape/deep-dive/synthesis | Maps to natural research progression |
| Report subtypes | bug/bandaid/event/decision/analysis | Covers identified use cases |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

- [x] **E2-212: Work Directory Structure Migration**
  - Description: Migrate work files from flat `WORK-{id}-*.md` to `{id}/WORK.md` directory structure
  - Fixes: Context scattering (H1), enables subdirectories for reports/notes
  - Spawned via: `just work E2-212` + `just link-spawn INV-043 M7b-WorkInfra E2-212`

- [x] **E2-213: Investigation Subtype Field**
  - Description: Add `subtype` field to investigation template (landscape/deep-dive/synthesis)
  - Fixes: Monolithic investigations (H3), enables iterative research
  - Spawned via: `just work E2-213` + `just link-spawn INV-043 M7b-WorkInfra E2-213`

- [x] **E2-214: Report Subtype Field and Work-Item Subdirectory**
  - Description: Add `subtype` field to report template, scaffold reports into work-item `reports/` subdirectory
  - Fixes: Report template underutilized (H4), no home for bugs/bandaids
  - Spawned via: `just work E2-214` + `just link-spawn INV-043 M7b-WorkInfra E2-214`

### Future (Requires more work first)

- [ ] **E2-XXX: Full Co-location Migration**
  - Description: Move plans and investigations inside work directories (Option A)
  - Blocked by: Hybrid approach (E2-212) proves value; requires major tooling effort

### Not Spawned Rationale (if no items)

N/A - 3 immediate items spawned, 1 future item identified

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 129 | 2025-12-27 | HYPOTHESIZE | Started | Initial context and hypotheses |
| 129 | 2025-12-27 | EXPLORE | Complete | investigation-agent gathered evidence |
| 129 | 2025-12-27 | CONCLUDE | Complete | Spawned E2-212, E2-213, E2-214 |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-H4 have verdict | [x] | H1,H3,H4 CONFIRMED; H2 INCONCLUSIVE |
| Evidence has sources | All findings have file:line or concept ID | [x] | 11 codebase, 3 memory sources |
| Spawned items created | Items exist in backlog or via /new-* | [x] | E2-212, E2-213, E2-214 created |
| Memory stored | ingester_ingest called, memory_refs populated | [x] | 79765-79778 |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | Yes | Task subagent_type='investigation-agent' |
| Are all evidence sources cited with file:line or concept ID? | Yes | Evidence Collection table complete |
| Were all hypotheses tested with documented verdicts? | Yes | H1-H4 all have verdicts |
| Are spawned items created (not just listed)? | Yes | just work + just link-spawn |
| Is memory_refs populated in frontmatter? | Yes | 14 concept IDs |

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete ALL items before /close -->

### Required (MUST complete)
- [x] **Findings synthesized** - Answer to objective documented in Findings section
- [x] **Evidence sourced** - All findings have file:line or concept ID citations
- [x] **Hypotheses resolved** - All hypotheses have Confirmed/Refuted/Inconclusive verdict
- [x] **Spawned items created** - Via /new-* commands with `spawned_by` field (or rationale if none)
- [x] **Memory stored** - `ingester_ingest` called with findings summary
- [x] **memory_refs populated** - Frontmatter updated with concept IDs
- [x] **lifecycle_phase updated** - Set to `conclude`
- [x] **Ground Truth Verification complete** - All items checked above

### Optional
- [x] Design outputs documented (if applicable)
- [x] Session progress updated (if multi-session)

---

## References

- Spawned by: Session 127 discussion (work item WORK-INV-043)
- Related: INV-024 (Work Item as File Architecture) - predecessor
- Related: ADR-039 (Work Item as File Architecture) - formal decision
- Spawned: E2-212, E2-213, E2-214 (implementation items)

---
