# generated: 2025-11-23
# System Auto: last updated on: 2025-11-23 11:11:20
# LangExtract Library Reference

**Library:** LangExtract by Google
**Context7 ID:** `/google/langextract`
**Version:** v1.0.7
**Source Reputation:** High
**Code Examples:** 101
**Benchmark Score:** 83.4

**Description:** LangExtract is a Python library that uses LLMs to extract structured information from unstructured text documents based on user-defined instructions, mapping extractions to their exact source locations.

---

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Core Concepts](#core-concepts)
3. [Basic Usage](#basic-usage)
4. [API Reference](#api-reference)
5. [Advanced Configuration](#advanced-configuration)
6. [Provider System](#provider-system)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)

---

## Installation & Setup

### Basic Installation

```bash
pip install langextract
```

### API Key Configuration

LangExtract supports multiple methods for API key configuration:

**Method 1: Environment Variable (Recommended)**
```bash
export LANGEXTRACT_API_KEY="your-api-key-here"
```

**Method 2: Direct Parameter (Development Only)**
```python
import langextract as lx

result = lx.extract(
    text_or_documents=input_text,
    prompt_description="Extract information...",
    examples=[...],
    model_id="gemini-2.5-flash",
    api_key="your-api-key-here"  # Only for testing/development
)
```

**Method 3: Provider-Specific Environment Variables**
```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-key"

# For custom providers
export MYPROVIDER_API_KEY="your-custom-key"
```

---

## Core Concepts

### Data Structures

LangExtract uses several core data structures:

#### 1. ExampleData
Structured examples to guide the extraction process (few-shot learning).

```python
import langextract as lx

example = lx.data.ExampleData(
    text="Patient was given 250 mg IV Cefazolin TID for one week.",
    extractions=[
        lx.data.Extraction(
            extraction_class="dosage",
            extraction_text="250 mg"
        ),
        lx.data.Extraction(
            extraction_class="route",
            extraction_text="IV"
        ),
        lx.data.Extraction(
            extraction_class="medication",
            extraction_text="Cefazolin"
        ),
    ]
)
```

#### 2. Extraction
Represents a single extracted entity with metadata.

**Key Attributes:**
- `extraction_class`: The category/type of extraction (e.g., "medication", "character")
- `extraction_text`: The actual extracted text
- `attributes`: Optional dict for additional metadata
- `char_interval`: Character-level position in source text
- `token_interval`: Token-level position (if available)
- `alignment_status`: Quality indicator (MATCH_EXACT, MATCH_FUZZY, NO_MATCH)

```python
extraction = lx.data.Extraction(
    extraction_class="character",
    extraction_text="ROMEO",
    attributes={"emotional_state": "wonder"}
)
```

#### 3. ExtractionResult
The complete result object returned by `lx.extract()`.

**Key Properties:**
- `extractions`: List of Extraction objects
- `text`: Original input text
- Access to alignment quality metrics

---

## Basic Usage

### Simple Entity Extraction

```python
import langextract as lx
import textwrap

# Define what you want to extract
prompt = textwrap.dedent("""
    Extract characters, emotions, and relationships in order of appearance.
    Use exact text for extractions. Do not paraphrase or overlap entities.
    Provide meaningful attributes for each entity to add context.
""")

# Provide few-shot examples
examples = [
    lx.data.ExampleData(
        text="ROMEO. But soft! What light through yonder window breaks?",
        extractions=[
            lx.data.Extraction(
                extraction_class="character",
                extraction_text="ROMEO",
                attributes={"emotional_state": "wonder"}
            ),
            lx.data.Extraction(
                extraction_class="emotion",
                extraction_text="But soft!",
                attributes={"feeling": "gentle awe"}
            ),
        ]
    )
]

# Run extraction
input_text = "Lady Juliet gazed longingly at the stars, her heart aching for Romeo"
result = lx.extract(
    text_or_documents=input_text,
    prompt_description=prompt,
    examples=examples,
    model_id="gemini-2.5-flash",
)

# Access results
for extraction in result.extractions:
    print(f"{extraction.extraction_class}: {extraction.extraction_text}")
    print(f"  Position: {extraction.char_interval}")
    print(f"  Attributes: {extraction.attributes}")
```

### Medical/Clinical NER Example

```python
import langextract as lx

input_text = "Patient took 400 mg PO Ibuprofen q4h for two days."

prompt_description = """Extract medication information including medication name,
dosage, route, frequency, and duration in the order they appear in the text."""

examples = [
    lx.data.ExampleData(
        text="Patient was given 250 mg IV Cefazolin TID for one week.",
        extractions=[
            lx.data.Extraction(extraction_class="dosage", extraction_text="250 mg"),
            lx.data.Extraction(extraction_class="route", extraction_text="IV"),
            lx.data.Extraction(extraction_class="medication", extraction_text="Cefazolin"),
            lx.data.Extraction(extraction_class="frequency", extraction_text="TID"),
            lx.data.Extraction(extraction_class="duration", extraction_text="for one week")
        ]
    )
]

result = lx.extract(
    text_or_documents=input_text,
    prompt_description=prompt_description,
    examples=examples,
    model_id="gemini-2.5-pro",
)

# Display with positions
for entity in result.extractions:
    if entity.char_interval:
        start, end = entity.char_interval.start_pos, entity.char_interval.end_pos
        print(f"• {entity.extraction_class}: {entity.extraction_text} (pos: {start}-{end})")
```

### Grouped Attributes (Relationship Linking)

Use attributes to link related extractions:

```python
from collections import defaultdict
import langextract as lx

input_text = """
Patient takes Aspirin 100mg daily for heart health and
Simvastatin 20mg at bedtime for cholesterol.
"""

examples = [
    lx.data.ExampleData(
        text="Patient takes Aspirin 100mg daily for heart health.",
        extractions=[
            lx.data.Extraction(
                extraction_class="medication",
                extraction_text="Aspirin",
                attributes={"medication_group": "Aspirin"}
            ),
            lx.data.Extraction(
                extraction_class="dosage",
                extraction_text="100mg",
                attributes={"medication_group": "Aspirin"}
            ),
            lx.data.Extraction(
                extraction_class="frequency",
                extraction_text="daily",
                attributes={"medication_group": "Aspirin"}
            ),
        ]
    )
]

result = lx.extract(
    text_or_documents=input_text,
    prompt_description="Extract medications with linked attributes using medication_group.",
    examples=examples,
    model_id="gemini-2.5-flash",
)

# Group extractions by medication
medication_groups = defaultdict(list)
for extraction in result.extractions:
    if extraction.attributes and "medication_group" in extraction.attributes:
        group_name = extraction.attributes["medication_group"]
        medication_groups[group_name].append(extraction)

# Display grouped results
for med_name, group_extractions in medication_groups.items():
    print(f"\n{med_name}:")
    for extraction in group_extractions:
        print(f"  {extraction.extraction_class}: {extraction.extraction_text}")
```

---

## API Reference

### Main Extraction Function

```python
lx.extract(
    text_or_documents: str | list[str],
    prompt_description: str,
    examples: list[ExampleData],
    model_id: str,

    # Optional: API Configuration
    api_key: str = None,
    model_url: str = None,

    # Optional: Document Processing
    max_char_buffer: int = 1000,      # Characters per chunk
    batch_length: int = 10,            # Chunks per batch
    max_workers: int = 20,             # Parallel workers

    # Optional: Extraction Configuration
    extraction_passes: int = 1,        # Number of extraction runs
    temperature: float = 0.7,          # Sampling temperature
    fence_output: bool = True,         # Use ```json delimiters
    use_schema_constraints: bool = True,  # Apply JSON schema

    # Optional: Validation
    prompt_validation_level = PromptValidationLevel.WARNING,
    prompt_validation_strict: bool = False,

    # Optional: Context & Alignment
    additional_context: str = None,    # Extra instructions for LLM
    resolver_params: dict = None,      # Fuzzy alignment settings

    # Optional: UI & Debugging
    show_progress: bool = False,
    debug: bool = False,
) -> ExtractionResult
```

### Accessing Extraction Details

```python
# After running extraction
result = lx.extract(...)

# Iterate through extractions
for extraction in result.extractions:
    # Basic information
    print(f"Class: {extraction.extraction_class}")
    print(f"Text: {extraction.extraction_text}")

    # Character-level position
    if extraction.char_interval:
        start = extraction.char_interval.start_pos
        end = extraction.char_interval.end_pos
        print(f"Position: {start}-{end}")

        # Verify against source
        source_text = result.text[start:end]
        assert source_text == extraction.extraction_text

    # Token-level position (if available)
    if extraction.token_interval:
        start_token = extraction.token_interval.start_pos
        end_token = extraction.token_interval.end_pos
        print(f"Tokens: {start_token}-{end_token}")

    # Alignment quality
    print(f"Alignment: {extraction.alignment_status}")

    # Custom attributes
    if extraction.attributes:
        for key, value in extraction.attributes.items():
            print(f"  {key}: {value}")
```

### Alignment Status Analysis

```python
from langextract.core.data import AlignmentStatus

# Analyze extraction quality
exact_matches = sum(1 for e in result.extractions
                   if e.alignment_status == AlignmentStatus.MATCH_EXACT)
fuzzy_matches = sum(1 for e in result.extractions
                   if e.alignment_status == AlignmentStatus.MATCH_FUZZY)
no_match = sum(1 for e in result.extractions
              if e.alignment_status == AlignmentStatus.NO_MATCH)

print(f"Total: {len(result.extractions)}")
print(f"Exact: {exact_matches}, Fuzzy: {fuzzy_matches}, No match: {no_match}")

# Filter high-quality extractions
high_quality = [e for e in result.extractions
                if e.alignment_status in (AlignmentStatus.MATCH_EXACT,
                                         AlignmentStatus.MATCH_FUZZY)]
```

---

## Advanced Configuration

### Using ModelConfig for Explicit Configuration

```python
import langextract as lx

# Explicit provider configuration
config = lx.factory.ModelConfig(
    model_id="gemini-2.5-pro",
    provider_kwargs={
        "api_key": "your-api-key-here",
        "temperature": 0.5,
        "vertexai": False,  # Set True for Google Cloud Vertex AI
    }
)

# Create model instance
model = lx.factory.create_model(
    config=config,
    examples=examples,
    use_schema_constraints=True,
    fence_output=False
)

# Use pre-configured model
result = lx.extract(
    text_or_documents=input_text,
    prompt_description=prompt,
    examples=examples,
    model=model
)
```

### Vertex AI Configuration

```python
vertex_config = lx.factory.ModelConfig(
    model_id="gemini-2.5-flash",
    provider_kwargs={
        "vertexai": True,
        "project": "your-gcp-project-id",
        "location": "us-central1",
    }
)
```

### Advanced Pipeline Configuration

```python
import langextract as lx
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

result = lx.extract(
    text_or_documents=input_text,
    prompt_description=prompt,
    examples=examples,
    model_id="gemini-2.5-flash",

    # Chunking and parallelization
    max_char_buffer=1000,
    batch_length=10,
    max_workers=20,

    # Multi-pass extraction (consensus)
    extraction_passes=3,

    # Model parameters
    temperature=0.3,              # Lower = more consistent
    fence_output=True,
    use_schema_constraints=True,

    # Validation
    prompt_validation_level=lx.prompting.PromptValidationLevel.WARNING,
    prompt_validation_strict=False,

    # Additional context
    additional_context="Focus on primary diagnoses and medications.",

    # Fuzzy alignment
    resolver_params={
        "enable_fuzzy_alignment": True,
        "fuzzy_alignment_threshold": 0.75,
        "accept_match_lesser": True,
    },

    # UI
    show_progress=True,
    debug=True,
)
```

### OpenAI Models

```python
import os

result = lx.extract(
    text_or_documents=input_text,
    prompt_description=prompt,
    examples=examples,
    model_id="gpt-4o",  # Alternative: "gpt-4o-mini", "gpt-4-turbo"
    api_key=os.environ.get('OPENAI_API_KEY'),
    fence_output=True,
    use_schema_constraints=False,  # OpenAI doesn't support schema constraints yet
)
```

### Local LLMs via Ollama

```python
# Prerequisites:
# 1. Install Ollama: https://ollama.ai
# 2. Pull model: ollama pull gemma2:2b
# 3. Start server: ollama serve

result = lx.extract(
    text_or_documents=input_text,
    prompt_description=prompt,
    examples=examples,
    model_id="gemma2:2b",  # Automatically selects Ollama provider
    model_url="http://localhost:11434",
    fence_output=False,
    use_schema_constraints=False
)
```

---

## Provider System

LangExtract uses a plugin-based provider system for different LLM backends.

### Available Providers

- **Gemini** (Google): `gemini-2.5-pro`, `gemini-2.5-flash`
- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`
- **Ollama** (Local): `gemma2:2b`, etc.
- **Custom Providers**: Via plugin system

### Provider Auto-Selection

LangExtract automatically selects the appropriate provider based on `model_id`:

```python
# Automatically uses Gemini provider
result = lx.extract(..., model_id="gemini-2.5-flash")

# Automatically uses OpenAI provider
result = lx.extract(..., model_id="gpt-4o")

# Automatically uses Ollama provider
result = lx.extract(..., model_id="gemma2:2b")
```

### Explicit Provider Selection

```python
config = lx.factory.ModelConfig(
    model_id="gemma2:2b",
    provider="OllamaLanguageModel",  # Explicit provider
    provider_kwargs={
        "model_url": "http://localhost:11434"
    }
)
model = lx.factory.create_model(config)
```

### Custom Provider Implementation

#### 1. Create Provider Class

```python
# langextract_myprovider/__init__.py
import os
import langextract as lx

@lx.providers.registry.register(
    r'^mymodel',    # Pattern for model IDs
    r'^custom',     # Alternative pattern
    priority=10     # Higher priority = preferred
)
class MyProviderLanguageModel(lx.inference.BaseLanguageModel):
    def __init__(self, model_id: str, api_key: str = None, **kwargs):
        super().__init__()
        self.model_id = model_id
        self.api_key = api_key or os.environ.get('MYPROVIDER_API_KEY')
        self.client = MyProviderClient(api_key=self.api_key)

    def infer(self, batch_prompts, **kwargs):
        for prompt in batch_prompts:
            result = self.client.generate(prompt, **kwargs)
            yield [lx.inference.ScoredOutput(score=1.0, output=result)]
```

#### 2. Configure Entry Point

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "langextract-myprovider"
version = "0.1.0"
dependencies = ["langextract>=1.0.0"]

[project.entry-points."langextract.providers"]
myprovider = "langextract_myprovider:MyProviderLanguageModel"
```

#### 3. Install and Use

```bash
# Install in development mode
pip install -e .

# Test registration
python -c "
import langextract as lx
lx.providers.load_plugins_once()
print('Registered:', any('myprovider' in str(e) for e in lx.providers.registry.list_entries()))
"
```

```python
# Use custom provider
config = lx.factory.ModelConfig(
    model_id="mymodel-v1",
    provider="MyProviderLanguageModel",
    provider_kwargs={"api_key": "your-api-key"}
)
model = lx.factory.create_model(config)
```

---

## Error Handling

### Provider Not Found

```python
from langextract import registry

try:
    result = lx.extract(..., model_id="unknown-model")
except ValueError as e:
    if "No provider registered" in str(e):
        print("Available providers:")
        for entry in registry.list_entries():
            print(f"  - {entry}")
    else:
        raise
```

### Common Parameters

```python
# Common parameters (handled by lx.extract)
result = lx.extract(
    text="Your document",
    model_id="gemini-2.5-flash",
    prompt_description="Extract entities",
    examples=[...],
    num_workers=4,           # Parallel processing
    max_chunk_size=3000,     # Document chunking
)

# Provider-specific parameters (passed via kwargs)
result = lx.extract(
    text="Your document",
    model_id="gemini-2.5-flash",
    prompt_description="Extract entities",
    temperature=0.7,         # Provider-specific
    api_key="your-key",      # Provider-specific
    max_output_tokens=1000,  # Provider-specific
)
```

---

## Best Practices

### 1. Prompt Engineering

```python
import textwrap

# ✓ GOOD: Clear, specific instructions
prompt = textwrap.dedent("""
    Extract characters, emotions, and relationships in order of appearance.
    Use exact text for extractions. Do not paraphrase or overlap entities.
    Provide meaningful attributes for each entity to add context.
""")

# ✗ BAD: Vague instructions
prompt = "Extract stuff from the text"
```

### 2. Example Quality

```python
# ✓ GOOD: Representative, diverse examples
examples = [
    lx.data.ExampleData(
        text="ROMEO. But soft! What light...",
        extractions=[
            lx.data.Extraction(
                extraction_class="character",
                extraction_text="ROMEO",
                attributes={"emotional_state": "wonder"}
            ),
            # ... more varied examples
        ]
    ),
    # Include 2-5 diverse examples
]

# ✗ BAD: Single or repetitive examples
```

### 3. Temperature Settings

```python
# For consistent, precise extraction (NER, medical data)
result = lx.extract(..., temperature=0.3)

# For creative/diverse extraction
result = lx.extract(..., temperature=0.7)
```

### 4. Validation & Quality Control

```python
from langextract.core.data import AlignmentStatus

# Filter low-quality extractions
high_quality = [
    e for e in result.extractions
    if e.alignment_status in (
        AlignmentStatus.MATCH_EXACT,
        AlignmentStatus.MATCH_FUZZY
    )
]

# Validate against source
for extraction in result.extractions:
    if extraction.char_interval:
        start = extraction.char_interval.start_pos
        end = extraction.char_interval.end_pos
        source = result.text[start:end]
        assert source == extraction.extraction_text
```

### 5. Multi-Pass Extraction (Consensus)

```python
# Run extraction multiple times for higher confidence
result = lx.extract(
    text_or_documents=input_text,
    prompt_description=prompt,
    examples=examples,
    model_id="gemini-2.5-flash",
    extraction_passes=3,  # Run 3 times
    temperature=0.3,      # Low temperature for consistency
)
```

### 6. Chunking for Large Documents

```python
# Process large documents in chunks
result = lx.extract(
    text_or_documents=long_document,
    prompt_description=prompt,
    examples=examples,
    model_id="gemini-2.5-flash",
    max_char_buffer=1000,  # Characters per chunk
    batch_length=10,       # Chunks per batch
    max_workers=20,        # Parallel processing
)
```

---

## Visualization & Output

### Save Results to JSONL

```python
# Save annotated documents
lx.io.save_annotated_documents(
    [result],
    output_name="extraction_results.jsonl",
    output_dir="./output"
)
```

### Generate Interactive HTML Visualization

```python
# Generate visualization
html_content = lx.visualize("extraction_results.jsonl")

# Save to file
with open("visualization.html", "w") as f:
    if hasattr(html_content, 'data'):
        f.write(html_content.data)  # Jupyter/Colab
    else:
        f.write(html_content)       # Standard Python

print("Visualization saved to visualization.html")
```

---

## Integration Notes for HAIOS

### Recommended Configuration for HAIOS ETL

```python
import langextract as lx
import logging

# Configure for production use
def extract_entities_for_haios(
    text: str,
    prompt: str,
    examples: list[lx.data.ExampleData],
    model_id: str = "gemini-2.5-flash"
) -> lx.ExtractionResult:
    """
    Extract entities with HAIOS-specific configuration.

    - High precision (low temperature)
    - Schema constraints enabled
    - Fuzzy alignment for robustness
    - Progress tracking disabled (for batch processing)
    """
    return lx.extract(
        text_or_documents=text,
        prompt_description=prompt,
        examples=examples,
        model_id=model_id,

        # Precision settings
        temperature=0.2,              # High precision
        use_schema_constraints=True,  # Enforce structure
        fence_output=True,            # Clean JSON

        # Alignment
        resolver_params={
            "enable_fuzzy_alignment": True,
            "fuzzy_alignment_threshold": 0.80,
        },

        # Validation
        prompt_validation_level=lx.prompting.PromptValidationLevel.WARNING,

        # Processing (adjust based on document size)
        max_char_buffer=2000,
        batch_length=5,
        max_workers=10,

        # UI (disabled for batch)
        show_progress=False,
        debug=False,
    )
```

### Error Handling Pattern

```python
from typing import Optional

def safe_extract(text: str, prompt: str, examples: list) -> Optional[lx.ExtractionResult]:
    """Safe extraction with comprehensive error handling."""
    try:
        result = lx.extract(
            text_or_documents=text,
            prompt_description=prompt,
            examples=examples,
            model_id="gemini-2.5-flash",
        )

        # Validate result quality
        if not result.extractions:
            logging.warning("No extractions found")
            return None

        # Check alignment quality
        exact = sum(1 for e in result.extractions
                   if e.alignment_status == AlignmentStatus.MATCH_EXACT)
        if exact < len(result.extractions) * 0.5:  # <50% exact matches
            logging.warning(f"Low alignment quality: {exact}/{len(result.extractions)} exact")

        return result

    except ValueError as e:
        if "Provider not found" in str(e):
            logging.error(f"LLM provider error: {e}")
        else:
            logging.error(f"Extraction failed: {e}")
        return None

    except Exception as e:
        logging.error(f"Unexpected error during extraction: {e}")
        return None
```

---

## References

- **Official Repository:** https://github.com/google/langextract
- **Context7 Library ID:** `/google/langextract`
- **Version:** v1.0.7
- **Documentation Retrieved:** 2025-11-23

---

**END OF REFERENCE**
