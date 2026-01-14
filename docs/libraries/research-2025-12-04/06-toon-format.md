source:
  url: "https://github.com/toon-format/toon"
  title: "Token-Oriented Object Notation (TOON)"
  type: "format"
  accessed: "2025-12-04"

summary:
  one_liner: "A token-efficient, human-readable data format designed for LLMs that combines YAML-like structure with CSV-style tables, achieving higher retrieval accuracy than JSON."
  key_concepts:
    - "Token Efficiency (~40% savings)"
    - "Retrieval Accuracy (+4%)"
    - "Tabular Arrays"
    - "Schema-Aware"
  architecture: "Specification and SDKs for serializing/deserializing data into a format optimized for LLM tokenizers."

relevance_to_haios:
  output_pipeline: "Provides a concrete 'Output Format' for Epoch N+1. Instead of dumping raw JSON or verbose Markdown, we can serialize the ReasoningBank into TOON. This allows us to fit more strategies into the context window."
  feedback_capture: "Not directly relevant."
  epoch_management: "Epoch N+1 artifacts could be stored/transmitted in TOON format."
  utility_increase: "Increases utility by maximizing the 'information density' of the context window."
  relevance_score: 5

technical_patterns:
  - name: "Tabular Array Serialization"
    description: "Collapsing arrays of objects into a CSV-like table with a single header row to save tokens on repeated keys."
    code_example: "items[3]{id,name}: 1,foo 2,bar 3,baz"
    applicable_to: "ReasoningBank (Strategy Injection)"

gaps:
  - "New format, might require custom parsers/serializers if not using the JS/TS SDK (HAIOS is Python)."

quotes:
  - text: "TOON conveys the same information with even fewer tokens – combining YAML-like indentation with CSV-style tabular arrays."
    context: "The core value proposition: same truth, less cost."
