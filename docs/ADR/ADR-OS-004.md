# ADR-OS-004: Global Event Tracking & Versioning (`g` and `v`)

*   **Status:** Proposed
*   **Date:** 2025-06-06
*   **Context:**
    In an event-driven, asynchronous system where multiple actions can occur over time, a reliable mechanism is needed to sequence events, establish causality, ensure data integrity, and provide a comprehensive audit trail. 
    Simple timestamps are prone to clock skew and don't provide a clear, causal sequence of OS-level events. 
    Furthermore, when multiple agents could potentially interact with OS Control Files, a mechanism to prevent race conditions and stale data writes is required.

*   **Decision:**
    We will adopt a dual-mechanism approach for system-wide event tracking and versioning:

    1.  **Global Event Counter (`g`):** A single, monotonically increasing integer, stored in `state.txt`, that is incremented for every significant OS action (e.g., phase transition, plan creation, task execution, issue logging, artifact registration). This `g` value will be used extensively for:
        *   **Sequencing:** Providing an unambiguous order of events across the entire system.
        *   **Timestamping:** Fields like `g_created`, `g_updated`, `g_decision` will store the `g` value at which the event occurred.
        *   **Unique ID Generation:** `g` will be a primary component in generating unique, chronologically-sortable IDs for OS artifacts like `request_<g>.txt`, `init_plan_<g>.txt`, `issue_<g>.txt`, etc.

    2.  **Instance Version Counter (`v`):** A per-file, integer-based version counter, present in the schema of all mutable OS Control Files (e.g., `state.txt`, `init_plan_*.txt`, `exec_plan_*.txt`, `issues_summary.txt`, etc.).
        *   **Purpose (Optimistic Locking):** To prevent stale writes. When the OS reads an OS Control File, it notes its `v` value. When it writes back, it checks if the `v` value on disk is still the same. If it is, the write proceeds, and the `v` value is incremented. If it's not (meaning another process changed the file), the write fails, forcing the current process to re-read the file and re-evaluate its action based on the newer data.
        *   **Scope:** The `v` counter is specific to each file instance.

*   **Rationale:**
    *   **Causal Ordering (`g`):** A monotonic counter provides a simpler and more reliable way to establish a "happened-before" relationship between events than wall-clock time, which is not guaranteed to be monotonic or consistent across different environments. It forms the backbone of the system's historical record.
    *   **Data Integrity (`v`):** Optimistic locking is a lightweight and effective strategy for ensuring data consistency in a system where concurrent writes to state files are possible (especially in a future multi-agent or asynchronous OS) but not expected to be highly frequent. It prevents agents from overwriting each other's changes based on stale information.
    *   **Simplicity & Durability:** Both `g` and `v` are simple integers that are easily stored and managed within our JSON-based OS Control Files, requiring no external services. Their values are persisted alongside the data they protect.

*   **Implementation Details:**
    *   The authoritative global `g` counter is the `g` field within `state.txt` (or its `os_file_header.g_file_last_modified` if using the headered format). All OS actions that need to increment the global clock must do so by updating `state.txt`.
    *   The `v` counter is a required field in the schema of every OS Control File that is designed to be read and then written back to. It must be incremented on every successful write.
    *   Project Artifacts (e.g., source code, reports) use a different versioning scheme (`version_tag` in their `EmbeddedAnnotationBlock`), which is semantic (e.g., "1.2.0") or hash-based, as it reflects the version of the *content*, not the OS's internal state management. The `g` counter is still used heavily within annotations (`g_last_modified_content`, etc.) to link content changes back to the global event timeline.

*   **Consequences:**
    *   **Pros:**
        *   Provides a robust, system-wide, ordered log of all significant events.
        *   Prevents data corruption from stale writes to critical OS state files.
        *   Creates unique, time-ordered, and human-readable IDs for core entities.
        *   Simple to implement and maintain.
    *   **Cons:**
        *   `state.txt` becomes a point of high contention, as many actions need to increment `g`. The OS logic must handle updates to `state.txt` efficiently and atomically.
        *   The logic for every agent/process that modifies an OS Control File must correctly implement the read-check-increment-write cycle for the `v` field.

*   **Alternatives Considered:**
    *   **Timestamp-based Versioning (e.g., `ETag` with Last-Modified):** Common in web protocols, but relies on synchronized clocks and doesn't provide a simple, sequential event count. Our `g` counter is superior for OS-internal event sequencing.
    *   **Pessimistic Locking (File Locks):** The OS would have to acquire an exclusive lock on a file before reading/writing. This can be complex to manage (especially handling stale locks) and can reduce concurrency. Optimistic locking is generally preferred when write conflicts are expected to be infrequent.