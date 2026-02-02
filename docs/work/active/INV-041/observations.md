---
template: observations
work_id: INV-041
captured_session: '290'
generated: '2026-02-02'
last_updated: '2026-02-02T17:02:49'
---
# Observations: INV-041

## What surprised you?

1. **Memory synthesis describes non-existent artifacts.** The memory system returned synthesized insights about `haios.config.json` as a centralized path configuration file (concepts 64209, 63257, 24425). This file does not exist - it's an aspirational pattern captured from past discussions. The memory synthesis correctly identified the *intent* but a naive consumer might assume it documents current reality. This is valuable for understanding direction but needs epistemic labeling (intent vs implementation).

2. **Path scatter is 7x larger than originally documented.** E2-212 (which spawned this investigation) mentioned "10+ files" with hardcoded paths. Actual count from Grep: **70+ files** (59 markdown + 11 Python). The problem grew as skills, commands, and agents proliferated during Epoch 2. This validates the urgency of centralization - manual updates at this scale are unsustainable.

## What's missing?

1. **No automated path drift detection.** When paths are defined in 70+ files, there's no mechanism to detect when definitions diverge. If someone changes a path in haios.yaml but forgets a skill file, it silently becomes incorrect. This investigation proposes centralization but doesn't address the transition period or prose consumers that can't use ConfigLoader at runtime.

2. **No prose consumer pattern for centralized config.** Python migration is straightforward (ConfigLoader.paths accessor). But 59 markdown files have no runtime config access - they're read directly by the LLM. Options mentioned (just recipe injection, preprocessing) need design work before prose migration can proceed. This is the harder half of the problem.

## What should we remember?

1. **Dual-format requirement pattern.** When centralizing configuration shared between code and LLM prose, format must serve both consumers:
   - Strings with `{placeholder}` syntax work because Python can interpolate them AND LLMs can read them directly
   - YAML is both machine-parseable and human-readable
   - This pattern applies to any config bridging code and prose layers

2. **Extend existing singletons, don't create new mechanisms.** ConfigLoader already exists as the config access pattern. haios.yaml already has partial path centralization (epoch section). Extending proven patterns beats introducing new infrastructure. Follow the grain.

## What drift did you notice?

1. **INV-041 context section has stale path.** The work item referenced `.claude/lib/scaffold.py` but actual location is `.claude/haios/lib/scaffold.py`. The path changed during restructuring but INV-041's Context section wasn't updated. Ironic: this is exactly the problem the investigation is solving.

2. **Memory synthesis vs implementation gap.** Memory concepts describe `haios.config.json` confidently as if it exists and is authoritative. This comes from synthesis of past discussions about what *should* exist. Future agents querying memory might build on this assumption. Consider: should synthesized concepts have epistemic markers distinguishing "discussed" from "implemented"?
