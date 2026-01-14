---
template: handoff
version: 1.0
type: architecture
date: 2025-12-06
author: Hephaestus (Builder)
status: superseded
priority: high
estimated_effort: 4-6 hours
---
# generated: 2025-12-06
# System Auto: last updated on: 2025-12-09 20:38:45
# Handoff: File-Based Epoch Architecture

## Executive Summary

This handoff describes the architecture for **file-based session capture** that enables the Governance Flywheel's Feedback stage and gates Epoch 2 promotion.

**Core Insight:** AI systems naturally read/write files. Use files as the collaboration interface, database as search index.

---

## Problem Statement

### Current Gap
1. AI systems (Claude Code, Gemini CLI) don't naturally collaborate with HAIOS
2. Memory is stored directly to database - no human review step
3. Governance Flywheel's **Feedback stage is missing**
4. No audit trail of reasoning for human inspection

### Why This Matters
- HAIOS is a **Trust Engine** - trust requires auditability
- Epoch 2 requires **validated, refined** knowledge
- Can't validate what you can't review
- Can't refine what you can't see

---

## Proposed Architecture

### Session Directory Structure
```
sessions/
  <session-id>/              # e.g., 2025-12-06-session-34
    metadata.json            # Session start time, context, etc.
    context-injected.md      # What hooks injected at start
    turns/
      turn-001.md            # User prompt + Claude response
      turn-002.md            # Next turn
      ...
    reasoning/
      trace-001.json         # Memory search: query, results, strategy
      trace-002.json         # Another search
    tools/
      bash-001.json          # Bash command + output
      edit-001.json          # File edit details
      read-001.json          # File read
    synthesis/
      summary.md             # SESSION_SYNTHESIS_REPORT (generated later)
```

### Three-Phase Flow

**Phase 1: RAW CAPTURE** (During session)
- SessionStart hook creates directory
- Every turn logged to `turns/turn-XXX.md`
- Memory searches logged to `reasoning/`
- Tool calls logged to `tools/`
- **Output:** Complete, low-trust audit trail

**Phase 2: SYNTHESIS** (Post-session, deliberate)
- Human or agent reviews session files
- Generates `SESSION_SYNTHESIS_REPORT`
- Identifies learnings, decisions, outcomes
- **Output:** Medium-trust, curated summary

**Phase 3: RATCHET** (Consolidation)
- Refined insights → memory database
- New ADRs, handoffs, checkpoints generated
- Validation Agent checks quality (NCCR/IUR)
- **Output:** High-trust, canonical knowledge

---

## Implementation Plan

### Hook 1: SessionStart (New)
**Event:** SessionStart
**Action:** Create session directory structure
```powershell
# Pseudocode
$sessionId = "$(Get-Date -Format 'yyyy-MM-dd')-session-$([guid]::NewGuid().ToString().Substring(0,8))"
New-Item -ItemType Directory -Path "sessions/$sessionId/turns"
New-Item -ItemType Directory -Path "sessions/$sessionId/reasoning"
New-Item -ItemType Directory -Path "sessions/$sessionId/tools"
# Write metadata.json with session start info
```

### Hook 2: UserPromptSubmit (Modify existing)
**Current:** Injects memory context
**Add:** Log injected context to `context-injected.md`

### Hook 3: Stop (Modify existing)
**Current:** Extracts reasoning from transcript
**Add:** Write turn summary to `turns/turn-XXX.md`

### Hook 4: PostToolUse (Modify existing)
**Current:** Updates timestamps
**Add:** Log tool calls to `tools/<tool>-XXX.json`

### New Component: ReasoningLogger
**Location:** `.claude/hooks/reasoning_logger.py`
**Triggered by:** memory_retrieval.py after each search
**Action:** Write search details to `reasoning/trace-XXX.json`

---

## Integration Points

### With Validation Agent
- Session files provide test cases for NCCR (known facts)
- Failed sessions inform IUR (what to refuse)
- @docs/specs/TRD-VALIDATION-AGENT-v1.md

### With Multi-Index Architecture
- Session synthesis feeds Graph Index (relationships discovered)
- Session summaries feed Summary Index
- @docs/reports/2025-12-04-REPORT-multi-index-architecture.md

### With Governance Flywheel
```
Principles → Execution → Feedback → Improvement
                              ↑
                              │
                     SESSION FILES ENABLE THIS
```

---

## Key References

- @docs/checkpoints/2025-12-05-SESSION-33-EXTENDED.md - Full context
- @docs/VISION_ANCHOR.md - LangExtract + ReasoningBank pillars
- @docs/vision/2025-11-30-VISION-INTERPRETATION-SESSION.md - Transformation engine
- @docs/specs/TRD-VALIDATION-AGENT-v1.md - Epoch promotion gates
- @haios_etl/retrieval.py - ReasoningAwareRetrieval

---

## Acceptance Criteria

- [ ] SessionStart hook creates directory structure
- [ ] Each turn written to `turns/turn-XXX.md`
- [ ] Memory searches logged to `reasoning/`
- [ ] Tool calls logged to `tools/`
- [ ] Can reconstruct full session from files alone
- [ ] Human can review, edit, and refine session files
- [ ] Refined files can be re-ingested to memory

---

## Post-Compact Instructions

1. **Refresh docs first** - Read this handoff + checkpoint before coding
2. **Query memory** - Search for "session file architecture" context
3. **Start with SessionStart hook** - Foundation for everything else
4. **Test incrementally** - Each hook independently before integration

---

## Questions for Operator

1. **Session ID format:** `YYYY-MM-DD-session-<short-guid>` or different?
2. **Turn format:** Markdown with frontmatter or plain?
3. **Retention policy:** Keep all sessions forever or prune?
4. **Synthesis trigger:** Manual command or automatic on session end?

---

## Resolution: SUPERSEDED

**Date:** 2025-12-09
**Session:** 52
**Decision:** This handoff is superseded by the architecture built in Sessions 38-51.

**Rationale:**
The proposed file-based raw capture approach was replaced by a memory-centric architecture:

| Proposed | Implemented |
|----------|-------------|
| `sessions/` directory with raw turns | Checkpoints as curated session summaries |
| Every turn logged to files | Context lives in conversation, extracted at boundaries |
| Reasoning traces to files | Stop.ps1 extracts reasoning directly to memory |
| Tool calls logged | PostToolUse timestamps, no raw logging |
| Three-phase file workflow | Memory ingestion + checkpoint review |

**Superseding Artifacts:**
- ADR-031: Workspace Awareness (operational self-awareness via haios-status.json)
- Checkpoint system: `docs/checkpoints/` with template governance
- Stop hook: ReasoningBank extraction to memory
- `/coldstart`, `/workspace` commands for session initialization

**The "Feedback stage" this handoff aimed to enable is now served by:**
1. Checkpoint review (human-readable session summaries)
2. Memory search (what was learned is queryable)
3. `/workspace` command (surfaces outstanding items)
4. haios-status.json (operational state snapshot)
