---
template: implementation_plan
status: complete
date: 2025-12-17
backlog_id: E2-093
title: "Preflight Checker Subagent"
author: Hephaestus
lifecycle_phase: plan
session: 85
spawned_by: Session-83
blocked_by: [E2-091]
related: [E2-091, E2-092, schema-verifier, ADR-038]
milestone: M3-Cycles
version: "1.2"
---
# generated: 2025-12-17
# System Auto: last updated on: 2025-12-20 20:21:12
# Implementation Plan: Preflight Checker Subagent

@docs/README.md
@docs/epistemic_state.md
@.claude/agents/schema-verifier.md

---

## Goal

A `preflight-checker` subagent exists that validates plan readiness (PLAN phase) and enforces DO phase guardrails (file manifest, >3 file gate) in an isolated context.

---

## Current State vs Desired State

### Current State

```markdown
# Implementation-cycle skill has L2 guidance:
# - "SHOULD" create file manifest
# - "SHOULD" confirm if >3 files
# No enforcement mechanism - agents can skip
```

**Behavior:** Guardrails are advisory only, easily skipped.

**Result:** Large-scope changes can proceed without confirmation.

### Desired State

```markdown
# .claude/agents/preflight-checker.md
---
name: preflight-checker
description: Validate plan readiness and enforce DO phase guardrails. Use before starting implementation.
tools: Read, Glob
---
# Preflight Checker
Validates:
1. Plan has filled-in sections (not template placeholders)
2. Tests First section is complete
3. File manifest exists (if in DO phase)
4. >3 files triggers confirmation requirement
```

**Behavior:** L3 enforcement - blocks until conditions met.

**Result:** Consistent quality gate before implementation.

---

## Tests First (TDD)

### Test 1: Agent File Exists
```bash
test -f ".claude/agents/preflight-checker.md"
# Expected: exit 0
```

### Test 2: Agent Appears in Discovery
```bash
# After creating, check haios-status-slim.json
# infrastructure.agents should include "preflight-checker"
```

### Test 3: Agent Has Required Frontmatter
```yaml
# Verify frontmatter has:
name: preflight-checker
description: ...
tools: Read, Glob
```

---

## Detailed Design

### Agent File Structure

```markdown
---
name: preflight-checker
description: Validate plan readiness and enforce DO phase guardrails. Use before starting implementation.
tools: Read, Glob
---
# Preflight Checker

Validates plan and implementation scope in isolated context.

## Requirement Level

**OPTIONAL** but **RECOMMENDED** before DO phase. The implementation-cycle skill will invoke this when available.

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

## Example

Input: "Check plan for E2-092"
Action: Read docs/plans/PLAN-E2-092-*.md
Output:
```
Plan: E2-092 (/implement Command)
Status: approved
Readiness: READY
- [x] Goal defined
- [x] Tests First complete
- [x] Detailed Design complete
```

Input: "Check file manifest with 5 files"
Output:
```
DO Phase Check: WARNING
Files in manifest: 5
> 3 files detected - requires operator confirmation
Blocked: true
Block reason: Scope exceeds 3-file threshold
```
```

### Behavior Logic

```
Input (plan_path, file_manifest?)
    │
    ├─► PLAN Phase Check
    │   ├─► Read plan file
    │   ├─► Check each section for placeholders
    │   ├─► Verify status is approved
    │   └─► Return readiness status
    │
    └─► DO Phase Check (if manifest provided)
        ├─► Count files in manifest
        ├─► If >3: blocked=true, require confirmation
        └─► Return scope assessment
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| L3 enforcement vs L2 guidance | L3 (blocking) | Prevents runaway scope, skill has L2 guidance |
| Tools available | Read, Glob only | Minimal footprint, read-only |
| Output format | JSON | Structured for parent agent parsing |
| >3 file threshold | Hard block | Based on Session 84 design discussion |

### Input/Output Examples

| Input | Output | Notes |
|-------|--------|-------|
| Plan with placeholders | `ready: false, issues: [...]` | Blocks until filled |
| Plan with status: draft | `ready: false, issues: ["status is draft"]` | Needs approval |
| Manifest with 2 files | `blocked: false` | Under threshold |
| Manifest with 5 files | `blocked: true, block_reason: ">3 files"` | Requires confirmation |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Plan file not found | Return error, suggest /new-plan | Manual test |
| Empty manifest | Pass (0 < 3) | N/A |
| Exactly 3 files | Pass (not >) | Edge case |

---

## Implementation Steps

### Step 1: Create Agent File
- [ ] Create `.claude/agents/preflight-checker.md`
- [ ] Add YAML frontmatter (name, description, tools)
- [ ] Add body content with checks

### Step 2: Verify Discovery
- [ ] PostToolUse hook should auto-refresh status
- [ ] Check haios-status-slim.json includes preflight-checker
- [ ] Verify agent appears in vitals

### Step 3: Integration Test
- [ ] Invoke via `Task(prompt="...", subagent_type="preflight-checker")`
- [ ] Test with incomplete plan
- [ ] Test with >3 file manifest

---

## Verification

- [ ] Agent file exists
- [ ] Agent discoverable in vitals
- [ ] PLAN phase checks work
- [ ] DO phase >3 file gate works

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Too restrictive | Medium | Can bypass with explicit override |
| Placeholder detection | Low | Use clear markers in templates |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 85 | 2025-12-18 | - | Plan filled | Design complete |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/agents/preflight-checker.md` | File exists with frontmatter | [ ] | |
| `haios-status-slim.json` | preflight-checker in agents | [ ] | Auto-refresh |
| Vitals output | Shows preflight-checker | [ ] | |

**Verification Commands:**
```bash
# Check agent exists
test -f ".claude/agents/preflight-checker.md" && echo "EXISTS"
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Agent appears in vitals? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass (agent exists, discoverable)
- [ ] WHY captured (reasoning stored to memory)
- [ ] Documentation current
- [ ] Ground Truth Verification completed above

---

## References

- E2-091: Implementation Cycle Skill
- schema-verifier: Reference subagent pattern
- Session 84: L2/L3 split design decision
- ADR-038: M2-Governance Symphony Architecture

### Symphony Integration (ADR-038)

| Movement | Integration |
|----------|-------------|
| **RHYTHM** | Agent discovered in vitals (auto-refresh via PostToolUse) |
| **LISTENING** | Could query memory for similar plan patterns |
| **RESONANCE** | Blocking events could be logged as warnings |

---
