---
name: investigation-cycle
description: HAIOS Investigation Cycle for structured research and discovery. Use
  when starting or resuming an investigation. Guides EXPLORE->HYPOTHESIZE->VALIDATE->CONCLUDE
  workflow with phase-specific tooling.
recipes:
- inv
generated: 2025-12-22
last_updated: '2026-02-01T21:21:47'
---
# Investigation Cycle

This skill defines the EXPLORE-HYPOTHESIZE-VALIDATE-CONCLUDE cycle for structured investigation of research questions. It composes existing primitives (Skills, Commands, Memory) into a coherent research workflow.

## When to Use

**SHOULD** invoke this skill when:
- Starting a new investigation
- Resuming work on an in-progress investigation
- Unsure of next step in research workflow

**Invocation:** `Skill(skill="investigation-cycle")`

---

## The Cycle

```
EXPLORE --> HYPOTHESIZE --> VALIDATE --> CONCLUDE --> CHAIN
    |            |             |            |           |
    |            |             |            |     [route next]
    |            |             |            |           |
  evidence    synthesize     verdicts    spawns   /-------------\
  gathering   hypotheses    per hypo    + memory  |             |
                                                type=inv    has plan?
                                                  |            |
                                            investigation  implement
                                               -cycle       -cycle
```

**E2.4 EXPLORE-FIRST Pattern:**

| Phase | Purpose | State |
|-------|---------|-------|
| EXPLORE | Gather evidence before forming hypotheses | EXPLORE |
| HYPOTHESIZE | Synthesize hypotheses FROM evidence | DESIGN |
| VALIDATE | Test each hypothesis against evidence | CHECK |
| CONCLUDE | Synthesize findings, spawn work, store memory | DONE |

**Parallel to Implementation Cycle:**

| Implementation | Investigation | Purpose |
|----------------|---------------|---------|
| PLAN | EXPLORE + HYPOTHESIZE | Define what to investigate |
| DO | (exploration done in EXPLORE) | - |
| CHECK | VALIDATE | Verify hypotheses |
| DONE | CONCLUDE | Capture and close |

---

### 1. EXPLORE Phase

**On Entry:**
```bash
just set-cycle investigation-cycle EXPLORE {work_id}
```

**Goal:** Gather evidence through unrestricted exploration before forming hypotheses.

**Actions:**
1. Read work file: `docs/work/active/{backlog_id}/WORK.md`
2. **MUST read ALL @ referenced files** at document top before proceeding
3. **MUST Glob referenced directories** to find all files (e.g., `@docs/work/active/INV-052/` → `Glob("docs/work/active/INV-052/**/*.md")`)
4. Query memory for prior related work: `memory_search_with_experience`
5. Explore freely: Read files, search codebase, fetch web content
6. Document evidence as discovered (no rigid format required)

**Governed Activities (EXPLORE state):**
- file-read: allow
- content-search: allow
- file-search: allow
- web-fetch: allow
- web-search: allow
- memory-search: allow
- file-write: warn (prefer notes over artifacts)

**Key Insight (Session 262, WORK-036):** Unrestricted exploration produces deeper analysis than constrained subagent invocation. Main agent explores freely; investigation-agent invocation is OPTIONAL.

**Exit Criteria:**
- [ ] Work file read with complete context
- [ ] **MUST:** All @ referenced files read
- [ ] Memory queried for prior related work
- [ ] Evidence documented (free-form notes acceptable)
- [ ] Sources examined are logged

**Tools:** Read, Glob, Grep, WebSearch, WebFetch, memory_search_with_experience

---

### 2. HYPOTHESIZE Phase

**On Entry:**
```bash
just set-cycle investigation-cycle HYPOTHESIZE {work_id}
```

**Goal:** Form hypotheses FROM the gathered evidence.

**Actions:**
1. Review evidence collected in EXPLORE phase
2. Synthesize 2-4 hypotheses that explain or address the objective
3. **MUST cite evidence** for each hypothesis
4. Define test method for each hypothesis (how will VALIDATE phase verify it?)
5. Define scope (In Scope / Out of Scope)

**Governed Activities (DESIGN state):**
- file-read: allow
- file-write: allow
- file-edit: allow
- memory-search: allow
- web-fetch: blocked (no new research - use EXPLORE evidence)
- web-search: blocked (no new research)

**Key Insight:** Hypotheses form AFTER exploration, not before. This is the inversion from the old HYPOTHESIZE-first pattern.

**Exit Criteria:**
- [ ] Hypotheses table populated with 2-4 hypotheses
- [ ] Each hypothesis has evidence citations
- [ ] Each hypothesis has defined test method
- [ ] Scope defined (in/out)
- [ ] Confidence level assigned to each hypothesis

**Tools:** Read, Edit, Write

---

### 3. VALIDATE Phase

**On Entry:**
```bash
just set-cycle investigation-cycle VALIDATE {work_id}
```

**Goal:** Test each hypothesis against the gathered evidence.

**Actions:**
1. For each hypothesis, review supporting/refuting evidence
2. Render verdict: Confirmed / Refuted / Inconclusive
3. Assign confidence level to each verdict
4. **MUST cite specific evidence** for each verdict
5. Document any unexpected findings

**Governed Activities (CHECK state):**
- file-read: allow
- content-search: allow
- memory-search: allow
- shell-execute: allow (for verification commands)
- file-write: warn (verdicts only)
- web-fetch: blocked (no new research)

**Key Insight:** VALIDATE is focused review, not exploration. Evidence already exists from EXPLORE phase. No new evidence gathering.

**Exit Criteria:**
- [ ] All hypotheses have verdict (Confirmed/Refuted/Inconclusive)
- [ ] All verdicts have confidence level
- [ ] All verdicts cite supporting evidence
- [ ] Hypothesis Verdicts table complete

**Tools:** Read, Grep, memory_search_with_experience

---

### 4. CONCLUDE Phase

**On Entry:**
```bash
just set-cycle investigation-cycle CONCLUDE {work_id}
```

**Goal:** Synthesize findings, spawn work items, and reconcile epoch artifacts.

**Actions:**
1. Review findings against original objective
2. Synthesize answer to the investigation question
3. Identify spawned work items (ADRs, backlog items, new investigations)
4. Create spawned items using `/new-*` commands with `spawned_by: {this_investigation_id}`
5. **Epoch Artifact Reconciliation (MUST - Session 276)** - see below
6. Store findings summary to memory via `ingester_ingest`
7. Update investigation status: `status: complete`
8. Populate `memory_refs` in work item frontmatter

#### 4a. Epoch Artifact Reconciliation (MUST)

Investigations reveal ground truth. Before closing, reconcile findings with epoch structure:

**Step 1: Check related chapters**

For each chapter referenced in work item (`chapter:` field or `@` references):

| If findings show... | Then update chapter... |
|---------------------|------------------------|
| Chapter questions answered | `status: Complete` |
| Implementation exists and is correct | `status: Complete` + add evidence |
| Implementation exists but is wrong/suboptimal | `status: Implemented-Deficient` + document deficiencies + link remediation work |
| Chapter premise was wrong | `status: Invalid` + document why |

**Step 2: Check related arc**

- If new chapter needed → Add to arc chapters table
- If investigation adds to arc theme → Update arc with findings summary
- Add memory_refs from this investigation

**Step 3: Check epoch**

- If investigation introduces new decision → Add to EPOCH.md decisions section
- If investigation marks exit criteria complete → Update EPOCH.md checklist
- Add memory_refs from this investigation

**Rationale (Session 276):** WORK-065/WORK-016 revealed that without this step, chapters stay "Planned" after code exists, findings get buried in WORK.md files, and epoch artifacts drift from reality. Investigations are the natural audit point.

**Governed Activities (DONE state):**
- file-read: allow
- file-write: allow
- memory-store: allow
- skill-invoke: allow

**Exit Criteria:**
- [ ] Findings synthesized (answer to objective documented)
- [ ] Spawned work items created with `spawned_by` field linking to investigation
- [ ] **MUST:** Epoch artifacts reconciled (chapters, arc, epoch updated if applicable)
- [ ] Learnings stored to memory (`ingester_ingest` called)
- [ ] `memory_refs` populated in work item frontmatter
- [ ] Investigation marked complete

**Tools:** ingester_ingest, Edit, /new-adr, /new-plan, /new-work

---

### 5. CHAIN Phase (Post-CONCLUDE)

**On Entry:**
```bash
just set-cycle investigation-cycle CHAIN {work_id}
```

**Goal:** Close investigation and route to next work item.

**Actions:**
1. Close investigation: `/close {backlog_id}`
2. Query next work: `just ready`
3. If items returned, read first work file to check `documents.plans`
4. Read work item `type` field from WORK.md
5. **Apply routing decision table** (see `routing-gate` skill):
   - If `next_work_id` is None → `await_operator`
   - If `type` == "investigation" OR ID starts with `INV-` → `invoke_investigation`
   - If `has_plan` is True → `invoke_implementation`
   - Else → `invoke_work_creation`
6. Execute the action:
   - `invoke_investigation` -> `Skill(skill="investigation-cycle")`
   - `invoke_implementation` -> `Skill(skill="implementation-cycle")`
   - `invoke_work_creation` -> `Skill(skill="work-creation-cycle")`
   - `await_operator` -> Report "No unblocked work. Awaiting operator direction."

**MUST:** Do not pause for acknowledgment - execute routing immediately.

**Exit Criteria:**
- [ ] Investigation closed via /close
- [ ] Next work item identified (or none available)
- [ ] Appropriate cycle skill invoked (or awaiting operator)

**On Complete:**
```bash
just clear-cycle
```

**Tools:** /close, Bash(just ready), Read, Skill(routing-gate)

---

## Composition Map

| Phase | Primary Tool | Memory Integration | Command |
|-------|--------------|-------------------|---------|
| EXPLORE | Read, Glob, Grep, WebSearch | memory_search (prior work) | /new-investigation |
| HYPOTHESIZE | Read, Edit | - | - |
| VALIDATE | Read, Grep | memory_search (verify patterns) | - |
| CONCLUDE | Edit, Write | ingester_ingest (findings) | - |
| CHAIN | Bash, Skill | - | /close |

---

## Quick Reference

| Phase | Question to Ask | If NO |
|-------|-----------------|-------|
| EXPLORE | Is evidence gathered? | Continue exploring freely |
| EXPLORE | Memory queried? | Run memory_search_with_experience |
| HYPOTHESIZE | Are hypotheses formed from evidence? | Synthesize from EXPLORE notes |
| HYPOTHESIZE | Does each hypothesis cite evidence? | Add citations |
| VALIDATE | Do all hypotheses have verdicts? | Review evidence, render verdict |
| VALIDATE | Are verdicts supported by evidence? | Cite specific sources |
| CONCLUDE | Are findings synthesized? | Write answer to objective |
| CONCLUDE | Are spawned items created? | Create via /new-* commands |
| CONCLUDE | **Are epoch artifacts reconciled?** | **Update chapters/arc/epoch per findings** |
| CONCLUDE | Are learnings stored? | Run ingester_ingest |
| CHAIN | Is investigation closed? | Run /close {backlog_id} |
| CHAIN | Is next work identified? | Run `just ready` |

**EXPLORE phase principles:**
- Explore freely before constraining with hypotheses
- Query memory for prior work early
- Document sources as you go

**HYPOTHESIZE phase principles:**
- Hypotheses form FROM evidence, not before
- Each hypothesis must cite supporting evidence
- Define how each will be tested

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Four phases not three | EXPLORE→HYPOTHESIZE→VALIDATE→CONCLUDE | Separates evidence gathering from hypothesis testing |
| EXPLORE-FIRST | Evidence before hypotheses | Session 262 showed unrestricted exploration produces depth |
| No MUST investigation-agent | Main agent explores freely | Subagent constraint limited discovery in prior pattern |
| VALIDATE as separate phase | Focused verdict-rendering | Separates synthesis (HYPOTHESIZE) from verification (VALIDATE) |
| Memory query at start | EXPLORE includes prior work check | Avoid re-investigating solved problems |
| Spawned work items | Required exit criterion | Investigations should produce actionable output |
| Epoch artifact reconciliation | MUST in CONCLUDE phase | Session 276: Without this, chapters stay "Planned" after code exists, findings buried in WORK.md |

---

## Phase Templates

For detailed phase guidance, see fractured templates:

| Phase | Template |
|-------|----------|
| EXPLORE | `.claude/templates/investigation/EXPLORE.md` |
| HYPOTHESIZE | `.claude/templates/investigation/HYPOTHESIZE.md` |
| VALIDATE | `.claude/templates/investigation/VALIDATE.md` |
| CONCLUDE | `.claude/templates/investigation/CONCLUDE.md` |

Each template defines:
- Input Contract (what must exist before starting)
- Governed Activities (from activity_matrix.yaml)
- Output Contract (what must be produced)

---

## Related

- **implementation-cycle skill:** Parallel workflow for implementation tasks
- **Investigation template:** `.claude/templates/investigation.md` (monolithic, deprecated)
- **Fractured templates:** `.claude/templates/investigation/` (preferred)
- **ADR-033:** Work Item Lifecycle (DoD criteria)
- **/new-investigation command:** Creates investigation documents
- **/close command:** Closes completed investigations
- **WORK-037:** Investigation that designed this EXPLORE-FIRST pattern
- **WORK-061:** Implementation of EXPLORE-FIRST pattern
