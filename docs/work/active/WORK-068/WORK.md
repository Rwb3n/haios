---
template: work_item
id: WORK-068
title: Agent Model Configuration - Add model field to HAIOS agents
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-01
spawned_by: WORK-056
chapter: null
arc: configuration
closed: '2026-02-01'
priority: medium
effort: trivial
traces_to:
- REQ-CONFIG-001
requirement_refs: []
source_files:
- .claude/agents/critique-agent.md
- .claude/agents/investigation-agent.md
- .claude/agents/preflight-checker.md
- .claude/agents/schema-verifier.md
- .claude/agents/test-runner.md
- .claude/agents/validation-agent.md
- .claude/agents/why-capturer.md
- .claude/agents/anti-pattern-checker.md
acceptance_criteria:
- Each HAIOS agent has model field in frontmatter
- Model assignments match cognitive requirements (opus for deep reasoning, haiku for
  mechanical)
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-01 22:40:18
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82983
- 82984
- 82985
- 82986
- 83010
- 83011
- 83012
- 83013
- 83014
- 83015
- 83016
- 83017
extensions: {}
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-01T22:48:28'
---
# WORK-068: Agent Model Configuration - Add model field to HAIOS agents

---

## Context

HAIOS agents currently inherit the parent model by default, which means all agents run on opus regardless of cognitive requirements. Claude Code supports a `model` field in agent frontmatter to specify haiku, sonnet, or opus per agent.

**Problem:** Using opus for all agents is suboptimal for cost and latency. Simple mechanical tasks (schema lookup, test execution) don't need opus-level reasoning.

**Solution:** Add `model:` field to each HAIOS agent frontmatter with appropriate model selection:

| Agent | Model | Rationale |
|-------|-------|-----------|
| **critique-agent** | opus | Assumption surfacing needs deepest reasoning |
| **investigation-agent** | opus | EXPLORE phase needs unrestricted depth |
| **validation-agent** | sonnet | DoD checks need reasoning but structured |
| **anti-pattern-checker** | sonnet | Pattern matching with reasoning |
| **preflight-checker** | haiku | Simple checklist validation |
| **schema-verifier** | haiku | Read-only SQL schema lookup |
| **test-runner** | haiku | Pytest execution wrapper |
| **why-capturer** | haiku | Structured learning extraction |

**Source:** WORK-056 observations (concepts 82983-82986), operator guidance Session 278.

---

## Deliverables

- [x] **Add `model: opus` to critique-agent.md**
- [x] **Add `model: opus` to investigation-agent.md**
- [x] **Add `model: sonnet` to validation-agent.md**
- [x] **Add `model: sonnet` to anti-pattern-checker.md**
- [x] **Add `model: haiku` to preflight-checker.md**
- [x] **Add `model: haiku` to schema-verifier.md**
- [x] **Add `model: haiku` to test-runner.md**
- [x] **Add `model: haiku` to why-capturer.md**
- [x] **Verify agents still function correctly** (schema-verifier haiku, critique-agent opus confirmed)

---

## History

### 2026-02-01 - Complete (Session 278)
- Added model field to all 8 agents
- Behavioral verification: schema-verifier (haiku), critique-agent (opus) confirmed working
- Memory stored: concepts 83010-83015

### 2026-02-01 - Created (Session 278)
- Spawned from WORK-056 observation about agent model configuration gap
- Model assignments based on cognitive requirements analysis

---

## References

- @docs/work/active/WORK-056/observations.md (source observation)
- @docs/work/active/WORK-063/observations.md (related observation)
- Claude Code sub-agents documentation (model field support)
