---
template: work_item
id: WORK-094
title: HAIOS Portability Architecture Investigation
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-03
spawned_by: Session-297-stakeholder-review
chapter: null
arc: portability
closed: '2026-02-03'
priority: high
effort: medium
traces_to:
- REQ-PORTABLE-001
- REQ-PORTABLE-002
- REQ-PORTABLE-003
requirement_refs: []
source_files:
- .claude/haios/lib/scaffold.py
- .claude/haios/config/haios.yaml
- .claude/templates/
acceptance_criteria:
- All hardcoded paths identified and catalogued
- Template seed/runtime pattern designed
- Init ceremony specification complete
- L4 requirement gaps identified (if any)
- Chapter structure for portability arc proposed
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-03 20:02:00
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 83342
- 83343
- 83344
- 83345
- 83351
- 83352
- 83353
- 83354
- 83355
- 83356
- 83357
- 83358
- 83359
- 83360
- 83361
- 83362
- 83363
- 83366
- 83367
- 83368
- 83369
- 83370
- 83371
- 83372
extensions:
  epoch: E2.5
  investigation_type: architecture
version: '2.0'
generated: 2026-02-03
last_updated: '2026-02-03T20:15:04'
---
# WORK-094: HAIOS Portability Architecture Investigation

---

## Context

During Session 297 E2.5 decomposition review, stakeholder raised portability concerns:

> "Can we verify that the templates folder will be migrated to haios/ for portability? With all dependencies and consumers considered?"

This led to a broader discussion about HAIOS as a distributable plugin.

### The Core Problem

HAIOS has **hardcoded paths** throughout the codebase that prevent clean plugin distribution:

| File | Hardcoded Path | Issue |
|------|----------------|-------|
| `scaffold.py:266` | `.claude/templates/` | Templates not in portable `haios/` |
| `cascade.py:43-44` | `.claude/haios-status.json` | Status files hardcoded |
| `dependencies.py:22-23` | `.claude/skills`, `.claude/agents` | Plugin structure hardcoded |
| `audit_decision_coverage.py:306-307` | `.claude/haios/epochs/E2_4/` | **BUG: hardcoded epoch** |

### Proposed Pattern: Seed + Runtime

```
.claude/haios/templates/    # SEED (source of truth, travels with plugin)
.claude/templates/          # RUNTIME (copied on init, customizable)
```

Init ceremony copies seed → runtime on first use, allowing:
- Plugin carries canonical templates
- Operators can customize runtime
- Upgrades can diff seed vs runtime

---

## Objective

Investigate and design the portability architecture for HAIOS as a distributable Claude Code plugin.

---

## Questions to Answer

1. **Hardcoded Paths:** What paths are hardcoded that should be configurable?
2. **Template Location:** Should templates live in `haios/templates/` (seed) vs `.claude/templates/` (runtime)?
3. **Init Ceremony:** What initialization ceremony is needed for fresh installs?
4. **L4 Requirements:** Are there portability requirements in L4? Should we add REQ-PORTABLE-*?
5. **Plugin Distribution:** What's the distribution model (git submodule, npm, copy)?
6. **Upgrade Path:** How do users upgrade when seed templates change?
7. **Arc Structure:** What chapters should the portability arc contain?

---

## Deliverables

- [x] Complete hardcoded path audit (7 files, 17 occurrences identified)
- [x] Template seed/runtime architecture design document
- [x] Init ceremony specification (inputs, outputs, idempotency)
- [x] L4 requirement proposal (REQ-PORTABLE-001 to 003)
- [x] Portability arc chapter structure proposal (CH-028 to CH-031)
- [ ] Migration plan for existing HAIOS installations (deferred to implementation)

---

## Session 297 Discussion Context

### Stakeholder Input

1. "Templates/ are not a Claude Code convention, we created that folder"
2. "Are there other hardcoded constants that could be moved to configurability?"
3. "If we do keep templates in .claude/ can we have a haios/template/ folder as an init seed directory?"
4. "work-xxx type investigation. explore > investigation > append to epoch2.5 > append to arcs > more chapters?"

### Agent Analysis

**Arguments FOR Migration to haios/:**
- Plugin portability (templates travel with plugin)
- Single source of truth
- ConfigLoader pattern already exists

**Arguments AGAINST:**
- Breaking change (many file references)
- `.claude/templates/` is current runtime location

**Hybrid Solution Proposed:**
- Seed in `haios/templates/` (canonical)
- Runtime in `.claude/templates/` (customizable)
- Init ceremony bridges them

---

---

## Investigation Findings (Session 298)

### Hypothesis Verdicts

| ID | Hypothesis | Verdict | Confidence |
|----|------------|---------|------------|
| H1 | HAIOS fails portability test | **CONFIRMED** | 95% |
| H2 | Hardcoded paths violate REQ-CONFIG-001 | **CONFIRMED** | 95% |
| H3 | Seed/Runtime pattern is correct | **CONFIRMED** | 80% |
| H4 | No init ceremony exists | **CONFIRMED** | 95% |

### Hardcoded Path Audit Results

| File | Occurrences | Key Paths |
|------|-------------|-----------|
| `scaffold.py` | 4 | `.claude/templates/`, status files |
| `status.py` | 4 | agents/, skills/, commands/ |
| `cascade.py` | 3 | status.json, events.jsonl |
| `dependencies.py` | 2 | skills/, agents/ |
| `audit_decision_coverage.py` | 2 | **BUG: E2_4 hardcoded** |
| `work_loader.py` | 1 | haios.yaml path |
| `audit.py` | 1 | status.json |
| **Total** | **17** | |

ConfigLoader usage: 8 occurrences across 3 files (work_engine.py, context_loader.py, config.py)

### Architecture Decision: Seed + Runtime

```
.claude/haios/                  ← SEED (portable, canonical)
├── templates/, skills/, agents/, hooks/, commands/

.claude/                        ← RUNTIME (project-specific)
├── templates/, skills/, agents/, hooks/, commands/
```

**Init Ceremony Flow:**
1. Check: Does runtime exist?
2. NO → Copy seed → runtime for each component
3. YES → Diff seed vs runtime, report changes
4. Create: haios-status.json, session file
5. Validate: All dependencies present

### Proposed L4 Requirements

| ID | Requirement | Derives From |
|----|-------------|--------------|
| REQ-PORTABLE-001 | All component paths via ConfigLoader | L3.6, REQ-CONFIG-001 |
| REQ-PORTABLE-002 | Init ceremony for fresh installs | L3.6 |
| REQ-PORTABLE-003 | Seed in haios/, runtime in .claude/ | L3.6, Portability Test |

### Proposed Chapters for Portability Arc

| CH-ID | Title | Requirements | Dependencies |
|-------|-------|--------------|--------------|
| CH-028 | PathConfigMigration | REQ-PORTABLE-001 | None |
| CH-029 | SeedStructure | REQ-PORTABLE-003 | CH-028 |
| CH-030 | InitCeremony | REQ-PORTABLE-002 | CH-029 |
| CH-031 | UpgradePath | REQ-PORTABLE-002 | CH-030 |

---

## History

### 2026-02-03 - Completed (Session 298)
- Investigation complete with 4 hypotheses validated
- Hardcoded path audit: 17 occurrences across 7 files
- Architecture decision: Seed + Runtime pattern
- L4 requirements proposed: REQ-PORTABLE-001 to 003
- Chapters proposed: CH-028 to CH-031
- Arc updated with findings

### 2026-02-03 - Created (Session 297)
- Spawned from stakeholder review during E2.5 decomposition
- Created portability arc stub
- Added to E2.5 active_arcs

---

## References

- @.claude/haios/epochs/E2_5/arcs/portability/ARC.md
- @.claude/haios/config/haios.yaml (paths section)
- @.claude/haios/lib/scaffold.py (template consumer)
- Memory refs: 83342-83345 (Session 297 decomposition learnings)
