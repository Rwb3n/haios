---
template: investigation
status: complete
date: 2025-12-19
backlog_id: INV-017
title: "Investigation: Observability Gap Analysis"
author: Hephaestus
session: 86
lifecycle_phase: conclude
spawned_by: Session-86
related: [E2-081, E2-007, E2-084, ADR-037, E2-102, E2-103, E2-130]
milestone: M3-Cycles
version: "1.2"
closed_session: 102
closure_note: "All spawned items complete. E2-102 (heartbeat): complete. E2-103 (failure_reason): complete. E2-104 (tool_error type): absorbed into E2-130. Findings remain valid post-Python migration."
generated: 2025-12-23
last_updated: 2025-12-23T11:02:07
---
# Investigation: Observability Gap Analysis

@docs/README.md
@docs/epistemic_state.md
@.claude/hooks/ErrorCapture.ps1

---

## Context

Session 86 began with a meta-question: "How is our system performing? Do we have observability on anomalies?"

This prompted a systematic audit of HAIOS observability infrastructure to assess:
1. What telemetry exists and is working
2. What gaps exist in anomaly detection
3. Whether observability investment is valuable at current scale

---

## Objective

Determine the current observability posture of HAIOS and identify low-cost wins that improve system health visibility without over-engineering.

---

## Scope

### In Scope
- Event logging (E2-084)
- Error capture hook (E2-007)
- ReasoningBank failure tracking
- Memory health metrics
- Heartbeat scheduler (E2-081)
- Session delta tracking (E2-078)

### Out of Scope
- ML-based anomaly detection
- External monitoring services
- Production deployment concerns
- Multi-operator scenarios

---

## Hypotheses

1. **H1:** ErrorCapture hook is wired but not effectively differentiating error types in memory
2. **H2:** Heartbeat scheduler (E2-081) is designed but not executing
3. **H3:** ReasoningBank captures failure occurrence but not failure reasons
4. **H4:** Current observability is adequate for single-operator development phase

---

## Investigation Steps

1. [x] Query event log statistics
2. [x] Check memory stats and health
3. [x] Verify ErrorCapture hook is wired in settings.local.json
4. [x] Query reasoning_traces for failure patterns
5. [x] Check heartbeat event count vs expected
6. [x] Assess error-related concept types

---

## Findings

### What IS Working

| Component | Evidence | Assessment |
|-----------|----------|------------|
| **Memory Storage** | 72,372 concepts, 8,250 entities | Healthy |
| **Embedding Coverage** | 69,636 / 72,372 (96%) | Good |
| **ReasoningBank** | 1,501 traces (57% success, 42% partial, <1% failure) | Active |
| **Event Log** | 26 cascades, 12 session events | Functional |
| **Session Tracking** | Session deltas computed in haios-status-slim.json | Working |
| **ErrorCapture Hook** | Wired in PostToolUse chain (settings.local.json:134) | Present |

### What is NOT Working / Missing

| Gap | Evidence | Impact |
|-----|----------|--------|
| **Heartbeat not scheduled** | Only 1 heartbeat event vs 26 cascades | No periodic health checks |
| **Failure reasons null** | 7 failures in reasoning_traces, all with `failure_reason = NULL` | Lost diagnostic context |
| **No error type differentiation** | No `tool_error` concept type in 110+ types | Errors mixed into generic types |
| **No anomaly detection** | No trending or alerting infrastructure | Blind to drift patterns |
| **No cross-session trending** | Session deltas exist but not aggregated historically | No longitudinal view |

### Quantitative Assessment

```
Event Log:
- heartbeat: 1 (ANOMALY - should be many if scheduled)
- cascade: 26 (normal - tracks completions)
- session: 12 (normal - 6 sessions * 2 events each)

ReasoningBank Outcomes:
- success: 861 (57%)
- partial_success: 633 (42%)
- failure: 7 (<1%)

Error-Related Concepts (containing "error" or "Error"):
- Critique: 658
- SynthesizedInsight: 443
- Directive: 380
(No dedicated error type exists)
```

### H1 Confirmed
ErrorCapture.ps1 is wired but stores errors without a dedicated type. Errors flow through the generic ingester and get classified as Critique/Directive/etc based on content, not source.

### H2 Confirmed
E2-081 designed heartbeat with Windows Task Scheduler, but `setup-heartbeat-task.ps1` was never executed to register the scheduled task. Single heartbeat event is manual test.

### H3 Confirmed
ReasoningBank `failure_reason` column exists but Stop hook extraction does not populate it. We know WHAT failed but not WHY.

### H4 Confirmed
At current scale (single operator, ~85 sessions, manual oversight), the system is survivable. Gaps become critical at scale or when trust is external.

---

## Spawned Work Items

Low-cost wins that address gaps without over-engineering:

- [ ] **E2-102:** Execute heartbeat scheduler setup (run `setup-heartbeat-task.ps1`)
- [ ] **E2-103:** Populate failure_reason in Stop hook extraction
- [ ] **E2-104:** Add dedicated `tool_error` concept type to ErrorCapture flow

Deferred (not valuable at current scale):
- ML-based anomaly detection
- Automated alerting
- Performance regression tracking
- Cross-session trending dashboard

---

## Expected Deliverables

- [x] Findings report (this document)
- [x] Recommendations (spawned work items)
- [ ] Memory storage (concepts) - pending closure

---

## References

- `.claude/hooks/ErrorCapture.ps1` - Error capture implementation
- `.claude/hooks/setup-heartbeat-task.ps1` - Heartbeat scheduler setup
- `docs/plans/PLAN-E2-081-heartbeat-scheduler.md` - Heartbeat design
- `docs/plans/PLAN-E2-007-ERROR-CAPTURE-HOOK.md` - Error capture design
- `haios_etl/retrieval.py` - ReasoningBank implementation

---
