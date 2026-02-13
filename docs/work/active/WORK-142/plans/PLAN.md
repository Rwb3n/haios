---
template: implementation_plan
status: complete
date: 2026-02-13
backlog_id: WORK-142
title: "Retro-Cycle Ceremony Implementation"
author: Hephaestus
lifecycle_phase: plan
session: 361
version: "1.5"
generated: 2026-02-13
last_updated: 2026-02-13T19:17:07
---
# Implementation Plan: Retro-Cycle Ceremony Implementation

---

## Goal

Replace observation-capture-cycle with a multi-step retro-cycle ceremony that structures autonomous agent reflection into typed, provenance-tagged memory entries with a downstream triage pathway.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 11 | Explicit manifest below |
| Lines of code affected | ~400 | Skill/command markdown edits |
| New files to create | 2 | retro-cycle/SKILL.md, test_retro_cycle.py |
| Tests to write | ~15 | 9 new + 6 updated |
| Dependencies | 0 | Pure markdown, no Python module changes |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Med | 4 consumer files reference observation-capture-cycle |
| Risk of regression | Med | 6 existing tests assert observation-capture-cycle refs |
| External dependencies | Low | No APIs, no config changes beyond registry |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| L5: Tests first | 20 min | High |
| L1: Create retro-cycle SKILL.md | 30 min | High |
| L2: Update close-work-cycle | 20 min | Med |
| L3: Update /close + session-end | 10 min | High |
| L4: Deprecate + registries | 15 min | High |
| **Total** | **~95 min** | |

---

## Current State vs Desired State

### Current State

```
/close {work_id}
  -> Skill(skill="observation-capture-cycle")     # Unstructured prose
       -> 4 questions, free-form answers
       -> ingester_ingest(content_type_hint="doxa")  # No typed provenance
  -> Skill(skill="close-work-cycle")
       -> VALIDATE -> ARCHIVE -> MEMORY -> CHAIN
          MEMORY phase: governance event check + closure summary storage
```

**Behavior:** Observations are untyped prose stored to memory. No bug/feature classification, no K/S/S extraction, no evidence anchoring, no proportional scaling.

### Desired State

```
/close {work_id}
  -> Skill(skill="retro-cycle")                    # Structured pipeline
       -> Phase 0: Scale Assessment (trivial|substantial)
       -> Phase 1: REFLECT (WCBB, WSY, WDN, WMI + evidence anchoring)
       -> Phase 2: DERIVE (Keep/Stop/Start, proportional)
       -> Phase 3: EXTRACT (bugs/features + confidence tags)
       -> Phase 4: COMMIT (typed provenance: retro-reflect, retro-kss, retro-extract)
  -> Skill(skill="close-work-cycle")
       -> VALIDATE -> ARCHIVE -> CHAIN
          VALIDATE phase: dod_relevant_findings + governance event check
          (MEMORY phase removed, absorbed by retro-cycle COMMIT)
```

**Behavior:** Observations are typed, evidence-anchored, provenance-tagged. Bugs/features classified with confidence. K/S/S directives extracted. Proportional scaling reduces overhead for trivial items.

---

## Tests First (TDD)

### New tests (tests/test_retro_cycle.py)

```python
def test_retro_cycle_skill_exists():
    assert Path(".claude/skills/retro-cycle/SKILL.md").exists()

def test_retro_cycle_has_ceremony_contract():
    # Valid YAML frontmatter with name, type, input_contract, output_contract
    fm = load_frontmatter(".claude/skills/retro-cycle/SKILL.md")
    assert fm["name"] == "retro-cycle"
    assert fm["type"] == "ceremony"
    assert "input_contract" in fm
    assert "output_contract" in fm

def test_retro_cycle_has_four_phases():
    content = Path(".claude/skills/retro-cycle/SKILL.md").read_text()
    for phase in ["REFLECT", "DERIVE", "EXTRACT", "COMMIT"]:
        assert phase in content

def test_retro_cycle_has_computable_predicate():
    content = Path(".claude/skills/retro-cycle/SKILL.md").read_text()
    assert "files_changed" in content
    assert "trivial" in content

def test_retro_cycle_has_evidence_anchoring():
    content = Path(".claude/skills/retro-cycle/SKILL.md").read_text()
    assert "evidence" in content.lower()
    assert "anchor" in content.lower()

def test_retro_cycle_has_escape_hatch():
    content = Path(".claude/skills/retro-cycle/SKILL.md").read_text()
    assert "skip_retro" in content or "skip-retro" in content

def test_retro_cycle_has_provenance_tags():
    content = Path(".claude/skills/retro-cycle/SKILL.md").read_text()
    for tag in ["retro-reflect", "retro-kss", "retro-extract"]:
        assert tag in content

def test_close_command_invokes_retro_cycle():
    content = Path(".claude/commands/close.md").read_text()
    assert "retro-cycle" in content

def test_close_work_cycle_references_retro_cycle():
    content = Path(".claude/skills/close-work-cycle/SKILL.md").read_text()
    assert "retro-cycle" in content
    retro_pos = content.find("retro-cycle")
    validate_pos = content.find("VALIDATE")
    assert retro_pos < validate_pos
```

### Updated existing tests

```python
# test_observation_capture_cycle.py - lines 46, 61:
# Change: assert "observation-capture-cycle" -> assert "retro-cycle"

# test_memory_ceremonies.py - line 120:
# Change: assert "observation-capture-cycle" -> assert "retro-cycle"

# test_ceremony_retrofit.py - line 35:
# Add "retro-cycle" to EXISTING_CEREMONY_SKILLS
```

---

## Detailed Design

**SKIPPED (exact code change sections):** Pure markdown skill/command authoring. No Python code changes. Design is fully specified in WORK-142 WORK.md (S359 design lock after 2 critique rounds).

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| RETRO before VALIDATE | Reordered from post-archive | INV-059: completion mode bias. Reflecting before confirming DoD preserves cognitive separation |
| No auto-spawn | Bugs/features to memory only | REQ-LIFECYCLE-004: chaining is caller choice. Surfaced at triage |
| No dedup at write time | Frequency IS signal | Agents are stateless across sessions. Independent convergence = stronger signal |
| MEMORY phase absorbed | Removed from close-work-cycle | retro-cycle COMMIT stores closure summary + observations in single pass |
| Proportional scaling | Computable predicate | files_changed <= 2 AND no plan AND no tests AND no CycleTransition events |
| Evidence anchoring | MUST reference artifact | Generic statements without evidence filtered (warning, not blocking) |
| 4 phases not 1 | REFLECT/DERIVE/EXTRACT/COMMIT | Observation != action != classification != persistence. Typed provenance requires separation |
| /close owns invocation | retro-cycle is predecessor to close-work-cycle, not entry gate | Avoids double invocation. /close invokes retro-cycle then close-work-cycle (current pattern preserved) |
| deprecated: true not stub: true | Keep obs-capture in EXISTING_CEREMONY_SKILLS | stub: true breaks test_existing_skills_not_marked_stub. deprecated: true is safe |
| Replace in registry, not add | Count stays 20 | Cleaner than keeping deprecated entry alongside replacement |

### Consumer Migration Table

| Responsibility | From | To |
|----------------|------|-----|
| 4 reflection questions | observation-capture-cycle | retro-cycle REFLECT (evidence-anchored WCBB/WSY/WDN/WMI) |
| Memory storage of observations | observation-capture-cycle (ingester_ingest, doxa) | retro-cycle COMMIT (typed provenance: retro-reflect, retro-kss, retro-extract) |
| Closure summary storage | close-work-cycle MEMORY phase | retro-cycle COMMIT phase |
| Governance event check | close-work-cycle MEMORY phase | close-work-cycle VALIDATE phase |

---

## Open Decisions

**None.** All decisions locked in S359 after 2 critique rounds.

---

## Implementation Steps

### Step 1: Write Failing Tests (RED)
- [ ] Create `tests/test_retro_cycle.py` with 9 tests
- [ ] Update `tests/test_observation_capture_cycle.py` (2 tests: assert retro-cycle not obs-capture)
- [ ] Update `tests/test_memory_ceremonies.py`:
  - `TestCloseWorkCycleComposition`: assert retro-cycle before VALIDATE
  - `test_registry_has_three_memory_ceremonies`: change expected set to `{"retro", "observation-triage", "memory-commit"}`
- [ ] Update `tests/test_ceremony_retrofit.py`:
  - Add "retro-cycle" to EXISTING_CEREMONY_SKILLS
  - `test_registry_count_still_20`: count stays 20 (retro-cycle replaces obs-capture in registry)
- [ ] Verify all new/updated tests fail

### Step 2: Layer 1 - Create retro-cycle SKILL.md (GREEN for 7 tests)
- [ ] Create `.claude/skills/retro-cycle/SKILL.md` with full frontmatter contract
- [ ] Include all 4 phases, computable predicate, evidence anchoring, escape hatches
- [ ] Include consumer migration table, composition map, quick reference
- [ ] Tests: test_retro_cycle_skill_exists through test_retro_cycle_has_provenance_tags pass

### Step 3: Layer 2 - Update close-work-cycle (GREEN for 1 more test)
- [ ] Document retro-cycle as predecessor (NOT entry gate that close-work-cycle invokes -- /close invokes retro-cycle separately, then invokes close-work-cycle)
- [ ] Reorder chain: RETRO -> VALIDATE -> ARCHIVE -> CHAIN
- [ ] Update frontmatter `description` to reflect new phase chain (remove "MEMORY" reference)
- [ ] Move governance event check to VALIDATE, add dod_relevant_findings handling
- [ ] Remove MEMORY phase section
- [ ] Update all tables (Composition Map, Quick Reference, Key Design Decisions, Related)
- [ ] Update close-work-cycle-agent.md (4 references)
- [ ] Test: test_close_work_cycle_references_retro_cycle passes

### Step 4: Layer 3 - Update /close command + session-end (GREEN for 1 more test)
- [ ] Replace observation-capture-cycle in close.md with retro-cycle
- [ ] Update session-end-ceremony SKILL.md line 96: change to "retro-cycle is invoked during /close -- no separate invocation needed at session-end for closed items"
- [ ] Test: test_close_command_invokes_retro_cycle passes

### Step 5: Layer 4 - Deprecate + registries
- [ ] Add `deprecated: true` to observation-capture-cycle frontmatter (NOT `stub: true` -- avoids breaking test_existing_skills_not_marked_stub)
- [ ] Add deprecation notice to body
- [ ] Replace observation-capture entry with retro-cycle in ceremony_registry.yaml (count stays 20)
- [ ] Add retro-cycle to manifest.yaml, update skill count comment from 33 to 34
- [ ] Update skills README.md (add retro-cycle, mark obs-capture deprecated)
- [ ] Test: test_ceremony_retrofit.py passes (retro-cycle in EXISTING list)

### Step 6: Integration Verification
- [ ] Run full affected test suite: `pytest tests/test_retro_cycle.py tests/test_observation_capture_cycle.py tests/test_memory_ceremonies.py tests/test_ceremony_retrofit.py -v`
- [ ] Run full test suite for regressions
- [ ] Grep verification: `observation-capture-cycle` in active consumers = 0

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Missed consumer references | Med | Layer 0 grep sweep (52 files found, ~8 active); Layer 4 verification grep |
| Test count assertion in ceremony_retrofit | Low | Add retro-cycle to EXISTING_CEREMONY_SKILLS list |
| Memory ceremony count assertion | Low | Update expected count in test_memory_ceremonies.py |
| WORK-143 depends on provenance tag contract | Med | Define tags clearly in Layer 1; WORK-143 reads from retro-cycle SKILL.md |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 361 | 2026-02-13 | - | In Progress | Plan authored, L1-L2 complete, tests written |
| 362 | 2026-02-13 | - | Complete | L3-L5 complete, YAML fix, CHAIN fixture fix, CHECK passed |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| retro-cycle skill with input/output contract | [ ] | SKILL.md exists, frontmatter valid |
| 4 REFLECT dimensions with evidence anchoring | [ ] | WCBB/WSY/WDN/WMI sections present |
| DERIVE phase K/S/S with proportional scaling | [ ] | DERIVE section with trivial/substantial |
| EXTRACT phase bugs/features with provenance tags | [ ] | EXTRACT section with confidence levels |
| COMMIT phase all outputs with no dedup | [ ] | COMMIT section with 3 provenance tags |
| Computable predicate for threshold | [ ] | Phase 0 section with 4 conditions |
| Escape hatch with governance logging | [ ] | skip_retro documented |
| DoD-relevant findings flow to VALIDATE | [ ] | dod_relevant_findings in output contract |
| close-work-cycle updated | [ ] | RETRO entry gate, no MEMORY phase |
| /close command updated | [ ] | retro-cycle reference, no obs-capture |
| observation-capture-cycle deprecated | [ ] | deprecated: true in frontmatter |
| Consumer migration table | [ ] | Table in retro-cycle SKILL.md |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/retro-cycle/SKILL.md` | New file, full ceremony contract | [ ] | |
| `.claude/skills/close-work-cycle/SKILL.md` | RETRO entry gate, no MEMORY phase | [ ] | |
| `.claude/agents/close-work-cycle-agent.md` | retro-cycle references | [ ] | |
| `.claude/commands/close.md` | retro-cycle invocation | [ ] | |
| `.claude/skills/session-end-ceremony/SKILL.md` | retro-cycle reference | [ ] | |
| `.claude/skills/observation-capture-cycle/SKILL.md` | deprecated: true | [ ] | |
| `.claude/haios/manifest.yaml` | retro-cycle entry | [ ] | |
| `.claude/haios/config/ceremony_registry.yaml` | retro-cycle entry | [ ] | |
| `.claude/skills/README.md` | retro-cycle listed, obs-capture deprecated | [ ] | |
| `tests/test_retro_cycle.py` | 9 tests, all pass | [ ] | |
| `Grep: observation-capture-cycle` in active consumers | Zero stale references | [ ] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass (all 15 new/updated)
- [ ] **MUST:** All 12 WORK.md deliverables verified complete
- [ ] **Runtime consumer exists** (/close command invokes retro-cycle)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** Consumer verification complete (zero stale observation-capture-cycle references in active consumers)
- [ ] Ground Truth Verification completed above

---

## References

- docs/work/active/WORK-142/WORK.md (design specification, S359 lock)
- .claude/haios/epochs/E2_6/retro-synthesis.md (S359 retro trend analysis)
- .claude/skills/observation-capture-cycle/SKILL.md (replaced by this work)
- .claude/skills/close-work-cycle/SKILL.md (primary consumer)
- .claude/commands/close.md (command consumer)
- REQ-CEREMONY-001, REQ-CEREMONY-002, REQ-FEEDBACK-001
- REQ-LIFECYCLE-004 (chaining is caller choice)
- INV-059 (completion mode bias - cognitive separation rationale)
- WORK-143 (companion: triage consumer update)

---
