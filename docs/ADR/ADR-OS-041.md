UPDATE ADR-OS-041: Add a new "Architectural Decisions" section to the Rhiza ADR.
Content for the Update:
Decision: "The persistence layer for structured JSON artifacts (e.g., Raw_Research_Artifact) will utilize native JSON field types in the underlying SQLite/NocoDB database."
Rationale: "This choice prioritizes the need for direct queryability and indexing of nested fields within the artifacts, which is essential for future analytics, dashboarding, and advanced triage logic. It allows for more efficient data retrieval than parsing text blobs at the application layer."
Risk Mitigation:
Integrity: "To ensure the integrity of the original artifact, the application layer (the n8n Load Node) must compute a SHA-256 hash of the serialized JSON string before insertion and store this hash in a separate payload_hash column in the same table. This preserves the ability to verify the immutability of the original evidence."