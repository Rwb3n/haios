---
template: observations
work_id: WORK-015
captured_session: '243'
generated: '2026-01-26'
last_updated: '2026-01-26T18:54:42'
---
# Observations: WORK-015

## What surprised you?

**Critique-agent found real spec gaps:** I didn't expect the critique-agent to find substantive issues. It identified that CH-002 requires R3 (confidence field) and R4 (traceability field) but my initial plan omitted both. The CRITIQUE phase caught A9 (missing traceability) and A10 (missing confidence) before implementation - demonstrating the value of assumption surfacing. This required plan revision but prevented implementing the wrong design.

**Parser order matters more than expected:** Initially I treated parsers as independent components. But NaturalLanguageParser's `can_parse()` returns True for any `.md` file, so if placed first in the parser list, it would grab TRD content before TRDParser could match. The order TRD → Manifesto → NaturalLanguage is architecturally critical, not arbitrary. Documented in Key Design Decisions table.

## What's missing?

**No runtime consumer yet:** The module is complete with 16 passing tests, but CH-003 (PlannerAgent) doesn't exist yet. RequirementExtractor has no caller outside tests. Per ADR-033 DoD: "Runtime consumer exists" is technically unmet. This is acceptable for CH-002 scope but noted. The intended consumer is documented in WORK-015 plan Step 10.

**Traceability is consumer-populated:** The `traceability` field exists in RequirementSet dataclass (per CH-002 R4) but the extractor doesn't populate it - the extractor extracts requirements, consumers link them to work items. This separation might surprise developers expecting a fully-populated output. Consider adding this to module docstring.

## What should we remember?

**Multi-parser architecture pattern:** When building extractors for heterogeneous document formats (TRDs vs manifesto vs prose), use a Parser protocol with `can_parse(file_path) -> bool` for selection and `parse(content, file_path) -> List[Item]` for extraction. Order parsers from most-specific to most-generic (fallback last). This pattern is reusable for future extractors (e.g., EntityExtractor, ConceptExtractor).

**Confidence field enables filtering:** Adding a `confidence: float` field to extracted data (1.0 for table/regex extraction, 0.7 for NLP inference) allows consumers to filter by quality. The NaturalLanguageParser sets `confidence=0.7` because its regex-based extraction from prose is inherently less reliable than structured table parsing. This pattern should be reused in any extractor with variable reliability.

**Line number tracking pattern:** `content[:match.start()].count('\n') + 1` is a simple, cross-platform way to track source line numbers for provenance. Works with Python's normalized line endings. No external dependencies. Used in all three parsers.

## What drift did you notice?

**WORK.md `current_node` stuck at `backlog`:** The work item still shows `current_node: backlog` despite being fully implemented. The node_history shows only the initial backlog entry with no subsequent transitions. Either the implementation-cycle didn't update it, or node transitions aren't wired. This is cosmetic (the `status` field is authoritative per ADR-041) but indicates node state machine may be incomplete.

**CH-002 chapter file not updated on completion:** The chapter file `.claude/haios/epochs/E2_3/arcs/pipeline/CH-002-requirement-extractor.md` still shows `Status: Active` even though its success criteria are met. Chapter files may need a completion update step added to close-work-cycle.
