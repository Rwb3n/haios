---
template: architecture_decision_record
status: accepted
date: 2026-02-20
adr_id: ADR-047
title: "Tiered Coldstart Context Injection"
author: Hephaestus
session: 412
lifecycle_phase: decide
decision: accepted
spawned_by: WORK-162
traces_to:
  - REQ-CONFIG-001
  - L3.3
related:
  - ADR-045
memory_refs: [84835, 84836, 85459, 85915, 85916, 85917, 85918, 85919, 85920, 85921, 85922, 85923, 85924]
version: "1.1"
generated: 2026-02-20
last_updated: 2026-02-20T23:15:00
---
# ADR-047: Tiered Coldstart Context Injection

@docs/work/active/WORK-162/WORK.md
@.claude/haios/epochs/E2_8/arcs/call/ARC.md

> **Status:** Accepted
> **Date:** 2026-02-20
> **Decision:** Accepted (Session 412)

---

## Decision Criteria (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Document alternatives | MUST | 3 options documented in Considered Options |
| Explain WHY | MUST | Rationale in Decision section |
| Link to memory | SHOULD | Memory 84835, 84836, 85459, 85923, 85924 |
| Get operator approval | MUST | Update decision field from "pending" to "accepted/rejected" |

---

## Context

### The Problem

Coldstart currently produces an **informed** agent but not an **operational** agent (mem:85923). After `/coldstart`, the agent knows WHO it is (identity) and WHAT work is available (queue), but not HOW to execute (operational patterns, tier model, recipe catalogue).

**Evidence (S393/S394):** A 200k-context agent ran coldstart successfully, then attempted 4 raw Python imports instead of using `just` recipes, burning ~15% of its context on failures (mem:85915). The agent never read CLAUDE.md (mem:85918), had no knowledge of `just` recipes (mem:85919), and violated the ADR-045 tier model (mem:85920).

### Token Budget Analysis

Current coldstart token allocation (E2.8, 4 active arcs):

| Component | Lines | Automated? | Est. Tokens |
|-----------|-------|-----------|-------------|
| Identity loader output | ~50 | YES | ~150 |
| Session loader output | ~30 | YES | ~90 |
| Work loader output | ~20 | YES | ~60 |
| Epoch validator output | ~10 | YES | ~30 |
| **Subtotal automated** | **~110** | | **~330** |
| EPOCH.md (manual Read) | 230 | NO | ~690 |
| 4x ARC.md (manual Read) | 272 | NO | ~816 |
| CLAUDE.md (manual Read) | 159 | NO | ~477 |
| Memory ref queries | ~50 | NO | ~150 |
| **Subtotal manual** | **~711** | | **~2,133** |
| **Total** | **~821** | | **~2,463** |

**88% of coldstart tokens come from manual Read calls.** The orchestrator automates only 12%.

### The Root Cause

The orchestrator was designed as a sequential loader pipeline (identity → session → work). It extracts and compresses manifesto content (727 lines → 50) but stops there. Epoch context, operational patterns, and agent instructions remain manual because they were added to `coldstart.md` as afterthoughts (Steps 3-5), not integrated into the orchestrator.

### Disproportionate Overhead

Full coldstart is the same whether the session is:
- Implementing a new feature (needs full context)
- Continuing yesterday's work (needs only delta)
- Fixing a typo in docs (needs almost nothing)

This violates L3.20 (Proportional Governance): governance overhead should scale with blast radius (mem:84835, 84836).

---

## Decision Drivers

1. **L3.20 Proportional Governance:** Overhead must scale with work complexity. A doc fix session should not pay the same coldstart cost as an epoch-opening session.
2. **Operational agent, not informed agent (mem:85924):** After coldstart, the agent must be able to execute work without reading additional files. The orchestrator output IS the operating manual.
3. **Token budget conservation:** 88% manual reads means the orchestrator is not fulfilling its purpose.
4. **S393/S394 failure evidence:** Real agent failure from missing HOW context proves the current contract is insufficient.
5. **L3.3 Context Must Persist:** Knowledge compounds across sessions. Tiering enables the right context for the right session type.

---

## Considered Options

### Option A: Extend Orchestrator with Epoch + Operations Loaders (Monolithic)

**Description:** Add two new loaders to `ColdstartOrchestrator`: an `EpochLoader` (extracts and compresses EPOCH.md + ARC.md files, like IdentityLoader does for manifesto) and an `OperationsLoader` (injects CLAUDE.md operational patterns, tier model, recipe catalogue). All coldstart runs the full pipeline. No tiering.

**Pros:**
- Simplest implementation — extends existing pattern
- All sessions get full context (no risk of under-loading)
- Identity loader compression pattern already proven (~93% reduction)

**Cons:**
- Still disproportionate for housekeeping sessions (full load for a typo fix)
- Does not address L3.20 (Proportional Governance)
- Epoch context (502 lines) may not compress as well as manifesto (tables, work item lists are already dense)
- Adds latency to every session start

### Option B: Tiered Coldstart with Auto-Detection (Recommended)

**Description:** Three coldstart tiers with automatic detection based on session intent:

| Tier | When | Loads | Est. Tokens | Manual Reads |
|------|------|-------|-------------|--------------|
| **Full** | New epoch/arc work, first session after transition | Identity + Session + Work + Epoch + Operations | ~800-1000 | 0 |
| **Light** | Continuation of prior session work | Session + Active work item context | ~300-400 | 0 |
| **Minimal** | Housekeeping (doc fixes, drift correction, admin) | Session number + config only | ~100-150 | 0 |

**Auto-detection heuristic:** Inspect checkpoint `pending` field, operator intent, and staleness:
- If operator specifies `/coldstart full` or `/coldstart minimal` → explicit tier (override)
- If checkpoint timestamp > `tier_detection.max_age_hours` (default: 24) → Full (stale checkpoint, reload everything)
- If checkpoint shows in-progress work item and is fresh → Light (continuation)
- Default (no argument, no in-progress work) → Full

**Staleness threshold:** Configurable in coldstart.yaml as `tier_detection.max_age_hours: 24`. Prevents Light tier selection from stale checkpoint data, which would replicate the S393/S394 missing-context failure via automation.

**New loaders required:**
1. `EpochLoader` — Reads EPOCH.md + active ARC.md files at runtime, extracts status tables, chapter progress, exit criteria. Compresses like IdentityLoader. Reads source files live every invocation (no caching — epoch content changes frequently).
2. `OperationsLoader` — Injects operational HOW: tier model (ADR-045), recipe catalogue (`just --list` filtered), module paths, common patterns (WorkEngine needs GovernanceLayer, ConfigLoader.get() for paths). **Reads source files live at runtime** (justfile, CLAUDE.md, ADR-045) — not pre-baked or cached. Rationale: operational content changes when recipes are added, modules move, or ADRs are revised. Stale operational context is a silent failure that replicates the S393/S394 problem (agent acts on wrong HOW). The per-session cost of live reads is acceptable since coldstart runs once per session.

**Changes to coldstart.md:**
- Steps 3-5 (manual Reads) eliminated — folded into loaders
- Step 1 (read haios.yaml) remains — config drives everything
- New: tier argument parsing
- New: `[PHASE: EPOCH]` and `[PHASE: OPERATIONS]` in output

**coldstart.yaml updated:**
```yaml
tier_detection:
  max_age_hours: 24  # Checkpoint older than this → escalate to Full

tiers:
  full:
    phases: [identity, session, work, epoch, operations]
  light:
    phases: [session, work_active_only]
  minimal:
    phases: [session_number_only]

phases:
  - id: identity
    breathe: true
  - id: session
    breathe: true
  - id: work
    breathe: false
  - id: epoch
    breathe: true
  - id: operations
    breathe: false
```

**Pros:**
- Directly addresses L3.20 (proportional overhead)
- Zero manual Reads in any tier (WORK-162 AC #2)
- Minimal tier enables fast housekeeping sessions
- Light tier enables efficient continuation
- Auto-detection reduces operator friction

**Cons:**
- More complex implementation (tier selection logic, 2 new loaders)
- Auto-detection could misfire (defaulting to wrong tier)
- Must keep tier loaders in sync with content changes (new arc = update EpochLoader)
- Risk of under-loading in Light/Minimal tiers (agent lacks context it needs)

### Option C: MCP Server Replaces Orchestrator

**Description:** Replace the Python orchestrator with an MCP server (`haios-operations`) that exposes coldstart as a tool. Agent calls `mcp__haios_operations__coldstart(tier="full")` instead of `just coldstart-orchestrator`. The MCP server returns structured JSON, not printed text.

**Pros:**
- Native agent interface (MCP tool call, not bash + text parsing)
- Structured output (JSON fields, not `[PHASE:]` markers in text)
- Could serve epoch/work/operations context on demand (progressive disclosure)
- Aligns with E2.8 CH-066 (MCPOperationsServer)

**Cons:**
- Largest implementation scope (new MCP server)
- MCP server infrastructure doesn't exist yet (CH-066 is "Planning")
- Python loaders would need rewrite or wrapping
- Dependency on MCP server stability (single point of failure for coldstart)
- Premature — the loaders work; the gap is coverage, not interface

---

## Decision

**Option B: Tiered Coldstart with Auto-Detection.**

Rationale:
1. Directly solves the disproportionate overhead problem (L3.20) that Option A ignores.
2. Stays within the proven loader pipeline architecture — extends rather than replaces.
3. Two new loaders (EpochLoader, OperationsLoader) follow the established pattern (IdentityLoader, SessionLoader, WorkLoader).
4. Auto-detection with explicit override (`/coldstart light`) gives operator control without friction.
5. Option C (MCP server) is the right long-term answer but depends on CH-066 infrastructure that doesn't exist yet. Option B is the bridge.

**The minimum viable context contract after coldstart (mem:85923):**
1. **Identity** — L0-L3 mission, epoch context (via IdentityLoader + EpochLoader)
2. **Prior** — Last checkpoint, pending, drift warnings (via SessionLoader)
3. **Work** — Queue options, alignment warnings (via WorkLoader)
4. **Operations** — Tier model, recipe catalogue, module paths, common patterns (via OperationsLoader)

After Full coldstart: zero manual Reads. The orchestrator output IS the agent's operating knowledge.

---

## Consequences

**Positive:**
- Housekeeping sessions start in ~100 tokens instead of ~2,500
- Continuation sessions skip redundant identity/epoch loading
- Agent is operational after coldstart, not just informed
- `coldstart.md` simplified (no manual Read steps)
- Token budget freed for actual work

**Negative:**
- Two new loaders to implement and maintain (EpochLoader, OperationsLoader)
- Tier auto-detection logic adds complexity
- Light/Minimal tiers may need escape hatch if agent discovers it needs more context mid-session
- EpochLoader must handle epoch transitions (new epoch = different file structure)

**Neutral:**
- `coldstart.yaml` grows but remains declarative
- Survey-cycle still chains after coldstart (no change to work selection)
- Option C (MCP) can subsume Option B later — loaders become MCP tool implementations

---

## Escape Hatch (Design Specification — Implemented in CLI Argument Forwarding Task)

If an agent in Light or Minimal tier discovers it needs full context, it can invoke `just coldstart-orchestrator --extend` to load additional phases without re-running the full pipeline. **Note: `--extend` does not exist in the current codebase. It is specified here and implemented as part of the CLI argument forwarding work item.** The `--extend` flag:
- Skips Phase 0 (orphan detection) — the current session is active, not orphaned
- Skips Session Start ceremony — already ran
- Runs only the specified additional phases (e.g., `--extend epoch operations`)
- Each loader is idempotent — re-running identity or session produces the same output

**Output integration:** When `--extend` is invoked mid-session, the orchestrator emits only the requested phases under an `[EXTEND: epoch operations]` header instead of the full `[READY FOR SELECTION]` block. This prevents ambiguity with the original coldstart output already in agent context. The extend output appends to — not replaces — the initial coldstart context.

Without `--extend`, a bare `just coldstart-orchestrator` mid-session would trigger `_check_for_orphans()` on the active session, potentially logging a synthetic session-end for the current live session. The `--extend` flag prevents this.

---

## Implementation

Implementation spawns from this ADR as work items under CH-061. **Child work items are scaffolded after this ADR reaches `accepted` status.** WORK-162 `spawned_children` is updated at that point.

- [ ] **EpochLoader** — New loader in `lib/`. Reads EPOCH.md + active ARC.md files live at runtime, extracts/compresses status, chapters, exit criteria. Follow IdentityLoader pattern.
- [ ] **OperationsLoader** — New loader in `lib/`. Reads source files live at runtime (justfile, CLAUDE.md, ADR-045). Injects tier model, recipe catalogue, module paths, common patterns. No caching — always current.
- [ ] **Tier selection logic** — Update `ColdstartOrchestrator.run()` to accept tier argument. Wire auto-detection heuristic with staleness threshold.
- [ ] **CLI argument forwarding** — Update `coldstart_orchestrator.py __main__` with `argparse` for tier argument and `--extend` flag. Update justfile `coldstart-orchestrator` recipe to forward arguments to Python script.
- [ ] **coldstart.yaml update** — Add `tier_detection`, tier definitions, and new phase entries.
- [ ] **coldstart.md update** — Remove Steps 3-5 (manual Reads). Add tier argument documentation. Document `--extend` escape hatch.
- [ ] **Tests** — Unit tests for EpochLoader, OperationsLoader, tier selection. Integration tests for auto-detection: (a) checkpoint with in-progress work → Light, (b) no checkpoint → Full, (c) stale checkpoint → Full, (d) explicit override → specified tier.
- [ ] **Verification** — Run full coldstart with new loaders, confirm zero manual Reads, measure token savings vs baseline.

---

## References

- @.claude/haios/epochs/E2_8/EPOCH.md (104% problem, Arc 1 call)
- @.claude/haios/lib/coldstart_orchestrator.py (current orchestrator)
- @.claude/haios/lib/identity_loader.py (compression pattern)
- @docs/ADR/ADR-045-three-tier-entry-point-architecture.md (tier model)
- @docs/work/active/WORK-162/WORK.md (parent work item)
- Memory: 84835, 84836 (coldstart overhead), 85459 (most tokens on context), 85923 (minimum viable contract), 85924 (CH-061 reframing)
