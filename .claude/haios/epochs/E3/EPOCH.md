# generated: 2026-01-19
# System Auto: last updated on: 2026-02-14T01:30:00
# Epoch 3: [To Be Determined]

## L4 Object Definition

**Epoch ID:** E3
**Name:** TBD (determined by investigation during E2.x)
**Status:** Future
**Prior:** E2.9 (Governance)
**Next:** E4 (Cognitive Memory)

---

## Vision

E3's identity is intentionally undefined. E2.x investigations will determine whether E3 is:
- **SDK Migration** — move from Claude Code CLI to Agent SDK (hard enforcement, multi-agent)
- **Autonomy** — self-directed sessions, confidence-based escalation
- **The Product** — portability test, drop HAIOS into a fresh workspace
- **Something else** — findings may reveal a better option

**Decision:** S365 — operator and agent agreed not to commit E3 scope without investigation.
This avoids the "assume over verify" anti-pattern (L1.5 — L3.2).

---

## Candidates

### Option A: SDK Migration
- Platform shift from CLI to Agent SDK
- Hard enforcement (not just context injection)
- Multi-agent concurrency
- Typed tool interfaces
- Prior analysis: E2 S25 architecture doc, INV-062 (Skill() unhookable in CLI)
- Risk: SDK maturity unknown, infrastructure cost implications (L1.8)

### Option B: Autonomy
- Session loop without operator
- Self-directed work selection (survey-cycle already exists as foundation)
- Confidence-based escalation
- Error recovery patterns
- Inward cycles: Introspect -> Meta-evaluate -> Adapt (from epoch4_vision/)

### Option C: The Product
- Portability test: "drop .claude/haios/ into a fresh workspace and produce a product"
- haios_etl migration resolved
- First real use of HAIOS on an external project
- Validation of everything E2.x built

---

## Investigation Required

Queue an investigation during E2.6 or E2.7 to answer:
1. What is the real gap between CLI and SDK?
2. What does infrastructure cost look like? (L1.8 constraint)
3. Can we run SDK alongside CLI, or is it a migration?
4. Which E3 option delivers the most value given constraints?

---

## Entry Criteria

- [ ] E2.9 Governance epoch complete
- [ ] E3 identity investigation complete with operator decision
- [ ] Entry criteria refined based on investigation findings

---

## Observations

Observations captured during E2.x that may inform E3:
- obs-e3-001: Stage 5 PRUNE not implemented (memory concern, may be E4)
- obs-e3-002: Greedy clustering produces 76% pair-only syntheses (memory concern, may be E4)
- E2 S25: SDK architecture mapping (Chariot modules -> SDK tools)
- E2 INV-062: Skill() invocation unhookable in CLI

---

## References

- @.claude/haios/epochs/E2_9/EPOCH.md (prior epoch)
- @.claude/haios/epochs/E4/EPOCH.md (next epoch — Cognitive Memory)
- @epoch4_vision/ (philosophical foundation, agents as stateless units)

---

*"First know what you're building. Then build it."*
