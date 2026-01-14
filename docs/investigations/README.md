---
template: readme
status: active
date: 2025-12-11
component: investigations
---
# generated: 2025-12-11
# System Auto: last updated on: 2025-12-11 23:01:40
# Investigation Documents

@docs/README.md
@docs/ADR/ADR-034-document-ontology-work-lifecycle.md

---

## Purpose

Investigation documents capture the **DISCOVERY** phase of the work lifecycle (ADR-034).

Before designing (ADR) or planning (PLAN), agents should investigate:
- Problem analysis
- Root cause identification
- Option exploration
- Evidence gathering

---

## Naming Convention

```
INVESTIGATION-<backlog_id>-<slug>.md
```

Examples:
- `INVESTIGATION-INV-008-authentication-gap.md`
- `INVESTIGATION-E2-033-hook-performance.md`

---

## Creating Investigations

Use the `/new-investigation` command:

```
/new-investigation INV-008 Authentication Gap Analysis
```

This creates a properly templated investigation document.

---

## Lifecycle

1. Investigation starts in `status: active`
2. Document findings as investigation progresses
3. List spawned work items (ADRs, backlog items) in "Spawned Work Items" section
4. Store findings to memory via `ingester_ingest`
5. Close with `status: complete`

---

## ADR-034 Reference

This directory implements the canonical DISCOVERY phase:
- All analysis/research work uses INVESTIGATION- prefix
- Legacy prefixes (INQUIRY, RESEARCH, GAP-CLOSER, PROTOTYPE) are aliases
- Investigations MUST list spawned work items before closure (ADR-033 Section 2b)

---
