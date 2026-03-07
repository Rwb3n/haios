---
allowed-tools: Bash, Edit, Read, Grep, Glob, mcp__haios-memory__ingester_ingest
description: Close a work item with DoD validation
argument-hint: <backlog_id>
generated: 2025-12-22
last_updated: '2026-01-25T21:35:05'
---
# Close Work Item

Close a work item with Definition of Done (DoD) validation per ADR-033.

**Arguments:** $ARGUMENTS

Parse the backlog_id (e.g., `E2-023`, `INV-033`).

---

## Step 1: Lookup Work Item

**ADR-039:** Work files are the source of truth.
**E2-212:** Work items are now directories: `docs/work/active/{id}/WORK.md`

### 1a. Find work file

Look for work file using directory pattern first, then flat pattern:
```
# Try directory structure first (E2-212)
Glob(pattern="docs/work/active/{backlog_id}/WORK.md")
# Fall back to flat structure (legacy)
Glob(pattern="docs/work/active/WORK-{backlog_id}-*.md")
```

**If work file found:**
1. Read work file frontmatter for `title`, `status`
2. Proceed to Step 1b (find associated documents)

**If NO work file found:**
- Check if it's an investigation (`type: investigation` or legacy INV-*) without a work file
- If investigation type, proceed to Step 1.5 (Investigation DoD)
- Otherwise: Inform user "Work item {backlog_id} not found in docs/work/active/"
- STOP

---

## Step 1.1: Detect Effort Tier (Prospective Predicate — REQ-LIFECYCLE-005)

After finding work item, determine close ceremony tier using WORK.md frontmatter (prospective predicate, not retrospective git diff):

1. Read `effort:` field from WORK.md frontmatter
2. Read `source_files:` list and count entries
3. If `effort: small` AND `source_files` count <= 3: Set `lightweight_close: true`
4. If `effort: medium` or higher: Set `lightweight_close: false`
5. Default (effort field missing): Set `lightweight_close: false` (conservative — absent data MUST NOT produce more permissive classification per REQ-LIFECYCLE-005)

**Note:** This is a prospective predicate (declared scope before work begins). retro-cycle Phase 0's `assess_scale()` is a retrospective predicate (git diff after work). Both are valid for their lifecycle position. Close ceremony tier uses the prospective predicate because tier detection happens before retro-cycle runs.

**Lightweight close path:** If `lightweight_close: true`:
- retro-cycle runs with trivial scaling (Phase 0 assess_scale handles this independently)
- close-work-cycle uses inline DoD checklist (skip dod-validation-cycle)
- checkpoint-cycle uses inline VERIFY (skip anti-pattern-checker)

**Full close path:** If `lightweight_close: false`:
- All ceremonies run at full weight (current behavior, unchanged)

**Flag propagation:** All skill invocations (retro-cycle, close-work-cycle, checkpoint-cycle) execute within the same agent turn. The `lightweight_close` flag persists in agent working memory across skill boundaries. No file write needed.

---

## Chain to Retro Cycle

After work item is found, first invoke retro-cycle for structured reflection:

```
Skill(skill="retro-cycle")
```

This forces the agent into dedicated cognitive space (REFLECT -> DERIVE -> COMMIT -> EXTRACT) before entering "closing mode." Evidence-anchored observations are stored with typed provenance tags.

---

## Chain to Retro-Enrichment Agent

After retro-cycle completes and returns `extracted_items`, invoke retro-enrichment-agent if `extracted_items` is non-empty.

**IMPORTANT:** Before invoking Task(), substitute `{work_id}`, `{memory_concept_ids_json}`, `{extract_concept_ids_json}`, and `{extracted_items_yaml}` with actual values from the retro-cycle return object. Do NOT copy the template verbatim — literal placeholder strings will cause silent malformed input.

```
Task(
  subagent_type='retro-enrichment-agent',
  model='haiku',
  prompt='Enrich retro-cycle EXTRACT output for {work_id}.
    work_id: {work_id}
    memory_concept_ids: {memory_concept_ids_json}
    extract_concept_ids: {extract_concept_ids_json}
    extracted_items: {extracted_items_yaml}
    Cross-reference each item against memory via memory_search_with_experience.
    Annotate with related_memory_ids, convergence_count, prior_work_ids.
    Store enriched output with retro-enrichment:{work_id} provenance.
    Return enriched_items list + enrichment_concept_ids.'
)
```

If `extracted_items` is empty (trivial scale or no actionable items), skip enrichment.
Enrichment never blocks closure — proceed to close-work-cycle regardless of enrichment result.

---

## Chain to Close Work Cycle

After retro-enrichment completes (or was skipped), invoke close-work-cycle:

```
Skill(skill="close-work-cycle")
```

The skill guides through VALIDATE -> ARCHIVE -> CHAIN phases.

**See `close-work-cycle` SKILL.md for VALIDATE/ARCHIVE/CHAIN phase details.**

---
