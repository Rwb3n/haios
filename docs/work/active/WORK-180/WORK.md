---
template: work_item
id: WORK-180
title: "Implement ADR-047 Tiered Coldstart"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-20
spawned_by: WORK-162
spawned_children: []
chapter: CH-061
arc: call
closed: null
priority: high
effort: large
traces_to:
  - REQ-CONFIG-001
  - L3.3
requirement_refs: []
source_files:
  - .claude/haios/lib/coldstart_orchestrator.py
  - .claude/haios/lib/identity_loader.py
  - .claude/haios/config/coldstart.yaml
  - .claude/commands/coldstart.md
acceptance_criteria:
  - "EpochLoader implemented: reads EPOCH.md + active ARC.md files live, extracts/compresses status, chapters, exit criteria"
  - "OperationsLoader implemented: reads justfile, CLAUDE.md, ADR-045 live, injects tier model, recipe catalogue, module paths"
  - "Tier selection logic: ColdstartOrchestrator accepts tier argument, auto-detection with staleness threshold"
  - "CLI argument forwarding: argparse in __main__, --extend flag, justfile recipe forwards args"
  - "coldstart.yaml updated with tier_detection, tier definitions, new phase entries"
  - "coldstart.md updated: zero manual Read steps, tier argument documented, --extend escape hatch documented"
  - "Tests: unit tests for both loaders, integration tests for tier auto-detection (4 paths)"
  - "Verification: full coldstart produces zero manual Reads, token savings measured vs baseline"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-02-20T23:49:53
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
  - 87131
extensions:
  epoch: E2.8
version: "2.0"
generated: 2026-02-20
last_updated: 2026-02-20T23:49:53
---
# WORK-180: Implement ADR-047 Tiered Coldstart

---

## Context

ADR-047 (Tiered Coldstart Context Injection) was accepted in S412 (WORK-162). The design specifies 3 coldstart tiers (Full/Light/Minimal), 2 new loaders (EpochLoader, OperationsLoader), auto-detection with staleness threshold, and an --extend escape hatch. This work item implements that design.

**The problem ADR-047 solves:** 88% of coldstart token cost comes from manual Read calls (EPOCH.md, 4x ARC.md, CLAUDE.md, memory queries). The orchestrator automates only 12%. After coldstart, agents are informed (WHO + WHAT) but not operational (no HOW). S393/S394 evidence: 200k agent failed because it had no knowledge of recipes/tier model.

**Implementation scope (from ADR-047 Implementation section):**
1. EpochLoader — new loader in lib/, follows IdentityLoader pattern
2. OperationsLoader — new loader in lib/, reads source files live (no caching)
3. Tier selection logic — update ColdstartOrchestrator.run() with tier argument + auto-detection
4. CLI argument forwarding — argparse in __main__, --extend flag, justfile recipe update
5. coldstart.yaml — tier_detection config, tier definitions, new phase entries
6. coldstart.md — remove manual Read steps, add tier docs
7. Tests — unit + integration (4 auto-detection paths)
8. Verification — zero manual Reads, token savings measurement

This is a parent work item. The implementing agent MAY decompose into children or implement directly depending on scope assessment during PLAN phase.

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

- [ ] EpochLoader class in .claude/haios/lib/epoch_loader.py
- [ ] OperationsLoader class in .claude/haios/lib/operations_loader.py
- [ ] ColdstartOrchestrator tier selection + auto-detection logic
- [ ] CLI argparse + --extend flag in coldstart_orchestrator.py
- [ ] Justfile recipe updated to forward arguments
- [ ] coldstart.yaml tier configuration
- [ ] coldstart.md zero-manual-Read version
- [ ] Unit tests for EpochLoader and OperationsLoader
- [ ] Integration tests for tier auto-detection (4 paths)
- [ ] Token savings verification (before/after measurement)

---

## History

### 2026-02-20 - Created (Session 412)
- Spawned from WORK-162 closure. ADR-047 accepted, implementation children need scaffolding.
- Parent tracking item for all ADR-047 implementation work.
- CH-061 was prematurely marked complete (only WORK-162 design was done). This item reopens the implementation scope.

---

## References

- @docs/ADR/ADR-047-tiered-coldstart-context-injection.md (design spec — MUST read before PLAN phase)
- @docs/work/active/WORK-162/WORK.md (parent design work item, closed S412)
- @.claude/haios/lib/coldstart_orchestrator.py (target for modification)
- @.claude/haios/lib/identity_loader.py (pattern to follow for new loaders)
- Memory: 87131 (WORK-162 closure summary)
