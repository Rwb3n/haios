# generated: 2026-02-19
# System Auto: last updated on: 2026-02-19T00:00:00
# Chapter: CeremonyAutomation

## Chapter Definition

**Chapter ID:** CH-059
**Arc:** call
**Epoch:** E2.8
**Name:** Ceremony Automation
**Status:** In Progress

---

## Purpose

Migrate mechanical (judgment-free) ceremony phases from SKILL.md (Tier 3, agent reads) to hooks/modules (Tier 1/2, auto-execute). Phases requiring judgment remain as skills. This is the implementation of CH-058's proportional governance design.

**Core insight:** Ceremony skills are markdown — the agent is the runtime (mem:84857). Moving mechanical phases to hooks/modules eliminates token cost for judgment-free operations. Retro-cycle Phase 0 (mem:85607, 85363) is the prototype: computable predicates skip retro for trivial items.

---

## Work Items

| ID | Title | Status | Type |
|----|-------|--------|------|
| WORK-160 | Ceremony Automation | Complete | implementation |
| WORK-167 | Governance Tier Detection | Complete | implementation |
| WORK-168 | Cycle Phase Auto-Advancement | Complete | implementation |
| WORK-169 | Critique-as-Hook | Backlog | implementation |
| WORK-170 | Checkpoint Field Auto-Population | Backlog | implementation |
| WORK-171 | Mechanical Phase Migration | Backlog | implementation |
| WORK-172 | Block EnterPlanMode via PreToolUse Hook | Complete | implementation |
| WORK-173 | Blocked_by Cascade on Work Closure | Complete | implementation |
| WORK-174 | WorkState Dataclass Expansion | Backlog | implementation |
| WORK-176 | Plan-Authoring-Cycle Subagent Delegation | Backlog | implementation |
| WORK-177 | Chapter Manifest Auto-Update on Work Creation | Complete | implementation |
| WORK-178 | CHECK Phase Subagent Delegation | Backlog | implementation |
| WORK-179 | Queue Commit Cycle Phase Auto-Advance Investigation | Complete | investigation |
| WORK-189 | Context Window Usage Injection via UserPromptSubmit Hook | Complete | implementation |
| WORK-190 | backlog_id_uniqueness Gate False Positive on WORK-1XX IDs | Complete | bug |
| WORK-191 | queue-commit Ceremony Contract Missing work_id Field | Complete | bug |
| WORK-194 | UserPromptSubmit Hook Injection Candidates Evaluation | Complete | investigation |
| WORK-195 | UserPromptSubmit Slim-Read-Once Refactor | Backlog | implementation |
| WORK-196 | UserPromptSubmit Hook Injection Batch (Session, Working, Duration) | Backlog | implementation |
| WORK-200 | Implement Proportional Close Ceremony | Complete | implementation |
| WORK-201 | Governance Events Not Written by set-cycle Recipe | Complete | investigation |
| WORK-204 | Chapter Manifest Auto-Update on Work Closure | Complete | implementation |
| WORK-203 | Session Event Log for Agent Ambient Visibility | Complete | investigation |
| WORK-205 | Survey-Cycle Auto-Prioritize for Backlog Items | Parked | implementation |
| WORK-206 | Implement Session Event Log | Complete | implementation |
| WORK-209 | Enforce Session/Process Review Computable Predicates via Hooks | Complete | implementation |

---

## Exit Criteria

- [ ] At least 3 mechanical ceremony phases migrated from SKILL.md to hooks/modules
- [ ] Session-end ceremony runs automatically via hook (not agent-read skill)
- [ ] Checkpoint population automated for standard fields
- [ ] cycle_phase advancement automated via PostToolUse hook
- [ ] Critique-as-hook detects inhale-to-exhale transitions, injects critique automatically
- [ ] Zero regression in existing ceremony behavior

---

## Dependencies

| Direction | Target | Reason |
|-----------|--------|--------|
| Blocked by | CH-058 (ProportionalGovernanceDesign) | CH-058 defines the design this chapter implements |
| None | - | No outbound blocks |

---

## References

- @.claude/haios/epochs/E2_8/arcs/call/ARC.md (parent arc)
- @.claude/haios/epochs/E2_8/EPOCH.md (parent epoch)
- @docs/work/active/WORK-160/WORK.md (work item)
- @docs/work/active/WORK-101/WORK.md (prerequisite design)
- @.claude/skills/retro-cycle/SKILL.md (Phase 0 prototype)
- Memory: 85390 (104% problem), 84857 (ceremony=markdown), 85607 (retro Phase 0)
