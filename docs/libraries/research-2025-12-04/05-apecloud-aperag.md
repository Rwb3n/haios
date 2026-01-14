source:
  url: "https://github.com/apecloud/ApeRAG"
  title: "ApeRAG: Production-ready GraphRAG"
  type: "framework"
  accessed: "2025-12-04"

summary:
  one_liner: "A production-grade RAG system combining GraphRAG (LightRAG), vector search, and MCP support for multi-modal knowledge retrieval."
  key_concepts:
    - "GraphRAG"
    - "Entity Normalization"
    - "Multi-modal Indexing (Vector, Graph, Summary)"
    - "MCP Integration"
  architecture: "Hybrid retrieval engine using LightRAG for graph construction, integrated with Kubernetes for scalability and MCP for agent access."

relevance_to_haios:
  output_pipeline: "Demonstrates a 'Transformation Engine' that converts raw text into multiple useful formats: Vectors (for similarity), Graphs (for relations), and Summaries (for high-level context). HAIOS should adopt this multi-index strategy for Epoch N+1."
  feedback_capture: "Uses 'Entity Normalization' which implies a feedback/cleaning step to merge duplicate entities."
  epoch_management: "Not explicit, but the 'Summary' index acts as a compressed version of the knowledge, suitable for carrying over to the next epoch."
  utility_increase: "GraphRAG significantly increases utility for complex relational queries compared to simple vector search."
  relevance_score: 5

technical_patterns:
  - name: "Multi-Index Transformation"
    description: "Transforming the same source data into multiple specialized indices (Vector, Graph, Summary) to support different query types."
    code_example: "Index(Text) -> [VectorIndex, GraphIndex, SummaryIndex]"
    applicable_to: "Output Pipeline / Knowledge Transformation"
  - name: "Entity Normalization"
    description: "Merging similar entities (e.g., 'Gemini' and 'Google Gemini') during the graph construction phase."
    code_example: "LLM-based entity resolution step"
    applicable_to: "Refinement Layer"

gaps:
  - "Complex infrastructure (Kubernetes) might be overkill for the current HAIOS scale."

quotes:
  - text: "Advanced Index Types: Five comprehensive index types for optimal retrieval: Vector, Full-text, Graph, Summary, and Vision."
    context: "A target architecture for HAIOS memory."
