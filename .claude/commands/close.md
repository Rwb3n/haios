---
allowed-tools: Bash, Edit, Read, Grep, Glob, mcp__haios-memory__ingester_ingest
description: Close a work item with DoD validation
argument-hint: <backlog_id>
generated: 2025-12-22
last_updated: '2026-01-25T21:35:05'
---
# Close Work Item

Close a work item with Definition of Done (DoD) validation per ADR-033.

**Arguments:** $ARGUMENTS

Parse the backlog_id (e.g., `E2-023`, `INV-033`).

---

## Step 1: Lookup Work Item

**ADR-039:** Work files are the source of truth.
**E2-212:** Work items are now directories: `docs/work/active/{id}/WORK.md`

### 1a. Find work file

Look for work file using directory pattern first, then flat pattern:
```
# Try directory structure first (E2-212)
Glob(pattern="docs/work/active/{backlog_id}/WORK.md")
# Fall back to flat structure (legacy)
Glob(pattern="docs/work/active/WORK-{backlog_id}-*.md")
```

**If work file found:**
1. Read work file frontmatter for `title`, `status`
2. Proceed to Step 1b (find associated documents)

**If NO work file found:**
- Check if it's an investigation (`type: investigation` or legacy INV-*) without a work file
- If investigation type, proceed to Step 1.5 (Investigation DoD)
- Otherwise: Inform user "Work item {backlog_id} not found in docs/work/active/"
- STOP

---

## Step 1.1: Detect Effort Tier (Prospective Predicate — REQ-LIFECYCLE-005)

After finding work item, determine close ceremony tier using WORK.md frontmatter (prospective predicate, not retrospective git diff):

1. Read `effort:` field from WORK.md frontmatter
2. Read `source_files:` list and count entries
3. If `effort: small` AND `source_files` count <= 3: Set `lightweight_close: true`
4. If `effort: medium` or higher: Set `lightweight_close: false`
5. Default (effort field missing): Set `lightweight_close: false` (conservative — absent data MUST NOT produce more permissive classification per REQ-LIFECYCLE-005)

**Note:** This is a prospective predicate (declared scope before work begins). retro-cycle Phase 0's `assess_scale()` is a retrospective predicate (git diff after work). Both are valid for their lifecycle position. Close ceremony tier uses the prospective predicate because tier detection happens before retro-cycle runs.

**Lightweight close path:** If `lightweight_close: true`:
- retro-cycle runs with trivial scaling (Phase 0 assess_scale handles this independently)
- close-work-cycle uses inline DoD checklist (skip dod-validation-cycle)
- checkpoint-cycle uses inline VERIFY (skip anti-pattern-checker)

**Full close path:** If `lightweight_close: false`:
- All ceremonies run at full weight (current behavior, unchanged)

**Flag propagation:** All skill invocations (retro-cycle, close-work-cycle, checkpoint-cycle) execute within the same agent turn. The `lightweight_close` flag persists in agent working memory across skill boundaries. No file write needed.

---

## Chain to Retro Cycle

After work item is found, first invoke retro-cycle for structured reflection:

```
Skill(skill="retro-cycle")
```

This forces the agent into dedicated cognitive space (REFLECT -> DERIVE -> COMMIT -> EXTRACT) before entering "closing mode." Evidence-anchored observations are stored with typed provenance tags.

---

## Chain to Retro-Enrichment Agent

After retro-cycle completes and returns `extracted_items`, invoke retro-enrichment-agent if `extracted_items` is non-empty.

**IMPORTANT:** Before invoking Task(), substitute `{work_id}`, `{memory_concept_ids_json}`, `{extract_concept_ids_json}`, and `{extracted_items_yaml}` with actual values from the retro-cycle return object. Do NOT copy the template verbatim — literal placeholder strings will cause silent malformed input.

```
Task(
  subagent_type='retro-enrichment-agent',
  model='haiku',
  prompt='Enrich retro-cycle EXTRACT output for {work_id}.
    work_id: {work_id}
    memory_concept_ids: {memory_concept_ids_json}
    extract_concept_ids: {extract_concept_ids_json}
    extracted_items: {extracted_items_yaml}
    Cross-reference each item against memory via memory_search_with_experience.
    Annotate with related_memory_ids, convergence_count, prior_work_ids.
    Store enriched output with retro-enrichment:{work_id} provenance.
    Return enriched_items list + enrichment_concept_ids.'
)
```

If `extracted_items` is empty (trivial scale or no actionable items), skip enrichment.
Enrichment never blocks closure — proceed to close-work-cycle regardless of enrichment result.

---

## Chain to Close Work Cycle

After retro-enrichment completes (or was skipped), invoke close-work-cycle:

```
Skill(skill="close-work-cycle")
```

The skill guides through VALIDATE -> ARCHIVE -> CHAIN phases.

**Note:** The remaining steps below document the skill's phases for reference.

---

### 1b. Find associated documents

Use Grep to find all documents referencing this backlog_id:

```
Grep(pattern="backlog_id.*{backlog_id}", path="docs/", glob="**/*.md")
```

This finds documents with either:
- `backlog_id: {ID}` (single reference)
- `backlog_ids: [...{ID}...]` (list reference)

### 1c. Categorize results by document type

Parse the file paths to categorize:
- `docs/work/active/{id}/plans/PLAN.md` or legacy `docs/plans/PLAN-*.md` → Plans (read frontmatter `status:` field)
- `docs/checkpoints/*.md` → Checkpoints
- `docs/reports/*.md` → Reports
- `docs/ADR/*.md` → ADRs
- `docs/investigations/*.md` → Investigations

### 1d. Extract plan statuses

For each plan file found, read the frontmatter and extract the `status:` field.
Plans are relevant for DoD validation (must be complete).

---

## Step 1.5: Investigation-Specific DoD (type: investigation OR INV-* prefix)

**If work item has `type: investigation` OR backlog_id starts with `INV-`**, apply investigation-specific DoD before standard DoD:

### 1.5a. Find investigation file

```
Glob(pattern="docs/investigations/INVESTIGATION-{backlog_id}-*.md")
```

### 1.5b. Read and verify investigation DoD

Read the investigation file and check these criteria:

| Criterion | Check | Fail Condition |
|-----------|-------|----------------|
| **Findings documented** | Read `## Findings` section | Contains placeholder text or < 50 characters |
| **Spawned items exist** | Read `## Spawned Work Items` section | Contains "None yet" |
| **Memory refs populated** | Check frontmatter `memory_refs:` | Missing or empty array |

**Placeholder detection:**
- Findings placeholder: `[Document findings here after investigation]`
- Spawned placeholder: `- [ ] None yet`

### 1.5c. Report investigation DoD status

Report to user:
```
Investigation DoD for {backlog_id}:
- [x/!] Findings documented
- [x/!] Spawned work items created
- [x/!] Memory refs populated
```

### 1.5d. Gate on investigation DoD

**If ANY criterion fails:**
- Report: "Investigation DoD not met. Complete CONCLUDE phase first."
- List what's missing
- STOP (do not proceed to standard DoD)

**If ALL pass:**
- Continue to Step 2 (standard DoD)

---

## Step 2: Validate Definition of Done (DoD)

Per ADR-033, a work item is COMPLETE when:

| Criterion | Verification Method |
|-----------|---------------------|
| Tests pass | Ask user: "Do all tests pass?" |
| WHY captured | Check if any checkpoint/report has memory refs OR ask user |
| Docs current | Ask user: "Are CLAUDE.md/READMEs updated?" |
| Traced files complete | Check all associated plans have status: complete |

### Validation Logic:

1. **Check plan statuses:**
   - If ANY associated plan has status != `complete`:
     - List the incomplete plans
     - Ask: "These plans are not complete. Continue anyway? (y/n)"
     - If no, STOP

2. **Prompt user for remaining DoD criteria:**
   - "Confirm DoD for {backlog_id}:"
   - "- [?] Tests pass"
   - "- [?] WHY captured (reasoning stored to memory)"
   - "- [?] Docs current (CLAUDE.md, READMEs)"
   - Ask user to confirm each OR accept all

3. **If DoD validation fails:**
   - Report what's missing
   - STOP (do not close incomplete work)

---

## Step 3: Execute Closure

If DoD passes:

### 3a. Update work file status

Per ADR-041 "status over location": work items stay in `docs/work/active/` until epoch cleanup. The `status` field determines state, not directory path.

1. **Update work file frontmatter:**
   - Change `status: active` to `status: complete`
   - Change `closed: null` to `closed: {today's date YYYY-MM-DD}`

2. **No directory move** - work item stays in `docs/work/active/`

### 3b. Update associated plans (if any not already complete)

For each plan file in the work item:
- Use Edit to change frontmatter `status: <current>` to `status: complete`

### 3c. Store closure summary to memory

Call `mcp__haios-memory__ingester_ingest`:
```
content: "Work Item Closure: {backlog_id}

Title: {title}

DoD Verified:
- Tests: PASS
- WHY captured: CONFIRMED
- Docs current: CONFIRMED
- Traced files: COMPLETE

Associated Documents:
- Plans: {list}
- Checkpoints: {list}

Closure Reason: {brief summary of what was accomplished}"

source_path: "closure:{backlog_id}"
content_type_hint: "techne"
```

### 3d. Refresh haios-status.json

Run:
```bash
just update-status
```

> **Note (E2-190):** Must use full `update-status` (not slim) so `just ready` shows accurate data.

### 3e. Git commit (E2-166)

Commit the closure changes:
```bash
just commit-close {backlog_id}
```

This commits:
- Work file move to archive
- Investigation/plan status updates
- haios-status.json changes

---

## Step 4: Report Closure

Report to user:
- "Work item {backlog_id} CLOSED"
- "Memory concept ID: {id from ingester response}"
- "Updated files:"
  - `docs/work/active/{backlog_id}/WORK.md` (status: complete)
  - {plan files updated}
- "haios-status.json refreshed"

---

## Verification Checklist

After closure, verify:

- [ ] Work file in `docs/work/active/` has `status: complete` and `closed: {date}`
- [ ] Associated plan files show `status: complete` in frontmatter
- [ ] Memory contains closure summary (queryable via "closure:{backlog_id}")

---

## Example Usage

```
/close E2-031
```

Expected flow:
1. Find work file: `docs/work/active/E2-031/WORK.md`
2. Invoke retro-cycle (REFLECT->DERIVE->COMMIT->EXTRACT)
3. Invoke retro-enrichment-agent (if extracted_items non-empty)
4. Check work directory for plans: `docs/work/active/E2-031/plans/`
5. Read plan frontmatter to check statuses
6. Prompt user for DoD confirmation
7. Update work file status (stays in active/ per ADR-041)
8. Update plan statuses to complete
9. Store closure summary to memory
10. Refresh haios-status.json
11. Report completion

---
