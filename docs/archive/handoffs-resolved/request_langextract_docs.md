# Documentation Request: langextract

**Target Library:** `langextract`
**Current Issue:** `Extraction failed: Examples are required for reliable extraction.`
**Context:** 
We are using `langextract.extract(content)` but it seems to require a schema definition with examples. We have a schema file at `docs/specs/langextract_schema_v1.yml` but we don't know how to pass it to the library.

**Request:**
Please research the `langextract` library and provide:
1.  **Function Signature:** What arguments does `extract()` accept?
2.  **Schema Format:** How do we define entities and concepts?
3.  **Examples:** How do we provide "ExampleData" or "examples" as required by the error message?
4.  **Code Snippet:** A working example of how to call `extract()` with a custom schema and examples.

**Reference Files:**
- `docs/specs/langextract_schema_v1.yml` (Our desired schema)
- `haios_etl/extraction.py` (Our current implementation)
