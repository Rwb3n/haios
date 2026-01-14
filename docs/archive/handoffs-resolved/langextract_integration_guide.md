# generated: 2025-11-23
# System Auto: last updated on: 2025-11-23 11:13:47
# LangExtract Integration Guide for HAIOS ETL

**Problem:** Current implementation calls `langextract.extract(content)` without required parameters.

**Solution:** Convert YAML schema to langextract ExampleData format with few-shot examples.

---

## Quick Fix for extraction.py

Replace the current `extract_from_file` method with:

```python
import langextract as lx
import textwrap
from typing import List

class ExtractionManager:
    def __init__(self, api_key: str, model_id: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_id = model_id
        self.prompt = self._build_prompt()
        self.examples = self._build_examples()

    def _build_prompt(self) -> str:
        """Build extraction prompt from schema definition."""
        return textwrap.dedent("""
            Extract entities and concepts from HAIOS agent conversation logs.

            ENTITIES to extract:
            - User: Speaker role for human operator (User:, human:, operator:)
            - Agent: Speaker role for AI (Cody:, Gemini:, Claude:, agent:)
            - ADR: Architecture Decision Records (ADR-OS-XXX)
            - Filepath: File references (paths ending in .py, .md, .json, etc.)
            - AntiPattern: Anti-pattern references (AP-XXX)

            CONCEPTS to extract:
            - Directive: Direct commands or instructions
            - Critique: Corrective feedback or flaw identification
            - Proposal: Plans, solutions, or recommendations
            - Decision: Formal decisions

            Use exact text for extractions. Extract in order of appearance.
            Provide attributes for context when available.
        """)

    def _build_examples(self) -> List[lx.data.ExampleData]:
        """Build few-shot examples from schema."""
        return [
            # Example 1: Entity extraction
            lx.data.ExampleData(
                text="User: Please implement ADR-OS-023 in the database.py file.",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="User:",
                        attributes={"entity_type": "User"}
                    ),
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="ADR-OS-023",
                        attributes={"entity_type": "ADR"}
                    ),
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="database.py",
                        attributes={"entity_type": "Filepath"}
                    ),
                ]
            ),

            # Example 2: Concept extraction
            lx.data.ExampleData(
                text="Agent: I propose we implement a Decoupled Adapter Pattern to solve this issue.",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="Agent:",
                        attributes={"entity_type": "Agent"}
                    ),
                    lx.data.Extraction(
                        extraction_class="concept",
                        extraction_text="I propose we implement a Decoupled Adapter Pattern",
                        attributes={"concept_type": "Proposal"}
                    ),
                ]
            ),

            # Example 3: Critique
            lx.data.ExampleData(
                text="User: No, that's wrong. The flaw is that the logic lives in the n8n database.",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="User:",
                        attributes={"entity_type": "User"}
                    ),
                    lx.data.Extraction(
                        extraction_class="concept",
                        extraction_text="No, that's wrong",
                        attributes={"concept_type": "Critique"}
                    ),
                    lx.data.Extraction(
                        extraction_class="concept",
                        extraction_text="The flaw is that the logic lives in the n8n database",
                        attributes={"concept_type": "Critique"}
                    ),
                ]
            ),

            # Example 4: Decision
            lx.data.ExampleData(
                text="Decision: ADOPT AND CANONIZE THIS POLICY per ADR-OS-015.",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="concept",
                        extraction_text="Decision: ADOPT AND CANONIZE THIS POLICY",
                        attributes={"concept_type": "Decision"}
                    ),
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="ADR-OS-015",
                        attributes={"entity_type": "ADR"}
                    ),
                ]
            ),
        ]

    def extract_from_file(self, file_path: str, content: str) -> ExtractionResult:
        """Extract entities and concepts from file content using LLM."""
        if langextract is None:
            raise ImportError("langextract library is not installed.")

        try:
            # Call langextract with proper parameters
            result = lx.extract(
                text_or_documents=content,
                prompt_description=self.prompt,
                examples=self.examples,
                model_id=self.model_id,
                api_key=self.api_key,

                # Optional: Quality settings
                temperature=0.2,              # High precision
                use_schema_constraints=True,  # Enforce structure
                fence_output=True,            # Clean JSON output
            )

            # Parse langextract result into our format
            entities = []
            concepts = []

            for extraction in result.extractions:
                if extraction.extraction_class == "entity":
                    entity_type = extraction.attributes.get("entity_type", "Unknown")
                    entities.append(Entity(
                        type=entity_type,
                        value=extraction.extraction_text
                    ))

                elif extraction.extraction_class == "concept":
                    concept_type = extraction.attributes.get("concept_type", "Unknown")
                    concepts.append(Concept(
                        type=concept_type,
                        content=extraction.extraction_text,
                        source_adr=None  # Could extract from context
                    ))

            return ExtractionResult(entities=entities, concepts=concepts)

        except Exception as e:
            raise ExtractionError(f"Extraction failed for {file_path}: {str(e)}") from e
```

---

## Understanding the Mapping

### Your YAML Schema → LangExtract Format

**YAML (What you have):**
```yaml
entities:
  - name: "ADR"
    pattern: "ADR-OS-\d{3}"
```

**LangExtract (What it needs):**
```python
lx.data.ExampleData(
    text="Please implement ADR-OS-023 in database.py",  # Input example
    extractions=[
        lx.data.Extraction(
            extraction_class="entity",      # Category
            extraction_text="ADR-OS-023",   # Actual text found
            attributes={"entity_type": "ADR"}  # Metadata
        ),
    ]
)
```

**Key Difference:** LangExtract doesn't use regex patterns. Instead, it learns from concrete input-output examples (few-shot learning).

---

## Step-by-Step Integration

### 1. Update extraction.py

Replace lines 32-81 with the implementation above.

### 2. Update Initialization Call

In your code that creates ExtractionManager:

```python
# Old (won't work)
manager = ExtractionManager(api_key="your-key")

# New (works)
manager = ExtractionManager(
    api_key=os.environ.get("LANGEXTRACT_API_KEY"),
    model_id="gemini-2.5-flash"
)
```

### 3. Set Environment Variable

```bash
export LANGEXTRACT_API_KEY="your-gemini-api-key-here"
```

### 4. Update Tests

The tests in `tests/test_extraction.py` will need updating:

```python
def test_extraction_success(self, mock_langextract):
    # Mock the new signature
    mock_result = MagicMock()
    mock_result.extractions = [
        MagicMock(
            extraction_class="entity",
            extraction_text="ADR-OS-023",
            attributes={"entity_type": "ADR"}
        ),
    ]
    mock_langextract.extract.return_value = mock_result

    # Test
    manager = ExtractionManager(api_key="test-key")
    result = manager.extract_from_file("test.md", "content with ADR-OS-023")

    # Verify extract was called with correct args
    mock_langextract.extract.assert_called_once()
    call_kwargs = mock_langextract.extract.call_args[1]
    assert call_kwargs["text_or_documents"] == "content with ADR-OS-023"
    assert call_kwargs["model_id"] == "gemini-2.5-flash"
    assert "prompt_description" in call_kwargs
    assert "examples" in call_kwargs
```

---

## Alternative: Load Examples from YAML (Advanced)

If you want to dynamically load examples from your YAML schema:

```python
import yaml
from pathlib import Path

class ExtractionManager:
    def __init__(self, api_key: str, model_id: str = "gemini-2.5-flash",
                 schema_path: str = "docs/specs/langextract_schema_v1.yml"):
        self.api_key = api_key
        self.model_id = model_id
        self.schema = self._load_schema(schema_path)
        self.prompt = self._build_prompt_from_schema()
        self.examples = self._build_examples_from_schema()

    def _load_schema(self, path: str) -> dict:
        """Load YAML schema file."""
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def _build_prompt_from_schema(self) -> str:
        """Generate prompt from schema definition."""
        entity_types = [e['name'] for e in self.schema.get('entities', [])]
        concept_types = [c['name'] for c in self.schema.get('concepts', [])]

        return textwrap.dedent(f"""
            Extract entities and concepts from HAIOS agent conversation logs.

            ENTITY TYPES: {', '.join(entity_types)}
            CONCEPT TYPES: {', '.join(concept_types)}

            Use exact text. Extract in order of appearance.
        """)

    def _build_examples_from_schema(self) -> List[lx.data.ExampleData]:
        """Build examples using schema examples field."""
        examples = []

        # Use examples from concepts section
        for concept in self.schema.get('concepts', []):
            if 'examples' in concept:
                for example_text in concept['examples']:
                    examples.append(lx.data.ExampleData(
                        text=example_text,
                        extractions=[
                            lx.data.Extraction(
                                extraction_class="concept",
                                extraction_text=example_text,
                                attributes={"concept_type": concept['name']}
                            )
                        ]
                    ))

        # Add hardcoded entity examples (since YAML doesn't have them)
        examples.extend([
            lx.data.ExampleData(
                text="User: Check ADR-OS-023 in database.py",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="User:",
                        attributes={"entity_type": "User"}
                    ),
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="ADR-OS-023",
                        attributes={"entity_type": "ADR"}
                    ),
                    lx.data.Extraction(
                        extraction_class="entity",
                        extraction_text="database.py",
                        attributes={"entity_type": "Filepath"}
                    ),
                ]
            ),
        ])

        return examples
```

---

## Testing the Integration

### 1. Quick Test Script

```python
# test_langextract_integration.py
import os
from haios_etl.extraction import ExtractionManager

# Set API key
os.environ['LANGEXTRACT_API_KEY'] = 'your-key-here'

# Create manager
manager = ExtractionManager(
    api_key=os.environ['LANGEXTRACT_API_KEY'],
    model_id="gemini-2.5-flash"
)

# Test extraction
test_content = """
User: Please implement ADR-OS-023 for the database layer.
Agent: I propose we use the Repository Pattern from ADR-OS-015.
User: No, that's wrong. The flaw is we need idempotency.
Decision: ADOPT the Event Sourcing approach.
"""

result = manager.extract_from_file("test.md", test_content)

print("Entities found:")
for entity in result.entities:
    print(f"  {entity.type}: {entity.value}")

print("\nConcepts found:")
for concept in result.concepts:
    print(f"  {concept.type}: {concept.content[:50]}...")
```

### 2. Expected Output

```
Entities found:
  User: User:
  ADR: ADR-OS-023
  Agent: Agent:
  ADR: ADR-OS-015
  User: User:

Concepts found:
  Directive: Please implement ADR-OS-023 for the database ...
  Proposal: I propose we use the Repository Pattern from...
  Critique: No, that's wrong...
  Critique: The flaw is we need idempotency...
  Decision: Decision: ADOPT the Event Sourcing approach...
```

---

## Next Steps

1. **Install langextract**: `pip install langextract`
2. **Set API key**: `export LANGEXTRACT_API_KEY="your-key"`
3. **Update extraction.py** with the new implementation
4. **Update tests** to match new signatures
5. **Run integration test** to verify
6. **Iterate on examples** to improve extraction quality

---

## Reference

- **Full API documentation:** `docs/libraries/langextract_reference.md`
- **Official repo:** https://github.com/google/langextract
- **Schema file:** `docs/specs/langextract_schema_v1.yml`

---

**Key Takeaway:** LangExtract uses **few-shot learning** (showing examples) rather than **pattern matching** (regex). Your YAML schema defines WHAT to extract, but you need to show HOW through concrete examples.
