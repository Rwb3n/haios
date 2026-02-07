# generated: 2025-12-29
# System Auto: last updated on: 2026-01-02T23:53:30
# INV-052: Architecture Redesign - Section Index

Generated: 2025-12-29 (Session 149)
Purpose: Index of deconstructed architecture sections

---

## Section Files

### Section 1: Hooks
- **SECTION-1A-HOOKS-CURRENT.md** - Current state (22 handlers, monolithic)
- **SECTION-1B-HOOKS-TARGET.md** - Target architecture (19 handlers, configurable)

### Section 2: Lifecycle
- **SECTION-2A-SESSION-LIFECYCLE.md** - Session as ephemeral ceremony
- **SECTION-2B-WORK-ITEM-LIFECYCLE.md** - Gated DAG, node_history, idempotency
- **SECTION-2C-WORK-ITEM-DIRECTORY.md** - Self-contained universe with portals
- **SECTION-2D-CYCLE-EXTENSIBILITY.md** - ~~Config-driven cycles~~ (SUPERSEDED by 2F)
- **SECTION-2E-CYCLE-SKILL-ANALYSIS.md** - Analysis of 7 cycles + orchestrator design
- **SECTION-2F-CYCLE-DEFINITIONS-SCHEMA.md** - Full schema + objective_complete gate

### Section 3: State
- **SECTION-3-STATE-STORAGE.md** - Consolidate state into WORK.md

### Section 4: Data Flow
- **SECTION-4-DATA-FLOW.md** - Single writer principle

### Section 5: Operational (Populated S151)
- **SECTION-5-SESSION-NUMBER-COMPUTATION.md** - Session number derivation from checkpoints
- **SECTION-6-CONFIGURATION-SURFACE.md** - All config files (9 files documented)
- **SECTION-7-JUSTFILE-RECIPES.md** - ~50 recipes in 9 categories
- **SECTION-8-MEMORY-INTEGRATION.md** - haios-memory MCP (13 tools)

### Section 6: Abstraction Paradigm (Populated S151)
- **SECTION-9-SLASH-COMMANDS.md** - 18 commands, chaining patterns
- **SECTION-10-SKILLS-TAXONOMY.md** - 15 skills (7 cycles, 3 bridges, 1 router, 4 utilities)
- **SECTION-11-SUBAGENTS.md** - 7 agents, tool matrices, isolation
- **SECTION-12-INVOCATION-PARADIGM.md** - 7-layer stack, flow examples, anti-patterns
- **SECTION-13-MCP-SERVERS.md** - 2 servers (haios-memory, context7), 15 tools

### Section 7: Bootstrap & Context (Populated S152)
- **SECTION-14-BOOTSTRAP-ARCHITECTURE.md** - L0-L3 context hierarchy, coldstart grounding
- **SECTION-15-INFORMATION-ARCHITECTURE.md** - Token budgets, loading priorities, context pressure
- **SECTION-16-SCAFFOLD-TEMPLATES.md** - Template system, governance flywheel

### Section 8: Modular Architecture (Created S153)
- **SECTION-17-MODULAR-ARCHITECTURE.md** - 5 black-box modules with I/O contracts (ADR-040)

### Section 9: Gap Resolution (S156)
- **SECTION-17.11-CONFIG-FILE-SCHEMAS.md** - 7 YAML config file schemas
- **SECTION-17.12-IMPLEMENTATION-SEQUENCE.md** - 5-phase build order, circular dependency resolution
- **SECTION-17.13-MIGRATION-PATH.md** - Migration steps for 4 boundary violations
- **SECTION-17.14-EVENT-SCHEMAS.md** - JSON Schema for 7 inter-module events
- **SECTION-17.15-ERROR-HANDLING.md** - Error types per module, recovery strategies
- **SECTION-18-PORTABLE-PLUGIN-SPEC.md** - manifest.yaml, LLM-agnostic plugin structure

### Supporting Documents
- **SECTION-2-LIFECYCLE-DIAGRAM.md** - 8 ASCII diagrams (visual summary)
- **SECTION-2G-CYCLE-EXTENSION-GUIDE.md** - How to add new cycles
- **SESSION-STATE-DIAGRAM.md** - Original monolithic audit (1079 lines, S148)
- **README.md** - Meta-context for continuing agents

---

## Key Decisions

| Decision | Choice | Session |
|----------|--------|---------|
| State ownership | Work item (WORK.md), not session | S149 |
| Crash recovery | Detect via `exited: null` in node_history | S149 |
| Extensibility | Config files (YAML), thin executors | S149 |
| Single writer | PostToolUse → WORK.md node_history | S149 |
| `design` node | Removed (vestigial, no cycle maps to it) | S150 |
| Routing rules | Embedded in ChainConfig, not separate file | S150 |
| objective_complete gate | Composite: deliverables + remaining_work + anti-pattern | S150 |
| Cycle orchestrator | Sits above phase executor, checks objective_complete before CHAIN | S150 |
| **Modular architecture** | 5 black-box modules with explicit I/O (ADR-040) | S153 |

---

## Remaining Work

- [x] **Section documentation** - 16 sections complete
- [x] **Gap analysis** - All sections have "Gaps Identified" tables
- [x] **Target architecture** - TARGET-ARCHITECTURE-DIAGRAM.md complete
- [ ] **Spawn implementation work items** - Create E2-* items from gap analysis

## Implementation Items to Spawn

From the gap analysis (TARGET-ARCHITECTURE-DIAGRAM.md Section 10):

| ID | Title | Priority | Source Gap |
|----|-------|----------|------------|
| E2-237 | Fix node-cycle-bindings.yaml cycle names | High | S6 |
| E2-238 | Implement memory_refs auto-linking | High | S8 |
| E2-239 | Create skill-manifest.yaml | Medium | S10 |
| E2-240 | Create agent-manifest.yaml | Medium | S11 |
| E2-241 | Create command-manifest.yaml | Medium | S9 |
| E2-242 | Create recipe-chains.yaml | Medium | S7 |
| E2-243 | Add session to node_history entries | Medium | S5 |
| E2-244 | Create cycle-definitions.yaml + executor | Medium | S8 |

**Note:** E2-234, E2-235, E2-236 already spawned in S150 for session recovery.

---

## Open Questions

1. node_history size limits
2. Atomic YAML updates
3. Migration from events.jsonl
4. Portal syntax (`[[ID]]` vs markdown)
5. Multi-agent locking
