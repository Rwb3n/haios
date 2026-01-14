# generated: 2025-12-30
# System Auto: last updated on: 2025-12-30T23:13:21
# Section 11: Subagents

Generated: 2025-12-30 (Session 151)
Purpose: Document all subagents, tool access, isolation boundaries, and when-to-use patterns
Status: COMPLETE

---

## Gaps Identified (S152 Analysis)

| Gap | Description | Target Fix |
|-----|-------------|------------|
| **Tool access not enforced** | `tools:` in frontmatter is advisory only | Enforce via Task tool dispatcher |
| **MCP tools not agent-aware** | mcp_server.py doesn't know which agent is calling | Add agent_id to MCP calls (optional) |
| **No auto-invocation based on phase** | Agents manually invoked, could be auto-triggered | Define in cycle-definitions.yaml exit_gates |

---

## Target Architecture: Agent Manifest

```yaml
# .claude/haios/config/agent-manifest.yaml
agents:
  preflight-checker:
    required: true
    invoked_at: "implementation-cycle PLAN→DO"
    tools: [Read, Glob]
    enforcement: hard  # Task tool MUST restrict to these tools
    output_schema:
      ready: boolean
      phase: string
      issues: string[]
      blocked: boolean

  schema-verifier:
    required: true
    invoked_at: "any SQL attempt"
    tools: [Read, schema_info, db_query]
    enforcement: hard
    trigger: "PreToolUse detects Bash with SELECT/INSERT/etc"

  validation-agent:
    required: false
    invoked_at: "implementation-cycle CHECK"
    tools: [Bash, Read, Glob]
    enforcement: soft  # Recommended but not blocked

  anti-pattern-checker:
    required: false
    invoked_at: "checkpoint-cycle VERIFY, pre-closure"
    tools: [Read, Grep, Glob]
    checks_against: "invariants.md L1 anti-patterns"
```

**Portable:** Agents are Claude CLI native. Manifest enables orchestration by any LLM interface.

---

## Overview

Subagents are isolated execution contexts with restricted tool access. They live in `.claude/agents/<name>.md` and are invoked via `Task(subagent_type="<name>")`.

**Location:** `.claude/agents/` (7 agents + README)
**Invocation:** `Task(subagent_type="<name>", prompt="...")`

---

## Agent Inventory (7 agents)

### Required Agents

| Agent | Tools | Requirement | Purpose |
|-------|-------|-------------|---------|
| `preflight-checker` | Read, Glob | **REQUIRED** at PLAN→DO | Plan readiness + >3 file gate |
| `schema-verifier` | Read, schema_info, db_query | **REQUIRED** for SQL | Isolated schema queries |

### Optional Agents

| Agent | Tools | Purpose |
|-------|-------|---------|
| `validation-agent` | Bash, Read, Glob | Unbiased CHECK phase validation |
| `investigation-agent` | Read, Grep, Glob, WebSearch, WebFetch, memory_search | EXPLORE phase evidence gathering |
| `test-runner` | Bash, Read | Isolated test execution |
| `why-capturer` | Read, ingester_ingest | Automated learning extraction |
| `anti-pattern-checker` | Read, Grep, Glob | Verify claims against L1 anti-patterns |

---

## Agent Details

### `preflight-checker`

**Purpose:** Validate plan readiness and enforce DO phase guardrails.

**Requirement:** MUST invoke before DO phase. Implementation-cycle invokes this at PLAN→DO transition.

**Checks:**
1. Plan sections filled (not placeholders)
2. Goal, Tests First, Detailed Design complete
3. status: approved (not draft)
4. File manifest ≤3 files (else WARNING)

**Output:**
```json
{
  "ready": true|false,
  "phase": "PLAN"|"DO",
  "issues": ["..."],
  "warnings": ["..."],
  "blocked": true|false,
  "block_reason": "..."
}
```

### `schema-verifier`

**Purpose:** Execute database queries in isolated context.

**Requirement:** MUST use for any SQL query. Direct SQL is blocked by PreToolUse hook.

**Tools:**
- `schema_info(table_name)` - Get table/column info
- `db_query(sql)` - Execute SELECT queries (read-only)

### `validation-agent`

**Purpose:** Unbiased CHECK phase validation.

**Why isolated:** Main agent may be biased toward "done". Subagent provides fresh perspective.

**Actions:**
- Run tests via Bash
- Check code against plan
- Verify deliverables exist

### `investigation-agent`

**Purpose:** EXPLORE phase evidence gathering with web access.

**Tools include WebSearch/WebFetch:** Can research external docs, APIs, patterns.

**Memory access:** Can query `memory_search_with_experience` for prior findings.

### `test-runner`

**Purpose:** Execute pytest in isolated context.

**Output:** Structured pass/fail summary.

**Use:** CHECK phase, standalone test runs.

### `why-capturer`

**Purpose:** Extract and store learnings from completed work.

**Actions:**
1. Read work file and related docs
2. Extract key decisions and rationale
3. Store via `ingester_ingest`

**Use:** DONE phase per ADR-033.

### `anti-pattern-checker`

**Purpose:** Verify claims against L1 anti-patterns before acceptance.

**Checks against:**
1. Assume over verify
2. Generate over retrieve
3. Wide context
4. Abandon
5. Force over adapt
6. Premature closure

---

## Tool Access Matrix

| Agent | Read | Glob | Grep | Bash | Web | Memory Query | Memory Store |
|-------|------|------|------|------|-----|--------------|--------------|
| preflight-checker | ✓ | ✓ | | | | | |
| schema-verifier | ✓ | | | | | | |
| validation-agent | ✓ | ✓ | | ✓ | | | |
| investigation-agent | ✓ | ✓ | ✓ | | ✓ | ✓ | |
| test-runner | ✓ | | | ✓ | | | |
| why-capturer | ✓ | | | | | | ✓ |
| anti-pattern-checker | ✓ | ✓ | ✓ | | | | |

---

## Isolation Boundaries

### What Subagents CAN Do
- Use tools explicitly granted in frontmatter
- Return single message with findings
- Query memory (if granted)
- Execute shell commands (if granted)

### What Subagents CANNOT Do
- Edit/Write files (unless explicitly granted)
- Access full conversation context
- Invoke other subagents
- Invoke skills
- Modify system state beyond granted tools

### Why Isolation Matters

1. **Prevents cascading failures** - Subagent failure doesn't crash main agent
2. **Enables focused validation** - Limited context = focused output
3. **Governance enforcement** - Subagent can't bypass restrictions
4. **Unbiased validation** - Fresh context prevents confirmation bias

---

## Invocation Patterns

### Basic Invocation
```python
Task(
    subagent_type="preflight-checker",
    prompt="Check plan for E2-123"
)
```

### With Context
```python
Task(
    subagent_type="investigation-agent",
    prompt="""
    Investigate: How does cycle state persist across sessions?

    Context:
    - Working on INV-052
    - Focus on WORK.md node_history
    """
)
```

### Return Handling
```python
result = Task(subagent_type="test-runner", prompt="Run pytest")
# result is single message with structured output
# Main agent interprets and decides next action
```

---

## Required vs Optional Logic

### Required Agents - Governance Enforced

| Agent | Enforcement Point |
|-------|-------------------|
| preflight-checker | implementation-cycle PLAN→DO gate |
| schema-verifier | PreToolUse hook blocks raw SQL |

### Optional Agents - Recommended Patterns

| Agent | When to Use |
|-------|-------------|
| validation-agent | CHECK phase for unbiased validation |
| investigation-agent | EXPLORE phase with web research |
| test-runner | Standalone test execution |
| why-capturer | DONE phase learning extraction |
| anti-pattern-checker | Before accepting completion claims |

---

## Agent Definition Structure

```markdown
---
name: agent-name
description: One-line description
tools: Tool1, Tool2, Tool3
generated: 2025-12-25
last_updated: 2025-12-28
---

# Agent Name

[Description and purpose]

## Requirement Level

[REQUIRED/Optional and when]

## Checks Performed

[What the agent validates/does]

## Input

[Expected prompt format]

## Output Format

[Structured output schema]

## Execution

[Step-by-step actions]

## Examples

[Input/Output examples]
```

---

## Subagent vs Skill Decision

| Use Case | Choice | Reason |
|----------|--------|--------|
| Validation that must be unbiased | **Subagent** | Isolated context |
| Multi-phase workflow | **Skill** | Phase orchestration |
| One-shot query/check | **Subagent** | Focused output |
| Memory-integrated work | **Skill** | Full memory access |
| Dangerous operation | **Subagent** | Limited tool access |
| Reusable orchestration | **Skill** | Composable |

---

*Populated Session 151*
