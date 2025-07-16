ADR-OS-052: GenAI Processors as Canonical Runtime

Content: This ADR will formally state that all internal agent and service logic for HAiOS MUST be implemented using the Processor and PartProcessor patterns from this library. It will also declare our Turn Artifact schema as superseded by ProcessorPart.