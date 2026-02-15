---
name: checkpoint-cycle
type: ceremony
description: Create checkpoint manifest. Scaffold, populate fields, commit.
category: session
input_contract:
  - field: session_number
    type: integer
    required: false
    description: "Session number (auto-detected from context if not provided)"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether checkpoint was created and committed"
  - field: checkpoint_path
    type: path
    guaranteed: on_success
    description: "Path to the created checkpoint manifest"
  - field: memory_concept_ids
    type: list
    guaranteed: on_success
    description: "Concept IDs from stored learnings"
side_effects:
  - "Write checkpoint manifest doc"
  - "Git commit via commit-session"
  - "Store learnings to memory via ingester_ingest"
recipes:
- checkpoint
- commit-session
- session-end
generated: 2025-12-25
last_updated: '2026-02-15'
---
# Checkpoint Cycle

Create a checkpoint manifest for session handoff.

## When to Use

After `/new-checkpoint` scaffolds the file, this skill guides population.

---

## Contract Validation (CH-011)

This ceremony has input/output contracts defined in frontmatter per REQ-CEREMONY-002.
Before proceeding, verify:
- `session_number` is available (from context or `.claude/session` file)
- Summary of work done is available for `completed` field

Contract enforcement mode is controlled by `ceremony_contract_enforcement`
toggle in haios.yaml (currently: warn).

---

## Checkpoint Cycle Phases

```
FILL --> VERIFY --> CAPTURE
```

### 1. FILL Phase

Populate the manifest with session work and learnings.

**What to Do:**

The checkpoint is a **loading manifest**, not an activity log.

**Fields to fill:**

| Field | What to Put |
|-------|-------------|
| `load_principles` | Files next session MUST read (default: S20, S22) |
| `load_memory_refs` | Concept IDs from this session's `ingester_ingest` calls |
| `pending` | Work item IDs for next session |
| `drift_observed` | Principle violations noticed (if any) |
| `completed` | What was done (for git commit message only) |

**Store Learnings:**

For each significant decision/learning this session:

```
ingester_ingest(
  content="<learning>",
  source_path="checkpoint:session-{N}",
  content_type_hint="techne"
)
```

Add returned concept IDs to `load_memory_refs`.

**Exit Criteria:**
- [ ] Manifest fields populated
- [ ] Learnings stored to memory
- [ ] Memory concept IDs added to load_memory_refs

---

### 3. VERIFY Phase

**Goal:** Validate checkpoint manifest for anti-patterns and governance violations before capture.

**Actions:**

1. Invoke anti-pattern-checker agent on the checkpoint manifest:

```python
Task(subagent_type='anti-pattern-checker', input={
  "document_path": checkpoint_path,
  "document_type": "checkpoint",
  "context": "Pre-commit validation before session ends"
})
```

2. Review anti-pattern report:
   - Check for missing required fields
   - Verify load_memory_refs not empty (principle: no learning loss)
   - Confirm drift_observed has companion observation files (if non-empty)

3. If patterns found:
   - Fix identified issues in manifest
   - Re-run verification if critical issues
   - Document exceptions (rare)

**On PASS:** All fields valid, no anti-patterns detected → proceed to CAPTURE

**On FAIL:** Anti-patterns detected → fix manifest and re-verify

**Exit Criteria:**
- [ ] anti-pattern-checker invoked successfully
- [ ] Report reviewed and addressed
- [ ] Manifest passes anti-pattern checks

---

### 2. CAPTURE Phase

**Goal:** Commit checkpoint to git and session record.

**Drift Observation Gate (SHOULD):**

**If `drift_observed` is non-empty**, prompt before commit:

```
Drift observed this session:
- {drift_item_1}
- {drift_item_2}

Create formal observation(s) for triage? [Y/n]
```

**If yes:** For each drift item, create observation file:
```bash
# Write to epochs/{current_epoch}/observations/obs-{session}-{n}.md
```

Use observation template:
- `id`: obs-{session}-{n}
- `triage_status`: pending
- `potential_action`: bugfix | investigation | adr | skill-update

**If no:** Proceed (agent judged drift minor, doesn't need formal tracking).

**Rationale:** Drift mentioned in checkpoint but not captured as observation gets lost. This nudge ensures drift surfaces for triage without being a hard gate.

**Commit:**

```bash
just commit-session {session} "{title}"
just session-end {session}
```

**Exit Criteria:**
- [ ] Drift decisions made (create observations or skip)
- [ ] Manifest committed to git
- [ ] Session record updated

---

## Composition Map

| Phase | Goal | Tool | Artifact |
|-------|------|------|----------|
| FILL | Populate manifest | Edit | checkpoint.md with fields filled |
| VERIFY | Anti-pattern check | Task | Anti-pattern report |
| CAPTURE | Commit & record | Bash | Git commit + session record |

---

## Example Completed Manifest

```yaml
---
template: checkpoint
session: 186
prior_session: 185
date: 2026-01-10

load_principles:
  - .claude/haios/epochs/E2/architecture/S20-pressure-dynamics.md

load_memory_refs:
  - 81222
  - 81248

pending:
  - E2-281
  - E2-282

drift_observed:
  - "survey-cycle is 5 phases, S20 says single-phase"

completed:
  - E2-279
---
```

---

## Key Principle

**The checkpoint is a manifest. The memory is the content. Git is the log.**

No ceremony. No exit criteria checklists. Fill the fields, store learnings, verify, commit.
