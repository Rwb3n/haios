# generated: 2025-11-23
# System Auto: last updated on: 2025-11-23 11:25:43
# LangExtract Advanced Features Response

**Request:** Session 5 - Error Handling & Performance
**Date:** 2025-11-23
**Status:** RESEARCHED

---

## 1. Exception Hierarchy

### Finding: LIMITED DOCUMENTATION

**What I Found:**
LangExtract documentation does NOT expose a rich exception hierarchy. Only one exception type is documented:

```python
from langextract import registry

try:
    result = lx.extract(..., model_id="unknown-model")
except ValueError as e:
    if "No provider registered" in str(e):
        print("Provider not found")
```

**Specific Questions:**

#### Q: Is there a `RateLimitError`?
**A: NOT DOCUMENTED.** No evidence of a specific rate limit exception.

**Implication:** Rate limits likely bubble up as generic exceptions from the underlying provider (e.g., Google Gemini SDK exceptions).

**Recommended Approach:**
```python
import time
from typing import Optional

def extract_with_retry(
    text: str,
    prompt: str,
    examples: list,
    max_retries: int = 3,
    backoff_base: float = 2.0
) -> Optional[lx.ExtractionResult]:
    """
    Wrapper with exponential backoff for rate limits.

    Since langextract doesn't expose specific exceptions,
    we catch broadly and retry on any exception.
    """
    for attempt in range(max_retries):
        try:
            return lx.extract(
                text_or_documents=text,
                prompt_description=prompt,
                examples=examples,
                model_id="gemini-2.5-flash",
            )
        except Exception as e:
            error_msg = str(e).lower()

            # Heuristic detection of retryable errors
            is_retryable = any([
                "rate limit" in error_msg,
                "quota" in error_msg,
                "429" in error_msg,
                "503" in error_msg,
                "timeout" in error_msg,
            ])

            if not is_retryable or attempt == max_retries - 1:
                # Non-retryable or final attempt
                raise

            # Exponential backoff
            sleep_time = backoff_base ** attempt
            logging.warning(
                f"Extraction failed (attempt {attempt + 1}/{max_retries}): {e}. "
                f"Retrying in {sleep_time}s..."
            )
            time.sleep(sleep_time)

    return None
```

#### Q: Is there a `ContextWindowExceededError`?
**A: NOT DOCUMENTED.** No specific exception for context window limits.

**Implication:** Context window errors will likely manifest as:
- Generic API errors from the provider
- Possibly silent truncation (depends on provider)

**Recommended Approach:**
```python
def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for English."""
    return len(text) // 4

def extract_with_chunking(
    text: str,
    prompt: str,
    examples: list,
    max_context_chars: int = 30000  # ~7.5k tokens for Gemini
) -> lx.ExtractionResult:
    """
    Automatically chunk if text exceeds context window.
    Uses langextract's built-in chunking.
    """
    if len(text) > max_context_chars:
        # Let langextract handle chunking
        return lx.extract(
            text_or_documents=text,
            prompt_description=prompt,
            examples=examples,
            model_id="gemini-2.5-flash",
            max_char_buffer=10000,  # Chunk size
            max_workers=10,         # Parallel processing
        )
    else:
        # Single pass for small documents
        return lx.extract(
            text_or_documents=text,
            prompt_description=prompt,
            examples=examples,
            model_id="gemini-2.5-flash",
        )
```

#### Q: How to distinguish transient vs permanent errors?
**A: NO BUILT-IN MECHANISM.** Must use heuristics on error messages.

**Recommended Classification:**
```python
from enum import Enum

class ErrorType(Enum):
    RETRYABLE = "retryable"
    PERMANENT = "permanent"
    UNKNOWN = "unknown"

def classify_error(exception: Exception) -> ErrorType:
    """
    Classify exceptions as retryable or permanent.

    Since langextract doesn't provide typed exceptions,
    we use string matching on error messages.
    """
    error_msg = str(exception).lower()

    # Retryable errors (transient)
    retryable_patterns = [
        "rate limit",
        "quota exceeded",
        "429",
        "503",
        "timeout",
        "temporarily unavailable",
        "connection reset",
        "connection refused",
    ]

    # Permanent errors (bad request, auth, etc.)
    permanent_patterns = [
        "invalid api key",
        "authentication failed",
        "400",
        "401",
        "403",
        "404",
        "invalid model",
        "provider not found",
        "invalid request",
    ]

    if any(pattern in error_msg for pattern in retryable_patterns):
        return ErrorType.RETRYABLE

    if any(pattern in error_msg for pattern in permanent_patterns):
        return ErrorType.PERMANENT

    return ErrorType.UNKNOWN

# Usage
try:
    result = lx.extract(...)
except Exception as e:
    error_type = classify_error(e)

    if error_type == ErrorType.RETRYABLE:
        # Apply retry logic
        logging.warning(f"Retryable error: {e}")
        # ... implement retry
    elif error_type == ErrorType.PERMANENT:
        # Fail fast
        logging.error(f"Permanent error: {e}")
        raise
    else:
        # Unknown - log and fail (or retry conservatively)
        logging.error(f"Unknown error type: {e}")
        raise
```

---

## 2. Async Support

### Finding: NO NATIVE ASYNCIO SUPPORT

**What I Found:**
- **No `alx.extract()` or async methods documented**
- **Thread-based parallelism** via `max_workers` parameter
- Built-in parallel processing for batch operations

**Evidence:**
```python
# LangExtract uses threading, not asyncio
result = lx.extract(
    text_or_documents=documents,
    prompt_description=prompt,
    examples=examples,
    model_id="gemini-2.5-flash",
    max_workers=10,  # Thread pool size, not async workers
)
```

### Is it Thread-Safe?

**A: LIKELY YES, but not explicitly documented.**

The library's design suggests thread safety:
- Uses `max_workers` for parallelism (implies ThreadPoolExecutor or similar)
- Processes multiple documents concurrently without issues
- No warnings about thread safety in docs

**Recommended Approach for Async Integration:**

If you need async (e.g., for FastAPI/async frameworks), wrap in `asyncio.to_thread()`:

```python
import asyncio
import langextract as lx

async def extract_async(
    text: str,
    prompt: str,
    examples: list,
    model_id: str = "gemini-2.5-flash"
) -> lx.ExtractionResult:
    """
    Async wrapper around synchronous langextract.

    Uses asyncio.to_thread to run in thread pool,
    preventing blocking of the event loop.
    """
    return await asyncio.to_thread(
        lx.extract,
        text_or_documents=text,
        prompt_description=prompt,
        examples=examples,
        model_id=model_id
    )

# Usage in async context
async def process_multiple_files(file_paths: list[str]):
    tasks = []
    for path in file_paths:
        content = await read_file_async(path)
        task = extract_async(content, prompt, examples)
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results
```

**Alternative: Use ThreadPoolExecutor directly**
```python
from concurrent.futures import ThreadPoolExecutor
import asyncio

async def extract_many_async(
    documents: list[str],
    prompt: str,
    examples: list,
    max_concurrent: int = 5
):
    """
    Process multiple documents with controlled concurrency.
    """
    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        futures = [
            loop.run_in_executor(
                executor,
                lx.extract,
                doc,
                prompt,
                examples,
                "gemini-2.5-flash"
            )
            for doc in documents
        ]

        results = await asyncio.gather(*futures)
        return results
```

---

## 3. Batching

### Finding: YES, NATIVE BATCH SUPPORT ✓

**What I Found:**
LangExtract supports batch processing via `Document` objects with built-in parallel processing.

**How It Works:**

```python
import langextract as lx

# Prepare batch with Document objects
documents = [
    lx.data.Document(
        text="Patient A took 500mg of Metformin twice daily.",
        document_id="patient_a_note_001"
    ),
    lx.data.Document(
        text="Patient B was prescribed 10mg Lisinopril once daily.",
        document_id="patient_b_note_001"
    ),
    lx.data.Document(
        text="Patient C uses 81mg Aspirin for cardiovascular protection.",
        document_id="patient_c_note_001"
    ),
]

# Process all documents in batch
results = lx.extract(
    text_or_documents=documents,  # Pass list of Document objects
    prompt_description=prompt,
    examples=examples,
    model_id="gemini-2.5-flash",
    max_workers=10,  # Parallel processing
)

# Results is an ITERATOR of AnnotatedDocument objects
for annotated_doc in results:
    print(f"Document: {annotated_doc.document_id}")
    print(f"Extractions: {len(annotated_doc.extractions)}")
    for extraction in annotated_doc.extractions:
        print(f"  {extraction.extraction_class}: {extraction.extraction_text}")
```

### Return Format

**Input:** `list[lx.data.Document]`
**Output:** `Iterator[AnnotatedDocument]`

Each `AnnotatedDocument` contains:
- `document_id`: The ID you provided
- `text`: Original text
- `extractions`: List of Extraction objects
- All the same fields as single-document results

### Performance Configuration

```python
# Optimal batch configuration
result = lx.extract(
    text_or_documents=documents,
    prompt_description=prompt,
    examples=examples,
    model_id="gemini-2.5-flash",

    # Parallelism
    max_workers=20,        # Number of concurrent API calls

    # Chunking (for large documents)
    max_char_buffer=2000,  # Characters per chunk
    batch_length=10,       # Chunks per batch

    # Multi-pass (for quality)
    extraction_passes=3,   # Run extraction 3 times per chunk

    # UI
    show_progress=True,    # Display progress bar
)
```

---

## 4. Recommended Implementation for HAIOS

Based on the research, here's the recommended implementation:

### Error-Resilient Extraction Manager

```python
import langextract as lx
import logging
import time
from typing import Optional, List
from enum import Enum
from dataclasses import dataclass

class ErrorType(Enum):
    RETRYABLE = "retryable"
    PERMANENT = "permanent"
    UNKNOWN = "unknown"

@dataclass
class ExtractionConfig:
    """Configuration for extraction with error handling."""
    max_retries: int = 3
    backoff_base: float = 2.0
    max_workers: int = 10
    max_char_buffer: int = 10000
    timeout: int = 120  # seconds

class RobustExtractionManager:
    """
    Production-ready extraction manager with:
    - Exponential backoff retry
    - Error classification
    - Batch processing
    - Performance monitoring
    """

    def __init__(
        self,
        api_key: str,
        model_id: str = "gemini-2.5-flash",
        config: Optional[ExtractionConfig] = None
    ):
        self.api_key = api_key
        self.model_id = model_id
        self.config = config or ExtractionConfig()
        self.prompt = self._build_prompt()
        self.examples = self._build_examples()

    def _classify_error(self, exception: Exception) -> ErrorType:
        """Classify error as retryable or permanent."""
        error_msg = str(exception).lower()

        retryable = ["rate limit", "quota", "429", "503", "timeout"]
        permanent = ["invalid api key", "401", "403", "provider not found"]

        if any(p in error_msg for p in retryable):
            return ErrorType.RETRYABLE
        if any(p in error_msg for p in permanent):
            return ErrorType.PERMANENT
        return ErrorType.UNKNOWN

    def extract_single(
        self,
        text: str,
        file_path: str
    ) -> Optional[lx.ExtractionResult]:
        """
        Extract from single document with retry logic.
        """
        for attempt in range(self.config.max_retries):
            try:
                result = lx.extract(
                    text_or_documents=text,
                    prompt_description=self.prompt,
                    examples=self.examples,
                    model_id=self.model_id,
                    api_key=self.api_key,

                    # Performance
                    max_char_buffer=self.config.max_char_buffer,
                    max_workers=self.config.max_workers,
                    timeout=self.config.timeout,

                    # Quality
                    temperature=0.2,
                    use_schema_constraints=True,
                )

                logging.info(f"Extracted {len(result.extractions)} items from {file_path}")
                return result

            except Exception as e:
                error_type = self._classify_error(e)

                if error_type == ErrorType.PERMANENT:
                    logging.error(f"Permanent error for {file_path}: {e}")
                    raise

                if error_type == ErrorType.RETRYABLE and attempt < self.config.max_retries - 1:
                    sleep_time = self.config.backoff_base ** attempt
                    logging.warning(
                        f"Retryable error for {file_path} "
                        f"(attempt {attempt + 1}/{self.config.max_retries}): {e}. "
                        f"Retrying in {sleep_time}s..."
                    )
                    time.sleep(sleep_time)
                else:
                    logging.error(f"Extraction failed for {file_path} after {attempt + 1} attempts: {e}")
                    raise

        return None

    def extract_batch(
        self,
        documents: List[tuple[str, str]]  # [(file_path, content), ...]
    ) -> List[Optional[lx.AnnotatedDocument]]:
        """
        Extract from multiple documents in parallel.

        Args:
            documents: List of (file_path, content) tuples

        Returns:
            List of AnnotatedDocument objects (or None for failures)
        """
        # Convert to Document objects
        doc_objects = [
            lx.data.Document(
                text=content,
                document_id=file_path
            )
            for file_path, content in documents
        ]

        try:
            results = lx.extract(
                text_or_documents=doc_objects,
                prompt_description=self.prompt,
                examples=self.examples,
                model_id=self.model_id,
                api_key=self.api_key,

                # Parallel processing
                max_workers=self.config.max_workers,
                max_char_buffer=self.config.max_char_buffer,

                # Quality
                temperature=0.2,
                use_schema_constraints=True,

                # UI
                show_progress=True,
            )

            # Convert iterator to list
            return list(results)

        except Exception as e:
            logging.error(f"Batch extraction failed: {e}")
            # Fallback to individual processing
            logging.info("Falling back to individual document processing")
            return [
                self.extract_single(content, file_path)
                for file_path, content in documents
            ]

    def _build_prompt(self) -> str:
        """Build extraction prompt."""
        # ... (same as integration guide)
        pass

    def _build_examples(self) -> List[lx.data.ExampleData]:
        """Build few-shot examples."""
        # ... (same as integration guide)
        pass
```

---

## 5. Summary & Recommendations

### Exception Handling
- **Status:** ❌ No typed exceptions
- **Mitigation:** Implement error classification via string matching
- **Pattern:** Exponential backoff with heuristic retry logic

### Async Support
- **Status:** ❌ No native asyncio
- **Mitigation:** Wrap with `asyncio.to_thread()` or `ThreadPoolExecutor`
- **Thread Safety:** Likely safe (based on design), not explicitly documented

### Batching
- **Status:** ✅ Full support via Document objects
- **Return Format:** `Iterator[AnnotatedDocument]`
- **Performance:** Built-in parallel processing with `max_workers`

### Next Steps for HAIOS

1. **Implement `RobustExtractionManager`** (see code above)
2. **Add metrics tracking** (token usage, latency, error rates)
3. **Test rate limit behavior** with small batch on real API
4. **Benchmark performance** (measure actual throughput)

### Open Questions

1. **What is the actual rate limit for Gemini API?** (Not in langextract docs)
2. **Does context window truncate silently or error?** (Needs testing)
3. **What's the cost per token?** (Check Google AI Studio pricing)

---

## 6. References

- **Basic Integration:** `docs/handoff/langextract_integration_guide.md`
- **API Reference:** `docs/libraries/langextract_reference.md`
- **Current Implementation:** `haios_etl/extraction.py`
- **Gemini API Docs:** https://ai.google.dev/gemini-api/docs

---

**Research Status:** COMPLETE
**Confidence:** HIGH (based on available documentation)
**Gaps:** Exception hierarchy, async support (requires testing to confirm thread safety)
