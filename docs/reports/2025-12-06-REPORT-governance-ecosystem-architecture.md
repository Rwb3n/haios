# Governance Ecosystem Architecture Report
> **Date:** 2025-12-06
> **Status:** Final
> **Author:** Genesis (Gemini)
> **Context:** Response to `docs/handoff/2025-12-06-INQUIRY-governance-ecosystem-analysis.md`

## 1. Executive Summary
This specific analysis explores how Claude Code's extensibility features (Hooks, Skills, Marketplace, etc.) can be layered onto the established **File-Based Epoch Architecture** to create a robust, self-reinforcing governance flywheel.

**Key Finding:** While the file-based foundation is solid, the "active" governance layer is currently under-leveraged. We are using Hooks for reactive enforcement, but we are missing opportunities to use **Marketplaces for alignment distribution**, **Subagents for role enforcement**, and **Skills for standardized governance procedures**.

**Recommendation:** Shift from "Governance by Document" to "Governance by Ecosystem," where the environment itself actively guides, constrains, and facilitates compliant behavior.

---

## 2. Capability Matrix

| Extensibility Point | Governance Function | Current Usage (Status) | Gap Analysis |
| :--- | :--- | :--- | :--- |
| **1. Hooks** (`HOOKS-REF`) | **Policy Enforcement:** Blocking actions, validating output, enforcing lifecycle steps (e.g., "Must read TRD before coding"). | **High:** `PostToolUse`, `UserPromptSubmit`, `Stop`, `ValidateTemplate`. | Well-utilized for reactive checks. Could be enhanced for *proactive* context injection (e.g., injecting rules into context on start). |
| **2. Skills** (`SKILLS-REF`) | **Standardized Procedures:** Encapsulating complex governance workflows (e.g., "Conduct Impact Analysis") into reusable units. | **Medium:** `extract-content`, `memory-agent`. | Governance workflows (e.g., TRD creation, Audit) are manual. They should be Skills. |
| **3. Marketplace** (`MARKETPLACE-REF`) | **Policy Distribution:** The "App Store" for governance. Distributing approved Agents, Skills, and Rule sets to new projects. | **None:** No local or remote marketplace configured. | **Critical Gap.** No mechanism to update governance rules across multiple workspaces/agents efficiently. |
| **4. Subagents** (`SUBAGENTS-REF`) | **Role Separation:** Enforcing "Separation of Duties" by switching context/tools for different modes (Planner vs. Builder). | **Medium:** `The-Proposer`, `The-Adversary`. | Agents are defined but not rigorously integrated into the *flow*. We need automatic handoff to specific subagents for specific Epoch phases. |
| **5. Plugins** (`PLUGINS-REF`) | **Governance Bundles:** Packaging Hooks, Skills, and Agents into a single installable "Governance Suite". | **None.** | **Strategic Opportunity.** We should package the "HAIOS Governance Stack" as a single Plugin for easy deployment. |
| **6. Commands** (`COMMANDS-REF`) | **On-Demand Audits:** Quick slash-commands for governance actions (e.g., `/audit`, `/status`, `/handover`). | **None.** | Gaps in developer experience. Governance checks are currently manual script executions rather than native commands. |
| **7. MCP** (`MCP-REF`) | **System of Record:** Providing authorized, read/write access to the "State" (Memory DB, Project Tracker). | **High:** `haios-memory`. | Good foundation. Needs visualization/querying tools exposed via MCP for the Auditor role. |
| **8. SDK** (`SDK-REF`) | **Custom Shells:** Building entirely custom interfaces for specialized roles (e.g., a "Validator Shell" that only allows testing). | **Low:** Implicit use in scripts. | Overkill for effective governance right now. Stick to lower-hanging fruit (Hooks/Skills). |
| **9. Tools** (`TOOLS-REF`) | **Granular Capabilities:** Defining the atomic actions agents can take. | **High:** Core functionality. | Governance-specific tools (e.g., `verify_adr_compliance`) are missing. |

---

## 3. Governance Architecture: The 4-Layer Stack

To maximize governance effectiveness, we propose layering these capabilities atop the File-Based Epoch Foundation.

### Layer 1: The Foundation (State)
*   **Mechanism:** **File-Based Epochs** (`checks/`, `docs/`, `memory.db`).
*   **Role:** The single source of truth. Immutable history, current state, and future plan.
*   **Integration:** All other layers read/write to this layer.

### Layer 2: The Guardrails (Enforcement)
*   **Mechanism:** **Hooks** (`PreToolUse`, `PostToolUse`, `ValidationAlertHook`).
*   **Role:** The "Editor." Prevents invalid state transitions.
    *   *Example:* A `PreToolUse` hook prevents `write_to_file` if the target file is a `TRD` and the user hasn't explicitly run a `scan_related_adrs` tool first.
    *   *Example:* A `PostToolUse` hook triggers `ValidateTemplate.ps1` immediately after a markdown file is saved.

### Layer 3: The Toolkit (Capabilities)
*   **Mechanism:** **Skills** (`skills/create-trd`, `skills/conduct-audit`) & **Commands** (`/audit`, `/handoff`).
*   **Role:** The "Guide." Makes doing the *right* thing the *easiest* thing.
    *   *Example:* Instead of manually prompting "Check for compliance," the agent runs `/audit`, triggering the `conduct-audit` Skill which follows a rigorous 10-step checklist.

### Layer 4: The Orchestra (Roles)
*   **Mechanism:** **Subagents** (`@Auditor`, `@Architect`, `@Builder`) & **Marketplace**.
*   **Role:** The "Team." Enforces separation of concerns.
    *   *Example:* The `@Architect` subagent has tools to write TRDs but *cannot* write code. The `@Builder` subagent has tools to write code but *cannot* modify TRDs without `@Architect` approval (simulated via file permissions or hook logic).
    *   *Distribution:* The entire configuration (Agents + Skills + Hooks) is versioned and distributed via a **Local Marketplace**, ensuring all projects stay in sync.

---

## 4. Strategic Recommendations

### Batch A (Immediate: Epoch 2)
*   **Focus:** **Enforcement & Ease of Use.**
*   **Actions:**
    1.  **Commands:** Create `/audit` and `/validate` slash commands that map to existing PowerShell scripts (`ValidateTemplate.ps1`). This reduces friction.
    2.  **Hooks:** Implement a `PreToolUse` hook for **Context Awareness**. If an agent opens a `TRD`, automatically inject the `ADR` index into the context window.
    3.  **Skills:** Package the "Reasoning Extraction" logic (`reasoning_extraction.py`) into a formal Skill so it can be invoked on-demand, not just at `Stop`.

### Batch B (Next: Epoch 3)
*   **Focus:** **Role Definition & Distribution.**
*   **Actions:**
    1.  **Subagents:** Formally define `@Hephaestus` (Builder) and `@Genesis` (Architect) as Claude Subagents with distinct tool permissions in `.claude/agents/`.
    2.  **Plugin:** Package the core governance scripts (`ValidateTemplate`, etc.) into a `haios-governance` plugin.
    3.  **Marketplace:** Establish a local marketplace repo to host this plugin, testing the "Update Loop" (updating the plugin updates the governance rules).

### Batch C (Future)
*   **Focus:** **Advanced Customization.**
*   **Actions:**
    1.  **SDK:** Build a "Governance Dashboard" TUI using the SDK that visualizes Epoch status and active risks in real-time.

---

## 5. Quick Wins (Low Effort / High Value)

1.  **Slash Command for Validation:**
    *   *Action:* Create `.claude/commands/validate.md`.
    *   *Content:* Invokes `ValidateTemplate.ps1` and summarizes output.
    *   *Value:* Makes validation one click/keystroke away.

2.  **"Read-First" Hook:**
    *   *Action:* Create a `PreToolUse` hook.
    *   *Logic:* If target is `*.py`, check if `TRD-*.md` has been read in the last 10 turns. If not, warn the agent.
    *   *Value:* Enforces "Spec-First" coding.

3.  **Governance Skill:**
    *   *Action:* Create `.claude/skills/governance/SKILL.md`.
    *   *Content:* Defines the "Update Epoch" procedure (Update Task -> Update Epistemic State -> Update Checkpoint).
    *   *Value:* Standardizes the most frequent governance loop.

## 6. Evolution Roadmap & Risks

*   **Bet on:** **MCP** and **Skills**. These seem to be the core primitives Anthropic is doubling down on. They are portable and composable.
*   **Watch:** **Subagents**. The feature is powerful but the "Context Handoff" cost (latency + loss of ephemeral context) needs to be managed carefully. Use them for *distinct phases* (Architecture vs. Coding), not rapid switching.
*   **Avoid:** Over-customizing via **SDK** for now. It increases maintenance burden. Use the standard client with configuration (Hooks/Plugins) as far as possible.

### Conclusion
The **File-Based Epoch Architecture** provides the "Law." The **Claude Ecosystem (Hooks, Skills, Agents)** provides the "Police" and the "Civil Services." Integrating them transforms HAIOS from a passive repository of documents into an active, self-governing intelligence system.
