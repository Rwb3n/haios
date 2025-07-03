ADR-OS-042: The HAiOS Vertical MCP Server Architecture
Status: DRAFT
Date: 2025-07-11
Deciders: Founding Operator, Genesis Architect
Referenced Research: "MCPs: Value Creation, Capture, and Destruction" (Xiao, Wu, Zhao)
1. Context
The HAiOS strategy is to create durable value by enabling the creation of specialized, high-margin AI integrations, rather than competing in the commoditized layer of generic agent execution. Market analysis indicates that the most defensible assets in the emerging agentic economy will be Vertical Model Context Protocol (MCP) Servers. These servers act as the compliant, secure, and domain-aware interface between AI agents and complex enterprise systems (e.g., EHRs, financial trading systems, legal case management software).
The "moat is in the mess." Value is not in the protocol syntax, but in the server's ability to handle complex compliance, security, and business logic. HAiOS requires a standard, repeatable, and governable architecture for building, deploying, and managing these Vertical MCP Servers. This ADR defines that architecture.
2. Assumptions
The open MCP standard will be the dominant protocol for agent-service interaction.
The primary value (and risk) of a Vertical MCP is in its embedded governance logic, not its external interface.
[a] A modular, plug-in based architecture is the most effective way to handle diverse domain-specific requirements (compliance, data transformation, etc.).
The performance overhead of the proposed Governance Core is acceptable for mission-critical, high-compliance workflows.
Each Vertical MCP Server built with this architecture will be a first-class HAiOS artifact, subject to the full lifecycle of planning, validation, and monitoring.
3. Decision
We will adopt a standardized, three-layer architecture for all HAiOS-generated Vertical MCP Servers. This architecture is designed to separate the concerns of protocol compliance, domain-specific governance, and backend integration.
The Three-Layer Architecture
Interface Layer (The Protocol Endpoint):
Purpose: To handle all communication with the outside world and ensure strict compliance with the open MCP standard.
Components: A lightweight web server that exposes the standard MCP endpoints for tool discovery, command parsing, and response formatting.
Responsibility: This layer is "dumb" by design. Its only job is to translate incoming agent requests into a standardized internal format and pass them to the Governance Core. It handles protocol-level concerns like authentication and request validation.
Governance Core (The "Moat"):
Purpose: This is the heart of the Vertical MCP Server. It enforces all the complex, domain-specific rules that make the server valuable and defensible.
Components: A pipeline of pluggable, mandatory modules that every request must pass through.
Compliance Module: A rules engine (e.g., powered by OPA/Rego) that enforces regulatory policies (e.g., "An agent with role 'nurse' cannot access billing information"). The policies are themselves version-controlled HAiOS artifacts.
Data Transformation & Masking Module: A pipeline for securely handling data. It performs actions like PII scrubbing, de-identification of patient data, or formatting data to meet specific legal standards before it is passed to the agent or the backend.
Transactional Integrity Module: A saga or two-phase commit coordinator that ensures multi-step business processes (e.g., "admit patient, assign bed, notify doctor") are executed atomically. It manages compensation logic for failures.
Domain Logic Module: The plug-in for custom, non-compliant business rules (e.g., "This type of trade can only be executed between 9:30 AM and 4:00 PM EST").
Immutable Audit Module: A dedicated logger that writes every action, policy decision, and data transformation to a secure, append-only audit log, separate from standard application logs. This is the evidence for auditors.
Backend Integration Layer (The Adapters):
Purpose: To translate the validated, secure, and compliant commands from the Governance Core into actions on the actual backend system(s).
Components: A collection of source-specific adapters (e.g., an Epic_EHR_Adapter, a Salesforce_Adapter, a FIX_Protocol_Adapter).
Responsibility: This layer handles the "last mile" of integration, dealing with the specific quirks of the target system's API or database schema.
4. HAiOS Governance Integration
As an Artifact: The entire codebase and configuration for a Vertical MCP Server is an HAiOS-managed project.
Blueprint & Validation: The design of its Governance Core policies is a BLUEPRINT task. The Plan Validation Gateway must verify that the policies are logical and do not contain loopholes.
Runtime Monitoring: A running Vertical MCP Server is monitored by the Argus Protocol. An unusual spike in Compliance Module rejections or Transactional Integrity rollbacks would trigger an anomaly alert.
5. Consequences
Positive:
Provides a standardized, repeatable blueprint for building high-value, defensible AI integrations.
Enforces security, compliance, and auditability by design, dramatically de-risking the use of AI agents in regulated industries.
Perfectly aligns the HAiOS's technical capabilities with a validated, high-margin market opportunity.
Negative:
This is a highly structured and "heavy" architecture compared to a simple API wrapper. It is intentionally not suited for building generic, low-compliance connectors.
Requires significant domain expertise to correctly implement the policies for the Governance Core.
6. Clarifying Questions
What specific technology stack (e.g., OPA, specific data masking libraries) will be the "recommended default" for the Governance Core modules?
How will the schemas for the pluggable modules be defined and versioned?
What is the standard testing methodology for validating the complex logic within the Governance Core?
How will HAiOS manage the lifecycle of the policy files (.rego files, etc.) that the Governance Core depends on?