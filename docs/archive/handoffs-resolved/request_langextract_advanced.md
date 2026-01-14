# Documentation Request: langextract (Advanced)

**Target Library:** `langextract`
**Purpose:** Session 5 (Error Handling & Performance)

**Context:**
We have a working synchronous integration. Now we need to implement robust error handling (retries, backoff) and optimize performance.

**Request:**
Please provide details on:
1.  **Exception Hierarchy:** What specific exceptions does `langextract` raise?
    -   Is there a specific `RateLimitError`?
    -   Is there a `ContextWindowExceededError`?
    -   How do we distinguish transient errors (retryable) from permanent errors (bad request)?
2.  **Async Support:** Does `langextract` support `asyncio`?
    -   Is there an `alx.extract` or similar async method?
    -   If not, is it thread-safe for use with `ThreadPoolExecutor`?
3.  **Batching:** Does `extract()` support batching multiple documents?
    -   If so, what is the return format?

**Reference:**
-   Current usage: `haios_etl/extraction.py`
