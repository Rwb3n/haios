---
template: implementation_plan
status: complete
date: 2025-12-17
backlog_id: E2-091
title: "Implementation Cycle Skill"
author: Hephaestus
lifecycle_phase: plan
session: 84
# DAG edge fields (E2-076b)
spawned_by: Session-83
# blocked_by: []  # Root item - no blockers
related: [E2-092, E2-093, E2-094, E2-095, E2-096, E2-097]
milestone: M3-Cycles
# parent_plan:
children: [E2-092, E2-093, E2-096]
# absorbs: []
enables: [E2-092, E2-093, E2-096]
# execution_layer:
version: "1.2"
---
# generated: 2025-12-17
# System Auto: last updated on: 2025-12-18 21:46:44
# Implementation Plan: Implementation Cycle Skill

@docs/README.md
@docs/epistemic_state.md
@docs/ADR/ADR-038-m2-governance-symphony-architecture.md

---

## Goal

A skill file exists at `.claude/skills/implementation-cycle/SKILL.md` that defines the PLAN-DO-CHECK-DONE cycle as a composition pattern, providing agents with structured guidance for implementing work items.

---

## Current State vs Desired State

### Current State

```
.claude/skills/
  extract-content/SKILL.md   # Entity extraction skill
  memory-agent/SKILL.md      # ReasoningBank pattern skill
  schema-ref/SKILL.md        # Schema reference skill
  # NO implementation-cycle skill exists
```

**Behavior:** Agents implement work items ad-hoc. No structured cycle guides the PLAN->DO->CHECK->DONE workflow. Agents may skip preflight checks, forget to run tests, or miss WHY capture.

**Result:** Inconsistent implementation quality. DoD (ADR-033) requirements rely on cultural memory rather than skill guidance.

### Desired State

```
.claude/skills/
  extract-content/SKILL.md
  memory-agent/SKILL.md
  schema-ref/SKILL.md
  implementation-cycle/SKILL.md   # NEW - defines the cycle
```

**Behavior:** Agents invoke `Skill(skill="implementation-cycle")` when starting implementation. The skill provides:
1. 4-state cycle definition (PLAN -> DO -> CHECK -> DONE)
2. Phase-specific instructions with tool references
3. Composition guidance (which subagents/commands to use)
4. DoD checklist integration

**Result:** Structured implementation workflow. Agents have clear guidance for each phase. Subagents (E2-093, E2-094, E2-095) and commands (E2-092) have a coherent framework to plug into.

---

## Tests First (TDD)

> **Note:** This is a Skill file (markdown), not Python code. Verification is structural/behavioral.

### Test 1: Skill File Structure Valid
```bash
# Verify YAML frontmatter is valid
powershell.exe -Command "Get-Content '.claude/skills/implementation-cycle/SKILL.md' -Raw | Select-String -Pattern '^---' -AllMatches"
# Expected: 2 matches (opening and closing frontmatter delimiters)

# Verify required frontmatter fields
powershell.exe -Command "Get-Content '.claude/skills/implementation-cycle/SKILL.md' -Head 10"
# Expected: name: implementation-cycle, description: present
```

### Test 2: Skill Appears in Available Skills
```bash
# After creating the skill, verify it appears in Claude Code
# The Skill tool's available_skills list should include implementation-cycle
```

### Test 3: Skill Content Complete
```bash
# Verify all 4 cycle phases are documented
powershell.exe -Command "Get-Content '.claude/skills/implementation-cycle/SKILL.md' -Raw | Select-String -Pattern '## (PLAN|DO|CHECK|DONE)' -AllMatches"
# Expected: 4 matches (one per phase)
```

### Test 4: Backward Compatibility
```bash
# Existing skills remain functional
# memory-agent, extract-content, schema-ref still appear in available skills
```

---

## Detailed Design

### Skill File Structure

```yaml
# .claude/skills/implementation-cycle/SKILL.md
---
name: implementation-cycle
description: HAIOS Implementation Cycle for structured work item implementation. Use when starting implementation of a plan. Guides PLAN->DO->CHECK->DONE workflow with phase-specific tooling.
---
# [Markdown content follows - see Content Structure below]
```

### Cycle State Machine

```
                    +--------+
                    |  PLAN  |  <- Entry point
                    +----+---+
                         |
        Plan file exists & approved?
                         |
              YES ───────┼─────── NO → Create/update plan
                         v
                    +--------+
                    |   DO   |  <- Implementation
                    +----+---+
                         |
        Implementation complete?
                         |
              YES ───────┼─────── NO → Continue coding
                         v
                    +--------+
                    |  CHECK |  <- Verification
                    +----+---+
                         |
        Tests pass + DoD met?
                         |
              YES ───────┼─────── NO → Fix issues, return to DO
                         v
                    +--------+
                    |  DONE  |  <- Closure
                    +--------+
```

### Content Structure (SKILL.md Body)

```markdown
# Implementation Cycle

## When to Use
**SHOULD** invoke this skill when:
- Starting implementation of a backlog item
- Resuming work on an in-progress item
- Unsure of next step in implementation workflow

## The Cycle

### 1. PLAN Phase
**Goal:** Verify plan exists and is ready for implementation.

**Actions:**
1. Read the plan file: `docs/plans/PLAN-{backlog_id}-*.md`
2. Verify plan has filled-in sections (not template placeholders)
3. Check `status: draft` -> if so, fill in design first
4. Optional: Run preflight checker (E2-093 when available)

**Exit Criteria:**
- [ ] Plan file exists with complete design
- [ ] Tests defined in "Tests First" section
- [ ] Current/Desired state documented

**Tools:** Read, Glob, Task(preflight-checker) [future]

### 2. DO Phase
**Goal:** Implement the design from the plan.

**Guardrails (SHOULD follow):**
1. **List affected files BEFORE writing** - Create manifest of files to modify
2. **One logical change at a time** - Atomic commits, easier rollback
3. **If >3 files, pause for confirmation** - Large scope = higher risk

**File Manifest Format:**
```markdown
## Files to Modify
- [ ] path/to/file1.py - Add function X
- [ ] path/to/file2.py - Update import
- [ ] tests/test_file.py - Add test for X
```
> If manifest has >3 files, SHOULD confirm scope with operator before proceeding.
> Preflight Checker (E2-093) will enforce this when available.

**Actions:**
1. Create file manifest (list all files to modify)
2. Write failing tests first (from plan's Tests section)
3. Implement ONE change at a time (RED → GREEN → REFACTOR)
4. Follow plan's Implementation Steps
5. Use memory-agent skill for prior learnings

**Exit Criteria:**
- [ ] File manifest complete and followed
- [ ] All planned code changes made
- [ ] Implementation matches Detailed Design
- [ ] Each change tested before next

**Tools:** Write, Edit, Bash(pytest), Skill(memory-agent), Task(preflight-checker) [future]

### 3. CHECK Phase
**Goal:** Verify implementation meets quality bar.

**Actions:**
1. Run test suite: `pytest tests/ -v`
2. Verify all tests pass (no regressions)
3. Run plan's Ground Truth Verification
4. Check DoD criteria (ADR-033)

**For non-code tasks** (docs, ADRs, configs):
- Skip pytest if no code changes
- Focus on Ground Truth Verification (files exist, content correct)
- Use `/validate` command for template compliance
- Manual review replaces automated tests

**Exit Criteria:**
- [ ] All tests pass (or N/A for non-code)
- [ ] Ground Truth Verification complete
- [ ] No regressions in full test suite (or N/A)

**Tools:** Bash(pytest), Read, Task(test-runner) [future], /validate

### 4. DONE Phase
**Goal:** Close the work item properly.

**Actions:**
1. Capture WHY: Store learnings to memory
2. Update plan status: `status: complete`
3. Close work item: `/close {backlog_id}`
4. Update documentation if behavior changed

**Exit Criteria:**
- [ ] WHY captured (memory_refs in checkpoint)
- [ ] Plan marked complete
- [ ] Work item closed via /close
- [ ] Docs updated (CLAUDE.md, READMEs)

**Tools:** ingester_ingest, Edit, SlashCommand(/close), Write

## Composition Map

| Phase | Primary Tool | Optional Subagent | Command |
|-------|--------------|-------------------|---------|
| PLAN  | Read, Glob   | preflight-checker | /new-plan |
| DO    | Write, Edit  | -                 | - |
| CHECK | Bash(pytest) | test-runner       | /validate |
| DONE  | Edit, Write  | why-capturer      | /close |

## Quick Reference

| Phase | Question to Ask | If NO |
|-------|-----------------|-------|
| PLAN  | Is the plan ready? | Fill in design |
| DO    | Is file manifest created? | List files first |
| DO    | Is implementation done? | One change at a time |
| CHECK | Is verification complete? | Fix issues, retest |
| DONE  | Is WHY captured? | Store learnings |

**DO phase guardrails:**
- List files BEFORE writing (manifest)
- One logical change at a time
- >3 files? Pause and confirm scope

**CHECK varies by task type:**
- Code: `pytest tests/ -v` + Ground Truth
- Docs/ADRs: `/validate` + Ground Truth
- Config: Manual review + Ground Truth

## Example Workflow: TDD Implementation

> Concrete example showing full cycle with test-first methodology

### Scenario: Implementing E2-094 (Test Runner Subagent)

**PLAN Phase:**
```
1. Read docs/plans/PLAN-E2-094-test-runner-subagent.md
2. Verify plan has:
   - Goal: "A subagent that runs pytest in isolation"
   - Tests First: Test cases defined
   - Detailed Design: Subagent structure documented
3. Exit: Plan is ready for implementation
```

**DO Phase (TDD with Guardrails):**
```
Step 0: Create File Manifest FIRST
----------------------------------------
## Files to Modify
- [ ] tests/test_subagents.py - Add test cases
- [ ] .claude/agents/test-runner.md - Create subagent (NEW)

File count: 2 (under threshold, proceed without confirmation)

Step 1: Write failing test FIRST
----------------------------------------
# tests/test_subagents.py
def test_test_runner_subagent_exists():
    """Verify subagent file exists with valid frontmatter."""
    path = Path(".claude/agents/test-runner.md")
    assert path.exists(), "Subagent file missing"
    content = path.read_text()
    assert "name: test-runner" in content

def test_test_runner_has_pytest_tool():
    """Verify subagent has access to Bash for pytest."""
    content = Path(".claude/agents/test-runner.md").read_text()
    assert "Bash" in content or "pytest" in content

# Run tests - they FAIL (RED)
$ pytest tests/test_subagents.py -v
FAILED test_test_runner_subagent_exists - FileNotFoundError
FAILED test_test_runner_has_pytest_tool - FileNotFoundError

Step 2: Implement ONE change to make tests pass
----------------------------------------
# Create .claude/agents/test-runner.md
---
name: test-runner
description: Run pytest in isolated context. Returns pass/fail summary.
tools: Bash, Read
---
# Test Runner Subagent
...

# Run tests - they PASS (GREEN)
$ pytest tests/test_subagents.py -v
PASSED test_test_runner_subagent_exists
PASSED test_test_runner_has_pytest_tool

Step 3: Update manifest
----------------------------------------
## Files to Modify
- [x] tests/test_subagents.py - Add test cases
- [x] .claude/agents/test-runner.md - Create subagent (NEW)

All files in manifest complete. Exit DO phase.
```

**CHECK Phase:**
```
1. Run full test suite:
   $ pytest tests/ -v
   207 passed, 0 failed

2. Ground Truth Verification:
   - [ ] .claude/agents/test-runner.md exists: YES
   - [ ] Frontmatter valid: YES
   - [ ] Tools field includes Bash: YES

3. DoD criteria (ADR-033):
   - [ ] Tests pass: YES (207 passed)
   - [ ] No regressions: YES
```

**DONE Phase:**
```
1. Capture WHY:
   ingester_ingest(
     content="Test Runner subagent design: Isolated pytest execution...",
     source_path="session:2025-12-18:E2-094",
     content_type_hint="techne"
   )

2. Update plan status:
   Edit plan frontmatter: status: complete

3. Close work item:
   /close E2-094

4. Update docs:
   Add test-runner to REFS/GOVERNANCE.md agents table
```

### TDD Cycle Within DO Phase

```
        +------------------+
        |  Write Test      |  <- Start here
        |  (it will fail)  |
        +--------+---------+
                 |
                 v
        +--------+---------+
        |  Run Test        |
        |  See it FAIL     |  <- RED
        +--------+---------+
                 |
                 v
        +--------+---------+
        |  Write Code      |
        |  Minimal to pass |
        +--------+---------+
                 |
                 v
        +--------+---------+
        |  Run Test        |
        |  See it PASS     |  <- GREEN
        +--------+---------+
                 |
                 v
        +--------+---------+
        |  Refactor        |  <- REFACTOR
        |  (if needed)     |
        +--------+---------+
                 |
                 v
           More tests?
           YES → Loop back
           NO  → Exit DO phase
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Skill vs Command | Skill | Skills inject guidance into context; commands invoke actions. Cycle is guidance. |
| 4 phases | PLAN-DO-CHECK-DONE | Minimal viable cycle. Maps to Deming/PDCA. Avoids over-engineering (concept 71925). |
| Composition pattern | Reference subagents, don't embed | Subagents implemented separately (E2-093/94/95). Skill stays focused on workflow. |
| L1-L2 enforcement | Prompted guidance | Start observable/prompted, not gated. Can tighten later based on usage. |
| Exit criteria format | Checkboxes | Agents can track progress within phase. Visual clarity. |
| Skill-Command separation | E2-091 defines pattern, E2-092 invokes it | `/implement` command (E2-092) will invoke this skill. Separation allows skill to be used independently or via command. |
| DO phase guardrails | L2 guidance + L3 future gate | File manifest + atomic changes reduce risk. >3 file gate prevents runaway changes. L2 in skill, L3 via E2-093 preflight. |

### Input/Output Examples

| Invocation | Context | Skill Guidance |
|------------|---------|----------------|
| `Skill(skill="implementation-cycle")` | Starting E2-092 | "You're in PLAN phase. Read docs/plans/PLAN-E2-092-*.md first." |
| `Skill(skill="implementation-cycle")` | Tests written, coding | "You're in DO phase. Follow Implementation Steps from plan." |
| `Skill(skill="implementation-cycle")` | Code done, need verify | "You're in CHECK phase. Run pytest, verify Ground Truth." |

### Edge Cases

| Case | Handling | Notes |
|------|----------|-------|
| No plan file exists | Direct to `/new-plan` command | PLAN phase catches this |
| Tests fail in CHECK | Return to DO phase | Explicit in state machine |
| WHY already captured | Skip to close | DONE phase is idempotent |
| Multi-session work | Skill re-entry resumes | Checkpoints preserve state |

---

## Implementation Steps

### Step 1: Create Directory Structure
- [ ] Create `.claude/skills/implementation-cycle/` directory
- [ ] Verify directory exists alongside other skills

### Step 2: Create SKILL.md with Frontmatter
- [ ] Create `.claude/skills/implementation-cycle/SKILL.md`
- [ ] Add YAML frontmatter (name, description)
- [ ] Test 1 passes (frontmatter valid)

### Step 3: Write Skill Content - When to Use
- [ ] Add "When to Use" section with SHOULD triggers
- [ ] Reference RFC 2119 requirement levels

### Step 4: Write Skill Content - 4 Phases
- [ ] Add PLAN phase with exit criteria
- [ ] Add DO phase with exit criteria
- [ ] Add CHECK phase with exit criteria
- [ ] Add DONE phase with exit criteria
- [ ] Test 3 passes (4 phases documented)

### Step 5: Write Skill Content - Composition Map
- [ ] Add Composition Map table
- [ ] Add Quick Reference table
- [ ] Reference future subagents with [future] annotation

### Step 6: Verify Skill Appears
- [ ] Start new Claude Code session
- [ ] Verify `implementation-cycle` appears in Skill tool's available_skills
- [ ] Test 2 passes (skill discoverable)

### Step 7: Integration Verification
- [ ] Test 4 passes (other skills still work)
- [ ] Document in CLAUDE.md or REFS/GOVERNANCE.md

---

## Verification

- [ ] Skill file exists at `.claude/skills/implementation-cycle/SKILL.md`
- [ ] Skill appears in Claude Code's available skills list
- [ ] All 4 phases documented with exit criteria
- [ ] Composition Map references future subagents correctly
- [ ] Documentation updated (REFS/GOVERNANCE.md)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Over-engineering the cycle | Medium | Keep to 4 phases, resist adding more. Memory concept 71925 warns of this. |
| Skill too verbose | Low | Progressive disclosure - Quick Reference for most cases, full docs for deep dives |
| Subagent references confusing | Low | Mark with [future] annotation, explain in Composition Map |
| Agents ignore the skill | Medium | Start with L1-L2 (prompted), measure adoption, tighten if needed |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 84 | 2025-12-18 | Pending | Complete | Designed + Implemented in single session |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/implementation-cycle/SKILL.md` | Exists with valid frontmatter + 4 phases | [x] | Created Session 84 |
| `.claude/REFS/GOVERNANCE.md` | Documents implementation-cycle skill | [x] | Added to Skills section |

**Verification Commands:**
```bash
# Verify skill file exists and has correct structure
powershell.exe -Command "Test-Path '.claude/skills/implementation-cycle/SKILL.md'"
# Result: True

# Verify 4 phases present
powershell.exe -Command "(Get-Content '.claude/skills/implementation-cycle/SKILL.md' -Raw | Select-String -Pattern '## [1-4]\. (PLAN|DO|CHECK|DONE)' -AllMatches).Matches.Count"
# Result: 4
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | Both files verified |
| Skill appears in Claude Code available_skills? | Pending | Requires new session to verify discovery |
| Any deviations from plan? | No | Implemented as designed |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Skill file exists and is valid
- [x] WHY captured (reasoning stored to memory)
- [x] Documentation current (REFS/GOVERNANCE.md)
- [ ] Skill discoverable in Claude Code (requires session restart)
- [x] Ground Truth Verification completed above

---

## References

- **ADR-033:** Work Item Lifecycle (DoD criteria)
- **ADR-038:** M2-Governance Symphony Architecture (composition pattern)
- **Memory 71918:** "Cycles are not new infrastructure - composition patterns"
- **Memory 71925:** "Over-engineering risk exceeds under-specifying risk"
- **Session 83:** M3-Cycles architecture design discussion

---
