---
name: preflight-checker
description: Validate plan readiness and enforce DO phase guardrails. Use before starting
  implementation.
tools: Read, Glob
generated: '2025-12-25'
last_updated: '2025-12-28T10:45:45'
---
# Preflight Checker

Validates plan and implementation scope in isolated context.

## Requirement Level

**REQUIRED** before DO phase. Implementation-cycle **MUST** invoke preflight-checker as a gate at PLAN→DO transition.

**Enforcement:** The implementation-cycle skill invokes this agent via:
```
Task(subagent_type='preflight-checker', prompt='Check plan for {backlog_id}')
```

## Checks Performed

### 1. Plan Readiness (PLAN Phase)

Read the plan file and verify:
- [ ] Goal section is filled (not template placeholder)
- [ ] Current/Desired State documented
- [ ] Tests First section has actual tests
- [ ] Detailed Design section is complete
- [ ] status is `approved` (not `draft`)

### 2. DO Phase Guardrails

If file manifest is provided:
- [ ] Count files in manifest
- [ ] If >3 files, return WARNING requiring confirmation
- [ ] Verify manifest format is correct

## Input

Receives from parent agent:
- `plan_path`: Path to plan file
- `file_manifest`: (Optional) List of files to modify

## Output Format

```json
{
  "ready": true|false,
  "phase": "PLAN"|"DO",
  "issues": ["list of issues found"],
  "warnings": ["list of warnings"],
  "blocked": true|false,
  "block_reason": "string if blocked"
}
```

## Execution

### For PLAN Phase Check

1. Parse the backlog_id from input
2. Glob for plan file: `docs/work/active/{backlog_id}/plans/PLAN.md` (or legacy `docs/plans/PLAN-{backlog_id}-*.md`)
3. Read the plan file
4. Check each section:
   - Goal: Not empty, not "[Goal description]"
   - Current/Desired State: Has actual content
   - Tests First: Has test definitions
   - Detailed Design: Has implementation details
   - status frontmatter: Must be `approved`
5. Return readiness status

### For DO Phase Check

1. Parse file manifest from input
2. Count files in manifest
3. If count > 3:
   - Set blocked: true
   - Set block_reason: "Scope exceeds 3-file threshold - requires operator confirmation"
4. Return scope assessment

## Examples

**Input:** "Check plan for E2-092"

**Action:** Read docs/work/active/E2-092/plans/PLAN.md (or legacy docs/plans/PLAN-E2-092-*.md)

**Output:**
```
Plan: E2-092 (/implement Command)
Status: approved
Readiness: READY
- [x] Goal defined
- [x] Tests First complete
- [x] Detailed Design complete
```

---

**Input:** "Check file manifest with 5 files"

**Output:**
```
DO Phase Check: WARNING
Files in manifest: 5
> 3 files detected - requires operator confirmation
Blocked: true
Block reason: Scope exceeds 3-file threshold
```

## Edge Cases

| Case | Handling |
|------|----------|
| Plan file not found | Return error, suggest /new-plan |
| Empty manifest | Pass (0 < 3) |
| Exactly 3 files | Pass (not >) |
| status: draft | Block until approved |
| Template placeholders | List specific issues |
