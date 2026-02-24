---
template: implementation_plan
subtype: design
status: complete
date: 2026-02-24
backlog_id: WORK-164
title: "Agent Cards"
author: Hephaestus
lifecycle_phase: plan
session: 439
version: "1.5"
generated: 2026-02-24
last_updated: 2026-02-24T10:13:13
---
# Design Plan: Agent Cards

---

<!-- TEMPLATE GOVERNANCE (v1.4)
     Design plan template — optimized for ADRs, specs, and documentation work.
     No code-specific sections (TDD, code diffs, function signatures).
     WORK-152: Fractured from monolithic implementation_plan template.

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Query prior work | SHOULD | Search memory for similar designs before authoring |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Define a standardized agent card schema, extend existing agent frontmatter, create an auto-generated AGENTS.md as the vendor-neutral discovery layer, create a Python lib/ module for programmatic agent queries, and update CLAUDE.md to reference AGENTS.md instead of hardcoding the agent table.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 13 | `.claude/agents/*.md` (13 agent files) — extend frontmatter |
| Files to modify | 2 | `.claude/agents/README.md`, `CLAUDE.md` — update references |
| New files to create | 2 | `AGENTS.md` (auto-generated), `.claude/haios/lib/agent_cards.py` (query module) |
| New files to create | 1 | `.claude/haios/lib/generate_agents_md.py` (generator script) |
| Dependencies | 3 | CLAUDE.md agent table, `.claude/agents/README.md`, haios.yaml agent config |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Schema definition + frontmatter extension | 30 min | High |
| Python query module (lib/) | 30 min | High |
| Auto-gen AGENTS.md script + initial generation | 30 min | High |
| Update 13 agent frontmatter files | 45 min | Medium |
| Update CLAUDE.md + README.md references | 15 min | High |
| Tests | 30 min | High |
| **Total** | ~3 hr | Medium |

---

## Current State vs Desired State

### Current State

**What exists now:** 13 agent `.md` files in `.claude/agents/` with YAML frontmatter containing partial capability card fields (name, description, tools, model, requirement_level, category, trigger_conditions, input_contract, output_contract, invoked_by, related_agents). A manual README.md listing 12 agents (missing design-review-validation-agent). CLAUDE.md contains a hardcoded agent table duplicating information from agent files.

**Problem:** (1) No `produces`/`consumes` fields — agents can't discover data flow contracts. (2) CLAUDE.md agent table is a manual duplicate that drifts (already shows 12 not 13). (3) No vendor-neutral discovery layer — agent info is scattered across CLAUDE.md (vendor-specific) and `.claude/agents/README.md`. (4) No programmatic query mechanism — agents must read files to discover each other (REQ-DISCOVER-003 violation).

### Desired State

**What should exist:** A three-layer discovery architecture: (1) CLAUDE.md (vendor-specific) references AGENTS.md, (2) AGENTS.md (vendor-neutral, auto-generated) is the human-readable registry with full agent table, (3) `.claude/haios/lib/agent_cards.py` provides programmatic queries (list, filter by category/requirement_level, get by name). All 13 agent files have standardized frontmatter with `produces`, `consumes`, and `id` fields added to existing schema.

**Outcome:** Agents discover each other via infrastructure (REQ-DISCOVER-003). Agent table never drifts because AGENTS.md is generated from frontmatter (single source of truth). Future consumers (MCP server, SDK tools) can import the Python module directly. Vendor portability: any AI tool can read AGENTS.md without Claude Code-specific knowledge.

---

## Detailed Design

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Discovery layering | CLAUDE.md → AGENTS.md → agent files | Operator directive S439: CLAUDE.md is vendor-specific. AGENTS.md is the vendor-neutral global. Decouples discovery from Claude Code. |
| Query mechanism | Python lib/ module (no MCP) | L3.20 proportional governance: 13 agents don't warrant MCP overhead. Module is importable by future MCP server when needed. |
| AGENTS.md generation | Auto-generated from frontmatter | Single source of truth. Prevents drift (current README shows 12, actual is 13). Script in lib/. |
| Schema extension | Add `id`, `role`, `capabilities`, `produces`, `consumes` to existing frontmatter | Minimal change. Existing fields cover 80%. `role` maps to `category` (acceptance criteria alignment). `capabilities` is a new structured list derived from trigger_conditions + tools. |
| Field optionality | New fields are Optional with defaults for TDD compatibility | A1 critique: AgentCard must instantiate from existing frontmatter before Step 2 extends it. Optional fields with defaults enable RED-GREEN cycle. |
| Artifact vocabulary | Controlled vocabulary for produces/consumes values | A5 critique: Without controlled vocabulary, artifact type strings drift immediately. Define canonical names upfront. |
| Script path anchoring | Use Path(__file__) for both agent_cards.py and generate_agents_md.py | A2/A9 critique: Relative paths break when scripts run from non-root cwd. Anchor to script location. |
| A2A alignment | Inspired by, not conformant to | A2A is for network agents with HTTP endpoints. HAIOS agents are in-process subagents. Take the schema concepts (id, capabilities, skills) but not the protocol (interfaces, security, endpoints). |
| README.md fate | Replaced by auto-generated AGENTS.md | README.md becomes a pointer to AGENTS.md. No dual maintenance. |

### Design Content

#### Agent Card Schema (Extended Frontmatter)

Existing fields (no changes):
```yaml
name: string           # Agent identifier (used in Task subagent_type)
description: string    # One-line purpose (used in Claude Code agent registry)
tools: string          # Comma-separated tool names
model: enum            # haiku | sonnet | opus
requirement_level: enum # required | recommended | optional
category: enum         # gate | verification | utility | cycle-delegation
trigger_conditions: list[string]  # When to invoke
input_contract: string  # What agent expects
output_contract: string # What agent returns
invoked_by: list[string] # Which skills/cycles invoke this agent
related_agents: list[string] # Cross-references
```

New fields:
```yaml
id: string                    # Unique identifier (e.g., "critique-agent"). Same as name for now.
role: string                  # Semantic role (maps to category). Values: "gate", "verifier", "utility", "cycle-delegate"
capabilities: list[string]    # What this agent can do (e.g., ["assumption-surfacing", "plan-critique"])
produces: list[string]        # Artifacts this agent creates — uses controlled vocabulary below
consumes: list[string]        # Artifacts this agent reads — uses controlled vocabulary below
```

**Field mapping to acceptance criteria:**
| AC Field | Schema Field | Notes |
|----------|-------------|-------|
| id | `id` | Same as `name` |
| role | `role` | Semantic alias for `category` with agent-facing vocabulary |
| capabilities | `capabilities` | New structured list — what the agent can do |
| tools | `tools` | Existing |
| triggers | `trigger_conditions` | Existing |
| produces | `produces` | New |
| consumes | `consumes` | New |

**Controlled Artifact Vocabulary (produces/consumes):**
| Artifact Type | Description | Example Producer | Example Consumer |
|--------------|-------------|-----------------|-----------------|
| `critique-report` | Assumption surfacing report | critique-agent | implementation-cycle |
| `assumptions-yaml` | Machine-parseable assumptions | critique-agent | preflight-checker |
| `test-results` | Pytest pass/fail summary | test-runner | validation-agent |
| `validation-report` | CHECK phase validation | validation-agent | close-work-cycle |
| `investigation-findings` | EXPLORE phase evidence | investigation-agent | investigation-cycle |
| `plan-document` | Authored implementation plan | plan-authoring-agent | critique-agent |
| `schema-info` | Database schema verification | schema-verifier | any |
| `design-review` | Design alignment PASS/FAIL | design-review-validation-agent | implementation-cycle |
| `anti-pattern-verdict` | L1 anti-pattern check | anti-pattern-checker | close-work-cycle |
| `learning-extraction` | WHY capture for memory | why-capturer | memory system |
| `work-item` | WORK.md structured data | any | any |
| `cycle-summary` | Structured cycle result | cycle-delegation agents | main agent |

**AgentCard dataclass (revised per A1 critique — Optional fields with defaults):**
```python
@dataclass
class AgentCard:
    name: str
    description: str
    tools: list[str]
    model: str
    # Existing optional fields
    requirement_level: str = "optional"
    category: str = "utility"
    trigger_conditions: list[str] = field(default_factory=list)
    input_contract: str = ""
    output_contract: str = ""
    invoked_by: list[str] = field(default_factory=list)
    related_agents: list[str] = field(default_factory=list)
    # New fields (Optional with defaults for TDD compatibility)
    id: str = ""                    # Defaults to name if empty
    role: str = ""                  # Defaults to category if empty
    capabilities: list[str] = field(default_factory=list)
    produces: list[str] = field(default_factory=list)
    consumes: list[str] = field(default_factory=list)
```

#### Three-Layer Discovery Architecture

```
Layer 1: CLAUDE.md (vendor-specific)
  - Contains: "See AGENTS.md for agent capabilities"
  - Removes: hardcoded agent table
  - Purpose: Claude Code reads this; points to Layer 2

Layer 2: AGENTS.md (vendor-neutral, auto-generated)
  - Contains: Full agent table, capability summaries, invocation patterns
  - Generated by: .claude/haios/lib/generate_agents_md.py
  - Purpose: Any AI tool or human can read this
  - Location: project root (next to CLAUDE.md)

Layer 3: .claude/agents/*.md (source of truth)
  - Contains: Full agent definitions with YAML frontmatter + prose docs
  - Purpose: Detailed agent documentation, machine-parseable frontmatter
```

#### Python Query Module: `.claude/haios/lib/agent_cards.py`

```python
# Public API
def list_agents() -> list[AgentCard]:
    """Glob .claude/agents/*.md, parse frontmatter, return AgentCard list."""

def get_agent(name: str) -> AgentCard | None:
    """Get single agent by name."""

def filter_agents(
    category: str | None = None,
    requirement_level: str | None = None,
    model: str | None = None,
) -> list[AgentCard]:
    """Filter agents by frontmatter fields."""

@dataclass
class AgentCard:
    id: str
    name: str
    description: str
    tools: list[str]
    model: str
    requirement_level: str
    category: str
    trigger_conditions: list[str]
    input_contract: str
    output_contract: str
    invoked_by: list[str]
    related_agents: list[str]
    produces: list[str]
    consumes: list[str]
```

#### AGENTS.md Generator: `.claude/haios/lib/generate_agents_md.py`

Script that:
1. Calls `list_agents()` from agent_cards module
2. Renders a markdown file with:
   - Summary table (name, model, requirement, category, purpose)
   - Per-category sections with trigger conditions and contracts
   - Invocation pattern examples
3. Writes to `AGENTS.md` at project root
4. Can be run as `python .claude/haios/lib/generate_agents_md.py`

### Open Questions

**Q: Should `produces`/`consumes` use file paths or abstract artifact types?**

RESOLVED: Abstract artifact types with a controlled vocabulary (12 canonical types defined above). File paths are context-dependent. Vocabulary validated by tests.

**Q: Should AGENTS.md generation be automated (pre-commit hook) or manual?**

RESOLVED: Manual via `just agents` recipe. Pre-commit hook is premature — only 13 agents, changes are rare.

**Q: What about the `.claude/agents/README.md` — keep or remove?**

RESOLVED: Keep but reduce to a pointer to AGENTS.md.

**Q: How do `role` and `capabilities` map to existing fields? (A4 critique)**

RESOLVED: `role` maps to `category` with agent-facing vocabulary (gate→gate, verification→verifier, utility→utility, cycle-delegation→cycle-delegate). `capabilities` is a new structured list describing what the agent can do (e.g., ["assumption-surfacing", "plan-critique"]).

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Query mechanism | Python module, MCP tool, static file | Python module | Operator confirmed: MCP is over-engineering for 13 agents. Module is future-proof. |
| Discovery layering | CLAUDE.md hardcoded, AGENTS.md auto-gen | AGENTS.md auto-gen | Operator directive: CLAUDE.md is vendor-specific, AGENTS.md is the global. |

---

## Implementation Steps

<!-- Each step describes authoring work, not code changes -->

### Step 1: Define Schema + Write Tests
- [ ] Write `tests/test_agent_cards.py` with tests for: parse single agent, list all agents, filter by category, filter by requirement_level, get by name, missing file handling, Optional field defaults
- [ ] Write `tests/test_generate_agents_md.py` with tests for: generates valid markdown, includes all agents, table row count matches agent count
- [ ] Create `.claude/haios/lib/agent_cards.py` with `AgentCard` dataclass (Optional new fields per A1) and `list_agents()`, `get_agent()`, `filter_agents()` functions. Use `Path(__file__)` anchoring for agent dir resolution (A2/A9).
- [ ] Run tests — should pass with existing frontmatter (new fields are Optional with defaults)

### Step 2: Extend Agent Frontmatter
- [ ] Add `id`, `role`, `capabilities`, `produces`, `consumes` fields to all 13 agent `.md` files using controlled artifact vocabulary
- [ ] **A6 MUST:** Update `tests/test_agent_capability_cards.py` required_fields set to include `id`, `role`, `capabilities`, `produces`, `consumes`
- [ ] Verify all frontmatter parses correctly (run full test suite)

### Step 3: Create AGENTS.md Generator
- [ ] Write `.claude/haios/lib/generate_agents_md.py` with `Path(__file__)` anchored output path (A9)
- [ ] Use `sys.path.insert` for agent_cards import (A2)
- [ ] Run generator to produce `AGENTS.md` at project root
- [ ] Verify generated content matches all 13 agents

### Step 4: Update References
- [ ] **A7 MUST:** Before modifying CLAUDE.md, grep `.claude/skills/`, `.claude/commands/`, `.claude/hooks/` for references to CLAUDE.md agent table. Document findings. Queue companion work if consumers found.
- [ ] **A11:** Verify AGENTS.md root placement is consistent with ADR-045 (read ADR-045 first)
- [ ] **MUST:** Update CLAUDE.md — replace hardcoded agent table with reference to AGENTS.md
- [ ] **MUST:** Update `.claude/agents/README.md` — reduce to pointer to AGENTS.md
- [ ] Add `just agents` recipe for regeneration convenience (with PYTHONPATH set)

### Step 5: Validate
- [ ] All tests pass (test_agent_cards, test_generate_agents_md, test_agent_capability_cards)
- [ ] AGENTS.md contains all 13 agents with correct metadata
- [ ] CLAUDE.md no longer has hardcoded agent table
- [ ] `list_agents()` returns 13 agents
- [ ] `filter_agents(category="gate")` returns preflight-checker and schema-verifier
- [ ] All produces/consumes values are in controlled vocabulary
- [ ] **A10:** Record critique artifact path in WORK.md artifacts[]

---

## Verification

- [ ] `agent_cards.py` module exists with public API (list, get, filter)
- [ ] `generate_agents_md.py` produces valid AGENTS.md
- [ ] All 13 agents have `id`, `produces`, `consumes` in frontmatter
- [ ] AGENTS.md at project root contains all 13 agents
- [ ] CLAUDE.md references AGENTS.md (no hardcoded table)
- [ ] `.claude/agents/README.md` is a pointer to AGENTS.md
- [ ] All tests pass (`test_agent_cards.py`, `test_generate_agents_md.py`)
- [ ] **MUST:** All READMEs current

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Frontmatter parse failures (malformed YAML) | Medium | Defensive parsing with try/except per file, skip invalid files with warning |
| AGENTS.md goes stale if agents added without regeneration | Low | Document in README that `just agents` must be run after agent changes. Future: pre-commit hook. |
| Consumer updates missed (test lists, manifest counts) | Medium | Grep for "Available Agents (12)" and similar hardcoded counts before closing |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 439 | 2026-02-24 | - | PLAN authored | EXPLORE + SPECIFY complete, plan authored |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-164/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Agent card schema definition | [ ] | `agent_cards.py` AgentCard dataclass |
| Existing agent audit (how many, what metadata exists) | [ ] | EXPLORE phase: 13 agents, 10 existing fields, 3 new fields needed |
| Query mechanism design (infrastructure discovery) | [ ] | `agent_cards.py` list/get/filter API |
| Migration plan from CLAUDE.md table | [ ] | Step 4 of implementation steps |
| Design document or ADR | [ ] | This plan document |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/agent_cards.py` | Module with AgentCard + list/get/filter | [ ] | |
| `.claude/haios/lib/generate_agents_md.py` | Generator script | [ ] | |
| `AGENTS.md` | Auto-generated, 13 agents | [ ] | |
| `CLAUDE.md` | Agent table replaced with AGENTS.md reference | [ ] | |
| `.claude/agents/README.md` | Pointer to AGENTS.md | [ ] | |
| `.claude/agents/*.md` (x13) | All have id, produces, consumes fields | [ ] | |
| `tests/test_agent_cards.py` | Tests passing | [ ] | |
| `tests/test_generate_agents_md.py` | Tests passing | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Design artifact complete
- [ ] **MUST:** All WORK.md deliverables verified complete
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories
- [ ] Ground Truth Verification completed above

---

## References

- REQ-DISCOVER-002: Three-tier entry point model
- REQ-DISCOVER-003: Agent discovers capabilities via infrastructure, not CLAUDE.md
- REQ-DISCOVER-004: All agents have capability cards
- WORK-144: Original capability card schema work (partial — existing frontmatter fields)
- Memory: 85154 (Dragon Quest pattern), 85155 (A2A protocol), 85156 (self-describing agents), 85210 (agents not discoverable), 85476 (deferred query tool)
- Google A2A Agent Card specification: https://a2a-protocol.org/latest/specification/
- Operator directive S439: CLAUDE.md is vendor-specific → AGENTS.md is global

---
