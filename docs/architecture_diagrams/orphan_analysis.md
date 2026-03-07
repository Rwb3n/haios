# HAIOS Orphan Analysis Report
**Audit Scope**: `.claude/agents`, `.claude/skills`, `.claude/hooks`, and `haios_etl/`.

An "orphan" in this system is defined as a component that exists on disk but is completely disconnected from the execution graph—meaning it is not permitted in `settings.local.json`, not invoked dynamically via `Task()`, or not imported by any other Python module.

---

## 1. Orphaned Skills (Unregistered in `settings.local.json`)
The L4 system relies on `settings.local.json` to explicitly allow `Skill(name)` commands. The following skills exist in `.claude/skills/` but are **not registered or permitted** in the local settings file. They cannot be invoked by Claude natively:

* **Ceremony Skills**: 
  * `close-arc-ceremony`, `close-chapter-ceremony`, `close-epoch-ceremony`, `open-epoch-ceremony`
  * `memory-commit-ceremony`, `session-start-ceremony`, `session-end-ceremony`, `spawn-work-ceremony`
* **Queue Management Skills**:
  * `queue-commit`, `queue-intake`, `queue-prioritize`, `queue-unpark`
* **Workflow Skills**:
  * `retro-cycle`, `ground-cycle`, `routing-gate`, `extract-content`, `schema-ref`

**Root Cause**: These appear to be either stubs generated during a retrograde test suite (`tests/test_ceremony_retrofit.py`), or they are Epoch 2.9/3.0 capabilities that were scaffolded out but never fully wired into the runtime configuration.

---

## 2. Orphaned Legacy Agents (`.claude/agents/`)
With the migration to the `.claude/skills/*/SKILL.md` architecture (and sub-agents natively supported by Claude Code), many legacy agent Markdown files are completely dead code.

**True Orphans:**
* `close-work-cycle-agent.md`
* `implementation-cycle-agent.md`
* `investigation-cycle-agent.md`
* `investigation-agent.md`
* `why-capturer.md`

**Partial Orphan:**
* `schema-verifier.md` (Not invoked dynamically, though intended to be a SQL hard-gate according to `haios.yaml`).

*(Note: `preflight-checker`, `test-runner`, `validation-agent`, `critique-agent`, and `anti-pattern-checker` are actively invoked dynamically via `Task(subagent_type=...)` inside active skills).*

**Root Cause**: These are L2/L3 legacy artifacts from before the `-cycle` functionality was converted to the standalone `skills/` architecture format. 

---

## 3. Orphaned Python Modules (`haios_etl/`)
The `haios_etl/` directory acts as the data and cognitive memory engine. However, several scripts are functionally dead:

**True Orphans:**
* `quality.py` (No imports across the codebase, only referenced in the README as a "Metrics Collection" layer).
* `health_checks.py` (Exclusively imported by the test suite and explicitly marked as `# Deprecated module` in `WORK/E2-270` plans).
* `job_registry.py` (Exclusively imported by the test suite and explicitly marked as `# Deprecated module` in `WORK/E2-270` plans).

**Root Cause**: The scope of the ETL shifted towards the ReasoningBank and dynamic semantic retrieval (`retrieval.py`/`synthesis.py`). The health check and job-registry functionality was likely abandoned or superseded by the `hook_dispatcher.py` event loop.

## 4. Active Engine Cores (Not Orphans)
**Status: Perfect hygiene.**
* `.claude/hooks/`: All four hook listener scripts are actively wired into `settings.local.json`.
* `.claude/haios/modules/` & `.claude/haios/lib/`: A comprehensive `grep` audit of these 50+ Python files (`work_engine`, `cycle_runner`, `ceremony_contracts`, etc.) revealed over 600 active import references, primarily driven by a rigorous and heavily maintained `tests/` directory. These directories form the legitimate backbone of the Epoch 2.5+ Independent Lifecycles architecture and contain **zero orphans**.
