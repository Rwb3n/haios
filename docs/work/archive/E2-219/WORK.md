---
template: work_item
id: E2-219
title: Ground Truth Verification Parser
status: complete
owner: Hephaestus
created: 2025-12-28
closed: 2025-12-28
milestone: M7c-Governance
priority: medium
effort: small
category: implementation
spawned_by: INV-042
spawned_by_investigation: INV-042
blocked_by: []
blocks:
- E2-220
enables:
- E2-220
related: []
current_node: do-active
node_history:
- node: backlog
  entered: 2025-12-28 16:40:55
  exited: '2025-12-28T16:53:03.894664'
- node: plan-active
  entered: '2025-12-28T16:53:03.894664'
  exited: '2025-12-28T16:58:40.925407'
- node: do-active
  entered: '2025-12-28T16:58:40.925407'
  exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2025-12-28
last_updated: '2025-12-28T16:41:32'
---
# WORK-E2-219: Ground Truth Verification Parser

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Implementation plans have Ground Truth Verification tables with file paths, grep patterns, and test commands, but no automated parser extracts these for machine-checking during DoD validation.

**Root cause:** INV-042 found 92% of verification items are machine-checkable but there's no infrastructure to parse the markdown table and classify verification types.

**Solution:** Create a parser that extracts verification items from Ground Truth Verification tables and classifies them by type (file-check, grep-check, test-run, json-verify, human-judgment).

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] Create `parse_ground_truth_verification()` function in `.claude/lib/validate.py`
- [ ] Parse markdown table: File | Expected State | Verified | Notes columns
- [ ] Classify verification type based on pattern matching (see INV-042 mapping table)
- [ ] Return structured list of verification items with type, path, expected_state, is_checked
- [ ] Write tests for parser with sample plan content

---

## History

### 2025-12-28 - Created (Session 136)
- Spawned from INV-042: Machine-Checked DoD Gates investigation
- Investigation found consistent template structure across 5 sampled plans
- 92% of verification items are machine-checkable

---

## References

- Spawned by: INV-042 (Machine-Checked DoD Gates)
- Design: `docs/work/active/INV-042/investigations/001-machine-checked-dod-gates.md`
- Template: `.claude/templates/implementation_plan.md:347-393`
