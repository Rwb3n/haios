---
template: work_item
id: INV-056
title: Hook-to-Module Migration for Epoch 2.2 Completion
status: complete
owner: Hephaestus
created: 2026-01-04
closed: '2026-01-04'
milestone: M7b-WorkInfra
priority: high
effort: medium
category: investigation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks:
- E2-259
- E2-260
- E2-261
- E2-262
- E2-263
- E2-264
enables: []
related:
- INV-052
- INV-053
- E2-085
- E2-120
- INV-057
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-04 19:08:34
  exited: null
cycle_docs: {}
memory_refs:
- 80678
- 80679
- 80680
- 80681
- 80682
- 80683
- 80684
- 80685
- 80686
- 80687
documents:
  investigations: []
  plans: []
  checkpoints: []
version: '1.0'
generated: 2026-01-04
last_updated: '2026-01-04T19:42:54'
---
# WORK-INV-056: Hook-to-Module Migration for Epoch 2.2 Completion

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Epoch 2.2 Chariot Architecture is incomplete. The 5 modules (GovernanceLayer, MemoryBridge, WorkEngine, ContextLoader, CycleRunner) are built and wired to justfile via cli.py, but hooks still import directly from `.claude/lib/` instead of using modules.

**Root cause:** Strangler Fig migration focused on justfile recipes first (E2-250). Hooks were not migrated because they work, but "optional" violates Epoch 2.2 requirement that modules REPLACE implementations.

**Current lib/ dependencies in hooks:**
| Hook | lib/ Import | Should Use |
|------|-------------|------------|
| user_prompt_submit.py | `status` | StatusModule or cli.py |
| pre_tool_use.py | `config`, `node_cycle` | GovernanceLayer, CycleRunner |
| post_tool_use.py | `error_capture`, `validate`, `status`, `node_cycle` | GovernanceLayer, CycleRunner, MemoryBridge |

---

## Current State

Investigation COMPLETE. All hypotheses tested. 6 work items spawned (E2-259 through E2-264).

---

## Deliverables

- [x] Analyze each hook's lib/ dependencies
- [x] Map dependencies to existing modules or identify new module needs
- [x] Design migration approach (extend modules vs new module)
- [x] Spawn implementation work items (E2-259 through E2-264)
- [ ] Update L4-implementation.md with Epoch 2.2 completion criteria (deferred to close)

---

## Findings

### H1: CONFIRMED - Most lib/ imports can map to existing modules
validate.py is already done via GovernanceLayer. Same delegation pattern works for other lib/ functions.

### H2: CONFIRMED - 5 gaps require extending existing modules
| lib/ Function | Target Module | Work Item |
|---------------|---------------|-----------|
| `status.generate_slim_status()` | ContextLoader | E2-259 |
| `config.ConfigLoader.toggles` | GovernanceLayer | E2-260 |
| `error_capture.is_actual_error()` | MemoryBridge | E2-261 |
| `reasoning_extraction.py` | MemoryBridge | E2-262 |
| `node_cycle.build_scaffold_command()` | CycleRunner | E2-263 |

### H3: REFUTED - No new modules needed
All gaps fit within scope of existing 5 modules. No 6th module required.

### Key Decision: Delegation Pattern
Modules wrap lib/ functions rather than copying code. This maintains backward compatibility and reduces duplication.

### Final Step
E2-264 rewires all 4 hooks to import from modules instead of lib/. Blocked by E2-259-263.

---

## History

### 2026-01-04 - Created (Session 168)
- Operator directive: "no optionals. everything must become 2.2"
- Prior work review: INV-052, INV-053, E2-085, E2-120
- Gap identified: Hooks still use lib/ directly

### 2026-01-04 - Investigation Complete (Session 169)
- All 4 hooks analyzed
- 5 module extension gaps identified
- Spawned E2-259 through E2-264
- Findings stored to memory (80678-80687)

---

## References

- INV-052: Session-State-System-Audit (full architecture documentation)
- INV-053: HAIOS Modular Architecture Review (simplified 5-module design)
- E2-085: Hook Migration PowerShell to Python (prior hook migration)
- E2-120: Complete PowerShell to Python Migration (execution of E2-085)
- L4-implementation.md: Epoch 2.2 requirements and module definitions
- Memory 80678-80687: Investigation findings
