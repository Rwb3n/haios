---
template: implementation_plan
id: E2-223
title: Integrate Routing-Gate into Cycle Skills
status: complete
author: Hephaestus
created: 2025-12-28
milestone: M7c-Governance
priority: medium
effort: small
backlog_id: E2-223
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-28T20:03:34'
---
# Implementation Plan: E2-223 - Integrate Routing-Gate into Cycle Skills

## Objective

Replace duplicated routing tables in three cycle skill CHAIN phases with routing-gate skill invocation.

---

## Current State

Three cycle skills each have identical routing tables in their CHAIN phase:

1. **implementation-cycle** (lines 205-215): Routing Decision Table with 4 cases
2. **investigation-cycle** (lines 127-134): Routing Decision Table with 4 cases
3. **close-work-cycle** (lines 203-210): Routing Decision Table with 4 cases

Each table duplicates the same logic:
- No items returned -> await operator
- ID starts with `INV-` -> investigation-cycle
- Work file has plan in `documents.plans` -> implementation-cycle
- Otherwise -> work-creation-cycle

**E2-221 created:** `.claude/lib/routing.py` with `determine_route()` function and `.claude/skills/routing-gate/SKILL.md` documenting usage.

---

## Desired State

Each cycle skill CHAIN phase:
1. Uses routing-gate skill documentation for routing logic
2. Calls routing-gate (conceptually, via instructions) rather than embedding decision table
3. DRY - single source of truth for routing decisions

---

## Detailed Design

### Approach

Replace the "Routing Decision Table" section in each CHAIN phase with instructions to use routing-gate.

**New CHAIN section pattern:**

```markdown
### N. CHAIN Phase

**Goal:** Route to next work item.

**Actions:**
1. Query next work: `just ready`
2. If items returned, read first work file to check `documents.plans`
3. **Invoke routing-gate skill logic:**
   - See `routing-gate` skill for decision table
   - Or call `determine_route(next_work_id, has_plan)` from `.claude/lib/routing.py`
4. Execute the returned action:
   - `invoke_investigation` -> `Skill(skill="investigation-cycle")`
   - `invoke_implementation` -> `Skill(skill="implementation-cycle")`
   - `invoke_work_creation` -> `Skill(skill="work-creation-cycle")`
   - `await_operator` -> Report "No unblocked work. Awaiting operator direction."

**Exit Criteria:**
- [ ] Next work item identified (or none available)
- [ ] Appropriate cycle skill invoked (or awaiting operator)

**Tools:** Bash(just ready), Read, Skill(routing-gate)
```

### Changes Per File

| File | Section | Change |
|------|---------|--------|
| implementation-cycle/SKILL.md | CHAIN Phase (5.) | Replace routing table with routing-gate reference |
| investigation-cycle/SKILL.md | CHAIN Phase (4.) | Replace routing table with routing-gate reference |
| close-work-cycle/SKILL.md | CHAIN Phase (5.) | Replace routing table with routing-gate reference |

---

## Tests First

**Test Type:** Manual verification (skill files are markdown, not code)

1. **CHAIN section consistency:** All three updated CHAIN sections follow same pattern
2. **Routing-gate reference:** Each mentions "routing-gate skill" or "determine_route()"
3. **No embedded tables:** Routing Decision Table removed from all three
4. **Tools updated:** `Skill(routing-gate)` or equivalent in Tools section

---

## Implementation Steps

1. Update implementation-cycle SKILL.md CHAIN phase
2. Update investigation-cycle SKILL.md CHAIN phase
3. Update close-work-cycle SKILL.md CHAIN phase
4. Add routing-gate to Related section of each (if not already)

---

## Ground Truth Verification

| Criterion | Verification |
|-----------|--------------|
| No duplicate routing tables | Grep for "Routing Decision Table" - should only find in routing-gate |
| Routing-gate referenced | Grep for "routing-gate" in each updated skill |
| DRY achieved | Single source of truth in routing-gate skill |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Agent confusion with reference | Low | Low | Clear instructions in new CHAIN section |
| Backward compatibility | None | None | No code changes, only documentation |

---

## Rollback Plan

Revert the three SKILL.md files to previous version via git.

---

## Related

- **E2-221:** Created routing-gate skill (prerequisite)
- **E2-222:** Routing threshold configuration (future)
- **INV-048:** Source investigation for routing architecture
