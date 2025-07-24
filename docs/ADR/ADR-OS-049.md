ADR-OS-049: The Governed Framework Wrapper Protocol
Status: Proposed
Date: 2025-07-17
Deciders: Founding Operator, Genesis Architect
Context: Based on the analysis of the OWL multi-agent framework, this ADR defines the architecture for safely integrating and governing powerful, third-party agentic frameworks within HAiOS.
1. Context
The agentic technology landscape is evolving at an explosive pace. Open-source projects like OWL and ElizaOS, and commercial tools like Claude Code, provide immense, pre-built capabilities for agent orchestration and execution.
It would be a strategic failure for HAiOS to attempt to reinvent these "Hephaestus Engines" from scratch. Our core value proposition is not in building a better agent framework, but in providing the governance, safety, and auditability layer that makes these powerful frameworks enterprise-ready.
However, running untrusted, complex, third-party frameworks within our system presents a major security and architectural challenge. We need a standardized, secure protocol for "wrapping" these external frameworks, allowing us to leverage their power without compromising our own core principles.
2. Models & Frameworks Applied
The "Admiralty" Strategy: This ADR is the ultimate expression of the Admiralty strategy. HAiOS is the admiral's flagship, and this protocol defines the standardized "docking collar" that allows other vessels (external frameworks) to connect to our fleet and receive orders.
Specification-Driven Development (SDD Framework): This is a Foundation Layer architecture. It defines the cross-cutting infrastructure needed to support Implementation Layer agents that might be built using external frameworks.
The "Lethal Trifecta" Mitigation: The entire protocol is designed as a defense-in-depth strategy to break the Lethal Trifecta by enforcing strict boundaries between the external framework and the core HAiOS state.
3. Decision
We will adopt a formal Governed Framework Wrapper Protocol. Any external agentic framework (like OWL) that is to be used within a HAiOS Execution Plan must be run inside this wrapper. The wrapper is a combination of a sandboxed runtime environment and a formal data contract for communication.
The "Napkin Sketch" of the Wrapper Architecture:
Generated code
+-------------------------------------------------------------+
|                HAIOS ORCHESTRATOR (PocketFlow)                |
+------------------------------------┬--------------------------+
                                     |
                                     | 1. Dispatches a Task via A2A Protocol
                                     |
                                     ▼
+------------------------------------┴--------------------------+
|      THE GOVERNED FRAMEWORK WRAPPER (Our "Airlock")           |
+-------------------------------------------------------------+
|                                                             |
|   +-------------------------------------------------------+ |
|   | 3. A2A SERVER ENDPOINT                                | |
|   | - Receives the task, validates against schema.        | |
|   +--------------------------┬----------------------------+ |
|                              |                              |
|                              ▼                              |
|   +--------------------------┴----------------------------+ |
|   | 4. SECURITY SANDBOX (e.g., gVisor, Docker Container)  | |
|   | - Strict network policies (no outbound internet)      | |
|   | - Read-only access to specific input artifacts.       | |
|   | - No access to core HAiOS state files.                | |
|   +--------------------------┬----------------------------+ |
|                              |                              |
|                              | 5. Executes the framework... |
|                              |                              |
|                              ▼                              |
|   +--------------------------┴----------------------------+ |
|   |    EXTERNAL FRAMEWORK (e.g., OWL RolePlaying society) | |
|   +--------------------------┬----------------------------+ |
|                              |                              |
|                              | 6. Framework writes outputs  |
|                              |    to a sandboxed `/outputs` |
|                              |    directory.                |
|                              ▼                              |
|   +--------------------------┴----------------------------+ |
|   | 7. EVIDENCE COLLECTOR                                 | |
|   | - Scans the `/outputs` directory for artifacts.       | |
|   | - Verifies they match the `Test_Specification.yml`.   | |
|   | - Calculates integrity hashes.                        | |
|   +-------------------------------------------------------+ |
|                                                             |
+------------------------------------┬--------------------------+
                                     |
                                     | 8. Returns a formal ValidationReport
                                     |    via the A2A Protocol.
                                     |
                                     ▼
+------------------------------------┴--------------------------+
|                HAIOS ORCHESTRATOR (Receives Result)           |
+-------------------------------------------------------------+
Use code with caution.
Implementation Details
Communication via A2A Protocol: The HAiOS orchestrator will only communicate with a wrapped framework via the formal A2A SDK (ADR-OS-050). The task definition, status updates, and final results must all conform to the A2A schemas. This provides a standardized, secure, and auditable communication channel.
Runtime via Security Sandbox: The external framework must be executed within a hardened security sandbox. The default implementation will be a dedicated, single-use Docker container with:
A minimal base image.
A read-only volume mount for input artifacts (/inputs).
A read-write volume mount for its output (/outputs).
A strict network policy that denies all outbound traffic by default, except to explicitly whitelisted internal services (like a database, if required by the plan).
Governance via Test_Specification.yml: The Execution Plan that commissions the wrapped framework must be accompanied by a Test_Specification.yml. The Evidence Collector component of the wrapper is responsible for running the checks defined in this file against the artifacts in the /outputs directory before signaling that the task is complete.
4. Consequences
Positive:
Enables Massive Leverage: Allows us to safely incorporate the power of entire open-source ecosystems like OWL without having to build them ourselves.
Enhances Security: Provides a robust "airlock" that protects the core HAiOS from potential vulnerabilities or malicious behavior in third-party code.
Enforces HAiOS Governance: It forces external frameworks to operate within our Evidence-Based Development and Certainty Ratchet models, even if they were not designed for it.
Negative:
Performance Overhead: Running frameworks in single-use containers with a formal RPC layer will have higher latency than running them as a native library. This is an accepted trade-off for security and governance.
Integration Complexity: Creating the wrapper and the A2A interface for a new framework is a non-trivial engineering task.