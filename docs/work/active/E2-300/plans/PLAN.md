---
template: implementation_plan
status: complete
date: 2026-01-17
backlog_id: E2-300
title: ContextLoader S17.3 Spec Alignment
author: Hephaestus
lifecycle_phase: plan
session: 201
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-18T10:32:53'
---
# Implementation Plan: ContextLoader S17.3 Spec Alignment

@docs/README.md
@docs/epistemic_state.md

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

Align ContextLoader's GroundedContext dataclass with INV-052 S17.3 spec (L0-L3 layers with proper types) while maintaining backward compatibility.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `.claude/haios/modules/context_loader.py`, `tests/test_context_loader.py` |
| Lines of code affected | ~459 | `wc -l`: context_loader.py (194) + test_context_loader.py (265) |
| New files to create | 0 | Refactor only |
| Tests to write | 3 | Spec alignment tests |
| Dependencies | 1 | coldstart.md skill uses ContextLoader output |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | coldstart skill consumes GroundedContext |
| Risk of regression | Low | 17 existing tests cover current behavior |
| External dependencies | Low | No external services |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Design decision | 15 min | High |
| Tests + implementation | 45 min | High |
| Verification | 15 min | High |
| **Total** | 75 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/modules/context_loader.py:24-37 - Current GroundedContext
@dataclass
class GroundedContext:
    """Result of context loading - L0-L4 grounding."""
    session_number: int
    prior_session: Optional[int] = None
    l0_telos: str = ""         # WHY - Mission, Prime Directive
    l1_principal: str = ""     # WHO - Operator constraints
    l2_intent: str = ""        # WHAT - Goals, trade-offs
    l3_requirements: str = ""  # HOW - Principles, boundaries
    l4_implementation: str = "" # WHAT to build - Architecture
    checkpoint_summary: str = ""
    strategies: List[Dict[str, Any]] = field(default_factory=list)
    ready_work: List[str] = field(default_factory=list)
```

**Behavior:** Loads L0-L4 manifesto files as strings.

**Result:** Field names don't match S17.3 spec. L2/L3 are strings instead of dicts. Tests and cold start skill use manifesto naming.

### Desired State (per S17.3 spec)

```python
# .claude/haios/modules/context_loader.py - S17.3 aligned GroundedContext
@dataclass
class GroundedContext:
    """Result of context loading - L0-L3 grounding per S17.3."""
    session_number: int
    prior_session: Optional[int] = None
    l0_north_star: str = ""     # Mission, principles
    l1_invariants: str = ""     # Patterns, anti-patterns
    l2_operational: Dict[str, Any] = field(default_factory=dict)  # Status, phase, milestone
    l3_session: Dict[str, Any] = field(default_factory=dict)      # Checkpoint, work context
    strategies: List[Dict[str, Any]] = field(default_factory=list)
    ready_work: List[str] = field(default_factory=list)
    # Backward compat aliases (read-only properties)
```

**Behavior:** Matches S17.3 spec with proper types. Provides backward-compat properties for existing consumers.

**Result:** Spec alignment while maintaining backward compatibility for coldstart skill.

---

## Tests First (TDD)

### Test 1: S17.3 Field Names Exist
```python
def test_grounded_context_has_s173_fields():
    """GroundedContext has S17.3 spec field names."""
    from context_loader import GroundedContext
    import dataclasses
    fields = {f.name for f in dataclasses.fields(GroundedContext)}
    s173_required = {"l0_north_star", "l1_invariants", "l2_operational", "l3_session"}
    assert s173_required <= fields
```

### Test 2: L2/L3 Are Dicts
```python
def test_l2_l3_are_dicts():
    """L2 and L3 fields are dicts per S17.3 spec."""
    from context_loader import GroundedContext
    ctx = GroundedContext(session_number=1)
    assert isinstance(ctx.l2_operational, dict)
    assert isinstance(ctx.l3_session, dict)
```

### Test 3: Backward Compatibility Properties
```python
def test_backward_compat_properties():
    """Old field names work as aliases for backward compat."""
    from context_loader import GroundedContext
    ctx = GroundedContext(session_number=1, l0_north_star="mission")
    # Old name should still work via property
    assert ctx.l0_telos == "mission"  # Alias for l0_north_star
```

---

## Detailed Design

### Strategy: Spec-First with Backward Compat

The S17.3 spec defines a 4-layer context model (L0-L3). Current implementation uses 5 layers (L0-L4) with different semantics. Strategy:

1. **Rename fields** to match S17.3 spec names
2. **Change L2/L3 types** from `str` to `dict` per spec
3. **Add backward-compat properties** so existing consumers work
4. **Remove L4** (spec doesn't have it; it's redundant with L3)

### Exact Code Change

**File:** `.claude/haios/modules/context_loader.py`
**Location:** Lines 24-37 (GroundedContext dataclass)

**Diff:**
```diff
@dataclass
class GroundedContext:
-    """Result of context loading - L0-L4 grounding."""
+    """Result of context loading - L0-L3 grounding per S17.3."""
     session_number: int
     prior_session: Optional[int] = None
-    l0_telos: str = ""         # WHY - Mission, Prime Directive
-    l1_principal: str = ""     # WHO - Operator constraints
-    l2_intent: str = ""        # WHAT - Goals, trade-offs
-    l3_requirements: str = ""  # HOW - Principles, boundaries
-    l4_implementation: str = "" # WHAT to build - Architecture
+    l0_north_star: str = ""     # Mission, principles
+    l1_invariants: str = ""     # Patterns, anti-patterns
+    l2_operational: Dict[str, Any] = field(default_factory=dict)  # Status, phase, milestone
+    l3_session: Dict[str, Any] = field(default_factory=dict)      # Checkpoint, work context
     checkpoint_summary: str = ""
     strategies: List[Dict[str, Any]] = field(default_factory=list)
     ready_work: List[str] = field(default_factory=list)
+
+    # Backward-compat aliases (read-only)
+    @property
+    def l0_telos(self) -> str:
+        return self.l0_north_star
+    @property
+    def l1_principal(self) -> str:
+        return self.l1_invariants
```

**File:** `.claude/haios/modules/context_loader.py`
**Location:** Lines 106-120 (load_context method)

**Diff:**
```diff
     def load_context(self, trigger: str = "coldstart") -> GroundedContext:
         session, prior = self.compute_session_number()
         ctx = GroundedContext(
             session_number=session,
             prior_session=prior,
-            l0_telos=self._read_manifesto_file("L0-telos.md"),
-            l1_principal=self._read_manifesto_file("L1-principal.md"),
-            l2_intent=self._read_manifesto_file("L2-intent.md"),
-            l3_requirements=self._read_manifesto_file("L3-requirements.md"),
-            l4_implementation=self._read_manifesto_file("L4-implementation.md"),
+            l0_north_star=self._read_manifesto_file("L0-telos.md"),  # Keep file names
+            l1_invariants=self._read_manifesto_file("L1-principal.md"),
+            l2_operational=self._build_operational_context(),  # NEW
+            l3_session=self._build_session_context(),          # NEW
             checkpoint_summary=self._get_latest_checkpoint(),
             strategies=self._get_strategies(trigger),
             ready_work=self._get_ready_work(),
         )
         return ctx
```

### New Methods

```python
def _build_operational_context(self) -> Dict[str, Any]:
    """Build L2 operational context dict per S17.3."""
    status = self.generate_status(slim=True)
    return {
        "milestone": status.get("milestone", "unknown"),
        "phase": status.get("work_cycle", {}).get("phase"),
        "active_work": status.get("active_work", []),
    }

def _build_session_context(self) -> Dict[str, Any]:
    """Build L3 session context dict per S17.3."""
    return {
        "checkpoint_summary": self._get_latest_checkpoint(),
        "ready_work": self._get_ready_work(),
    }
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Keep manifesto file names | L0-telos.md → l0_north_star | Avoids file rename/migration; field name change is sufficient |
| Add backward-compat properties | @property aliases | Existing coldstart.md may reference old names; graceful migration |
| L2/L3 as dicts | Match spec types | S17.3 spec says dict; enables structured data |
| Remove L4 from dataclass | No L4 in spec | S17.3 has L0-L3 only; L4 content folded into L3.session |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Consumer uses old field name | Backward-compat property returns new field value | Test 3 |
| L2/L3 empty | Default to empty dict | Test 2 |
| Status file missing | _build_operational_context returns empty dict | Existing error handling |

### Open Questions

**Q: Should we update coldstart.md skill to use new field names?**

Document discrepancy only. Skill update can be separate work item if needed. Backward-compat properties keep it working.

---

## Open Decisions (MUST resolve before implementation)

No open decisions. Work item `operator_decisions` field is empty.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| N/A | N/A | N/A | No blocking decisions |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 3 S17.3 alignment tests to `tests/test_context_loader.py`
- [ ] Verify tests fail (red) - fields don't exist yet

### Step 2: Update GroundedContext Dataclass
- [ ] Rename fields: l0_telos→l0_north_star, l1_principal→l1_invariants
- [ ] Change L2/L3 types: str→Dict[str, Any]
- [ ] Remove l4_implementation field
- [ ] Add backward-compat @property aliases
- [ ] Tests 1-3 pass (green)

### Step 3: Update load_context Method
- [ ] Add `_build_operational_context()` method
- [ ] Add `_build_session_context()` method
- [ ] Update load_context to use new field names and methods

### Step 4: Update Existing Tests
- [ ] Update `test_grounded_context_has_required_fields` for S17.3 fields
- [ ] Verify all 17+ existing tests still pass

### Step 5: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite (no regressions)

### Step 6: Consumer Verification
- [ ] Grep for `l0_telos|l1_principal|l2_intent|l3_requirements|l4_implementation` in skills
- [ ] Document which consumers use old names (they'll work via backward-compat)

### Step 7: README Sync
- [ ] Update `.claude/haios/modules/README.md` if it describes ContextLoader

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking coldstart.md skill | Medium | Backward-compat properties maintain old field names |
| Test churn | Low | Update tests to use new names; aliases keep old tests passing |
| L2/L3 dict structure wrong | Low | Start with minimal structure; can extend later |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/E2-300/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Review S17.3 spec layer definitions | [ ] | Read SECTION-17-MODULAR-ARCHITECTURE.md |
| Align ContextLoader implementation with spec | [ ] | Field names match, L2/L3 are dicts |
| Document discrepancies or rationale for deviations | [ ] | Key Design Decisions table in plan |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/context_loader.py` | S17.3 field names, L2/L3 as dict | [ ] | |
| `tests/test_context_loader.py` | 3 new S17.3 tests + existing pass | [ ] | |
| Grep: `l2_intent\|l3_requirements\|l4_implementation` in .claude/ | Zero references in code (allowed in comments) | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_context_loader.py -v
# Expected: 20+ tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

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

- @docs/work/archive/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md (S17.3 spec)
- @docs/work/archive/E2-254/observations.md (source observation)
- Memory concept 80655 (prior observation about spec mismatch)

---
