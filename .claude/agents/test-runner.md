---
name: test-runner
description: Execute pytest in isolated context. Returns structured pass/fail summary.
  Use during DO and CHECK phases.
tools: Bash, Read
model: haiku
requirement_level: required
category: utility
trigger_conditions:
  - DO phase of implementation-cycle (TDD test runs)
  - CHECK phase of implementation-cycle (full suite verification)
input_contract: "test path or filter expression"
output_contract: "Structured summary with pass/fail counts, duration, failed test names and errors"
invoked_by:
  - implementation-cycle (DO phase, TDD test runs — required)
  - implementation-cycle (CHECK phase, full suite verification — required)
related_agents:
  - validation-agent (broader CHECK phase validation)
id: test-runner
role: utility
capabilities:
  - pytest-execution
  - test-result-parsing
produces:
  - test-results
consumes:
  - work-item
generated: '2026-02-01'
last_updated: '2026-02-15T21:05:00'
---
# Test Runner

## Requirement Level

**REQUIRED** during DO phase for all pytest test runs.
**REQUIRED** during CHECK phase for full test suite verification.

Main agent MUST NOT run pytest inline. Delegate all test execution to this subagent (S436 / Memory 88078).

Executes tests in isolated context, returns clean summary to parent.

## Process

1. Receive test path or filter from parent
2. Run pytest with `--tb=short` for concise output
3. Parse output for pass/fail counts
4. Extract failed test names and error summaries
5. Return structured result

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

## Tips

- Use `--tb=short` for concise tracebacks
- Use `-x` to stop on first failure (faster feedback)
- Use `-k "test_name"` to filter tests
- Read test file first if parent needs specific test context
