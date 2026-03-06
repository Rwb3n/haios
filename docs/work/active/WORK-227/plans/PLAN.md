---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-03-06
backlog_id: WORK-227
title: "Investigation CONCLUDE Spawn Completeness Enforcement"
author: Hephaestus
lifecycle_phase: plan
session: 463
generated: 2026-03-06
last_updated: 2026-03-06T22:36:26

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-227/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete content, not pseudocode"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: Investigation CONCLUDE Spawn Completeness Enforcement

---

## Goal

After this plan is complete, the investigation CONCLUDE phase will enforce that every finding-recommended work item is either spawned or explicitly deferred with rationale, preventing silent partial-spawn scenarios like the WORK-218 incident.

---

## Open Decisions

None. All three deliverables are clearly scoped by acceptance criteria.

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/templates/investigation/CONCLUDE.md` | MODIFY | 2 |
| `.claude/commands/close.md` | MODIFY | 2 |
| `.claude/skills/investigation-cycle/SKILL.md` | MODIFY | 2 |
| `.claude/templates/investigation.md` | MODIFY | 2 |

### Consumer Files

No consumer files. These are agent-read markdown files (Tier 3). No Python imports or runtime consumers — agents read these at invocation time.

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| N/A | N/A | Doc-only changes — no Python tests applicable |

**SKIP RATIONALE (Tests):** All three files are markdown templates/skills/commands read by agents at invocation time. No Python code is created or modified. Verification is structural (grep for expected content).

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | No new files |
| Files to modify | 4 | Primary Files table |
| Tests to write | 0 | Doc-only — structural verification via grep |
| Total blast radius | 4 | Four markdown files |

---

## Layer 1: Specification

### Current State

**File 1: CONCLUDE.md template** (`.claude/templates/investigation/CONCLUDE.md:105-113`)
```markdown
## Spawned Work

| ID | Title | spawned_by |
|----|-------|------------|
| | | {this_work_id} |

### Not Spawned Rationale (if none)

[Explain why this investigation produced no follow-on work]
```

**Behavior:** Template has a "Spawned Work" table with ID/Title/spawned_by columns. The "Not Spawned Rationale" section handles zero-spawn. No disposition tracking for partial-spawn scenarios.

**Problem:** If findings recommend 5 items but only 2 are spawned, there is no enforcement requiring the remaining 3 to be explicitly deferred.

---

**File 2: close.md Step 1.5b** (`.claude/commands/close.md:161-168`)
```markdown
### 1.5b. Read and verify investigation DoD

| Criterion | Check | Fail Condition |
|-----------|-------|----------------|
| **Findings documented** | Read `## Findings` section | Contains placeholder text or < 50 characters |
| **Spawned items exist** | Read `## Spawned Work Items` section | Contains "None yet" |
| **Memory refs populated** | Check frontmatter `memory_refs:` | Missing or empty array |
```

**Behavior:** Binary check — "Does spawned section contain 'None yet'?" Passes as long as any spawning happened.

**Problem:** Does not cross-reference findings against spawned items. 2 out of 5 recommended items spawned = passes.

---

**File 3: investigation-cycle SKILL.md CONCLUDE exit criteria** (`.claude/skills/investigation-cycle/SKILL.md:277`)
```markdown
- [ ] Spawned work items created with `spawned_by` field linking to investigation
```

**Behavior:** "Spawned work items created" — presence check only.

**Problem:** No completeness qualifier. Doesn't require all recommended items to have disposition.

### Desired State

**File 1: CONCLUDE.md template** — Replace "Spawned Work" section with "Work Disposition" table:
```markdown
## Work Disposition

<!-- MUST: Every finding that recommends follow-on work MUST appear in this table.
     Each item must have a disposition: SPAWNED (with ID) or DEFERRED (with rationale).
     Close command Step 1.5b validates completeness against findings. -->

| Finding | Recommended Work | Disposition | ID / Rationale |
|---------|-----------------|-------------|----------------|
| [K1/I1] | [Work description] | SPAWNED | WORK-XXX |
| [K2] | [Work description] | DEFERRED | [Why not now] |

### No Follow-On Work (if none)

[Explain why this investigation produced no follow-on work items.
 Valid reasons: all questions answered, no actionable gaps found, purely informational.]
```

**Behavior:** Every finding-recommended item must have explicit disposition (SPAWNED or DEFERRED). Table links back to specific findings by ID.

---

**File 2: close.md Step 1.5b** — Replace binary check with cross-reference validation:
```markdown
| **Spawned work complete** | Read `## Work Disposition` table; verify every row has disposition SPAWNED or DEFERRED. If section is `## Spawned Work Items` (legacy), fall back to "Contains 'None yet'" check | Any row missing disposition, or table has placeholder rows |
```

**Behavior:** Validates that every finding-recommended item has explicit disposition. Falls back to legacy check for older investigations.

---

**File 3: investigation-cycle SKILL.md** — Update CONCLUDE exit criteria:
```markdown
- [ ] Work Disposition table complete: every finding-recommended item has disposition (SPAWNED with ID, or DEFERRED with rationale)
```

**Behavior:** Completeness qualifier — not just "did spawning happen" but "is every recommendation accounted for."

---

**File 4: Monolithic investigation template** (`.claude/templates/investigation.md:294-317`)
```markdown
## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

- [ ] **{ID}: {Title}**
  - Description: [What this item does]
  - Fixes: [What problem from investigation this addresses]
  - Spawned via: `/new-plan {ID} "{Title}"`

### Future (Requires more work first)

- [ ] **{ID}: {Title}**
  - Description: [What this item does]
  - Blocked by: [What must happen first]

### Not Spawned Rationale (if no items)

**RATIONALE:** [Why this investigation produced no spawned items - rare, explain thoroughly]
```

**Behavior:** Monolithic template (deprecated but still on disk) has its own "Spawned Work Items" section with binary presence check. No disposition tracking.

**Problem:** If any agent reads this template instead of the fractured CONCLUDE.md, the new enforcement is silently bypassed.

**Desired State:** Add deprecation redirect and update to use Work Disposition table:
```markdown
## Work Disposition

<!-- DEPRECATED: This monolithic template is preserved for backward compatibility.
     Prefer fractured template: .claude/templates/investigation/CONCLUDE.md

     MUST: Every finding that recommends follow-on work MUST appear in this table.
     Each item must have a disposition: SPAWNED (with ID) or DEFERRED (with rationale). -->

| Finding | Recommended Work | Disposition | ID / Rationale |
|---------|-----------------|-------------|----------------|
| [K1/I1] | [Work description] | SPAWNED | WORK-XXX |
| [K2] | [Work description] | DEFERRED | [Why not now] |

### No Follow-On Work (if none)

[Explain why this investigation produced no follow-on work items.]
```

---

**File 3 additional: Quick Reference table** (`.claude/skills/investigation-cycle/SKILL.md:351`)
```markdown
| CONCLUDE | Are spawned items created? | Create via /new-* commands |
```

**Problem:** After exit criteria update, Quick Reference still says "Are spawned items created?" — inconsistent within the same file.

**Desired State:**
```markdown
| CONCLUDE | Is Work Disposition table complete? | Complete disposition for all findings |
```

### Tests

**SKIP RATIONALE:** Doc-only changes. No Python code. Verification is structural grep for expected content patterns.

### Design

#### File 1 (MODIFY): `.claude/templates/investigation/CONCLUDE.md`

**Location:** Lines 105-121 — replace "Spawned Work" section

**Current Code:**
```markdown
## Spawned Work

| ID | Title | spawned_by |
|----|-------|------------|
| | | {this_work_id} |

### Not Spawned Rationale (if none)

[Explain why this investigation produced no follow-on work]
```

**Target Code:**
```markdown
## Work Disposition

<!-- MUST: Every finding that recommends follow-on work MUST appear in this table.
     Each item must have a disposition: SPAWNED (with ID) or DEFERRED (with rationale).
     Close command Step 1.5b validates completeness against findings. -->

| Finding | Recommended Work | Disposition | ID / Rationale |
|---------|-----------------|-------------|----------------|
| [K1/I1] | [Work description] | SPAWNED | WORK-XXX |
| [K2] | [Work description] | DEFERRED | [Why not now] |

### No Follow-On Work (if none)

[Explain why this investigation produced no follow-on work items.
 Valid reasons: all questions answered, no actionable gaps found, purely informational.]
```

Also update output_contract to add `work_disposition` field:
```yaml
- field: work_disposition
  type: table
  required: false
  description: Every finding-recommended item with disposition (SPAWNED/DEFERRED)
```

And remove the old `spawned_work` field from output_contract.

#### File 2 (MODIFY): `.claude/commands/close.md`

**Location:** Line 168 — replace spawned items row in Step 1.5b table

**Current Code:**
```markdown
| **Spawned items exist** | Read `## Spawned Work Items` section | Contains "None yet" |
```

**Target Code:**
```markdown
| **Spawned work complete** | Read `## Work Disposition` table; verify every row has disposition (SPAWNED or DEFERRED). Legacy fallback: if `## Spawned Work Items` exists instead, check for "None yet" | Any row missing disposition, or table has only placeholder rows |
```

#### File 3 (MODIFY): `.claude/skills/investigation-cycle/SKILL.md`

**Location:** Line 277 — replace exit criteria item

**Current Code:**
```markdown
- [ ] Spawned work items created with `spawned_by` field linking to investigation
```

**Target Code:**
```markdown
- [ ] Work Disposition table complete: every finding-recommended item has disposition (SPAWNED with ID, or DEFERRED with rationale)
```

#### File 4 (MODIFY): `.claude/templates/investigation.md`

**Location:** Lines 294-317 — replace "Spawned Work Items" section

**Current Code:**
```markdown
## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

- [ ] **{ID}: {Title}**
  - Description: [What this item does]
  - Fixes: [What problem from investigation this addresses]
  - Spawned via: `/new-plan {ID} "{Title}"`

### Future (Requires more work first)

- [ ] **{ID}: {Title}**
  - Description: [What this item does]
  - Blocked by: [What must happen first]

### Not Spawned Rationale (if no items)

**RATIONALE:** [Why this investigation produced no spawned items - rare, explain thoroughly]
```

**Target Code:**
```markdown
## Work Disposition

<!-- DEPRECATED: This monolithic template is preserved for backward compatibility.
     Prefer fractured template: .claude/templates/investigation/CONCLUDE.md

     MUST: Every finding that recommends follow-on work MUST appear in this table.
     Each item must have a disposition: SPAWNED (with ID) or DEFERRED (with rationale). -->

| Finding | Recommended Work | Disposition | ID / Rationale |
|---------|-----------------|-------------|----------------|
| [K1/I1] | [Work description] | SPAWNED | WORK-XXX |
| [K2] | [Work description] | DEFERRED | [Why not now] |

### No Follow-On Work (if none)

[Explain why this investigation produced no follow-on work items.]
```

#### File 3 additional: Quick Reference table in `.claude/skills/investigation-cycle/SKILL.md`

**Location:** Line 351

**Current Code:**
```markdown
| CONCLUDE | Are spawned items created? | Create via /new-* commands |
```

**Target Code:**
```markdown
| CONCLUDE | Is Work Disposition table complete? | Complete disposition for all findings |
```

### Call Chain

No call chain — these are agent-read markdown files, not runtime code.

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Table name "Work Disposition" | Over "Spawned Work" | Reflects both spawned AND deferred items, not just spawned |
| Finding column links to K/I/U IDs | Over free-text | Creates traceable link between epistemic review findings and disposition decisions |
| Legacy fallback in close.md | Keep old check for `## Spawned Work Items` | Older investigations used the old format; don't break retroactive closure |
| DEFERRED requires rationale | Over silent omission | Makes the decision explicit and auditable per L3.2 Evidence Over Assumption |

### Edge Cases

| Case | Handling | Verification |
|------|----------|------|
| Zero findings recommend work | "No Follow-On Work" section with rationale | close.md accepts empty disposition table with rationale section |
| Legacy investigation format | close.md falls back to "None yet" check | Legacy pattern still works |
| Mixed SPAWNED/DEFERRED | All valid — every row just needs disposition | Grep for disposition column completeness |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent ignores new template | L — agent reads template each time | Template comment explains MUST requirement |
| Close command false-positive on legacy | L — legacy check is permissive | Explicit fallback logic documented |

---

## Layer 2: Implementation Steps

### Step 1: Modify CONCLUDE.md template
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY)
- **input:** Current CONCLUDE.md read and understood
- **action:** Replace "Spawned Work" section (lines 105-121) with "Work Disposition" table. Update output_contract frontmatter: replace `spawned_work` with `work_disposition`.
- **output:** CONCLUDE.md has Work Disposition table with Finding/Recommended Work/Disposition/ID columns
- **verify:** `grep "Work Disposition" .claude/templates/investigation/CONCLUDE.md` returns 1+ match AND `grep "Spawned Work" .claude/templates/investigation/CONCLUDE.md` returns 0 matches

### Step 2: Modify close.md Step 1.5b
- **spec_ref:** Layer 1 > Design > File 2 (MODIFY)
- **input:** Step 1 complete
- **action:** Replace "Spawned items exist" row with "Spawned work complete" row including cross-reference validation and legacy fallback
- **output:** close.md Step 1.5b validates disposition completeness
- **verify:** `grep "Work Disposition" .claude/commands/close.md` returns 1+ match AND `grep "Spawned items exist" .claude/commands/close.md` returns 0 matches

### Step 3: Modify investigation-cycle SKILL.md (exit criteria + Quick Reference)
- **spec_ref:** Layer 1 > Design > File 3 (MODIFY) + File 3 additional
- **input:** Step 2 complete
- **action:** (a) Replace spawned work exit criteria line with completeness-qualified version. (b) Update Quick Reference table row for CONCLUDE from "Are spawned items created?" to "Is Work Disposition table complete?"
- **output:** CONCLUDE exit criteria and Quick Reference both require disposition completeness
- **verify:** `grep "Work Disposition table complete" .claude/skills/investigation-cycle/SKILL.md` returns 1+ match AND `grep "Spawned work items created with" .claude/skills/investigation-cycle/SKILL.md` returns 0 matches AND `grep "Are spawned items created" .claude/skills/investigation-cycle/SKILL.md` returns 0 matches

### Step 4: Modify monolithic investigation template
- **spec_ref:** Layer 1 > Design > File 4 (MODIFY)
- **input:** Step 3 complete
- **action:** Replace "Spawned Work Items" section (lines 294-317) with "Work Disposition" table including deprecation redirect comment
- **output:** Monolithic template has Work Disposition table consistent with fractured template
- **verify:** `grep "Work Disposition" .claude/templates/investigation.md` returns 1+ match AND `grep "## Spawned Work Items" .claude/templates/investigation.md` returns 0 matches

---

## Ground Truth Verification

### Tests

**SKIP RATIONALE:** No Python code modified. All changes are markdown templates/skills/commands.

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| CONCLUDE.md has Work Disposition table | `grep "Work Disposition" .claude/templates/investigation/CONCLUDE.md` | 1+ match |
| close.md Step 1.5b validates disposition completeness | `grep "Spawned work complete" .claude/commands/close.md` | 1+ match |
| investigation-cycle CONCLUDE exit criteria has completeness qualifier | `grep "Work Disposition table complete" .claude/skills/investigation-cycle/SKILL.md` | 1+ match |
| Quick Reference table updated | `grep "Is Work Disposition table complete" .claude/skills/investigation-cycle/SKILL.md` | 1+ match |
| Monolithic template has Work Disposition | `grep "Work Disposition" .claude/templates/investigation.md` | 1+ match |
| Monolithic template has deprecation redirect | `grep "DEPRECATED" .claude/templates/investigation.md` | 1+ match |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| Old "Spawned Work" section removed from CONCLUDE.md | `grep "## Spawned Work$" .claude/templates/investigation/CONCLUDE.md` | 0 matches |
| Old binary check removed from close.md | `grep "Spawned items exist" .claude/commands/close.md` | 0 matches |
| Old exit criteria removed from SKILL.md | `grep "Spawned work items created with" .claude/skills/investigation-cycle/SKILL.md` | 0 matches |
| Old Quick Reference removed from SKILL.md | `grep "Are spawned items created" .claude/skills/investigation-cycle/SKILL.md` | 0 matches |
| Old "Spawned Work Items" removed from monolithic | `grep "## Spawned Work Items" .claude/templates/investigation.md` | 0 matches |

### Completion Criteria (DoD)

- [ ] All WORK.md deliverables verified (table above)
- [ ] No stale references (Consumer Integrity table above)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" not applicable — doc-only change. Structural grep verification substitutes.

---

## References

- docs/work/active/WORK-221/WORK.md (parent investigation)
- .claude/templates/investigation/CONCLUDE.md (template to update)
- .claude/commands/close.md (close command to update)
- .claude/skills/investigation-cycle/SKILL.md (skill to update)

---
