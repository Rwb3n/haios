---
template: work_item
id: WORK-009
title: Coldstart Orchestrator - Wire ContextLoader
type: feature
status: active
owner: Hephaestus
created: 2026-01-22
spawned_by: WORK-008
chapter: CH-007
arc: configuration
closed: null
priority: high
effort: medium
requirement_refs:
- R4
source_files:
- .claude/haios/epochs/E2_3/arcs/configuration/CH-007-coldstart-orchestrator.md
- .claude/commands/coldstart.md
- .claude/haios/modules/context_loader.py
acceptance_criteria:
- Coldstart runs via just coldstart
- No Read tools invoked by agent for identity loading
- Identity phase uses ContextLoader output
blocked_by: []
blocks: []
enables:
- CH-005 Session Loader integration
- CH-006 Work Loader integration
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-22 21:56:46
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82298
- 82299
extensions: {}
version: '2.0'
generated: 2026-01-22
last_updated: '2026-01-22T21:58:12'
---
# WORK-009: Coldstart Orchestrator - Wire ContextLoader

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** ContextLoader (WORK-008) is complete and working, but /coldstart still reads manifesto files manually. The chain is incomplete:

```
IdentityLoader ✓ → ContextLoader ✓ → coldstart.md ✗ (still reads files)
```

**Root cause:** /coldstart is a markdown skill that instructs the agent to read files. It doesn't call ContextLoader.load_context() which would use the registered loaders.

**Arc exit criteria:** "Coldstart via injection (no manual file reads)" - this work directly addresses it.

**Scope:** Wire identity phase only. Session loader (CH-005) and work loader (CH-006) are separate work items.

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

- [ ] `just coldstart` recipe calls ContextLoader.load_context(role="main")
- [ ] Recipe outputs identity content (from IdentityLoader via ContextLoader)
- [ ] /coldstart skill uses recipe output instead of manual file reads for identity phase
- [ ] Test verifies identity content appears in coldstart output
- [ ] Demo: run /coldstart and verify no Read calls for L0-L4 manifesto files

---

## History

### 2026-01-22 - Created (Session 227)
- Spawned from WORK-008 (ContextLoader Identity Integration)
- Addresses CH-007 requirements incrementally (identity phase first)

---

## References

- @docs/work/active/WORK-008/WORK.md (parent work - complete)
- @.claude/haios/epochs/E2_3/arcs/configuration/CH-007-coldstart-orchestrator.md
- @.claude/haios/epochs/E2_3/arcs/configuration/ARC.md (exit criteria)
- @.claude/commands/coldstart.md (modification target)
- @.claude/haios/modules/context_loader.py (to be called)
