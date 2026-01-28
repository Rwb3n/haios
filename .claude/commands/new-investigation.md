---
allowed-tools: Bash, mcp__haios-memory__memory_search_with_experience
description: Create new Investigation document with template
argument-hint: <title>
generated: '2025-12-25'
last_updated: '2026-01-28T22:44:16'
---

# Create Investigation

**MUST** use this command (not raw Write) when creating investigation documents.

Arguments: $ARGUMENTS

## ID Policy (WORK-030)

Investigations use **WORK-XXX** format with `type: investigation` in the work file.
The INV-XXX prefix is deprecated. All work items use universal WORK-XXX IDs.

Parse arguments:
- If one argument: title only (auto-assign WORK-XXX)
- If two arguments: backlog_id and title (backwards compatible)

## Prerequisite: Work File Required

**MUST** create work item before investigation document (L1 invariant: Work Before Plan).

```bash
# Step 1: Get next ID and create work item with type: investigation
python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from scaffold import get_next_work_id; print(get_next_work_id())"
# Use that ID:
just work WORK-031 "<title>"

# Step 2: Set type: investigation in the work file frontmatter
# Edit docs/work/active/WORK-031/WORK.md to set type: investigation

# Step 3: Run work-creation-cycle to populate Context/Deliverables
Skill(skill="work-creation-cycle")

# Step 4: Then create investigation document
just inv WORK-031 "<title>"
```

If work file doesn't exist, `just inv` will fail with guidance to run `/new-work` first.

## Memory Query (E2-083: Proactive Retrieval)

Before scaffolding, query memory for prior related work:
1. Query `mcp__haios-memory__memory_search_with_experience` with:
   - query: `"prior investigations about {title keywords}"`
   - mode: `semantic`
2. If related investigations or findings found, note them with "**Related prior work:**"
3. Suggest cross-references: "See also: INV-xxx" if relevant
4. Example: For title "Schema Drift Issues", query: `"prior investigations about schema drift"`

## Create Investigation

Run scaffolding via just recipe:

```bash
just inv <backlog_id> "<title>"
```

Example:
```bash
just inv WORK-031 "Observability Gap Analysis"
# Creates: docs/work/active/WORK-031/investigations/001-observability-gap-analysis.md
```

Report the created file path to the user.

---

## Chain to Investigation Cycle (E2-XXX)

After scaffolding, **MUST** immediately invoke the investigation-cycle skill:

```
Skill(skill="investigation-cycle")
```

This chains the creation into the structured HYPOTHESIZE→EXPLORE→CONCLUDE workflow.
The skill will:
1. Read the newly created investigation file
2. Guide filling in hypotheses and scope (HYPOTHESIZE phase)
3. Execute investigation steps (EXPLORE phase)
4. Synthesize findings and spawn work items (CONCLUDE phase)

---

## Allowed Field Values

| Field | Allowed Values |
|-------|----------------|
| status | `draft`, `active`, `pending`, `closed`, `complete`, `archived` |
| lifecycle_phase | `discovery` (default) |

Templates default to `status: active`. Use `complete` when investigation is done.

---

## ADR-034 Reference

This command implements the canonical DISCOVERY phase from ADR-034:
- Investigations analyze problems before design or planning
- Use INVESTIGATION- prefix for all discovery phase documents
- Store findings to memory before closing
- List spawned work items in the document
