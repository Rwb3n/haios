---
name: open-epoch-ceremony
type: ceremony
description: "Initialize a new epoch with directory structure, config transition, work item triage, and arc decomposition."
category: closure
input_contract:
  - field: epoch_id
    type: string
    required: true
    description: "New epoch ID (e.g., E2.8)"
  - field: prior_epoch_id
    type: string
    required: true
    description: "Just-closed epoch ID (e.g., E2.7)"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether all phases completed"
  - field: epoch_id
    type: string
    guaranteed: always
    description: "The new epoch ID"
  - field: arcs
    type: list
    guaranteed: on_success
    description: "Arc names after decomposition"
  - field: migrated_items
    type: integer
    guaranteed: on_success
    description: "Count of work items triaged"
side_effects:
  - "Create epoch directory structure"
  - "Update haios.yaml epoch config"
  - "Update EPOCH.md status to Active"
  - "Triage prior epoch work items"
  - "Log OpenEpoch event to governance-events.jsonl"
generated: 2026-02-17
last_updated: "2026-02-17"
---
# Open Epoch Ceremony

Initialize a new epoch after close-epoch-ceremony completes. Creates structure, migrates config, triages work items, and decomposes arcs.

## When to Use

**Manual invocation:** `Skill(skill="open-epoch-ceremony")` immediately after close-epoch-ceremony completes.

**Rare:** Epochs are long-lived containers. This ceremony is invoked infrequently.

**Prerequisite:** close-epoch-ceremony MUST have completed for the prior epoch.

---

## The Ceremony Loop

```
close-epoch-ceremony (VALIDATE -> ARCHIVE -> TRANSITION)
    |
    v
open-epoch-ceremony (SCAFFOLD -> CONFIG -> TRIAGE -> DECOMPOSE -> VALIDATE)
    |
    v
arc-decomposition (operator design session)
    |
    v
first coldstart of new epoch
```

---

## The Cycle

```
SCAFFOLD --> CONFIG --> TRIAGE --> DECOMPOSE --> VALIDATE
```

### 1. SCAFFOLD Phase

**Goal:** Create epoch directory structure.

**Actions:**
1. Create epoch directory: `.claude/haios/epochs/E{X}_{Y}/`
2. Create subdirectories:
   - `arcs/` — arc definitions (populated in DECOMPOSE)
   - `architecture/` — architecture docs (may carry forward)
   - `observations/` — session observations
3. If EPOCH.md doesn't exist, scaffold it:
   ```bash
   # Scaffold or copy from template
   ```
4. If EPOCH.md already exists (pre-created in prior session), verify structure

**Pre-existing EPOCH.md:** Some epochs are designed before they open (E2.8 was written during E2.7). If EPOCH.md exists, SCAFFOLD verifies it has required sections rather than creating it.

**Required EPOCH.md sections:**
- L4 Object Definition (ID, Name, Status, Started, Prior, Next)
- Purpose (mission statement)
- What We Carry Forward
- Exit Criteria
- References

**Exit Criteria:**
- [ ] Epoch directory exists with arcs/, architecture/, observations/
- [ ] EPOCH.md exists with required sections
- [ ] Status field is `Active` (or ready to be set)

**Tools:** Bash(mkdir), Read, Write

---

### 2. CONFIG Phase

**Goal:** Update all configuration files for the new epoch.

**Files to update:**

| File | Fields | Example |
|------|--------|---------|
| `.claude/haios/config/haios.yaml` | `epoch.current`, `epoch.subversion`, `epoch.epoch_file`, `epoch.architecture_dir`, `epoch.arcs_dir`, `epoch.observations_dir`, `epoch.prior_epoch`, `epoch.active_arcs`, `manifest.version`, `manifest.description` | `current: E2.8`, `version: "2.8"` |
| EPOCH.md | `**Status:** Active`, `**Started:** {date} (Session {N})` | See SCAFFOLD phase |

**Verification:** After updating, read haios.yaml back and verify:
```python
from config import ConfigLoader
ConfigLoader.reset()
config = ConfigLoader.get()
assert config.haios["epoch"]["current"] == "E2.8"
assert config.haios["manifest"]["version"] == "2.8"
```

**Known gaps (S393 retro finding):**
- `identity.yaml` epoch path — check if this file still exists and needs updating
- `CLAUDE.md` footer — version line should reflect new epoch
- These were missed in E2.7->E2.8 transition. MUST check both.

**Exit Criteria:**
- [ ] haios.yaml epoch section updated (all fields)
- [ ] haios.yaml manifest version and description updated
- [ ] EPOCH.md Status set to Active with Started date
- [ ] ConfigLoader.reset() + verify reads new values
- [ ] identity.yaml checked and updated if needed
- [ ] CLAUDE.md version footer checked and updated if needed

**Tools:** Edit, Read, Bash(python verification)

---

### 3. TRIAGE Phase

**Goal:** Audit and triage all work items from the prior epoch.

This is the most judgment-intensive phase. It ensures nothing falls through the cracks at epoch boundaries.

**Actions:**

#### 3a. Audit all active work items
```python
# Find all non-complete items
for work_dir in (PROJECT_ROOT / "docs/work/active").iterdir():
    # Read WORK.md, check status and queue_position
    # Categorize: complete, active, blocked, parked
```

#### 3b. Fix stale queue positions
Items with `status: complete` but `queue_position != done` are stale. Batch fix:
- If state machine allows transition: use `set_queue_position()`
- If blocked by state machine: direct file write (document as admin cleanup)

**S393 finding:** 16 items were stale from E2.5. The queue state machine has no `backlog -> done` path for pre-state-machine items. This is a known gap (Memory: 85840).

#### 3c. Categorize remaining active items

For each non-complete item, assign disposition:

| Disposition | Meaning | Action |
|-------------|---------|--------|
| **carry** | Relevant to new epoch | Update `extensions.epoch`, assign to arc/chapter |
| **defer** | Not relevant now, will be later | Note in EPOCH.md deferred table with destination epoch |
| **park** | Out of scope indefinitely | Set `queue_position: parked` with rationale |
| **close** | Obsoleted by new epoch's approach | Close with rationale |

#### 3d. Update item metadata
For carried items:
- Update `extensions.epoch` to new epoch ID
- Update `chapter` and `arc` fields if reassigned
- Update `queue_position` if needed (e.g., unpark for new epoch)

#### 3e. Report triage results
```
Triage Results:
- Stale fixed: {N}
- Carried to {epoch}: {list}
- Deferred to {epoch}: {list}
- Parked: {list}
- Closed: {list}
- Total active remaining: {N}
```

**Exit Criteria:**
- [ ] All active items audited
- [ ] Stale queue positions fixed
- [ ] Each active item has a disposition (carry/defer/park/close)
- [ ] Carried items have updated epoch/chapter/arc fields
- [ ] Triage results reported

**Tools:** Read, Grep, Bash(python), Edit

---

### 4. DECOMPOSE Phase

**Goal:** Define arcs and chapters for the new epoch.

This is an **operator design session**, not a fully automatable phase. The agent provides evidence, the operator provides strategy.

**Actions:**

#### 4a. Query memory for epoch inputs
```python
# Query for observations, retro findings, feature requests, bugs
memory_search_with_experience(query="<epoch theme> observations features bugs", mode="knowledge_lookup")
```

Cast a wide net:
- Retro extractions (features + bugs)
- Observation triage findings
- Architectural decisions from prior epochs
- Ancient aspirations (L0/L1 principles that connect to this epoch's mission)

#### 4b. Present evidence synthesis to operator
Organize findings by theme. Let patterns emerge from evidence, don't force structure.

#### 4c. Operator-agent design dialogue
- Agent proposes strawman arc decomposition
- Operator challenges, reshapes, approves
- Iterate 1-2 rounds to consensus

#### 4d. Write arc structure
For each arc:
1. Create `arcs/{arc_name}/ARC.md` with:
   - Definition (ID, Epoch, Theme, Status)
   - Purpose
   - Requirements Implemented
   - Chapters table
   - Exit Criteria
   - References
2. Update EPOCH.md with arc tables
3. Update haios.yaml `epoch.active_arcs` list

**Exit Criteria:**
- [ ] Memory queried for epoch-relevant findings
- [ ] Evidence synthesized and presented to operator
- [ ] Arc decomposition agreed with operator
- [ ] ARC.md files created for each arc
- [ ] EPOCH.md updated with arc tables and chapter listings
- [ ] haios.yaml `active_arcs` populated

**Tools:** memory_search_with_experience, AskUserQuestion, Write, Edit

---

### 5. VALIDATE Phase

**Goal:** Verify the epoch is fully initialized and consistent.

**Consistency checks:**

| Check | Method | Expected |
|-------|--------|----------|
| haios.yaml epoch.current | Read config | Matches new epoch ID |
| haios.yaml active_arcs | Read config | Non-empty, matches ARC.md files |
| EPOCH.md Status | Read file | `Active` |
| EPOCH.md arcs table | Read file | Matches ARC.md files |
| ARC.md files exist | Glob | One per active_arcs entry |
| Each ARC.md has chapters | Read files | Non-empty chapters table |
| Carried work items updated | Read items | `extensions.epoch` matches new epoch |
| No orphan items | Audit | All active items have disposition |

**Actions:**
1. Run each check
2. Report results
3. If any check fails: report and fix before completing
4. Log `OpenEpoch` governance event

**Exit Criteria:**
- [ ] All consistency checks pass
- [ ] OpenEpoch event logged to governance-events.jsonl
- [ ] Ceremony complete

**Tools:** Read, Glob, Grep, Bash

---

## Composition Map

| Phase | Primary Tool | Operator Involvement | Token Cost |
|-------|--------------|---------------------|------------|
| SCAFFOLD | Bash, Write | None (mechanical) | Low |
| CONFIG | Edit, Read, Bash | None (mechanical) | Low |
| TRIAGE | Read, Grep, Edit | Disposition decisions for ambiguous items | Medium |
| DECOMPOSE | memory_search, AskUserQuestion, Write | **High** (strategy) | High |
| VALIDATE | Read, Glob, Grep | None (mechanical) | Low |

---

## Quick Reference

| Phase | Question to Ask | If NO |
|-------|-----------------|-------|
| SCAFFOLD | Does epoch directory exist? | Create it |
| SCAFFOLD | Does EPOCH.md exist? | Scaffold or create |
| CONFIG | Is haios.yaml updated? | Edit config |
| CONFIG | Is identity.yaml updated? | Check and edit if needed |
| CONFIG | Is CLAUDE.md footer current? | Update version line |
| TRIAGE | Are all active items audited? | Audit remaining |
| TRIAGE | Are stale queue positions fixed? | Batch fix |
| TRIAGE | Does each item have a disposition? | Assign carry/defer/park/close |
| DECOMPOSE | Is memory queried? | Query for epoch inputs |
| DECOMPOSE | Are arcs agreed with operator? | Design dialogue |
| DECOMPOSE | Are ARC.md files created? | Write them |
| VALIDATE | Do all consistency checks pass? | Fix failures |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Five phases | SCAFFOLD -> CONFIG -> TRIAGE -> DECOMPOSE -> VALIDATE | Covers full lifecycle from structure to verification |
| DECOMPOSE is operator-driven | Agent provides evidence, operator provides strategy | L3.4: Operator holds strategy, agent holds execution |
| TRIAGE before DECOMPOSE | Clean backlog before designing new arcs | Stale items pollute arc planning (S393: 16 stale found) |
| Memory query in DECOMPOSE | Cast wide net across retro findings, observations, aspirations | S393 validated: deep memory query connected L0 to E2.8 architecture |
| VALIDATE as final gate | Consistency checks after all changes | Catch config drift early (S393: manifest version missed) |
| Mirror close-epoch-ceremony | Symmetric ceremony pair | Close = VALIDATE -> ARCHIVE -> TRANSITION. Open = SCAFFOLD -> CONFIG -> TRIAGE -> DECOMPOSE -> VALIDATE |

---

## S393 Lessons (First Execution)

The E2.7 -> E2.8 transition was the first execution of this ceremony (ad hoc, pre-standardization). Lessons captured:

| Finding | Impact | Now Addressed |
|---------|--------|---------------|
| manifest.version not updated | Config drift | CONFIG phase checks manifest |
| identity.yaml not checked | Potential stale loader config | CONFIG phase includes identity.yaml |
| CLAUDE.md footer not updated | Stale version reference | CONFIG phase includes CLAUDE.md |
| 16 stale queue positions | False backlog size | TRIAGE phase includes stale fix |
| WORK-136 stale reference in EPOCH.md | Misleading scope | TRIAGE phase audits all references |
| Memory query surfaced L0 connection | Arc quality improved | DECOMPOSE phase mandates memory query |
| No governance event logged | Missing audit trail | VALIDATE phase logs OpenEpoch event |

---

## Related

- **close-epoch-ceremony skill:** Symmetric pair (closes the epoch this skill opens the next one)
- **CH-008 (E2.4):** Original epoch transition spec (5 steps). This skill implements and extends it.
- **ADR-042:** Arc > Chapter hierarchy (arcs are the primary decomposition unit)
- **REQ-CEREMONY-001:** Ceremonies govern side-effects
- **REQ-CEREMONY-002:** Each ceremony has input/output contract
