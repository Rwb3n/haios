---
template: implementation_plan
status: complete
date: 2025-12-27
backlog_id: E2-206
title: Slim Vitals - Remove Static Infrastructure
author: Hephaestus
lifecycle_phase: plan
session: 125
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-27T13:23:11'
---
# Implementation Plan: Slim Vitals - Remove Static Infrastructure

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

Vitals will inject only dynamic operational context (~40 tokens) instead of redundant static infrastructure lists (~115 tokens), reducing per-prompt overhead by 65%.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/hooks/hooks/user_prompt_submit.py` |
| Lines of code affected | ~35 | Lines 155-187 in `_get_vitals()` |
| New files to create | 0 | N/A |
| Tests to write | 0 | Output format change, no logic tests needed |
| Dependencies | 0 | No modules import this function directly |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single function in one hook |
| Risk of regression | Low | Pure deletion, keeping core lines |
| External dependencies | Low | Only reads haios-status-slim.json |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Implementation | 5 min | High |
| Verification | 2 min | High |
| **Total** | 7 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/hooks/hooks/user_prompt_submit.py:155-187
        # Active work (top 5)
        if active_work := slim.get("active_work"):
            if active_work:
                active_str = ", ".join(active_work[:5])
                lines.append(f"Active: {active_str}")

        # Blocked items (top 3)
        if blocked := slim.get("blocked_items"):
            # ... 10 lines of blocked item formatting ...

        # Infrastructure summary
        if infra := slim.get("infrastructure"):
            if infra.get("commands"):
                lines.append("Commands: /new-*, /close, /validate, /status")
            if infra.get("skills"):
                lines.append(f"Skills: {', '.join(infra['skills'])}")
            if infra.get("agents"):
                lines.append(f"Agents: {', '.join(infra['agents'])}")
            if infra.get("mcps"):
                mcp_list = [f"{m['name']}({m['tools']})" for m in infra["mcps"]]
                lines.append(f"MCPs: {', '.join(mcp_list)}")

        lines.append("Recipes: just --list")
        lines.append("---")
```

**Behavior:** Vitals inject ~115 tokens per prompt including static infrastructure lists (commands, skills, agents, MCPs, recipes).

**Result:** Token waste on every prompt. Infrastructure is static and already documented in CLAUDE.md.

### Desired State

```python
# .claude/hooks/hooks/user_prompt_submit.py:155-165
        # Blocked items (only show if any exist) - E2-206: slim vitals
        if blocked := slim.get("blocked_items"):
            if blocked:
                blocked_count = len(blocked) if isinstance(blocked, dict) else len(blocked)
                if blocked_count > 0:
                    lines.append(f"Blocked: {blocked_count} items")

        # E2-206: Removed static infrastructure (commands, skills, agents, MCPs, recipes)
        # These are documented in CLAUDE.md and don't change mid-session
        lines.append("---")
```

**Behavior:** Vitals inject only ~40 tokens per prompt: milestone, working context, blocked count (if any).

**Result:** 65% token reduction. Dynamic context preserved, static redundancy removed.

---

## Tests First (TDD)

**SKIPPED:** Pure output format change with no logic. Verification is visual inspection of vitals output.

### Manual Verification Steps

1. After implementation, send any message to trigger vitals
2. Verify vitals output contains:
   - `--- HAIOS Vitals ---`
   - `Milestone:` line with progress
   - `Working:` line (if active work cycle)
   - `Blocked: N items` (only if blocked > 0)
   - `---`
3. Verify vitals output does NOT contain:
   - `Commands:`
   - `Skills:`
   - `Agents:`
   - `MCPs:`
   - `Recipes:`

---

## Detailed Design

### Exact Code Change

**File:** `.claude/hooks/hooks/user_prompt_submit.py`
**Location:** Lines 155-187 in `_get_vitals()`

**Current Code (to remove):**
```python
# Lines 155-187
        # Active work (top 5)
        if active_work := slim.get("active_work"):
            if active_work:
                active_str = ", ".join(active_work[:5])
                lines.append(f"Active: {active_str}")

        # Blocked items (top 3)
        if blocked := slim.get("blocked_items"):
            if blocked:
                blocked_list = []
                items = list(blocked.items())[:3] if isinstance(blocked, dict) else blocked[:3]
                for item in items:
                    if isinstance(item, tuple):
                        item_id, item_data = item
                        blockers = ",".join(item_data.get("blocked_by", []))
                        blocked_list.append(f"{item_id}[{blockers}]")
                if blocked_list:
                    lines.append(f"Blocked: {', '.join(blocked_list)}")

        # Infrastructure summary
        if infra := slim.get("infrastructure"):
            if infra.get("commands"):
                lines.append("Commands: /new-*, /close, /validate, /status")
            if infra.get("skills"):
                lines.append(f"Skills: {', '.join(infra['skills'])}")
            if infra.get("agents"):
                lines.append(f"Agents: {', '.join(infra['agents'])}")
            if infra.get("mcps"):
                mcp_list = [f"{m['name']}({m['tools']})" for m in infra["mcps"]]
                lines.append(f"MCPs: {', '.join(mcp_list)}")

        lines.append("Recipes: just --list")
        lines.append("---")
```

**Replacement Code:**
```python
        # Blocked items (only show if any exist) - E2-206: slim vitals
        if blocked := slim.get("blocked_items"):
            if blocked:
                blocked_count = len(blocked) if isinstance(blocked, dict) else len(blocked)
                if blocked_count > 0:
                    lines.append(f"Blocked: {blocked_count} items")

        # E2-206: Removed static infrastructure (commands, skills, agents, MCPs, recipes)
        # These are documented in CLAUDE.md and don't change mid-session
        lines.append("---")
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Remove Active work | Delete entirely | Redundant with Working line (E2-118) |
| Simplify Blocked | Count only | Full list with blockers is noisy |
| Remove infrastructure | Delete entirely | Already in CLAUDE.md, static |
| Remove Recipes pointer | Delete | Already in CLAUDE.md |
| Keep Session delta | Keep (lines 130-141) | Shows momentum, dynamic per-session |

### Input/Output Examples

**Current vitals output:**
```
--- HAIOS Vitals ---
Milestone: M7d-Plumbing (92%) [+13 from E2-079]
Since S123: +13%
Working: INV-027 [investigation:discovery/hypothesize]
Commands: /new-*, /close, /validate, /status
Skills: audit, checkpoint-cycle, close-work-cycle, ... (13 items)
Agents: investigation-agent, preflight-checker, ... (6 items)
MCPs: haios-memory(13), context7(2)
Recipes: just --list
---
```

**Slim vitals output (after fix):**
```
--- HAIOS Vitals ---
Milestone: M7d-Plumbing (92%) [+13 from E2-079]
Since S123: +13%
Working: INV-027 [investigation:discovery/hypothesize]
---
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No blocked items | No "Blocked:" line shown | Visual verification |
| Blocked items exist | Show "Blocked: N items" | Visual verification |
| No work cycle | No "Working:" line shown | Already handled by E2-118 |

---

## Implementation Steps

### Step 1: Replace vitals code
- [ ] Edit `.claude/hooks/hooks/user_prompt_submit.py` lines 155-187
- [ ] Replace Active work, Blocked items (detailed), Infrastructure, Recipes with simplified version

### Step 2: Visual verification
- [ ] Send a message to trigger vitals
- [ ] Confirm vitals output is slim (no Commands/Skills/Agents/MCPs/Recipes)
- [ ] Confirm milestone, session delta, working context still present

### Step 3: README Sync
- [ ] **SKIPPED:** No README changes needed - internal hook modification only

---

## Verification

- [ ] Visual inspection of vitals output
- [ ] Confirm no Commands/Skills/Agents/MCPs/Recipes lines

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Claude forgets infrastructure | Low | CLAUDE.md has complete lists |
| Blocked items less visible | Low | Count summary still shows if > 0 |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/hooks/hooks/user_prompt_submit.py` | Lines 155-165 have slim vitals code | [ ] | |
| Vitals output | No Commands/Skills/Agents/MCPs/Recipes | [ ] | |

**Completion Criteria (DoD per ADR-033):**
- [ ] Code change verified
- [ ] WHY captured (reasoning stored to memory)
- [ ] Visual verification complete

---

## References

- E2-118: Added Working line to vitals (this session)
- Session 125: Reasoning on vitals token optimization

---
