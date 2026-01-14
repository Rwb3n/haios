---
template: implementation_plan
status: complete
date: 2025-12-07
backlog_id: PLAN-INVESTIGATION-MEMORY-PROCESS-OBSERVABILITY
title: "Memory Process Observability Investigation"
author: Hephaestus
lifecycle_phase: plan
version: "1.0"
---
# generated: 2025-12-07
# System Auto: last updated on: 2025-12-09 18:48:54
# Implementation Plan: Memory Process Observability Investigation

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Ensure HAIOS has **comprehensive observability** across all layers so operators always know:
1. **What** is currently running (process identification)
2. **Where** it is (% complete, phase, stage)
3. **Whether** it's progressing (heartbeat, health)
4. **Why** it might be stuck (dependencies, locks, resources)

---

## Problem Statement

**Trigger:** Session 43 cross-pollination ran 39+ minutes with no progress indication after initial "Comparing X concepts against Y traces" log. Operator had no visibility into whether process was working or stuck.

**Root Cause:** Long-running loops lack progress logging. Only START and END logs exist.

**Impact:** Operator cannot make informed decisions about cancelling/continuing operations.

---

## OBSERVE: Observability Audit (4 Layers)

### Layer 1: Intra-Process (Function-Level Logging)

| Function | START Log | PROGRESS Log | END Log | Gap? |
|----------|-----------|--------------|---------|------|
| `find_similar_concepts()` | No | No | Yes (line 128) | HIGH |
| `find_similar_traces()` | No | No | Yes (line 163) | HIGH |
| `find_cross_type_overlaps()` | Yes (line 591) | **NO** | Yes (line 613) | **CRITICAL** |
| `run_synthesis_pipeline()` | Yes (stage logs) | Yes (every 100 bridges) | Yes | OK |
| `extract_from_file()` | No | No | No | Medium |
| `process_file()` | No | No | No | Medium |

### Layer 2: Inter-Process (Handoffs & Dependencies)

| Handoff | Visibility | Gap? |
|---------|------------|------|
| ETL → DB persist | Implicit (no confirmation log) | HIGH |
| DB → MCP query | None | HIGH |
| Synthesis → DB store | Implicit | Medium |
| Hook → MCP call | None | HIGH |
| Background job → Foreground | Shell ID only, no registry | **CRITICAL** |

### Layer 3: System Health (Resources & Services)

| Component | Health Check | Gap? |
|-----------|--------------|------|
| Database (SQLite) | None | HIGH |
| WAL file size | None | HIGH |
| DB locks/contention | None | **CRITICAL** |
| Memory usage | None | HIGH |
| Gemini API | Only on failure | Medium |
| MCP server | None (assumed running) | HIGH |
| Disk I/O | None | Medium |

### Layer 4: Operator Dashboard (Unified View)

| Need | Current State | Gap? |
|------|---------------|------|
| "What's running now?" | Must remember shell IDs | **CRITICAL** |
| "System healthy?" | `/status` partial | HIGH |
| "What phase is system in?" | Fragmented logs | HIGH |
| "Background job status?" | Manual BashOutput calls | HIGH |
| "Why is it slow/stuck?" | No diagnostics | **CRITICAL** |

---

## Proposed Changes

### Layer 1 Fix: Intra-Process Progress

#### 1a. CRITICAL: Comparison Loop (synthesis.py:593-611) - DONE (Session 43)
- [x] Add progress log every 10k comparisons OR every 10 seconds
- [x] Include: comparisons done, % complete, elapsed time, rate, ETA
- [x] Format: `"Progress: X/Y (Z%) - Ns elapsed - Rk/sec - ETA Ms"`

#### 1b. HIGH: Clustering Functions - DONE (Session 44)
- [x] Add progress in `_build_clusters()` loop (used by both find_similar_concepts/traces)
- [x] Format: `"Clustering progress: X/Y items (Z%) - Ns elapsed"`

#### 1c. Standard: Progress Helper
- [ ] Create `_log_progress(current, total, start_time)` helper
- [ ] Standardize format across all functions

### Layer 2 Fix: Inter-Process Visibility

#### 2a. CRITICAL: Background Job Registry - DONE (Session 44)
- [x] Create `haios_etl/job_registry.py` with `JobRegistry` class
- [x] Register job on start: `{shell_id, command, started_at, status, pid}`
- [x] Deregister on complete/fail (safe for nonexistent)
- [x] File persistence: `.claude/background_jobs.json`
- [x] 12 tests, all passing
- [ ] `/status` reads this registry (Phase 4)

#### 2b. HIGH: Handoff Confirmation Logs
- [ ] Log after DB persist: `"Stored concept {id} to DB"`
- [ ] Log after MCP call: `"MCP query completed in {ms}ms"`

### Layer 3 Fix: System Health Checks - DONE (Session 44)

#### 3a. CRITICAL: DB Health - DONE
- [x] Add `check_db_health()` function: WAL size, DB size, table count, accessibility
- [x] Log warnings if WAL > 100MB
- [x] Returns DBHealth dataclass with status

#### 3b. HIGH: Memory Check - DONE
- [x] Add `check_memory_health()` function using psutil
- [x] Warn if > 80% memory used, critical if > 95%
- [x] Returns MemoryHealth dataclass with usage stats

#### 3c. HIGH: MCP Health - DONE
- [x] Add `check_mcp_health()` function
- [x] Basic availability check (config exists)
- [x] 13 tests, all passing

### Layer 4 Fix: Operator Dashboard - DONE (Session 44)

#### 4a. CRITICAL: Enhanced `/status` - DONE
- [x] Show active background jobs (from registry)
- [x] Show DB health summary (status, WAL size)
- [x] Show memory health (status, usage %)
- [x] Show MCP health (status)
- [x] Updated .claude/commands/status.md

#### 4b. HIGH: New `/jobs` Command - DEFERRED
- [ ] List all background jobs with status (available via /status for now)
- [ ] Show elapsed time, last output line
- [ ] Allow `--cancel <id>`

---

## Verification

- [ ] Tests pass (current baseline)
- [ ] Run cross-pollination with new logging - confirm visibility
- [ ] Documentation updated (OPERATIONS.md)
- [ ] All long-running functions have progress logging

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Log spam | Low | Use time-based throttle (60s minimum between progress logs) |
| Performance overhead | Low | Logging is I/O, not CPU - minimal impact |
| Inconsistent formats | Medium | Define standard format, enforce in code review |

---

## References

- Session 43: Cross-pollination blind spot discovered
- Code: haios_etl/synthesis.py:593-611 (comparison loop)
- Code: haios_etl/synthesis.py:830 (existing bridge progress pattern)

---
