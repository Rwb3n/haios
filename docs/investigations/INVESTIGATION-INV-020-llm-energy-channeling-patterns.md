---
template: investigation
status: complete
date: 2025-12-21
backlog_id: INV-020
title: "Investigation: LLM Energy Channeling Patterns"
author: Hephaestus
session: 95
lifecycle_phase: conclude
spawned_by: Session 95 meta-observation
related: [M3-Cycles, E2-130, INV-012, INV-023]
memory_refs: [77199, 77200, 77201, 77202, 77203, 77204, 77205, 77206, 77207, 77208, 77209]
version: "1.1"
generated: 2025-12-21
last_updated: 2025-12-22T21:21:33
---
# Investigation: LLM Energy Channeling Patterns

@docs/epistemic_state.md
@.claude/hooks/README.md
@.claude/REFS/GOVERNANCE.md

---

## Context

During E2-130 implementation (Session 95), the operator observed that certain architectural patterns effectively "channel" LLM behavior through environmental constraints rather than just prompting. Examples:

| Pattern | Example | Effect |
|---------|---------|--------|
| **Blocker → Agent** | SQL blocked → schema-verifier subagent | Forces correct path |
| **Tool → Tracker** | Complex task → TodoWrite visible progress | Keeps agent on track |
| **Governance → Command** | Raw write blocked → /new-* command | Enforces templates |

This is a meta-question: How well is the M3-Cycles infrastructure (hooks, commands, skills, agents) actually channeling behavior? What patterns work best? What's not working?

---

## Objective

1. **Audit current channeling mechanisms** - What's wired, what's enforced, what's visual-only?
2. **Identify effective patterns** - Which approaches reliably guide LLM behavior?
3. **Find gaps** - Where does behavior slip through intended channels?
4. **Design improvements** - How to harness tools (TodoWrite, subagents, hooks) more effectively?

---

## Scope

### In Scope
- Hooks: PreToolUse blockers, PostToolUse automation, UserPromptSubmit injection
- Commands/Skills: Usage patterns, adoption rate
- Subagents: When they're invoked, effectiveness
- Tool usage: TodoWrite, memory tools, Task agents
- Governance enforcement: What's explicit vs implicit

### Out of Scope
- Claude Code CLI internals (can't modify)
- Prompt engineering details (separate concern)

---

## Hypotheses

1. **H1:** Blockers (PreToolUse) are more effective than suggestions (UserPromptSubmit reminders)
2. **H2:** Subagents with isolated context prevent scope creep better than inline work
3. **H3:** TodoWrite provides visible checkpointing that improves task completion
4. **H4:** Some M3 infrastructure is wired but not actively channeling behavior (ceremony without effect)
5. **H5:** Visual feedback (status injection) affects behavior less than hard blockers

---

## Investigation Steps

1. [x] Audit all PreToolUse blockers - what paths are protected?
2. [x] Audit all UserPromptSubmit injections - what context is added?
3. [x] Review subagent usage patterns across recent sessions
4. [x] Analyze TodoWrite usage correlation with task completion
5. [x] Identify "dead" infrastructure - wired but not enforced
6. [x] Document effective vs ineffective patterns
7. [x] Propose improvements

---

## Findings

### F1: Enforcement Spectrum Analysis

| Level | Type | What's Wired | Effectiveness | Evidence |
|-------|------|--------------|---------------|----------|
| **L4: Automated** | PostToolUse | Auto-timestamps, cascade triggers, event logging | **HIGH** | Works silently, no agent awareness needed |
| **L3: Gated** | PreToolUse blockers | SQL, governed paths, plan backlog_id | **HIGH** | Agent MUST use alternative path |
| **L2: Prompted** | UserPromptSubmit | Vitals, thresholds, RFC2119 reminders | **LOW** | Present but easily ignored |
| **L1: Observable** | Events | haios-events.jsonl (20+ events logged) | **ZERO** | Logged but NEVER read back |
| **L0: None** | Cultural | Cycle phases, memory queries | **ZERO** | Pure documentation |

### F2: What's Actually Blocking (L3)

| Blocker | Trigger | Alternative Path | Status |
|---------|---------|------------------|--------|
| SQL blocking | `SELECT...FROM`, `INSERT INTO` | schema-verifier subagent | ACTIVE |
| Path governance | Write to `docs/plans/`, `docs/checkpoints/`, etc. | `/new-*` commands | ACTIVE |
| Plan validation | Missing `backlog_id:` in plan | Add backlog_id field | ACTIVE |

**All other enforcement is L2 or lower (suggestions only).**

### F3: Dead Infrastructure (Wired But Not Enforced)

| Component | What It Says | Reality |
|-----------|--------------|---------|
| **Events (RESONANCE)** | Logs cycle transitions, cascade triggers, sessions | **Never read back** - no feedback loop |
| **Lifecycle guidance** | "MUST use /new-investigation" | **Only suggests** - user can override with "skip discovery" |
| **RFC2119 reminders** | "MUST use /close" for closures | **Only suggests** - no actual blocking |
| **Memory query in commands** | `/new-plan` says query memory first | **Only documented** - not verified |
| **Cycle skills** | "SHOULD invoke implementation-cycle" | **Pure guidance** - agent can ignore entirely |

### F4: Effective vs Ineffective Patterns

**EFFECTIVE (forces correct path):**
```
Agent attempts SQL → PreToolUse BLOCKS → Only option: schema-verifier
Agent attempts raw Write → PreToolUse BLOCKS → Only option: /new-* command
```

**INEFFECTIVE (suggests but no consequence):**
```
Agent sees vitals → "M4-Research at 86%" → Agent proceeds without action
Agent sees RFC2119 reminder → "MUST use /close" → Agent ignores, closes manually
Agent sees lifecycle guidance → "Consider /new-investigation" → Agent skips
Events log cycle transition → No reader → Information lost
```

### F5: The "Last Mile" Problem

From memory (concept 77136): *"INV-020 and INV-023 both address the 'last mile' problem - retrieved strategies are suggestions that are easily ignored."*

The pattern applies across the system:
- Strategies from memory → **suggestions** → ignored
- Vitals in prompt → **suggestions** → skimmed
- RFC2119 reminders → **suggestions** → dismissed
- Skill guidance → **suggestions** → bypassed

**Only L3/L4 enforcement actually changes behavior.**

### F6: Hypothesis Verdicts

| Hypothesis | Evidence | Verdict |
|------------|----------|---------|
| **H1:** Blockers > suggestions | SQL blocking works perfectly, RFC2119 reminders ignored | **CONFIRMED** |
| **H2:** Isolated subagents prevent scope creep | investigation-agent isolated 30k tokens (Session 99) | **CONFIRMED** |
| **H3:** TodoWrite visibility helps completion | Rarely used proactively, no enforcement | **INCONCLUSIVE** |
| **H4:** Some M3 infrastructure is ceremony | Events log but don't feed back, skills guide but don't enforce | **CONFIRMED** |
| **H5:** Visual feedback < hard blockers | Vitals shown every prompt, behavior unchanged | **CONFIRMED** |

---

## Recommendations

### The Core Insight

**"Doing right should be easy" means "doing wrong should be hard."**

Current architecture makes wrong easy (just ignore suggestions). Fix: Promote key L2 suggestions to L3 blockers.

### Proposed Enforcement Upgrades

| Current (L2) | Proposed (L3) | Implementation |
|--------------|---------------|----------------|
| RFC2119 reminder for /close | Block manual closure | PreToolUse: detect "closed", "complete" in Edit to backlog.md |
| Lifecycle guidance for discovery | Block /new-plan without investigation | PreToolUse: check for INVESTIGATION-{id}.md before allowing plan |
| Memory query suggested | Block plan creation without memory query proof | Require `memory_queried: true` frontmatter |
| Cycle phase transitions | Log-and-warn, then block | Phase 1: warn on skip; Phase 2: block after adoption |

### Proposed Feedback Loop (RESONANCE → DYNAMICS)

Currently events log but aren't read. Close the loop:

```
Events → Pattern Detection → Dynamic Thresholds
  |                                    |
  v                                    v
haios-events.jsonl → Analyzer → Adjust vitals/reminders
```

**Implementation:** Add `just analyze-events` recipe that:
1. Reads recent events
2. Detects patterns (cycle skipping, rapid closures without CHECK)
3. Injects specific warnings based on actual behavior

---

## Spawned Work Items

### Immediate (M5-Plugin)

1. **E2-135: Close Command Enforcement**
   - Status: proposed
   - Effort: Small
   - Action: PreToolUse blocks Edit to backlog.md with "Status: complete" pattern
   - Forces: Use /close instead of manual status change
   - spawned_by: INV-020

2. **E2-136: Status Generator Archive Reading**
   - Status: proposed
   - Effort: Small
   - Action: `_discover_milestones_from_backlog()` also reads backlog_archive.md
   - Fixes: E2-129, E2-131, E2-116 phantom items
   - spawned_by: INV-020

### Future (M6-Feedback)

3. **E2-137: Event Pattern Analyzer**
   - Status: proposed
   - Effort: Medium
   - Action: `just analyze-events` reads haios-events.jsonl, detects anti-patterns
   - Closes: RESONANCE → DYNAMICS feedback loop
   - spawned_by: INV-020

4. **E2-138: Lifecycle Gate Enforcement**
   - Status: proposed
   - Effort: Medium
   - Action: PreToolUse blocks /new-plan without prior investigation
   - Promotes: Lifecycle guidance from L2 to L3
   - spawned_by: INV-020

---

## Channeling Pattern Catalog

### Effective Patterns (Use These)

| Pattern | Mechanism | Example |
|---------|-----------|---------|
| **Blocker → Alternative** | PreToolUse deny with redirect | SQL → schema-verifier |
| **Path → Command** | PreToolUse deny raw writes | docs/plans/ → /new-plan |
| **Subagent Isolation** | Task with subagent_type | Complex query → investigation-agent |
| **Automation** | PostToolUse silent action | YAML → auto-timestamp |

### Ineffective Patterns (Avoid These)

| Pattern | Problem | Evidence |
|---------|---------|----------|
| **Text Reminder** | Easy to ignore | RFC2119 reminders dismissed |
| **SHOULD in docs** | No enforcement | Skills say SHOULD, agent doesn't invoke |
| **Log-Only Events** | No feedback | 20+ events logged, never read |
| **Override Option** | Agent takes override | "skip discovery" always chosen |

---

## References

- E2-130: Example of SQL blocker → schema-verifier pattern
- INV-012: Static Registration Anti-Pattern (related discovery)
- INV-023: ReasoningBank Feedback Loop (related - suggestions ignored)
- M3-Cycles: Implementation infrastructure audited
- ADR-038: Symphony Architecture (RHYTHM, DYNAMICS, LISTENING, RESONANCE)
- Session 95, 100 observations

---
