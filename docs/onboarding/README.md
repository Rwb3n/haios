# HAiOS Developer On-Boarding Guide

Welcome to Hybrid_AI_OS (HAiOS)!  This short guide orients new contributors to the
project's architecture, operational phases, and key reference material.

## 1. Project Essence
HAiOS is an **operating-system-like orchestration layer** for AI-assisted project
execution.  All activity is governed by structured *OS Control Files* and rich
*Project Artifact Files*, with strict JSON-schema contracts codified in our ADRs
and documentation volumes.

*Start here if you are new:* skim the **Overall Mandate & Core Principles**
(`docs/Document_1/I-OVERALL_MANDATE_CORE_PRINCIPLES.md`).  It explains the
multi-phase lifecycle: **ANALYZE → BLUEPRINT → CONSTRUCT → VALIDATE → IDLE**.

## 2. Foundational Narrative (Genesis & Cody Reports)
The `docs/Cody_Reports` directory captures the evolutionary story of HAiOS.
Reading them gives instant historical context & rationale behind design choices.

* `Genesis_Architect_Notes.md` – philosophical ground truth; why structured-mistrust exists.
* `Cody_Report_0001.md` – Phase-0 completion & readiness for MVP (Phase 1).
* `Cody_Report_0002.md` – early lessons: fast-track remediation & critique loops.
* `Cody_Report_0003.md` – v2 engine refactor summary & Sparse Priming Representation.
* `Cody_Report_0004.md` – v3 compliance hardening; readiness checks & snapshots.
* `Cody_Report_0005.md` – v3.1 evidence-driven validation; full test pyramid.

Skim these chronologically to understand *why* each architectural element
exists before diving into the technical specs.

## 3. Architectural Decision Records (ADRs)
The `docs/ADR` folder contains the canonical decisions shaping the engine.
A quick reading order:

1. `ADR-OS-001`  – Folder taxonomy & control file conventions.
2. `ADR-OS-006`  – Registry map integrity & schema validation.
3. `ADR-OS-013`  – Pre-Execution Readiness Check logic.
4. `ADR-OS-016`  – Snapshot handling & rotation.
5. `ADR-OS-018`  – Security baseline (Vault, isolation, kill-switches).
6. `ADR-OS-019`  – Observability & budget enforcement.
7. `ADR-OS-020`  – Developer **DEV_FAST** runtime mode.

Each ADR is **immutable once approved**; newer changes extend via superseding
records rather than edits.

## 4. Roadmaps
High-level progress and milestone tracking lives in `docs/roadmaps`:

* `roadmap_main.md` – end-to-end vision from Phase 0 foundations to the ADK.
* `phase1_v2.md`  – Titanium sprint breakdown for **Phase 1 (Core Engine)**.
* `phase1_to_2.md` – Contract bridge between Phase 1 and the multi-agent Phase 2.

## 5. Core Documentation Volumes
The three reference volumes elaborate on concepts, schemas, and scaffold spec:

* **Document 1** – Operational principles & phase logic (folder `docs/Document_1`).
* **Document 2** – All JSON-schema definitions (`docs/Document_2`).
* **Document 3** – Scaffold Definition Specification (`docs/Document_3`).

> Tip: keep Document 2 open while writing or reviewing any OS Control File.

## 6. Source Layout Cheat-Sheet
```
src/
  │   __main__.py         – CLI entry point ("haios run …")
  │   engine.py           – high-level orchestration loop
  │   plan_runner.py      – parses & advances execution plans
  │   task_executor.py    – executes individual tasks
  │   utils/              – shared helpers
  └── docs/onboarding/    – ← YOU ARE HERE
```

Tests live under `src/tests`; major scenario tests reside in `src/tests/task_exec`.

## 7. Error Handling Patterns & Best Practices

### 7.1 Exception Hierarchy & Propagation
HAiOS uses a structured exception hierarchy for proper error handling:

```python
# Security violations MUST propagate to engine level
except PathEscapeError:
    # Re-raise security violations so engine can handle with exit code 2
    raise
except Exception as e:
    # Handle other exceptions appropriately
    logger.error("operation_failed", err=str(e), exc_info=True)
    return False
```

### 7.2 Exit Code Standards
The engine follows strict exit code conventions:
- **0**: Success
- **1**: Internal/unexpected errors, task failures
- **2**: Security violations, configuration errors

### 7.3 Error Output Requirements
All error handlers must:
1. **Log structured data** via `logger.error()` for observability
2. **Write human-readable messages** to `stderr` for debugging
3. **Preserve exception context** with `exc_info=True` when appropriate

Example pattern:
```python
try:
    # Operation that might fail
    result = risky_operation()
except SpecificError as e:
    print(f"SpecificError: {e}", file=sys.stderr, flush=True)
    logger.error("operation_failed", err=str(e), exc_info=True)
    sys.exit(appropriate_code)
```

### 7.4 File Operation Safety
When modifying files that may be accessed concurrently:

1. **Read current state** before modifications to preserve concurrent changes
2. **Use atomic operations** via `atomic_write()` for consistency
3. **Handle Windows file locking** gracefully with appropriate fallbacks

Example:
```python
# Read current file state to preserve concurrent modifications
try:
    if file_path.exists():
        current_data = json.loads(file_path.read_text(encoding='utf-8'))
    else:
        current_data = default_structure
except (json.JSONDecodeError, IOError):
    current_data = fallback_structure

# Modify data
current_data.update(new_changes)

# Atomic write
atomic_write(file_path, json.dumps(current_data, indent=2))
```

## 8. Code Review Standards

### 8.1 Error Handling Review Checklist
When reviewing code changes, ensure:

- [ ] **Security exceptions** (`PathEscapeError`, `SecurityError`) are not caught generically
- [ ] **Appropriate exit codes** are used (0/1/2 pattern)
- [ ] **Both structured logging AND stderr output** are present for errors
- [ ] **File operations** preserve concurrent modifications where applicable
- [ ] **Exception context** is preserved with `exc_info=True` for debugging

### 8.2 Test Coverage Requirements
All changes must include:

- [ ] **Unit tests** for new functionality
- [ ] **Error scenario tests** for exception paths
- [ ] **E2E tests** for user-facing features
- [ ] **Schema validation** for any JSON structure changes

### 8.3 Import and Dependency Standards
- [ ] **Required imports** are present (`sys` for stderr, `json` for data handling)
- [ ] **Exception classes** are imported from appropriate modules
- [ ] **No circular dependencies** introduced
- [ ] **Minimal import footprint** maintained

### 8.4 Documentation Standards
- [ ] **Error conditions** documented in docstrings
- [ ] **Exit codes** specified for CLI-facing functions
- [ ] **Concurrency considerations** noted for file operations
- [ ] **Schema changes** reflected in Document 2

## 9. Getting Started Locally
1. `python -m pip install -r requirements.txt`
2. Run the demo plan in **DEV_FAST** mode:
   ```bash
   python -m src --demo --mode dev-fast | cat
   ```
3. Inspect generated artifacts under `core_scaffold/os_root`.

## 10. Contributing Workflow
1. Create/modify *plan* or *task* definitions **via code edits**, never manual
   runtime tweaks inside `os_root`.
2. Ensure your changes pass strict JSON-schema validation (`make validate`).
3. Run unit tests (`pytest -q`).  Aim for ≥ 85 % coverage.
4. **Follow error handling patterns** outlined in Section 7.
5. **Apply code review standards** from Section 8 during self-review.
6. Commit messages reference ADR numbers if you're changing behaviour guarded by
   those decisions.

---
Happy hacking!  Reach out via the `human_attention_queue.txt` for guidance or
approvals when required. 