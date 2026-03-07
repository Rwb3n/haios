# HAIOS Architecture Remediation Roadmap

Based on the architectural gaps identified in Epoch 2.8, the following roadmap aligns the necessary fixes with the existing project trajectory, specifically targeting the upcoming **Epoch 2.9 (Governance)** and **Epoch 3 (TBD/SDK Migration)**.

---

## Phase 1: Securing the Foundations (Target: Epoch 2.9)
*Epoch 2.9 is explicitly defined as the final "infrastructure" epoch focused on Governance. This makes it the imperative landing zone for patching the "Trust Ratchet" enforcement leaks.*

### 1.1 Strictly Enforce Ceremony Gates
- **Objective**: Stop agents from bypassing lifecycle phases (e.g., entering `DO` without completing `PLAN`).
- **Action**: Modify `.claude/haios/config/haios.yaml`. Change `ceremony_contract_enforcement` and `ceremony_context_enforcement` from `warn` to `block`.
- **Validation**: Attempt to trigger a `PreToolUse` hook to write a code file while a `WORK.md` item is still in the `PLAN` state. The hook must reject the tool call.

### 1.2 Implement the SQL Hard Gate
- **Objective**: Prevent brittle, raw bash `sqlite3` queries that bypass the abstraction layer.
- **Action**: In `haios.yaml`, uncomment the `# block_sql: true` directive. Ensure the `PreToolUse` hook actively scans for and rejects raw SQL bash executions.
- **Validation**: Instruct the Main Agent to run `sqlite3 haios_memory.db "SELECT * FROM entities"`. The execution must be blocked with an instruction to use the MCP `db_query` tool instead.

### 1.3 Deploy the Validator Agent
- **Objective**: Automate the `CHECK` phase of the Independent Lifecycle.
- **Action**: Complete pending queue item `TD-002`. Integrate `validation-agent.md` into the workflow so it is mandatorily triggered before a work item can transition to `DONE`.

---

## Phase 2: Upgrading Cognitive Memory & Context Injection (Target: Late Epoch 2.9 / Early E3)
*Before E3 pivots towards Autonomy or SDK Migration, the Memory engine must shift from hoarding logs to providing high-signal intelligence, and leverage advanced Claude features for context.*

### 2.1 Refactor ReasoningBank Extraction
- **Objective**: Stop storing raw execution traces. Start storing distilled, transferable strategies.
- **Action**: Update `haios_etl/extraction.py` (specifically `extract_strategy()`). Alter the LLM prompt to heavily penalize logging "what happened" and fiercely mandate extracting "what was learned" (a reusable `{title, description}` strategy).
- **Validation**: Run a known failing command sequence. Inspect the `reasoning_traces` SQLite table to verify the output is a preventative strategy rule, not a chronological log of the failure.

### 2.2 Dynamic Relevance Retrieval & Skill Context Injection
- **Objective**: Maximize token efficiency during context injection and leverage new Claude capabilities.
- **Action**: 
  - Update `haios_etl/retrieval.py` to replace hardcoded `0.8` similarity cutoffs with dynamic Top-K relative semantic matching clustering.
  - Refactor CLI skills to use the `!` dynamic context injection syntax (e.g., `` - PR diff: !`gh pr diff` ``) to offload bash script pre-fetching where applicable.

---

## Phase 3: Project Foreman & Headless Orchestration (Target: Epoch 3 Candidates)
*Epoch 3 is currently debating between SDK Migration, Autonomy, or Product Portability. These fixes directly support the "Autonomy" and "SDK Migration" themes by leveraging Claude's native sub-agents and Headless SDK.*

### 3.1 Build the Project Foreman using Native Sub-agents
- **Objective**: Automate work delegation natively extending Claude's `agent:` routing capabilities.
- **Action**: 
  - Draft the `.claude/agents/project-foreman.md` identity file. 
  - Update `hook_dispatcher.py` to support the `SubagentStart` and `SubagentStop` hook events. Use these hooks to intercept a sub-agent's initialization and dynamically inject the `docs/work/active/WORK-XXX` backlog.
  - Convert heavy investigative CLI skills to run explicitly under the `agent: Explore` context so they don't corrupt the main conversational context.

### 3.2 Migrate to Headless SDK architecture
- **Objective**: Allow robust programmatic control of Claude (Option A in Epoch 3 Vision).
- **Action**: Re-write `cli.py` batch commands (ingest, synthesize) to spawn headless `claude` instances programmatically via the Agent SDK, utilizing the `--output-format json` and structured output schema flags for resilient data extraction.
- **Validation**: Run a batch ingestion script which spins up a background agent, correctly parses the structured JSON output, and shuts down without polluting a user-facing terminal.

---

## Next Steps
This roadmap should be submitted as a formal `CH-NNN-Architecture-Remediation` Chapter document within the Epoch 2.9 (Governance) hierarchy for operator approval. Once approved, the items in Phase 1 can be immediately triaged into active `WORK` items.
