---
template: work_item
id: WORK-008
title: ContextLoader Identity Integration
type: feature
status: active
owner: Hephaestus
created: 2026-01-22
spawned_by: WORK-007
chapter: CH-004
arc: configuration
closed: null
priority: medium
effort: small
requirement_refs:
- R4
source_files:
- .claude/haios/epochs/E2_3/arcs/configuration/CH-004-identity-loader.md
- .claude/haios/lib/identity_loader.py
- .claude/haios/modules/context_loader.py
acceptance_criteria:
- ContextLoader calls IdentityLoader during load_context()
- Coldstart receives identity context automatically
- No manual file reads for manifesto content
blocked_by: []
blocks: []
enables:
- CH-005 (Session Loader)
- CH-007 (Coldstart Orchestrator)
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-22 19:49:18
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82292
- 82293
- 82294
- 82295
extensions: {}
version: '2.0'
generated: 2026-01-22
last_updated: '2026-01-22T19:50:06'
---
# WORK-008: ContextLoader Identity Integration

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** IdentityLoader exists and works (`just identity` produces 35 lines), but it's not wired into the automated coldstart flow. Coldstart still reads full manifesto files manually.

**Current state:**
```python
# .claude/haios/modules/context_loader.py
# Still reads L0-L4 directly:
l0_telos=self._read_manifesto_file("L0-telos.md"),  # 101 lines
l1_principal=self._read_manifesto_file("L1-principal.md"),  # 147 lines
...
```

**Root cause:** WORK-007 Phase C (Integration) was deferred per E2-186 file scope limit. The IdentityLoader exists but has no runtime consumer in the coldstart path.

**Solution:** Modify ContextLoader to import and call IdentityLoader, replacing direct manifesto file reads with extracted essence (~35 lines vs 1137 lines).

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

- [ ] `.claude/haios/modules/context_loader.py` modified to import IdentityLoader
- [ ] `load_context()` calls `IdentityLoader().load()` instead of direct file reads
- [ ] GroundedContext has `identity_context` field (or equivalent)
- [ ] Integration test: `just coldstart` receives identity context automatically
- [ ] Update `context_loader.py` docstring to reflect identity integration

---

## History

### 2026-01-22 - Created (Session 226)
- Spawned from WORK-007 Phase C (deferred integration)
- First runtime consumer wiring for identity_loader.py

---

## References

- @docs/work/active/WORK-007/WORK.md (parent work - completed)
- @docs/work/active/WORK-007/plans/PLAN.md (Phase C deferred here)
- @.claude/haios/lib/identity_loader.py (to be integrated)
- @.claude/haios/modules/context_loader.py (modification target)
- @.claude/haios/epochs/E2_3/arcs/configuration/CH-004-identity-loader.md (chapter spec)
