---
template: work_item
id: WORK-142
title: Retro-Cycle Ceremony Design and Implementation
type: design
status: active
owner: Hephaestus
created: 2026-02-12
spawned_by: null
spawned_children:
- WORK-143
chapter: null
arc: null
closed: null
priority: high
effort: large
traces_to:
- REQ-CEREMONY-001
- REQ-CEREMONY-002
- REQ-FEEDBACK-001
requirement_refs: []
source_files:
- .claude/skills/observation-capture-cycle/SKILL.md
- .claude/skills/close-work-cycle/SKILL.md
- .claude/commands/close.md
acceptance_criteria:
- retro-cycle skill defined with input/output contract
- 4 REFLECT dimensions (WCBB, WSY, WDN, WMI) with evidence anchoring
- DERIVE phase produces K/S/S directives (proportional scaling)
- EXTRACT phase stores bugs and features to memory with typed provenance tags
- COMMIT phase stores all outputs with no deduplication
- Computable predicate for trivial/substantial threshold
- Escape hatch (--skip-retro) with governance event logging
- DoD-relevant findings flow from REFLECT to VALIDATE
- close-work-cycle updated to use RETRO phase
- /close command updated to remove observation-capture-cycle reference
- observation-capture-cycle deprecated
blocked_by: []
blocks:
- WORK-143
enables:
- WORK-143
queue_position: working
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-12 23:34:46
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 85057
- 85058
- 85059
- 85060
- 85061
- 85062
- 85063
- 85064
- 85065
- 85066
- 85067
- 85068
- 85069
- 85070
extensions: {}
version: '2.0'
generated: 2026-02-12
last_updated: '2026-02-13T19:07:49.415687'
queue_history:
- position: ready
  entered: '2026-02-13T19:07:49.378405'
  exited: '2026-02-13T19:07:49.411540'
- position: working
  entered: '2026-02-13T19:07:49.411540'
  exited: null
---
# WORK-142: Retro-Cycle Ceremony Design and Implementation

---

## Context

### Problem

The current observation-capture-cycle is a single-step autonomous reflection that produces unstructured prose stored to memory. These observations then sit in files and memory until manually triaged (observation-triage-cycle). The outputs are not typed (bug vs feature vs behavioral directive), there is no pipeline chaining, and the triage consumer operates on file-based frontmatter — not memory provenance tags.

### Root Cause

observation-capture-cycle was designed as a reflection gate, not a data pipeline. It captures signal but doesn't structure, classify, or route it. The 4 questions are good prompts but produce undifferentiated prose that requires human effort to act on.

### Proposed Solution: retro-cycle

Replace observation-capture-cycle with a multi-step retro-cycle ceremony that structures autonomous agent reflection into typed, provenance-tagged memory entries with a downstream triage pathway.

**Key design decisions (Session 359 discussion + 2 critique rounds):**

1. **Autonomous extraction** — agent reads work evidence (work item, plan, tests, diff, governance events), same as current. Agent was always the one answering, not the operator.

2. **4-phase pipeline:**
   ```
   close-work-cycle: RETRO -> VALIDATE -> ARCHIVE -> CHAIN
                       |
                       +-- REFLECT: WCBB, WSY, WDN, WMI (evidence-anchored)
                       +-- DERIVE: Keep / Stop / Start (proportional)
                       +-- EXTRACT: Bugs + Features -> memory (NO auto-spawn)
                       +-- COMMIT: All to memory with typed provenance
   ```

3. **RETRO before VALIDATE** — preserves cognitive separation from INV-059 (completion mode bias). Reflecting before confirming DoD, not after archiving.

4. **No auto-spawn** — bugs and features stored to memory with confidence tags. Surfaced at downstream triage ceremony. Respects REQ-LIFECYCLE-004 (chaining is caller choice).

5. **No deduplication at write time** — agents are stateless across sessions. If independent sessions converge on the same observation, frequency IS the signal. Deduplication happens at read time (triage ceremony).

6. **Proportional scaling** — computable predicate determines trivial vs substantial:
   ```
   trivial = (files_changed <= 2)
         AND (no plan exists in work dir)
         AND (no test files changed)
         AND (no CycleTransition governance events for this work_id)
   ```
   Trivial: single-pass retro. Substantial: full 4-phase pipeline.

7. **Evidence anchoring** — every REFLECT observation MUST reference a specific artifact (file path, diff hunk, governance event ID, test name). Generic statements filtered.

8. **DoD-relevant severity tag** — if REFLECT surfaces something that should block closure, it flows to VALIDATE as input (tagged `dod-relevant`), not stored for later triage.

9. **Escape hatches** — `--skip-retro` flag logged to governance events. Each sub-phase degrades gracefully if evidence unavailable. RETRO never blocks closure.

10. **Replaces MEMORY phase** — RETRO COMMIT absorbs closure summary storage. Governance event check moves to VALIDATE phase.

### REFLECT Dimensions

| Dimension | What It Captures | Orientation |
|-----------|-----------------|-------------|
| WCBB: What could've been better? | Quality gaps, process friction | Evaluative (negative) |
| WSY: What surprised you? | Unexpected behaviors, wrong assumptions | Epistemic |
| WDN: What drift did you notice? | Reality vs docs, code vs spec | Systemic |
| WMI: What's missing? | Tooling gaps, architectural gaps | Prescriptive |

### Critique Findings (2 rounds)

**Round 1 (10 assumptions, 4 blocking):**
- A1: Agent self-reflection quality → evidence anchoring required
- A2: Auto-spawn violates REQ-LIFECYCLE-004 → removed, all to memory
- A3: 4 sub-phases add overhead → proportional scaling
- A4: Internal phase loses cognitive separation → reordered RETRO before VALIDATE
- A8: No escape hatches → defined per sub-phase + --skip-retro

**Round 2 (10 assumptions, 2 blocking):**
- A3: Trivial/substantial threshold undefined → computable predicate
- A6: Triage consumer doesn't exist for new format → WORK-143 companion
- A10: Honest framing → this solves observation quality and actionability, not ceremony overhead for substantial items. Proportional scaling achieves parity for trivial items.

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

- [ ] retro-cycle SKILL.md with input/output contract and ceremony steps
- [ ] REFLECT phase: 4 dimensions (WCBB, WSY, WDN, WMI) with evidence anchoring rule
- [ ] DERIVE phase: K/S/S extraction with proportional scaling gate
- [ ] EXTRACT phase: Bug/feature classification with confidence tags (no auto-spawn)
- [ ] COMMIT phase: Memory storage with typed provenance (retro-reflect, retro-kss, retro-extract)
- [ ] Computable predicate for trivial/substantial threshold
- [ ] Escape hatches: --skip-retro flag, per-sub-phase degradation
- [ ] DoD-relevant severity tag: REFLECT findings flow to VALIDATE
- [ ] close-work-cycle SKILL.md updated (MEMORY -> RETRO, reordered chain)
- [ ] /close command updated (remove observation-capture-cycle reference)
- [ ] observation-capture-cycle SKILL.md deprecated (stub: true or archived)
- [ ] Consumer migration table documenting where each removed responsibility lands

---

## History

### 2026-02-12 - Created (Session 359)
- Design discussion: operator proposed multi-step retro pipeline (WWW+WCBB -> K/S/S -> Bug/Feature -> Memory)
- Retro synthesis created: .claude/haios/epochs/E2_6/retro-synthesis.md (90+ memory entries)
- Key operator decisions: autonomous mode, no dedup (frequency = signal), replace not augment
- Critique round 1: 10 assumptions, 4 blocking → auto-spawn removed, proportional scaling added, reordered to RETRO before VALIDATE
- Critique round 2: 10 assumptions, 2 blocking → computable predicate for threshold, companion WORK-143 for triage consumer
- Dimension finalized: WCBB, WSY, WDN, WMI (kept all 4, defer consolidation to empirical evidence)
- Design locked in by operator

---

## References

- .claude/haios/epochs/E2_6/retro-synthesis.md (S359 retro trend analysis)
- .claude/skills/observation-capture-cycle/SKILL.md (replaced by this work)
- .claude/skills/close-work-cycle/SKILL.md (consumer, updated by this work)
- .claude/commands/close.md (consumer, updated by this work)
- .claude/skills/observation-triage-cycle/SKILL.md (downstream consumer, updated by WORK-143)
- obs-313-ceremony-composition-gap.md (dynamic ceremony composition)
- obs-314-operator-initiated-system-evolution.md (missing ceremony chain)
- obs-339-system-assessment.md (ceremony overhead, flat metadata)
- INV-059 finding: completion mode bias (cognitive separation rationale)
- REQ-CEREMONY-001, REQ-CEREMONY-002, REQ-FEEDBACK-001
- REQ-LIFECYCLE-004 (chaining is caller choice — no auto-spawn)
- WORK-143 (companion: triage consumer update)
