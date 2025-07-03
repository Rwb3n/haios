# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "adr_os_034_md",
        "g_annotation_created": 253,
        "version_tag_of_host_at_annotation": "1.0.0"
    },
    "payload": {
        "description": "Defines the Orchestration Layer and Session Management system for coordinating multi-agent workflows and maintaining conversational context across HAiOS operations.",
        "artifact_type": "DOCUMENTATION",
        "purpose_statement": "To establish a formal orchestration system that manages agent coordination, session state, and workflow execution while providing a unified interface for human operators.",
        "authors_and_contributors": [
            { "g_contribution": 253, "identifier": "Hybrid_AI_OS" },
            { "g_contribution": 250, "identifier": "Third_Party_Architectural_Review" }
        ],
        "internal_dependencies": [
            "adr_os_template_md",
            "adr_os_032_md",
            "adr_os_021_md",
            "adr_os_030_md",
            "3rdpartyeval-10.md",
            "docs/source/roadmaps/phase1_to_2.md"
        ],
        "linked_issue_ids": []
    }
}
# ANNOTATION_BLOCK_END

# ADR-OS-034: Orchestration Layer & Session Management

* **Status**: DEFERRED
* **Date**: 2025-01-28
* **Deciders**: \[List of decision-makers]
* **Reviewed By**: \[List of reviewers]

_ update: While a correct long-term vision, the "Human Gap Analysis" revealed that this is a "Phase 2+" concern. Focusing on it now would be a distraction from the immediate, necessary work of hardening the core engine and improving the solo operator's workflow.
Action: Shelve this ADR for now. Revisit after the "Minimum Viable Foundry" milestone is complete. _

---

## Context

HAiOS currently operates through individual agent interactions without a unified orchestration layer to coordinate multi-agent workflows, maintain conversational context, or provide session continuity. This creates several critical limitations:

1. **No Session Persistence**: Conversational context and work state are lost between interactions
2. **Agent Coordination Gaps**: Multiple agents working on related tasks lack coordination mechanisms
3. **Workflow Fragmentation**: Complex workflows spanning multiple phases lack unified management
4. **Human Interface Inconsistency**: No standardized interface for human operators to monitor and control HAiOS operations
5. **State Management Complexity**: No centralized system for managing distributed state across agents and sessions

The current architecture referenced in `docs/source/roadmaps/phase1_to_2.md` identifies the need for a "Cockpit" interface but lacks the underlying orchestration infrastructure to support comprehensive session management and agent coordination.

Additionally, the existing agent roles defined in ADR-OS-030 (Supervisor, Manager, Executor, etc.) need an orchestration layer to coordinate their interactions effectively and maintain operational coherence across complex, multi-phase workflows.

## Assumptions

* [ ] Session state can be effectively serialized and persisted without losing critical context or creating performance bottlenecks.
* [ ] The orchestration layer can coordinate multiple agents without creating single points of failure or coordination bottlenecks.
* [ ] Workflow definitions can capture sufficient detail to enable automated orchestration while remaining maintainable and understandable.
* [ ] The Cockpit interface can provide meaningful visibility and control without overwhelming operators with excessive detail.
* [ ] Session management can handle concurrent operations and agent coordination without race conditions or state corruption.
* [ ] The orchestration system can integrate with existing HAiOS governance (event tracking, audit trails) without creating architectural conflicts.
* [ ] Workflow recovery and error handling can be implemented effectively within the orchestration framework.
* [ ] The system can scale to handle multiple concurrent sessions and complex multi-agent workflows without performance degradation.
* [ ] Agent communication protocols can be standardized sufficiently to enable reliable orchestration across different agent types.

_This section was expanded to surface implicit assumptions about state management complexity, coordination mechanisms, scalability, and integration challenges._

## Decision

**Decision:**

> We will implement an **Orchestration Layer & Session Management System** that provides unified coordination of multi-agent workflows, persistent session state management, and a standardized interface for human operators to monitor and control HAiOS operations.

### Orchestration Layer Architecture

**Core Components:**

1. **Session Manager**: Maintains persistent session state, context, and conversation history
2. **Workflow Orchestrator**: Coordinates multi-agent workflows based on defined workflow specifications
3. **Agent Coordinator**: Manages agent lifecycle, communication, and resource allocation
4. **Cockpit Interface**: Provides human operators with visibility and control over HAiOS operations
5. **State Synchronizer**: Ensures consistency between distributed agent state and centralized orchestration state

### Session Management System

**Session Structure:**
```json
{
  "session_header": {
    "session_id": "session_[timestamp]_[uuid]",
    "created_g": "global event counter",
    "last_activity_g": "most recent activity",
    "status": "ACTIVE|SUSPENDED|COMPLETED|FAILED",
    "human_operator_id": "operator identification"
  },
  "session_context": {
    "conversation_history": "Complete interaction history",
    "active_workflows": ["workflow_id_1", "workflow_id_2"],
    "agent_assignments": {"agent_id": "current_task_assignment"},
    "shared_state": "Cross-agent shared data and context"
  },
  "session_metadata": {
    "project_context": "Associated project or initiative",
    "priority_level": "HIGH|MEDIUM|LOW",
    "resource_constraints": "Memory, time, cost limitations",
    "checkpoint_frequency": "Auto-save interval"
  }
}
```

**Confidence:** High

## Consequences

* **Positive:**
  - Enables coherent multi-agent workflows with proper coordination
  - Provides persistent session state and work continuity
  - Offers unified human interface for HAiOS operations monitoring and control
  - Improves system reliability through centralized state management and recovery

* **Negative:**
  - Adds architectural complexity with centralized orchestration layer
  - Potential single point of failure if orchestration layer fails
  - Performance overhead from centralized coordination and state management

---

*This template integrates explicit assumption-surfacing, confidence indicators, self-critiques, and clarifying questions as per ADR-OS-021.*
