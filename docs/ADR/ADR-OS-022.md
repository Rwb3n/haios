# ADR-OS-022: Mechanical Inventory Buffer

* **Status**: Proposed
* **Date**: 2025-06-23
* **Deciders**: Architecture Team
* **Reviewed By**: \[TBD]

---

## Context

After contextâ€‘drift events (e.g., agent restart, truncated prompt, or file lock contention) AI Builder agents sometimes regenerate artifacts that already exist, wasting compute and occasionally overwriting newer work.  In Eliyahu Goldrattâ€™s *The Goal* the production line solves a similar problem with physical buffers of inventory staged before each workâ€‘centre.  We will replicate that idea by giving every **execution plan** and optionally each **task node** an explicit, versioned **mechanical inventory** of reusable items (code snippets, credentials, preâ€‘computed results, file handles, etc.).  Agents consume from the buffer instead of reâ€‘creating resources, and Supervisor/Manager agents own mutation rights.

## Assumptions

* [ ] Plan-level inventory captures all shared resources required by multiple tasks.
* [ ] Task-level inventory contains only items relevant to that specific node.
* [ ] Inventory state is persisted in Git-tracked annotation blocks; delta logs guarantee crash safety.
* [ ] Garbage-collection keeps annotation files from unbounded growth.
* [ ] The inventory buffer protocol is robust against race conditions, zombie reservations, and log replay errors.
* [ ] The system can detect and recover from inventory/annotation desynchronization or corruption.
* [ ] All compliance requirements from referenced ADRs (e.g., ADR-OS-023, ADR-OS-024, ADR-OS-027, ADR-OS-029, ADR-OS-032) are up-to-date and enforced.

## Decision

1. **Twoâ€‘tier Scope**
   *Planâ€‘level* inventory lives in the executionâ€‘plan annotation; *taskâ€‘level* inventory lives in each taskâ€™s annotation block.

2. **Persistent, Fileâ€‘backed Storage**
   Inventory arrays sit inside the existing `EmbeddedAnnotationBlock` payload.  On engine restart the orchestrator reâ€‘hydrates from disk and replays `inventory_delta_<g>.log` files.

3. **Optimistic Reservation Protocol**
   First consumer marks an item `RESERVED` with its `agent_id`; the same agent must promote to `CONSUMED` or the janitor will roll back.

4. **Expiration & Garbage Collection**
   Every item must carry `expires_at_g` **or** `ttl_seconds`.  A Supervisor janitor loop prunes items every **100 global events** (default; configurable).

5. **Delta Logging**
   Every mutation (create, reserve, consume, expire) is appended to a compact, appendâ€‘only delta file so no updates are lost across crashes.

6. **Access Control**
   *Manager* & *Supervisor* agents have **read/write**; *Builder* agents have **readâ€‘only**.  Builder requests to add inventory must be escalated via an `ADD_INVENTORY` task handled by Manager.

**Confidence:** Medium

## Schema Changes (versionÂ `2.1`)

```diff
   // --- Mechanical Inventory Buffer ---
+  "inventory": [
+    {
+      "item_id": "str",                  // unique identifier
+      "item_type": "str",                // CODE_SNIPPET | RESULT | FILE_HANDLE | CREDENTIAL | â€¦
+      "quantity": 1,                       // integer >=Â 0
+      "meta": { â€¦ },                      // freeâ€‘form metadata
+      "lifecycle_status": "CREATED|RESERVED|CONSUMED|EXPIRED",
+      "reserved_by_agent_id": "str|null",
+      "g_created": 123,
+      "g_last_modified": 125,
+      "expires_at_g": 225,                // OR null
+      "ttl_seconds": 604800               // OR null (one week)
+    }
+  ]|null,
```

`inventory_delta_<g>.log` (appendâ€‘only):

```text
<g> CREATED  item_id=snippet_42  item_type=CODE_SNIPPET  qty=1 â€¦
<g> RESERVED item_id=snippet_42  by=agent.build.7
<g> CONSUMED item_id=snippet_42  by=agent.build.7
```

## Rationale

1. **Stops Redundant Work**
   Items fetched once are reâ€‘used many times.
   *Selfâ€‘critique*: Could outdated snippets cause stale bugs?
   *Confidence*: Medium
2. **Versionâ€‘Controlled Truth**
   Git history gives audit & rollback.
   *Selfâ€‘critique*: Commits may bloat; GC mitigates.
   *Confidence*: High
3. **Crashâ€‘Safe via Delta Log**
   No singleâ€file commit race.
   *Selfâ€‘critique*: One more control file to manage.
   *Confidence*: High
4. **Minimal Locking Overhead**
   Optimistic reservation avoids a lock server.
   *Selfâ€‘critique*: Zombie reservations require janitor cleanup.
   *Confidence*: Medium

## Alternatives Considered

| Alternative                           | Reason Rejected                                     | Confidence |
| ------------------------------------- | --------------------------------------------------- | ---------- |
| Global shared inventory only          | Hard to enforce task isolation, high contention     | High       |
| Ephemeral inâ€‘memory cache             | Lost after restart; canâ€™t audit                     | Medium     |
| Heavyweight distributed cache (Redis) | Adds infra complexity, violates fileâ€‘centric design | High       |

### Distributed Systems Implications

This inventory system is a microcosm of a distributed state machine and MUST adhere to the following policies:

*   **Idempotency (ADR-OS-023):** All inventory operations (create, reserve, consume, expire) MUST be idempotent. A retried operation to create `item_id_42` must succeed without creating a duplicate.
*   **Asynchronicity (ADR-OS-024):** The `inventory_delta_<g>.log` is an event stream. Agents MUST publish events to this stream asynchronously. A dedicated "Inventory Manager" agent or service should be responsible for consuming this stream and updating the canonical state in the `EmbeddedAnnotationBlock`.
*   **Event Ordering (ADR-OS-027):** The `g` counter in the delta log provides a total ordering. For more complex, causally-related inventory operations, vector clocks MUST be added to the event schema to ensure the state can be correctly reconstructed even if logs are processed out of order.
*   **Observability (ADR-OS-029):** Every event written to the delta log MUST be part of a distributed trace. This allows for complete visibility into an item's lifecycle, from creation to consumption, across multiple agents and tasks.

## Consequences

* **Positive**: Reduces regeneration churn; enforces deterministic reuse; provides audit trail.
* **Negative**: Slight schema complexity and janitor overhead; larger file diffs.

## Clarifying Questions

* Should janitor cadence be configurable per project (e.g., time-based vs. g-based), and what are the trade-offs for different project sizes and agent activity levels?
* What policy governs Builder requests to escalate `ADD_INVENTORY` tasks, and how are these requests audited and approved?
* Do we need a separate retention policy for consumed items, or is garbage collection (GC) sufficient for all inventory types?
* How does the system ensure distributed consistency and recovery from log replay errors, zombie reservations, or annotation desynchronization?
* What is the process for evolving the inventory item schema and protocol as new resource types or lifecycle states are introduced?

---

*See ADR-OS-021 for the overall Assumption-Surfacing pattern.  Schema bump from 2.0 → 2.1 is backward compatible (empty inventory arrays are valid under 2.1).*

