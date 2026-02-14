---
template: work_item
id: WORK-147
title: "Implement Schema Registry and ConfigLoader Extension"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-14
spawned_by: WORK-067
spawned_children: []
chapter: CH-036
arc: referenceability
closed: null
priority: medium
effort: medium
traces_to:
- REQ-REFERENCE-002
requirement_refs: []
source_files:
- .claude/haios/lib/config.py
- .claude/haios/lib/scaffold.py
- .claude/haios/lib/validate.py
acceptance_criteria:
- Schema registry directory exists at .claude/haios/schemas/ with core/ and project/ subdirectories
- ConfigLoader gains schemas property and get_schema(domain, key) method
- At least one core schema file (work_item.yaml) populated with authoritative enums
- substitute_variables() resolves {{schema:domain.key}} references
- haios.yaml paths section includes schemas entry
- Existing tests pass (no regressions)
blocked_by: []
blocks: []
enables:
- WORK-135
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-14T14:09:54
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-14
last_updated: 2026-02-14T14:09:54
---
# WORK-147: Implement Schema Registry and ConfigLoader Extension

---

## Context

**Problem:** WORK-067 investigation found 46 distinct enum/schema definitions scattered across 8 file categories with no centralized registry. REQ-REFERENCE-002 requires "templates MUST consume schemas via reference, not duplication."

**Solution (from WORK-067 findings):** Create a central schema registry at `.claude/haios/schemas/` with two tiers (core/ for portable enums, project/ for HAIOS-specific), extend ConfigLoader with schema access, and extend scaffold.py to resolve `{{schema:domain.key}}` references.

---

## Deliverables

- [ ] Create `.claude/haios/schemas/core/work_item.yaml` with status, type, priority, effort enums
- [ ] Create `.claude/haios/schemas/core/queue.yaml` with queue_position, queue_types, transitions
- [ ] Create `.claude/haios/schemas/core/lifecycle.yaml` with cycle_phase, lifecycles, transitions
- [ ] Create `.claude/haios/schemas/project/` directory (initially empty, structure only)
- [ ] Add `schemas: ".claude/haios/schemas"` to haios.yaml paths section
- [ ] Extend ConfigLoader with `schemas` property and `get_schema(domain, key)` method
- [ ] Extend `substitute_variables()` to resolve `{{schema:domain.key}}` syntax
- [ ] Tests for ConfigLoader schema loading and get_schema()
- [ ] Tests for substitute_variables() schema resolution

---

## History

### 2026-02-14 - Created (Session 367)
- Spawned from WORK-067 investigation CONCLUDE phase
- Implements schema registry architecture defined in WORK-067 findings
- Serves REQ-REFERENCE-002 and E2.6 referenceability exit criteria

---

## References

- @docs/work/active/WORK-067/WORK.md (investigation findings — schema architecture)
- @.claude/haios/lib/config.py (ConfigLoader — extension target)
- @.claude/haios/lib/scaffold.py (substitute_variables — extension target)
- @.claude/haios/manifesto/L4/functional_requirements.md:642-648 (REQ-REFERENCE-002)
