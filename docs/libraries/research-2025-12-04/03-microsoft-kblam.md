source:
  url: "https://github.com/microsoft/KBLaM"
  title: "KBLaM: Knowledge Base Augmented Language Models"
  type: "framework"
  accessed: "2025-12-04"

summary:
  one_liner: "A method to augment LLMs with external knowledge by training adapters to transform the KB into special knowledge tokens, eliminating the need for external retrieval (RAG)."
  key_concepts:
    - "Knowledge Tokens"
    - "Adapter Training"
    - "Retrieval-Free Augmentation"
    - "Linear Scaling"
  architecture: "Base LLM (frozen) + Trainable Adapters that ingest KB entities and output knowledge tokens into the context."

relevance_to_haios:
  output_pipeline: "Suggests a radical transformation: Instead of just retrieving text, we could 'compile' our ReasoningBank into a compressed token representation (or at least a highly optimized context block) for the next epoch."
  feedback_capture: "Not explicitly addressed, but the training of adapters implies a feedback loop (loss function) based on QA performance."
  epoch_management: "Each Epoch could correspond to a retrained/updated set of Knowledge Tokens/Adapters."
  utility_increase: "Reduces inference latency (no retrieval step) and potentially improves grounding by 'baking' knowledge into the model's working memory."
  relevance_score: 4

technical_patterns:
  - name: "Knowledge-to-Token Transformation"
    description: "Transforming structured KB entries into dense vector representations (tokens) that the LLM can attend to directly."
    code_example: "Adapter(KB_Embedding) -> Knowledge_Tokens"
    applicable_to: "ReasoningBank (Context Injection)"

gaps:
  - "Requires training/fine-tuning adapters, which is computationally expensive compared to simple RAG."
  - "Currently a research prototype, not production-ready."

quotes:
  - text: "KBLaM eliminates external retrieval modules... its computational overhead scales linearly with KB size rather than quadratically."
    context: "Highlights the efficiency gain of transforming knowledge vs. searching it."
