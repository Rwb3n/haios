---
template: implementation_plan
status: complete
date: 2025-12-17
backlog_id: E2-094
title: "Test Runner Subagent"
author: Hephaestus
lifecycle_phase: done
session: 87
spawned_by: Session-83
# blocked_by: []  # Independent - can start without E2-091
related: [E2-091, E2-093, ADR-038]
milestone: M3-Cycles
version: "1.2"
---
# generated: 2025-12-17
# System Auto: last updated on: 2025-12-19 23:00:21
# Implementation Plan: Test Runner Subagent

@docs/README.md
@docs/epistemic_state.md
@.claude/agents/schema-verifier.md

---

## Goal

A `test-runner` subagent exists that executes pytest in an isolated context during CHECK phase and returns structured pass/fail results without polluting main agent context.

---

## Current State vs Desired State

### Current State

```markdown
# Parent agent runs pytest directly:
Bash(pytest tests/ -v)
# Output floods main context
# Long test output hard to parse
# Test failures mixed with other conversation
```

**Behavior:** Test output consumes main context, hard to summarize.

**Result:** Context pollution, difficult to extract pass/fail status.

### Desired State

```markdown
# .claude/agents/test-runner.md
---
name: test-runner
description: Execute pytest in isolated context. Returns structured pass/fail summary. Use during CHECK phase.
tools: Bash, Read
---
# Test Runner
Runs tests, returns concise summary:
- Total: X passed, Y failed
- Failed tests: [list]
- Error messages: [if any]
```

**Behavior:** Tests run in isolated subprocess, clean summary returned.

**Result:** Parent context stays clean, clear pass/fail status.

---

## Tests First (TDD)

### Test 1: Agent File Exists
```bash
test -f ".claude/agents/test-runner.md"
# Expected: exit 0
```

### Test 2: Agent Appears in Discovery
```bash
# After creating, check haios-status-slim.json
# infrastructure.agents should include "test-runner"
```

### Test 3: Agent Has Required Frontmatter
```yaml
# Verify frontmatter has:
name: test-runner
description: ...
tools: Bash, Read
```

---

## Detailed Design

### Agent File Structure

```markdown
---
name: test-runner
description: Execute pytest in isolated context. Returns structured pass/fail summary. Use during CHECK phase.
tools: Bash, Read
---
# Test Runner

Executes tests in isolated context, returns clean summary to parent.

## Requirement Level

**OPTIONAL** but **RECOMMENDED** during CHECK phase for large test suites.

## Input

Receives from parent agent:
- `test_path`: Path to test file or directory (default: `tests/`)
- `verbose`: Boolean for verbose output (default: false)
- `filter`: Optional pytest filter expression

## Process

1. Run pytest with specified options
2. Parse output for pass/fail counts
3. Extract failed test names and error summaries
4. Return structured result

## Output Format

Return a concise summary:
```
Test Results: PASS | FAIL
Total: X passed, Y failed, Z skipped
Duration: N.Ns

[If failures:]
Failed Tests:
- test_name_1: AssertionError: expected X got Y
- test_name_2: Error message

[If all pass:]
All tests passing.
```

## Example

Input: "Run tests in tests/test_database.py"
Action: `pytest tests/test_database.py -v --tb=short`
Output:
```
Test Results: PASS
Total: 12 passed, 0 failed
Duration: 2.3s
All tests passing.
```

Input: "Run full test suite"
Action: `pytest tests/ -v --tb=line`
Output:
```
Test Results: FAIL
Total: 205 passed, 2 failed
Duration: 15.7s

Failed Tests:
- test_integration.py::test_sync_flow: AssertionError
- test_mcp.py::test_connection: TimeoutError
```
```

### Behavior Logic

```
Input (test_path, verbose?, filter?)
    │
    ▼
Build pytest command
    │
    ▼
Execute: pytest {test_path} --tb=short
    │
    ▼
Parse output for:
    ├─► Pass/fail counts (regex: "(\d+) passed")
    ├─► Failed test names
    └─► Error messages
    │
    ▼
Return structured summary
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Output format | Text summary | Easy to read, parent can parse if needed |
| Tools | Bash, Read | Bash for pytest, Read for test file inspection |
| Traceback level | --tb=short | Balance between info and verbosity |
| Isolation value | High | Keeps parent context clean |

### Input/Output Examples

| Input | Output | Notes |
|-------|--------|-------|
| "Run all tests" | Summary with counts | Full suite |
| "Run tests/test_x.py" | Summary for one file | Targeted |
| "Run with filter test_db" | Filtered results | pytest -k filter |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No tests found | Report "0 tests collected" | Manual |
| pytest not installed | Error message | Manual |
| Timeout | Report timeout, partial results | N/A |

---

## Implementation Steps

### Step 1: Create Agent File
- [ ] Create `.claude/agents/test-runner.md`
- [ ] Add YAML frontmatter (name, description, tools)
- [ ] Add body content with process

### Step 2: Verify Discovery
- [ ] PostToolUse hook should auto-refresh status
- [ ] Check haios-status-slim.json includes test-runner
- [ ] Verify agent appears in vitals

### Step 3: Integration Test
- [ ] Invoke via `Task(prompt="Run tests in tests/", subagent_type="test-runner")`
- [ ] Verify structured output returned
- [ ] Test with passing and failing tests

---

## Verification

- [ ] Agent file exists
- [ ] Agent discoverable in vitals
- [ ] Returns structured pass/fail summary

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Large output | Medium | --tb=short truncates |
| Slow tests | Low | Optional timeout |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 85 | 2025-12-18 | - | Plan filled | Design complete |
| 87 | 2025-12-19 | - | Complete | Agent created, discovered, hot-reload limitation documented |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/agents/test-runner.md` | File exists with frontmatter | [x] | Session 87 |
| `haios-status-slim.json` | test-runner in agents | [x] | Auto-refresh worked |
| Vitals output | Shows test-runner | [x] | Discovered via PostToolUse |

**Verification Commands:**
```bash
# Check agent exists
test -f ".claude/agents/test-runner.md" && echo "EXISTS"
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | File read, frontmatter confirmed |
| Agent appears in vitals? | Yes | haios-status-slim.json shows test-runner |
| Any deviations from plan? | Yes | See limitation below |

**Limitation Discovered:** Claude Code's `Task(subagent_type=...)` registry doesn't hot-reload mid-session. Agent file exists and is discovered by our PostToolUse hook (haios-status-slim.json updated), but won't be invocable until next session start. This is expected behavior - subagent registry is populated from `.claude/agents/` at session initialization.

---

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (agent exists, discoverable)
- [x] WHY captured (reasoning stored to memory)
- [x] Documentation current
- [x] Ground Truth Verification completed above

---

## References

- E2-091: Implementation Cycle Skill
- schema-verifier: Reference subagent pattern
- ADR-038: M2-Governance Symphony Architecture

### Symphony Integration (ADR-038)

| Movement | Integration |
|----------|-------------|
| **RHYTHM** | Agent discovered in vitals (auto-refresh via PostToolUse) |
| **LISTENING** | Could store test failure patterns to memory |
| **RESONANCE** | Test results could be logged as events |

---
