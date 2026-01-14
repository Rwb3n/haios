---
allowed-tools: Bash, mcp__haios-memory__memory_search_with_experience
description: Create new Implementation Plan with template
argument-hint: <backlog_id> <title>
generated: '2025-12-25'
last_updated: '2025-12-28T10:56:32'
---

# Create Implementation Plan

**MUST** use this command (not raw Write) when creating files in `docs/plans/`.

Arguments: $ARGUMENTS

Parse arguments as: `<backlog_id> <title>`
- First argument is the backlog ID (e.g., E2-015)
- Remaining arguments form the title

**REQUIRED:** Every plan **MUST** be linked to a backlog item (E2-xxx).

## Prerequisite: Work File Required

**MUST** create work item before implementation plan (L1 invariant: Work Before Plan).

```bash
# Step 1: Create work item
just work <backlog_id> "<title>"

# Step 2: Run work-creation-cycle to populate Context/Deliverables
Skill(skill="work-creation-cycle")

# Step 3: Then create plan (this command)
```

If work file doesn't exist, `just plan` will fail with guidance to run `/new-work` first.

## Memory Query (E2-083: Proactive Retrieval)

Before scaffolding, query memory for relevant prior work:
1. Query `mcp__haios-memory__memory_search_with_experience` with:
   - query: `"implementation planning strategies for {title}"`
   - mode: `knowledge_lookup`
2. If relevant strategies or patterns found, note them for inclusion in the plan
3. Example: For title "Test Runner Subagent", query: `"implementation planning strategies for test runner subagent"`

## Create Plan

Run scaffolding via just recipe:

```bash
just plan <backlog_id> "<title>"
```

Example:
```bash
just plan E2-094 "Test Runner Subagent"
# Creates: docs/work/active/E2-094/plans/PLAN.md
```

Report the created file path to the user.

---

## Chain to Plan Authoring Cycle

After scaffolding, **MUST** immediately invoke the plan-authoring-cycle skill to populate the plan:

```
Skill(skill="plan-authoring-cycle")
```

This chains the creation into the structured ANALYZE→AUTHOR→VALIDATE workflow.
The skill will:
1. Read the newly created plan file
2. Identify sections with placeholder text
3. Systematically populate Goal, Effort, Design, Tests sections
4. Validate plan is complete (no placeholders)
5. Set plan status to `approved`

---

## Then Chain to Implementation Cycle

After plan-authoring-cycle completes (plan is `approved`), **MUST** invoke the implementation-cycle skill:

```
Skill(skill="implementation-cycle")
```

This chains into the structured PLAN→DO→CHECK→DONE workflow.
The skill will:
1. Verify plan is approved and complete
2. Execute implementation with TDD (DO phase)
3. Verify tests and integration (CHECK phase)
4. Capture WHY and close (DONE phase)

---

## Allowed Field Values

| Field | Allowed Values |
|-------|----------------|
| status | `draft`, `approved`, `rejected`, `complete` |

Templates default to `status: draft`. Typical lifecycle: draft → approved → complete.
