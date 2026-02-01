---
template: work_item
id: WORK-043
title: CH-001 InvestigationFracture - Split Monolithic Template
type: design
status: complete
owner: Hephaestus
created: 2026-01-30
spawned_by: null
chapter: CH-001
arc: templates
closed: '2026-02-01'
priority: high
effort: medium
traces_to:
- REQ-TEMPLATE-001
- REQ-TEMPLATE-002
- REQ-FLOW-002
requirement_refs: []
source_files:
- .claude/templates/investigation.md
acceptance_criteria:
- Investigation template fractured into 4 phase files (EXPLORE, HYPOTHESIZE, VALIDATE,
  CONCLUDE)
- Each phase template has Input Contract and Output Contract sections
- Each phase template is 30-50 lines (not exceeding 100)
- Phase templates reference governed activities from activity_matrix.yaml
blocked_by: []
blocks: []
enables:
- WORK-044
- WORK-046
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-30 21:50:40
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82724
- 82725
- 82726
- 82727
- 82728
- 82838
- 82856
- 82857
- 82858
- 82859
- 82860
- 82861
- 82862
- 82863
- 82868
- 82869
extensions: {}
version: '2.0'
generated: 2026-01-30
last_updated: '2026-02-01T15:29:20'
---
# WORK-043: CH-001 InvestigationFracture - Split Monolithic Template

---

## Context

**Problem:** The current investigation template (`.claude/templates/investigation.md`) is 369 lines with 25 MUST gates and 27 checkboxes. This "Template Tax" (WORK-036) creates cognitive overload and couples unrelated phases. Agents must scroll through irrelevant sections for their current phase.

**Root Cause:** Template was designed for documentation completeness, not phase-aware guidance. All phases live in one file, forcing agents to mentally filter to their current phase.

**E2.4 Decision (Session 265):** Fracture monolithic templates into phase-specific files with explicit input/output contracts. Each phase template should be ~30-50 lines and reference the governed activities allowed in that phase.

**Target Structure:**
```
.claude/templates/investigation/
├── EXPLORE.md        (~40 lines)
├── HYPOTHESIZE.md    (~40 lines)
├── VALIDATE.md       (~40 lines)
└── CONCLUDE.md       (~40 lines)
```

**Contract Pattern (from Templates arc):**
```markdown
# {PHASE} Phase

## Input Contract
- [ ] {What must exist before this phase}

## Governed Activities
- {activity-1}, {activity-2}

## Output Contract
- [ ] {What must exist after this phase}

## Template
{Minimal structure for outputs}
```

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning)

     These checkboxes are the SOURCE OF TRUTH for work completion.

     During CHECK phase of implementation-cycle:
     - Agent MUST read this section
     - Agent MUST verify EACH checkbox can be marked complete
     - If ANY deliverable is incomplete, work is NOT done

     "Tests pass" ≠ "Deliverables complete"
     Tests verify code works. Deliverables verify scope is complete.

     NOTE (WORK-001): Acceptance criteria are in frontmatter (machine-parseable).
     Deliverables are implementation outputs, not requirements.
-->

- [x] **EXPLORE.md** - Phase template with input contract (work item exists), output contract (evidence documented), governed activities (explore-read, explore-search, explore-memory, capture-notes)
- [x] **HYPOTHESIZE.md** - Phase template with input contract (evidence gathered), output contract (hypotheses stated with test methods), governed activities (requirements-read, hypothesis-write)
- [x] **VALIDATE.md** - Phase template with input contract (hypotheses defined), output contract (verdicts for each hypothesis), governed activities (test-execute, verdict-write)
- [x] **CONCLUDE.md** - Phase template with input contract (verdicts documented), output contract (spawned work, memory stored), governed activities (conclusion-write, memory-store, spawn-work)
- [x] **CH-001-InvestigationFracture.md** - Chapter file documenting the design decisions
- [x] **Memory stored** - Design decisions ingested to memory with WHY captured (82856-82863)

---

## History

### 2026-01-30 - Created (Session 247)
- Initial scaffold

### 2026-02-01 - Populated (Session 271)
- Added context linking to Templates arc, WORK-036 Template Tax investigation
- Defined 6 deliverables: 4 phase templates + chapter file + memory
- Linked to REQ-TEMPLATE-001, REQ-TEMPLATE-002, REQ-FLOW-002
- Added memory_refs to Session 265 fractured templates decisions (82724-82728)

---

## References

- @.claude/haios/epochs/E2_4/arcs/templates/ARC.md
- @.claude/haios/epochs/E2_4/EPOCH.md (Decision 6: Fractured Templates)
- @.claude/templates/investigation.md (current monolithic - 369 lines)
- @docs/work/active/WORK-036/ (Template Tax investigation)
- @.claude/haios/config/activity_matrix.yaml (governed activities)
