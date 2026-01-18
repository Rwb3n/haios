# generated: 2026-01-06
# System Auto: last updated on: 2026-01-18T15:33:52
# Arc: Chariot

## Arc Definition

**Arc ID:** Chariot
**Epoch:** E2.2 (The Refinement)
**Name:** Module Architecture
**Status:** Active
**Pressure:** [volumous] - thematic exploration
**Memory Refs:** 81194-81198 (E2-279 decomposition), 81199-81210 (closure), 81351-81365 (S190 arc discussion)

---

## Theme

The 9 Chariot modules that make HAIOS portable and LLM-agnostic:

| Module | Breath | Function | Lines |
|--------|--------|----------|-------|
| ContextLoader | Inhale | Take in context (L0-L4) | ~300 |
| MemoryBridge | Inhale | Take in prior knowledge | ~450 |
| CycleRunner | Rhythm | Enforce inhale/exhale pattern | ~350 |
| GovernanceLayer | Exhale | Gates, verification, commitment | ~350 |
| WorkEngine | Exhale | Commit state to truth (core CRUD) | ~585 |
| CascadeEngine | Exhale | Completion cascade, unblock | ~387 |
| PortalManager | Exhale | REFS.md management | ~230 |
| SpawnTree | Exhale | Spawn tree traversal | ~170 |
| BackfillEngine | Exhale | Backlog content backfill | ~220 |

*E2-279 (Session 186): WorkEngine decomposed 1197→585 lines. 4 satellites extracted with lazy delegation.*

---

## REQUIRED READING

| Document | Why Required |
|----------|--------------|
| `../../EPOCH.md` | Epoch-level architecture |
| `../../architecture/S17-modular-architecture.md` | Module interfaces |
| `../../architecture/S20-pressure-dynamics.md` | Module ↔ breath mapping |
| `../../architecture/S25-sdk-path-to-autonomy.md` | Epoch 4 migration path (SDK enables hard enforcement) |

---

## Chapters

| Chapter | Name | Status | Purpose |
|---------|------|--------|---------|
| CH-001 | ModuleWiring | **Complete** | E2-279: WorkEngine delegates to satellites |
| CH-002 | BoundaryEnforcement | Planned | Enforce module boundaries (hooks?) |
| CH-003 | SDKMigration | Vision | Claude Agent SDK enables hard enforcement (S25, Epoch 4) |
| CH-004 | PathAuthority | Planned | Recipes own paths - agent doesn't hardcode (S190) - **INV-041 exists** |
| CH-005 | FileTypeLocking | Planned | PreToolUse enforces what file types go where (S190) |
| CH-006 | CycleDelegation | **Active** | INV-068: Subagents execute cycles, main track routes (S199) |
| CH-007 | APIDocumentation | Planned | Formalize module interfaces + data dictionary (S203, INV-069) |
| CH-008 | ToolDiscoverability | Planned | Audit, prune, organize, document recipes + commands for subagent containerization (S203) |

---

## Arc Completion Criteria

- [x] All 9 modules have runtime consumers (E2-279)
- [ ] Module boundaries enforced (no cross-boundary calls)
- [ ] Portable plugin structure works

---

---

## CH-007: API Documentation (Session 203)

**Problem:** Module interfaces and data schemas are scattered or implicit. S17 drift (INV-069) showed interface specs don't stay current. A "clueless shareholder" asking "where's the API reference?" has no good answer.

**What Exists (Scattered):**
| Artifact | Location | Coverage |
|----------|----------|----------|
| DB Schema | `docs/specs/memory_db_schema_v3.sql` | Complete - 17 tables |
| Module Interfaces | S17 (stale), `L4-implementation.md` | Partial, drifted |
| Config Schema | `haios.yaml`, `cycles.yaml` | Implicit - no formal schema |
| Work Item Schema | Template + frontmatter | Implicit in templates |
| Cycle/Phase Contracts | Skills markdown | Prose, not formal |

**What's Missing:**
1. **Module API Reference**: Function signatures for 9 modules
2. **Data Dictionary**: Field definitions (current_node, memory_refs, spawned_by, etc.)
3. **Config Schema**: Valid values for haios.yaml
4. **Event Contracts**: What events flow between modules

**Recommended Approach (Hybrid):**
- **Data Dictionary** → New architecture file (stable, rarely changes)
- **Module Interfaces** → Auto-generate from code docstrings/type hints
- **Config Schema** → YAML schema file with runtime validation

**Depends On:** E2-301 (S17 revision) - fix stale interfaces first, then formalize

**Memory Refs:** 81482-81495 (INV-069 findings)

**Session 205 Observations (triaged from E2-301, E2-302, E2-303):**
- Gap: No automated staleness detection for architecture docs (E2-302)
- Gap: No spec-implementation diff tool - manually comparing S17 to code required reading both files (E2-301)
- Pattern: "Documentation drift from vision divergence" - Session 150's future work evolved differently, diagrams showed files that never existed (E2-302, E2-303)

---

## CH-008: Tool Discoverability (Session 203)

**Problem:** Recipes and commands are the agent's "hands" - execution machinery. For subagent containerization (INV-068, Epoch 4), spawned agents need to discover what tools exist, when to use them, and what they do. Current state is sprawling and undocumented.

**Current State:**

| Component | Count | Discoverability | Documentation |
|-----------|-------|-----------------|---------------|
| Just recipes | 70+ | `just --list` (flat dump) | None - must read Justfile |
| Slash commands | ~15 | `/help` (basic list) | Inline in markdown |
| MCP tools | 13 | MCP spec | Good - in haios-memory |

**Problems:**
1. **Sprawl**: 70+ recipes accumulated organically, no categorization
2. **Dead code**: Unknown how many recipes are actually used
3. **No help**: `just <recipe>` gives no usage info
4. **Command sprawl**: Commands added without organization
5. **Subagent blind**: Spawned agent can't efficiently discover available tools
6. **Naming confusion**: Template types don't match intuitive names (e.g., `work` rejected, must use `work_item`) - S205 observation from E2-303

### Phase 1: Audit & Prune

**Recipes:**
| Action | Criteria | Method |
|--------|----------|--------|
| **Identify dead** | No callers in skills/hooks/commands | Grep for recipe names |
| **Identify duplicates** | Same function, different names | Manual review |
| **Delete unused** | Dead + no obvious future use | Remove from Justfile |
| **Deprecate carefully** | Dead but might be needed | Move to `just.archive` section |

**Commands:**
| Action | Criteria | Method |
|--------|----------|--------|
| **Identify dead** | No usage in 30+ sessions | Check checkpoint history |
| **Consolidate overlapping** | Similar function | Merge or alias |
| **Remove stale** | References deprecated features | Delete |

### Phase 2: Organize

**Recipe Categories:**
```just
# === SESSION LIFECYCLE ===
session-start, session-end, coldstart-hook

# === WORK ITEM MANAGEMENT ===
work, close-work, cascade, ready, queue

# === CYCLE CONTROL ===
set-cycle, clear-cycle, set-queue

# === SCAFFOLDING ===
scaffold, scaffold-observations, new-investigation

# === STATUS & OBSERVABILITY ===
update-status, update-status-slim, events, health

# === DEVELOPMENT ===
test, lint, format
```

**Command Categories:**
```
# Lifecycle: /coldstart, /new-checkpoint
# Work: /new-work, /new-plan, /new-investigation, /close, /implement
# Utility: /status, /workspace, /validate, /schema
# System: /haios, /audit
```

### Phase 3: Document

**Recipe Documentation:**
```just
# Close a work item (updates status, runs cascade, refreshes status)
# Usage: just close-work <id>
# Example: just close-work E2-301
close-work id:
    python .claude/haios/modules/cli.py close {{id}}
    just cascade {{id}} complete
    just update-status
```

**Command Index** (machine-readable):
```yaml
# .claude/commands/index.yaml
commands:
  coldstart:
    purpose: Initialize session
    arguments: none
    chains_to: survey-cycle
  close:
    purpose: Close work item with DoD validation
    arguments: <backlog_id>
    chains_to: observation-capture-cycle, close-work-cycle
```

### Phase 4: Discoverability API

**For agents:**
```bash
just help <recipe>          # Show recipe documentation
just discover <category>    # List recipes in category
just discover --all         # Categorized overview
```

**For subagents (containerization prep):**
```yaml
# .claude/haios/config/tool-manifest.yaml
# What tools a subagent can access
subagent_tools:
  investigation-agent:
    recipes: [set-cycle, clear-cycle]
    commands: []
    mcp_tools: [memory_search_with_experience]
  validation-agent:
    recipes: [test]
    commands: []
    mcp_tools: [db_query]
```

### Deliverables

- [ ] Recipe audit complete (count dead, duplicates, active)
- [ ] Dead recipes removed or archived
- [ ] Justfile organized by category with section headers
- [ ] Recipe docstrings added (usage, example)
- [ ] Command index created (machine-readable)
- [ ] `just help <recipe>` works
- [ ] `just discover` works
- [ ] Subagent tool manifest drafted

**Depends On:**
- INV-068 (Cycle Delegation) - defines what subagents need
- CH-007 (API Documentation) - same pattern, different layer

**Enables:**
- Epoch 4 subagent containerization
- Cleaner agent onboarding
- Reduced "what recipe does X?" questions

**Priority:** Medium - blocks efficient subagent work

**Memory Refs:** 81496-81503 (S203 architecture recommendations)

---

## References

- S17: Modular Architecture
- S20: Pressure Dynamics (breath mapping)
- S25: SDK Path to Autonomy (Epoch 4 migration)
- E2-279: WorkEngine Decomposition (Session 185-186)
- E2-293: session_state schema extension (active_queue, phase_history)
- E2-301: S17 Revision (spawned by INV-069, prerequisite for CH-007)
- INV-065: Session State Cascade Architecture (Session 194)
- INV-062: Session State Tracking (enforcement gaps)
- INV-068: Cycle Delegation Architecture (Session 199)
- INV-069: Architecture File Consistency Audit (Session 203) - spawned CH-007
- Memory 81194-81210: Decomposition learnings
- Memory 81309-81324: SDK discovery
- Memory 81433-81435: Session boundary pattern (S199)
- Memory 81482-81495: INV-069 audit findings
