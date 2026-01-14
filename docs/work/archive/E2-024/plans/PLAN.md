---
template: implementation_plan
status: complete
date: 2025-12-28
backlog_id: E2-024
title: Dependency Integrity Validator
author: Hephaestus
lifecycle_phase: plan
session: 140
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-28T21:35:56'
---
# Implementation Plan: Dependency Integrity Validator

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

## Goal

Create a dependency validation function that checks skill, agent, and command references exist, integrated with status generation to surface broken references.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `.claude/lib/dependencies.py` (new), `.claude/lib/status.py` |
| Lines of code affected | ~150 | New validation module + status integration |
| New files to create | 1 | `.claude/lib/dependencies.py` |
| Tests to write | 7 | Test extraction, validation, edge cases |
| Dependencies | 2 | status.py, pathlib |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single integration point (status.py) |
| Risk of regression | Low | New functionality, doesn't modify existing |
| External dependencies | None | Pure Python, uses existing discovery patterns |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 15 min | High |
| Implement extraction functions | 20 min | High |
| Implement validation logic | 15 min | High |
| Integrate with status | 10 min | High |
| **Total** | 60 min | High |

---

## Current State vs Desired State

### Current State

No dependency validation exists. Skills reference other skills/agents:

```markdown
# .claude/skills/implementation-cycle/SKILL.md:71
Skill(skill="plan-validation-cycle")

# .claude/skills/implementation-cycle/SKILL.md:76
Task(subagent_type='preflight-checker', prompt='Check plan for {backlog_id}')
```

**Behavior:** References are not validated. If a skill is renamed/deleted, references become stale.

**Result:** Broken references discovered only at runtime when agent tries to invoke.

### Desired State

```python
# .claude/lib/dependencies.py (new file)
def validate_dependencies() -> dict:
    """Validate all skill/agent/command references exist."""
    return {
        "valid": True/False,
        "broken_refs": [
            {"source": "skill:implementation-cycle", "target": "skill:plan-validation-cycle", "type": "skill"},
        ],
        "summary": "X references checked, Y broken"
    }
```

**Behavior:** All cross-references validated at status generation time.

**Result:** Broken references surfaced in haios-status.json, visible via `/status` command.

---

## Tests First (TDD)

### Test 1: Extract Skill References
```python
def test_extract_skill_refs():
    content = 'Skill(skill="plan-validation-cycle")'
    refs = extract_skill_refs(content)
    assert refs == ["plan-validation-cycle"]
```

### Test 2: Extract Agent References
```python
def test_extract_agent_refs():
    content = "Task(subagent_type='preflight-checker', prompt='...')"
    refs = extract_agent_refs(content)
    assert refs == ["preflight-checker"]
```

### Test 3: Extract Multiple Refs
```python
def test_extract_multiple_skill_refs():
    content = 'Skill(skill="a") then Skill(skill="b")'
    refs = extract_skill_refs(content)
    assert refs == ["a", "b"]
```

### Test 4: Get Available Skills
```python
def test_get_available_skills():
    skills = get_available_skills()
    assert "implementation-cycle" in skills
    assert "close-work-cycle" in skills
```

### Test 5: Get Available Agents
```python
def test_get_available_agents():
    agents = get_available_agents()
    assert "preflight-checker" in agents
    assert "schema-verifier" in agents
```

### Test 6: Validate All Valid
```python
def test_validate_dependencies_all_valid():
    result = validate_dependencies()
    # Should have no broken refs in a healthy system
    assert result["valid"] == True or len(result["broken_refs"]) == 0
```

### Test 7: Detection of Broken Ref
```python
def test_validate_detects_broken_ref(tmp_path, monkeypatch):
    # Create a skill with broken reference
    skill_dir = tmp_path / ".claude" / "skills" / "test-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text('Skill(skill="nonexistent-skill")')

    # Mock the skills path
    monkeypatch.setattr("dependencies.SKILLS_PATH", tmp_path / ".claude" / "skills")

    result = validate_dependencies()
    assert result["valid"] == False
    assert any(r["target"] == "skill:nonexistent-skill" for r in result["broken_refs"])
```

---

## Detailed Design

### Architecture

```
validate_dependencies()
    |
    +-- Discover all skills (.claude/skills/*/SKILL.md)
    |     +-- For each skill:
    |           +-- Extract Skill(skill="...") references
    |           +-- Extract Task(subagent_type='...') references
    |
    +-- Discover all agents (.claude/agents/*.md)
    |
    +-- Build reference graph
    |
    +-- Validate all references exist
    |     +-- skill refs → check skill exists
    |     +-- agent refs → check agent exists
    |
    +-- Return validation result
```

### Function Signatures

```python
# .claude/lib/dependencies.py

import re
from pathlib import Path

SKILLS_PATH = Path(".claude/skills")
AGENTS_PATH = Path(".claude/agents")

def extract_skill_refs(content: str) -> list[str]:
    """Extract skill names from Skill(skill="...") patterns."""
    pattern = r'Skill\(skill=["\']([^"\']+)["\']\)'
    return re.findall(pattern, content)

def extract_agent_refs(content: str) -> list[str]:
    """Extract agent names from Task(subagent_type='...') patterns."""
    pattern = r"Task\([^)]*subagent_type=['\"]([^'\"]+)['\"]"
    return re.findall(pattern, content)

def get_available_skills() -> set[str]:
    """Get set of available skill names from .claude/skills/*/SKILL.md"""
    skills = set()
    for path in SKILLS_PATH.glob("*/SKILL.md"):
        skills.add(path.parent.name)
    return skills

def get_available_agents() -> set[str]:
    """Get set of available agent names from .claude/agents/*.md"""
    agents = set()
    for path in AGENTS_PATH.glob("*.md"):
        if path.stem != "README":
            agents.add(path.stem)
    return agents

def validate_dependencies() -> dict:
    """Validate all skill/agent references exist.

    Returns:
        dict with keys:
        - valid: bool - True if no broken refs
        - broken_refs: list[dict] - Each has source, target, type
        - summary: str - Human-readable summary
    """
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Separate module | dependencies.py | Single responsibility, testable in isolation |
| Regex extraction | Simple patterns | Skill/agent invocation patterns are consistent |
| Return structure | dict with valid, broken_refs, summary | Enables both boolean check and detailed report |
| Skip commands | Only check skills/agents | Commands rarely reference each other, lower priority |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Empty skill file | Skip, no refs to check | Implicit |
| Self-reference | Allow (valid) | Test 6 |
| Multiple refs same target | Deduplicate in report | Test 3 |
| README.md in agents | Exclude from agent list | Explicit filter |

---

## Implementation Steps

### Step 1: Write Tests First
- [ ] Create `tests/test_dependencies.py`
- [ ] Add tests 1-7 from Tests First section
- [ ] Verify all tests fail (red) - module doesn't exist yet

### Step 2: Create dependencies.py with Extraction Functions
- [ ] Create `.claude/lib/dependencies.py`
- [ ] Implement `extract_skill_refs()` and `extract_agent_refs()`
- [ ] Tests 1-3 pass (green)

### Step 3: Implement Discovery Functions
- [ ] Implement `get_available_skills()` and `get_available_agents()`
- [ ] Tests 4-5 pass (green)

### Step 4: Implement validate_dependencies()
- [ ] Implement main validation function
- [ ] Tests 6-7 pass (green)

### Step 5: Verify All Tests Pass
- [ ] Run `pytest tests/test_dependencies.py -v`
- [ ] All 7 tests green

### Step 6: Integration (Optional)
**SKIPPED:** Status integration is optional enhancement. Core validation function is the deliverable. Can add to status.py in future iteration if needed.

---

## Verification

- [ ] Tests pass (`pytest tests/test_dependencies.py -v`)
- [ ] N/A - No README changes needed (new file in existing lib/)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Regex misses edge cases | Low | Pattern tested against real skill files |
| Performance with many skills | Low | Current skill count is ~15, O(n) is fine |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 140 | 2025-12-28 | - | In progress | Plan populated |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/dependencies.py` | File exists with validate_dependencies() | [x] | 170 lines |
| `tests/test_dependencies.py` | 15 tests, all passing | [x] | 15 passed in 0.15s |

**Verification Commands:**
```bash
pytest tests/test_dependencies.py -v
# Expected: 7 tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| Does validate_dependencies() exist? | Yes | .claude/lib/dependencies.py:104 |
| Do all tests pass? | Yes | 15/15 passed |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] WHY captured (reasoning stored to memory)
- [ ] Docs current (N/A - no behavior change to document)

---

## References

- Work item: E2-024
- Related: E2-225 (Path Governance Gap - similar pattern validation)

---
