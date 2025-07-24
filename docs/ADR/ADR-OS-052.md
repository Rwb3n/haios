ADR-OS-052: "GenAI Processors" as Canonical Runtime Framework
Status: Proposed
Date: 2025-07-17
Deciders: Founding Operator, Genesis Architect
Context: Based on the analysis of the google/genai-processors open-source library, this ADR establishes the official runtime and data-flow architecture for all internal HAiOS services and agents.
1. Context
The HAiOS requires a standardized, robust, and maintainable framework for building the internal logic of its agents and services. Our initial prototypes have used a mix of monolithic scripts (2a_orchestrator_working.py) and early refactoring attempts with lightweight frameworks (PocketFlow).
While functional, these approaches lack a unified, powerful set of primitives for handling the asynchronous, streaming, and multi-modal nature of modern AI workflows. Building these primitives from scratch would be a significant and duplicative engineering effort.
The discovery of Google's "GenAI Processors" library provides a complete, mature, and philosophically-aligned solution. It offers a composable, asynchronous, data-flow paradigm that is perfectly suited to the complex orchestration tasks required by HAiOS.
2. Models & Frameworks Applied
Data-Flow Programming: The core model of the library, where a system is modeled as a graph of independent "processors" that data flows through. This is a highly scalable and resilient architectural style.
Separation of Concerns: The Processor abstraction cleanly separates the unit of computation from the orchestration of the pipeline, aligning perfectly with our Planner -> Builder and PocketFlow concepts.
Futures & Promises (Async): The framework is built on a robust asyncio foundation, which is a prerequisite for any high-performance agentic system.
3. Decision
Framework Adoption: The "GenAI Processors" library is hereby adopted as the exclusive, mandatory framework for implementing all internal data-flow and agentic logic within the HAiOS. All new Python-based agents and services must be built using the Processor and ProcessorPart abstractions.
Data Type Canonization: Our internal, custom Turn Artifact schema is now SUPERSEDED. We will adopt the official genai_processors.content_api.ProcessorPart as the canonical data packet for all data flowing within a HAiOS service.
Refactoring Mandate: Existing prototypes, most notably the 2A_Orchestrator, must be refactored to be compliant with this new canonical framework.
The "Napkin Sketch" of a genai-processors-based HAiOS Service:
Generated code
+-------------------------------------------------------------+
|          HAIOS SERVICE (e.g., 2A Orchestrator v2.0)           |
+-------------------------------------------------------------+
|                                                             |
|   - Built as a `processor.chain([...])` pipeline.           |
|                                                             |
|   - Each logical step is a discrete `Processor`               |
|     (e.g., `ReadPromptProcessor`, `ClaudeProcessor`,         |
|      `SaveOutputProcessor`).                                |
|                                                             |
|   - Data moves between processors as a stream of            |
|     `ProcessorPart` objects.                                |
|                                                             |
|   - The entire service exposes itself to the outside        |
|     world via an `A2A Protocol` endpoint.                   |
|                                                             |
+-------------------------------------------------------------+
Use code with caution.
4. Consequences
Positive:
Provides a Unified Runtime: All of our internal code will now share a common, powerful, and expressive architectural pattern. This dramatically improves maintainability and consistency.
Accelerates Development: We inherit a rich set of pre-built primitives for handling complex async streams, parallelism (// operator), and multi-modal data.
Enhances Robustness: The framework's design encourages the creation of small, single-responsibility, and easily testable Processor components.
Future-Proofs our Architecture: By building on a foundation designed for multi-modal, streaming AI, we are well-positioned for the future of agentic systems.
Negative:
Learning Curve: The Operator and any future developers must learn the specific idioms and patterns of the genai-processors library.
Refactoring Cost: We must invest time to refactor our existing 2A_Orchestrator prototype to be compliant with this new standard. This is an accepted and necessary cost.
5. Integration Plan
This ADR has a cascading impact on our entire stack:
ADR-OS-050 (A2A Protocol): A2A is the protocol for communication between services. genai-processors is the framework for logic within a service. They are perfectly complementary. The A2A Server endpoint will be responsible for translating an incoming A2A Task into a stream of ProcessorParts that can be fed into a genai-processors pipeline.
2A System: The v2.0 blueprint must be a genai-processors pipeline, as prototyped in EXEC_PLAN_BUILD_2A_ORCHESTRATOR_V2_GENAI.
Rhiza Agent: The entire Rhiza architecture (Ingest -> Triage -> Analyze) will be implemented as a processor.chain. The research_example from the genai-processors repo will serve as our reference implementation.