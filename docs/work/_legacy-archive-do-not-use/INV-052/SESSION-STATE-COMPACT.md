# generated: 2025-12-29
# System Auto: last updated on: 2025-12-29T21:42:33
# HAIOS Session State System (Compact)

Generated: 2025-12-29 | Full version: SESSION-STATE-DIAGRAM.md (~1050 lines, ~15-20k tokens)

## 1. Hook Layer

```
UserPromptSubmit → refresh status, inject vitals, context % warning
PreToolUse      → SQL blocking, PowerShell blocking, path governance
PostToolUse     → timestamps, cycle transition logging, error capture
Stop            → ReasoningBank extraction
```

All routed via `.claude/hooks/hook_dispatcher.py`

## 2. Session Lifecycle

```
/coldstart → just session-start N → [WORK] → checkpoint-cycle → just session-end N
```

**Phases:**
1. **INIT:** coldstart reads config, status, checkpoint; queries memory (session_recovery)
2. **WORK:** hooks fire on each prompt/tool; cycle transitions logged
3. **END:** checkpoint-cycle (SCAFFOLD→FILL→VERIFY→CAPTURE→COMMIT)

## 3. State Files

| File | Purpose | Updated By |
|------|---------|------------|
| `haios-status-slim.json` | Compact status, session delta | UserPromptSubmit hook |
| `haios-status.json` | Full workspace status | `just update-status` |
| `haios-events.jsonl` | Sessions, cycles, heartbeat | just recipes, PostToolUse |
| `governance-events.jsonl` | E2-108 cycle phases | governance_events.py |
| `pending-alerts.json` | Validation failures queue | validate.py |
| `validation.jsonl` | Template validation history | validate.py |

## 4. Session Number

Source: `docs/checkpoints/*.md` filenames → extract SESSION-(\d+) → latest = current

Formula for new session: `current_session + 1`

## 5. Key Recipes

```
just session-start N    # Log start event
just session-end N      # Log end event
just commit-session N T # Git commit checkpoint + work + status
just scaffold checkpoint N "title"
just ready              # Show unblocked work
```

## 6. Issues Found (2025-12-29)

1. **Session 145 no end** - Context crash at 94%, no checkpoint
2. **No auto session-start** - coldstart doesn't trigger it
3. **Late context warning** - 94% leaves no runway
4. **Milestone confusion** - Status vs checkpoint milestone differ (normal)
5. **No crash recovery** - Orphan sessions not detected

## 7. Recommendations

| Priority | Fix | Location |
|----------|-----|----------|
| P1 | Auto session-start in coldstart | coldstart.md |
| P2 | Warn at 85%, force at 90% | user_prompt_submit.py |
| P3 | Detect orphan sessions | status.py or coldstart |
| P4 | Multi-milestone display | haios-status-slim.json |

## 8. Database ERD (15 tables)

**Core:** artifacts, entities, concepts, entity_occurrences, concept_occurrences, processing_log, quality_metrics

**Retrieval:** embeddings, reasoning_traces (ReasoningBank)

**Knowledge:** memory_metadata, memory_relationships

**Synthesis:** synthesis_clusters, synthesis_cluster_members, synthesis_provenance

**Agent:** agent_registry, skill_registry

## 9. File Tree (Key Paths)

```
.claude/
├── .claude-plugin/plugin.json    # Plugin manifest
├── commands/ (18)                # Slash commands
├── config/                       # toggles, thresholds, bindings
├── hooks/hook_dispatcher.py      # Main router
├── lib/ (27 modules)             # All Python code
├── skills/ (15)                  # Cycle skills
├── agents/ (7)                   # Subagents
├── templates/ (9)                # Document templates
├── REFS/ (10)                    # Reference docs
├── mcp/, output-styles/          # MCP docs, persona
└── *.json, *.jsonl               # State files

docs/
├── checkpoints/                  # SESSION-N-*.md
├── work/active/, work/archive/   # WORK.md files
├── investigations/               # INVESTIGATION-*.md
└── specs/memory_db_schema_v3.sql # DB schema (authoritative)

haios_etl/                        # DEPRECATED → .claude/lib/
```

## 10. Memory Flow

```
coldstart → memory_search_with_experience(mode='session_recovery')
    ↓
strategies from reasoning_traces.strategy_*
    ↓
SESSION WORK
    ↓
checkpoint-cycle → ingester_ingest → concepts table
    ↓
memory_refs in checkpoint frontmatter
```

---
*~200 lines, ~2k tokens (vs ~1050 lines, ~15-20k tokens in full version)*
