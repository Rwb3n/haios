source:
  url: "https://github.com/topoteretes/cognee"
  title: "Cognee: Memory for AI Agents"
  type: "framework"
  accessed: "2025-12-04"

summary:
  one_liner: "A framework for building deterministic memory for AI agents using Knowledge Graphs and Vector Stores, focusing on optimizing the interface between the graph and the LLM."
  key_concepts:
    - "Deterministic Memory"
    - "Graph-LLM Interface"
    - "Cognitive Architecture"
    - "Data Pipelines"
  architecture: "Pipeline-based architecture that ingests data, structures it into a graph, and provides a retrieval interface for agents."

relevance_to_haios:
  output_pipeline: "Emphasizes the 'Interface' aspect: How does the agent consume the memory? Suggests that the Output Pipeline should produce a 'deterministic' artifact (Graph) that is easy for the next agent to query."
  feedback_capture: "Not explicitly detailed in the README."
  epoch_management: "The 'Pipeline' concept aligns with our Epoch transition logic (Raw -> Structured)."
  utility_increase: "Graph-based memory increases utility by enabling complex reasoning over connected data."
  relevance_score: 4

technical_patterns:
  - name: "Deterministic Graph Construction"
    description: "Using LLMs to extract entities/relations deterministically to build a stable graph."
    code_example: "cognee.add(data) -> Graph"
    applicable_to: "Refinement Layer"

gaps:
  - "Documentation is high-level, implementation details require digging into code."

quotes:
  - text: "Memory for AI Agents in 6 lines of code."
    context: "Simplicity of interface is key for adoption."
