---
template: work_item
id: WORK-094
title: HAIOS Portability Architecture Investigation
type: investigation
status: active
owner: Hephaestus
created: 2026-02-03
spawned_by: Session-297-stakeholder-review
chapter: null
arc: portability
closed: null
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
extensions:
  epoch: E2.5
  investigation_type: architecture
version: '2.0'
generated: 2026-02-03
last_updated: '2026-02-03T20:02:30'
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

- [ ] Complete hardcoded path audit (all files in haios/lib, haios/modules, hooks/)
- [ ] Template seed/runtime architecture design document
- [ ] Init ceremony specification (inputs, outputs, idempotency)
- [ ] L4 requirement proposal (REQ-PORTABLE-001 to 003)
- [ ] Portability arc chapter structure proposal
- [ ] Migration plan for existing HAIOS installations

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

## History

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
