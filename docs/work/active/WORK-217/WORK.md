---
template: work_item
id: WORK-217
title: Implement Retro-Enrichment Agent
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-24
spawned_by: WORK-211
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-02-24'
priority: medium
effort: small
traces_to:
- REQ-FEEDBACK-006
- REQ-MEMORY-001
requirement_refs: []
source_files:
- .claude/skills/retro-cycle/SKILL.md (integration point)
- .claude/commands/close.md (invocation point)
acceptance_criteria:
- retro-enrichment-agent.md exists with input/output contract
- Agent queries memory_search_with_experience for each extracted item
- Agent annotates items with related_memory_ids, convergence_count, prior_work_ids
- Agent stores enriched items with retro-enrichment provenance
- /close command invokes enrichment agent after retro-cycle returns
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: CHAIN
node_history:
- node: backlog
  entered: 2026-02-24 21:18:42
  exited: '2026-02-24T23:03:19.480465'
artifacts: []
cycle_docs: {}
memory_refs:
- 88476
- 88477
- 88478
- 88479
- 88508
- 88509
- 88628
- 88629
- 88630
- 88631
- 88632
- 88633
- 88634
- 88635
- 88636
- 88637
- 88638
- 88639
- 88640
- 88641
- 88642
- 88643
- 88482
extensions: {}
version: '2.0'
generated: 2026-02-24
last_updated: '2026-02-24T23:03:19.484124'
queue_history:
- position: done
  entered: '2026-02-24T23:03:19.480465'
  exited: null
---
# WORK-217: Implement Retro-Enrichment Agent

---

## Context

**Spawned from:** WORK-211 (Post-Retro Enrichment Subagent Design — investigation)

**Problem:** Retro-cycle EXTRACT produces typed items (bug/feature/refactor/upgrade) stored to memory, but these items have no cross-references to prior related observations. Observation-triage-cycle consumes these items cold — without knowing if 10 prior sessions flagged the same issue. Memory has 88k+ concepts but no mechanism connects new retro output to existing entries.

**Solution (WORK-211 findings):** A haiku subagent that runs after retro-cycle COMMIT+EXTRACT, taking the output contract (memory_concept_ids, extracted_items, extract_concept_ids) and enriching each item with semantic memory cross-references. Enrichment annotates — it does not auto-spawn (REQ-LIFECYCLE-004). Triage consumes richer data.

**Agent Contract (designed in WORK-211):**
- **Input:** work_id, memory_concept_ids, extract_concept_ids, extracted_items (from retro-cycle output)
- **Process:** For each item → query memory_search_with_experience → collect related IDs, convergence count, prior WORK-* references
- **Output:** enriched_items list with annotations, enrichment_concept_ids
- **Model:** haiku (mechanical cross-referencing)
- **Provenance:** retro-enrichment:{work_id}

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning)

     These checkboxes are the SOURCE OF TRUTH for work completion.

     During CHECK phase of implementation-cycle:
     - Agent MUST read this section
     - Agent MUST verify EACH checkbox can be marked complete
     - If ANY deliverable is incomplete, work is NOT done

     "Tests pass" ≠ "Deliverables complete"
     Tests verify code works. Deliverables verify scope is complete.

     NOTE (WORK-001): Acceptance criteria are in frontmatter (machine-parseable).
     Deliverables are implementation outputs, not requirements.
-->

- [ ] `retro-enrichment-agent.md` agent card with input/output contract, model, trigger conditions
- [ ] Integration in `/close` command: invoke enrichment agent after retro-cycle returns
- [ ] Enrichment stores to memory with `retro-enrichment:{work_id}` provenance tag

---

## History

### 2026-02-24 - Created (Session 446)
- Initial creation

---

## References

- @docs/work/active/WORK-211/WORK.md (source investigation)
- @.claude/skills/retro-cycle/SKILL.md (retro-cycle contract)
- @.claude/skills/observation-triage-cycle/SKILL.md (downstream consumer)
- @.claude/agents/close-work-cycle-agent.md (similar agent pattern)
- Memory: 88078 (S436 operator directive)
