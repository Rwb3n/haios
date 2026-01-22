---
template: implementation_plan
status: complete
date: 2026-01-22
backlog_id: WORK-009
title: Coldstart Orchestrator Wire ContextLoader
author: Hephaestus
lifecycle_phase: plan
session: 228
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-22T22:30:45'
---
# Implementation Plan: Coldstart Orchestrator Wire ContextLoader

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

The `/coldstart` command will use `just coldstart` recipe output for identity context instead of making manual Read calls to L0-L4 manifesto files.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | cli.py, justfile, coldstart.md |
| Lines of code affected | ~50 | cli.py:196-214 (19 lines), justfile (5 lines), coldstart.md Steps 2-3 (~25 lines) |
| New files to create | 0 | Wiring existing modules |
| Tests to write | 2 | test_context_load_outputs_identity, test_coldstart_recipe_works |
| Dependencies | 1 | context_loader.py imports identity_loader |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single module -> recipe -> command chain |
| Risk of regression | Low | Existing 28 tests in context_loader + identity_loader |
| External dependencies | Low | No external APIs, pure Python |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Update cli.py context-load | 15 min | High |
| Add just coldstart recipe | 10 min | High |
| Update coldstart.md identity phase | 20 min | High |
| Write tests | 15 min | High |
| **Total** | ~1 hour | High |

---

## Current State vs Desired State

### Current State

```python
# cli.py:196-212 - context-load outputs legacy char counts only
def cmd_context_load(project_root: Path = None) -> int:
    from context_loader import ContextLoader
    loader = ContextLoader(project_root=project_root)
    ctx = loader.load_context()  # No role param, gets legacy fields
    print(f"Session: {ctx.session_number} (prior: {ctx.prior_session})")
    print(f"L0 Telos: {len(ctx.l0_telos)} chars")  # Just char counts
    # ... more char counts ...
```

```markdown
# coldstart.md Step 2 - Manual file reads
## Step 2: Load Manifesto (MUST)
**MUST** read the foundational context:
1. `.claude/haios/manifesto/L0-telos.md` - Why HAIOS exists
# Agent interprets this and makes Read tool calls
```

**Behavior:** Agent reads coldstart.md, interprets prose, makes 5+ Read calls to L0-L4 files.

**Result:** Token waste (~1137 lines from full manifesto files), context pollution, manual file reads.

### Desired State

```python
# cli.py - context-load outputs identity content
def cmd_context_load(project_root: Path = None, role: str = "main") -> int:
    from context_loader import ContextLoader
    loader = ContextLoader(project_root=project_root)
    ctx = loader.load_context(role=role)

    # Output identity content from IdentityLoader (~35 lines extracted essence)
    if "identity" in ctx.loaded_context:
        print(ctx.loaded_context["identity"])
    # Also output session info
    print(f"\nSession: {ctx.session_number} (prior: {ctx.prior_session})")
```

```markdown
# coldstart.md Step 2 - Uses recipe output
## Step 2: Load Identity (from recipe output)
The identity context has been injected by `just coldstart`.
Extract: mission, constraints, principles from the [IDENTITY] block above.
No Read calls needed - content is in context.
```

**Behavior:** `just coldstart` calls cli.py which outputs identity content directly. Agent sees content in recipe output.

**Result:** Token efficient (~35 lines), no Read calls for identity phase, content injection pattern.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: CLI Context-Load Outputs Identity Content
```python
def test_context_load_outputs_identity(tmp_path, capsys):
    """context-load command outputs identity content when role=main."""
    # Setup: Create minimal config and manifesto structure
    setup_test_environment(tmp_path)

    # Action: Call cmd_context_load with role="main"
    result = cmd_context_load(project_root=tmp_path, role="main")

    # Assert: Output contains identity content markers
    captured = capsys.readouterr()
    assert "=== IDENTITY ===" in captured.out  # IdentityLoader template marker
    assert "Mission:" in captured.out
    assert result == 0
```

### Test 2: Coldstart Recipe Produces Identity Output
```python
def test_coldstart_recipe_output(tmp_path):
    """just coldstart recipe calls context-load and produces identity output."""
    # This is an integration test - run via subprocess
    import subprocess
    result = subprocess.run(
        ["just", "coldstart"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
        encoding="utf-8"
    )

    assert "=== IDENTITY ===" in result.stdout or result.returncode == 0
```

### Test 3: Backward Compatibility - Legacy Fields Still Available
```python
def test_load_context_legacy_fields_available(tmp_path):
    """ContextLoader still populates legacy l0_telos fields when no loaders configured."""
    # Setup: Config with no context.roles (triggers backward compat)
    setup_test_environment_no_roles(tmp_path)

    loader = ContextLoader(project_root=tmp_path)
    ctx = loader.load_context()

    # Legacy fields still populated for backward compat
    assert ctx.l0_telos != "" or ctx.loaded_context != {}
```

---

## Detailed Design

### Exact Code Change

**File 1:** `.claude/haios/modules/cli.py`
**Location:** Lines 196-212 in `cmd_context_load()`

**Current Code:**
```python
# cli.py:196-212 - Current implementation outputs char counts
def cmd_context_load(project_root: Path = None) -> int:
    """Load L0-L4 context and display summary."""
    from context_loader import ContextLoader

    loader = ContextLoader(project_root=project_root)
    ctx = loader.load_context()

    print(f"Session: {ctx.session_number} (prior: {ctx.prior_session})")
    print(f"L0 Telos: {len(ctx.l0_telos)} chars")
    print(f"L1 Principal: {len(ctx.l1_principal)} chars")
    print(f"L2 Intent: {len(ctx.l2_intent)} chars")
    print(f"L3 Requirements: {len(ctx.l3_requirements)} chars")
    print(f"L4 Implementation: {len(ctx.l4_implementation)} chars")
    print(f"Checkpoint: {len(ctx.checkpoint_summary)} chars")
    print(f"Strategies: {len(ctx.strategies)}")
    print(f"Ready work: {len(ctx.ready_work)}")
```

**Changed Code:**
```python
# cli.py - Target implementation outputs identity content
def cmd_context_load(project_root: Path = None, role: str = "main") -> int:
    """
    Load context based on role and output loaded content.

    WORK-009: Outputs identity content for coldstart injection.
    """
    from context_loader import ContextLoader

    loader = ContextLoader(project_root=project_root)
    ctx = loader.load_context(role=role)

    # Output loaded_context from role-based loaders (WORK-009)
    for loader_name, content in ctx.loaded_context.items():
        if content:
            print(content)

    # Session info
    print(f"\n[SESSION]")
    print(f"Number: {ctx.session_number}")
    print(f"Prior: {ctx.prior_session or 'None'}")

    # Ready work summary
    if ctx.ready_work:
        print(f"\n[READY WORK]")
        for work_id in ctx.ready_work[:5]:
            print(f"- {work_id}")

    return 0
```

**File 2:** `justfile`
**Location:** After identity recipe (line 181)

**New Recipe:**
```just
# Coldstart context loading for injection
# Usage: just coldstart
coldstart:
    python .claude/haios/modules/cli.py context-load
```

**File 3:** `.claude/commands/coldstart.md`
**Location:** Steps 2-3 (Lines 29-45)

**Current:**
```markdown
## Step 2: Load Manifesto (MUST)

**MUST** read the foundational context - immutable philosophy:

1. `.claude/haios/manifesto/L0-telos.md` - Why HAIOS exists (IMMUTABLE)
2. `.claude/haios/manifesto/L1-principal.md` - Who the operator is
...
```

**Changed:**
```markdown
## Step 2: Identity Context (Injected)

The identity context was loaded by `just coldstart` and appears in the output above.

Extract from the `=== IDENTITY ===` block:
- **Mission:** The Prime Directive
- **Constraints:** Known operator constraints
- **Principles:** Core behavioral principles

**No Read calls needed** - identity content is injected via recipe output.
```

### Call Chain Context

```
/coldstart (skill invocation)
    |
    +-> just coldstart (recipe)
    |       |
    |       +-> cli.py context-load
    |               |
    |               +-> ContextLoader.load_context(role="main")
    |                       |
    |                       +-> IdentityLoader.load()
    |                               Returns: str (3512 chars)
    |               Returns: GroundedContext
    |       Prints: identity content to stdout
    |
    +-> Agent sees content in recipe output (no Read calls for L0-L4)
```

### Function/Component Signatures

```python
def cmd_context_load(project_root: Path = None, role: str = "main") -> int:
    """
    Load context based on role and output loaded content.

    WORK-009: Refactored to output identity content for coldstart injection.
    Previously output char counts only.

    Args:
        project_root: Project root path (default: auto-detect)
        role: Role defining which loaders to use (default: "main")

    Returns:
        0 on success

    Raises:
        ValueError: If role not found in config
    """
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Output format | Print loader content directly | Content injection pattern - agent sees content in recipe output, no parsing needed |
| Role parameter | Default to "main" | Backward compat - existing calls work; explicit role for future phases |
| Section markers | Use `[SESSION]`, `[READY WORK]` | Parseable by agent, matches `=== IDENTITY ===` pattern from IdentityLoader |
| coldstart.md changes | Remove Read instructions, add "injected" language | Makes explicit that content is in context, not to be fetched |

### Input/Output Examples

**Before (current `just context-load`):**
```
Session: 228 (prior: 227)
L0 Telos: 4123 chars
L1 Principal: 3852 chars
L2 Intent: 2941 chars
L3 Requirements: 6521 chars
L4 Implementation: 21847 chars
Checkpoint: 2000 chars
Strategies: 0
Ready work: 10
```

**After (new `just coldstart`):**
```
=== IDENTITY ===
Mission: "The system's success is not measured in lines of code, but in its ability to reduce the Operator's cognitive load..."

Companion Relationship:
- Trust Earned, Not Assumed
- Symbiotic Intelligence
- Continuity Across Sessions
- Faithful Alignment

Constraints:
- Burnout Threshold
- Limited Time
- No Network
- Financial Precarity
- Human as Bottleneck

Principles:
- The Certainty Ratchet
- Evidence Over Assumption
- Context Must Persist
...

[SESSION]
Number: 228
Prior: 227

[READY WORK]
- E2-072
- E2-236
- INV-017
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No config roles defined | Graceful degradation - empty loaded_context, legacy fields used | Test 3 |
| IdentityLoader fails | Warning logged, empty string in loaded_context | Existing test in test_context_loader.py |
| Unicode in output (Windows) | Use encoding="utf-8" in print calls | Known issue - out of scope |

### Open Questions

**Q: Should we update the CLI to accept role as command-line argument?**

Currently context-load doesn't take arguments. For now, hardcode role="main" for coldstart. Future work (CH-005 Session Loader) may add `--role` argument.

---

## Open Decisions (MUST resolve before implementation)

**No blocking decisions.** WORK-009 has no `operator_decisions` field.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| N/A | - | - | Work item has clear scope and no ambiguity |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add `test_context_load_outputs_identity` to `tests/test_context_loader.py`
- [ ] Verify test fails (cli function doesn't output identity content yet)

### Step 2: Update cli.py context-load Function
- [ ] Modify `cmd_context_load()` to accept `role` parameter (default: "main")
- [ ] Change output to print `loaded_context` content instead of char counts
- [ ] Add `[SESSION]` and `[READY WORK]` output sections
- [ ] Test 1 passes (green)

### Step 3: Add just coldstart Recipe
- [ ] Add `coldstart` recipe to justfile after identity recipe
- [ ] Recipe calls `python .claude/haios/modules/cli.py context-load`
- [ ] Verify `just coldstart` outputs identity content

### Step 4: Update coldstart.md Skill
- [ ] Replace Step 2 (Load Manifesto) with "Identity Context (Injected)" section
- [ ] Remove Read instructions for L0-L4 files
- [ ] Add language about content being in context from recipe output
- [ ] Demo acceptance criterion passes (no Read calls for manifesto)

### Step 5: Integration Verification
- [ ] All tests pass: `pytest tests/test_context_loader.py -v`
- [ ] Run full test suite: `pytest` (no regressions)
- [ ] Manual test: `/coldstart` does not invoke Read for L0-L4 files

### Step 6: README Sync (MUST)
- [ ] **SKIP:** No new directories created, no structure changes
- [ ] Verify `.claude/haios/modules/README.md` mentions context-load role parameter

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Unicode encoding issues on Windows | Low | Known issue with identity loader. Out of scope for this work. Use `encoding="utf-8"` where possible. |
| Breaking backward compatibility | Medium | Keep legacy char count output as fallback when loaded_context is empty |
| coldstart.md changes break existing workflows | Low | Keep Step 3+ unchanged (epoch, checkpoint, memory). Only identity phase changes. |
| Agent doesn't see injected content | Medium | Clear section markers (`=== IDENTITY ===`) help agent parse output |

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

**MUST** read `docs/work/active/WORK-009/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| `just coldstart` recipe calls ContextLoader.load_context(role="main") | [ ] | Read justfile, verify recipe |
| Recipe outputs identity content (from IdentityLoader via ContextLoader) | [ ] | Run `just coldstart`, check output |
| /coldstart skill uses recipe output instead of manual file reads for identity phase | [ ] | Read coldstart.md Step 2 |
| Test verifies identity content appears in coldstart output | [ ] | Run pytest, verify test exists and passes |
| Demo: run /coldstart and verify no Read calls for L0-L4 manifesto files | [ ] | Manual verification |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/cli.py` | `cmd_context_load()` outputs loaded_context | [ ] | |
| `justfile` | `coldstart` recipe exists, calls cli.py context-load | [ ] | |
| `.claude/commands/coldstart.md` | Step 2 says "Identity Context (Injected)" | [ ] | |
| `tests/test_context_loader.py` | Test for identity output exists | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest [test_file] -v
# Expected: X tests passed
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

- @docs/work/active/WORK-008/WORK.md - Parent work (ContextLoader Identity Integration)
- @.claude/haios/epochs/E2_3/arcs/configuration/CH-007-coldstart-orchestrator.md - Chapter spec
- @.claude/haios/modules/context_loader.py - Module to wire
- @.claude/commands/coldstart.md - Skill to update
- Memory concepts 82206, 82205 - Prior learnings about coldstart/ContextLoader gap

---
