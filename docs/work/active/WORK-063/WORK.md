---
template: work_item
id: WORK-063
title: Add context:fork to validation-agent
type: implementation
status: backlog
owner: Hephaestus
created: 2026-02-01
spawned_by: WORK-058
chapter: null
arc: configuration
closed: null
priority: high
effort: trivial
traces_to:
- REQ-CONTEXT-001
requirement_refs: []
source_files:
- .claude/agents/validation-agent.md
acceptance_criteria:
- validation-agent.md has context:fork in frontmatter
- Agent spawned with fork receives only explicit prompt, not parent history
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-01 17:21:03
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-01T17:22:17'
---
# WORK-063: Add context:fork to validation-agent

---

## Context

WORK-058 investigation found that `context: fork` in subagent frontmatter provides isolated context for validation. Current validation-agent shares full parent context, which can bias CHECK phase verdicts.

**Problem:** An agent that sees all implementation work may unconsciously favor passing.

**Solution:** Add `context: fork` to validation-agent frontmatter. Fork isolation forces explicit context passing via prompt only.

---

## Deliverables

- [ ] **Add `context: fork` to validation-agent.md frontmatter**
- [ ] **Verify agent behavior** - spawned agent receives only prompt, not parent history

---

## Implementation

Single line change to `.claude/agents/validation-agent.md`:

```yaml
---
name: validation-agent
description: Unbiased CHECK phase validation...
tools: Bash, Read, Glob
context: fork  # NEW: Isolated from parent context
---
```

---

## History

### 2026-02-01 - Created (Session 274)
- Spawned from WORK-058 investigation
- High priority, trivial effort

---

## References

- @docs/work/active/WORK-058/WORK.md (parent investigation)
- @.claude/agents/validation-agent.md (target file)
