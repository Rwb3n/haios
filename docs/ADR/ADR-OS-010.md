# ADR-OS-010: Constraint Management & Locking Strategy

*   **Status:** Proposed
*   **Date:** 2025-06-09
*   **Context:**
    Autonomous AI agents, while powerful, can exhibit "drift" or "forget" critical project-level constraints over time (e.g., technology choices, architectural patterns, non-negotiable requirements). To ensure long-term project integrity and alignment with strategic decisions, a mechanism is needed to make these constraints durable and explicitly non-mutable by standard agent operations.

*   **Decision:**
    We will implement a **granular data locking strategy** directly within the schemas of our OS Control Files and `EmbeddedAnnotationBlock`s. This will be achieved by adding specific boolean "lock" fields to designated keys or objects.

    The convention for these fields will be:
    *   `_fieldname_locked: true`: For simple key-value pairs (e.g., `_overall_goal_locked`).
    *   `_locked_entry_definition: true`: For objects within an array, locking the *definitional* content of that specific entry.
    *   `_list_immutable: true`: For an array, preventing the addition, removal, or reordering of its items.
    *   `_locked_object_definition: true`: For a sub-object, locking its key structure and the values of its definitional fields.

    An AI agent **MUST** check for the presence and `true` value of these lock fields before attempting any modification. If a locked item is encountered and the task requires its modification, the agent **MUST NOT** proceed. Instead, it must log a `BLOCKER` `Issue` and set its current task `status` to `BLOCKED`, signaling the need for explicit human/supervisor override.

*   **Rationale:**
    *   **Enforces Architectural Integrity:** Provides a direct, machine-readable mechanism to protect foundational decisions (e.g., "Use shadcn/ui," "This stage is non-negotiable") from being inadvertently changed by a subordinate agent.
    *   **Durable, Proximate Constraints:** Placing the lock directly on the data it protects makes the constraint explicit and co-located with the context. An agent examining an artifact's annotation immediately knows which parts are fixed.
    *   **Clear Override Path:** The "log issue and block" behavior creates a formal, auditable process for overriding locked constraints. An override is not a simple bypass but requires a new `Request` and a conscious decision from a higher-level authority.
    *   **Reduces "AI Hallucination" Impact:** Prevents an agent from creatively "refactoring" a core component into a non-compliant state because it hallucinated a new requirement or forgot an old one.

*   **Implementation Areas:**
    This locking mechanism will be applied selectively across various schemas, including but not limited to:
    *   **`init_plan_*.txt`:** Locking the `overall_goal`, `quality_acceptance_criteria`, and the structure of `initiative_lifecycle_stages` after they are approved.
    *   **`exec_plan_*.txt`:** Locking the `plan_type`, `goal`, and the core definitions of `tasks` and their `execution_checklist`s once the plan is finalized and ready for `CONSTRUCT`.
    *   **`EmbeddedAnnotationBlock`:** Locking critical `requisites_and_assumptions`, key `external_dependencies`, `scaffold_info` structure, and the definitions within `test_plan_notes_from_scaffold`.

*   **The Locking Lifecycle:**
    1.  **Creation:** Artifacts are often created in a "DRAFT" or unlocked state.
    2.  **Review/Critique:** During review (e.g., by a `CRITIQUE_AGENT` or human supervisor), the decision is made on what to lock.
    3.  **Locking:** An explicit OS action (triggered by plan completion or a specific `Request`) sets the relevant `_locked*` flags to `true`. This action is logged.
    4.  **Enforcement:** The locks are now active for all subsequent agent interactions.
    5.  **Override (Exception):** A `BLOCKER` issue is raised by an agent. A user/supervisor provides a new `Request` explicitly authorizing the change. An OS action then temporarily bypasses or permanently removes the lock to apply the change, logging this override in a `decision_log`.

*   **Consequences:**
    *   **Pros:**
        *   Provides strong guardrails for autonomous agents.
        *   Makes project constraints explicit and machine-readable.
        *   Creates a formal process for high-stakes changes.
    *   **Cons:**
        *   Adds complexity to the schemas and the AI agent's operational logic (must always check for locks).
        *   Can introduce rigidity if not applied judiciously. The default state for most fields should be unlocked.

*   **Alternatives Considered:**
    *   **Role-Based Access Control (RBAC):** Defining that only certain agent personas can edit certain fields. This is a complementary, not mutually exclusive, idea. Our `_locked*` flag is a data-centric constraint, while RBAC is an agent-centric one. Using both could be powerful in a more mature system.
    *   **Constraints in a Single Global File:** Having one file list all locked paths. Rejected as it decouples the constraint from the data it protects, making it harder for an agent to be contextually aware of the lock.