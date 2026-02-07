---
template: implementation_plan
status: complete
date: 2025-12-29
backlog_id: E2-232
title: Anti-Pattern Checker Agent
author: Hephaestus
lifecycle_phase: plan
session: 144
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-29T11:41:28'
---
# Implementation Plan: Anti-Pattern Checker Agent

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

Create an anti-pattern-checker agent that mechanically verifies claims against the 6 L1 anti-patterns from invariants.md, returning structured JSON output with pass/fail verdicts per verification lens.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | No existing files modified |
| Lines of code affected | 0 | New file only |
| New files to create | 2 | `.claude/agents/anti-pattern-checker.md`, `tests/test_anti_pattern_checker.py` |
| Tests to write | 4 | Agent structure, output format, lens coverage, edge cases |
| Dependencies | 1 | Follows validation-agent pattern |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Standalone agent, manual invocation initially |
| Risk of regression | Low | New file, no existing code touched |
| External dependencies | Low | Only reads files via Read/Grep/Glob tools |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 15 min | High |
| Create agent file | 30 min | High |
| Verify runtime discovery | 10 min | High |
| **Total** | ~55 min | High |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/agents/ directory contains 6 agents:
# - investigation-agent.md
# - preflight-checker.md
# - schema-verifier.md
# - test-runner.md
# - validation-agent.md
# - why-capturer.md
```

**Behavior:** Claims about epoch/milestone completion are made without mechanical verification. Agent relies on self-assessment which is subject to Optimistic Confidence anti-pattern.

**Result:** Session 143 produced an incorrect claim that "Epoch 2 exit criteria are essentially met" with no evidence - operator had to manually challenge.

### Desired State

```markdown
# .claude/agents/ directory contains 7 agents:
# - anti-pattern-checker.md  <-- NEW
# - investigation-agent.md
# - preflight-checker.md
# - schema-verifier.md
# - test-runner.md
# - validation-agent.md
# - why-capturer.md
```

**Behavior:** Before major claims (epoch complete, milestone complete, criteria met), agent can invoke anti-pattern-checker to verify claims against 6 L1 anti-patterns.

**Result:** Claims are mechanically verified with evidence requirements. JSON output shows pass/fail per lens, preventing unsupported assertions from being accepted.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Agent File Structure
```python
def test_agent_file_exists():
    """Agent file must exist at expected location."""
    agent_file = Path('.claude/agents/anti-pattern-checker.md')
    assert agent_file.exists(), "Missing .claude/agents/anti-pattern-checker.md"

def test_agent_has_required_frontmatter():
    """Agent must have name, description, tools in frontmatter."""
    agent_file = Path('.claude/agents/anti-pattern-checker.md')
    content = agent_file.read_text()
    assert 'name: anti-pattern-checker' in content
    assert 'description:' in content
    assert 'tools:' in content
```

### Test 2: Verification Lenses Defined
```python
def test_agent_defines_six_lenses():
    """Agent must define all 6 L1 anti-pattern lenses."""
    agent_file = Path('.claude/agents/anti-pattern-checker.md')
    content = agent_file.read_text()
    lenses = ['assume_over_verify', 'generate_over_retrieve', 'move_fast',
              'optimistic_confidence', 'pattern_match', 'ceremonial_completion']
    for lens in lenses:
        assert lens in content or lens.replace('_', ' ') in content, f"Missing lens: {lens}"
```

### Test 3: Output Format Documented
```python
def test_agent_has_output_format():
    """Agent must document JSON output format."""
    agent_file = Path('.claude/agents/anti-pattern-checker.md')
    content = agent_file.read_text()
    assert 'Output Format' in content or '## Output' in content
    assert '"verified"' in content or 'verified' in content
    assert '"lenses"' in content or 'lenses' in content
```

### Test 4: Runtime Discovery
```python
def test_agent_discovered_by_status():
    """Agent must appear in haios-status-slim.json after update."""
    from status import get_agents
    agents = get_agents()
    assert 'anti-pattern-checker' in agents, "Agent not discovered"
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does.
     Future agents should be able to implement from this section alone.
     This section bridges the gap between tests (WHAT) and steps (HOW).

     MUST INCLUDE (per Session 88 enhancement):
     1. Actual current code that will be changed (copy from source)
     2. Exact diff/change to be made
     3. Function signature details with context
     4. Input/output examples with REAL data from the system -->

### New File: `.claude/agents/anti-pattern-checker.md`

**SKIPPED Exact Code Change:** This is a new file, not modifying existing code.

### Agent Structure (following validation-agent pattern)

```yaml
---
name: anti-pattern-checker
description: Verify claims against 6 L1 anti-patterns before acceptance. Use for epoch,
  milestone, or major completion claims.
tools: Read, Grep, Glob
generated: '2025-12-29'
last_updated: '2025-12-29T...'
---
```

### The 6 Verification Lenses (from invariants.md:83-95)

| Lens ID | Anti-Pattern | Question | Evidence Requirement | Failure Indicator |
|---------|--------------|----------|---------------------|-------------------|
| `assume_over_verify` | Assume over verify | "What evidence was cited for this claim?" | File:line ref or concept ID | No evidence, declarative claim only |
| `generate_over_retrieve` | Generate over retrieve | "Was memory/prior work consulted?" | memory_refs populated | Empty prior work section |
| `move_fast` | Move fast | "Was this claim validated via gate?" | Gate passage confirmed | Claims without verification step |
| `optimistic_confidence` | Optimistic confidence | "Is high confidence quantitatively supported?" | Metrics, counts, percentages | "essentially", "mostly" without numbers |
| `pattern_match` | Pattern-match solutions | "Were edge cases considered?" | Edge case table present | Generic solution only |
| `ceremonial_completion` | Ceremonial completion | "Does 'done' match ground truth?" | Verification checklist complete | Unchecked items remain |

### Invocation Pattern

```
Task(subagent_type='anti-pattern-checker', prompt='Verify claim: "{claim}" in context: {file_path}')
```

### Output Format (JSON)

```json
{
  "claim": "Epoch 2 exit criteria are essentially met",
  "context": "Session 143 roadmap review",
  "verified": false,
  "lenses": {
    "assume_over_verify": {
      "pass": false,
      "evidence": "None cited",
      "gap": "No file:line or memory refs for any criterion"
    },
    "generate_over_retrieve": {
      "pass": false,
      "evidence": "Memory not queried",
      "gap": "Prior epoch discussions not retrieved"
    },
    "move_fast": {
      "pass": false,
      "evidence": "No gate invoked",
      "gap": "Claimed without verification step"
    },
    "optimistic_confidence": {
      "pass": false,
      "evidence": "'essentially' used without quantification",
      "gap": "No percentage, count, or metric provided"
    },
    "pattern_match": {
      "pass": true,
      "evidence": "N/A - not a solution claim",
      "gap": null
    },
    "ceremonial_completion": {
      "pass": false,
      "evidence": "5 criteria claimed, 0 verified",
      "gap": "No ground truth verification"
    }
  },
  "verdict": "UNSUPPORTED",
  "gaps": [
    "No evidence cited for any exit criterion",
    "Memory not consulted for prior epoch definitions",
    "No quantitative assessment (% complete, items remaining)",
    "Ground truth verification not performed"
  ]
}
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| 6 lenses from invariants.md | Use existing L1 anti-patterns directly | Already defined, proven in Session 143, no new patterns needed |
| JSON output format | Match preflight-checker pattern | Machine-readable for future gate integration |
| SHOULD for manual, MUST for epochs | Graduated enforcement | Avoid friction on routine claims |
| Read/Grep/Glob tools only | No modification capability | Agent only verifies, never changes |
| Standalone initially | No automatic hook integration | E2-233 will add checkpoint-cycle VERIFY phase |

### Input/Output Examples

**Example 1: Session 143 Incorrect Claim (Real Data)**

**Input:**
```
Verify claim: "Epoch 2 exit criteria are essentially met"
Context: Session 143 roadmap review
```

**Output:**
```json
{
  "claim": "Epoch 2 exit criteria are essentially met",
  "verified": false,
  "verdict": "UNSUPPORTED",
  "gaps": [
    "Used 'essentially' without defining what's incomplete",
    "No evidence for 5 claimed criteria",
    "Epoch 2 exit criteria from roadmap.md not cited"
  ]
}
```

**Example 2: Supported Claim (Expected Pattern)**

**Input:**
```
Verify claim: "M7c-Governance is 100% complete (27/27 items)"
Context: docs/work/archive/*, haios-status.json
```

**Output:**
```json
{
  "claim": "M7c-Governance is 100% complete (27/27 items)",
  "verified": true,
  "verdict": "SUPPORTED",
  "lenses": {
    "assume_over_verify": {"pass": true, "evidence": "haios-status.json:milestone.progress=100"},
    "optimistic_confidence": {"pass": true, "evidence": "27/27 quantified, verified via just tree"}
  },
  "gaps": []
}
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Claim has no context | Request context path from invoker | Manual test during development |
| All lenses pass | Return `verified: true`, `verdict: SUPPORTED` | Test 3 |
| Partial evidence | Return lens-by-lens breakdown with gaps | Part of Test 2 |
| Non-claim input | Return error: "Input is not a claim" | Edge case section in agent |

### Open Questions

**Q: Should the agent block on UNSUPPORTED or just warn?**

Answer: WARN only. Agent reports findings, parent decides action. This preserves flexibility for legitimate edge cases.

**Q: Should we add automatic invocation via hook?**

Answer: Deferred to E2-233. Initial implementation is manual invocation only.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_anti_pattern_checker.py`
- [ ] Add tests from "Tests First" section above
- [ ] Verify all tests fail (red): `pytest tests/test_anti_pattern_checker.py -v`

### Step 2: Create Agent File
- [ ] Create `.claude/agents/anti-pattern-checker.md`
- [ ] Add frontmatter (name, description, tools)
- [ ] Add Requirement Level section (SHOULD manual, MUST for epoch claims)
- [ ] Tests 1-2 pass (file exists, frontmatter correct)

### Step 3: Add 6 Verification Lenses
- [ ] Add table from Detailed Design (6 lenses with questions/evidence/failure indicators)
- [ ] Add Process section (how to apply each lens)
- [ ] Test 2 passes (lenses defined)

### Step 4: Add Output Format and Examples
- [ ] Add Output Format section with JSON structure
- [ ] Add Examples section (Session 143 incorrect claim, supported claim)
- [ ] Add Edge Cases table
- [ ] Test 3 passes (output format documented)

### Step 5: Verify Runtime Discovery
- [ ] Run `just update-status-slim`
- [ ] Verify agent appears in haios-status-slim.json
- [ ] Test 4 passes (runtime discovery works)

### Step 6: Integration Verification
- [ ] All tests pass: `pytest tests/test_anti_pattern_checker.py -v`
- [ ] Run full test suite: `pytest tests/ -v --tb=short`
- [ ] No regressions

### Step 7: README Sync (MUST)
- [ ] **MUST:** Update `.claude/agents/README.md` to list new agent
- [ ] **MUST:** Verify README accurately reflects 7 agents now

### Step 8: Consumer Verification
**SKIPPED:** New file, no consumers to migrate. Future integration (E2-233) will add checkpoint-cycle reference.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent not invoked (forgotten) | Medium | E2-233 will add automatic invocation in checkpoint-cycle |
| Too strict (blocks valid claims) | Low | WARN only, parent decides action |
| Lens definitions too vague | Low | Examples in agent show concrete application |

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
| `.claude/agents/anti-pattern-checker.md` | Has frontmatter (name, description, tools), 6 lenses, output format, examples | [ ] | |
| `tests/test_anti_pattern_checker.py` | Has 4+ tests covering structure, lenses, output, discovery | [ ] | |
| `.claude/agents/README.md` | **MUST:** Lists anti-pattern-checker as 7th agent | [ ] | |
| `.claude/haios-status-slim.json` | Agent appears in infrastructure.agents list | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_anti_pattern_checker.py -v
# Expected: 4+ tests passed
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
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- **Design Spec:** `docs/work/active/INV-050/investigations/001-anti-pattern-checker-agent-design.md`
- **Source Patterns:** `.claude/config/invariants.md:83-95` (6 L1 anti-patterns)
- **Architecture Pattern:** `.claude/agents/validation-agent.md` (output format)
- **Spawned By:** INV-050 (Anti-Pattern Checker Agent Design)
- **Enables:** E2-233 (checkpoint-cycle VERIFY phase integration)
- **Memory:** 80243-80255 (INV-050 design findings)

---
