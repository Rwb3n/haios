---
generated: 2026-02-12
session: 359
purpose: Cross-epoch retrospective trend analysis for E2.6 arc planning
sources:
  observations: [obs-313, obs-314, obs-317, obs-330, obs-339]
  epochs: [E2_3, E2_4, E2_5, E2_6]
  memory_ids: [84127, 84166, 84167, 84173, 84202, 84207, 84211, 84212, 84215, 84217, 84218, 84219, 84224, 84229, 84230, 84231, 84244, 84248, 84256, 84257, 84259, 84260, 84267, 84268, 84269, 84270, 84284, 84285, 84286, 84291, 84292, 84306, 84307, 84308, 84310, 84315, 84332, 84803, 84804, 84805, 84806, 84807, 84808, 84809, 84811, 84814, 84815, 84818, 84821, 84825, 84826, 84833, 84835, 84836, 84837, 84843, 84848, 84852, 84855, 84860, 84873, 84878, 84881, 84884, 84891, 84892, 84894, 84896, 84897, 84904, 84928, 84935, 84951, 84962, 84963, 84967, 84999, 85002, 85004, 85005, 85010, 85011, 85024, 85025, 85027, 85028, 85035, 85036, 85039, 85041, 85042, 85046, 85047, 85050, 85056]
---
# Retrospective Trend Synthesis for E2.6 Planning

## Method

Cross-referenced all observation files (obs-313 through obs-339), EPOCH.md retro sections (E2.3 through E2.6), checkpoint retros (S339), and 90+ memory entries spanning sessions 206-358. Categorized findings into operator-requested dimensions and extracted recurring trends.

---

## 1. WHAT WENT WELL (Carry Forward)

### Trend A: TDD RED-GREEN = Zero-Debug (HIGH CONFIDENCE)
- **Evidence:** 15/15 (S317), 19/19 (S318), 17/17 (S333), 13/13 (S336), 8/8 (S340), 110/110 (S351)
- **Memory:** 84284, 84803, 85047
- **Pattern:** When tests are written first with precise specs, implementation passes on first attempt
- **Sessions:** S317-S351 (consistent across 10+ sessions)
- **Agent UX relevance:** HIGH — this is a proven methodology to preserve, not change

### Trend B: Critique Agent Catches Real Issues (HIGH CONFIDENCE)
- **Evidence:** 3-10 genuine issues per review (S332-336), catches spec contradictions (84173), catches asymmetry gaps
- **Memory:** 84284, 84306, 84310, 84803, 84884
- **Pattern:** Pre-DO critique gate has the highest ROI of any governance gate
- **Sessions:** S314+ (consistent)
- **Agent UX relevance:** HIGH — preserve, but make invocation cheaper

### Trend C: Plan(sonnet) + Critique(haiku) Model Allocation (MEDIUM CONFIDENCE)
- **Evidence:** obs-317 (100k plan → zero-iteration impl), 84127
- **Pattern:** Deep planning in isolated subagent context eliminates iteration in main context
- **Agent UX relevance:** MEDIUM — model allocation is already working, no change needed

### Trend D: Structured Bug Capture → Batch Fix (HIGH CONFIDENCE)
- **Evidence:** obs-330 (4 bugs in ~15 min), S358 (4 more bugs captured), 84928, 84963, 85004
- **Pattern:** Precise bug descriptions with memory refs → fast batch fix sessions
- **Agent UX relevance:** HIGH — batch pattern avoids ceremony overhead per trivial item

### Trend E: Operator Retros at Phase Boundaries (MEDIUM CONFIDENCE)
- **Evidence:** 84285, 3 retros in S314, S332, S339
- **Pattern:** Early issue detection when operator reflects at boundaries
- **Agent UX relevance:** LOW — operator-initiated, not agent-driven

### Trend F: Critique-Then-Defer (MEDIUM CONFIDENCE)
- **Evidence:** 84291, S333-334
- **Pattern:** Identify issues during review, spawn work items, don't fix inline
- **Agent UX relevance:** MEDIUM — maintains traceability without scope creep

### Trend G: Pure Additive Hook Extension (MEDIUM CONFIDENCE)
- **Evidence:** S335, PreToolUse/PostToolUse pattern
- **Pattern:** Hooks that add behavior without modifying existing hooks = cleanest integration
- **Agent UX relevance:** HIGH — hooks are core agent infrastructure

---

## 2. COULD'VE GONE BETTER (Fix in E2.6)

### Trend H: Ceremony Overhead Is Disproportionate (CRITICAL — 9 memory entries)
- **Evidence:** 84332, 84804, 84837, 84896, 84897, 84951, 85002, 85027, 85028, 85050
- **Frequency:** Referenced in sessions 330, 332, 333, 334, 335, 336, 339, 340, 351, 358
- **Pattern:** ~40% of tokens on governance vs ~30% on implementation for small items
- **Specific:** 12+ ceremony invocations for a single well-defined change (84951)
- **Agent UX relevance:** CRITICAL — this is THE core problem E2.6 must solve

### Trend I: Filesystem Hierarchy Wrong Permanent Structure (HIGH — 3 memory entries)
- **Evidence:** 84805, 84811, obs-339
- **Pattern:** Arcs nested in epochs in directories → agent spends tokens traversing paths
- **Specific:** Arcs need to float between epochs via metadata, not directory nesting
- **Agent UX relevance:** CRITICAL — flat storage + metadata is the proposed architectural fix

### Trend J: Status Cascade Missing (HIGH — 8 memory entries)
- **Evidence:** 84215, 84217, 84218, 84219, 84229, 84231, 84257, 84825, 84826
- **Pattern:** close-work doesn't cascade to parent chapter/arc/epoch status
- **Specific:** S331 found all 4 queue chapters showing Planned despite complete implementations (84229)
- **Agent UX relevance:** HIGH — agent wastes tokens on stale status discovery

### Trend K: Chapter Files Do Double Duty (MEDIUM — 2 memory entries)
- **Evidence:** 84230, obs-339
- **Pattern:** Chapters serve as both design spec AND status tracker
- **Proposal:** Chapters immutable design docs; status lives in work items, aggregated by queries
- **Agent UX relevance:** HIGH — directly feeds flat metadata architecture

### Trend L: Coldstart Overhead Disproportionate for Housekeeping (MEDIUM — 3 memory entries)
- **Evidence:** 84835, 84836, 84855
- **Pattern:** Full coldstart (config + orchestrator + 7 arc reads + memory queries) overkill for doc fixes
- **Proposal:** Lightweight "housekeeping cycle" or partial coldstart
- **Agent UX relevance:** HIGH — directly reduces agent token spend

### Trend M: MUST Gates Skipped Without Logging (HIGH — 7 memory entries)
- **Evidence:** 84268, 84269, 84270, 84292, 84307, 84308, 84873, 84881, 84894
- **Pattern:** Agents skip governance gates; no logging when they do
- **Specific:** "Validation momentum causes gate skip" — earlier positive signals create momentum to skip later gates
- **Agent UX relevance:** MEDIUM — gate logging is a governance fix, not UX

### Trend N: Memory System Underutilized (MEDIUM — 1 strong entry)
- **Evidence:** 84808, obs-339
- **Pattern:** 85k+ concepts but retrieval is ad-hoc; Greek Triad taxonomy dead; auto-classifier diverged
- **Agent UX relevance:** MEDIUM — better memory retrieval helps agent, but not core UX problem

### Trend O: Scaffold Bugs and Missing Lint (MEDIUM — 5 entries)
- **Evidence:** 84166, 84167, 84814, 84815, obs-330
- **Pattern:** {{TYPE}} unsubstituted, no scaffold output lint, consumer updates missed
- **Agent UX relevance:** LOW — tactical fixes, not architectural

---

## 3. KEEP DOING

| Practice | Evidence | Confidence |
|----------|----------|------------|
| TDD RED-GREEN methodology | 6+ sessions with 100% first-pass | HIGH |
| Critique agent before every DO | 10+ sessions catching real issues | HIGH |
| Structured bug capture → batch fix | S330, S358 | HIGH |
| Critique-then-defer for scope control | S333-334 | MEDIUM |
| Pure additive hook extension | S335 | MEDIUM |
| Operator retros at phase boundaries | S314, S332, S339 | MEDIUM |
| Plan subagent with deep exploration | S317 (obs-317) | MEDIUM |
| stub:true frontmatter for stubs | S333 | LOW |

---

## 4. STOP DOING

| Anti-Pattern | Evidence | Memory IDs |
|-------------|----------|------------|
| Reading mutable state for computable values | Session-start non-idempotent bug, obs-330 | 84202 |
| Over-investigating known bugs | Broad grep when source file known, obs-330 | — |
| Skipping MUST gates without logging | 3+ instances across sessions | 84268, 84307, 84308 |
| Working outside governance cycles | S333 governance bypass irony | 84292 |
| Letting chapter/arc status rot | 4 chapters showed wrong status at closure | 84229, 84256 |
| Full ceremony chain for trivial fixes | 12+ invocations for single change | 84951, 85002, 85050 |
| Hardcoding epoch paths | audit_decision_coverage bug | 85035, 85036 |

---

## 5. START DOING

| Practice | Rationale | Related Work |
|----------|-----------|-------------|
| Scaffold output lint (assert no {{ remains) | Would have caught Bug 2 immediately | obs-330 |
| Auto-detect missing plan → route to plan-authoring | Agents currently skip PLAN if no plan exists | 84860 |
| Gate skip logging to governance-events.jsonl | MUST violations go untracked | 84270 |
| Status cascade on closure (work → chapter → arc) | Eliminates stale status discovery | 84219, WORK-034 |
| Lightweight housekeeping coldstart | Reduce token spend on doc fix sessions | 84836 |
| Batch scope triage ceremony | Missing from ceremony chain (obs-314) | WORK-102 |
| Config-driven path resolution (not hardcoded) | Recurring bug class across epochs | 85036 |

---

## 6. BUG ALERTS (Active)

| ID | Bug | Status | Source |
|----|-----|--------|--------|
| WORK-138 | Scaffold checkpoint CLI arg parsing broken | Open | S358 retro |
| WORK-139 | close-epoch-ceremony SKILL.md documents stale file moves | Open | S358 retro |
| WORK-140 | Audit doesn't detect status vs node history divergence | Open | S358 retro |
| WORK-141 | audit-decision-coverage returns 0 exit code on warnings | Open | S358 retro |

### Recurring Bug Classes

| Class | Instances | Pattern |
|-------|-----------|---------|
| **Non-idempotent state updates** | session-start prior_session, checkpoint stale values | Read-then-write mutable state without re-entrancy guard |
| **Consumer update missed after restructure** | CH-006 (8+ consumers), scaffold (manifest), fractured templates | Change source → forget consumers |
| **Hardcoded paths** | audit_decision_coverage E2_4, identity_loader wrong epoch | Should use ConfigLoader |
| **Stale documentation** | close-epoch-ceremony file moves, stage-governance recipe | Docs diverge from implementation |

---

## 7. FEATURE REQUESTS (From Observations + Memory)

| Request | Source | E2.6 Fit? |
|---------|--------|-----------|
| Dynamic ceremony composition (config-driven, not skill-driven) | obs-313 | YES — core agent UX |
| Operator-initiated review ceremonies (Session/Process/Scope/System) | obs-314 | YES — epoch governance arc |
| Proportional governance (scale ceremony to item size) | WORK-101, 84332 | YES — critical for overhead reduction |
| Flat metadata for arcs/chapters (metadata relationships) | obs-339, 84811 | YES — structural migration arc |
| Engine functions for arc/chapter queries | EPOCH.md E2.6 | YES — recipe composability |
| Lightweight housekeeping coldstart | 84836 | YES — agent UX |
| Batch scope triage ceremony | obs-314 (Session 339 update) | YES — epoch governance |
| CeremonyRunner (separate from CycleRunner) | obs-339 | MAYBE — depends on dynamic composition decision |
| Greek Triad taxonomy audit/replacement | 84808 | LOW — memory subsystem, not core UX |

---

## 8. TREND SUMMARY: What Points to Agent UX?

### The Top 5 Trends (by frequency, severity, and E2.6 alignment)

| Rank | Trend | Category | Memory Count | E2.6 Relevance |
|------|-------|----------|-------------|----------------|
| 1 | **Ceremony overhead disproportionate** | Could've gone better | 9+ | CRITICAL |
| 2 | **Filesystem hierarchy wrong permanent structure** | Could've gone better | 3 | CRITICAL |
| 3 | **Status cascade missing** | Could've gone better | 8 | HIGH |
| 4 | **Batch fixes avoid ceremony overhead** | What went well | 4+ | HIGH |
| 5 | **Coldstart overhead for housekeeping** | Could've gone better | 3 | HIGH |

### The E2.6 Thesis (Derived from Trends)

**The governance system works but costs too much.** The proof:
- TDD, critique gates, and ceremonies produce high-quality output (Trends A, B, D)
- But 40% of tokens go to governance, not work (Trend H)
- The filesystem hierarchy amplifies this cost (Trend I)
- Status rot forces discovery work that should be automatic (Trend J)
- Even starting a session costs too much for small tasks (Trend L)

**The fix is structural, not incremental:**
1. Flat storage + metadata relationships (eliminates path traversal)
2. Engine functions replace file reads (reduces token spend)
3. Proportional governance (scales ceremony to item size)
4. Status cascade automation (eliminates stale discovery)
5. Lightweight coldstart variants (right-size session overhead)

### What Doesn't Point to Agent UX (Park or Defer)

| Item | Why Not Core UX |
|------|----------------|
| Greek Triad taxonomy | Memory subsystem concern |
| Gate skip logging | Governance integrity, not UX |
| Scaffold lint | Tactical test infra |
| Plan agent exemplar workflow | Already working, codify later |

---

## Next Step

Use these trends to inform E2.6 arc decomposition. The top 5 trends map directly to the arcs proposed in EPOCH.md:
- Trend H + L → **agent-ux** arc (proportional governance, lightweight coldstart)
- Trend I + K → **structural-migration** arc (flat storage, metadata relationships)
- Trend J → **recipe-composability** arc (engine functions, status cascade)
- Feature requests → **epoch-governance** arc (review ceremonies, scope triage)
