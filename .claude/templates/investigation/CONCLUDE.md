---
template: investigation_phase
phase: CONCLUDE
maps_to_state: DONE
version: '1.1'
input_contract:
- field: validate_complete
  type: boolean
  required: true
  description: VALIDATE phase complete
- field: all_verdicts
  type: table
  required: true
  description: All hypotheses have verdicts
output_contract:
- field: findings_synthesized
  type: markdown
  required: true
  description: Answer to investigation objective
- field: spawned_work
  type: table
  required: false
  description: Spawned work items created
- field: memory_stored
  type: list
  required: true
  description: Learnings stored via ingester_ingest
- field: memory_refs
  type: list
  required: true
  description: memory_refs populated in work item frontmatter
generated: '2026-02-04'
last_updated: '2026-02-04T22:29:16'
---
# CONCLUDE Phase

Synthesize findings, spawn work, store to memory.

## Input Contract

- [ ] VALIDATE phase complete
- [ ] All hypotheses have verdicts

## Governed Activities

*From activity_matrix.yaml for DONE state:*

| Activity | Rule | Notes |
|----------|------|-------|
| file-read | allow | Read findings |
| file-write | allow | Write conclusions |
| memory-store | allow | Ingest learnings |
| skill-invoke | allow | Spawn work items |

## Output Contract

- [ ] Findings synthesized (answer to objective)
- [ ] Spawned work items created via `/new-work` or `/new-plan`
- [ ] Memory stored via `ingester_ingest`
- [ ] `memory_refs` populated in work item frontmatter
- [ ] Rationale documented if no spawned work

## Template

```markdown
## Conclusion

[One paragraph synthesizing the answer to the investigation objective]

## Spawned Work

| ID | Title | spawned_by |
|----|-------|------------|
| | | {this_work_id} |

### Not Spawned Rationale (if none)

[Explain why this investigation produced no follow-on work]

## Memory Storage

- [ ] `ingester_ingest` called with findings
- [ ] `memory_refs` updated in WORK.md frontmatter

**Concept IDs stored:** [list IDs here]
```
