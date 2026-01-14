---
template: implementation_plan
status: complete
date: 2025-12-25
backlog_id: E2-180
title: work-creation-cycle skill
author: Hephaestus
lifecycle_phase: plan
session: 116
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-25T10:44:46'
---
# Implementation Plan: work-creation-cycle skill

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

After this plan is complete, the work-creation-cycle skill will guide agents through populating work item fields after scaffolding, ensuring work items have complete Context and Deliverables before being actioned.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `/new-work.md` (command), `README.md` (skills) |
| Lines of code affected | ~30 | Command chaining addition |
| New files to create | 1 | `.claude/skills/work-creation-cycle/SKILL.md` |
| Tests to write | 0 | Skill is markdown/prompt, verification is runtime discovery |
| Dependencies | 1 | `/new-work` command |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only /new-work command chains to skill |
| Risk of regression | Low | New skill, no existing behavior to break |
| External dependencies | Low | None |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Create SKILL.md | 15 min | High |
| Update /new-work | 5 min | High |
| Verify runtime | 5 min | High |
| **Total** | 25 min | |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/commands/new-work.md - Current behavior
just work <backlog_id> "<title>"
# Creates work file and exits
# No skill chaining, no population guidance
```

**Behavior:** `/new-work` scaffolds work file with placeholder fields (`[Problem and root cause]`, `[Deliverable 1]`)

**Result:** Work items created with incomplete Context and Deliverables - requires manual population with no guidance

### Desired State

```markdown
# .claude/commands/new-work.md - Target behavior
just work <backlog_id> "<title>"
# Then chains to skill:
Skill(skill="work-creation-cycle")
# Skill guides through populating essential fields
```

**Behavior:** `/new-work` scaffolds work file THEN chains to work-creation-cycle skill that guides through VERIFY → POPULATE → READY phases

**Result:** Work items created with complete Context and Deliverables through guided workflow

---

## Tests First (TDD)

**SKIPPED:** Skill is markdown prompt injection, not Python code. Verification is runtime discovery.

### Verification Criteria (replaces pytest)

1. **Skill file exists:** `.claude/skills/work-creation-cycle/SKILL.md` file present
2. **Frontmatter valid:** Has `name`, `description`, `generated`, `last_updated` fields
3. **Runtime discovery:** Skill appears in `haios-status-slim.json` under `infrastructure.skills`
4. **Command chains:** `/new-work` contains `Skill(skill="work-creation-cycle")` invocation

```bash
# Verification commands
just update-status-slim
cat .claude/haios-status-slim.json | python -c "import sys,json; d=json.load(sys.stdin); print('work-creation-cycle' in d['infrastructure']['skills'])"
# Expected: True
```

---

## Detailed Design

### Skill File Structure

**File:** `.claude/skills/work-creation-cycle/SKILL.md`

```markdown
---
name: work-creation-cycle
description: HAIOS Work Creation Cycle for structured work item population. Use when creating new work items. Guides VERIFY->POPULATE->READY workflow.
generated: 2025-12-25
last_updated: 2025-12-25
---
# Work Creation Cycle

This skill defines the VERIFY-POPULATE-READY cycle for populating work items after scaffolding.

## When to Use

**Invoked automatically** by `/new-work` command after scaffolding.
**Manual invocation:** `Skill(skill="work-creation-cycle")` when populating an existing work file.

---

## The Cycle

```
VERIFY --> POPULATE --> READY
```

### 1. VERIFY Phase

**Goal:** Confirm work file was created and is valid.

**Actions:**
1. Read the work file: `docs/work/active/WORK-{id}-*.md`
2. Verify file has valid YAML frontmatter
3. Confirm `status: active` and `current_node: backlog`
4. Check for `spawned_by` field if this is spawned work

**Exit Criteria:**
- [ ] Work file exists at expected path
- [ ] Frontmatter valid (template: work_item)
- [ ] Status is `active`

---

### 2. POPULATE Phase

**Goal:** Fill in essential work item fields.

**Guardrails (MUST follow):**
1. **Context section MUST be populated** - Replace `[Problem and root cause]` with actual problem description
2. **Deliverables MUST be actionable** - Replace placeholders with specific checkboxes

**Actions:**
1. Prompt for Context: "What problem does this work item solve?"
2. Fill in Context section with problem statement
3. Prompt for Deliverables: "What are the specific outputs?"
4. Fill in Deliverables as checklist items
5. Optionally set: milestone, priority, spawned_by, blocked_by

**Exit Criteria:**
- [ ] Context section has real content (not placeholder)
- [ ] Deliverables have specific items (not placeholders)
- [ ] Optional: milestone assigned

---

### 3. READY Phase

**Goal:** Validate work item is actionable.

**Actions:**
1. Read work file to verify all fields populated
2. Check Context section contains >20 characters
3. Check Deliverables has at least one checkbox item
4. Update History section with population timestamp

**Exit Criteria:**
- [ ] Context populated with meaningful content
- [ ] Deliverables has actionable checklist
- [ ] Work item ready for further lifecycle progression

---

## Composition Map

| Phase | Primary Tool | Memory Integration |
|-------|--------------|-------------------|
| VERIFY | Read, Glob | - |
| POPULATE | Edit, AskUserQuestion | Query for prior similar work |
| READY | Read, Edit | - |

---

## Quick Reference

| Phase | Question to Ask | If NO |
|-------|-----------------|-------|
| VERIFY | Does work file exist? | Re-run /new-work |
| POPULATE | Is Context filled? | Prompt user for problem statement |
| POPULATE | Are Deliverables defined? | Prompt user for outputs |
| READY | Is work item actionable? | Return to POPULATE |
```

### Command Change

**File:** `.claude/commands/new-work.md`
**Addition:** Chain to skill after scaffolding

```diff
 Run scaffolding via just recipe:

 ```bash
 just work <backlog_id> "<title>"
 ```

+---
+
+## After Scaffolding
+
+**Chain to skill to populate essential fields:**
+
+```
+Skill(skill="work-creation-cycle")
+```
+
+This guides through VERIFY → POPULATE → READY phases to ensure work item has complete Context and Deliverables.
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Three phases not two | VERIFY → POPULATE → READY | VERIFY catches scaffolding failures; READY validates completeness |
| Lightweight phases | Minimal exit criteria | Work items can be quick-created or fully elaborated based on context |
| Optional milestone | Not required in POPULATE | Milestone can be assigned later during prioritization |
| Chaining via command | /new-work chains to skill | Follows INV-033 pattern: commands scaffold, skills guide |

### Edge Cases

| Case | Handling |
|------|----------|
| Spawned work item | VERIFY checks spawned_by field is set |
| Quick creation | POPULATE can accept minimal input (operator discretion) |
| Existing work file | Skill can be invoked directly on existing files |

---

## Implementation Steps

### Step 1: Create skill directory and SKILL.md
- [ ] Create directory: `.claude/skills/work-creation-cycle/`
- [ ] Create SKILL.md with content from Detailed Design
- [ ] Verify frontmatter includes required fields

### Step 2: Update /new-work command
- [ ] Add "After Scaffolding" section to `.claude/commands/new-work.md`
- [ ] Include Skill invocation: `Skill(skill="work-creation-cycle")`

### Step 3: Verify runtime discovery
- [ ] Run `just update-status`
- [ ] Check skill appears in `haios-status-slim.json`
- [ ] Verify via: `python -c "import sys,json; d=json.load(open('.claude/haios-status-slim.json')); print('work-creation-cycle' in d['infrastructure']['skills'])"`

### Step 4: README Sync (MUST)
- [ ] **MUST:** Create `.claude/skills/work-creation-cycle/README.md` (skill directory)
- [ ] **MUST:** Update `.claude/skills/README.md` (parent) to list new skill
- [ ] **MUST:** Update `.claude/commands/README.md` to note /new-work chaining

---

## Verification

- [ ] Skill file exists: `.claude/skills/work-creation-cycle/SKILL.md`
- [ ] Runtime discovery: skill in `haios-status-slim.json`
- [ ] Command chains: `/new-work` includes Skill invocation
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Skill not discovered | Low | Run `just update-status` and verify JSON |
| Command not chaining | Low | Verify by running `/new-work` test |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 117 | 2025-12-25 | - | In Progress | Plan created, starting implementation |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/work-creation-cycle/SKILL.md` | Has frontmatter + 3 phases | [ ] | |
| `.claude/commands/new-work.md` | Contains Skill invocation | [ ] | |
| `.claude/haios-status-slim.json` | Lists work-creation-cycle in skills | [ ] | |
| `.claude/skills/work-creation-cycle/README.md` | Exists, describes skill | [ ] | |
| `.claude/skills/README.md` | Lists work-creation-cycle | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
just update-status-slim
python -c "import sys,json; d=json.load(open('.claude/haios-status-slim.json')); print('work-creation-cycle' in d['infrastructure']['skills'])"
# Expected: True
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [ ] | |
| Runtime discovery verified? | [ ] | |
| Any deviations from plan? | [ ] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Skill file exists and has valid content
- [ ] Runtime discovery works
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated
- [ ] Ground Truth Verification completed above

---

## References

- INV-033: Skill as Node Entry Gate Formalization
- INV-035: Skill Architecture Refactoring
- ADR-039: Work Item as File Architecture

---
