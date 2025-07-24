ADR-OS-050: A2A Protocol Adoption for Inter-Agent Communication
Status: Proposed
Date: 2025-07-17
Deciders: Founding Operator, Genesis Architect
Context: Based on the analysis of the A2A Python SDK, this ADR establishes the official communication standard for all HAiOS services and agents.
1. Context
As the HAiOS ecosystem grows from a single, monolithic script into a distributed system of specialized agents and services (e.g., 2A Orchestrator, Rhiza, Plan Validation Gateway, Vertical MCPs), the need for a standardized, robust communication protocol becomes critical.
Relying on ad-hoc communication methods (like direct HTTP calls with custom JSON payloads or simple file-based signaling) is not scalable, secure, or maintainable. This approach leads to:
Tight Coupling: Services become tightly bound to each other's specific API implementations.
Brittle Integrations: A minor change in one service can break another.
Duplicated Effort: Each new service requires boilerplate code for handling requests, errors, and data serialization.
Lack of Interoperability: Our system would be an isolated island, unable to easily communicate with the broader, emerging agentic ecosystem.
The discovery of the open-source Agent-to-Agent (A2A) Communication Protocol and its associated SDK provides a mature, feature-complete solution to this problem.
2. Models & Frameworks Applied
Protocol-First Architecture (from "Asymmetric Leverage" analysis): By adopting an open standard, we position HAiOS to be a key player in the interoperable agentic web, rather than a closed, proprietary system.
Specification-Driven Development (SDD Framework): The A2A protocol provides the formal Bridge Layer specification for all communication. The A2A SDK provides the Foundation Layer implementation that our Implementation Layer agents will build upon.
Separation of Concerns: A2A cleanly separates the transport of information from the business logic of the agents themselves.
3. Decision
Protocol Adoption: The Agent-to-Agent (A2A) Communication Protocol is hereby adopted as the exclusive, mandatory standard for all asynchronous and synchronous service-to-service and agent-to-agent communication within the HAiOS ecosystem.
Schema Canonization: Our internal, custom data models for tasks and messages (e.g., the Turn Artifact) are now SUPERSEDED. We will adopt the official A2A schemas (Task, Message, Artifact, AgentCard, etc.) as the canonical types for these concepts.
SDK Adoption: The official a2a-sdk (or language-equivalent implementations) will be the standard library used to build and interact with A2A-compliant services.
The "Napkin Sketch" of the A2A-Powered HAiOS:
Generated code
+------------------------------------+      +------------------------------------+
|      HAIOS ORCHESTRATOR            |      |      RHIZA AGENT SERVICE           |
| (e.g., PocketFlow graph)         |      | (A2A-compliant server)           |
+------------------------------------+      +------------------------------------+
|                                    |      |                                    |
| - Uses `A2A Client` to create a    |      | - Built using `A2A Server` framework.|
|   `Task` object.                   |<---->| - Implements handlers like         |
|                                    | A2A  |   `on_get_task`.                   |
| - Sends `CreateTaskRequest`        | Proto|                                    |
|                                    |      |                                    |
+------------------------------------+      +------------------------------------+
                 ^
                 |
                 | All communication is a formal,
                 | typed, and auditable RPC call,
                 | not an ad-hoc HTTP request.
                 |
                 v
+------------------------------------+      +------------------------------------+
|      PLAN VALIDATION GATEWAY       |      |      VERTICAL MCP SERVER           |
| (A2A-compliant server)           |      | (A2A-compliant server)           |
+------------------------------------+      +------------------------------------+
Use code with caution.
4. Consequences
Positive:
Massive Acceleration: Saves us thousands of hours of work by providing a pre-built, battle-tested client-server framework for agentic communication.
Instant Interoperability: Any service we build is instantly compatible with any other tool or agent that speaks the A2A protocol.
Robustness & Reliability: We inherit a mature system with features like typed objects, error handling, and support for multiple transport layers (JSON-RPC, gRPC).
Architectural Clarity: Provides a clear, unambiguous "lingua franca" for our entire distributed system.
Negative:
External Dependency: We are now dependent on the A2A open-source project. We must be prepared to contribute to it or fork it if its direction diverges from our needs.
Requires Refactoring: Our current, simple prototypes (2A Orchestrator, etc.) must be refactored to use this more formal client-server model. This is an accepted and necessary cost.
5. Integration Plan
ADR-OS-042 (Vertical MCPs): Must be updated to state that all HAiOS-generated Vertical MCPs must expose an A2A-compliant endpoint.
Rhiza MVF: The blueprint must be updated. The Python adapters will be re-written as standalone A2A microservices. The n8n or PocketFlow orchestrator will be the A2A Client that calls them.
2A System: The v1.3+ refactor will move from a simple script to a model where the orchestrator is a client that makes A2A calls to a "Claude Code A2A Server," which in turn uses the claude-code-sdk.