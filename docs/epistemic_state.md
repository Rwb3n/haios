# generated: 2025-12-09
# System Auto: last updated on: 2025-12-26T15:34:31
# Epistemic State: Operational Self-Awareness

> **Purpose:** Surface known behavioral patterns and knowledge gaps. Not a history log.
> **Philosophy:** These patterns are FEATURES of the architecture, not bugs. Leverage them, don't fight them.

---

## Known Behavioral Patterns (Anti-Patterns)

> **L1 Anti-Patterns:** See `.claude/config/invariants.md` for 6 fundamental LLM patterns (Assume over verify, Generate over retrieve, Move fast, Optimistic confidence, Pattern-match solutions, Ceremonial completion). Those are architectural truths that apply universally.

**Implementation-Specific Patterns (L2):**

| Tendency | Outcome | Mitigation | Memory Ref |
|----------|---------|------------|------------|
| PowerShell through bash | `$_` and `$variable` get eaten | Use Grep tool or proper escaping | 64677 |
| Static registration | New artifacts not discovered | Dynamic discovery functions + verify runtime discovery | 72331-72336 |

---

## Active Knowledge Gaps (Unknowns)

| Gap | Context | Backlog Ref |
|-----|---------|-------------|
| Strategy quality improvement | Generic strategies not actionable | INV-003, E2-017 |
| Entity embedding coverage | 0% entity embeddings | INV-004, E2-018 |
| Concept type consolidation | 110+ types, inconsistent | E2-019 |
| **ReasoningBank feedback loop** | Write-heavy, read-weak - no reinforcement signal | **INV-023** |

---

## Recently Surfaced (Session 50+)

- **Schema Discovery Gap**: RESOLVED. PreToolUse hook now blocks direct SQL, requires schema-verifier subagent. (E2-020, Session 50)
- **PowerShell-Bash Interop**: Recurring pattern where `$_` and `$variable` get mangled. Sessions 49, 50.
- **Memory Reference Governance**: Investigations should produce memory refs, backlog items should link to memory. (ADR-032, E2-021)
- **Work Item Lifecycle**: DoD defined (tests + WHY + docs + traced files). `/close` command enforces. (ADR-033, E2-031, E2-023, Session 56-58)
- **Static Registration Anti-Pattern**: RESOLVED. UpdateHaiosStatus.ps1 had hardcoded skills/agents/commands. Added dynamic discovery functions (Get-Skills, Get-Agents, Get-Commands). DoD should verify runtime discovery. (INV-012, Session 85)
- **Ceremonial Completion Anti-Pattern**: RESOLVED. E2-080 justfile created but `just scaffold` recipe was broken (passed non-existent params), slash commands never updated. Fixed Session 86 by enhancing ScaffoldTemplate.ps1 and updating all `/new-*` commands. Guardrail: DoD must include integration testing. (E2-105, Session 86)
- **README Sync Anti-Pattern**: RESOLVED. Documentation updates deferred to end-of-plan cleanup, causing stale READMEs. Fixed Session 92 by updating implementation_plan template: README sync is now a MUST step per phase, DoD requires "READMEs updated in all modified directories (upstream and downstream)". (Memory 76991-76999)
- **ReasoningBank Feedback Gap**: ACTIVE. Memory retrieval works (finds relevant concepts) but no feedback loop exists. Agent queries memory, gets results, but: (1) strategies returned are often meta/generic, (2) no mechanism to reinforce "this was useful", (3) learned discounting - agent skims results due to low signal-to-noise. Write-heavy, read-weak architecture. (INV-023, Session 98)
- **MCP Transient Tool Errors**: OBSERVING. During coldstart, `memory_search_with_experience` returned "No such tool available" but `memory_stats` succeeded immediately after, and retry of search worked. Possible causes: lazy initialization, IPC timing, tool registration race. Related to INV-028 (Agent Error Reporting Gap). (Session 111)
- **Close Command Status Sync Gap**: RESOLVED. `/close` was using `just update-status-slim` which doesn't update full `haios-status.json`. The `just ready` command reads full status, causing closed items to appear ready. Fixed E2-190: close now uses `just update-status`. (Session 119)
- **Work File Placeholder Gap**: RESOLVED. 8 work files had unpopulated Context/Deliverables sections. Added placeholder validation to work-creation-cycle READY phase (E2-191). Guardrails now detect `[Problem and root cause]` and `[Deliverable N]` placeholders. (Session 119)

---

## Mitigation Mechanisms

> See `CLAUDE.md` for current hooks, commands, skills, and agents (authoritative list).
> This section removed (E2-088) - was duplicate of CLAUDE.md governance tables.

---

## Epoch 3 Scaling Concerns (Observations)

> These are accumulated observations, not backlog items. When patterns are clear, they inform Epoch 3 direction.

| Observation | Pattern | Potential Direction |
|-------------|---------|---------------------|
| backlog.md is 1500+ lines | File growth | Archive completed items, or DB-backed backlog |
| Large output handling (1.3MB read fail) | Memory-agent gap | Smart summarization/chunking in memory-agent skillset |
| LLM channeling patterns work | Blockers > suggestions | Formalize effective channeling patterns (INV-020) |
| Standard terminology aids LLM | Training data leverage | Use Agile/PMBOK terms, not custom vocabulary (INV-021) |
| **ReasoningBank retrieval without feedback** | Write-heavy, read-weak | Usage feedback loop, relevance reinforcement (INV-023) |

---

## References

- **Archived History:** `docs/archive/epistemic_state_v1_2025-12-09.md`
- **System Status:** `.claude/haios-status.json`
- **Work Tracking:** `docs/work/` (active items in `active/`, completed in `archive/`)
- **Session History:** `docs/checkpoints/`
- **Memory Concepts:** 64641-64677 (Session 50), 65008-65063 (Sessions 56-58), 72331-72336 (Session 85), 72377-72388 (Session 86), 78997-79013 (Session 119)
- **ADR-032:** Memory-Linked Work Governance
- **ADR-033:** Work Item Lifecycle Governance
- **ADR-039:** Work Item as File Architecture
- **INV-012:** Static Registration Anti-Pattern Mitigation
- **INV-035:** Skill Architecture Refactoring (M8-SkillArch source)

---

**Last Updated:** 2025-12-25 (Session 119)
**Milestone Completed:** M8-SkillArch (12 skills, 6 agents, validation gates)
