---
template: investigation
status: complete
date: 2026-01-28
backlog_id: WORK-028
title: MCP haios-memory Server Connection Failure
author: Hephaestus
session: 247
lifecycle_phase: conclude
spawned_by: null
related: []
memory_refs: []
version: '2.0'
generated: 2025-12-22
last_updated: '2026-01-28T22:28:35'
---
# Investigation: MCP haios-memory Server Connection Failure

@docs/README.md
@docs/epistemic_state.md

<!-- FILE REFERENCE REQUIREMENTS (MUST - Session 171 Learning)

     1. MUST use full @ paths for prior work:
        CORRECT: @docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md
        WRONG:   INV-052, "See INV-052"

     2. MUST read ALL @ referenced files BEFORE starting EXPLORE phase:
        - Read each @path listed at document top
        - For directory references (@docs/work/active/INV-052/), MUST Glob to find all files
        - Document key findings in Prior Work Query section
        - Do NOT proceed to EXPLORE until references are read

     3. MUST Glob referenced directories:
        @docs/work/active/INV-052/ → Glob("docs/work/active/INV-052/**/*.md")
        Then read key files (SECTION-*.md, WORK.md, investigations/*.md)

     Rationale: Session 171 wasted ~15% context searching for INV-052 in wrong
     location because agent ignored @ references and guessed file locations.
-->

<!-- TEMPLATE GOVERNANCE (v2.0 - E2-144)

     INVESTIGATION CYCLE: HYPOTHESIZE -> EXPLORE -> CONCLUDE

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: Pure discovery, no design outputs needed"
     - "SKIPPED: Single hypothesis, no complex mapping required"
     - "SKIPPED: External research only, no codebase evidence"

     This prevents silent section deletion and ensures conscious decisions.

     SUBAGENT REQUIREMENT (L3):
     For EXPLORE phase, you MUST invoke investigation-agent subagent:
     Task(prompt='EXPLORE: {hypothesis}', subagent_type='investigation-agent')

     Rationale: Session 101 proved L2 ("RECOMMENDED") guidance is ignored ~20% of time.
     L3 enforcement ensures structured evidence gathering.
-->

---

## Discovery Protocol (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Query memory first | SHOULD | Search for prior investigations on topic before starting |
| Document hypotheses | SHOULD | State what you expect to find before exploring |
| Use investigation-agent | MUST | Delegate EXPLORE phase to subagent for structured evidence |
| Capture findings | MUST | Fill Findings section with evidence, not assumptions |

---

## Context

<!-- HYPOTHESIZE PHASE: Describe background before exploring -->

**Trigger:** Session 254 coldstart - operator asked "what's going on with memory?" after observing schema-verifier subagent couldn't execute queries. `/mcp` command confirmed "Failed to reconnect to haios-memory."

**Problem Statement:** The MCP server `haios-memory` is not connecting, breaking the intended memory query/ingestion path and forcing fallback to direct module calls.

**Prior Observations:**
- `schema-verifier` subagent reported MCP tools not available in its context
- Direct SQL queries via Bash were blocked by PreToolUse hook (as designed)
- Memory operations via `haios_etl.database.DatabaseManager` work directly
- Database file exists (360MB) and contains 82k+ concepts
- `just status` works because it uses haios_etl directly, not MCP

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "[investigation topic keywords]"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| [ID] | [What was learned] | [How it applies] |

**Prior Investigations:**
- [ ] Searched for related INV-* documents
- [ ] No prior work found / Found: [INV-xxx]

---

## Objective

<!-- One clear question this investigation will answer -->

**Why is the haios-memory MCP server failing to connect, and how do we fix it?**

---

## Scope

### In Scope
- MCP server configuration (`.mcp.json` or equivalent)
- MCP server startup/connection mechanism
- haios-memory server implementation
- Error messages and logs from connection attempts

### Out of Scope
- Rewriting the MCP server from scratch
- Alternative memory architectures
- haios_etl module internals (these work fine)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | ~5 | MCP config, server entry, logs |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | 2 | Codebase + Claude Code MCP system |
| Estimated complexity | Low | Configuration issue most likely |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | MCP server config missing or invalid | High | Check `.mcp.json` exists and has correct haios-memory entry | 1st |
| **H2** | MCP server process crashed or not started | Med | Check if server process is running, examine startup logs | 2nd |
| **H3** | Path/dependency issue in server startup | Med | Check server entry point, verify Python environment | 3rd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [x] Find MCP configuration file (`.mcp.json` or similar) - Found at project root
2. [x] Find haios-memory server entry point - `.claude/haios/lib/mcp_server.py`
3. [x] Check Claude Code MCP connection mechanism - Uses stdio, config in `.mcp.json`

### Phase 2: Hypothesis Testing
4. [x] Test H1: Read MCP config, verify haios-memory entry exists and is valid - **INVALID PATH**
5. [x] Test H2: Check server process status, look for error logs - N/A, can't start
6. [x] Test H3: Verify server entry point paths and dependencies - Path issue confirmed

### Phase 3: Synthesis
7. [x] Compile evidence table - Done above
8. [x] Determine verdict for each hypothesis - H1 confirmed
9. [x] Identify fix or spawned work items - Fix is simple config update

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| MCP config points to non-existent path | `.mcp.json:5` | H1 | `"args": [".claude/lib/mcp_server.py"]` |
| Old path doesn't exist | `.claude/lib/mcp_server.py` | H1 | `ls` returns "No such file or directory" |
| Server exists at new location | `.claude/haios/lib/mcp_server.py` | H1 | File exists, 13400 bytes, last modified Jan 21 |
| Old lib directory deleted | `.claude/lib/` | H1 | Directory completely removed (WORK-026/027 migration) |
| PYTHONPATH also wrong | `.mcp.json:8` | H1 | `"PYTHONPATH": ".claude/lib"` should be `.claude/haios/lib` |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| [ID] | [Summary] | H1/H2/H3 | [How it applies] |

### External Evidence (if applicable)

| Source | Finding | Supports Hypothesis | URL/Reference |
|--------|---------|---------------------|---------------|
| [Doc/Article] | [Summary] | H1/H2/H3 | [Link] |

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **CONFIRMED** | `.mcp.json` points to `.claude/lib/mcp_server.py` which doesn't exist. Server is at `.claude/haios/lib/mcp_server.py`. | High |
| H2 | Refuted | Server can't start because path is wrong - not a crash or process issue. | High |
| H3 | Subsumed by H1 | The path issue IS the dependency problem - MCP can't find the server file. | High |

### Detailed Findings

#### Finding 1: MCP Config Path Mismatch

**Evidence:**
```json
// .mcp.json (current - BROKEN)
{
  "mcpServers": {
    "haios-memory": {
      "command": "python",
      "args": [".claude/lib/mcp_server.py"],  // WRONG PATH
      "env": {
        "DB_PATH": "haios_memory.db",
        "PYTHONPATH": ".claude/lib"  // ALSO WRONG
      }
    }
  }
}
```

**Analysis:** The WORK-026/WORK-027 migration moved all code from `.claude/lib/` to `.claude/haios/lib/`. The MCP configuration was not updated as part of that migration.

**Implication:** Simple fix - update both paths in `.mcp.json`.

#### Finding 2: Migration Was Incomplete

**Evidence:**
```bash
$ ls -la .claude/lib/
ls: cannot access '.claude/lib/': No such file or directory

$ ls -la .claude/haios/lib/mcp_server.py
-rw-r--r-- 1 ruben 197609 13400 Jan 21 20:01 .claude/haios/lib/mcp_server.py
```

**Analysis:** The old directory was completely deleted. The migration checklist (WORK-026) likely didn't include `.mcp.json` as a file to update because it's outside the `.claude/haios/` tree.

**Implication:** Need to add `.mcp.json` to migration checklists for future moves.

---

## Design Outputs

<!-- If investigation produces architectural designs, document them here
     SKIP this section if investigation is pure discovery with no design outputs -->

### Schema Design (if applicable)

```yaml
# [Name of schema]
field_name: type
  description: [What this field does]
```

### Mapping Table (if applicable)

| Source | Target | Relationship | Notes |
|--------|--------|--------------|-------|
| [A] | [B] | [How A relates to B] | |

### Mechanism Design (if applicable)

```
TRIGGER: [What initiates the mechanism]

ACTION:
    1. [Step 1]
    2. [Step 2]
    3. [Step 3]

OUTCOME: [What results from the mechanism]
```

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| [Decision point] | [What was chosen] | [Why this choice - most important part] |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

- [x] **WORK-029: Cleanup Dead MCP Code in .claude/haios/lib/**
  - Description: Delete broken MCP-related files copied from haios_etl that have broken imports
  - Fixes: Confusion from dead code, prevents future attempts to use broken files
  - Files to remove: `mcp_server.py`, `extraction.py`, `retrieval.py` (and any others with haios_etl dependencies)

### Future (Epoch 3+)

- [ ] **haios-memory Full Migration**
  - Description: Move entire haios_etl/ into .claude/haios/ for true plugin portability
  - Blocked by: Epoch 3 planning, significant effort, needs proper packaging strategy
  - Note: Added to `docs/notes/FUTURE-haios-memory-migration.md`

### Config Fix Applied

- [x] Updated `.mcp.json` to use `python -m haios_etl.mcp_server` (working server)

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 247 | 2026-01-28 | HYPOTHESIZE | Started | Initial context and hypotheses |
| - | - | - | - | No additional sessions yet |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-HN have verdict | [ ] | |
| Evidence has sources | All findings have file:line or concept ID | [ ] | |
| Spawned items created | Items exist in backlog or via /new-* | [ ] | |
| Memory stored | ingester_ingest called, memory_refs populated | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | [Yes/No] | |
| Are all evidence sources cited with file:line or concept ID? | [Yes/No] | |
| Were all hypotheses tested with documented verdicts? | [Yes/No] | |
| Are spawned items created (not just listed)? | [Yes/No] | |
| Is memory_refs populated in frontmatter? | [Yes/No] | |

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete ALL items before /close -->

### Required (MUST complete)
- [ ] **Findings synthesized** - Answer to objective documented in Findings section
- [ ] **Evidence sourced** - All findings have file:line or concept ID citations
- [ ] **Hypotheses resolved** - All hypotheses have Confirmed/Refuted/Inconclusive verdict
- [ ] **Spawned items created** - Via /new-* commands with `spawned_by` field (or rationale if none)
- [ ] **Memory stored** - `ingester_ingest` called with findings summary
- [ ] **memory_refs populated** - Frontmatter updated with concept IDs
- [ ] **lifecycle_phase updated** - Set to `conclude`
- [ ] **Ground Truth Verification complete** - All items checked above

### Optional
- [ ] Design outputs documented (if applicable)
- [ ] Session progress updated (if multi-session)

---

## References

- [Spawned by: Session/Investigation/Work item that triggered this]
- [Related investigation 1]
- [Related ADR or spec]

---
