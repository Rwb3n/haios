---
template: architecture_decision_record
status: accepted
date: 2025-12-13
adr_id: ADR-035
title: "RFC 2119 Governance Signaling"
author: Hephaestus
session: 65
backlog_id: E2-037
lifecycle_phase: decide
decision: accepted
---
# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 17:11:54
# ADR-035: RFC 2119 Governance Signaling

@docs/README.md
@docs/epistemic_state.md

> **Status:** Accepted
> **Date:** 2025-12-13
> **Decision:** Accepted (Session 66)
> **Backlog:** E2-037

---

## Context

Session 65 strategic analysis revealed a fundamental gap in HAIOS governance: **work events do not automatically spawn artifacts**.

### The Two-Track Problem

HAIOS operates on two parallel tracks that are not synchronized:

```
WORK TRACK (ephemeral, in-session)          ARTIFACT TRACK (persistent, documents + memory)
--------------------------------------      ---------------------------------------------
  discover  ─────────────────────?──────>   INVESTIGATION
  design    ─────────────────────?──────>   ADR
  plan      ─────────────────────?──────>   PLAN
  implement ─────────────────────?──────>   code (git)
  verify    ─────────────────────?──────>   REPORT
  close     ─────────────────────?──────>   CHECKPOINT + memory
```

The `?` arrows represent **missing bridges**. Currently, only manual intervention connects work events to artifact creation.

### Why Mechanical Automation Fails

Hooks (PreToolUse, PostToolUse, UserPromptSubmit, Stop) can only detect:
- File operations (Write, Edit)
- User messages (text only)
- Session boundaries (Stop)

Hooks **cannot** detect:
- Claude's reasoning (discoveries happen in thought)
- Semantic events (decisions, insights, verifications)
- Intent behind actions

This means mechanical automation (hook-based detection and artifact creation) is fundamentally limited for semantic events.

### Memory Reference

The full "HAIOS Song" ontology analysis is captured in memory:
- **Concepts:** 70904-70939
- **Source:** session:65:strategic-analysis:haios-song-ontology

---

## Decision Drivers

1. **Semantic events are invisible to hooks** - Discoveries and decisions happen in Claude's reasoning, not in hook-visible events
2. **Manual bridging is error-prone** - Session 63 discovered a bug but didn't spawn E2-FIX-002; Session 64 had to manually create it
3. **Governance philosophy: "Doing right should be easy"** - Guidance should flow naturally, not require constant vigilance
4. **Claude understands RFC 2119** - MUST/SHOULD/MAY semantics are well-established in Claude's training
5. **Graduated compliance** - Not everything needs hard enforcement; SHOULD/MAY allow judgment

---

## Considered Options

### Option A: Mechanical Automation (Hook-Based)

**Description:** Enhance hooks to detect patterns and auto-create artifacts.

```
PostToolUse detects file in docs/plans/* → auto-validate format
UserPromptSubmit detects "bug" keyword → auto-suggest investigation
Stop hook → auto-create checkpoint draft
```

**Pros:**
- Fully automated, no Claude cooperation needed
- Consistent, deterministic behavior

**Cons:**
- Limited to hook-visible events (file ops, user messages)
- Cannot detect semantic events (discoveries in Claude's reasoning)
- High false positive rate on keyword detection
- Brittle pattern matching

### Option B: Semantic Guidance (RFC 2119 Signals)

**Description:** Use MUST/SHOULD/MAY keywords to guide Claude toward proper commands/skills/agents at the right moments. Signals embedded in CLAUDE.md and optionally injected via hooks.

```markdown
## Governance Triggers (RFC 2119)

| Situation | Strength | Action |
|-----------|----------|--------|
| Discover bug/gap/issue | MUST | /new-investigation |
| Make architectural decision | SHOULD | /new-adr |
| Session work complete | SHOULD | /new-checkpoint |
| Close work item | MUST | /close |
| Need database schema | MUST | schema-verifier subagent |
```

**Pros:**
- Leverages Claude's semantic understanding
- Graduated compliance (MUST vs SHOULD vs MAY)
- Extensible without code changes
- Fails gracefully (work continues if SHOULD ignored)
- Auditable (rules are explicit text)

**Cons:**
- Relies on Claude compliance (no enforcement)
- May be ignored in long sessions
- No guarantee of consistency

### Option C: Hybrid (Mechanical + Semantic)

**Description:** Combine mechanical automation for detectable events with semantic guidance for reasoning-based events.

- **Mechanical:** PostToolUse validates governed documents, Stop hook prompts for checkpoint
- **Semantic:** CLAUDE.md rules guide discovery→investigation, decision→ADR

**Pros:**
- Best of both worlds
- Mechanical for what's detectable, semantic for what's not
- Defense in depth

**Cons:**
- More complexity to maintain
- Potential conflict between mechanical and semantic guidance

---

## Decision

**Option B: Semantic Guidance (RFC 2119 Signals)** with Option C elements added incrementally.

### Rationale

1. **Primary limitation is semantic detection**, not lack of automation. Hooks can't see Claude's reasoning.
2. **RFC 2119 is native to Claude** - MUST/SHOULD/MAY are well-understood semantics.
3. **Guidance over enforcement** aligns with HAIOS philosophy ("Doing right should be easy").
4. **Incremental path** - Start with semantic, add mechanical for clear wins.

### The Signal System

#### Tier 1: MUST (Absolute Requirements)

| Trigger | Action | Rationale |
|---------|--------|-----------|
| Discover bug/gap/issue | `/new-investigation` | Document before fixing |
| Any SQL query needed | `schema-verifier` subagent | Verify schema first |
| Close work item | `/close <id>` | Validate DoD |
| Create governed document | `/new-*` command | Use templates |

#### Tier 2: SHOULD (Strong Recommendations)

| Trigger | Action | Rationale |
|---------|--------|-----------|
| Make architectural decision | `/new-adr` | Document significant choices |
| Session work complete | `/new-checkpoint` | Capture progress |
| Verification complete | `/new-report` | Document results |
| Complex memory retrieval | `memory-agent` skill | Better context |

#### Tier 3: MAY (Optional)

| Trigger | Action | Rationale |
|---------|--------|-----------|
| Exploring codebase | `Explore` subagent | Faster than manual grep |
| Quick status check | `/status` | Quick health check |

---

## Consequences

**Positive:**
- Work events more likely to spawn proper artifacts
- Lifecycle compliance improves without hard blocking
- Claude's semantic understanding leveraged (not fought)
- Rules are auditable and maintainable
- Graduated enforcement allows judgment

**Negative:**
- No guarantee of compliance (Claude can ignore SHOULD/MAY)
- May need periodic reinforcement in long sessions
- Rules must be updated as new patterns emerge

**Neutral:**
- Shifts responsibility from hooks to Claude's judgment
- Creates explicit governance contract between system and agent

---

## Implementation

### Phase 1: Static Rules (CLAUDE.md)

- [ ] Add "Governance Triggers" section to CLAUDE.md
- [ ] Define MUST/SHOULD/MAY tables
- [ ] Reference this ADR

### Phase 2: Dynamic Reminders (UserPromptSubmit)

- [ ] Enhance UserPromptSubmit to detect trigger keywords
- [ ] Inject contextual reminders (e.g., "Discovery detected. MUST use /new-investigation")
- [ ] Measure false positive rate

### Phase 3: Compliance Tracking

- [ ] Track signal compliance over 5 sessions
- [ ] Identify ignored signals and patterns
- [ ] Iterate on trigger definitions

### Phase 4: Mechanical Additions (Optional)

- [ ] PostToolUse validation for governed documents
- [ ] Stop hook checkpoint prompt
- [ ] Evaluate hybrid value

---

## References

- **Memory:** Concepts 70904-70939 (HAIOS Song Ontology)
- **Backlog:** E2-037 (RFC 2119 Governance Signaling System)
- **Related ADRs:**
  - ADR-033: Work Item Lifecycle Governance
  - ADR-034: Document Ontology & Work Lifecycle
- **Related Items:**
  - E2-034: Cold Start Context Optimization
  - E2-035: Checkpoint Lifecycle Enhancement
  - E2-036: UpdateHaiosStatus Regex Pattern Fix

---
