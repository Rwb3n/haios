---
template: implementation_plan
status: complete
date: 2025-12-06
backlog_id: E2-001
title: "Epoch 2: Memory System Leverage"
id: PLAN-EPOCH2-008
author: Hephaestus
priority: high
session: 37
lifecycle_phase: plan
audit_session: 56
audit_note: "Phase 1 (governance integration) ~80% complete. Phase 2-3 (activity indexing, extraction quality) not started. Remains relevant roadmap for E2-021."
closed_session: 73
closed_date: 2025-12-14
resolution: "Superseded by organic evolution: Phase 1 -> ADR-037 + E2-059; Phase 2 -> deprioritized; Phase 3 -> INV-015"
superseded_by: [ADR-037, INV-014, INV-015]
---
# generated: 2025-12-06
# System Auto: last updated on: 2025-12-14 14:47:52
# PLAN-EPOCH2-008: Memory System Leverage

@docs/epistemic_state.md
@.claude/skills/memory-agent/prompt.md

> **Problem:** Infrastructure exists but isn't leveraged. Commands are file-based. Timestamps are comments. Extraction produces generic strategies. The interface works but internal mechanism is smoke and mirrors.
>
> **Solution:** Integrate memory into governance layer. Make everything observable queryable.

---

## Background

Session 37 identified that while the ReasoningBank loop is mechanically closed, the semantic value is low:

1. **Extraction quality:** Strategies are generic ("Leverage Default Hybrid Search") not domain-specific
2. **Governance isolation:** /coldstart, /haios, /status read files, don't query memory
3. **Timestamps unused:** `System Auto: last updated on` exists in files but isn't indexed
4. **Activity invisible:** No way to query "what was modified recently?"

The memory-agent skill documents the correct workflow, but the system doesn't follow it.

---

## Objectives

### O1: Memory-Integrated Governance
Make slash commands use the memory system, not just files.

### O2: Observable → Queryable
Every file modification, timestamp, and activity should be indexed in memory.

### O3: Domain-Specific Extraction
Revise extraction prompt to capture HAIOS-specific learnings, not meta-patterns.

---

## Implementation

### Phase 1: Governance Integration

#### P1.1: /coldstart Enhancement
**File:** `.claude/commands/coldstart.md`

Current:
```
1. Read CLAUDE.md
2. Read epistemic_state.md
3. Read latest checkpoint
4. Read haios-status.json
```

Enhanced:
```
1. Read CLAUDE.md
2. Read epistemic_state.md
3. Read latest checkpoint
4. Read haios-status.json
5. Query: memory_search_with_experience("HAIOS session context initialization")
6. Inject retrieved strategies into summary
```

#### P1.2: /haios Enhancement
**File:** `.claude/commands/haios.md`

Current:
```
Read .claude/haios-status.json
```

Enhanced:
```
1. Read .claude/haios-status.json
2. Query: memory_stats()
3. Query: memory_search_with_experience("recent HAIOS activity")
4. Combine static config with live intelligence
```

#### P1.3: /checkpoint Enhancement
**File:** `.claude/commands/checkpoint.md`

Current:
```
Create checkpoint file from template
```

Enhanced:
```
1. Create checkpoint file from template
2. Store: memory_store(
     content="Session N key finding: <summary>",
     content_type="techne",
     source_path="checkpoint:session-N"
   )
3. Checkpoint is now in BOTH file system AND memory
```

---

### Phase 2: Activity Indexing

#### P2.1: PostToolUse Memory Storage
**File:** `.claude/hooks/PostToolUse.ps1`

After adding timestamp to file, ALSO store activity:
```powershell
# After file modification
$activity = @{
    event = "file_modified"
    path = $filePath
    timestamp = $timestamp
}
# Call Python to store in memory
python memory_activity_store.py $activityJson
```

**New file:** `.claude/hooks/memory_activity_store.py`
```python
# Stores file modification events to memory
# Makes activity queryable via memory_search
```

#### P2.2: Timestamp Indexing
Option A: On-demand - query parses files for timestamps
Option B: On-modify - PostToolUse indexes timestamp to memory

Recommend: Option B (real-time indexing)

---

### Phase 3: Extraction Quality

#### P3.1: Revise Extraction Prompt
**File:** `haios_etl/extraction.py` - `extract_strategy()` method

Current prompt (inferred):
```
"Extract a transferable strategy from this session"
```

Revised prompt:
```
"What specific decision or approach led to this outcome?
What would you tell a future HAIOS session facing this same task?
Focus on:
- What worked/failed in THIS codebase
- Concrete file paths, function names, or patterns
- Gotchas specific to this project"
```

#### P3.2: Validation
After change, verify:
- Strategies mention HAIOS-specific concepts
- Fewer generic "search pattern" strategies
- Domain terms appear (Greek Triad, ReasoningBank, epistemic_state, etc.)

---

## Success Criteria

| Criterion | Metric |
|-----------|--------|
| /coldstart uses memory | Outputs "Retrieved N strategies" |
| /haios shows live stats | Includes memory_stats() output |
| Activity is queryable | "recent modifications" returns results |
| Extraction is domain-specific | <20% generic strategies in new traces |

---

## Dependencies

- Memory MCP server running (haios-memory)
- API key for Gemini (extraction)
- Cross-pollination working (verified Session 37)

---

## Risks

| Risk | Mitigation |
|------|------------|
| Hook timeout | Memory calls add latency - set appropriate timeouts |
| Over-indexing | Don't store every trivial change - filter noise |
| Prompt regression | A/B test extraction before full rollout |

---

## Design Decisions

### DD-021: Governance-Memory Integration Pattern
Commands should query memory AFTER loading files, injecting strategies into their output.

### DD-022: Activity Storage Granularity
Store file modification events, not character-level changes. One event per file per save.

### DD-023: Extraction Prompt Domain Grounding
Prompt must explicitly reference "this codebase" and "HAIOS" to anchor strategies.

---

## References

- Session 37 finding: Concept ID 62512 (extraction quality gap)
- memory-agent skill: `.claude/skills/memory-agent/prompt.md`
- ReasoningBank paper: `docs/libraries/2509.25140v1.pdf`

---

**Status:** Draft
**Next:** Operator approval, then Phase 1 implementation


<!-- VALIDATION ERRORS (2025-12-06 22:30:45):
  - ERROR: Missing required fields: directive_id
-->


<!-- VALIDATION ERRORS (2025-12-14 14:47:45):
  - ERROR: Invalid status 'superseded' for implementation_plan template. Allowed: draft, approved, rejected, complete
-->
