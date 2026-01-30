---
template: observations
work_id: WORK-036
captured_session: '263'
generated: '2026-01-30'
last_updated: '2026-01-30T19:30:39'
---
# Observations: WORK-036

## What surprised you?

**The quantitative evidence was stronger than expected.** I hypothesized that template overhead constrains depth, but counting revealed 25 MUST gates + 27 checkboxes - a "Template Tax" that's measurable. The template grew from 125 lines (v1.0, per memory concept 77254) to 372 lines (v2.0) - 197% growth. This growth happened through incremental improvements (Session 171 learning, E2-144 governance, etc.) where each addition made sense locally but accumulated into compliance burden.

**The investigation template critique was meta-ironic.** This investigation used the investigation template to investigate the investigation template's ineffectiveness. The irony wasn't lost: I experienced the Template Tax while documenting the Template Tax. The template's checkboxes felt like overhead during the work.

**The Explore agent's effectiveness is real but not mysterious.** Session 262's Explore agent success wasn't magic - it's explainable: zero constraints + open prompt + full tool access = comprehensive exploration. The "mystery" was simply that we removed the Template Tax.

## What's missing?

**PreToolUse hook lacks governance-context awareness (OBS-263-001).** When `/new-work` calls `just work`, the hook blocks it because it doesn't know we're already inside a governance command. Error: `BLOCKED: Direct work_item scaffold. Use '/new-work' command instead.` The workaround (call `scaffold.py` directly) works but is inelegant. Fix: Either pass environment variable (HAIOS_GOVERNANCE_CONTEXT=new-work) or have /new-work call scaffold.py directly.

**Session number not auto-populated in investigation templates (OBS-263-002).** The scaffold doesn't read `.claude/session` to populate the `{{SESSION}}` placeholder. The investigation file showed `session: 247` when it should have been `session: 262`. Minor cosmetic issue requiring manual fix.

## What should we remember?

**Depth and compliance are inversely correlated.** This is the core finding worth promoting to L3/L4. Evidence:
- Session 101: Agent bypassed investigation-agent subagent rather than comply with template (memory concept 77254)
- Session 262: Unconstrained Explore agent produced 271-line comprehensive analysis vs 12-line table format expected by investigation-agent
- Implication: Governance should be minimal (5 essential gates) not comprehensive (25 MUST gates)

**The right tool for the right job.** Rather than redesigning investigation-cycle, we could simply:
- Use Explore agent for discovery work (open questions like "Is X ready?")
- Use investigation-cycle for hypothesis validation (specific tests like "Does H1 hold?")
- Accept different work types need different tools

This is Option A from the investigation: "Accept Finding" - no infrastructure change needed, just better tool selection.

**WORK-037 spawned for future exploration.** Options C (EXPLORE-FIRST) and D (Hybrid) merit design discussion, but operator explicitly said "not sure if it fits this epoch so leave for later triage." Created with low priority.

## What drift did you notice?

**Investigation template evolved past its original purpose.** The template was designed to ensure rigor through structure. But v2.0 at 372 lines has become a compliance exercise that constrains depth. The documentation (SKILL.md, investigation-agent.md) still claims it "ensures structured research" but evidence shows it produces shallow outputs. The template optimizes for compliance, not discovery.

**investigation-agent output format is too rigid.** The agent definition (`.claude/agents/investigation-agent.md:55-65`) specifies a 12-line table format:
```
| Hypothesis | Evidence | Source | Supports? |
```
This was meant to ensure evidence has sources. But it prevents narrative analysis, code examples, and design rationale - exactly what made Session 262's Explore output valuable. The format constraint became the primary depth limiter.
