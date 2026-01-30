---
template: work_item
id: WORK-036
title: Investigation Template vs Explore Agent Effectiveness
type: investigation
status: complete
owner: Hephaestus
created: 2026-01-30
spawned_by: null
chapter: null
arc: null
closed: '2026-01-30'
priority: medium
effort: medium
traces_to: []
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-30 19:07:08
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82646
- 82647
- 82648
- 82649
- 82650
- 82651
- 82652
- 82653
- 82654
- 82655
- 82656
- 82661
- 82662
- 82663
- 82664
- 82665
- 82666
- 82667
- 82668
extensions: {}
version: '2.0'
generated: 2026-01-30
last_updated: '2026-01-30T19:07:38'
---
# WORK-036: Investigation Template vs Explore Agent Effectiveness

@docs/README.md
@docs/epistemic_state.md

---

## Context

In Session 262, an Explore agent with an open-ended prompt produced a comprehensive 12-part architectural analysis (45+ files examined, patterns catalogued, design recommendations). This output quality exceeded typical investigation-cycle outputs.

**The Question:** Why did this succeed where formal INV-* investigations sometimes produce shallow summaries?

**Related Prior Work:** Memory concept 77254 notes: "The investigation template at 125 lines could not channel agents to produce detailed outputs. Session 101 proved this when agent bypassed subagent and wrote summaries instead of detailed evidence."

---

## Deliverables

- [ ] Analysis of Session 262 Explore prompt characteristics
- [ ] Comparison with investigation-cycle/investigation-agent patterns
- [ ] Identify factors that enabled depth (tool access, prompt framing, no template constraints)
- [ ] Recommendations for investigation-cycle skill improvements
- [ ] Memory storage of findings

---

## History

### 2026-01-30 - Created (Session 262)
- Spawned from observation: Explore agent output quality vs investigation template

---

## References

- Session 262 Explore agent output (CH-004 design analysis)
- Memory concept 77254 (investigation template ineffectiveness)
- @.claude/skills/investigation-cycle/SKILL.md
- @.claude/agents/investigation-agent.md
