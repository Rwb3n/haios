---
template: work_item
id: WORK-060
title: Claude Code Platform Features - plansDirectory, MCP improvements, auto-reload
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-01
spawned_by: WORK-056
chapter: null
arc: configuration
closed: '2026-02-01'
priority: medium
effort: small
traces_to:
- REQ-CONFIG-001
requirement_refs: []
source_files:
- .claude/haios/config/haios.yaml
- .claude/settings.json
acceptance_criteria:
- plansDirectory setting evaluated for plan consolidation
- MCP list_changed capability evaluated
- Auto skill hot-reload evaluated for HAIOS skills
- Setup hook event evaluated for fresh clone initialization
- Adoption recommendation with implementation plan
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-01 15:18:24
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82879
- 82880
- 82881
- 82882
- 82883
- 82884
- 82885
- 82886
- 82887
- 82888
- 82889
- 82890
- 82891
- 82899
- 82900
- 82901
- 82902
- 82901
- 82903
extensions: {}
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-01T16:22:20'
---
# WORK-060: Claude Code Platform Features - plansDirectory, MCP improvements, auto-reload

---

## Context

Claude Code 2.1.x introduced platform features that could improve HAIOS infrastructure:

**Features to Investigate:**

| Feature | Version | Potential Use |
|---------|---------|---------------|
| **`plansDirectory`** | 2.1.9 | Custom plan storage - consolidate plan artifacts |
| **MCP `list_changed`** | 2.1.0 | Dynamic tool updates - hot-reload memory tools |
| **Auto skill hot-reload** | 2.1.0 | Skills reload without restart |
| **Setup hook event** | 2.1.10 | `--init` triggers hooks - auto-setup on fresh clone |
| **Large tool outputs to disk** | 2.1.2 | File references instead of truncation |

**Current State:**
- Plans stored in work item directories (cycle_docs field)
- MCP tools defined statically
- Skills require restart to update
- Fresh clone requires manual `/coldstart`

**Questions:**
1. Can plansDirectory consolidate plans outside work items?
2. Can list_changed enable dynamic memory tool configuration?
3. Is auto skill reload useful for HAIOS development?
4. Can Setup hook replace manual coldstart on fresh clone?

---

## Deliverables

- [x] **plansDirectory evaluation** - Skip: breaks HAIOS colocation pattern
- [x] **MCP list_changed doc** - Skip: no use case for static memory tools
- [x] **Setup hook evaluation** - Low: requires --init flag, cannot auto-trigger
- [x] **Adoption recommendation** - None of these features require HAIOS implementation work

---

## History

### 2026-02-01 - Created (Session 271)
- Spawned from WORK-056 parent investigation
- Linked to configuration arc (platform infrastructure)

### 2026-02-01 - Investigation Complete (Session 273)
- Evaluated all 5 platform features
- Findings: 2 already active, 2 not suitable, 1 minimal value
- No implementation work spawned
- Memory refs: 82879-82891

---

## References

- @docs/work/active/WORK-056/WORK.md (parent investigation)
- @.claude/haios/config/haios.yaml (current config)
- @.claude/settings.json (Claude Code settings)
