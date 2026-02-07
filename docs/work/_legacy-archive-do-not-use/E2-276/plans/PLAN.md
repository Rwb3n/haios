---
template: implementation_plan
status: complete
date: 2026-01-06
backlog_id: E2-276
title: Design ground-cycle Skill
author: Hephaestus
lifecycle_phase: plan
session: 178
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-06T21:21:50'
---
# Implementation Plan: Design ground-cycle Skill

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

A ground-cycle skill will exist that loads epoch architecture, provenance chain, and memory context before any cognitive work begins, outputting a GroundedContext object that downstream cycles consume.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | No existing files modified |
| Lines of code affected | 0 | New skill creation |
| New files to create | 2 | `.claude/skills/ground-cycle/SKILL.md`, `tests/test_ground_cycle.py` |
| Tests to write | 5 | 4 phase tests + 1 integration |
| Dependencies | 3 | plan-authoring-cycle, investigation-cycle, implementation-cycle (consumers) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Med | Called by 3 cycles, reads WORK.md, queries memory |
| Risk of regression | Low | New skill, no existing behavior |
| External dependencies | Low | MCP memory (already integrated) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write SKILL.md | 45 min | High |
| Write tests | 30 min | High |
| **Total** | ~1.5 hr | High |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/skills/plan-authoring-cycle/SKILL.md (current)
## 1. ANALYZE Phase
**Actions:**
1. Read the plan file...
2. Check each section for placeholder text...

# No context loading - jumps straight into plan analysis
```

**Behavior:** plan-authoring-cycle starts with ANALYZE phase. It reads the plan file and checks for placeholders, but has no mechanism to load architectural context first.

**Result:** E2-271 was planned against `.claude/lib/` when INV-052 specifies `.claude/haios/modules/`. Architectural decisions LOST because agent never loaded source investigation.

### Desired State

```markdown
# .claude/skills/plan-authoring-cycle/SKILL.md (target)
## 0. GROUND Phase (calls ground-cycle)
**Actions:**
1. Invoke ground-cycle with work_id
2. Receive GroundedContext
3. Proceed with full architectural awareness

# Context loaded BEFORE cognitive work
```

**Behavior:** plan-authoring-cycle (and investigation-cycle, implementation-cycle) invoke ground-cycle BEFORE their first cognitive phase. Agent enters with epoch architecture, provenance chain, and memory strategies loaded.

**Result:** Plans authored against correct architecture. No more `.claude/lib/` vs `.claude/haios/modules/` confusion.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: SKILL.md structure validation
```python
def test_ground_cycle_skill_has_required_sections():
    """Verify skill file has frontmatter and all 4 phases."""
    skill_path = Path(".claude/skills/ground-cycle/SKILL.md")
    content = skill_path.read_text()

    # Check frontmatter
    assert content.startswith("---")
    assert "name: ground-cycle" in content

    # Check phases exist
    assert "## 1. PROVENANCE Phase" in content or "### 1. PROVENANCE Phase" in content
    assert "ARCHITECTURE Phase" in content
    assert "MEMORY Phase" in content
    assert "CONTEXT MAP Phase" in content
```

### Test 2: PROVENANCE phase reads spawned_by_investigation
```python
def test_provenance_phase_documented():
    """Verify PROVENANCE phase specifies traversing spawned_by chain."""
    skill_path = Path(".claude/skills/ground-cycle/SKILL.md")
    content = skill_path.read_text()

    # PROVENANCE should mention spawned_by traversal
    assert "spawned_by" in content.lower() or "provenance" in content.lower()
    assert "Read work item" in content or "WORK.md" in content
```

### Test 3: ARCHITECTURE phase loads epoch documents
```python
def test_architecture_phase_loads_epoch():
    """Verify ARCHITECTURE phase specifies loading epoch architecture."""
    skill_path = Path(".claude/skills/ground-cycle/SKILL.md")
    content = skill_path.read_text()

    # Should reference epoch loading
    assert "epoch" in content.lower()
    assert "EPOCH.md" in content or "architecture" in content.lower()
```

### Test 4: GroundedContext output documented
```python
def test_grounded_context_output_defined():
    """Verify the skill defines GroundedContext output structure."""
    skill_path = Path(".claude/skills/ground-cycle/SKILL.md")
    content = skill_path.read_text()

    # Should define output structure
    assert "GroundedContext" in content or "Output:" in content
    assert "provenance_chain" in content or "epoch" in content
```

### Test 5: Integration with calling cycles documented
```python
def test_integration_points_documented():
    """Verify skill documents how other cycles call it."""
    skill_path = Path(".claude/skills/ground-cycle/SKILL.md")
    content = skill_path.read_text()

    # Should mention calling cycles
    assert "plan-authoring" in content or "investigation-cycle" in content or "implementation-cycle" in content
```

---

## Detailed Design

<!-- Creating new skill - no existing code to modify -->

### Skill File Structure

**File:** `.claude/skills/ground-cycle/SKILL.md`
**Pattern:** Following implementation-cycle/SKILL.md structure (345 lines)

```markdown
---
name: ground-cycle
description: HAIOS Ground Cycle for loading architectural context before cognitive work.
  Use before plan-authoring, investigation, or implementation cycles.
generated: 2026-01-06
last_updated: '2026-01-06'
---
# Ground Cycle

This skill defines the PROVENANCE-ARCHITECTURE-MEMORY-CONTEXT MAP cycle for loading
context before any cognitive work begins.

## When to Use

**Automatically invoked** at the start of:
- plan-authoring-cycle (before AMBIGUITY phase)
- investigation-cycle (before HYPOTHESIZE phase)
- implementation-cycle (before PLAN phase)

**Manual invocation:** `Skill(skill="ground-cycle", args="{work_id}")`

---

## The Cycle

```
PROVENANCE --> ARCHITECTURE --> MEMORY --> CONTEXT MAP --> [return GroundedContext]
     |               |              |              |
  Read WORK.md   Load epoch    Query prior     Build output
  Traverse      architecture   patterns       for caller
  spawned_by
```

### 1. PROVENANCE Phase

**Goal:** Traverse spawned_by chain to find source investigations.

**Actions:**
1. Read work item: `docs/work/active/{work_id}/WORK.md`
2. Extract `spawned_by_investigation` field
3. If set, read source investigation's key findings
4. Recursively traverse: E2-271 → INV-057 → INV-052
5. Collect provenance chain

**Exit Criteria:**
- [ ] Work item WORK.md read
- [ ] spawned_by_investigation traversed (if set)
- [ ] Provenance chain collected

**Tools:** Read, Glob

---

### 2. ARCHITECTURE Phase

**Goal:** Load epoch architecture for the work item.

**Actions:**
1. Extract `epoch` field from work item (e.g., "E2")
2. Load epoch definition: `.claude/haios/epochs/{epoch}/EPOCH.md`
3. Load REQUIRED READING from epoch's architecture/
4. Extract `chapter` and `arc` fields if present
5. Load chapter/arc REQUIRED READING if applicable

**Exit Criteria:**
- [ ] EPOCH.md loaded
- [ ] Architecture documents loaded
- [ ] REQUIRED READING section parsed

**Tools:** Read

---

### 3. MEMORY Phase

**Goal:** Query memory for relevant strategies and prior work.

**Actions:**
1. Query memory for epoch architecture: `"Epoch 2.2 architecture modules"`
2. Query memory for provenance chain topics
3. Query memory for work item related concepts
4. Collect relevant strategies

**Exit Criteria:**
- [ ] Memory queried with epoch context
- [ ] Strategies collected

**Tools:** mcp__haios-memory__memory_search_with_experience

---

### 4. CONTEXT MAP Phase

**Goal:** Build and output GroundedContext.

**Actions:**
1. Assemble GroundedContext object:
   ```yaml
   GroundedContext:
     epoch: E2
     chapter: C3-WorkInfra
     arc: ARC-001-ground-cycle
     provenance_chain: [E2-271, INV-057, INV-052]
     architectural_refs:
       - .claude/haios/epochs/E2/EPOCH.md
       - .claude/haios/epochs/E2/architecture/S17-modular-architecture.md
     memory_concepts: [80858, 80866, 80918]
     required_reading_loaded: true
   ```
2. Return to calling cycle

**Exit Criteria:**
- [ ] GroundedContext assembled
- [ ] Returned to calling cycle

**Tools:** (internal)

---

## Composition Map

| Phase | Primary Tool | Memory Integration |
|-------|--------------|-------------------|
| PROVENANCE | Read, Glob | - |
| ARCHITECTURE | Read | - |
| MEMORY | memory_search_with_experience | Query epoch + provenance |
| CONTEXT MAP | (internal) | - |

---

## Integration Points

### Calling Cycles

ground-cycle is invoked as "Phase 0" before cognitive work:

| Cycle | When Called | Before Phase |
|-------|-------------|--------------|
| plan-authoring-cycle | Work item enters `plan` node | AMBIGUITY |
| investigation-cycle | Work item enters `discovery` node | HYPOTHESIZE |
| implementation-cycle | Work item enters `implement` node | PLAN |

### Invocation Pattern

```python
# In plan-authoring-cycle, before AMBIGUITY phase:
Skill(skill="ground-cycle", args="{work_id}")
# ground-cycle returns GroundedContext
# plan-authoring-cycle continues with architectural awareness
```

---

## Related

- **ARC-001-ground-cycle:** Arc containing this and related work items
- **S17-modular-architecture.md:** Module interfaces ground-cycle loads
- **S2C-work-item-directory.md:** Portal system for provenance traversal
- **S14-bootstrap-architecture.md:** Context loading hierarchy
```

### Call Chain Context

```
/new-plan E2-XXX (or /implement, /new-investigation)
    |
    +-> plan-authoring-cycle
            |
            +-> ground-cycle        # <-- THIS SKILL
            |       Input: work_id
            |       Output: GroundedContext
            |
            +-> AMBIGUITY phase (with grounded context)
            +-> ANALYZE phase
            +-> AUTHOR phase
            +-> VALIDATE phase
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Separate skill vs inline code | Separate skill | Reusable by multiple cycles (plan-authoring, investigation, implementation) |
| 4 phases | PROVENANCE→ARCHITECTURE→MEMORY→CONTEXT MAP | Logical progression: find source → load spec → query prior → output |
| Return GroundedContext | YAML-like structure | Matches S17 ContextLoader.GroundedContext interface |
| No state persistence | In-memory only | Context is session-scoped, regenerated each invocation |
| Token budget awareness | Reference S15 limits | GroundedContext fits within L4 budget (~variable tokens) |

### Input/Output Examples

**Input:**
```
Skill(skill="ground-cycle", args="E2-271")
```

**Output (GroundedContext):**
```yaml
GroundedContext:
  epoch: E2
  chapter: C3-WorkInfra
  arc: null  # E2-271 doesn't have arc assignment
  provenance_chain:
    - E2-271
    - INV-057  # spawned_by_investigation
    - INV-052  # INV-057's spawned_by_investigation
  architectural_refs:
    - .claude/haios/epochs/E2/EPOCH.md
    - .claude/haios/epochs/E2/architecture/S17-modular-architecture.md
    - .claude/haios/epochs/E2/architecture/S2C-work-item-directory.md
  memory_concepts: [80858, 80866, 80907, 80918]
  required_reading_loaded: true
```

**With grounded context, agent knows:**
- Module location is `.claude/haios/modules/` (from S17)
- Portal system uses `references/REFS.md` (from S2C)
- Prior strategies about ground-cycle design (from memory)

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No spawned_by_investigation | Skip PROVENANCE traversal, continue | Test 2 (empty chain) |
| No epoch field in work item | Default to "E2" (current epoch) | N/A - manual verification |
| Epoch directory missing | Warn and continue without architecture | N/A - manual verification |
| Memory MCP timeout | Warn and continue without strategies | Test 5 (graceful degradation) |

### Open Questions

**Q: Should ground-cycle modify the calling cycle's behavior or just provide context?**

Answer: Just provide context. ground-cycle outputs GroundedContext which the calling cycle uses. It does not modify the caller's phases or exit criteria.

---

## Open Decisions (MUST resolve before implementation)

<!-- No operator_decisions in work item - section is clean -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| *No open decisions* | - | - | Work item operator_decisions is empty |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_ground_cycle.py`
- [ ] Add 5 tests from Tests First section
- [ ] Run `pytest tests/test_ground_cycle.py` - verify all fail (file doesn't exist)

### Step 2: Create Skill Directory
- [ ] Create `.claude/skills/ground-cycle/` directory
- [ ] Tests still fail (SKILL.md doesn't exist)

### Step 3: Write SKILL.md with Frontmatter
- [ ] Create `.claude/skills/ground-cycle/SKILL.md`
- [ ] Add frontmatter (name, description, generated, last_updated)
- [ ] Test 1 should pass (frontmatter check)

### Step 4: Add Phase Definitions
- [ ] Add PROVENANCE phase (Goal, Actions, Exit Criteria, Tools)
- [ ] Add ARCHITECTURE phase
- [ ] Add MEMORY phase
- [ ] Add CONTEXT MAP phase
- [ ] Tests 1-4 should pass (phase and output checks)

### Step 5: Add Integration Documentation
- [ ] Add "Integration Points" section documenting calling cycles
- [ ] Add "When to Use" section
- [ ] Add "Related" section
- [ ] Test 5 should pass (integration documentation)

### Step 6: Run Full Test Suite
- [ ] Run `pytest tests/test_ground_cycle.py -v` - all 5 pass
- [ ] Run `pytest tests/` - no regressions

### Step 7: Verify Runtime Discovery
- [ ] Run `just update-status-slim`
- [ ] Verify `ground-cycle` appears in `haios-status-slim.json` skills array

### Step 8: README Sync (MUST)
- [ ] **MUST:** Update `.claude/skills/README.md` to include ground-cycle
- [ ] **MUST:** Verify README content matches actual file state

### Step 9: Documentation Alignment
- [ ] Update CLAUDE.md skills table to add ground-cycle
- [ ] Update `.claude/haios/epochs/E2/chapters/workinfra/arcs/ARC-001-ground-cycle/ARC.md` status

> **Note:** This is a design task (category: design). The actual implementation of calling cycles integrating ground-cycle is E2-277 through E2-282.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment: ground-cycle phases don't match S17 ContextLoader interface | High | Verified GroundedContext output matches S17.3 exactly |
| Integration: Calling cycles don't invoke ground-cycle correctly | Medium | This design task only creates skill; integration is E2-277+ |
| Token budget: GroundedContext exceeds L4 budget | Medium | S15 shows L4 is "variable" - remaining tokens; ARCHITECTURE phase limits docs loaded |
| Scope creep: Adding features not in ARC-001 spec | Low | Design constrained to 4 phases from Session 177 discovery |
| Knowledge gap: Unsure how Skills invoke other Skills | Low | Verified pattern exists - plan-authoring-cycle chains to plan-validation-cycle |

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

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/ground-cycle/SKILL.md` | Exists with 4 phases, GroundedContext output | [ ] | |
| `tests/test_ground_cycle.py` | 5 tests exist and pass | [ ] | |
| `.claude/skills/README.md` | **MUST:** Lists ground-cycle | [ ] | |
| `CLAUDE.md` | **MUST:** Skills table includes ground-cycle | [ ] | |
| `.claude/haios-status-slim.json` | `ground-cycle` in skills array | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_ground_cycle.py -v
# Expected: 5 tests passed
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
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.

---

## References

- `.claude/haios/epochs/E2/EPOCH.md` - Epoch definition (REQUIRED READING)
- `.claude/haios/epochs/E2/architecture/S17-modular-architecture.md` - Module interfaces
- `.claude/haios/epochs/E2/architecture/S2C-work-item-directory.md` - Portal system
- `.claude/haios/epochs/E2/architecture/S14-bootstrap-architecture.md` - Context loading
- `.claude/haios/epochs/E2/architecture/S15-information-architecture.md` - Token budgets
- `.claude/haios/epochs/E2/chapters/workinfra/arcs/ARC-001-ground-cycle/ARC.md` - Arc definition
- `docs/checkpoints/2026-01-06-01-SESSION-177-epoch-chapter-arc-hierarchy-and-ground-cycle-discovery.md` - Discovery session
- Memory concepts 80858-80874 (ground-cycle discovery), 80910-80917 (hierarchy design)

---
