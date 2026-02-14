---
generated: 2026-02-14
session: 365
purpose: Full system archaeological audit for E2.6 epoch planning
type: audit
---
# HAIOS System Audit - Session 365

Full inventory of all building blocks, contracts, and infrastructure.

---

## 1. Skills (34 total)

| Skill | Stub | Category | Description |
|-------|------|----------|-------------|
| arc-review | YES | Ceremony/Feedback | Review arc direction after chapter completion |
| audit | no | Utility | Run all HAIOS audit checks |
| chapter-review | YES | Ceremony/Feedback | Review chapter scope after work completion |
| checkpoint-cycle | no | Ceremony/Session | Create checkpoint manifest |
| close-arc-ceremony | no | Ceremony/Closure | Verify arc DoD |
| close-chapter-ceremony | no | Ceremony/Closure | Verify chapter DoD |
| close-epoch-ceremony | no | Ceremony/Closure | Verify epoch DoD |
| close-work-cycle | no | Ceremony/Closure | Structured work item closure (VALIDATE->ARCHIVE->CHAIN) |
| design-review-validation | no | Lifecycle | Verify implementation alignment during DO phase |
| dod-validation-cycle | no | Lifecycle | Validate Definition of Done before closure |
| epoch-review | YES | Ceremony/Feedback | Review epoch goals after arc completion |
| extract-content | no | Utility | Extract entities/concepts via memory system |
| ground-cycle | no | Lifecycle | Load architectural context before cognitive work |
| implementation-cycle | no | Lifecycle | Structured implementation (PLAN->DO->CHECK->DONE) |
| investigation-cycle | no | Lifecycle | Structured research (EXPLORE->HYPOTHESIZE->VALIDATE->CONCLUDE) |
| memory-agent | no | Utility | Context retrieval and learning storage |
| memory-commit-ceremony | no | Ceremony/Memory | Store learnings with provenance |
| observation-capture-cycle | DEPRECATED | Ceremony/Memory | Replaced by retro-cycle (WORK-142) |
| observation-triage-cycle | no | Ceremony/Memory | Process captured observations (SCAN->TRIAGE->PROMOTE) |
| plan-authoring-cycle | no | Lifecycle | Structured plan population (AMBIGUITY->ANALYZE->AUTHOR->VALIDATE) |
| plan-validation-cycle | no | Lifecycle | Validate plan readiness (CHECK->VALIDATE->APPROVE) |
| queue-commit | no | Ceremony/Queue | Move ready to working |
| queue-intake | no | Ceremony/Queue | Create new work item at backlog |
| queue-prioritize | no | Ceremony/Queue | Move backlog to ready |
| queue-unpark | no | Ceremony/Queue | Move between parked and backlog |
| requirements-review | YES | Ceremony/Feedback | Review L4 requirements after epoch completion |
| retro-cycle | no | Ceremony/Memory | Typed reflection (REFLECT->DERIVE->EXTRACT->COMMIT) |
| routing-gate | no | Utility | Work-type routing in CHAIN phase |
| schema-ref | no | Utility | Database schema reference |
| session-end-ceremony | no | Ceremony/Session | Finalize session with orphan check |
| session-start-ceremony | no | Ceremony/Session | Initialize session with context loading |
| spawn-work-ceremony | no | Ceremony/Spawn | Create linked work item |
| survey-cycle | no | Lifecycle | Session-level work selection (GATHER->ASSESS->OPTIONS->CHOOSE->ROUTE) |
| work-creation-cycle | no | Ceremony/Queue | Structured work item population (VERIFY->POPULATE->READY) |

**Summary:** 30 active, 4 stubs (all feedback ceremonies), 1 deprecated.
**By category:** 20 ceremonies, 8 lifecycles, 6 utilities.

---

## 2. Agents (11 total)

| Agent | Model | Required? | Purpose | Context |
|-------|-------|-----------|---------|---------|
| anti-pattern-checker | sonnet | SHOULD | Verify claims against 6 L1 anti-patterns | Default |
| close-work-cycle-agent | sonnet | Optional | Execute close-work-cycle autonomously | Fork |
| critique-agent | opus | Optional | Pre-implementation assumption surfacing | Default |
| implementation-cycle-agent | sonnet | Optional | Full implementation cycle in isolated context | Fork |
| investigation-agent | opus | Required (EXPLORE) | Phase-aware research with memory queries | Default |
| investigation-cycle-agent | sonnet | Optional | Full investigation cycle in isolated context | Fork |
| preflight-checker | haiku | REQUIRED | Validate plan readiness before DO phase | Default |
| schema-verifier | haiku | REQUIRED | Verify schema and run read-only SQL | Default |
| test-runner | haiku | Recommended | Execute pytest in isolated context | Default |
| validation-agent | sonnet | Recommended | Unbiased CHECK phase validation | Default |
| why-capturer | haiku | Recommended | Extract learnings during DONE phase (ADR-033) | Default |

**Patterns:**
- 3 "fork" agents (cycle delegation, context reduction per WORK-081)
- 2 REQUIRED gates (preflight, schema)
- 3 haiku agents (cost-efficient for simple tasks)
- 2 opus agents (deep reasoning: critique, investigation)

---

## 3. Templates (37 total)

### Root-level structured templates (10)

| Template | Variables | Purpose |
|----------|-----------|---------|
| work_item.md | BACKLOG_ID, TITLE, TYPE, DATE, SPAWNED_BY, TIMESTAMP, SESSION | Work item scaffold |
| checkpoint.md | SESSION, PREV_SESSION, DATE | Session checkpoint |
| skill.md | SKILL_NAME, DESCRIPTION, DATE | Skill definition |
| architecture_decision_record.md | DATE, ID, TITLE, AUTHOR, SESSION | ADR |
| report.md | DATE, TITLE, AUTHOR, SESSION | Report/analysis |
| observations.md | BACKLOG_ID, SESSION, DATE, TIMESTAMP | Observation capture |
| investigation.md | DATE, BACKLOG_ID, TITLE, SESSION | DEPRECATED monolithic |
| handoff_investigation.md | DATE, TITLE | DEPRECATED (ADR-034) |
| arc.md | DATE, NAME, ID, EPOCH | Arc definition |
| chapter.md | DATE, NAME, ID, ARC | Chapter definition |

### Fractured phase templates (20 = 5 lifecycles x 4 phases)

| Lifecycle | Phases | State Mappings |
|-----------|--------|----------------|
| investigation/ | EXPLORE, HYPOTHESIZE, VALIDATE, CONCLUDE | EXPLORE->EXPLORE, HYPOTHESIZE->DESIGN, VALIDATE->CHECK, CONCLUDE->DONE |
| design/ | EXPLORE, SPECIFY, CRITIQUE, COMPLETE | EXPLORE->EXPLORE, SPECIFY->DESIGN, CRITIQUE->CHECK, COMPLETE->DONE |
| implementation/ | PLAN, DO, CHECK, DONE | Direct mapping |
| validation/ | VERIFY, JUDGE, REPORT | All map to CHECK |
| triage/ | SCAN, ASSESS, RANK, COMMIT | SCAN->EXPLORE, ASSESS->EXPLORE, RANK->DESIGN, COMMIT->DONE |

### Other (7)
- 5 README index files (one per lifecycle)
- 1 legacy template: `_legacy/implementation_plan.md` (still used as fallback)
- 1 ceremony template: `ceremony/SKILL.md` (uses `{var}` not `{{var}}`)

---

## 4. Recipes (71 total)

| Category | Count | Key Recipes |
|----------|-------|-------------|
| Governance | 26 | validate, scaffold, plan, inv, adr, work, checkpoint, node, link, close-work, update-status, cascade, backfill |
| ETL | 11 | status, synthesis, process, ingest, embeddings, migrate-backlog |
| Loaders | 9 | identity, coldstart, session-context, work-options, coldstart-orchestrator, memory-query, context-load, cycle-phases, pipeline-run |
| Rhythm | 12 | heartbeat, events, session-start, session-end, set-cycle, get-cycle, clear-cycle, set-queue |
| Plan Tree | 12 | tree, ready, queue, queue-next, queue-check, queue-prioritize, queue-commit, queue-unpark, queue-park, spawns |
| Utility | 4 | git-status, git-log, health, checkpoint-latest |
| Git Commit | 4 | commit-session, commit-close, stage-governance, chapter-status |
| Audit | 4 | audit-sync, audit-gaps, audit-stale, audit-decision-coverage |

---

## 5. Hooks (4 event hooks + 2 helpers)

| Hook | Event | Purpose |
|------|-------|---------|
| pre_tool_use.py | PreToolUse | SQL blocking, PowerShell blocking, scaffold guard, path governance, plan validation, memory refs warning, backlog ID uniqueness, exit gates |
| post_tool_use.py | PostToolUse | Error capture, memory auto-link, timestamp injection, template validation, artifact refresh, cycle transition logging, investigation sync, scaffold suggestions |
| stop.py | Stop | Extract learnings via MemoryBridge for ReasoningBank |
| user_prompt_submit.py | UserPromptSubmit | Date/time injection, session state warning, lifecycle guidance, RFC2119 reminders |
| memory_retrieval.py | Helper | Embedding generation, memory search, TOON formatting |
| reasoning_extraction.py | Helper | Transcript parsing, learning extraction, strategy storage |

---

## 6. Commands (19 total)

| Command | Purpose |
|---------|---------|
| /coldstart | Initialize session (config->orchestrator->epoch->survey) |
| /new-work | Create work item with auto-incremented ID |
| /new-investigation | Create investigation document |
| /new-plan | Create implementation plan |
| /new-checkpoint | Create session checkpoint |
| /new-adr | Create Architecture Decision Record |
| /new-handoff | Create handoff document |
| /new-report | Create report document |
| /implement | Start PLAN-DO-CHECK-DONE cycle |
| /close | Close work item with DoD validation |
| /status | System health dashboard |
| /ready | List unblocked work items |
| /workspace | Operational status |
| /tree | Milestone progress tree |
| /validate | Validate markdown against templates |
| /reason | Inject Critical Reasoning Framework |
| /critique | Invoke critique agent on artifact |
| /schema | Quick database schema lookup |
| /haios | Full HAIOS system status dashboard |

---

## 7. Python Code (45 files, 16,724 lines)

### modules/ (16 files, 6,448 lines) — Chariot Architecture

| Module | Lines | Role |
|--------|-------|------|
| cli.py | 763 | CLI entry point (16 commands) |
| work_engine.py | 1,167 | Core work item state machine (20+ methods) |
| governance_layer.py | 707 | Gate enforcement, ceremony context |
| cycle_runner.py | 621 | Phase gate validator, lifecycle outputs |
| memory_bridge.py | 486 | MCP wrapper for memory operations |
| requirement_extractor.py | 395 | L4 requirement parsing |
| cascade_engine.py | 387 | Status cascade (E2-279 extraction) |
| planner_agent.py | 364 | Work grouping and dependency estimation |
| context_loader.py | 319 | Config-driven context loading |
| portal_manager.py | 258 | Portal/link operations |
| backfill_engine.py | 228 | Backlog-to-work migration |
| pipeline_orchestrator.py | 214 | Doc-to-product pipeline |
| corpus_loader.py | 182 | Document corpus discovery |
| spawn_tree.py | 170 | Spawn relationship visualization |
| ceremony_runner.py | 141 | Ceremony phase dispatch |
| __init__.py | 46 | Re-exports |

### lib/ (29 files, 10,276 lines) — Utilities & Cross-cutting

| Module | Lines | Role |
|--------|-------|------|
| status.py | 1,244 | Status generation (largest file) |
| observations.py | 841 | Observation triage + retro queries |
| validate.py | 777 | DoD validation chains |
| cascade.py | 600 | LEGACY cascade (superseded by modules/) |
| scaffold.py | 538 | Template scaffolding, work creation |
| loader.py | 487 | Node-cycle bindings, exit criteria |
| ceremony_contracts.py | 472 | Contract validation, registry |
| cli.py | 469 | ETL CLI entry point |
| dod_validation.py | 449 | DoD parsing helpers |
| audit_decision_coverage.py | 385 | Decision traceability validation |
| governance_events.py | 370 | Event logging (JSONL) |
| node_cycle.py | 300 | Node-cycle detection |
| backfill.py | 276 | LEGACY backfill |
| work_item.py | 253 | Work item data structures |
| audit.py | 257 | Sync/gap/stale audits |
| spawn_ceremonies.py | 233 | Spawn execution |
| session_loader.py | 225 | Session context from checkpoint |
| work_loader.py | 242 | Work options for coldstart |
| spawn.py | 192 | LEGACY spawn tree |
| dependencies.py | 191 | Skill/agent ref extraction |
| error_capture.py | 188 | Error classification & storage |
| queue_ceremonies.py | 159 | Queue transition logging |
| coldstart_orchestrator.py | 154 | Loader sequencing |
| config.py | 124 | Path constants, ConfigLoader |
| identity_loader.py | 106 | Manifesto extraction |
| routing.py | 82 | Work-type routing |
| __init__.py | 31 | Re-exports |
| errors.py | 15 | Exception definitions |
| database.py | 616 | Database management |

### Legacy/Orphaned (3 files in lib/)
- `cascade.py` — superseded by modules/cascade_engine.py
- `spawn.py` — superseded by modules/spawn_tree.py
- `backfill.py` — superseded by modules/backfill_engine.py

---

## 8. Work Items (128 total)

| Metric | Count |
|--------|-------|
| Total active | 120 |
| Total archived | 8 |
| Complete | 106 (88%) |
| Active (open) | 9 |
| Blocked | 2 |
| Backlog | 3 |

### Open Work Items (14 — 9 active + 2 blocked + 3 backlog)

| ID | Title | Type | Priority | Arc |
|----|-------|------|----------|-----|
| WORK-020 | Discoverability Architecture | investigation | medium | portability |
| WORK-034 | Upstream Status Propagation | implementation | medium | ceremonies |
| WORK-067 | Portable Schema Architecture | investigation | high | portability |
| WORK-071 | Pre-Decomposition Review Gate | design | medium | feedback |
| WORK-075 | System Audit as L4 Traceability | implementation | medium | feedback |
| WORK-082 | Epistemic Review Ceremony | investigation | medium | feedback |
| WORK-093 | Implement Lifecycle Asset Types | feature | high | assets |
| WORK-096 | Agent UX Test in DoD Validation | implementation | low | ceremonies |
| WORK-097 | Plan Decomposition Traceability | implementation | medium | lifecycles |
| WORK-101 | Proportional Governance Design | design | medium | lifecycles (BLOCKED) |
| WORK-102 | Session/Process Review Ceremonies | design | medium | feedback (BLOCKED) |
| WORK-104 | Validation/Triage Cycle Mappings | feature | low | lifecycles |
| WORK-135 | Manifest Auto-Sync | implementation | low | portability |
| WORK-136 | Checkpoint Pending Staleness | investigation | low | ceremonies |

### Known Issue
97% of items stuck at `current_node=backlog` despite `status=complete`. WorkEngine.transition() not called by lifecycle cycles. (WORK-016, WORK-023)

---

## 9. Structural Summary

### What We Have (Building Blocks)

```
Building Blocks:
  Skills (34)     — Markdown prompts, injected into agent context
  Agents (11)     — Isolated context windows with tool subsets
  Recipes (71)    — Just commands as CLI entrypoints
  Templates (37)  — Scaffolds for contracts (WORK.md, PLAN.md, etc.)
  Hooks (4+2)     — Event-driven governance enforcement
  Commands (19)   — User-facing slash commands
  Python (45)     — modules/ (engines) + lib/ (utilities)
```

### Framework Hierarchy (designed E2.4, partially implemented E2.5)

```
Principles (L3)
  -> Ways of Working (ceremonies, lifecycles)
    -> Ceremonies (20 defined, ~16 implemented as skills)
      -> Activities (lifecycle phases: EXPLORE, PLAN, DO, CHECK, DONE)
        -> Assets (work items, plans, investigations, checkpoints, ADRs)
```

### Contracts (Information Architecture)

```
Contracts (template instances that transmit context):
  WORK.md       — Work item definition, frontmatter-heavy
  PLAN.md       — Implementation plan, prose-heavy
  INV.md        — Investigation findings
  checkpoint.md — Session state snapshot for cross-session continuity
  ARC.md        — Arc definition and scope
  EPOCH.md      — Epoch goals and exit criteria
```

### Infrastructure Hierarchy

```
Epoch -> Arc -> Chapter -> Work Item
  (hierarchy currently in filesystem, proposed: metadata)
```

---

## 10. Observations & Hidden Nuggets

### Duplication Found
1. **3 legacy lib/ files** (cascade, spawn, backfill) duplicated in modules/ — cleanup candidates
2. **2 CLI files** (modules/cli.py + lib/cli.py) — different purposes but naming collision
3. **observation-capture-cycle** deprecated but still present

### Asymmetries Found
1. **4 feedback ceremony stubs** (arc-review, chapter-review, epoch-review, requirements-review) — all stubs, never implemented
2. **Ceremony template** uses `{var}` syntax while everything else uses `{{var}}`
3. **Only critique-agent** has config in haios.yaml — other 10 agents are self-contained markdown

### Scale Observations
1. **71 recipes** is a large surface area — many are aliases or wrappers
2. **10,276 lines in lib/** vs **6,448 in modules/** — lib is 60% larger despite being "utilities"
3. **status.py at 1,244 lines** is the largest single file — status generation is complex
4. **19 commands** but agents mostly interact via skills, not commands

### Architecture Insights
1. **Module-first principle** (CLAUDE.md) says commands->cli->modules->lib, but many recipes call lib/ directly via Python scripts
2. **ConfigLoader** is the canonical path resolver but only 3 modules use it
3. **GovernanceLayer** is the most imported module — gate enforcement touches everything
4. **CycleRunner** and **CeremonyRunner** exist side-by-side — the relationship isn't clear
5. **Memory system** has 85k+ concepts but retrieval is ad-hoc (no structured query patterns)

### Potential E2.6 Targets
1. **Proportional governance** — the 40% overhead comes from skills being monolithic markdown injections
2. **Flat metadata** — arc.md and chapter.md templates exist but aren't used yet (arcs still in filesystem hierarchy)
3. **Recipe rationalization** — 71 recipes could be grouped/composed differently
4. **Legacy cleanup** — 3 orphaned lib/ files, 1 deprecated skill, 2 deprecated templates
5. **Contract redesign** — WORK.md frontmatter has 30+ fields; could be layered for progressive disclosure

---

## 11. haios_etl/ — The Memory Engine (DEPRECATED but operational)

The MCP server powering `haios-memory`. Officially deprecated (Session 92) but still the running code.

| Module | Lines | Purpose |
|--------|-------|---------|
| mcp_server.py | 13,064 | FastMCP server exposing 13 tools |
| synthesis.py | 35,218 | 5-stage memory consolidation (CLUSTER->SYNTHESIZE->STORE->CROSS-POLLINATE->PRUNE) |
| database.py | 26,492 | SQLite + WAL + sqlite-vec vector storage |
| extraction.py | 19,462 | LLM-based entity/concept extraction (Gemini) |
| cli.py | 17,217 | ETL CLI |
| retrieval.py | 12,929 | Vector search + ReasoningBank experience learning |
| health_checks.py | 8,517 | DB health, memory monitoring |
| refinement.py | 6,736 | Greek Triad classification (episteme/techne/doxa) |
| job_registry.py | 6,984 | Job tracking |
| processing.py | 6,507 | BatchProcessor with idempotency (SHA256) |
| quality.py | 444 | Quality metrics |
| agents/ | — | interpreter.py, ingester.py, collaboration.py |
| migrations/ | — | 9 schema migrations |
| preprocessors/ | — | GeminiDumpPreprocessor |

**Relationship to .claude/haios/lib/:** Migration was planned but lib/ imports FROM haios_etl. The "deprecated" package is still the actual runtime.

**Key insight:** 85k+ concepts, but Greek Triad taxonomy is dead (0 doxa, 14 episteme — all old). Auto-classifier diverged from original design.

---

## 12. epoch3/ — Cognitive Memory Vision (Specification Only)

**Vision:** Unified cognitive memory with three paradigms.

| Paradigm | Inspiration | Purpose |
|----------|-------------|---------|
| Declarative | HINDSIGHT paper | Facts, beliefs, entities, experiences with confidence |
| Procedural | ReasoningBank paper | Strategies, skills, failure lessons |
| Predictive | FORESIGHT (novel) | World models, self-models, goal networks, metamemory |

**Key documents:** foresight-spec.md, unified-memory.md, three-paradigm-model.md, reasoningbank-analysis.md, integration-patterns.md, v1.1-enhancements.md

**Status:** Complete specifications, NOT implemented. Contains a 448MB ChatGPT data export zip.

**Gems:**
- Bayesian Competence Calibration (Beta distributions for self-model)
- Metamemory / Feeling-of-Knowing as first-class retrieval confidence
- Failure learning as core signal (not just success patterns)
- Strategy Compressor (DBSCAN clustering + LLM abstraction)

---

## 13. epoch4_vision/ — The Philosophical Foundation (12 documents)

**Vision:** Ground-up redesign where "agents all the way down" and filesystem is the only persistent memory.

**5 First Principles:**
1. Agents are stateless
2. Files are the only memory
3. Every file is written for an LLM to read
4. Agents only write to their own outbox
5. Parents invoke children by writing to their inbox

**Architecture layers:** Substrate -> Runtime -> Agents -> Utilities -> Cycles -> Lifecycle -> Errors -> Operator

**Status:** Stub corpus — 12 outline documents, no implementation.

**Gems:**
- "Nursery, not factory" — agents are becoming, not tools
- Operator as Agent — same inbox/outbox protocol, no privileged pathways
- Graceful autonomy scaling — success = operator becomes unnecessary
- Honesty incentivized by design (all state visible in files)
- Inward cycles (Introspect -> Meta-evaluate -> Adapt) alongside outward cycles

---

## 14. HAIOS-RAW/ — The Archaeological Layer (515 files)

The original HAIOS framework from Jun-Oct 2025 (Epoch 1 & early Epoch 2).

| Directory | Files | Contents |
|-----------|-------|----------|
| docs/ | 241 | 23 schemas, 9 TRDs, 132 Cody Reports (Epoch 1), 16 3rd-party evals, APIP proposal |
| fleet/ | 121 | Agent implementations: 2a_agent (multi-node), rhiza_agent (advanced with DB/adapters), A1/A2/scribe |
| system/ | 138 | 57 ADRs (ADR-OS-000 through 057), personas, linters, ETL research |
| templates/ | 12 | Template system (ADR, checkpoint, plan, report, verification, directive, proposal, backlog) |

**Key artifacts:**
- 57 Architecture Decision Records (the "canon")
- 132 Cody Reports (genesis architect checkpoint reports)
- Full schema documentation (state, request, issue, exec_plan, config)
- Agent implementations with node-based architecture
- ETL research findings (MCP, vector DBs, knowledge graphs, sqlite-vec)

---

## 15. docs/ — Full Documentation Tree (300+ files)

| Subdirectory | Files | Contents |
|--------------|-------|----------|
| ADR/ | 15 | ADR-030 through ADR-044 (current epoch decisions) |
| anti-patterns/ | 2 | AP-STALE-FOOTER (1 active anti-pattern) |
| archive/ | ~50 | Sessions 2-17 checkpoints, resolved handoffs |
| checkpoints/ | 20 | Sessions 340-363 (recent) |
| handoff/ | 21 | Context transfer documents |
| investigations/ | 44 | INV-008 to INV-044, E2-series investigations |
| libraries/ | 14 | langextract, sqlite-vec, LightRAG, NetworkX, TOON, ReasoningBank paper, 7 research docs |
| notes/ | 1 | Future memory migration note |
| plans/ | 109 | EPOCH2 plans (8), E2-series (60+), ADR impl (6), agent/infra (7), synthesis (5), file lifecycle (3) |
| pm_archive/ | 5 | Historical backlog, milestones |
| reports/ | 18 | Evaluations, investigations, audits, strategic docs |
| risks-decisions/ | 4 | RD-001 to RD-004 (LLM non-determinism, rate limits, processing time, SQLite) |
| samples/ | 0 | Empty |
| specs/ | 15 | TRDs (ETL v1/v2, refinement, synthesis, validation, work-item), DB schemas (v2/v3), agent specs |
| vision/ | 2 | Canonical vision interpretation session |
| walkthroughs/ | 2 | Agent ecosystem MVP walkthrough |
| work/ | 128 | Active work items (120) + legacy archive (8) |

**Root docs:**
- COGNITIVE_MEMORY_SYSTEM_SPEC.md (60KB, ~85% implemented)
- CONSTRAINTS_AND_MITIGATIONS.md (46KB, 13 constraint categories)
- VISION_ANCHOR.md (8KB, LangExtract + ReasoningBank foundation)
- OPERATIONS.md (8KB, ETL operations manual)
- MCP_INTEGRATION.md (8KB, 8 MCP tools guide)

---

## 16. .claude/ — Full Plugin Structure

### Root files
| File | Size | Purpose |
|------|------|---------|
| session | — | Current session number |
| haios-status.json | 276KB | Full system status |
| haios-status-slim.json | 3.4KB | Slim status for context injection |
| haios-events.jsonl | 83KB | Governance event log |
| validation.jsonl | 212KB | Validation outcomes |
| pending-alerts.json | — | Alert queue |
| settings.json | — | Base settings |
| settings.local.json | — | Local overrides |

### Manifesto hierarchy (L0-L4)
```
manifesto/
  L0-telos.md           — Ultimate purpose/end state
  L1-principal.md       — Principal principles (constraints)
  L2-intent.md          — Intent statements
  L3-requirements.md    — Requirements
  L4/
    functional_requirements.md    — REQ-LIFECYCLE, REQ-QUEUE, REQ-CEREMONY, REQ-FEEDBACK
    technical_requirements.md     — Architecture specs
    agent_user_requirements.md    — Agent & user requirements
    project_requirements.md       — Project requirements
```

### Config files (16 in .claude/haios/config/)
- haios.yaml (main), activity_matrix.yaml, ceremony_registry.yaml, coldstart.yaml
- components.yaml, cycles.yaml, work_queues.yaml
- corpus/haios-requirements.yaml
- critique_frameworks/assumption_surfacing.yaml
- loaders/ (identity, session, work configs)

### Top-level config (7 in .claude/config/)
- governance-toggles.yaml, invariants.md, node-cycle-bindings.yaml
- north-star.md, roadmap.md, routing-thresholds.yaml

### Epoch history (6 epochs, 185 files)
```
E2     — Foundation (skills paradigm, bootstrap)
E2_3   — Configuration & Migration (46 observations)
E2_4   — Activities & Flow (breath model)
E2_5   — Lifecycles & Ceremonies (27 chapters across 5 arcs) — COMPLETE
E2_6   — Agent UX (planning)
E3     — Future (2 observations)
```

### Other .claude/ directories
- REFS/ (11 reference docs: commands, hooks, MCP, SDK, skills, subagents, troubleshooting)
- logs/ (error_capture, memory_retrieval, reasoning_extraction)
- output-styles/ (agent output formatting)
- tools/ (tool definitions)

---

## 17. Root-level Loose Files

### Proposals (7 files)
- PROPOSAL-MEMVID-EPOCH3.md (+ 5 copies) — Unified memory substrate vision
- stale_APIP-PROPOSAL.md — Agent Project Interface Protocol (v0.1 draft)

### Deprecated guides (3 files)
- deprecated_ADMIN.md, deprecated_AGENT.md, deprecated_GEMINI.md — superseded by CLAUDE.md

### Plan samples (2 files)
- plan-sample.md — WORK-142 retro-cycle plan (480 lines, layered methodology)
- plan-sample-2.md — E2.5 arc decomposition (27 chapters)

### Reference material (3 files)
- skills-claude-blog-2.txt, skills-claude-code-blog.txt, skills-subagents-blog-post.txt — Anthropic blog posts on skills architecture

### Utilities (6 files)
- requirements.txt (langextract, PyYAML, pytest, mcp, etc.)
- check_schema.py (11-line schema check)
- repomix-output.xml, repomix-output-2.xml (full codebase export for AI analysis)
- test_output.txt, test_results.txt

### Database (4 files)
- haios_memory.db (active), .db-shm, .db-wal (WAL journal)
- haios_memory.db.backup.20251130, .pre-synthesis-2025-12-21 (backups)

### Scripts (46 files in scripts/)
- 26 root scripts (migrations, verification, embeddings, investigations)
- 8 dev scripts (debugging from early sessions)
- 1 migration script
- 3 verification scripts

---

## 18. Tests (96 test files, ~750KB)

Largest test files:
- test_work_engine.py (77KB) — comprehensive state machine tests
- test_synthesis.py (52KB) — memory consolidation pipeline
- test_lib_scaffold.py (37KB) — template scaffolding
- test_hooks.py (31KB) — governance hook testing
- test_lib_validate.py (31KB) — DoD validation
- test_lib_status.py (24KB) — status generation

Test infrastructure:
- conftest.py with `_load_module_once()` (S351 WORK-117)
- helpers.py with test utilities
- fixtures/ directory
- 1296 passed, 18 failed, 4 skipped (as of S351)

---

## 19. Full System Scale

| Dimension | Count |
|-----------|-------|
| **Total files (estimated)** | 1,500+ |
| **Python code** | ~200 files, ~50,000+ lines |
| **Markdown documents** | ~800+ files |
| **YAML configs** | ~25 files |
| **Epochs traversed** | 6 (E2 through E3) |
| **Work items created** | 143 |
| **ADRs (current)** | 15 (ADR-030 to ADR-044) |
| **ADRs (historical/RAW)** | 57 (ADR-OS-000 to ADR-OS-057) |
| **Memory concepts** | 85,000+ |
| **Sessions** | 365 |
| **Test cases** | ~1,300 |
| **Observations** | 63+ across 4 epochs |
| **Plans** | 109 |
| **Investigations** | 44 |

---

## 20. Deep Observations — What the Dig Revealed

### The Three Layers of HAIOS

```
Layer 1: HAIOS-RAW (Jun-Oct 2025)
  57 ADRs, schemas, agent prototypes, ETL research
  → The "constitution" — design principles still referenced

Layer 2: haios_etl + docs/ (Oct-Dec 2025)
  Memory system, MCP server, ETL pipeline, 85k concepts
  → The "engine" — still running despite "deprecated" status

Layer 3: .claude/ governance (Dec 2025-Feb 2026)
  Skills, hooks, ceremonies, lifecycles, work items
  → The "operating system" — where all active development lives
```

### Unrealized Visions Worth Revisiting

1. **epoch3/ Three-Paradigm Memory** — Declarative + Procedural + Predictive. We built declarative (concepts/entities), partially built procedural (ReasoningBank traces), never built predictive (FORESIGHT). The metamemory/feeling-of-knowing concept is particularly relevant to Agent UX.

2. **epoch4_vision/ Inbox-Outbox Protocol** — File-based inter-agent communication with strict scope isolation. We partially implemented this with work items and checkpoints, but the formal inbox/outbox/state/history directory structure was never built. The "nursery not factory" philosophy permeates current design implicitly but isn't codified.

3. **APIP (Agent Project Interface Protocol)** — Standardized agent-project interaction framework. Partially realized through CLAUDE.md + plugin structure, but the formal protocol spec was never completed.

4. **Dynamic Ceremony Composition** (obs-313) — Ceremonies as composable config-driven units, not static skills. This is exactly the E2.6 agent-ux vision.

### Duplication & Drift

| Item | Location 1 | Location 2 | Status |
|------|-----------|-----------|--------|
| cascade logic | modules/cascade_engine.py | lib/cascade.py | Duplicated |
| spawn logic | modules/spawn_tree.py | lib/spawn.py | Duplicated |
| backfill logic | modules/backfill_engine.py | lib/backfill.py | Duplicated |
| ETL code | haios_etl/ | .claude/haios/lib/ (planned) | Migration incomplete |
| CLI | modules/cli.py | lib/cli.py | Different purpose, naming collision |
| ADRs | docs/ADR/ (15) | HAIOS-RAW/system/canon/ADR/ (57) | Two eras |
| Templates | .claude/templates/ | HAIOS-RAW/templates/ | Two eras |
| MEMVID proposal | 6 copies in root | — | Cleanup candidate |

### Things That Exist But Nobody References

1. `.claude/REFS/` — 11 reference docs (commands, hooks, MCP, SDK, skills, subagents, troubleshooting). Are agents using these?
2. `.claude/config/north-star.md` and `roadmap.md` — loaded at coldstart?
3. `docs/libraries/` — 14 reference documents. Consumed by anyone?
4. `docs/anti-patterns/` — Only 1 anti-pattern documented. More observed but not captured.
5. `_future_specs/` — Single unrealized MCP API spec.
6. `investigations/` and `plans/` and `reports/` (root level) — Empty directories.
7. `output/` — One-off scripts and results from Dec 2025.
8. `.benchmarks/` — Empty.

### The Information Architecture Gap

The system has **contracts** (WORK.md, PLAN.md, checkpoint) but they evolved organically:
- WORK.md frontmatter: 30+ fields, many rarely used
- Plans in docs/plans/: 109 files, mix of EPOCH2-era and E2-series naming
- Checkpoints: Two archives (docs/archive/checkpoints/ for old, docs/checkpoints/ for recent)
- Handoffs: Separate docs/handoff/ — are these still used?

Progressive disclosure is documented as a principle (docs/README.md mentions 7 layers) but not enforced in contract design.

---

## 21. L4 Requirement Coverage

*Generated by `scripts/audit_l4_coverage.py` (WORK-075, Session 370). Regenerate with `just audit-l4-coverage`.*

### Data Quality

| Metric | Count |
|--------|-------|
| Total work items scanned | 185 |
| Items with `traces_to` populated | 99 (54%) |
| Items without `traces_to` (legacy/empty) | 86 (46%) |

**Note:** Many legacy work items (E2-xxx, INV-xxx, CH-xxx) predate the `traces_to` field (REQ-TRACE-001). "Gap" means no items *with `traces_to`* reference this requirement, not necessarily that no implementation exists.

### Coverage Table

| Requirement | Domain | Work Items | Status |
|-------------|--------|------------|--------|
| REQ-ACTIVITY-001 | Activities | WORK-039, WORK-040, WORK-041, WORK-042 | Implemented |
| REQ-ACTIVITY-002 | Activities | WORK-041, WORK-042 | Implemented |
| REQ-ASSET-001 | Asset | WORK-093 | In Progress |
| REQ-ASSET-002 | Asset | - | Gap |
| REQ-ASSET-003 | Asset | WORK-097, WORK-150 | Implemented |
| REQ-ASSET-004 | Asset | WORK-097, WORK-150 | Implemented |
| REQ-ASSET-005 | Asset | WORK-150 | In Progress |
| REQ-CEREMONY-001 | Ceremony | WORK-101, WORK-110, WORK-113, WORK-114, WORK-115, WORK-116, WORK-120, WORK-122, WORK-127, WORK-129, WORK-130, WORK-133, WORK-136, WORK-137, WORK-142 | Implemented |
| REQ-CEREMONY-002 | Ceremony | WORK-102, WORK-110, WORK-111, WORK-112, WORK-113, WORK-114, WORK-115, WORK-120, WORK-122, WORK-123, WORK-133, WORK-137, WORK-142, WORK-143 | Implemented |
| REQ-CEREMONY-003 | Ceremony | WORK-096, WORK-118 | Implemented |
| REQ-CEREMONY-004 | Ceremony | WORK-082 | In Progress |
| REQ-CONFIG-001 | Config | WORK-060, WORK-068, WORK-100 | Implemented |
| REQ-CONFIG-002 | Config | - | Gap |
| REQ-CONFIG-003 | Config | WORK-145 | In Progress |
| REQ-CONFIG-004 | Config | - | Gap |
| REQ-CONFIG-005 | Config | - | Gap |
| REQ-CONTEXT-001 | Context | E2-236, WORK-023, WORK-056, WORK-058, WORK-063, WORK-065 | Implemented |
| REQ-CONTEXT-002 | Context | - | Gap |
| REQ-CONTEXT-003 | Context | - | Gap |
| REQ-CRITIQUE-001 | Critique | WORK-121 | Implemented |
| REQ-CRITIQUE-002 | Critique | - | Gap |
| REQ-DISCOVER-001 | Discoverability | WORK-020 | Implemented |
| REQ-DISCOVER-002 | Discoverability | WORK-020, WORK-149 | Implemented |
| REQ-DISCOVER-003 | Discoverability | WORK-020, WORK-148, WORK-149 | Implemented |
| REQ-DISCOVER-004 | Discoverability | WORK-144 | In Progress |
| REQ-DOD-001 | DoD | WORK-076, WORK-122 | Implemented |
| REQ-DOD-002 | DoD | WORK-077, WORK-078, WORK-122 | Implemented |
| REQ-FEEDBACK-001 | Feedback | WORK-102, WORK-142, WORK-143 | Implemented |
| REQ-FEEDBACK-002 | Feedback | - | Gap |
| REQ-FEEDBACK-003 | Feedback | - | Gap |
| REQ-FEEDBACK-004 | Feedback | - | Gap |
| REQ-FEEDBACK-005 | Feedback | - | Gap |
| REQ-FLOW-001 | Flow | WORK-040, WORK-079 | Implemented |
| REQ-FLOW-002 | Flow | WORK-040, WORK-043 | Implemented |
| REQ-FLOW-003 | Flow | - | Gap |
| REQ-GOVERN-001 | Governance | WORK-042, WORK-056, WORK-057, WORK-064 | Implemented |
| REQ-GOVERN-002 | Governance | E2-305, E2-306, INV-069, WORK-042 | Implemented |
| REQ-GOVERN-003 | Governance | - | Gap |
| REQ-LIFECYCLE-001 | Lifecycle | WORK-081, WORK-101, WORK-104 | Implemented |
| REQ-LIFECYCLE-002 | Lifecycle | - | Gap |
| REQ-LIFECYCLE-003 | Lifecycle | WORK-086 | Implemented |
| REQ-LIFECYCLE-004 | Lifecycle | - | Gap |
| REQ-MEMORY-001 | Memory | WORK-038, WORK-083, WORK-108, WORK-133 | Implemented |
| REQ-MEMORY-002 | Memory | - | Gap |
| REQ-OBSERVE-001 | Observability | - | Gap |
| REQ-OBSERVE-002 | Observability | - | Gap |
| REQ-OBSERVE-003 | Observability | - | Gap |
| REQ-OBSERVE-004 | Observability | - | Gap |
| REQ-OBSERVE-005 | Observability | WORK-146 | In Progress |
| REQ-QUEUE-001 | Queue | WORK-066, WORK-105, WORK-106, WORK-126, WORK-131, WORK-132 | Implemented |
| REQ-QUEUE-002 | Queue | WORK-107 | Implemented |
| REQ-QUEUE-003 | Queue | WORK-103, WORK-106, WORK-109 | Implemented |
| REQ-QUEUE-004 | Queue | WORK-110, WORK-124, WORK-125, WORK-128 | Implemented |
| REQ-QUEUE-005 | Queue | WORK-106, WORK-109 | Implemented |
| REQ-REFERENCE-001 | Referenceability | WORK-067 | Implemented |
| REQ-REFERENCE-002 | Referenceability | WORK-067, WORK-147 | Implemented |
| REQ-TEMPLATE-001 | Templates | WORK-043, WORK-088 | Implemented |
| REQ-TEMPLATE-002 | Templates | WORK-043, WORK-089, WORK-090, WORK-091, WORK-092, WORK-098, WORK-099 | Implemented |
| REQ-TRACE-001 | Traceability | - | Gap |
| REQ-TRACE-002 | Traceability | - | Gap |
| REQ-TRACE-003 | Traceability | WORK-070 | Implemented |
| REQ-TRACE-004 | Traceability | E2-304, WORK-015, WORK-031, WORK-032 | Implemented |
| REQ-TRACE-005 | Traceability | INV-070, WORK-015, WORK-031, WORK-032, WORK-069, WORK-071, WORK-072, WORK-073, WORK-074, WORK-075 | Implemented |
| REQ-VALID-001 | Validation | E2-304 | Implemented |
| REQ-VALID-002 | Validation | - | Gap |
| REQ-VALID-003 | Validation | - | Gap |
| REQ-WORK-001 | Work | WORK-059 | Implemented |
| REQ-WORK-002 | Work | - | Gap |

### Coverage Summary

| Status | Count | Percentage |
|--------|-------|------------|
| Implemented | 37 | 54% |
| In Progress | 6 | 9% |
| Gap | 25 | 37% |
| **Total** | **68** | **100%** |

---

## 22. E2.4 Decision Coverage

*Maps E2.4 epoch decisions to E2.6 arcs/chapters based on conceptual alignment.*

| Decision | Title | Arcs/Chapters | Status |
|----------|-------|---------------|--------|
| D1 | Five-Layer Hierarchy | discoverability (CH-032..034), observability (CH-042) | Mapped |
| D2 | Work Classification (Two-Axis) | traceability (CH-038) | Mapped |
| D3 | Governed Activities | traceability (CH-040: gate skip logging) | Mapped |
| D4 | Critique as Hard Gate | traceability (CH-038: WORK-097 spawn_type) | Mapped |
| D5 | Universal Flow | traceability (CH-038: lifecycle mappings) | Mapped |
| D6 | Fractured Templates | referenceability (CH-036: template bootstrap) | Mapped |
| D7 | Four-Dimensional Work Item State (WORK-065) | traceability (CH-038: WORK-104 activity matrix) | Mapped |
| D8 | Multi-Level Governance (WORK-055) | traceability (CH-039: L4 coverage audit) | Mapped |

All 8 E2.4 decisions have arc/chapter assignments in E2.6.

---

## 23. Gap Analysis

### L4 Requirements Without Implementation

25 of 68 requirements (37%) have no work item with `traces_to` referencing them:

- **REQ-ASSET-002** (Asset): No work item traces to this requirement
- **REQ-CONFIG-002** (Config): No work item traces to this requirement
- **REQ-CONFIG-004** (Config): No work item traces to this requirement
- **REQ-CONFIG-005** (Config): No work item traces to this requirement
- **REQ-CONTEXT-002** (Context): No work item traces to this requirement
- **REQ-CONTEXT-003** (Context): No work item traces to this requirement
- **REQ-CRITIQUE-002** (Critique): No work item traces to this requirement
- **REQ-FEEDBACK-002** (Feedback): No work item traces to this requirement
- **REQ-FEEDBACK-003** (Feedback): No work item traces to this requirement
- **REQ-FEEDBACK-004** (Feedback): No work item traces to this requirement
- **REQ-FEEDBACK-005** (Feedback): No work item traces to this requirement
- **REQ-FLOW-003** (Flow): No work item traces to this requirement
- **REQ-GOVERN-003** (Governance): No work item traces to this requirement
- **REQ-LIFECYCLE-002** (Lifecycle): No work item traces to this requirement
- **REQ-LIFECYCLE-004** (Lifecycle): No work item traces to this requirement
- **REQ-MEMORY-002** (Memory): No work item traces to this requirement
- **REQ-OBSERVE-001** (Observability): No work item traces to this requirement
- **REQ-OBSERVE-002** (Observability): No work item traces to this requirement
- **REQ-OBSERVE-003** (Observability): No work item traces to this requirement
- **REQ-OBSERVE-004** (Observability): No work item traces to this requirement
- **REQ-TRACE-001** (Traceability): No work item traces to this requirement
- **REQ-TRACE-002** (Traceability): No work item traces to this requirement
- **REQ-VALID-002** (Validation): No work item traces to this requirement
- **REQ-VALID-003** (Validation): No work item traces to this requirement
- **REQ-WORK-002** (Work): No work item traces to this requirement

**Observations:**
- Observability (4/5 gap) and Feedback (4/5 gap) are the weakest domains
- Some gaps may be false positives due to missing `traces_to` in legacy items (46% of items lack the field)
- REQ-TRACE-001 and REQ-TRACE-002 are ironic gaps — the traceability requirements themselves lack traceability metadata

### Epoch Decisions Without Arc/Chapter Mapping

All 8 epoch decisions have arc/chapter assignments. No gaps.
