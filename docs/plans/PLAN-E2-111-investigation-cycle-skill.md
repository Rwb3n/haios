---
template: implementation_plan
status: complete
date: 2025-12-22
backlog_id: E2-111
title: "Investigation Cycle Skill"
author: Hephaestus
lifecycle_phase: plan
session: 97
spawned_by: M4-Research
related: [implementation-cycle, E2-112, E2-113, E2-115]
milestone: M4-Research
enables: [E2-112, E2-113, E2-115]
version: "1.5"
generated: 2025-12-22
last_updated: 2025-12-22T16:53:04
---
# Implementation Plan: Investigation Cycle Skill

@docs/README.md
@docs/epistemic_state.md
@.claude/skills/implementation-cycle/SKILL.md

---

## Goal

Create an investigation-cycle skill that guides HYPOTHESIZE-EXPLORE-CONCLUDE workflow for research work, parallel to how implementation-cycle guides PLAN-DO-CHECK-DONE for implementation work.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | New skill only |
| Lines of code affected | 0 | Documentation-only skill |
| New files to create | 2 | SKILL.md + README.md |
| Tests to write | 0 | Skill is prompt-based (no code) |
| Dependencies | 2 | memory-agent, investigation template |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Skill references existing commands/templates |
| Risk of regression | Low | New skill, no existing code |
| External dependencies | Low | Uses existing memory MCP |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Design skill structure | 30 min | High |
| Write SKILL.md | 30 min | High |
| Verify discovery | 10 min | High |
| **Total** | ~1 hour | High |

---

## Current State vs Desired State

### Current State

**SKIPPED:** New feature - no existing investigation-cycle skill exists.

**Behavior:** Investigations are ad-hoc. No structured workflow guides the HYPOTHESIZE-EXPLORE-CONCLUDE phases.

**Result:** Inconsistent investigation quality, findings may not be stored to memory, spawned work items may be forgotten.

### Desired State

```
.claude/skills/investigation-cycle/
├── SKILL.md      # Skill definition with three phases
└── README.md     # Skill documentation
```

**Behavior:** Agents invoke `Skill(skill="investigation-cycle")` when starting or resuming research work. Skill guides structured workflow with phase-specific tools and exit criteria.

**Result:** Consistent investigation workflow, findings always stored, spawned work properly tracked.

---

## Tests First (TDD)

**SKIPPED:** Skill is prompt-based documentation (no Python code). Verification is manual: skill appears in haios-status-slim.json after discovery.

**Manual Verification:**
```bash
# Verify skill discoverable
just update-status-slim
# Expected: "investigation-cycle" in skills array
```

---

## Detailed Design

### The Investigation Cycle

```
HYPOTHESIZE --> EXPLORE --> CONCLUDE
      ^            ^           |
      |            +-----------+ (if more to explore)
      +-- (if no investigation doc)
```

**Parallel to Implementation Cycle:**

| Implementation | Investigation | Purpose |
|----------------|---------------|---------|
| PLAN | HYPOTHESIZE | Define what to do |
| DO | EXPLORE | Execute the work |
| CHECK | CONCLUDE | Verify and close |
| DONE | (part of CONCLUDE) | Capture learnings |

### Phase 1: HYPOTHESIZE

**Goal:** Verify investigation exists and is ready for exploration.

**Actions:**
1. Read investigation file: `docs/investigations/INVESTIGATION-{backlog_id}-*.md`
2. Verify investigation has filled-in sections (not template placeholders)
3. Check `status: active` - if draft, fill in context/hypotheses first
4. Query memory for prior related work

**Exit Criteria:**
- [ ] Investigation file exists with complete context
- [ ] Hypotheses defined (at least H1)
- [ ] Scope defined (in/out)
- [ ] Memory queried for prior related findings

**Tools:** Read, Glob, memory_search_with_experience

### Phase 2: EXPLORE

**Goal:** Execute investigation steps and document findings.

**Guardrails (SHOULD follow):**
1. **One hypothesis at a time** - Focus exploration
2. **Document findings as discovered** - Don't wait until end
3. **Query memory before assuming** - Prior work may answer questions

**Actions:**
1. Execute investigation steps from document
2. For each step, update Findings section
3. Use memory-agent for context before deep dives
4. If new hypotheses emerge, add them to document

**Exit Criteria:**
- [ ] All investigation steps executed
- [ ] Findings section populated with evidence
- [ ] Hypotheses marked as confirmed/refuted/inconclusive

**Tools:** Read, Grep, Glob, Bash, memory_search_with_experience, WebSearch (if needed)

### Phase 3: CONCLUDE

**Goal:** Synthesize findings and spawn work items.

**Actions:**
1. Review findings against original objective
2. Identify spawned work items (ADRs, backlog items, new investigations)
3. Create spawned items using `/new-*` commands with `spawned_by: {this_investigation_id}`
4. Store findings summary to memory via `ingester_ingest`
5. Update investigation status: `status: complete`
6. Close investigation: `/close {backlog_id}`

**Exit Criteria:**
- [ ] Findings synthesized (answer to objective documented)
- [ ] Spawned work items created with `spawned_by` field linking to investigation
- [ ] Learnings stored to memory (memory_refs populated)
- [ ] Investigation marked complete

**Tools:** ingester_ingest, Edit, /new-adr, /new-plan, /close

**Future Integration (E2-113):** Phase transitions (HYPOTHESIZE→EXPLORE→CONCLUDE) will emit events to haios-events.jsonl when E2-113 is implemented.

### Composition Map

| Phase | Primary Tool | Memory Integration | Command |
|-------|--------------|-------------------|---------|
| HYPOTHESIZE | Read, Glob | memory_search (prior work) | /new-investigation |
| EXPLORE | Grep, Read, Bash | memory_search (context) | - |
| CONCLUDE | Edit, Write | ingester_ingest (findings) | /close |

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Three phases not four | CONCLUDE combines CHECK+DONE | Investigations don't have a separate verification step |
| No TDD requirement | Investigations produce findings, not code | Research is exploratory, not constructive |
| Memory query at start | HYPOTHESIZE includes prior work check | Avoid re-investigating solved problems |
| Spawned work items | Required exit criterion | Investigations should produce actionable output |

### Quick Reference

| Phase | Question to Ask | If NO |
|-------|-----------------|-------|
| HYPOTHESIZE | Is investigation ready? | Fill in context/hypotheses |
| EXPLORE | Are all steps executed? | Continue exploration |
| EXPLORE | Are findings documented? | Update Findings section |
| CONCLUDE | Are spawned items created? | Create via /new-* |
| CONCLUDE | Are learnings stored? | Run ingester_ingest |

---

## Implementation Steps

### Step 1: Create Skill Directory
- [ ] Create `.claude/skills/investigation-cycle/` directory

### Step 2: Write SKILL.md
- [ ] Create `.claude/skills/investigation-cycle/SKILL.md` with:
  - Frontmatter (name, description)
  - When to Use section
  - The three-phase cycle with diagrams
  - Phase details (Goal, Actions, Exit Criteria, Tools)
  - Composition Map
  - Quick Reference table

### Step 3: Create README.md
- [ ] Create `.claude/skills/investigation-cycle/README.md`

### Step 4: Verify Discovery
- [ ] Run `just update-status-slim`
- [ ] Verify `investigation-cycle` appears in skills array
- [ ] Test invocation: `Skill(skill="investigation-cycle")`

### Step 5: README Sync (MUST)
- [ ] **MUST:** Create `.claude/skills/investigation-cycle/README.md`
- [ ] **MUST:** Update `.claude/skills/README.md` if it exists

### Step 6: Consumer Verification (MUST for migrations/refactors)

**SKIPPED:** New skill creation, not a migration.

---

## Verification

- [ ] SKILL.md created with complete content
- [ ] README.md created
- [ ] Skill appears in `haios-status-slim.json` after `just update-status-slim`
- [ ] `/validate` passes on SKILL.md (if template exists)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Skill not discovered | Medium | Verify frontmatter format matches existing skills |
| Too rigid for exploration | Low | Exit criteria are guidelines, not gates |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 97 | 2025-12-22 | - | Plan drafted | Design complete |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/investigation-cycle/SKILL.md` | Complete skill definition | [ ] | |
| `.claude/skills/investigation-cycle/README.md` | Skill documentation | [ ] | |
| `.claude/haios-status-slim.json` | Contains "investigation-cycle" | [ ] | |

**Verification Commands:**
```bash
# Verify skill discoverable
just update-status-slim
cat .claude/haios-status-slim.json | grep investigation-cycle
# Expected: "investigation-cycle" in skills array
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] N/A - no pytest tests (skill is documentation)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- **implementation-cycle skill:** `.claude/skills/implementation-cycle/SKILL.md` - Pattern to follow
- **Investigation template:** `.claude/templates/investigation.md` - Document structure
- **Memory concepts:** 72320 (implementation-cycle), 54752/55181 (investigation structure)
- **Backlog:** E2-111 (this item), enables E2-112, E2-113, E2-115
- **E2-115 DoD alignment:** CONCLUDE phase exit criteria match E2-115 DoD ("findings documented, spawns created and linked")
- **E2-110 complete:** Spawn field governance done - E2-114 should be unblocked (stale blocker in backlog)
- **Real investigation example:** `docs/investigations/INVESTIGATION-INV-020-llm-energy-channeling-patterns.md`

---
