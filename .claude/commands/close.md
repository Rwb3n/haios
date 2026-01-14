---
allowed-tools: Bash, Edit, Read, Grep, Glob, mcp__haios-memory__ingester_ingest
description: Close a work item with DoD validation
argument-hint: <backlog_id>
generated: 2025-12-22
last_updated: '2026-01-08T21:34:40'
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
- Check if it's an investigation (INV-*) without a work file
- If INV-*, proceed to Step 1.5 (Investigation DoD)
- Otherwise: Inform user "Work item {backlog_id} not found in docs/work/active/"
- STOP

---

## Chain to Observation Capture

After work item is found, first invoke observation-capture-cycle for genuine reflection:

```
Skill(skill="observation-capture-cycle")
```

This forces the agent into dedicated cognitive space (RECALL -> NOTICE -> COMMIT) before entering "closing mode."

---

## Chain to Close Work Cycle

After observation-capture-cycle completes, invoke close-work-cycle:

```
Skill(skill="close-work-cycle")
```

The skill guides through VALIDATE -> ARCHIVE -> MEMORY phases.

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

## Step 1.5: Investigation-Specific DoD (INV-* only)

**If backlog_id starts with `INV-`**, apply investigation-specific DoD before standard DoD:

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
2. Invoke observation-capture-cycle (RECALL->NOTICE->COMMIT)
3. Check work directory for plans: `docs/work/active/E2-031/plans/`
4. Read plan frontmatter to check statuses
5. Prompt user for DoD confirmation
6. Update work file status (stays in active/ per ADR-041)
7. Update plan statuses to complete
8. Store closure summary to memory
9. Refresh haios-status.json
10. Report completion

---
