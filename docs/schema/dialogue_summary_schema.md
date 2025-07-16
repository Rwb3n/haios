# Dialogue Summary Schema

## Overview
The dialogue summary is a structured, durable artifact that captures the evolving state of a 2A Agent architectural dialogue. It serves as context for agents to prevent amnesia across rounds and provides an audit trail of decision evolution.

## File Structure
- **Location**: `output_2A/session_[timestamp]/summary.md`
- **Format**: Structured Markdown with required sections
- **Updates**: Regenerated after each dialogue round

## Required Schema

```markdown
# Dialogue Summary: [Session ID]

**Question**: [Original architectural question]
**Round**: [Current round number]
**Status**: [IN_PROGRESS | CONVERGED | FAILED]

## Key Decisions & Agreements
- [Concrete decisions both agents have agreed upon]
- [Technical specifications that have been settled]
- [Architectural patterns that have been validated]

## Open Questions & Dissents
- [Points of disagreement between agents]
- [Unresolved technical challenges]
- [Areas requiring further exploration]

## Current State of Proposal
[Brief narrative describing the current solution being debated, its evolution, and next steps]

## Context for Next Round
[Essential context that agents need to continue the dialogue effectively]
```

## Validation Rules
1. **Session ID**: Must match the format `session_YYYYMMDD_HHMMSS`
2. **Status Values**: Must be one of: IN_PROGRESS, CONVERGED, FAILED
3. **Section Completeness**: All required sections must be present
4. **Round Tracking**: Round number must increment sequentially

## Integration Points
- **SummarizerNode**: Generates summary content by reading `dialogue.json`
- **ArchitectNode**: Reads both `dialogue.json` and `summary.md` for context
- **Consensus Detection**: Status changes to CONVERGED when "**No Further Dissent**" detected

## Security Considerations
- Summary generation is read-only for LLM agents
- File I/O operations handled by trusted Python orchestrator
- No direct file write access granted to persona agents

## Example Usage
```python
# SummarizerNode post() method
def post(self, summary_content: str):
    summary_path = f"{self.session_dir}/summary.md"
    with open(summary_path, 'w') as f:
        f.write(summary_content)
```