---
template: implementation_plan
status: complete
date: 2025-12-25
backlog_id: E2-165
title: Checkpoint Skill with Git Commit
author: Hephaestus
lifecycle_phase: plan
session: 119
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-25T21:26:46'
---
# Implementation Plan: Checkpoint Skill with Git Commit

@docs/README.md
@docs/epistemic_state.md

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: New feature, no existing code to show current state"
     - "SKIPPED: Pure documentation task, no code changes"
     - "SKIPPED: Trivial fix, single line change doesn't warrant detailed design"

     This prevents silent section deletion and ensures conscious decisions.
-->

---

## Goal

Create a checkpoint-cycle skill that guides checkpoint creation through SCAFFOLD→FILL→CAPTURE→COMMIT phases, ensuring git commits happen as part of the workflow (not manual afterthought).

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | checkpoint template, skills README |
| Lines of code affected | ~30 | Template @ refs removal |
| New files to create | 2 | SKILL.md, README.md in checkpoint skill dir |
| Tests to write | 0 | Pure markdown skill, no pytest |
| Dependencies | 0 | Standalone skill |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Uses existing just recipes |
| Risk of regression | Low | New skill, doesn't modify existing code |
| External dependencies | Low | Only justfile recipes (already exist) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Create skill files | 15 min | High |
| Update template (@ refs) | 5 min | High |
| Update skills README | 5 min | High |
| **Total** | 25 min | High |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/commands/new-checkpoint.md (command)
- Static text expansion
- Lists 5 manual steps
- No enforcement of git commit
- @ references in template (ceremonial per INV-E2-116)
```

**Behavior:** User runs `/new-checkpoint`, gets scaffolded file, then must manually follow 5 steps including git commit.

**Result:** Git commits often forgotten. No structured workflow. Template has useless @ references.

### Desired State

```markdown
# .claude/skills/checkpoint-cycle/SKILL.md (skill)
- Four phases: SCAFFOLD → FILL → CAPTURE → COMMIT
- Each phase has exit criteria
- COMMIT phase calls `just commit-session {N}`
- Template cleaned of @ references
```

**Behavior:** User invokes skill, guided through each phase, git commit guaranteed as final step.

**Result:** Consistent checkpoint workflow with automatic git integration.

---

## Tests First (TDD)

**SKIPPED:** Pure markdown skill - no pytest code. Verification via:
1. Skill file exists and is discoverable (`just update-status`)
2. Template has no @ references
3. Manual: invoke skill and verify phases work

---

## Detailed Design

### Skill Structure

**Directory:** `.claude/skills/checkpoint-cycle/`

**Files:**
- `SKILL.md` - Main skill definition with phases
- `README.md` - One-liner description for discovery

### Skill Frontmatter

```yaml
---
name: checkpoint-cycle
description: HAIOS Checkpoint Cycle for structured session capture. Use when
  creating or completing a checkpoint. Guides SCAFFOLD->FILL->CAPTURE->COMMIT workflow.
generated: 2025-12-25
---
```

### The Four Phases

```
SCAFFOLD --> FILL --> CAPTURE --> COMMIT
```

**1. SCAFFOLD Phase**
- Goal: Create checkpoint file via just recipe
- Action: `just scaffold checkpoint {session} "{title}"`
- Exit: File exists at expected path

**2. FILL Phase**
- Goal: Populate checkpoint content
- Actions:
  - Fill Summary section
  - Fill Completed Work with checkboxes
  - Fill Files Modified
  - Fill Key Findings
  - Optionally add Spawned Work Items section (E2-035)
- Exit: All sections have content (not placeholders)

**3. CAPTURE Phase**
- Goal: Store learnings to memory
- Actions:
  - Call `ingester_ingest` for each key decision/learning
  - Update `memory_refs` in frontmatter
  - Update WHY Captured table
- Exit: memory_refs populated

**4. COMMIT Phase**
- Goal: Git commit the checkpoint
- Action: `just commit-session {session} "{title}"`
- Exit: Git commit created

### Template Changes

**File:** `.claude/templates/checkpoint.md`

**Remove @ references (lines 24-26):**
```diff
-@docs/README.md
-@docs/epistemic_state.md
-@docs/checkpoints/*SESSION-{{PREV_SESSION}}*.md
+<!-- Context files loaded via coldstart, not @ references (INV-E2-116) -->
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| 4 phases not 3 | SCAFFOLD-FILL-CAPTURE-COMMIT | CAPTURE (memory) and COMMIT (git) are distinct steps |
| Keep command | Command scaffolds, skill guides | Commands can't enforce workflow, skills can |
| Remove @ refs | Replace with comment | INV-E2-116 confirmed @ refs are ceremonial in saved files |
| Add Spawned Work Items | Optional section in FILL | E2-035 intent - prompt for discovered issues |

### Edge Cases

| Case | Handling |
|------|----------|
| No learnings to capture | CAPTURE phase skips ingester, notes "N/A" |
| Git fails | Report error, suggest manual commit |
| File already exists | Overwrite warning (just scaffold handles) |

---

## Implementation Steps

### Step 1: Create skill directory
- [ ] Create `.claude/skills/checkpoint-cycle/` directory
- [ ] Create `README.md` with one-liner description

### Step 2: Create SKILL.md
- [ ] Write SKILL.md with 4 phases: SCAFFOLD, FILL, CAPTURE, COMMIT
- [ ] Include exit criteria for each phase
- [ ] Reference `just commit-session` in COMMIT phase

### Step 3: Update checkpoint template
- [ ] Remove @ references from `.claude/templates/checkpoint.md`
- [ ] Add comment explaining why (INV-E2-116)

### Step 4: Update skills README
- [ ] Add checkpoint-cycle to `.claude/skills/README.md`

### Step 5: Verify discovery
- [ ] Run `just update-status`
- [ ] Verify `checkpoint-cycle` appears in haios-status-slim.json skills list

### Step 6: README Sync (MUST)
- [ ] **MUST:** Update `.claude/skills/README.md` with new skill
- [ ] **MUST:** Verify README content matches actual file state

---

## Verification

- [ ] Skill discoverable in haios-status-slim.json
- [ ] Template has no @ references
- [ ] **MUST:** skills README updated

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Command still exists | Low | Keep command for backward compat, skill is preferred |
| Git commit fails | Medium | COMMIT phase reports error, suggests manual fix |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 120 | 2025-12-25 | - | In Progress | Plan created |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/checkpoint-cycle/SKILL.md` | 4 phases defined | [ ] | |
| `.claude/skills/checkpoint-cycle/README.md` | One-liner exists | [ ] | |
| `.claude/templates/checkpoint.md` | No @ references | [ ] | |
| `.claude/skills/README.md` | Lists checkpoint-cycle | [ ] | |
| `.claude/haios-status-slim.json` | checkpoint-cycle in skills | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Skill appears in status? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Skill discoverable
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated
- [ ] Ground Truth Verification completed above

---

## References

- INV-036: Coldstart-Checkpoint-Heartbeat Context Value Audit
- INV-E2-116: @ Reference Necessity in Checkpoints
- E2-132: Remove @ References (merged)
- E2-035: Checkpoint Lifecycle Enhancement (merged)

---
