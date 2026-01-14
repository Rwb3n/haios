### `haios-memory-mcp` API Specification (v1)

This API will use the JSON-RPC format over HTTP POST requests.

---

#### **Method 1: `memory.search`**

This is the primary workhorse method. It allows for a flexible search across the memory, combining keyword/semantic search with structured filters based on the entities and concepts we've extracted.

**Request Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "memory.search",
  "params": {
    "query": "What is the 'Certainty Ratchet'?",
    "entity_filter": [
      {"type": "ADR", "value": "ADR-OS-043"}
    ],
    "concept_filter": [
      {"type": "Principle"}
    ],
    "limit": 10
  },
  "id": 1
}
```

**Response Example:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "hits": [
      {
        "artifact_path": "docs/source/Cody_Reports/Epoch_2/Cody_Report_1006.md",
        "line_number": 50,
        "snippet": "The Certainty Ratchet is a machine for systematically identifying and eliminating ambiguity.",
        "score": 0.95,
        "entities": [{"type": "Principle", "value": "Certainty Ratchet"}],
        "concepts": []
      }
    ]
  },
  "id": 1
}
```

---

#### **Method 2: `memory.getArtifactDetails`**

A simpler method to retrieve all known structured information about a single, specific file.

**Request Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "memory.getArtifactDetails",
  "params": {
    "file_path": "docs/ADR/ADR-OS-043.md"
  },
  "id": 2
}
```

**Response Example:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "artifact": {
      "file_path": "docs/ADR/ADR-OS-043.md",
      "last_processed_at": "2025-10-11T12:00:00Z",
      "entities": [
        {"type": "ADR", "value": "ADR-OS-043"},
        {"type": "Principle", "value": "Governance Flywheel"}
      ],
      "concepts": [
        {"type": "Decision", "content": "Adopt the Governance Flywheel architecture."}
      ]
    }
  },
  "id": 2
}
```
