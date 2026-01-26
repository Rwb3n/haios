---
id: CH-007
arc: observations
name: CheckpointGateFreshness
status: Active
created: 2026-01-26
spawned_from:
- obs-214-001
generated: '2026-01-26'
last_updated: '2026-01-26T19:29:21'
---
# Chapter: Checkpoint Gate Freshness Check

## Purpose

Make plan-validation-cycle checkpoint gate context-aware to avoid redundant checkpoints.

## Context

obs-214-001 documented that plan-validation-cycle creates checkpoints even when session just started from coldstart and no new context accumulated. This wastes tokens and creates noisy checkpoint history.

## Deliverables

1. Update plan-validation-cycle APPROVE phase
2. Add session freshness check before checkpoint
3. SHOULD checkpoint IF significant context accumulated
4. MAY skip IF session fresh from coldstart AND plan authored prior session

## Success Criteria

- [ ] plan-validation-cycle checks session freshness
- [ ] Redundant post-coldstart checkpoints avoided

## References

- obs-214-001: Checkpoint gate ignores freshness
- plan-validation-cycle SKILL.md
