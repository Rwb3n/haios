---
name: close-work-cycle
type: ceremony
description: "HAIOS Close Work Cycle for structured work item closure. Prerequisite:
  retro-cycle must complete before this cycle (invoked by /close). Guides
  VALIDATE->ARCHIVE->CHAIN workflow with DoD enforcement."
category:
  - closure
  - queue
input_contract:
  - field: work_id
    type: string
    required: true
    description: "Work item ID to close (e.g., WORK-110)"
    pattern: "WORK-\\d{3}"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether closure completed successfully"
  - field: work_id
    type: string
    guaranteed: always
    description: "The work item ID"
  - field: archived_path
    type: path
    guaranteed: on_success
    description: "Path to the closed work item file"
  - field: memory_concept_ids
    type: list
    guaranteed: on_success
    description: "Memory concept IDs from retro-cycle COMMIT (delegated)"
  - field: error
    type: string
    guaranteed: on_failure
    description: "Error description"
side_effects:
  - "Status change (active -> complete)"
  - "Memory commit (delegated to retro-cycle COMMIT phase)"
  - "Log ceremony event"
  - "Git commit via checkpoint-cycle"
  - "Upstream status propagation to ARC.md (WORK-034)"
recipes:
- close-work
- update-status
generated: 2025-12-25
last_updated: '2026-02-03T23:03:31'
---
# Close Work Cycle

This skill defines the VALIDATE-ARCHIVE-CHAIN cycle for closing work items with Definition of Done (DoD) enforcement per ADR-033. Prerequisite: retro-cycle must complete before this cycle (invoked by /close command).

## When to Use

**Invoked automatically** by `/close` command after retro-cycle.
**Manual invocation:** `Skill(skill="close-work-cycle")` when closing an existing work item.

---

## The Cycle

```
[retro-cycle] --> VALIDATE --> ARCHIVE --> CHAIN
      │                                      |
      │                                [route next]
  structured reflection                      |
  (REFLECT->DERIVE->               /-------------\
   COMMIT->EXTRACT)          type=investigation  has plan?   else
                                   |                  |          |
                                   |          implement  work-creation
                              investigation    -cycle     -cycle
                                 -cycle
```

**Prerequisite (MUST):**

1. **Retro-Cycle (WORK-142):** Before starting this cycle, **MUST** complete retro-cycle:
   ```
   Skill(skill="retro-cycle")
   ```
   This invocation is owned by `/close` command, not by close-work-cycle itself. retro-cycle structures autonomous reflection into typed, provenance-tagged memory entries (REFLECT->DERIVE->COMMIT->EXTRACT). If retro-cycle returned `dod_relevant_findings`, those are passed to VALIDATE phase.

---

### Lightweight Path (effort=small)

**When:** `/close` command sets `lightweight_close: true` (effort=small + source_files <= 3).

**Replace VALIDATE with inline DoD checklist:**

1. **Pytest gate** (if type=implementation AND source_files contains .py): Run `pytest` — INVARIANT, never skipped
2. **WHY captured**: Check memory_refs populated in WORK.md or retro COMMIT produced concept IDs
3. **Docs current**: If source_files touch CLAUDE.md consumers, prompt. Otherwise N/A.
4. **Traced requirement** (REQ-TRACE-003): Read traces_to, verify deliverables address requirement
5. **Governance events** (soft gate): Grep for work_id in governance-events.jsonl

**If all pass:** Proceed to ARCHIVE (unchanged).
**If any hard gate fails:** BLOCK — revert to full path.

**ARCHIVE and CHAIN proceed normally**, except checkpoint-cycle uses lightweight VERIFY.

---

### 1. VALIDATE Phase

**On Entry:**
```
mcp__haios-operations__cycle_set(cycle="close-work-cycle", phase="VALIDATE", work_id="{work_id}")
```

**Goal:** Verify work item meets Definition of Done criteria.

**Guardrails (MUST follow):**
1. **Tests MUST pass** - Prompt user to confirm
1b. **Pytest Hard Gate (WORK-101, code items only):**
    - If work item has `type: implementation` AND `source_files:` contains `.py` files:
      - **MUST** run `pytest tests/ -v` (or scoped to relevant test files)
      - If any test fails: **BLOCK** closure. Return to DO phase.
      - If no tests exist for changed files: **WARN** (soft gate, not block)
    - If work item is `type: design` or `type: investigation`: Skip pytest gate (N/A).
      Rationale: these types produce documents, not executable artifacts.
    - This gate applies regardless of governance tier (REQ-CEREMONY-005) — Trivial-tier type=implementation items MUST pass pytest at closure. Tier governs within-lifecycle ceremony weight, not closure gates.
2. **WHY MUST be captured** - Check for memory_refs in associated docs
3. **Docs MUST be current** - CLAUDE.md, READMEs updated
4. **Traced files MUST be complete** - Associated plans have status: complete
5. **Traced requirement MUST be addressed** (REQ-TRACE-003) - Verify work item's `traces_to:` requirement was satisfied

**Actions:**
1. Read work file: `docs/work/active/{id}/WORK.md` (or `docs/work/active/WORK-{id}-*.md` for legacy)
2. Check work directory for plans: `docs/work/active/{id}/plans/`
3. Check plan statuses - all must be `complete`
4. For `type: investigation` items: Apply investigation-specific DoD
5. **Validate traced requirement addressed (REQ-TRACE-003):**
   - Read `traces_to:` from work item frontmatter
   - For each requirement ID, verify deliverables demonstrate requirement satisfaction
   - If requirement cannot be verified as addressed, BLOCK closure
6. **Review retro-cycle dod_relevant_findings (WORK-142):**
   - If retro-cycle returned `dod_relevant_findings` (non-empty list), review each finding
   - Evaluate whether any finding should block closure
   - If blocking: report finding to operator, BLOCK closure until addressed
   - If non-blocking: note findings in closure summary
7. **Governance event check (moved from MEMORY phase, E2-108):**
   - Check for cycle events: `grep "{id}" .claude/haios/governance-events.jsonl`
   - If no events found, warn that governance may have been bypassed (soft gate)
8. **Agent UX Test (SHOULD, not MUST — WORK-241):**
   - If work item modified SKILL.md files or ceremony definitions:
     - Check: Are instructions clear and unambiguous for a stateless agent?
     - Check: Do examples match current tool names and patterns?
   - Skip if no ceremony/skill files modified (most closures)
9. Prompt user for DoD confirmation

**Exit Criteria:**
- [ ] Work file exists and has status: active
- [ ] All associated plans have status: complete
- [ ] **MUST:** Traced requirement(s) verified as addressed (REQ-TRACE-003)
- [ ] DoD-relevant findings from retro-cycle reviewed (if any)
- [ ] Governance event check completed (warning if no events)
- [ ] User confirms: tests pass, WHY captured, docs current

**Tools:** Read, Glob, Grep

---

### 2. ARCHIVE Phase

**On Entry:**
```
mcp__haios-operations__cycle_set(cycle="close-work-cycle", phase="ARCHIVE", work_id="{work_id}")
```

> **Execution Context: DELEGATE to haiku subagent (S436 operator directive)**
> ARCHIVE is mechanical: status update, cascade, status propagation. No cognitive context
> required. Delegate to save main-agent tokens. (S436: close-work-cycle-agent ran 68 tool
> calls monolithically; delegation makes this mechanical.)

**Delegation pattern:**
```
Task(
  subagent_type='general-purpose',
  model='haiku',
  prompt='Execute close-work-cycle ARCHIVE phase for {work_id}.
    1. Run: mcp__haios-operations__hierarchy_close_work(work_id="{work_id}")
    2. Verify: work file has status: complete and closed date set
    3. Update associated plans to status: complete
    4. Run StatusPropagator().propagate("{work_id}")
    Report: DONE (archived_path) or FAIL (error).'
)
```

**Goal:** Update work item status to complete.

**Note:** Per ADR-041 "status over location" - work items stay in `docs/work/active/` until epoch cleanup. The `status: complete` field determines state, not directory path.

**Actions:**
1. Run atomic hierarchy_close_work MCP tool:
   ```
   mcp__haios-operations__hierarchy_close_work(work_id="{id}")
   ```
   This atomically performs:
   - Update `status: active` to `status: complete`
   - Update `closed: null` to `closed: {YYYY-MM-DD}`
   - Run cascade (report unblocked items)
   - Clear blocked_by references in downstream WORK.md files (WORK-173, fail-permissive)
   - Run StatusPropagator cascade (absorbed into hierarchy_close_work)

2. Update any associated plans to `status: complete` (if not already)

3. **Run upstream status propagation (WORK-034):**
   ```python
   from status_propagator import StatusPropagator
   result = StatusPropagator().propagate(work_id)
   ```
   This checks if the closed work item's chapter is now complete (all chapter work items done),
   and if so, updates the chapter status row in the parent ARC.md. Also checks arc completion.
   Results: `chapter_completed` (ARC.md updated), `chapter_incomplete` (no change), `no_hierarchy` (no chapter/arc fields), or `arc_completed` (all chapters done).

**Exit Criteria:**
- [ ] `hierarchy_close_work` succeeded
- [ ] Work file has `status: complete` and `closed: {date}`
- [ ] Associated plans marked complete
- [ ] Status propagation executed (chapter/arc status synced)

**Tools:** mcp__haios-operations__hierarchy_close_work, Python(status_propagator)

---

### 3. CHAIN Phase (Post-ARCHIVE)

**On Entry:**
```
mcp__haios-operations__cycle_set(cycle="close-work-cycle", phase="CHAIN", work_id="{work_id}")
```

> **Execution Context: PARTIAL DELEGATE to haiku subagent (S436 operator directive)**
> CHAIN has both mechanical steps (checkpoint, queue query) and interactive steps
> (AskUserQuestion for operator routing). Mechanical steps delegate to haiku; the
> AskUserQuestion MUST remain in main agent context (subagent isolated context cannot
> reliably surface interactive prompts to operator — critique A8).

**Delegation pattern (mechanical steps only):**
```
result = Task(
  subagent_type='general-purpose',
  model='haiku',
  prompt='Execute close-work-cycle CHAIN mechanical steps for {work_id}.
    1. Invoke checkpoint-cycle (Skill(skill="checkpoint-cycle"))
    2. Run: mcp__haios-operations__queue_ready()
    3. Read each ready work item type field
    Report: list of ready items with their types.'
)
# Main agent then presents AskUserQuestion with routing options
# using the haiku result as input. AskUserQuestion stays inline.
```

**Goal:** Checkpoint context then route to next work item.

#### 4a. Checkpoint (MUST - E2-287)

**MUST** invoke checkpoint-cycle before routing to next work:

```
Skill(skill="checkpoint-cycle")
```

**Rationale:** Work complexity within hardened gating system makes context limits per work item likely. Checkpointing after closure ensures context from completed work is preserved before starting new work. Next session picks up with full context of decisions made.

#### 4b. Route to Next Work (REQ-LIFECYCLE-004: Caller Choice)

**Actions:**
1. (Closure already completed in MEMORY phase)
2. (Checkpoint completed in 4a)
3. Query next work: `mcp__haios-operations__queue_ready()`
4. If items returned, read first work file to determine suggested routing
5. Read work item `type` field from WORK.md
6. **Determine suggested action** (WORK-030: type field is authoritative):
   - If `next_work_id` is None → suggest `complete_without_spawn`
   - If `type` == "investigation" → suggest `investigation-cycle`
   - If `has_plan` is True → suggest `implementation-cycle`
   - Else → suggest `work-creation-cycle`

7. **Present options to caller** (REQ-LIFECYCLE-004):

   Use AskUserQuestion to present choices:
   ```
   AskUserQuestion(questions=[{
     "question": "Work closed. What next?",
     "header": "Next Action",
     "options": [
       {"label": "Complete without spawn", "description": "Store output, no next work item"},
       {"label": "Chain to {suggested_cycle}", "description": "Continue with {next_work_id}"},
       {"label": "Select different work", "description": "Choose from queue"}
     ],
     "multiSelect": false
   }])
   ```

8. **Execute chosen action:**
   - `Complete without spawn` → Report "Work complete. No spawn." (valid, no warning)
   - `Chain to {cycle}` → `Skill(skill="{cycle}")`
   - `Select different work` → `Skill(skill="survey-cycle")`

**Note:** "Complete without spawn" is a first-class valid outcome per REQ-LIFECYCLE-004.

**Exit Criteria:**
- [ ] **MUST:** checkpoint-cycle invoked (E2-287)
- [ ] Next work item identified (or none available)
- [ ] Appropriate cycle skill invoked (or awaiting operator)

**On Complete:**
```
mcp__haios-operations__cycle_clear()
```

**Tools:** mcp__haios-operations__queue_ready, Read, Skill(checkpoint-cycle, routing-gate)

---

## Composition Map

| Phase | Primary Tool | Memory Integration |
|-------|--------------|-------------------|
| (Prerequisite) retro-cycle | Skill (invoked by /close) | Typed reflection via REFLECT->DERIVE->COMMIT->EXTRACT |
| VALIDATE | Read, Glob, Grep | dod_relevant_findings from retro-cycle |
| ARCHIVE | mcp__haios-operations__hierarchy_close_work | - |
| CHAIN | Skill (checkpoint-cycle, routing) | Context preservation (E2-287) |

---

## Quick Reference

| Phase | Question to Ask | If NO |
|-------|-----------------|-------|
| (Prerequisite) | retro-cycle completed? | /close must invoke retro-cycle first |
| VALIDATE | Does work file exist? | STOP - not found |
| VALIDATE | Are all plans complete? | STOP or warn user |
| VALIDATE | **Is traced requirement addressed? (REQ-TRACE-003)** | **STOP - requirement not satisfied** |
| VALIDATE | Any DoD-relevant findings from retro-cycle? | Review and evaluate |
| VALIDATE | Governance events exist for work_id? | Warn (soft gate) |
| VALIDATE | Does user confirm DoD? | STOP - DoD not met |
| VALIDATE | **Pytest gate pass? (type=implementation + .py)** | **BLOCK - return to DO** |
| ARCHIVE | Is work file archived? | Run `mcp__haios-operations__hierarchy_close_work(work_id)` |
| CHAIN | Is next work identified? | Run `mcp__haios-operations__queue_ready()` |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Three inline phases | VALIDATE -> ARCHIVE -> CHAIN | WORK-142: MEMORY absorbed by retro-cycle COMMIT |
| retro-cycle as prerequisite | /close invokes retro-cycle before close-work-cycle | WORK-142: Structured reflection with typed provenance replaces observation-capture-cycle |
| Keep command lookup | Skill assumes work item found | Command handles "not found" case before skill |
| Skill documents steps | Command + Skill redundancy | Command is authoritative; skill provides structure |
| Governance check in VALIDATE | Moved from removed MEMORY phase | WORK-142: Consolidates all checks before archive |
| **CHAIN presents options, not auto-executes** | AskUserQuestion for caller choice | WORK-087: REQ-LIFECYCLE-004 "chaining is caller choice" |
| **"Complete without spawn" first-class** | Listed as option 1 | REQ-LIFECYCLE-004: Valid outcome, not exceptional case |
| **Pytest hard gate for code items** | BLOCK closure if tests fail (type=implementation + .py) | WORK-101: REQ-CEREMONY-005 tier-independent closure gate. Design/investigation items exempt (produce docs, not code). |

---

## Related

- **retro-cycle skill:** Prerequisite for structured reflection (WORK-142, replaces observation-capture-cycle)
- **observation-capture-cycle skill:** DEPRECATED, replaced by retro-cycle (WORK-142)
- **observation-triage-cycle skill:** Processes retro-cycle provenance tags (WORK-143)
- **dod-validation-cycle skill:** DEPRECATED (WORK-241) — Agent UX Test absorbed into VALIDATE step 8
- **work-creation-cycle skill:** Parallel workflow for creation
- **implementation-cycle skill:** Parallel workflow for implementation
- **investigation-cycle skill:** Parallel workflow for research
- **ADR-033:** Work Item Lifecycle Governance
- **/close command:** Invokes retro-cycle then this skill
