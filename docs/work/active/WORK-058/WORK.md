---
template: work_item
id: WORK-058
title: Claude Code Session/Context Management - SESSION_ID, agent_type, context:fork
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-01
spawned_by: WORK-056
chapter: null
arc: configuration
closed: '2026-02-01'
priority: high
effort: medium
traces_to:
- REQ-CONTEXT-001
requirement_refs: []
source_files:
- .claude/session
- .claude/haios/modules/coldstart_orchestrator.py
acceptance_criteria:
- SESSION_ID substitution documented and evaluated
- agent_type in SessionStart hook evaluated for role-based loading
- context:fork pattern evaluated for isolated subagents
- Adoption recommendation with implementation plan
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-01 15:18:17
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82915
- 82916
- 82917
- 82918
- 82919
- 82920
- 82921
- 82922
- 82927
extensions: {}
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-01T17:01:24'
---
# WORK-058: Claude Code Session/Context Management - SESSION_ID, agent_type, context:fork

---

## Context

Claude Code 2.1.x introduced session and context management features that could improve HAIOS continuity:

**Features to Investigate:**

| Feature | Version | Potential Use |
|---------|---------|---------------|
| **`${CLAUDE_SESSION_ID}`** | 2.1.9 | Skills can reference session ID - link checkpoints to sessions |
| **`agent_type` in SessionStart** | 2.1.2 | Know which agent type for role-based context loading |
| **`context: fork`** | 2.1.0 | Isolated context for subagents - cleaner validation agents |
| **`--from-pr` flag** | 2.1.27 | Resume sessions linked to GitHub PRs |

**Current State:**
- HAIOS tracks session via `.claude/session` file (manual increment)
- Coldstart orchestrator loads context but doesn't know agent type
- Subagents share full context (can be noisy)

**Questions:**
1. Can SESSION_ID replace our manual session tracking?
2. Can agent_type enable true role-based loading per haios.yaml config?
3. Can context:fork create cleaner isolated validators/investigators?
4. Is PR-linked resume useful for HAIOS workflows?

---

## Deliverables

- [x] **SESSION_ID integration doc** - AUGMENT not replace (CC uses UUID, HAIOS uses incrementing integers)
- [x] **agent_type feasibility** - LIMITED value (only main vs subagent, not which subagent)
- [x] **context:fork evaluation** - ADOPT for validation-agent (unbiased CHECK phase)
- [x] **Adoption recommendation** - See Findings section

---

## History

### 2026-02-01 - Created (Session 271)
- Spawned from WORK-056 parent investigation
- Linked to configuration arc (context management)

### 2026-02-01 - Investigation Complete (Session 274)
- Evaluated all 4 features from CC 2.1.x
- Findings:
  - SESSION_ID: AUGMENT (store CC UUID alongside HAIOS session number)
  - agent_type: LIMITED (only main vs subagent, not which subagent)
  - context:fork: ADOPT for validation-agent (HIGH priority)
  - --from-pr: SKIP (HAIOS uses work items, not PRs)
- Spawned: WORK-063 (add context:fork to validation-agent)
- Memory refs: 82915-82922

---

## Findings

### Feature Evaluation Matrix

| Feature | Verdict | Adoption | Priority |
|---------|---------|----------|----------|
| `CLAUDE_SESSION_ID` | AUGMENT | Store alongside HAIOS session | Low |
| `agent_type` (SessionStart) | LIMITED | Analytics only | Low |
| `context: fork` | **ADOPT** | Apply to validation-agent | **High** |
| `--from-pr` | SKIP | Not useful for HAIOS | None |

### Key Insight: context:fork for Unbiased Validation

Current validation-agent shares full parent context, which can influence verdicts. `context: fork` provides:
- Clean isolation with only explicit prompt
- No implementation history leakage
- Unbiased CHECK phase validation

### Spawned Work

**WORK-063:** Add context:fork to validation-agent frontmatter (trivial effort, high value)

---

## References

- @docs/work/active/WORK-056/WORK.md (parent investigation)
- @.claude/session (current session tracking)
- @.claude/haios/modules/coldstart_orchestrator.py (context loading)
