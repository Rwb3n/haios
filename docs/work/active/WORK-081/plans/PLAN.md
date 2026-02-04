---
template: implementation_plan
status: approved
date: 2026-02-04
backlog_id: WORK-081
title: Cycle-as-Subagent Delegation Pattern Implementation
author: Hephaestus
lifecycle_phase: plan
session: 308
version: '1.5'
generated: 2025-12-21
last_updated: '2026-02-04T21:49:50'
---
# Implementation Plan: Cycle-as-Subagent Delegation Pattern Implementation

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

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Main agent can delegate full cycle execution to isolated subagents via Task tool, reducing main track context consumption by 70-90% while preserving governance.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 4 | README.md + 3 cycle skill files (optional wiring) |
| Lines of code affected | ~50 | Skill wiring additions |
| New files to create | 3 | implementation-cycle-agent.md, investigation-cycle-agent.md, close-work-cycle-agent.md |
| Tests to write | 3 | One integration test per agent |
| Dependencies | 0 | Agents are standalone markdown; Task tool built into Claude Code |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Each agent is standalone; invocation via Task tool |
| Risk of regression | Low | Additive pattern, no existing code modified |
| External dependencies | Low | Task tool is built-in Claude Code primitive |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Create 3 agent files | 30 min | High |
| Write integration tests | 20 min | High |
| Update README.md | 10 min | High |
| **Total** | ~1 hr | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/skills/implementation-cycle/SKILL.md - Inline execution
# Main agent executes full cycle inline:
#   PLAN -> DO -> CHECK -> DONE -> CHAIN
# Each phase consumes main agent context
# Full governance (~390 lines skill definition) loaded per invocation
```

**Behavior:** Main agent loads skill content and executes all phases inline. Context accumulates across phases.

**Result:** Main track reaches context limits faster. Coldstart + hooks + inline cycles exhaust context before work completes.

### Desired State

```python
# Main agent delegates to subagent:
Task(
    subagent_type='implementation-cycle-agent',
    prompt='Execute implementation cycle for WORK-081. Plan: docs/work/active/WORK-081/plans/PLAN.md'
)
# Subagent runs in fresh context, returns structured summary
# Main track receives ~20 lines summary instead of ~390 lines inline execution
```

**Behavior:** Main agent delegates full cycle to subagent with fresh context. Subagent executes autonomously and returns structured summary.

**Result:** 70-90% context reduction for main track. Patterns port directly to SDK custom tools (Epoch 4 path).

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Agent File Exists with Valid Frontmatter
```python
def test_implementation_cycle_agent_exists():
    """Verify agent file exists with required frontmatter fields."""
    agent_path = Path(".claude/agents/implementation-cycle-agent.md")
    assert agent_path.exists(), "Agent file must exist"

    content = agent_path.read_text()
    # Check required frontmatter fields
    assert "name: implementation-cycle-agent" in content
    assert "description:" in content
    assert "tools:" in content
    assert "model:" in content
```

### Test 2: Agent Discoverable in Status
```python
def test_agent_discoverable_in_status():
    """Verify agent appears in haios-status-slim.json after update."""
    # Run: just update-status-slim
    status_path = Path(".claude/haios-status-slim.json")
    status = json.loads(status_path.read_text())

    agent_names = [a["name"] for a in status.get("agents", [])]
    assert "implementation-cycle-agent" in agent_names
    assert "investigation-cycle-agent" in agent_names
    assert "close-work-cycle-agent" in agent_names
```

### Test 3: Agent Has Structured Output Format
```python
def test_agent_defines_output_format():
    """Verify agent documents expected return format."""
    agent_path = Path(".claude/agents/implementation-cycle-agent.md")
    content = agent_path.read_text()

    # Agent should define output format for parent consumption
    assert "## Output Format" in content or "## Return Format" in content
    assert "Cycle Result:" in content or "Implementation Result:" in content
```

### Test 4: Task Tool Runtime Discoverability (A1 Critique Response)
```python
def test_task_tool_can_invoke_agent():
    """Verify Task tool can discover and invoke agent at runtime.

    NOTE: This is a manual verification step, not automated pytest.
    Run after agent files created:

    Task(
        subagent_type='implementation-cycle-agent',
        prompt='Echo test: respond with "Agent reachable" and nothing else.'
    )

    Expected: Subagent responds with "Agent reachable"
    If fails: Agent file exists but Task tool cannot discover it
    """
    # Manual verification - document result in Ground Truth Verification
    pass
```

---

## Detailed Design

### Pattern: Agent Markdown File

Each cycle agent follows the established agent pattern (verified from validation-agent.md, test-runner.md):

```yaml
---
name: {cycle}-agent
description: Execute {cycle} autonomously in isolated context. Returns structured summary.
tools: Bash, Read, Glob, Grep, Edit, Write, Skill
model: sonnet  # Full capability for cycle execution
context: fork  # Fresh context, not inheriting parent
generated: 2026-02-04
last_updated: 2026-02-04T00:00:00
---
```

### Agent Structure (3 Files)

**File 1:** `.claude/agents/implementation-cycle-agent.md`
- Executes PLAN → DO → CHECK → DONE → CHAIN phases
- Loads implementation-cycle skill content as reference
- **MUST include embedded governance gates** (see Governance Enforcement below)
- Returns: Implementation Result (PASS/FAIL), tests run, deliverables verified, **gates honored**

**File 2:** `.claude/agents/investigation-cycle-agent.md`
- Executes EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE → CHAIN phases
- Loads investigation-cycle skill content as reference
- **MUST include embedded governance gates**
- Returns: Investigation Result, hypotheses verdicts, spawned work items, **gates honored**

**File 3:** `.claude/agents/close-work-cycle-agent.md`
- Executes VALIDATE → ARCHIVE → MEMORY → CHAIN phases
- Loads close-work-cycle skill content as reference
- **MUST include embedded governance gates**
- Returns: Closure Result, DoD validation, memory refs, **gates honored**

### Governance Enforcement (A5 Critique Response)

**Problem:** Agent markdown files are instructional guidance, not enforcement. Subagent may skip governance gates.

**Solution: Defense-in-Depth**

1. **Embed MUST gates in agent instructions:**
   ```markdown
   ## Governance Gates (MUST)

   Before proceeding past each phase, you MUST:
   - PLAN phase exit: Invoke preflight-checker, report result in output
   - DO phase exit: Invoke design-review-validation, report result in output
   - CHECK phase: Verify ALL WORK.md deliverables, list each in output

   Your output MUST include:
   ## Gates Honored
   - preflight-checker: PASS/FAIL
   - design-review-validation: PASS/FAIL
   - deliverables-verified: X/Y complete
   ```

2. **Parent verifies output contains gate results:**
   - Parse "## Gates Honored" section from subagent output
   - If section missing or any gate FAIL: treat as BLOCKED, do not proceed
   - This is post-hoc verification, not enforcement, but surfaces bypass

3. **Trade-off accepted:**
   - Subagent could lie about gate results (fabricate PASS)
   - Mitigation: Sample auditing in validation-agent reviews
   - Full enforcement requires SDK-level tooling (Epoch 4)

### Call Chain Context

```
Main Agent (Orchestrator)
    |
    +-> coldstart (identity, session, work context)
    |
    +-> survey-cycle (select work)
    |
    +-> Task(subagent_type='implementation-cycle-agent')  # <-- NEW
    |       Prompt: "Execute implementation cycle for {work_id}"
    |       Returns: Structured summary (~20 lines)
    |
    +-> Process summary, route to next work
```

### Output Format (Standardized Across All 3 Agents)

```
Cycle Result: PASS | FAIL | BLOCKED

## Summary
- Work ID: {work_id}
- Phases completed: {list}
- Duration: {estimate}

## Gates Honored (A5 Governance Enforcement)
- preflight-checker: PASS | FAIL | SKIPPED
- design-review-validation: PASS | FAIL | SKIPPED
- deliverables-verified: X/Y complete

## Outcome
{Brief description of what was accomplished}

## Artifacts
- {List of files created/modified}

## Next Action
{Suggested routing or "await_operator"}

## Blockers (if FAIL/BLOCKED)
- {List specific blockers}
```

**Parent Parsing Requirements (A4 Critique Response):**
- Parse output fault-tolerantly - handle missing sections gracefully
- If "## Gates Honored" missing: treat as governance bypass warning, log but allow
- If "Cycle Result:" missing: treat entire output as BLOCKED
- If sections malformed: extract what's available, warn on missing

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Full-cycle delegation | One agent per cycle (not phase-as-subagent) | Memory 83227: Simpler, fewer context switches, patterns port to SDK |
| model: sonnet | Full capability model | Cycles require complex reasoning, file operations, governance |
| context: fork | Fresh context | Isolation is the point - don't inherit parent context bloat |
| Skill reference, not embedding | Agent reads skill file | Skill is source of truth; agent adapts to skill changes |
| Structured output format | Standardized across agents | Parent can parse consistently regardless of cycle type |
| Optional delegation | Skills offer delegation, don't require it | Operator can choose inline execution for debugging |
| **Governance via instruction + verification** | Embed MUST gates in agent + parent verifies output | A5 critique: "voluntary compliance" + post-hoc check provides defense-in-depth |
| **Fault-tolerant output parsing** | Parent handles missing sections gracefully | A4 critique: Subagent may deviate from format; parent must be resilient |

### Input/Output Examples

**Invocation (from main agent):**
```python
Task(
    subagent_type='implementation-cycle-agent',
    prompt='''Execute implementation cycle for WORK-081.
Plan: docs/work/active/WORK-081/plans/PLAN.md
Work: docs/work/active/WORK-081/WORK.md

Execute all phases (PLAN→DO→CHECK→DONE→CHAIN).
Return structured summary when complete.'''
)
```

**Return (to main agent):**
```
Cycle Result: PASS

## Summary
- Work ID: WORK-081
- Phases completed: PLAN, DO, CHECK, DONE, CHAIN
- Duration: ~45 min

## Outcome
Implemented Cycle-as-Subagent delegation pattern. Created 3 agent files,
updated README, all tests passing.

## Artifacts
- .claude/agents/implementation-cycle-agent.md (created)
- .claude/agents/investigation-cycle-agent.md (created)
- .claude/agents/close-work-cycle-agent.md (created)
- .claude/agents/README.md (updated)

## Next Action
Work closed. Queue head: WORK-067 (investigation). Suggest: investigation-cycle

## Blockers
None
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Subagent hits context limit | Return partial summary with BLOCKED status | Manual verification |
| Plan not found | Return FAIL with specific blocker | Test 1 (file exists) |
| Tests fail in CHECK | Return FAIL, list failing tests | Validation in output format |
| No next work in queue | Return "await_operator" in Next Action | Manual verification |

### Open Questions

**Q: Should agents auto-invoke checkpoint-cycle?**

Answer: No. Checkpoint is parent responsibility. Agent returns summary; parent decides when to checkpoint. This keeps agents focused on their cycle.

**Q: How does agent access skill content?**

Answer: Agent reads skill file directly via Read tool. Skill file is source of truth. Agent follows skill structure but executes autonomously.

---

## Open Decisions (MUST resolve before implementation)

**No open decisions.** Work item has no `operator_decisions` field - all design choices resolved in INV-068 investigation.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Create implementation-cycle-agent.md
- [ ] Create `.claude/agents/implementation-cycle-agent.md`
- [ ] Include frontmatter: name, description, tools, model, context
- [ ] Document: Process (read skill, execute phases), Output Format, Examples
- [ ] Test 1 passes (file exists with valid frontmatter)

### Step 2: Create investigation-cycle-agent.md
- [ ] Create `.claude/agents/investigation-cycle-agent.md`
- [ ] Same structure as implementation-cycle-agent
- [ ] Adapt for EXPLORE→HYPOTHESIZE→VALIDATE→CONCLUDE→CHAIN phases
- [ ] Test 1 pattern verified

### Step 3: Create close-work-cycle-agent.md
- [ ] Create `.claude/agents/close-work-cycle-agent.md`
- [ ] Same structure as other agents
- [ ] Adapt for VALIDATE→ARCHIVE→MEMORY→CHAIN phases
- [ ] Test 1 pattern verified

### Step 4: Update README.md
- [ ] Add 3 new agents to Available Agents table
- [ ] Add "Cycle Delegation Agents" category section
- [ ] Document invocation pattern with examples
- [ ] Run `just update-status-slim`
- [ ] Test 2 passes (agents discoverable in status)

### Step 5: Verify Output Format
- [ ] Each agent has ## Output Format section
- [ ] Format matches standardized template
- [ ] Test 3 passes

### Step 6: Integration Verification
- [ ] Run full test suite (no regressions)
- [ ] Manually verify Task invocation works (optional demo)

### Step 7: README Sync (MUST)
- [ ] **MUST:** Verify `.claude/agents/README.md` reflects all agents
- [ ] **MUST:** Verify agent count in README matches actual files

**Note:** This is additive work - no consumer migration needed. New agents don't replace existing functionality.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Subagent can't access skill content | Medium | Agent uses Read tool to load skill file; verified in existing agents |
| Output format drift between agents | Low | Standardized template in design; copy-paste consistency |
| **Governance bypass in subagent (A5)** | Medium | **Defense-in-depth: Embed MUST gates in agent + parent verifies "Gates Honored" section in output** |
| Context limit in subagent | Low | Subagent has fresh context; cycles are bounded work |
| SDK migration path unclear | Low | Pattern designed to port directly per S25; validate when SDK available |
| **Task tool can't discover agent (A1)** | High | **Add manual Task invocation test (Test 4) to verify runtime discoverability** |
| **Output parsing fails silently (A4)** | Medium | **Parent parses fault-tolerantly; missing sections logged as warnings, not failures** |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-081/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Create implementation-cycle-agent | [ ] | File exists at .claude/agents/implementation-cycle-agent.md |
| Create investigation-cycle-agent | [ ] | File exists at .claude/agents/investigation-cycle-agent.md |
| Create close-work-cycle-agent | [ ] | File exists at .claude/agents/close-work-cycle-agent.md |
| Update cycle skills for delegation | [ ] | OUT OF SCOPE per INV-068 (optional wiring, not required) |
| Test: subagent executes cycle | [ ] | Manual verification or integration test |
| Document pattern in README.md | [ ] | README.md updated with new agents |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/agents/implementation-cycle-agent.md` | Exists with valid frontmatter | [ ] | |
| `.claude/agents/investigation-cycle-agent.md` | Exists with valid frontmatter | [ ] | |
| `.claude/agents/close-work-cycle-agent.md` | Exists with valid frontmatter | [ ] | |
| `.claude/agents/README.md` | Lists all 11 agents (8 existing + 3 new) | [ ] | |
| `.claude/haios-status-slim.json` | Contains 3 new agents | [ ] | |

**Verification Commands:**
```bash
# Verify agent files exist
ls .claude/agents/*-cycle-agent.md

# Verify agents in status
just update-status-slim
grep -c "cycle-agent" .claude/haios-status-slim.json
# Expected: 3
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- @docs/work/active/INV-068/WORK.md (spawning investigation - architectural decision)
- @.claude/agents/README.md (existing agent patterns)
- @.claude/agents/validation-agent.md (agent frontmatter pattern)
- @.claude/skills/implementation-cycle/SKILL.md (cycle to delegate)
- @.claude/skills/investigation-cycle/SKILL.md (cycle to delegate)
- @.claude/skills/close-work-cycle/SKILL.md (cycle to delegate)
- @.claude/haios/epochs/E2_3/architecture/S20-pressure-dynamics.md (volumous/tight pattern)
- Memory: 83227 (full-cycle delegation decision), 83214 (Task tool isolation)

---
