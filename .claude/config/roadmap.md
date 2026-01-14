# generated: 2025-12-26
# System Auto: last updated on: 2025-12-27T14:22:02
# HAIOS Roadmap: Epochs and Milestones

> Strategic planning context. Epochs define eras, milestones define strategic goals.
> Work item tracking is in `docs/work/` - NOT here.

---

## Current Position

- **Epoch:** Epoch 2 - Governance Suite
- **Active Milestones:** M7b-WorkInfra (17%), M7c-Governance (31%), M7e-Hygiene (0%)
- **Just Completed:** M7d-Plumbing (S126)

---

## Epochs

Epochs are major eras of HAIOS development. Each has a theme and exit criteria.

### Epoch 1: Foundation (Complete)
**Theme:** Core infrastructure and memory system
**Exit Criteria:** Memory ETL pipeline operational, basic CLI

### Epoch 2: Governance Suite (Current)
**Theme:** Hooks, commands, templates, structured workflows
**Exit Criteria (S126 Clarified):**
- **Autonomous Session Loop:** coldstart → pick work → execute → checkpoint → clear → coldstart
- Agent drives, human steers (can pause to discuss, but doesn't need to invoke commands)
- Work item routing: agent picks next logical item after completion
- Cycle completion: agent chains investigation-cycle → implementation-cycle → close without prompting
- Session continuity: checkpoint/memory survives clear, coldstart resumes where left off

**Legacy Criteria (Complete):**
- All governance hooks operational (PreToolUse, PostToolUse, UserPromptSubmit, Stop) ✓
- Skill architecture complete (12+ skills) ✓
- Work item lifecycle enforced (ADR-033) ✓
- Memory integration active ✓

### Epoch 3: FORESIGHT (Future)
**Theme:** Prediction, calibration, self-improvement
**Exit Criteria:**
- SIMULATE: Predict outcomes before action
- INTROSPECT: Assess own capabilities
- ANTICIPATE: Flag likely issues
- UPDATE: Calibrate based on outcomes

---

## Milestones

Milestones are strategic goals within an epoch. They define WHAT to achieve, not individual work items.

### Epoch 2 Milestones

| ID | Name | Goal | Status |
|----|------|------|--------|
| M7a | Recipes | Justfile execution toolkit | Complete |
| M7b | WorkInfra | Work item file architecture (ADR-039) | 17% (2/12) |
| M7c | Governance | Hooks and enforcement mechanisms | 31% (4/13) |
| M7d | Plumbing | Status generation, events, integration | **Complete** (S126) |
| M7e | Hygiene | Documentation sync and cleanup | 0% (0/7) |
| M8 | SkillArch | Skill and agent architecture | Complete |
| M8-Memory | Memory system enhancements | 7% (1/15) |

### Epoch 3 Milestones (Planned)

| ID | Name | Goal | Status |
|----|------|------|--------|
| M9 | FORESIGHT-Core | Prediction and calibration infrastructure | Planned |
| M10 | FORESIGHT-Ops | Operationalize self-improvement | Planned |

### Epoch 4 Milestones (Vision)

| ID | Name | Goal | Status |
|----|------|------|--------|
| M11 | AUTONOMY-Loop | Perpetual agent loop - skill-to-skill routing, human-out-of-loop work | Vision |
| M12 | AUTONOMY-Spawn | Claude Code SDK headless spawning, session queue orchestration | Vision |

**Epoch 4 Notes (captured S126):**
- Stop hook can trigger external processes but not Claude skills directly
- Need orchestrator pattern: hook → queue → scheduler → spawn new session
- Glossed-bug extraction from transcripts (scan for "noticed", "TODO", "should investigate")
- Requires Claude Code SDK for headless execution

---

## Milestone Definitions

### M7d-Plumbing
**Goal:** Wire up status generation, event logging, and system integration.

**Success Criteria:**
- Status refreshes on every prompt
- Events logged to haios-events.jsonl
- Cascade triggers propagate correctly
- Vitals injection complete

**NOT Tracked Here:** Individual work items (E2-xxx). Use `just tree-current` for progress.

---

## How Milestones Work

1. **Definition:** Strategic goal added to this file
2. **Assignment:** Work items get `milestone: M7d-Plumbing` in their frontmatter
3. **Tracking:** `just tree` shows progress (computed from work files)
4. **Completion:** When exit criteria met, milestone marked Complete

**Key Distinction:**
- This file = WHAT to achieve (static strategic goals)
- Work files = HOW to achieve it (dynamic work items)
- haios-status.json = Progress snapshot (computed)

---

*Last Updated: 2025-12-26 (Session 124)*
