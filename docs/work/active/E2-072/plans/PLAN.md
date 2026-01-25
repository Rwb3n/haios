---
template: implementation_plan
status: approved
date: 2026-01-25
backlog_id: E2-072
title: Critique Subagent (Assumption Surfacing)
author: Hephaestus
lifecycle_phase: plan
session: 234
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-25T00:59:49'
---
# Implementation Plan: Critique Subagent (Assumption Surfacing)

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

A HAIOS-configured critique subagent that surfaces implicit assumptions in plans before implementation, integrated as a gate in plan-validation-cycle, with the Assumption Surfacing framework defined as portable YAML configuration.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `haios.yaml`, `plan-validation-cycle/SKILL.md` |
| Lines of code affected | ~20 | Config additions |
| New files to create | 4 | See list below |
| Tests to write | 3 | Framework loading, critique process, integration |
| Dependencies | 2 | plan-validation-cycle, haios.yaml loader |

**New Files:**
1. `.claude/agents/critique-agent.md` - Agent definition
2. `.claude/haios/config/critique_frameworks/assumption_surfacing.yaml` - Default framework
3. `.claude/commands/critique.md` - Manual invocation command
4. `tests/test_critique_agent.py` - Tests

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | plan-validation-cycle, haios.yaml config |
| Risk of regression | Low | New capability, no existing behavior changed |
| External dependencies | Low | Pure file-based, no external APIs |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Phase 1: Framework config | 30 min | High |
| Phase 2: Agent definition | 30 min | High |
| Phase 3: Integration | 45 min | Medium |
| Phase 4: Testing | 30 min | High |
| **Total** | ~2.5 hr | |

---

## Current State vs Desired State

### Current State

**plan-validation-cycle** has phases: CHECK → VALIDATE → APPROVE

No critique/assumption surfacing occurs. Plans proceed to implementation with implicit assumptions unexamined.

**Behavior:** Plans go directly from authoring to implementation without cognitive bias check.

**Result:** Designs contain unexamined assumptions. Main agent has confirmation bias (sunk cost after planning effort).

### Desired State

**plan-validation-cycle** has phases: CHECK → **CRITIQUE** → VALIDATE → APPROVE

```
plan.md ──► [CRITIQUE-AGENT] ──► critique-report.md + assumptions.yaml
                  │                        │
                  │                        ▼
                  │                 [VERDICT GATE]
                  │                 PROCEED / REVISE / BLOCK
                  ▼
           assumptions.yaml (machine-parseable for downstream gates)
```

**Behavior:** Critique agent runs in isolated context, loads framework from config, surfaces assumptions with mitigations.

**Result:** Implicit assumptions surfaced before implementation. Cognitive bias mitigated through isolation.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Framework Loading
```python
def test_framework_loads_from_config():
    """Verify assumption_surfacing.yaml loads correctly."""
    from pathlib import Path
    import yaml

    framework_path = Path(".claude/haios/config/critique_frameworks/assumption_surfacing.yaml")
    assert framework_path.exists(), "Framework file must exist"

    with open(framework_path) as f:
        framework = yaml.safe_load(f)

    assert "categories" in framework
    assert len(framework["categories"]) >= 5  # dependency, data, user_behavior, environment, scope
    assert "verdict_rules" in framework
```

### Test 2: Critique Agent Output Schema
```python
def test_critique_output_schema():
    """Verify critique output matches expected schema."""
    import yaml

    # Mock critique output
    output = {
        "assumptions": [
            {
                "id": "A1",
                "statement": "Memory query returns results",
                "category": "dependency",
                "confidence": "medium",
                "risk_if_wrong": "Context loading fails",
                "mitigation": "Add fallback",
                "related_requirement": "Builder must signal blockage",
                "related_deliverable": "D2"
            }
        ],
        "verdict": "REVISE",
        "blocking_assumptions": ["A1"]
    }

    # Validate required fields
    for assumption in output["assumptions"]:
        assert "id" in assumption
        assert "category" in assumption
        assert assumption["category"] in ["dependency", "data", "user_behavior", "environment", "scope"]
        assert "confidence" in assumption
        assert "mitigation" in assumption
```

### Test 3: Agent Definition Valid
```python
def test_critique_agent_definition():
    """Verify agent definition has required frontmatter."""
    from pathlib import Path
    import yaml

    agent_path = Path(".claude/agents/critique-agent.md")
    assert agent_path.exists(), "Agent file must exist"

    content = agent_path.read_text()
    # Extract frontmatter
    parts = content.split("---")
    frontmatter = yaml.safe_load(parts[1])

    assert frontmatter["name"] == "critique-agent"
    assert "tools" in frontmatter
    assert "Read" in frontmatter["tools"]
```

---

## Detailed Design

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    HAIOS-CONFIGURED CRITIQUE AGENT                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  haios.yaml                                                          │
│  └── agents.critique                                                 │
│       ├── framework: assumption_surfacing                            │
│       ├── frameworks_dir: .claude/haios/config/critique_frameworks/  │
│       └── integration.gate: plan-validation-cycle.CRITIQUE           │
│                                                                      │
│  assumption_surfacing.yaml                                           │
│  └── categories: [dependency, data, user_behavior, environment, scope]│
│  └── verdict_rules: {BLOCK, REVISE, PROCEED}                         │
│                                                                      │
│  critique-agent.md                                                   │
│  └── Loads config → Loads framework → Processes plan → Outputs      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Component 1: haios.yaml Extension

**File:** `.claude/haios/config/haios.yaml`
**Location:** Add after `context:` section

```yaml
# Agent configurations (E2-072: Phase-as-Subagent pattern)
agents:
  critique:
    description: "Pre-implementation assumption surfacing"
    framework: assumption_surfacing  # Default framework
    frameworks_dir: ".claude/haios/config/critique_frameworks/"
    integration:
      gate: plan-validation-cycle.CRITIQUE
      trigger: pre-DO
    context_loading:
      - manifesto/L4/agent_user_requirements.md
      - work_item
      - plan
```

### Component 2: Framework Configuration

**File:** `.claude/haios/config/critique_frameworks/assumption_surfacing.yaml`

```yaml
name: assumption_surfacing
version: "1.0"
description: "Surface implicit assumptions in designs before implementation"

categories:
  - id: dependency
    label: "External Dependencies"
    prompt: "What external systems, APIs, or components does this assume will work?"

  - id: data
    label: "Data Assumptions"
    prompt: "What data availability, format, or quality is assumed?"

  - id: user_behavior
    label: "User/Agent Behavior"
    prompt: "What behaviors are assumed from users or other agents?"

  - id: environment
    label: "Environment"
    prompt: "What runtime environment characteristics are assumed?"

  - id: scope
    label: "Scope Boundaries"
    prompt: "What is assumed to be out of scope that might actually matter?"

output_schema:
  assumptions:
    - id: string
      statement: string
      category: enum[dependency, data, user_behavior, environment, scope]
      confidence: enum[high, medium, low]
      risk_if_wrong: string
      mitigation: string
      related_requirement: string  # L4 traceability
      related_deliverable: string  # Work item traceability

verdict_rules:
  BLOCK: "Any assumption with confidence=low and no mitigation"
  REVISE: "Any assumption with risk_if_wrong containing 'silent' or 'fail'"
  PROCEED: "All assumptions have mitigations or are high confidence"
```

### Component 3: Agent Definition

**File:** `.claude/agents/critique-agent.md`

```markdown
---
name: critique-agent
description: Pre-implementation assumption surfacing. Framework loaded from haios.yaml config.
tools: Read, Glob
color: yellow
---
# Critique Agent

Surfaces implicit assumptions in plans before implementation begins.

## Context Loading

1. Read `.claude/haios/config/haios.yaml` to get `agents.critique.framework`
2. Load framework from `agents.critique.frameworks_dir/{framework}.yaml`
3. Read work item WORK.md for deliverables (requirements baseline)
4. Read plan artifact to critique

## Process

For each category in framework:
1. Apply category prompt to plan content
2. Identify assumptions matching category
3. Assess confidence level (high/medium/low)
4. Assess risk if wrong
5. Propose mitigation strategy
6. Link to related L4 requirement if applicable
7. Link to work item deliverable if applicable

## Output

Write to work item directory:
- `critique/critique-report.md` - Human-readable findings
- `critique/assumptions.yaml` - Machine-parseable for gates

Return verdict per framework's verdict_rules:
- **BLOCK**: Cannot proceed, unmitigated low-confidence assumptions
- **REVISE**: Should revise plan to address risks
- **PROCEED**: Safe to continue to implementation

## Invocation

```
Task(subagent_type='critique-agent', prompt='Critique plan: {plan_path}')
```
```

### Component 4: Command for Manual Use

**File:** `.claude/commands/critique.md`

```markdown
# Critique Command

Manually invoke critique agent on any artifact.

## Usage

```
/critique <artifact_path>
```

## Examples

```
/critique docs/work/active/E2-072/plans/PLAN.md
/critique docs/adr/ADR-045-new-architecture.md
```

## Process

1. Parse artifact path from arguments
2. Invoke critique-agent subagent
3. Report verdict and findings location
```

### Integration: plan-validation-cycle Update

**File:** `.claude/skills/plan-validation-cycle/SKILL.md`

Add CRITIQUE phase between CHECK and VALIDATE:

```markdown
### 2. CRITIQUE Phase (NEW - E2-072)

**On Entry:**
```bash
just set-cycle plan-validation-cycle CRITIQUE {work_id}
```

**Goal:** Surface implicit assumptions before implementation.

**Actions:**
1. Invoke critique-agent subagent:
   ```
   Task(subagent_type='critique-agent', prompt='Critique plan: {plan_path}')
   ```
2. Read critique verdict from `assumptions.yaml`
3. If BLOCK: Report blocking assumptions, STOP
4. If REVISE: Report recommendations, ask operator to proceed or revise
5. If PROCEED: Continue to VALIDATE phase

**Exit Criteria:**
- [ ] Critique agent invoked
- [ ] Verdict is PROCEED or operator approves REVISE
```

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Framework as YAML config | Config-driven, not code | Portability - drop .claude/haios/ into any project |
| Categories in framework | 5 categories | Balance coverage vs cognitive load |
| Output to work item dir | `{work}/critique/` | Context stays with work item (L4: files as context) |
| Verdict as enum | BLOCK/REVISE/PROCEED | Clear gate semantics, machine-parseable |
| L4 traceability field | `related_requirement` | Links assumptions to L4 agent_user_requirements |
| Integration as phase | plan-validation-cycle.CRITIQUE | Automatic, not skippable (governance) |
| Manual command also | `/critique` | Flexibility for ADRs, designs, any artifact |

### Data Flow (Unix Philosophy)

```
plan.md (input file)
    │
    ▼
[critique-agent]
    │
    ├──► critique-report.md (human output)
    ├──► assumptions.yaml (machine output)
    └──► verdict (signal to gate)
           │
           ▼
    [plan-validation-cycle gate]
           │
           ├─ BLOCK ──► STOP
           ├─ REVISE ──► operator decision
           └─ PROCEED ──► continue
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Framework file missing | Fall back to inline default, warn | Test 1 |
| Plan file empty | Return BLOCK with "no content to critique" | Edge test |
| All assumptions high confidence | Return PROCEED | Test 2 |
| Operator overrides REVISE | Log decision, proceed | Integration |

### Open Questions

**Q: Should assumptions persist across sessions?**

Store to memory via `ingester_ingest` with `source_path: critique:{work_id}`. This enables learning from assumption patterns across work items.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Store assumptions to memory? | Yes, No | Yes | Enables learning from assumption patterns across work items |
| Create critique_frameworks directory? | Yes (new dir), No (inline in haios.yaml) | Yes | Extensibility - can add pre_mortem.yaml, red_team.yaml later |
| Critique output location | work/{id}/critique/, ephemeral | work/{id}/critique/ | Persists with work item, traceable |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_critique_agent.py`
- [ ] Add Test 1: Framework loading
- [ ] Add Test 2: Output schema validation
- [ ] Add Test 3: Agent definition validation
- [ ] Verify all tests fail (red)

### Step 2: Create Framework Configuration
- [ ] Create directory `.claude/haios/config/critique_frameworks/`
- [ ] Create `assumption_surfacing.yaml` with 5 categories
- [ ] Test 1 passes (green)

### Step 3: Create Agent Definition
- [ ] Create `.claude/agents/critique-agent.md`
- [ ] Add frontmatter (name, description, tools)
- [ ] Add context loading instructions
- [ ] Add process steps
- [ ] Add output format
- [ ] Test 3 passes (green)

### Step 4: Extend haios.yaml
- [ ] Add `agents.critique` section to haios.yaml
- [ ] Define framework, frameworks_dir, integration

### Step 5: Create Command
- [ ] Create `.claude/commands/critique.md`
- [ ] Define usage and examples

### Step 6: Update plan-validation-cycle
- [ ] Add CRITIQUE phase to `.claude/skills/plan-validation-cycle/SKILL.md`
- [ ] Add subagent invocation pattern
- [ ] Add verdict handling logic

### Step 7: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite (no regressions)
- [ ] Test manual `/critique` command on existing plan

### Step 8: README Sync (MUST)
- [ ] **MUST:** Update `.claude/agents/README.md` with critique-agent
- [ ] **MUST:** Create `.claude/haios/config/critique_frameworks/README.md`
- [ ] **MUST:** Update `.claude/commands/README.md` with /critique

### Step 9: Test on Existing Designs
- [ ] Run critique on E2-072 plan (self-critique)
- [ ] Run critique on one ADR
- [ ] Run critique on one investigation design
- [ ] Document findings

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Framework file missing at runtime | Medium | Agent has inline fallback default |
| Critique adds latency to plan-validation | Low | Critique is fast (file read + structured analysis) |
| Over-critique causes plan paralysis | Medium | REVISE allows operator override |
| Agent outputs malformed YAML | Medium | Test 2 validates schema |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 234 | 2026-01-25 | - | Plan authored | Design discussion, L4 alignment, HAIOS config pattern |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/E2-072/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Create `.claude/agents/critic.md` subagent definition | [ ] | File exists with valid frontmatter |
| Define critique framework (Assumption Surfacing as default) | [ ] | `assumption_surfacing.yaml` has 5 categories |
| Create `/critique <artifact>` command or skill invocation | [ ] | `.claude/commands/critique.md` exists |
| Test on 3 existing designs, validate improvement | [ ] | Critique reports generated |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/agents/critique-agent.md` | Agent with frontmatter, tools: Read, Glob | [ ] | |
| `.claude/haios/config/critique_frameworks/assumption_surfacing.yaml` | 5 categories, verdict_rules | [ ] | |
| `.claude/commands/critique.md` | Usage, examples | [ ] | |
| `.claude/haios/config/haios.yaml` | agents.critique section | [ ] | |
| `.claude/skills/plan-validation-cycle/SKILL.md` | CRITIQUE phase added | [ ] | |
| `tests/test_critique_agent.py` | 3 tests, all pass | [ ] | |
| `.claude/agents/README.md` | Updated with critique-agent | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_critique_agent.py -v
# Expected: 3 tests passed
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

- Memory 71460: "Used Assumption Surfacing framework, identified 6 assumptions" - origin of E2-072
- Memory 80988: "Files ARE the context window for the next agent" - Unix philosophy
- Memory 81591: "Each agent loads what IT needs" - L4 principle
- @.claude/haios/manifesto/L4/agent_user_requirements.md - Validator Agent requirements
- @.claude/haios/manifesto/L4/technical_requirements.md - What's built vs needed
- @.claude/haios/epochs/E2_3/EPOCH.md - Pipeline mission
- @.claude/agents/anti-pattern-checker.md - Related agent (post-hoc vs pre-implementation)
- @.claude/agents/validation-agent.md - Related agent (CHECK phase vs CRITIQUE phase)

---
