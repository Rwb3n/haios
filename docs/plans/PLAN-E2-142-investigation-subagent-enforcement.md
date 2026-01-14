---
template: implementation_plan
status: complete
date: 2025-12-23
backlog_id: E2-142
title: "Investigation Subagent Enforcement"
author: Hephaestus
lifecycle_phase: plan
session: 104
spawned_by: INV-022
version: "1.5"
generated: 2025-12-23
last_updated: 2025-12-23T13:47:56
---
# Implementation Plan: Investigation Subagent Enforcement

@docs/README.md
@docs/epistemic_state.md

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.
-->

---

## Goal

Investigation-cycle skill and investigation-agent will use L3 (MUST) language instead of L2 (SHOULD/RECOMMENDED), requiring subagent invocation during EXPLORE phase.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | SKILL.md, investigation-agent.md |
| Lines of code affected | ~10 | Text changes only |
| New files to create | 0 | - |
| Tests to write | 0 | Documentation change, no code |
| Dependencies | 0 | No code dependencies |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Standalone documentation |
| Risk of regression | None | No code changes |
| External dependencies | None | No APIs, services, or config |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Update SKILL.md | 5 min | High |
| Update investigation-agent.md | 5 min | High |
| **Total** | 10 min | High |

---

## Current State vs Desired State

This section documents the L2 to L3 upgrade for investigation subagent usage.

### Current State

**.claude/skills/investigation-cycle/SKILL.md (lines 65-68):**
```markdown
**Guardrails (SHOULD follow):**
1. **One hypothesis at a time** - Focus exploration
2. **Document findings as discovered** - Don't wait until end
3. **Query memory before assuming** - Prior work may answer questions
```

**.claude/agents/investigation-agent.md (line 18):**
```markdown
**OPTIONAL** but **RECOMMENDED** for complex investigations.
```

**Behavior:** Agent may bypass investigation-agent subagent ~20% of the time.

**Result:** Investigation work done directly instead of delegated to specialized subagent.

### Desired State

**.claude/skills/investigation-cycle/SKILL.md:**
```markdown
**Guardrails (MUST follow):**
1. **MUST invoke investigation-agent** for EXPLORE phase - specialized subagent handles evidence gathering
2. **One hypothesis at a time** - Focus exploration
3. **Document findings as discovered** - Don't wait until end
4. **Query memory before assuming** - Prior work may answer questions
```

**.claude/agents/investigation-agent.md:**
```markdown
**REQUIRED** for EXPLORE phase. The investigation-cycle skill MUST invoke this agent.
```

**Behavior:** Agent must use investigation-agent subagent during EXPLORE phase.

**Result:** L3 enforcement - guidance becomes requirement.

---

## Tests First (TDD)

**SKIPPED:** Pure documentation task, no code to test. Verification is manual review of markdown files.

---

## Detailed Design

Two markdown files need text changes to upgrade from L2 (SHOULD/RECOMMENDED) to L3 (MUST/REQUIRED) language.

### Exact Text Change 1: investigation-cycle SKILL.md

**File:** `.claude/skills/investigation-cycle/SKILL.md`
**Location:** Lines 65-68, EXPLORE phase Guardrails section

**Current Text:**
```markdown
**Guardrails (SHOULD follow):**
1. **One hypothesis at a time** - Focus exploration
2. **Document findings as discovered** - Don't wait until end
3. **Query memory before assuming** - Prior work may answer questions
```

**Changed Text:**
```markdown
**Guardrails (MUST follow):**
1. **MUST invoke investigation-agent** for evidence gathering - specialized subagent handles exploration
2. **One hypothesis at a time** - Focus exploration
3. **Document findings as discovered** - Don't wait until end
4. **Query memory before assuming** - Prior work may answer questions
```

### Exact Text Change 2: investigation-agent.md

**File:** `.claude/agents/investigation-agent.md`
**Location:** Lines 17-18, Requirement Level section

**Current Text:**
```markdown
## Requirement Level

**OPTIONAL** but **RECOMMENDED** for complex investigations. The investigation-cycle skill may invoke this agent.
```

**Changed Text:**
```markdown
## Requirement Level

**REQUIRED** for EXPLORE phase. The investigation-cycle skill **MUST** invoke this agent for evidence gathering during investigations.
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| L3 not L4 | Text requirement, not hook enforcement | L3 (guidance) is appropriate - hard blocking would be too restrictive for edge cases |
| EXPLORE phase only | Not HYPOTHESIZE or CONCLUDE | EXPLORE is where evidence gathering happens - the subagent's specialty |
| Add guardrail, not replace | New guardrail #1, renumber others | Existing guardrails are still valid |

### Memory Context (E2-083)

Prior work found via memory query:
- Concept 77258: "L3 subagent requirement (MUST invoke investigation-agent)"
- Concept 76827: "L3 enforcement via guidance, not hard blocking"

---

## Implementation Steps

This is a trivial documentation change requiring edits to two markdown files.

### Step 1: Update investigation-cycle SKILL.md
- [ ] Change "SHOULD follow" to "MUST follow"
- [ ] Add new guardrail #1 for investigation-agent invocation
- [ ] Renumber existing guardrails to 2, 3, 4

### Step 2: Update investigation-agent.md
- [ ] Change "OPTIONAL but RECOMMENDED" to "REQUIRED"
- [ ] Update description to reference MUST requirement

### Step 3: Verification
- [ ] Read both files to confirm changes
- [ ] Validate no typos or formatting issues

### Step 4: README Sync
**SKIPPED:** No new files, no directory structure changes. Parent READMEs don't need updates.

### Step 5: Consumer Verification
**SKIPPED:** Documentation change only, no code references to update.

---

## Verification

- [ ] SKILL.md contains "MUST follow" and investigation-agent guardrail
- [ ] investigation-agent.md contains "REQUIRED for EXPLORE phase"
- [ ] Both files render correctly in markdown

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent still bypasses | Low | L3 is guidance not enforcement - acceptable |
| Too restrictive | Low | Only applies to EXPLORE phase |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 104 | 2025-12-23 | - | Plan created | Ready for implementation |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/investigation-cycle/SKILL.md` | "MUST follow", investigation-agent guardrail | [ ] | |
| `.claude/agents/investigation-agent.md` | "REQUIRED for EXPLORE phase" | [ ] | |

**Verification Commands:**
```bash
# Grep for L3 language
Grep(pattern="MUST follow|REQUIRED", path=".claude/skills/investigation-cycle")
Grep(pattern="REQUIRED for EXPLORE", path=".claude/agents")
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Changes match plan exactly? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Text changes made
- [ ] WHY captured (reasoning stored to memory)
- [ ] Files verified by reading
- [ ] Ground Truth Verification completed above

---

## References

- **Spawned by:** INV-022 (Work-Cycle-DAG Unified Architecture)
- **Related:** E2-144 (Investigation Template Enhancement)
- **Pattern:** L2 → L3 upgrade (documented suggestion to requirement)
- **Memory:** Concepts 77258, 76827 (L3 enforcement patterns)

---
