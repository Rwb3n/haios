---
template: work_item
id: WORK-007
title: Implement Identity Loader for Configuration Arc
type: feature
status: active
owner: Hephaestus
created: 2026-01-21
spawned_by: CH-004
chapter: CH-004
arc: configuration
closed: null
priority: medium
effort: medium
requirement_refs:
- R1
- R2
- R3
- R4
source_files:
- .claude/haios/epochs/E2_3/arcs/configuration/CH-004-identity-loader.md
- .claude/haios/epochs/E2_3/arcs/configuration/ARC.md
acceptance_criteria:
- Identity loaded via config, not hardcoded reads
- Output < 100 lines
- Contains mission, principles, constraints, epoch
- Coldstart Phase 1 can use this loader
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-21 22:20:30
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-21
last_updated: '2026-01-21T22:27:40'
---
# WORK-007: Implement Identity Loader for Configuration Arc

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Agent reads 5 full manifesto files (1137 lines) during coldstart when it only needs ~50 lines of extracted essence.

**Current state:**
```
Coldstart reads:
  - L0-telos.md (101 lines)
  - L1-principal.md (147 lines)
  - L2-intent.md (114 lines)
  - L3-requirements.md (192 lines)
  - L4-implementation.md (583 lines)

Agent needs: Prime directive, principles, constraints, epoch context
Waste: ~1000 lines of unnecessary context tokens
```

**Root cause:** No extraction mechanism exists to select specific content from manifesto files. The base Loader (WORK-005) provides extraction DSL, but no identity-specific config or loader exists.

**Solution:** Create an IdentityLoader that uses the base Loader with config defining what to extract from L0-L3 manifesto files. This is the first runtime consumer of loader.py (E2-250 requirement).

**Agent need:**
> "Who am I? What's my mission? What principles govern me? What constraints apply?"

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

- [ ] `.claude/haios/config/loaders/identity.yaml` - Config defining manifesto extractions
- [ ] `.claude/haios/lib/identity_loader.py` - IdentityLoader class using base Loader
- [ ] `just identity` recipe - CLI invocation
- [ ] Unit tests: `tests/test_identity_loader.py`
- [ ] Output format per CH-004 R3 (< 100 lines)
- [ ] Integration: ContextLoader can call IdentityLoader (first runtime consumer)

---

## History

### 2026-01-21 - Created (Session 223)
- Initial creation via work-creation-cycle
- Spawned from CH-004 Identity Loader chapter
- First runtime consumer of WORK-005 loader.py base

---

## References

- @.claude/haios/epochs/E2_3/arcs/configuration/CH-004-identity-loader.md (chapter spec)
- @.claude/haios/epochs/E2_3/arcs/configuration/ARC.md (arc context)
- @.claude/haios/lib/loader.py (base loader from WORK-005)
- @docs/work/active/WORK-005/WORK.md (dependency - loader base)
