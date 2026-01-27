---
id: CH-012
arc: configuration
name: HookValueAssessment
status: Active
created: 2026-01-27
spawned_from:
- obs-250-02
- WORK-027
generated: '2026-01-27'
last_updated: '2026-01-27T21:47:12'
---
# Chapter: Hook Value Assessment

## Purpose

Evaluate whether PostToolUse hooks (timestamp injection, YAML rewriting) provide net value vs the friction they introduce during batch operations.

## Context

Session 250 (WORK-027) revealed significant friction from the PostToolUse timestamp hook during batch file edits. The hook rewrites `last_updated` on every file save, causing "file modified since read" errors that force sequential re-reads. This roughly doubled tool calls for a mechanical migration task.

Question: Does the `last_updated` timestamp provide enough value to justify the friction, or should it be removed/made conditional?

## Traces

- L3.6: Graceful Degradation (hooks should not impede normal work)
- REQ-GOVERN-002: Governance hooks (PostToolUse is governance infrastructure)
- obs-250-02: mcp_server import chain broken (related hook infrastructure)
