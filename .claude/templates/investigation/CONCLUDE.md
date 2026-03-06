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
- field: epistemic_review
  type: table
  required: true
  description: K/I/U classification of all findings (KNOWN/INFERRED/UNKNOWN)
- field: verdict
  type: enum
  required: true
  description: PROCEED / DEFER / INVESTIGATE-MORE based on unknowns
- field: operator_decision
  type: enum
  required: false
  description: If DEFER verdict — operator response (proceed/investigate-more/defer-to-next-session)
- field: work_disposition
  type: table
  required: false
  description: Every finding-recommended item with disposition (SPAWNED/DEFERRED)
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
- [ ] Epistemic review completed (K/I/U table + verdict)
- [ ] Verdict rendered (PROCEED/DEFER/INVESTIGATE-MORE)
- [ ] If DEFER: operator consulted via AskUserQuestion
- [ ] Work Disposition table complete: every finding-recommended item has disposition (SPAWNED with ID, or DEFERRED with rationale)
- [ ] Memory stored via `ingester_ingest`
- [ ] `memory_refs` populated in work item frontmatter
- [ ] Rationale documented if no spawned work

## Template

```markdown
## Conclusion

[One paragraph synthesizing the answer to the investigation objective]

## Epistemic Review

### Findings Classification

| # | Category | Finding | Evidence/Reasoning |
|---|----------|---------|-------------------|
| K1 | KNOWN | [Fact] | [file:line / memory ID / URL] |
| I1 | INFERRED | [Conclusion] | [Premise → conclusion] |
| U1 | UNKNOWN | [Gap] | Impact: [blocking/non-blocking] |

### Verdict

**Verdict:** [PROCEED / DEFER / INVESTIGATE-MORE]

**Rationale:** [Why this verdict based on unknowns above]

<!-- If DEFER: AskUserQuestion was presented. Record operator decision: -->
**Operator Decision:** [proceed / investigate-more / defer-to-next-session]
**Decision Rationale:** [Why operator chose this direction]

## Work Disposition

<!-- MUST: Every finding that recommends follow-on work MUST appear in this table.
     Each item must have a disposition: SPAWNED (with ID) or DEFERRED (with rationale).
     Close command Step 1.5b validates completeness against findings. -->

| Finding | Recommended Work | Disposition | ID / Rationale |
|---------|-----------------|-------------|----------------|
| [K1/I1] | [Work description] | SPAWNED | WORK-XXX |
| [K2] | [Work description] | DEFERRED | [Why not now] |

### No Follow-On Work (if none)

[Explain why this investigation produced no follow-on work items.
 Valid reasons: all questions answered, no actionable gaps found, purely informational.]

## Memory Storage

- [ ] `ingester_ingest` called with findings
- [ ] `memory_refs` updated in WORK.md frontmatter

**Concept IDs stored:** [list IDs here]
```
