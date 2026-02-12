---
template: implementation_plan
status: complete
date: 2026-02-12
backlog_id: WORK-133
title: "Implement Memory Ceremonies (CH-016)"
author: Hephaestus
lifecycle_phase: plan
session: 353
version: "1.5"
generated: 2026-02-12
last_updated: 2026-02-12T18:45:09
---
# Implementation Plan: Implement Memory Ceremonies (CH-016)

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: New feature, no existing code to show current state"
     - "SKIPPED: Pure documentation task, no code changes"
     - "SKIPPED: Trivial fix, single line change doesn't warrant detailed design"

     This prevents silent section deletion and ensures conscious decisions.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

All three memory ceremonies (observation-capture, observation-triage, memory-commit) will have formal ceremony contracts, non-stub implementations, governance event logging, and unit test coverage — completing CH-016 of the ceremonies arc.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/skills/memory-commit-ceremony/SKILL.md` (de-stub) |
| New files to create | 1 | `tests/test_memory_ceremonies.py` |
| Tests to write | ~6 | Contract validation, event logging, integration |
| Dependencies | 2 | `ceremony_contracts.py`, `governance_events.py` |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Skill file + test file; no module code changes |
| Risk of regression | Low | Existing ceremony tests provide safety net |
| External dependencies | Low | ingester_ingest is MCP tool (mocked in tests) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests + de-stub | 30 min | High |
| Verification passes | 15 min | High |
| **Total** | 45 min | |

---

## Current State vs Desired State

### Current State

Three memory ceremony skills exist:

1. **observation-capture-cycle** — Full implementation with contracts in frontmatter (`type: ceremony`, `input_contract`, `output_contract`, `side_effects`). Has 4 questions, hard gate on non-empty. Tests exist in `test_observation_capture_cycle.py`.

2. **observation-triage-cycle** — Full implementation with contracts in frontmatter. SCAN/TRIAGE/PROMOTE phases. Tests exist in `test_observations.py`.

3. **memory-commit-ceremony** — **Stub** (`stub: true` in frontmatter). Has contracts defined but ceremony steps are minimal (4 bullet points). No event logging. No tests.

**close-work-cycle** references observation-capture-cycle as entry gate (verified in SKILL.md line 76-79).

**ceremony_registry.yaml** lists all 3 as `has_contract: true, has_skill: true`.

### Desired State

1. **observation-capture-cycle** — No changes needed (verified complete).
2. **observation-triage-cycle** — No changes needed (verified complete).
3. **memory-commit-ceremony** — De-stubbed: `stub: true` removed, ceremony steps expanded with explicit event logging step, error handling for ingester failures.
4. **Tests** — New `test_memory_ceremonies.py` covering all 3 ceremonies' contract validity and memory-commit-ceremony behavior.
5. **CH-016** status updated to Complete with explicit deferral note on R4 (observation schema in YAML) — deferred to E2.6 assets arc. 9/10 success criteria met; R4 is an asset-typing concern outside ceremonies scope.

---

## Tests First (TDD)

File: `tests/test_memory_ceremonies.py`

### Test Utility: load_skill_frontmatter
```python
import yaml
from pathlib import Path

def load_skill_frontmatter(skill_path: str) -> dict:
    """Parse YAML frontmatter from a skill markdown file.

    Reads the content between the first two '---' delimiters
    and returns the parsed YAML dict.
    """
    content = Path(skill_path).read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"No YAML frontmatter found in {skill_path}")
    return yaml.safe_load(parts[1])
```

### Test 1: All three memory ceremony skills have valid contracts
```python
def test_observation_capture_has_ceremony_contract():
    """observation-capture-cycle has type: ceremony and valid contracts."""
    skill = load_skill_frontmatter(".claude/skills/observation-capture-cycle/SKILL.md")
    assert skill["type"] == "ceremony"
    assert skill["category"] == "memory"
    contract = CeremonyContract.from_frontmatter(skill)
    assert len(contract.input_contract) >= 1
    assert len(contract.output_contract) >= 1
    assert len(contract.side_effects) >= 1

def test_observation_triage_has_ceremony_contract():
    """observation-triage-cycle has type: ceremony and valid contracts."""
    skill = load_skill_frontmatter(".claude/skills/observation-triage-cycle/SKILL.md")
    assert skill["type"] == "ceremony"
    assert skill["category"] == "memory"
    contract = CeremonyContract.from_frontmatter(skill)
    assert len(contract.output_contract) >= 1

def test_memory_commit_has_ceremony_contract():
    """memory-commit-ceremony has type: ceremony and valid contracts."""
    skill = load_skill_frontmatter(".claude/skills/memory-commit-ceremony/SKILL.md")
    assert skill["type"] == "ceremony"
    assert skill["category"] == "memory"
    contract = CeremonyContract.from_frontmatter(skill)
    assert len(contract.input_contract) >= 1
    assert len(contract.output_contract) >= 1
```

### Test 2: memory-commit-ceremony is not a stub
```python
def test_memory_commit_not_stub():
    """memory-commit-ceremony must not have stub: true."""
    skill = load_skill_frontmatter(".claude/skills/memory-commit-ceremony/SKILL.md")
    assert skill.get("stub") is not True, "memory-commit-ceremony must not be a stub"
```

### Test 3: memory-commit-ceremony has event logging step
```python
def test_memory_commit_has_event_logging():
    """memory-commit-ceremony documents MemoryCommitted event logging."""
    content = Path(".claude/skills/memory-commit-ceremony/SKILL.md").read_text()
    assert "MemoryCommitted" in content or "log_ceremony_event" in content or "governance-events" in content
```

### Test 4: memory-commit-ceremony has error handling
```python
def test_memory_commit_has_error_handling():
    """memory-commit-ceremony documents failure handling."""
    content = Path(".claude/skills/memory-commit-ceremony/SKILL.md").read_text()
    assert "error" in content.lower() or "fail" in content.lower()
```

### Test 5: close-work-cycle composes observation-capture
```python
def test_close_work_cycle_composes_observation_capture():
    """close-work-cycle references observation-capture-cycle as entry gate."""
    content = Path(".claude/skills/close-work-cycle/SKILL.md").read_text()
    assert "observation-capture-cycle" in content
    # observation-capture must come before VALIDATE phase
    obs_pos = content.find("observation-capture-cycle")
    validate_pos = content.find("### 1. VALIDATE Phase")
    assert obs_pos < validate_pos
```

### Test 6: ceremony registry lists all 3 memory ceremonies
```python
def _has_category(entry, cat):
    """Check if registry entry has category (handles str or list)."""
    if isinstance(entry.category, list):
        return cat in entry.category
    return entry.category == cat

def test_registry_has_three_memory_ceremonies():
    """ceremony_registry.yaml has all 3 memory ceremonies with contracts."""
    registry = load_ceremony_registry()
    memory_ceremonies = [c for c in registry.ceremonies if _has_category(c, "memory")]
    assert len(memory_ceremonies) == 3
    names = {c.name for c in memory_ceremonies}
    assert names == {"observation-capture", "observation-triage", "memory-commit"}
    for c in memory_ceremonies:
        assert c.has_contract is True
        assert c.has_skill is True
```

---

## Detailed Design

### Change 1: De-stub memory-commit-ceremony

**File:** `.claude/skills/memory-commit-ceremony/SKILL.md`

**Current frontmatter (line 6):**
```yaml
stub: true
```

**Change:** Remove `stub: true` line entirely.

**Current body (lines 62-68):**
```markdown
## Ceremony Steps

1. Validate content is non-empty
2. Call ingester_ingest with content and source_path
3. Log MemoryCommit ceremony event
4. Report concept IDs to operator
```

**Changed body:** Expand with explicit subsections for each step, add error handling, add event logging details:

```markdown
## Ceremony Steps

### Step 1: Validate Input
- Verify `content` is non-empty string (BLOCK if empty)
- Verify `source_path` is non-empty string (BLOCK if empty)
- Default `content_type_hint` to "doxa" if not provided

### Step 2: Store to Memory
- Call `ingester_ingest` MCP tool:
  - `content`: The learning content
  - `source_path`: Provenance path (e.g., "closure:WORK-133")
  - `content_type_hint`: Classification hint
- Capture returned concept IDs

### Step 3: Log Governance Event
- Log `MemoryCommitted` event to governance-events.jsonl:
  ```json
  {
    "type": "MemoryCommitted",
    "ceremony": "memory-commit",
    "source_path": "closure:WORK-133",
    "concept_count": 2,
    "timestamp": "2026-02-12T18:00:00"
  }
  ```

### Step 4: Report Results
- Report concept IDs to operator
- Update work item `memory_refs` field with returned IDs

## Error Handling

| Error | Handling |
|-------|----------|
| Empty content | BLOCK — return `{success: false, error: "Content is empty"}` |
| Empty source_path | BLOCK — return `{success: false, error: "Source path is empty"}` |
| ingester_ingest failure | WARN — log error, return `{success: false, error: "<message>"}` |
| No concept IDs returned | WARN — log warning, return `{success: true, concept_ids: []}` |
```

### Call Chain Context

```
/close WORK-133
    |
    +-> observation-capture-cycle   (entry gate — formal ceremony skill invocation)
    +-> dod-validation-cycle        (DoD check)
    +-> close-work-cycle
            |
            +-> VALIDATE phase
            +-> ARCHIVE phase
            +-> MEMORY phase
            |       |
            |       +-> ingester_ingest (MCP tool — called directly, NOT via ceremony skill)
            |       +-> governance event check
            |
            +-> CHAIN phase
```

**Note (Critique A8):** close-work-cycle's MEMORY phase currently calls `ingester_ingest` directly — it does NOT invoke `Skill(skill="memory-commit-ceremony")`. The memory-commit-ceremony skill documents the intended ceremony steps and contracts, but formal composition (close-work-cycle delegating to the ceremony skill) is a future improvement. The ceremony skill serves as the documented contract and instructions for agents performing memory commits in any context, not only during work closure.

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Skill-level change only | No new Python modules | Memory-commit is a skill (agent instructions), not code. The ceremony_contracts.py already validates contracts from frontmatter. |
| Event type name | `MemoryCommitted` | Consistent with existing event naming pattern (CeremonyStart, CeremonyEnd) |
| Error handling in skill | Document behavior, don't add code | Skills are agent instructions. Error handling is documented for the agent to follow. |
| No observation schema in YAML | Defer to E2.6 | CH-016 lists this in success criteria but it's an asset-typing concern (deferred arc). Observations are already stored in markdown. |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| ingester_ingest MCP tool unavailable | Warn, continue without memory storage | Test 4 (error handling) |
| Duplicate content submitted | ingester handles dedup; ceremony doesn't filter | N/A (ingester concern) |
| Very large content string | Pass through to ingester; no truncation | N/A |

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Observation schema in YAML (CH-016 R4) | Implement now, Defer to E2.6 | Defer to E2.6 | Asset typing is in the deferred assets arc. Current markdown format works. |

---

## Implementation Steps

### Step 1: Write Failing Tests (RED)
- [ ] Create `tests/test_memory_ceremonies.py` with all 6 tests from Tests First section
- [ ] Verify tests 1-3 pass (contracts already exist), test 2 fails (stub: true), tests 4-6 verify existing state

### Step 2: De-stub memory-commit-ceremony (GREEN)
- [ ] Remove `stub: true` from frontmatter
- [ ] Expand ceremony steps with explicit subsections (validate, store, log event, report)
- [ ] Add error handling section
- [ ] Add MemoryCommitted event documentation
- [ ] Test 2 (not stub) passes
- [ ] Tests 3-4 (event logging, error handling) pass

### Step 3: Run Full Test Suite
- [ ] Run existing observation tests: `pytest tests/test_observation_capture_cycle.py tests/test_observations.py -v`
- [ ] Run new ceremony tests: `pytest tests/test_memory_ceremonies.py -v`
- [ ] Run full suite to check for regressions

### Step 4: Update CH-016 Chapter Status
- [ ] Update CH-016-MemoryCeremonies.md status to Complete
- [ ] Add WORK-133 to Work Items field

### Step 5: Consumer Verification
- [ ] **SKIPPED:** No migration or rename — skill path unchanged, no consumers to update

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Observation schema deferred breaks CH-016 success criteria | Low | CH-016 lists 10 criteria; schema is asset-typing (E2.6 scope). 9/10 achievable. Document deferral. |
| Memory-commit skill expansion changes agent behavior | Low | Skill is instructions, not code. Expanding instructions refines behavior, doesn't break it. |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| De-stub memory-commit-ceremony | [ ] | `stub: true` removed from frontmatter |
| Verify observation-capture-cycle contract | [ ] | Test 1a passes |
| Verify observation-triage-cycle contract | [ ] | Test 1b passes |
| Verify close-work-cycle composes observation-capture | [ ] | Test 5 passes |
| Add MemoryCommitted event logging | [ ] | Test 3 passes |
| Unit tests for memory-commit-ceremony | [ ] | Tests 2-4 pass |
| Verify existing tests pass | [ ] | `pytest tests/test_observation_capture_cycle.py tests/test_observations.py` green |
| Update CH-016 status to Complete | [ ] | CH-016 file shows status: Complete |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/memory-commit-ceremony/SKILL.md` | No `stub: true`, expanded steps, error handling, event logging | [ ] | |
| `tests/test_memory_ceremonies.py` | 6+ tests, all passing | [ ] | |
| `.claude/haios/epochs/E2_5/arcs/ceremonies/CH-016-MemoryCeremonies.md` | Status: Complete, Work Items: WORK-133 | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_memory_ceremonies.py tests/test_observation_capture_cycle.py tests/test_observations.py -v
# Expected: all tests pass
```

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- CH-016: `.claude/haios/epochs/E2_5/arcs/ceremonies/CH-016-MemoryCeremonies.md`
- ADR-033: Work Item Lifecycle Governance
- REQ-CEREMONY-001, REQ-CEREMONY-002: L4 functional requirements
- REQ-MEMORY-001: Memory storage with provenance
- Critique assumptions A20-A22: `.claude/haios/epochs/E2_5/arcs/ceremonies/CRITIQUE.md`

---
