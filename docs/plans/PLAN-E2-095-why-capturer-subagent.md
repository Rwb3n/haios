---
template: implementation_plan
status: complete
date: 2025-12-17
backlog_id: E2-095
title: "WHY Capturer Subagent"
author: Hephaestus
lifecycle_phase: done
session: 87
spawned_by: Session-83
# blocked_by: []  # Independent - can start without E2-091
related: [E2-091, E2-106, ADR-033, ADR-038, epoch3/foresight-spec.md]
milestone: M3-Cycles
version: "1.3"
---
# generated: 2025-12-17
# System Auto: last updated on: 2025-12-19 23:18:57
# Implementation Plan: WHY Capturer Subagent

@docs/README.md
@docs/epistemic_state.md
@.claude/agents/schema-verifier.md

---

## Goal

A `why-capturer` subagent exists that extracts learnings from completed work and stores them to memory via `ingester_ingest`, automating the DONE phase's "capture WHY" requirement.

---

## Current State vs Desired State

### Current State

```markdown
# Parent agent manually captures WHY:
ingester_ingest(
    content="[manually written summary]",
    source_path="session:...",
    content_type_hint="techne"
)
# Requires manual effort
# Easy to forget or skip
# Inconsistent quality
```

**Behavior:** WHY capture is manual and inconsistent.

**Result:** Some sessions have rich learnings, others have none.

### Desired State

```markdown
# .claude/agents/why-capturer.md
---
name: why-capturer
description: Extract and store learnings from completed work. Use during DONE phase to capture WHY per ADR-033.
tools: Read, mcp__haios-memory__ingester_ingest
---
# WHY Capturer
Analyzes completed work, extracts:
- Key decisions made
- Problems encountered and solutions
- Patterns discovered
- Reusable strategies
Stores to memory with proper classification.
```

**Behavior:** Automated extraction and storage of learnings.

**Result:** Consistent WHY capture, rich experiential memory.

---

## Tests First (TDD)

### Test 1: Agent File Exists
```bash
test -f ".claude/agents/why-capturer.md"
# Expected: exit 0
```

### Test 2: Agent Appears in Discovery
```bash
# After creating, check haios-status-slim.json
# infrastructure.agents should include "why-capturer"
```

### Test 3: Agent Has Required Frontmatter
```yaml
# Verify frontmatter has:
name: why-capturer
description: ...
tools: Read, mcp__haios-memory__ingester_ingest
```

---

## Detailed Design

### Agent File Structure

```markdown
---
name: why-capturer
description: Extract and store learnings from completed work. Use during DONE phase to capture WHY per ADR-033.
tools: Read, mcp__haios-memory__ingester_ingest
---
# WHY Capturer

Extracts learnings from completed work and stores to memory.

## Requirement Level

**RECOMMENDED** during DONE phase. ADR-033 requires WHY capture for work item closure.

## Input

Receives from parent agent:
- `backlog_id`: The work item being closed
- `plan_path`: Path to the plan file
- `checkpoint_path`: (Optional) Path to session checkpoint
- `context_summary`: (Optional) Brief description of what was done

## Extraction Process

1. Read the plan file for:
   - Goal (what was achieved)
   - Key Design Decisions (WHY choices were made)
   - Deviations from plan (lessons learned)

2. Analyze for learnable patterns:
   - Problems encountered → solutions
   - Techniques that worked well
   - Anti-patterns discovered
   - Reusable strategies

3. FORESIGHT Calibration (E2-106 - if foresight_prep exists):
   If plan has `foresight_prep` section:
   - Extract prediction vs actual comparison
   - Calculate prediction_error
   - Note failure_modes_discovered
   - Store calibration data for Epoch 3 Self Model

4. Classify each learning:
   - `techne`: Practical how-to knowledge
   - `episteme`: Factual discoveries
   - `doxa`: Opinions/interpretations

4. Store via `ingester_ingest`:
   - source_path: `closure:{backlog_id}`
   - content_type_hint: appropriate classification

## Output Format

Return summary of what was captured:
```
WHY Captured for {backlog_id}

Learnings stored:
- [concept_id]: [brief description] (techne)
- [concept_id]: [brief description] (episteme)

Total: N concepts stored
Source: closure:{backlog_id}

# If foresight_prep was present:
FORESIGHT Calibration:
- Predicted: {predicted_outcome}
- Actual: {actual_outcome}
- Prediction Error: {prediction_error}
- Domain: {competence_domain}
- Failure Modes: {failure_modes_discovered}
```

## Example

Input: "Capture WHY for E2-091"
Action: Read plan, extract decisions
Output:
```
WHY Captured for E2-091

Learnings stored:
- 72314: Implementation cycle uses composition pattern (techne)
- 72315: L2 guidance in skill, L3 enforcement in preflight (episteme)
- 72316: DO phase guardrails prevent runaway changes (techne)

Total: 3 concepts stored
Source: closure:E2-091

FORESIGHT Calibration:
- Predicted: "Skill file with phase documentation and tooling map"
- Actual: "Skill complete, added DO phase guardrails beyond original plan"
- Prediction Error: 0.15
- Domain: skill_development
- Failure Modes: ["Underestimated need for L2/L3 separation"]
```

## Extraction Prompts

Use these prompts to extract learnings:

### From Key Design Decisions:
"For each decision, extract: what was decided, why, and what alternatives were considered"

### From Deviations:
"What changed from the original plan? Why? What would you do differently?"

### From Problems:
"What unexpected issues arose? How were they solved? Is this reusable?"
```

### Behavior Logic

```
Input (backlog_id, plan_path, context?)
    │
    ▼
Read plan file
    │
    ▼
Extract from sections:
    ├─► Key Design Decisions → WHY choices
    ├─► Deviations → lessons learned
    └─► Ground Truth Verification → actual outcomes
    │
    ▼
For each learning:
    ├─► Classify (techne/episteme/doxa)
    └─► Call ingester_ingest()
    │
    ▼
Return summary with concept IDs
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Tools | Read + ingester_ingest | Read plan, store learnings |
| Classification | Agent determines | Context-aware classification |
| Source format | `closure:{backlog_id}` | Clear provenance |
| Output | Summary with IDs | Parent can verify storage |

### Input/Output Examples

| Input | Output | Notes |
|-------|--------|-------|
| E2-091 plan | 3-5 concepts stored | Design decisions |
| Investigation | 2-3 concepts | Findings, recommendations |
| Bug fix | 1-2 concepts | Root cause, solution |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Plan has no decisions section | Extract from other sections | Manual |
| Empty plan | Return "No learnings found" | Manual |
| Ingestion fails | Report error, continue | N/A |

---

## Implementation Steps

### Step 1: Create Agent File
- [ ] Create `.claude/agents/why-capturer.md`
- [ ] Add YAML frontmatter (name, description, tools)
- [ ] Add body content with extraction process

### Step 2: Verify Discovery
- [ ] PostToolUse hook should auto-refresh status
- [ ] Check haios-status-slim.json includes why-capturer
- [ ] Verify agent appears in vitals

### Step 3: Integration Test
- [ ] Invoke via `Task(prompt="Capture WHY for E2-091", subagent_type="why-capturer")`
- [ ] Verify concepts are stored
- [ ] Check memory for stored content

---

## Verification

- [ ] Agent file exists
- [ ] Agent discoverable in vitals
- [ ] Successfully extracts and stores learnings

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Low-quality extraction | Medium | Provide extraction prompts |
| Over-extraction | Low | Limit to key learnings |
| Ingestion failures | Low | Report and continue |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 85 | 2025-12-18 | - | Plan filled | Design complete |
| 87 | 2025-12-19 | - | Complete | Agent created, discovered, FORESIGHT-ready |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/agents/why-capturer.md` | File exists with frontmatter | [x] | Session 87 |
| `haios-status-slim.json` | why-capturer in agents | [x] | Auto-refresh worked |
| Vitals output | Shows why-capturer | [x] | Discovered via PostToolUse |

**Verification Commands:**
```bash
# Check agent exists
test -f ".claude/agents/why-capturer.md" && echo "EXISTS"
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | File created, frontmatter verified |
| Agent appears in vitals? | Yes | haios-status-slim.json shows why-capturer |
| Any deviations from plan? | No | Followed design exactly |

**Same Limitation as E2-094:** Claude Code's `Task(subagent_type=...)` registry doesn't hot-reload mid-session. Agent is discovered but won't be invocable until next session start.

---

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (agent exists, discoverable)
- [x] WHY captured (reasoning stored to memory)
- [x] Documentation current
- [x] Ground Truth Verification completed above

---

## References

- E2-091: Implementation Cycle Skill
- ADR-033: Work Item Lifecycle (DoD)
- schema-verifier: Reference subagent pattern
- ADR-038: M2-Governance Symphony Architecture

### Symphony Integration (ADR-038)

| Movement | Integration |
|----------|-------------|
| **RHYTHM** | Agent discovered in vitals (auto-refresh via PostToolUse) |
| **LISTENING** | PRIMARY: Stores learnings via ingester_ingest |
| **RESONANCE** | Knowledge capture events could be logged |

---
