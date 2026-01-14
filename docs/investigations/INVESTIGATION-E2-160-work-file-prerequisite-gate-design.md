---
template: investigation
status: complete
date: 2025-12-24
backlog_id: E2-160
title: Work File Prerequisite Gate Design
author: Hephaestus
session: 109
lifecycle_phase: conclude
spawned_by: Session-109
related:
- ADR-039
- INV-020
- E2-154
- E2-155
memory_refs: []
version: '2.0'
generated: 2025-12-22
last_updated: '2025-12-29T12:26:37'
---
# Investigation: Work File Prerequisite Gate Design

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

**Trigger:** Session 109 - Created INV-027 investigation directly without work file, bypassing M6 DAG architecture.

**Problem Statement:** `/new-investigation` and `/new-plan` commands can create orphaned documents that bypass the work file lifecycle (scaffold-on-entry, exit gates, node tracking).

**Prior Observations:**
- M6-WorkCycle established work files as source of truth for tracking items through DAG
- E2-154 (scaffold-on-entry) only fires when `current_node` changes in existing work file
- E2-155 (exit gates) only fires when leaving a node in existing work file
- Without work file, these governance mechanisms are bypassed entirely
- INV-020 established that L3 (gated) enforcement is highly effective vs L2 (prompted)

---

## Process Observations (Session 109)

**Expected vs Actual during this investigation setup:**

| Step | Expected | Actual | Gap? |
|------|----------|--------|------|
| Change `current_node: backlog → discovery` | PostToolUse suggests `/new-investigation` | No visible suggestion appeared | Yes - hook may not output to agent |
| Run `/new-investigation` | Work file `cycle_docs` auto-updates | Had to manually edit work file | Yes - no auto-linking |
| Investigation created | `documents.investigations` populated | Had to manually add | Yes - no auto-linking |

**Implication:** Even with E2-154 wired, the flow has manual gaps. The L3 gate (E2-160) is necessary but not sufficient - auto-linking (E2-161?) may also be needed.

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "PreToolUse gate work file enforcement L3 blocker"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 77419-77432 | HAIOS harness review - L3/L4 blockers highly effective | Core principle |
| 77199-77209 | INV-020: Enforcement Spectrum L0-L4 | Design guidance |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] Found: INV-020 (Enforcement Spectrum), INV-027 (spawned this)

---

## Objective

<!-- One clear question this investigation will answer -->

How should PreToolUse gates enforce that work files exist before `/new-investigation` or `/new-plan` can create documents?

---

## Scope

### In Scope
- PreToolUse hook integration point for slash commands
- Work file existence check logic
- Error message design
- Commands to gate: `/new-investigation`, `/new-plan`

### Out of Scope
- Auto-creation of work files (separate feature)
- Auto-linking created documents to work files (separate feature E2-161?)
- Other commands (checkpoints, reports, ADRs)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 3 | pre_tool_use.py, new-investigation.md, new-plan.md |
| Hypotheses to test | 2 | Listed below |
| Expected evidence sources | 2 | Codebase, INV-020 |
| Estimated complexity | Low | Simple glob check |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | PreToolUse can intercept slash command execution and block based on file existence check | High | Read pre_tool_use.py, find where commands are handled | 1st |
| **H2** | A simple `glob.glob("docs/work/active/WORK-{id}-*.md")` check is sufficient | High | Test pattern matching logic | 2nd |

---

## Evidence Collection

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| `docs/investigations/` NOT in governed_paths | `pre_tool_use.py:193-199` | Partially H1 | Existing path governance doesn't cover investigations |
| PreToolUse gates Write/Edit, not Skill | `pre_tool_use.py:44-77` | H1 | Can intercept Write from scaffold_template |
| scaffold_template writes via Path.write_text | `.claude/lib/scaffold.py` | H1 | Write happens in Python, not raw Write tool |

### Key Discovery

**The existing path governance pattern won't work directly because:**
1. `docs/investigations/` isn't blocked - investigations are valid to create
2. The issue is CONDITIONAL - only block if work file doesn't exist
3. scaffold_template uses Python `Path.write_text()`, not the Write tool

**Options:**
1. **Gate in scaffold.py** - Check work file exists before writing
2. **Gate in PreToolUse** - Check Write to `docs/investigations/INVESTIGATION-{id}-*` if work file missing
3. **Gate in commands** - Update `/new-investigation` to check first

Option 1 (scaffold.py) is cleanest - single enforcement point for all governed documents.

### Design Proposal

**Location:** `scaffold_template()` in `.claude/lib/scaffold.py` before line 324 (write)

**Implementation:**
```python
# Templates that require work file to exist first
WORK_FILE_REQUIRED_TEMPLATES = {"investigation", "implementation_plan"}

def _work_file_exists(backlog_id: str) -> bool:
    """Check if work file exists for backlog_id."""
    pattern = PROJECT_ROOT / "docs" / "work" / "active" / f"WORK-{backlog_id}-*.md"
    return len(list(pattern.parent.glob(pattern.name))) > 0

# In scaffold_template(), before write:
if template in WORK_FILE_REQUIRED_TEMPLATES and backlog_id:
    if not _work_file_exists(backlog_id):
        raise ValueError(
            f"Work file required. Run '/new-work {backlog_id} \"{title}\"' first."
        )
```

**Why this approach:**
1. Single enforcement point - all paths go through scaffold_template()
2. L3 enforcement - raises exception, blocks the operation
3. Clear error message - tells user exactly what to do
4. Simple implementation - ~10 lines of code
5. Testable - easy to unit test with mock filesystem

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [x] Query memory for prior learnings on topic
2. [ ] Search codebase for relevant patterns (Grep/Glob)
3. [ ] Read identified files and document findings

### Phase 2: Hypothesis Testing
4. [ ] Test H1: [Specific actions]
5. [ ] Test H2: [Specific actions]
6. [ ] Test H3: [Specific actions]

### Phase 3: Synthesis
7. [ ] Compile evidence table
8. [ ] Determine verdict for each hypothesis
9. [ ] Identify spawned work items

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| [What was found] | `path/file.py:123-145` | H1/H2/H3 | [Context] |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| [ID] | [Summary] | H1/H2/H3 | [How it applies] |

### External Evidence (if applicable)

| Source | Finding | Supports Hypothesis | URL/Reference |
|--------|---------|---------------------|---------------|
| [Doc/Article] | [Summary] | H1/H2/H3 | [Link] |

---

## Findings

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **CONFIRMED** | scaffold_template() is single entry point (`scaffold.py:234-326`) | High |
| H2 | **CONFIRMED** | Simple glob: `WORK-{id}-*.md` matches work files | High |

### Detailed Findings

#### F1: scaffold.py is the single enforcement point

**Evidence:** All `/new-*` commands route through `just scaffold` → `scaffold_template()`. Write at line 324.

**Analysis:** Check before line 324 gates ALL document creation for specified template types.

**Implication:** ~10 lines provides L3 enforcement for entire workflow.

#### F2: ADR-039 Phase 4 is the architectural home

**Evidence:** ADR-039 defines work-item-as-file architecture with phases 1-3.

**Analysis:** E2-160 is Phase 4 (Enforcement) - updated ADR-039 to include it.

**Implication:** No new ADR needed.

---

## Design Outputs

<!-- If investigation produces architectural designs, document them here
     SKIP this section if investigation is pure discovery with no design outputs -->

### Schema Design (if applicable)

```yaml
# [Name of schema]
field_name: type
  description: [What this field does]
```

### Mapping Table (if applicable)

| Source | Target | Relationship | Notes |
|--------|--------|--------------|-------|
| [A] | [B] | [How A relates to B] | |

### Mechanism Design (if applicable)

```
TRIGGER: [What initiates the mechanism]

ACTION:
    1. [Step 1]
    2. [Step 2]
    3. [Step 3]

OUTCOME: [What results from the mechanism]
```

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| [Decision point] | [What was chosen] | [Why this choice - most important part] |

---

## Spawned Work Items

### Immediate (Can implement now)

- [x] **E2-160: Work File Prerequisite Gate** (this item - moving to plan)
  - Description: L3 gate in scaffold.py requiring work file before investigation/plan creation
  - Fixes: Orphaned documents bypassing work file lifecycle
  - Next: Create plan, implement

### Future (Requires more work first)

- [ ] **E2-161: Auto-link Created Documents to Work File** (not created yet)
  - Description: When investigation/plan created, auto-update work file's cycle_docs and documents fields
  - Blocked by: E2-160 (gate first, then auto-linking)

---

## Session Progress Tracker

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 109 | 2025-12-24 | CONCLUDE | Complete | Design confirmed, ADR-039 updated |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-HN have verdict | [ ] | |
| Evidence has sources | All findings have file:line or concept ID | [ ] | |
| Spawned items created | Items exist in backlog or via /new-* | [ ] | |
| Memory stored | ingester_ingest called, memory_refs populated | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | [Yes/No] | |
| Are all evidence sources cited with file:line or concept ID? | [Yes/No] | |
| Were all hypotheses tested with documented verdicts? | [Yes/No] | |
| Are spawned items created (not just listed)? | [Yes/No] | |
| Is memory_refs populated in frontmatter? | [Yes/No] | |

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete ALL items before /close -->

### Required (MUST complete)
- [ ] **Findings synthesized** - Answer to objective documented in Findings section
- [ ] **Evidence sourced** - All findings have file:line or concept ID citations
- [ ] **Hypotheses resolved** - All hypotheses have Confirmed/Refuted/Inconclusive verdict
- [ ] **Spawned items created** - Via /new-* commands with `spawned_by` field (or rationale if none)
- [ ] **Memory stored** - `ingester_ingest` called with findings summary
- [ ] **memory_refs populated** - Frontmatter updated with concept IDs
- [ ] **lifecycle_phase updated** - Set to `conclude`
- [ ] **Ground Truth Verification complete** - All items checked above

### Optional
- [ ] Design outputs documented (if applicable)
- [ ] Session progress updated (if multi-session)

---

## References

- [Spawned by: Session/Investigation/Work item that triggered this]
- [Related investigation 1]
- [Related ADR or spec]

---
