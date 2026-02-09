---
template: work_item
id: WORK-111
title: Ceremony Contract Schema Design
type: design
status: complete
owner: Hephaestus
created: 2026-02-09
spawned_by: null
chapter: ceremonies/CH-011
arc: ceremonies
closed: 2026-02-09
priority: high
effort: small
traces_to:
- REQ-CEREMONY-002
requirement_refs: []
source_files: []
acceptance_criteria:
- Contract YAML schema defined with input_contract, output_contract, side_effects,
  category fields
- Ceremony registry (YAML) listing all 19 ceremonies with category, skill path, and
  contract status
- Schema documented in ceremony template file
blocked_by: []
blocks:
- WORK-112
- WORK-113
enables:
- WORK-112
- WORK-113
queue_position: done
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-09 22:19:48
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 84249
- 84251
- 84263
- 84264
extensions:
  epoch: E2.5
version: '2.0'
generated: 2026-02-09
last_updated: '2026-02-09T22:46:08.504359'
---
# WORK-111: Ceremony Contract Schema Design

---

## Context

CH-011 (CeremonyContracts) requires all 19 ceremonies to have machine-readable contracts in YAML frontmatter. Currently, zero ceremonies have formal contracts — 11 have skill files with markdown-table contracts but no YAML frontmatter schema (memory 84249).

This work item defines the contract schema itself and creates a persistent ceremony registry so future sessions don't need to re-discover ceremony state (memory 84251 — survey cost was 60 tool calls, 190s, 80K tokens).

**Scope:** Design only. No skill file edits. No validation code.

---

## Deliverables

- [ ] Contract YAML schema definition (fields, types, required/optional, examples)
- [ ] Ceremony registry file (`.claude/haios/config/ceremony_registry.yaml`) listing all 19 ceremonies
- [ ] Ceremony skill template (`.claude/templates/ceremony/SKILL.md`) using the schema

---

## History

### 2026-02-09 - Created (Session 332)
- Spawned from ceremonies arc survey (CH-011 decomposition)
- 1 of 3 work items for CH-011: schema → retrofit → validation

---

## References

- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-011-CeremonyContracts.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-002)
- @.claude/skills/queue-commit/SKILL.md (reference implementation with markdown contracts)
