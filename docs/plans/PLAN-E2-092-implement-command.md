---
template: implementation_plan
status: complete
date: 2025-12-17
backlog_id: E2-092
title: "/implement Command"
author: Hephaestus
lifecycle_phase: plan
session: 85
spawned_by: Session-83
blocked_by: [E2-091]
related: [E2-091, E2-093, ADR-038]
milestone: M3-Cycles
enables: [E2-096]
version: "1.2"
---
# generated: 2025-12-17
# System Auto: last updated on: 2025-12-20 20:01:42
# Implementation Plan: /implement Command

@docs/README.md
@docs/epistemic_state.md
@.claude/skills/implementation-cycle/SKILL.md

---

## Goal

A `/implement <backlog_id>` command exists that invokes the implementation-cycle skill and guides agents through the PLAN-DO-CHECK-DONE workflow for the specified work item.

---

## Current State vs Desired State

### Current State

```markdown
# No /implement command exists
# Agents must manually:
# 1. Invoke Skill(skill="implementation-cycle")
# 2. Parse backlog_id from user input
# 3. Navigate cycle phases manually
```

**Behavior:** Agents must remember to invoke the skill and track cycle state manually.

**Result:** Inconsistent cycle adoption, easy to skip phases.

### Desired State

```markdown
# .claude/commands/implement.md
---
allowed-tools: Read, Glob, Write, Edit, Bash, Skill, Task
description: Implement a backlog item using the PLAN-DO-CHECK-DONE cycle
argument-hint: <backlog_id>
---
# Implement Work Item

Parse $ARGUMENTS for backlog_id, then invoke implementation-cycle skill.
```

**Behavior:** Single command entry point that ensures cycle is followed.

**Result:** Consistent implementation workflow, no skipped phases.

---

## Tests First (TDD)

### Test 1: Command File Exists
```bash
# Verify command file exists
test -f ".claude/commands/implement.md"
# Expected: exit 0
```

### Test 2: Command Appears in Discovery
```bash
# After creating, run UpdateHaiosStatus.ps1 and check
# infrastructure.commands should include "/implement"
```

### Test 3: Command Content Has Required Sections
```markdown
# Verify frontmatter has:
# - allowed-tools
# - description
# - argument-hint
# And body invokes Skill(skill="implementation-cycle")
```

---

## Detailed Design

### Command File Structure

```markdown
---
allowed-tools: Read, Glob, Write, Edit, Bash, Skill, Task, SlashCommand
description: Implement a backlog item using the PLAN-DO-CHECK-DONE cycle
argument-hint: <backlog_id>
---
# Implement Work Item

**Arguments:** $ARGUMENTS

Parse the backlog_id from arguments (e.g., `E2-092`, `INV-012`).

## Workflow

1. **Invoke Skill:** `Skill(skill="implementation-cycle")`
2. **Pass Context:** The skill will guide through PLAN-DO-CHECK-DONE
3. **Track State:** Update plan status as phases complete

## Phase Entry Points

| Phase | Entry Condition |
|-------|-----------------|
| PLAN | Plan exists at `docs/plans/PLAN-{backlog_id}-*.md` |
| DO | Plan status is `approved` and design is complete |
| CHECK | Implementation complete, ready for verification |
| DONE | All tests pass, ready for closure |

## Quick Start

After invoking this command:
1. I will read the plan file for {backlog_id}
2. Determine current phase based on plan status
3. Execute phase-specific actions from the skill
4. Report progress and next steps
```

### Behavior Logic

```
/implement E2-092
    │
    ▼
Parse backlog_id from $ARGUMENTS
    │
    ▼
Invoke Skill(skill="implementation-cycle")
    │
    ▼
Skill guides through PLAN → DO → CHECK → DONE
    │
    ▼
Complete with /close {backlog_id}
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Command vs direct skill | Command | Provides discoverable entry point, can add pre-checks later |
| Skill invocation | Inline in command body | Keeps orchestration in skill, command is thin wrapper |
| Argument format | Single backlog_id | Simple, matches existing patterns (/close, /validate) |

### Input/Output Examples

| Input | Output | Notes |
|-------|--------|-------|
| `/implement E2-092` | Invokes skill, reads plan | Typical case |
| `/implement INV-012` | Works for investigations too | Any backlog ID format |
| `/implement` (no args) | Error: backlog_id required | Edge case |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No backlog_id provided | Prompt user for ID | Manual test |
| Plan file doesn't exist | Skill suggests /new-plan | Test 3 |
| Invalid ID format | Proceed anyway, skill handles | N/A |

---

## Implementation Steps

### Step 1: Create Command File
- [ ] Create `.claude/commands/implement.md`
- [ ] Add YAML frontmatter (allowed-tools, description, argument-hint)
- [ ] Add body content with skill invocation

### Step 2: Verify Discovery
- [ ] PostToolUse hook should auto-refresh status
- [ ] Check haios-status-slim.json includes /implement
- [ ] Verify command appears in vitals

### Step 3: Test Invocation
- [ ] Run `/implement E2-092` (or another ID)
- [ ] Verify skill is invoked
- [ ] Verify plan file is read

---

## Verification

- [ ] Command file exists
- [ ] Command discoverable in vitals
- [ ] Invokes implementation-cycle skill correctly

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Command too thin | Low | Intentional - orchestration in skill |
| Argument parsing | Low | Simple single-arg format |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 85 | 2025-12-18 | - | Plan filled | Design complete |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/commands/implement.md` | File exists with frontmatter | [ ] | |
| `haios-status-slim.json` | /implement in commands | [ ] | Auto-refresh via PostToolUse |
| Vitals output | Shows /implement | [ ] | |

**Verification Commands:**
```bash
# Check command exists
test -f ".claude/commands/implement.md" && echo "EXISTS"

# Check discovery (after creating)
# Look for /implement in infrastructure.commands
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Command appears in vitals? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass (command exists, discoverable)
- [ ] WHY captured (reasoning stored to memory)
- [ ] Documentation current
- [ ] Ground Truth Verification completed above

---

## References

- E2-091: Implementation Cycle Skill
- ADR-038: M2-Governance Symphony Architecture
- INV-012: Static Registration Anti-Pattern (discovery verification)

### Symphony Integration (ADR-038)

| Movement | Integration |
|----------|-------------|
| **RHYTHM** | Command discovered in vitals |
| **LISTENING** | Skill invokes memory-agent for prior learnings |
| **RESONANCE** | E2-097 will log cycle transitions triggered by this command |

---
