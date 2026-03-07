# HAIOS Complete System Inventory

This document provides a comprehensive inventory of all Agents, Skills, and Templates within the `.claude/` ecosystem, along with their current operational status.

## 1. Skill Inventory (`.claude/skills/`)
Skills are L4 operations explicitly permitted in `settings.local.json`.

| Skill Name | Category | Status | Description |
|---|---|---|---|
| `audit` | unknown | **Orphaned/Inactive** | Run all HAIOS audit checks to find drift, gaps, and stale items. Use before starting a new session or after completing a milestone. |
| `checkpoint-cycle` | session | **Orphaned/Inactive** | Create checkpoint manifest. Scaffold, populate fields, commit. |
| `close-arc-ceremony` | closure | **Orphaned/Inactive** | HAIOS Close Arc Ceremony for verifying arc DoD. Use when all chapters in an arc are complete. Guides VALIDATE->MARK->REPORT workflow with orphan decision check. |
| `close-chapter-ceremony` | closure | **Orphaned/Inactive** | HAIOS Close Chapter Ceremony for verifying chapter DoD. Use when all work items in a chapter are complete. Guides VALIDATE->MARK->REPORT workflow with decision verification. |
| `close-epoch-ceremony` | closure | **Orphaned/Inactive** | HAIOS Close Epoch Ceremony for verifying epoch DoD. Use when all arcs are complete. Guides VALIDATE->ARCHIVE->TRANSITION workflow. |
| `close-work-cycle` | ['closure', 'queue'] | **Orphaned/Inactive** | HAIOS Close Work Cycle for structured work item closure. Prerequisite: retro-cycle must complete before this cycle (invoked by /close). Guides VALIDATE->ARCHIVE->CHAIN workflow with DoD enforcement. |
| `design-review-validation` | unknown | **Orphaned/Inactive** | HAIOS Design Review Validation for verifying implementation alignment. Use during DO phase. Guides COMPARE->VERIFY->APPROVE workflow. |
| `dod-validation-cycle` | unknown | **Orphaned/Inactive** | HAIOS DoD Validation Cycle for validating Definition of Done before closure. Use before DONE phase. Guides CHECK->VALIDATE->APPROVE workflow. |
| `extract-content` | unknown | **Orphaned/Inactive** | Extract entities and concepts from documents using HAIOS memory system. Use when ingesting new documents, analyzing content structure, or populating the knowledge base. |
| `ground-cycle` | unknown | **Orphaned/Inactive** | HAIOS Ground Cycle for loading architectural context before cognitive work. Use before plan-authoring, investigation, or implementation cycles. |
| `implementation-cycle` | unknown | **Orphaned/Inactive** | HAIOS Implementation Cycle for structured work item implementation. Use when starting implementation of a plan. Guides PLAN->DO->CHECK->DONE workflow with phase-specific tooling. |
| `investigation-cycle` | unknown | **Orphaned/Inactive** | HAIOS Investigation Cycle for structured research and discovery. Use when starting or resuming an investigation. Guides EXPLORE->HYPOTHESIZE->VALIDATE->CONCLUDE workflow with phase-specific tooling. |
| `memory-agent` | unknown | **Orphaned/Inactive** | HAIOS Memory Agent for intelligent context retrieval and learning. Use BEFORE answering complex questions to retrieve relevant strategies and context. Use AFTER completing tasks to extract and store learnings. Closes the ReasoningBank loop by injecting strategies into reasoning. |
| `memory-commit-ceremony` | memory | **Orphaned/Inactive** | Store learnings to memory with provenance tracking. |
| `observation-triage-cycle` | memory | **Orphaned/Inactive** | HAIOS Observation Triage Cycle for processing captured observations. Use when scanning archived work items to triage and act on observations. Supports both memory-based retro-triage (WORK-143) and filesystem-based legacy triage. Guides SCAN->TRIAGE->PROMOTE workflow with dimension validation. |
| `open-epoch-ceremony` | closure | **Orphaned/Inactive** | Initialize a new epoch with directory structure, config transition, work item triage, and arc decomposition. |
| `plan-authoring-cycle` | unknown | **Orphaned/Inactive** | HAIOS Plan Authoring Cycle for structured plan population. Use when filling in implementation plan sections. Guides AMBIGUITY->ANALYZE->AUTHOR->VALIDATE workflow. |
| `plan-validation-cycle` | unknown | **Orphaned/Inactive** | HAIOS Plan Validation Bridge for validating plan readiness. Use before entering DO phase. Guides CHECK->VALIDATE->APPROVE workflow. |
| `queue-commit` | queue | **Orphaned/Inactive** | Move work item from ready to working queue position, signaling active work session. Use when starting implementation of a ready item. Typically invoked by survey-cycle after work selection. |
| `queue-intake` | queue | **Orphaned/Inactive** | Create new work item at backlog queue position with ceremony logging. Use when capturing a new idea or requirement as a tracked work item. Wraps work-creation-cycle with queue ceremony event. |
| `queue-prioritize` | queue | **Orphaned/Inactive** | Move work items from backlog to ready queue position with rationale. Use when selecting items for upcoming work. Batch capable. Rationale required for audit trail. |
| `queue-unpark` | queue | **Orphaned/Inactive** | Move work item between parked and backlog (scope decision). Use when bringing a parked item into scope (Unpark) or deferring a backlog item out of scope (Park). Operator decision requiring rationale. |
| `retro-cycle` | ['memory', 'closure'] | **Orphaned/Inactive** | Multi-step autonomous reflection with typed provenance for work closure. Replaces observation-capture-cycle with structured pipeline: REFLECT->DERIVE->EXTRACT->COMMIT. |
| `routing-gate` | unknown | **Orphaned/Inactive** | Bridge skill for work-type routing in CHAIN phase. Use to determine next cycle skill based on work item signals. |
| `schema-ref` | unknown | **Orphaned/Inactive** | Database schema reference for haios_memory.db. MUST be used before any SQL query to verify table and column names. Use when verifying schema, checking table structure, or before database operations. |
| `session-end-ceremony` | session | **Orphaned/Inactive** | Finalize session with orphan check and event logging. |
| `session-start-ceremony` | session | **Orphaned/Inactive** | Initialize a new session with context loading and event logging. |
| `spawn-work-ceremony` | spawn | **Orphaned/Inactive** | Create a linked work item from an existing work item. |
| `survey-cycle` | unknown | **Orphaned/Inactive** | HAIOS Survey Cycle for structured session-level work selection. Use after coldstart context loading. Guides GATHER->ASSESS->OPTIONS->CHOOSE->ROUTE workflow with volumous exploration before tight commitment. |
| `work-creation-cycle` | unknown | **Orphaned/Inactive** | HAIOS Work Creation Cycle for structured work item population. Use when creating new work items. Guides VERIFY->POPULATE->READY workflow. |

## 2. Agent Inventory (`.claude/agents/`)
Agents are specialized personas. Modern L4 architecture dictates they should be invoked dynamically via `Task(subagent_type=X)` within Skills. Legacy agents exist as dead markdown files.

| Agent Name | Status | Description |
|---|---|---|
| `anti-pattern-checker` | **Active (Dynamic Invoke)** | Verify claims against 6 L1 anti-patterns before acceptance. Use for epoch, milestone, or major compl |
| `critique-agent` | **Active (Dynamic Invoke)** | Pre-implementation assumption surfacing. Framework loaded from haios.yaml config. |
| `preflight-checker` | **Active (Dynamic Invoke)** | Validate plan readiness and enforce DO phase guardrails. Use before starting implementation. |
| `test-runner` | **Active (Dynamic Invoke)** | Execute pytest in isolated context. Returns structured pass/fail summary. Use during CHECK phase. |
| `validation-agent` | **Active (Dynamic Invoke)** | Unbiased CHECK phase validation. Runs tests, demos features, checks DoD criteria in isolated context |
| `close-work-cycle-agent` | **Legacy/Orphaned** | Execute close-work-cycle autonomously in isolated context. Returns structured summary with DoD valid |
| `implementation-cycle-agent` | **Legacy/Orphaned** | Execute implementation-cycle autonomously in isolated context. Returns structured summary with gover |
| `investigation-agent` | **Legacy/Orphaned** | Phase-aware research agent for HAIOS investigations. Use during investigation-cycle to conduct hypot |
| `investigation-cycle-agent` | **Legacy/Orphaned** | Execute investigation-cycle autonomously in isolated context. Returns structured summary with hypoth |
| `schema-verifier` | **Legacy/Orphaned** | Verify database schema and run read-only queries. Returns table/column info in isolated context. Use |
| `why-capturer` | **Legacy/Orphaned** | Extract and store learnings from completed work. Use during DONE phase to capture WHY per ADR-033. |

## 3. Template Inventory (`.claude/templates/`)
Templates are standard scaffolds used across the system arcs.

| Template Path | Type | Status |
|---|---|---|
| `_legacy/implementation_plan.md` | markdown | **Available** |
| `arc.md` | markdown | **Available** |
| `architecture_decision_record.md` | markdown | **Available** |
| `ceremony/SKILL.md` | markdown | **Available** |
| `chapter.md` | markdown | **Available** |
| `checkpoint.md` | markdown | **Available** |
| `design/COMPLETE.md` | markdown | **Available** |
| `design/CRITIQUE.md` | markdown | **Available** |
| `design/EXPLORE.md` | markdown | **Available** |
| `design/SPECIFY.md` | markdown | **Available** |
| `handoff_investigation.md` | markdown | **Available** |
| `implementation/CHECK.md` | markdown | **Available** |
| `implementation/DO.md` | markdown | **Available** |
| `implementation/DONE.md` | markdown | **Available** |
| `implementation/PLAN.md` | markdown | **Available** |
| `investigation.md` | markdown | **Available** |
| `investigation/CONCLUDE.md` | markdown | **Available** |
| `investigation/EXPLORE.md` | markdown | **Available** |
| `investigation/HYPOTHESIZE.md` | markdown | **Available** |
| `investigation/VALIDATE.md` | markdown | **Available** |
| `observations.md` | markdown | **Available** |
| `plans/cleanup.md` | markdown | **Available** |
| `plans/design.md` | markdown | **Available** |
| `plans/implementation.md` | markdown | **Available** |
| `report.md` | markdown | **Available** |
| `skill.md` | markdown | **Available** |
| `triage/ASSESS.md` | markdown | **Available** |
| `triage/COMMIT.md` | markdown | **Available** |
| `triage/RANK.md` | markdown | **Available** |
| `triage/SCAN.md` | markdown | **Available** |
| `validation/JUDGE.md` | markdown | **Available** |
| `validation/REPORT.md` | markdown | **Available** |
| `validation/VERIFY.md` | markdown | **Available** |
| `work_item.md` | markdown | **Available** |
