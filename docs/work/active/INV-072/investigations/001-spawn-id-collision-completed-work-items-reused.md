---
template: investigation
status: active
date: 2026-01-26
backlog_id: INV-072
title: Spawn ID Collision - Completed Work Items Reused
author: Hephaestus
session: 246
lifecycle_phase: conclude
spawned_by: null
related: []
memory_refs:
- 82467
- 82468
- 82469
version: '2.0'
generated: 2025-12-22
last_updated: '2026-01-26T21:41:02'
---
# Investigation: Spawn ID Collision - Completed Work Items Reused

@docs/README.md
@docs/epistemic_state.md

<!-- FILE REFERENCE REQUIREMENTS (MUST - Session 171 Learning)

     1. MUST use full @ paths for prior work:
        CORRECT: @docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md
        WRONG:   INV-052, "See INV-052"

     2. MUST read ALL @ referenced files BEFORE starting EXPLORE phase:
        - Read each @path listed at document top
        - For directory references (@docs/work/active/INV-052/), MUST Glob to find all files
        - Document key findings in Prior Work Query section
        - Do NOT proceed to EXPLORE until references are read

     3. MUST Glob referenced directories:
        @docs/work/active/INV-052/ → Glob("docs/work/active/INV-052/**/*.md")
        Then read key files (SECTION-*.md, WORK.md, investigations/*.md)

     Rationale: Session 171 wasted ~15% context searching for INV-052 in wrong
     location because agent ignored @ references and guessed file locations.
-->

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

## Discovery Protocol (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Query memory first | SHOULD | Search for prior investigations on topic before starting |
| Document hypotheses | SHOULD | State what you expect to find before exploring |
| Use investigation-agent | MUST | Delegate EXPLORE phase to subagent for structured evidence |
| Capture findings | MUST | Fill Findings section with evidence, not assumptions |

---

## Context

<!-- HYPOTHESIZE PHASE: Describe background before exploring -->

**Trigger:** During Session 246 survey-cycle, E2-294 was selected from queue. PLAN.md content did not match WORK.md deliverables.

**Problem Statement:** Work item E2-294 was COMPLETED in Session 196, but reused for different work in Session 245 without clearing prior artifacts, causing PLAN.md/WORK.md mismatch.

**Prior Observations:**
- Git history shows E2-294 was `current_node: complete` with title "Wire implementation-cycle and investigation-cycle with set-cycle" in commit 921c8c3
- Git history shows E2-294 was overwritten with new title "Wire Session Event Logging into Lifecycle" in commit fe17c99
- PLAN.md still contains Session 196 content (set-cycle wiring), not Session 245 content (session logging)
- Memory concepts 77290, 79940 document prior ID collision incidents

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "work item ID collision spawn duplicate reuse completed"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 77290 | ID collision where two files can have same backlog_id (INV-011 Session 101) | Same class of bug |
| 79940 | Old INV-042 investigation file collision in docs/investigations/ | Same class of bug |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] Found: Memory shows prior incidents but no formal investigation

---

## Objective

<!-- One clear question this investigation will answer -->

**Why did the spawn logic reuse a completed work item ID, and how can we prevent this?**

---

## Scope

### In Scope
- ID allocation algorithm in work_engine.py or scaffold modules
- The specific spawn that created E2-294 in Session 245
- Count of other completed work items that were reused
- Fix proposal

### Out of Scope
- Fixing all historical collisions (that's spawned work)
- Changing ID naming scheme (separate concern)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | ~5 | work_engine.py, scaffold, justfile, cli.py |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | 2 | Codebase + Git history |
| Estimated complexity | Low | ID allocation is centralized |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | Agent manually edited WORK.md without using spawn command | High | Check git diff for fe17c99 - was it `just spawn` or raw Edit? | 1st |
| **H2** | `just work` command doesn't check for existing completed items | Med | Read work_engine.py or scaffold module, check for status validation | 2nd |
| **H3** | ID allocation scans active/ but completed items stay in active/ | Med | Check if completed items should be moved to archive/ | 3rd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [x] Read git diff for commit fe17c99 to see exact changes
2. [x] Read work_engine.py for ID allocation logic
3. [x] Read scaffold module for work item creation

### Phase 2: Hypothesis Testing
4. [x] Test H1: Check if agent used Edit tool or `just work` command
5. [x] Test H2: Check if work command validates existing IDs
6. [x] Test H3: Check ADR-041 for completed item location policy

### Phase 3: Synthesis
7. [x] Compile evidence table
8. [x] Determine verdict for each hypothesis
9. [x] Identify spawned work items (E2-304, E2-305 created)

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| E2-XXX IDs are agent-specified, not auto-generated | `.claude/lib/scaffold.py:153-174` | H1 | `get_next_work_id()` only handles WORK-XXX |
| No status check in `_work_file_exists()` | `.claude/lib/scaffold.py:117-139` | H2 | Returns True if file exists regardless of status |
| `create_work()` uses `exist_ok=True` | `.claude/haios/modules/work_engine.py:189-245` | H2 | Silently succeeds if directory exists |
| Status over location policy | `docs/ADR/ADR-041-svelte-governance-criteria.md:104` | H3 | Completed items stay in active/ |
| `close()` doesn't move files | `.claude/haios/modules/work_engine.py:440-465` | H3 | Sets status=complete but no directory change |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 77290 | ID collision where two files can have same backlog_id (INV-011 Session 101) | All | Prior incident, same class of bug |
| 79940 | Old INV-042 investigation file collision | All | Prior incident, same class of bug |

### External Evidence (if applicable)

**SKIPPED:** Investigation is codebase-only, no external sources needed.

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **Partially Confirmed** | Agent used proper command but picked existing ID. E2-XXX IDs are agent-specified, not auto-generated (scaffold.py:153-174) | High |
| H2 | **Confirmed** | `scaffold_template()` has no validation for existing completed items. `_work_file_exists()` only gates plans/investigations. | High |
| H3 | **Confirmed** | ADR-041 "status over location" keeps completed items in active/. Correct policy but creates precondition for collision when combined with lack of validation. | High |

### Detailed Findings

#### Finding 1: E2-XXX IDs Are Agent-Specified, Not Auto-Generated

**Evidence:**
```python
# .claude/lib/scaffold.py:153-174
def get_next_work_id() -> str:
    """Generate next sequential WORK-XXX ID.
    Ignores legacy E2-XXX and INV-XXX directories.
    """
```

**Analysis:** `get_next_work_id()` only handles WORK-XXX format. For E2-XXX and INV-XXX, agent must manually specify the ID without tooling support for uniqueness.

**Implication:** Either extend auto-generation to all ID formats or add validation to reject completed IDs.

#### Finding 2: No Status-Aware Validation in Work Creation

**Evidence:**
```python
# .claude/haios/modules/work_engine.py:189-245
def create_work(self, id: str, title: str, ...):
    work_dir = self.active_dir / id
    work_dir.mkdir(parents=True, exist_ok=True)  # Silently succeeds if exists
    work_path.write_text(content, ...)  # Overwrites existing WORK.md
```

**Analysis:** Creation path has no guard against overwriting completed items. `exist_ok=True` doesn't error when directory exists.

**Implication:** Add validation: "Does ID exist AND status is terminal (complete/archived)?" If yes, reject.

#### Finding 3: Root Cause Is Triple Combination

**Evidence:** Session 245 agent spawned E2-294 from E2-236. Agent chose ID E2-294 (likely incrementing from recent work) without checking if it existed with status=complete from Session 196.

**Analysis:** Three factors combined: (1) agent specifies ID, (2) no status validation in creation, (3) completed items stay in active/ per ADR-041.

**Implication:** Fix is validation, not location change. ADR-041 is correct.

---

## Design Outputs

### Mechanism Design: Status-Aware ID Validation

```
TRIGGER: Agent calls `just work <id> "<title>"` or `create_work(id, title, ...)`

ACTION:
    1. Check if docs/work/active/{id}/WORK.md exists
    2. If exists, read frontmatter and check status field
    3. If status in ['complete', 'archived']:
       - REJECT: "Error: ID {id} already exists with status '{status}'. Use a new ID."
    4. If status in ['active', 'draft', 'backlog']:
       - WARN: "Warning: ID {id} already exists in status '{status}'. Continuing will overwrite."
       - Require --force flag to proceed

OUTCOME: Prevents accidental overwrite of completed work items
```

### Implementation Location

| File | Change | Notes |
|------|--------|-------|
| `.claude/haios/modules/work_engine.py` | Add `_validate_id_available()` before `create_work()` | Primary gate |
| `.claude/lib/scaffold.py` | Add same check in `scaffold_template()` for work_item | Backup gate |

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Validation, not location change | Add status check, keep ADR-041 | Moving files breaks references; validation is non-breaking |
| Error for complete/archived, warn for active | Different severity levels | Complete items should never be overwritten; active items might be intentional edits |
| Check in both work_engine and scaffold | Defense in depth | Multiple entry points to work creation |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

- [x] **E2-304: Add Status-Aware ID Validation to Work Creation**
  - Description: Add `_validate_id_available()` to work_engine.py that rejects IDs with status complete/archived
  - Fixes: Root cause - no validation prevents reusing completed IDs
  - Created: `docs/work/active/E2-304/WORK.md`

- [x] **E2-305: Mitigate E2-294 Collision - Restore or Rename**
  - Description: Decide whether to restore original E2-294 from git and create new ID for session logging, or keep current E2-294 with fresh plan
  - Fixes: Immediate symptom - E2-294 has mismatched PLAN.md
  - Created: `docs/work/active/E2-305/WORK.md`

### Future (Requires more work first)

- [ ] **INV-XXX: Audit for Other ID Collisions**
  - Description: Scan git history for other completed items that were overwritten
  - Blocked by: E2-304 (need validation in place first to prevent new collisions while scanning)

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 246 | 2026-01-26 | HYPOTHESIZE | Started | Initial context and hypotheses |
| - | - | - | - | No additional sessions yet |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-H3 have verdict | [x] | H1: Partially Confirmed, H2: Confirmed, H3: Confirmed |
| Evidence has sources | All findings have file:line or concept ID | [x] | scaffold.py:117-139, work_engine.py:189-245, etc. |
| Spawned items created | Items exist in backlog or via /new-* | [x] | E2-304, E2-305 created via `just work` |
| Memory stored | ingester_ingest called, memory_refs populated | [x] | Concepts 82467-82469 created |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | Yes | Task with subagent_type=investigation-agent |
| Are all evidence sources cited with file:line or concept ID? | Yes | scaffold.py:117-139, work_engine.py:189-245, ADR-041:104 |
| Were all hypotheses tested with documented verdicts? | Yes | H1-H3 all have verdicts in Findings section |
| Are spawned items created (not just listed)? | Yes | E2-304, E2-305 created via `just work` |
| Is memory_refs populated in frontmatter? | Yes | [82467, 82468, 82469] |

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete ALL items before /close -->

### Required (MUST complete)
- [x] **Findings synthesized** - Root cause is triple combination documented in Findings
- [x] **Evidence sourced** - All findings have file:line citations
- [x] **Hypotheses resolved** - H1-H3 all have verdicts
- [x] **Spawned items created** - E2-304, E2-305 with spawned_by: INV-072
- [x] **Memory stored** - ingester_ingest called, concepts 82467-82469
- [x] **memory_refs populated** - Frontmatter has [82467, 82468, 82469]
- [x] **lifecycle_phase updated** - Set to conclude
- [x] **Ground Truth Verification complete** - All items checked above

### Optional
- [x] Design outputs documented - Mechanism Design section populated
- [x] Session progress updated - Single session investigation

---

## References

- Spawned by: Session 246 survey-cycle (discovered when E2-294 PLAN/WORK mismatch detected)
- @docs/work/active/E2-294/WORK.md (collision victim)
- @docs/ADR/ADR-041-svelte-governance-criteria.md (status over location policy)
- @.claude/haios/modules/work_engine.py (implementation target)
- @.claude/lib/scaffold.py (implementation target)

---
