---
type: reference
skill: implementation-cycle
---
# Implementation Cycle — Composition and Quick Reference

## Composition Map

| Phase | Primary Tool | Subagent | Command |
|-------|--------------|----------|---------|
| PLAN  | Read, Glob   | plan-authoring-agent (sonnet)*, preflight-checker (haiku) | /new-plan |
| DO    | Write, Edit  | design-review-validation-agent (sonnet, exit gate) | - |
| CHECK | Bash(pytest) | test-runner (haiku), preflight-checker/deliverables (haiku) | /validate |
| DONE  | Edit, Write  | why-capturer | - |
| CHAIN | Bash, Skill  | - | /close |

---

## Quick Reference

| Phase | Question to Ask | If NO |
|-------|-----------------|-------|
| PLAN  | Is the plan ready? | Fill in design |
| DO    | Is file manifest created? | List files first |
| DO    | Is implementation done? | One change at a time |
| CHECK | Is verification complete? | Fix issues, retest |
| CHECK | **Are ALL WORK.md deliverables done?** | **BLOCK - return to DO** |
| CHECK | **Are ALL plan steps checked off?** | **BLOCK - return to DO** |
| CHECK | Is artifact discoverable? | Run update-status, verify in slim JSON |
| DONE  | Is WHY captured? | Store learnings |
| CHAIN | Is work item closed? | Run /close {backlog_id} |
| CHAIN | Is next work identified? | Run `mcp__haios-operations__queue_ready()` |

**DO phase guardrails:**
- List files BEFORE writing (manifest)
- One logical change at a time
- >3 files? Pause and confirm scope

**CHECK varies by task type:**
- Code: `pytest tests/ -v` + Ground Truth
- Docs/ADRs: `/validate` + Ground Truth
- Config: Manual review + Ground Truth
- Skills/Agents/Commands: `mcp__haios-operations__hierarchy_update_status()` + verify in haios-status-slim.json

---

## TDD Cycle Within DO Phase

```
Write Test (FAIL) --> Run --> Write Code --> Run (PASS) --> Refactor --> Loop
     RED                         GREEN                      REFACTOR
```

1. Write a failing test first
2. Run test - see it FAIL (RED)
3. Write minimal code to pass
4. Run test - see it PASS (GREEN)
5. Refactor if needed
6. Repeat for next test

---

## Governance Event Logging (E2-108)

**SHOULD** log phase transitions and validation outcomes for observability.

### Phase Transition Logging

Phase transitions are logged automatically via PostToolUse hook (WORK-168). The hook also:
- **Auto-advances** session_state to the next phase after each lifecycle skill invocation
- **Auto-syncs** the WORK.md `cycle_phase` field to match session_state (WORK-171)

No manual `cycle_set` calls are needed — phase advancement is automatic.

View metrics with:
```bash
just governance-metrics
```

### Validation Outcome Logging

Validation outcomes are logged automatically. Check audit trail via:
```bash
just events
```

### Benefits

- **Metrics:** `just governance-metrics` shows pass rates and common failures
- **Warnings:** Repeated failures (3+) trigger immediate warning
- **Audit:** Events are checked at close time to surface governance bypasses
