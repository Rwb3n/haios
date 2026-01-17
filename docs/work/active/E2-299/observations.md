---
template: observations
work_id: E2-299
captured_session: '200'
generated: '2026-01-17'
last_updated: '2026-01-17T15:34:55'
---
# Observations: E2-299

## What surprised you?

<!-- Unexpected behaviors, things easier/harder than expected -->

- [x] Typo was NOT in the template - template was correct (`plans: []`). The typo was introduced during manual YAML editing of specific work items. YAML accepts any key name silently - no schema validation catches malformed field names.

## What's missing?

<!-- Gaps, missing features, AgentUX friction -->

- [x] YAML schema validation for WORK.md frontmatter - would catch typos like `planss:` at write time. Currently scaffold and validate tools don't detect malformed field names, only missing required fields.

## What should we remember?

<!-- Learnings, patterns, warnings -->

- [x] The observation-capture mechanism works: typo caught during E2-253 -> documented in observations.md -> triaged by INV-067 -> spawned as E2-299 -> fixed in S200. This is the observation->triage->fix pipeline operating correctly.
