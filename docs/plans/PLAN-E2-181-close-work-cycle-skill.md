---
template: implementation_plan
status: complete
date: 2025-12-25
backlog_id: E2-181
title: close-work-cycle skill
author: Hephaestus
lifecycle_phase: plan
session: 117
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-25T15:05:42'
---
# Implementation Plan: close-work-cycle skill

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

After this plan is complete, the close-work-cycle skill will guide agents through structured work item closure with DoD validation, ensuring all exit criteria are met before archival.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `/close.md` (command), `.claude/skills/README.md` |
| Lines of code affected | ~30 | Command chaining addition |
| New files to create | 2 | `.claude/skills/close-work-cycle/SKILL.md`, `README.md` |
| Tests to write | 0 | Skill is markdown/prompt, verification is runtime discovery |
| Dependencies | 1 | `/close` command |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only /close command chains to skill |
| Risk of regression | Low | New skill, no existing behavior to break |
| External dependencies | Low | None |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Create SKILL.md | 20 min | High |
| Update /close | 5 min | High |
| Verify runtime | 5 min | High |
| **Total** | 30 min | |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/commands/close.md - Current behavior
/close <backlog_id>
# Executes multi-step closure procedure directly
# No skill invocation, inline logic in command
```

**Behavior:** `/close` command contains all closure logic inline - 4 steps with DoD validation, archival, and memory storage

**Result:** Works but:
1. No skill-level behavioral contract (Gate Contract pattern from INV-033)
2. No phase-specific guardrails
3. Command does everything rather than skill guiding workflow

### Desired State

```markdown
# .claude/commands/close.md - Target behavior
/close <backlog_id>
# Performs initial lookup, then chains to skill:
Skill(skill="close-work-cycle")
# Skill guides through VALIDATE -> ARCHIVE -> CAPTURE phases
```

**Behavior:** `/close` performs initial work item lookup THEN chains to close-work-cycle skill that provides phase-specific Gate Contracts

**Result:** Structured closure with:
1. Clear phase contracts (Entry + Guardrails + Exit)
2. Consistent behavior through skill definition
3. Follows Command-Skill Chaining pattern (INV-033)

---

## Tests First (TDD)

**SKIPPED:** Skill is markdown prompt injection, not Python code. Verification is runtime discovery.

### Verification Criteria (replaces pytest)

1. **Skill file exists:** `.claude/skills/close-work-cycle/SKILL.md` file present
2. **Frontmatter valid:** Has `name`, `description`, `generated`, `last_updated` fields
3. **Runtime discovery:** Skill appears in `haios-status-slim.json` under `infrastructure.skills`
4. **Command chains:** `/close` contains `Skill(skill="close-work-cycle")` invocation

```bash
# Verification commands
just update-status-slim
python -c "import json; d=json.load(open('.claude/haios-status-slim.json')); print('close-work-cycle' in d['infrastructure']['skills'])"
# Expected: True
```

---

## Detailed Design

### Skill File Structure

**File:** `.claude/skills/close-work-cycle/SKILL.md`

```markdown
---
name: close-work-cycle
description: HAIOS Close Work Cycle for structured work item closure. Use when closing
  work items. Guides VALIDATE->ARCHIVE->CAPTURE workflow with DoD enforcement.
generated: 2025-12-25
last_updated: 2025-12-25
---
# Close Work Cycle

This skill defines the VALIDATE-ARCHIVE-CAPTURE cycle for closing work items with
Definition of Done (DoD) enforcement per ADR-033.

## When to Use

**Invoked automatically** by `/close` command after work item lookup.
**Manual invocation:** `Skill(skill="close-work-cycle")` when closing an existing work item.

---

## The Cycle

```
VALIDATE --> ARCHIVE --> CAPTURE
```

### 1. VALIDATE Phase

**Goal:** Verify work item meets Definition of Done criteria.

**Guardrails (MUST follow):**
1. **Tests MUST pass** - Prompt user to confirm
2. **WHY MUST be captured** - Check for memory_refs in associated docs
3. **Docs MUST be current** - CLAUDE.md, READMEs updated
4. **Traced files MUST be complete** - Associated plans have status: complete

**Actions:**
1. Read work file: `docs/work/active/WORK-{id}-*.md`
2. Grep for associated documents (plans, checkpoints)
3. Check plan statuses - all must be `complete`
4. For INV-* items: Apply investigation-specific DoD
5. Prompt user for DoD confirmation

**Exit Criteria:**
- [ ] Work file exists and has status: active
- [ ] All associated plans have status: complete
- [ ] User confirms: tests pass, WHY captured, docs current

**Tools:** Read, Glob, Grep

---

### 2. ARCHIVE Phase

**Goal:** Update status and move work file to archive.

**Actions:**
1. Update work file frontmatter:
   - Change `status: active` to `status: complete`
   - Change `closed: null` to `closed: {YYYY-MM-DD}`
2. Move work file from `docs/work/active/` to `docs/work/archive/`
3. Update any associated plans to `status: complete`

**Exit Criteria:**
- [ ] Work file status is `complete`
- [ ] Work file closed date is set
- [ ] Work file is in archive directory
- [ ] Associated plans marked complete

**Tools:** Edit, Bash(mv)

---

### 3. CAPTURE Phase

**Goal:** Store closure summary to memory and refresh status.

**Actions:**
1. Store closure summary via `ingester_ingest`:
   - Title, backlog_id, DoD status, associated documents
   - Use source_path: `closure:{backlog_id}`
2. Refresh haios-status.json: `just update-status-slim`
3. Report closure to user with memory concept ID

**Exit Criteria:**
- [ ] Closure summary stored to memory
- [ ] haios-status.json refreshed
- [ ] User informed of successful closure

**Tools:** ingester_ingest, Bash(just update-status-slim)

---

## Composition Map

| Phase | Primary Tool | Memory Integration |
|-------|--------------|-------------------|
| VALIDATE | Read, Glob, Grep | Query for prior work (optional) |
| ARCHIVE | Edit, Bash | - |
| CAPTURE | ingester_ingest | Store closure summary |

---

## Quick Reference

| Phase | Question to Ask | If NO |
|-------|-----------------|-------|
| VALIDATE | Does work file exist? | STOP - not found |
| VALIDATE | Are all plans complete? | STOP or warn user |
| VALIDATE | Does user confirm DoD? | STOP - DoD not met |
| ARCHIVE | Is work file archived? | Complete archival |
| CAPTURE | Is closure stored? | Store via ingester |
```

### Command Change

**File:** `.claude/commands/close.md`
**Addition:** Chain to skill after initial lookup

Current command has Steps 1-4 with inline logic. Add skill chaining after Step 1 (Lookup):

```diff
 ## Step 1: Lookup Work Item

 **ADR-039:** Work files (`docs/work/active/WORK-*.md`) are the source of truth.

 ... (keep existing lookup logic) ...

+---
+
+## Chain to Skill
+
+After work item is found, invoke the close-work-cycle skill:
+
+```
+Skill(skill="close-work-cycle")
+```
+
+The skill guides through VALIDATE -> ARCHIVE -> CAPTURE phases.
+
+**Note:** The remaining steps below document the skill's phases for reference.
+
 ---

 ## Step 1.5: Investigation-Specific DoD (INV-* only)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Three phases | VALIDATE → ARCHIVE → CAPTURE | Mirrors /close steps but with Gate Contracts |
| Keep command lookup | Skill assumes work item found | Command handles "not found" case before skill |
| Skill documents steps | Command + Skill redundancy | Command is the authoritative reference; skill provides structure |
| Capture phase last | After archive | Memory should reflect completed state |

### Edge Cases

| Case | Handling |
|------|----------|
| Work item not found | Handled by /close command BEFORE skill invocation |
| Investigation item (INV-*) | VALIDATE phase includes investigation-specific DoD |
| Plan not complete | VALIDATE phase warns user, offers continue option |
| User declines DoD | STOP - skill exits without archiving |

---

## Implementation Steps

### Step 1: Create skill directory and SKILL.md
- [ ] Create directory: `.claude/skills/close-work-cycle/`
- [ ] Create SKILL.md with content from Detailed Design
- [ ] Verify frontmatter includes required fields (`name`, `description`, `generated`, `last_updated`)

### Step 2: Update /close command
- [ ] Add "Chain to Skill" section to `.claude/commands/close.md`
- [ ] Insert after Step 1 (Lookup Work Item)
- [ ] Include Skill invocation: `Skill(skill="close-work-cycle")`

### Step 3: Verify runtime discovery
- [ ] Run `just update-status-slim`
- [ ] Check skill appears in `haios-status-slim.json`
- [ ] Verify via: `python -c "import json; d=json.load(open('.claude/haios-status-slim.json')); print('close-work-cycle' in d['infrastructure']['skills'])"`

### Step 4: README Sync (MUST)
- [ ] **MUST:** Create `.claude/skills/close-work-cycle/README.md` (skill directory)
- [ ] **MUST:** Update `.claude/skills/README.md` (parent) to list new skill
- [ ] **MUST:** Update `.claude/commands/README.md` to note /close chaining

---

## Verification

- [ ] Skill file exists: `.claude/skills/close-work-cycle/SKILL.md`
- [ ] Runtime discovery: skill in `haios-status-slim.json`
- [ ] Command chains: `/close` includes Skill invocation
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Skill not discovered | Low | Run `just update-status` and verify JSON |
| Command not chaining | Low | Verify by running `/close` test |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 117 | 2025-12-25 | - | In Progress | Plan created |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/close-work-cycle/SKILL.md` | Has frontmatter + 3 phases | [ ] | |
| `.claude/commands/close.md` | Contains Skill invocation | [ ] | |
| `.claude/haios-status-slim.json` | Lists close-work-cycle in skills | [ ] | |
| `.claude/skills/close-work-cycle/README.md` | Exists, describes skill | [ ] | |
| `.claude/skills/README.md` | Lists close-work-cycle | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
just update-status-slim
python -c "import json; d=json.load(open('.claude/haios-status-slim.json')); print('close-work-cycle' in d['infrastructure']['skills'])"
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
- ADR-033: Work Item Lifecycle Governance
- E2-180: work-creation-cycle skill (parallel implementation)

---
