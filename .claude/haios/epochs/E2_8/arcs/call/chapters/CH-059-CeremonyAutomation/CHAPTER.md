---
id: CH-059
name: Ceremony Automation
arc: call
epoch: E2.8
status: In Progress
work_items:
- id: WORK-160
  title: Ceremony Automation
  status: Complete
  type: implementation
- id: WORK-167
  title: Governance Tier Detection
  status: Complete
  type: implementation
- id: WORK-168
  title: Cycle Phase Auto-Advancement
  status: Complete
  type: implementation
- id: WORK-169
  title: Critique-as-Hook
  status: Complete
  type: implementation
- id: WORK-170
  title: Checkpoint Field Auto-Population
  status: Complete
  type: implementation
- id: WORK-171
  title: Mechanical Phase Migration
  status: Backlog
  type: implementation
- id: WORK-172
  title: Block EnterPlanMode via PreToolUse Hook
  status: Complete
  type: implementation
- id: WORK-173
  title: Blocked_by Cascade on Work Closure
  status: Complete
  type: implementation
- id: WORK-174
  title: WorkState Dataclass Expansion
  status: Backlog
  type: implementation
- id: WORK-176
  title: Plan-Authoring-Cycle Subagent Delegation
  status: Backlog
  type: implementation
- id: WORK-177
  title: Chapter Manifest Auto-Update on Work Creation
  status: Complete
  type: implementation
- id: WORK-178
  title: CHECK Phase Subagent Delegation
  status: Backlog
  type: implementation
- id: WORK-179
  title: Queue Commit Cycle Phase Auto-Advance Investigation
  status: Complete
  type: investigation
- id: WORK-189
  title: Context Window Usage Injection via UserPromptSubmit Hook
  status: Complete
  type: implementation
- id: WORK-190
  title: backlog_id_uniqueness Gate False Positive on WORK-1XX IDs
  status: Complete
  type: bug
- id: WORK-191
  title: queue-commit Ceremony Contract Missing work_id Field
  status: Complete
  type: bug
- id: WORK-194
  title: UserPromptSubmit Hook Injection Candidates Evaluation
  status: Complete
  type: investigation
- id: WORK-195
  title: UserPromptSubmit Slim-Read-Once Refactor
  status: Backlog
  type: implementation
- id: WORK-196
  title: UserPromptSubmit Hook Injection Batch (Session, Working, Duration)
  status: Backlog
  type: implementation
- id: WORK-200
  title: Implement Proportional Close Ceremony
  status: Complete
  type: implementation
- id: WORK-201
  title: Governance Events Not Written by set-cycle Recipe
  status: Complete
  type: investigation
- id: WORK-204
  title: Chapter Manifest Auto-Update on Work Closure
  status: Complete
  type: implementation
- id: WORK-203
  title: Session Event Log for Agent Ambient Visibility
  status: Complete
  type: investigation
- id: WORK-205
  title: Survey-Cycle Auto-Prioritize for Backlog Items
  status: Parked
  type: implementation
- id: WORK-206
  title: Implement Session Event Log
  status: Complete
  type: implementation
- id: WORK-209
  title: Enforce Session/Process Review Computable Predicates via Hooks
  status: Complete
  type: implementation
- id: WORK-210
  title: Split Retro-Cycle into Inline Reflect plus Delegated Close
  status: Complete
  type: implementation
- id: WORK-211
  title: Post-Retro Enrichment Subagent Design
  status: Complete
  type: implementation
- id: WORK-212
  title: Mechanical Phase Delegation to Haiku Subagents
  status: Complete
  type: refactor
- id: WORK-214
  title: Governance Event Log Rotation Per Epoch
  status: Complete
  type: implementation
- id: WORK-215
  title: Session ID Field on Governance Events
  status: Complete
  type: implementation
- id: WORK-216
  title: Hook Output Trimming for Noise Reduction
  status: Complete
  type: implementation
- id: WORK-217
  title: Implement Retro-Enrichment Agent
  status: Complete
  type: implementation
- id: WORK-233
  title: Add context_pct Field to Governance Events
  status: Complete
  type: implementation
- id: WORK-234
  title: Constrain EXTRACT Phase Haiku Prompt to Eliminate File Reads
  status: Complete
  type: implementation
- id: WORK-236
  title: 'Investigation: context_pct Governance Event Consumer Design'
  status: Complete
  type: investigation
- id: WORK-237
  title: Implement context_pct Auto-Injection via Slim Relay
  status: Complete
  type: implementation
- id: WORK-238
  title: 'Investigation: DONE/CHAIN Phase Duplication with Close-Work-Cycle'
  status: Complete
  type: investigation
- id: WORK-241
  title: 'Eliminate dod-validation-cycle: absorb Agent UX Test into close-work VALIDATE'
  status: Complete
  type: implementation
- id: WORK-242
  title: Remove plan status double-update from impl-cycle DONE phase
  status: Complete
  type: implementation
- id: WORK-243
  title: 'Clean /close command: remove stale Steps 2-3 duplicate documentation'
  status: Complete
  type: implementation
- id: WORK-250
  title: Tier-Aware Gate Skipping — Proportional Ceremony Enforcement
  status: Complete
  type: implementation
exit_criteria:
- text: At least 3 mechanical ceremony phases migrated from SKILL.md to hooks/modules
  checked: true
- text: Session-end ceremony runs automatically via hook (not agent-read skill)
  checked: false
- text: Checkpoint population automated for standard fields
  checked: false
- text: cycle_phase advancement automated via PostToolUse hook
  checked: true
- text: Critique-as-hook detects inhale-to-exhale transitions, injects critique automatically
  checked: true
- text: Zero regression in existing ceremony behavior
  checked: true
dependencies:
- direction: Blocked by
  target: CH-058 (ProportionalGovernanceDesign)
  reason: CH-058 defines the design this chapter implements
---
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
| WORK-169 | Critique-as-Hook | Complete | implementation |
| WORK-170 | Checkpoint Field Auto-Population | Complete | implementation |
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
| WORK-210 | Split Retro-Cycle into Inline Reflect plus Delegated Close | Complete | implementation |
| WORK-211 | Post-Retro Enrichment Subagent Design | Complete | implementation |
| WORK-212 | Mechanical Phase Delegation to Haiku Subagents | Complete | refactor |
| WORK-214 | Governance Event Log Rotation Per Epoch | Complete | implementation |
| WORK-215 | Session ID Field on Governance Events | Complete | implementation |
| WORK-216 | Hook Output Trimming for Noise Reduction | Complete | implementation |
| WORK-217 | Implement Retro-Enrichment Agent | Complete | implementation |
| WORK-233 | Add context_pct Field to Governance Events | Complete | implementation |
| WORK-234 | Constrain EXTRACT Phase Haiku Prompt to Eliminate File Reads | Complete | implementation |
| WORK-236 | Investigation: context_pct Governance Event Consumer Design | Complete | investigation |
| WORK-237 | Implement context_pct Auto-Injection via Slim Relay | Complete | implementation |
| WORK-238 | Investigation: DONE/CHAIN Phase Duplication with Close-Work-Cycle | Complete | investigation |
| WORK-241 | Eliminate dod-validation-cycle: absorb Agent UX Test into close-work VALIDATE | Complete | implementation |
| WORK-242 | Remove plan status double-update from impl-cycle DONE phase | Complete | implementation |
| WORK-243 | Clean /close command: remove stale Steps 2-3 duplicate documentation | Complete | implementation |
| WORK-250 | Tier-Aware Gate Skipping — Proportional Ceremony Enforcement | Complete | implementation |

---

## Exit Criteria

- [x] At least 3 mechanical ceremony phases migrated from SKILL.md to hooks/modules (S480: critique-as-hook WORK-169, cycle_phase auto-advance WORK-168, retro gate WORK-253, tier detection WORK-167, context_pct injection WORK-237)
- [ ] Session-end ceremony runs automatically via hook (not agent-read skill)
- [ ] Checkpoint population automated for standard fields
- [x] cycle_phase advancement automated via PostToolUse hook (WORK-168)
- [x] Critique-as-hook detects inhale-to-exhale transitions, injects critique automatically (WORK-169, critique_injector.py)
- [x] Zero regression in existing ceremony behavior (S480: test suite 1856p, pre-existing failures only)

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
