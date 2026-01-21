---
template: implementation_plan
status: complete
date: 2026-01-21
backlog_id: WORK-005
title: Implement Loader Base for Configuration Arc
author: Hephaestus
lifecycle_phase: plan
session: 219
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-21T21:04:41'
---
# Implementation Plan: Implement Loader Base for Configuration Arc

@docs/README.md
@docs/epistemic_state.md

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: New feature, no existing code to show current state"
     - "SKIPPED: Pure documentation task, no code changes"
     - "SKIPPED: Trivial fix, single line change doesn't warrant detailed design"

     This prevents silent section deletion and ensures conscious decisions.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

A config-driven extraction DSL and Loader base class that extracts specific content (blockquotes, headings, lists, frontmatter) from structured markdown files and outputs injection-ready strings for agent context.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | New module, no modifications |
| Lines of code affected | ~0 | New code only |
| New files to create | 3 | `.claude/haios/lib/loader.py`, `tests/test_loader.py`, `.claude/haios/config/loaders/example.yaml` |
| Tests to write | 10 | 8 extraction types + 1 format + 1 integration |
| Dependencies | 1 | `yaml` (stdlib), patterns from `config.py` |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Standalone module, future loaders will import |
| Risk of regression | Low | New code, no existing behavior to break |
| External dependencies | Low | Only yaml stdlib, regex stdlib |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 30 min | High |
| Implement extraction types | 45 min | High |
| Format/template system | 15 min | High |
| Integration test | 15 min | High |
| **Total** | ~2 hr | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/commands/coldstart.md - Current prose instructs manual file reads
# Step 2: Load Manifesto (MUST)
# Read: .claude/haios/manifesto/L0-telos.md
# Read: .claude/haios/manifesto/L1-principal.md
# ... (agent makes 5+ Read tool calls, loading ~500 lines total)
```

**Behavior:** Agent reads entire markdown files when only specific content is needed.

**Result:**
- Token waste: L0-telos.md is 101 lines, but Prime Directive is 1 sentence
- Multiple tool calls: 5+ Read calls during coldstart
- Module-First violation: Prose instructs file reads instead of calling modules

### Desired State

```python
# .claude/haios/lib/loader.py - Config-driven extraction
from loader import Loader

loader = Loader(Path(".claude/haios/config/loaders/identity.yaml"))
content = loader.load()
# Returns: "PRIME DIRECTIVE: The system's success is measured by..."

# Config drives extraction (identity.yaml):
# extract:
#   mission:
#     file: manifesto/L0-telos.md
#     section: "## The Prime Directive"
#     type: blockquote
```

**Behavior:** Loader reads config, extracts only requested content, returns formatted string.

**Result:**
- Token efficiency: Only needed content extracted
- Single call: `loader.load()` returns injection-ready string
- Module-First compliant: Just recipes call loader module

---

## Tests First (TDD)

### Test 1: Extract Blockquote
```python
def test_extract_blockquote():
    """Extract first blockquote from a section."""
    md_content = """
## The Prime Directive

> The system's success is measured by its ability to reduce cognitive load.

Other text here.
"""
    result = extract_blockquote(md_content, "## The Prime Directive")
    assert result == "The system's success is measured by its ability to reduce cognitive load."
```

### Test 2: Extract First Paragraph
```python
def test_extract_first_paragraph():
    """Extract text until first blank line."""
    md_content = """
## Context

This is the first paragraph that describes
the context of the problem.

This is the second paragraph.
"""
    result = extract_first_paragraph(md_content, "## Context")
    assert "first paragraph" in result
    assert "second paragraph" not in result
```

### Test 3: Extract All H3 Headings
```python
def test_extract_all_h3():
    """Extract all ### headings with their first line."""
    md_content = """
## Principles

### 1. Evidence Over Assumption
Decisions require evidence.

### 2. Context Must Persist
Knowledge compounds.
"""
    result = extract_all_h3(md_content, "## Principles")
    assert len(result) == 2
    assert "Evidence Over Assumption" in result[0]
```

### Test 4: Extract Numbered List
```python
def test_extract_numbered_list():
    """Extract all 1. 2. 3. items."""
    md_content = """
## Steps

1. First step
2. Second step
3. Third step
"""
    result = extract_numbered_list(md_content, "## Steps")
    assert len(result) == 3
```

### Test 5: Extract Bulleted List
```python
def test_extract_bulleted_list():
    """Extract all - items."""
    md_content = """
## Features

- Feature one
- Feature two
"""
    result = extract_bulleted_list(md_content, "## Features")
    assert len(result) == 2
```

### Test 6: Extract Frontmatter Field
```python
def test_extract_frontmatter():
    """Extract YAML frontmatter field."""
    md_content = """---
title: Test Document
status: active
---
# Content
"""
    result = extract_frontmatter(md_content, "status")
    assert result == "active"
```

### Test 7: Extract Code Block
```python
def test_extract_code_block():
    """Extract first fenced code block."""
    md_content = """
## Example

```python
def hello():
    print("world")
```
"""
    result = extract_code_block(md_content, "## Example")
    assert "def hello():" in result
```

### Test 8: Extract Full Section
```python
def test_extract_full_section():
    """Extract everything under a heading until next same-level heading."""
    md_content = """
## Section One

Content here.

More content.

## Section Two

Different content.
"""
    result = extract_full_section(md_content, "## Section One")
    assert "Content here" in result
    assert "Different content" not in result
```

### Test 9: Loader Format Template
```python
def test_loader_format():
    """Format extracted values into template."""
    loader = Loader(config_path)
    extracted = {"mission": "Test mission", "principles": ["P1", "P2"]}
    result = loader.format(extracted)
    assert "Mission: Test mission" in result
```

### Test 10: Loader Integration
```python
def test_loader_load():
    """Full load() integration test."""
    loader = Loader(example_config_path)
    result = loader.load()
    assert isinstance(result, str)
    assert len(result) > 0
```

---

## Detailed Design

### New File: `.claude/haios/lib/loader.py`

**Pattern Verification (E2-255):** Sibling `.claude/lib/config.py` patterns (to be adopted):
- Standard imports (pathlib, yaml, typing)
- Singleton pattern (optional, not needed here)
- `CONFIG_DIR = Path(__file__).parent.parent / "config"` for path resolution (relative to haios/lib/)
- Graceful degradation on file not found

**Note:** This is the first module in `.claude/haios/lib/`. See obs-219-001 for migration plan of `.claude/lib/` contents.

### Function/Component Signatures

```python
# .claude/haios/lib/loader.py
from pathlib import Path
from typing import Dict, Any, List, Optional
import re
import yaml


class Loader:
    """
    Config-driven content extractor for structured markdown files.

    Implements CH-003 extraction DSL for the Configuration arc.

    Usage:
        loader = Loader(Path("config/loaders/identity.yaml"))
        content = loader.load()  # Returns injection-ready string
    """

    def __init__(self, config_path: Path):
        """
        Initialize loader with config file.

        Args:
            config_path: Path to YAML config defining extractions

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config is invalid YAML
        """

    def extract(self) -> Dict[str, Any]:
        """
        Extract all values defined in config.

        Returns:
            Dict mapping extraction names to extracted values
        """

    def format(self, extracted: Dict[str, Any]) -> str:
        """
        Format extracted values using output template.

        Args:
            extracted: Dict from extract()

        Returns:
            Formatted string ready for injection
        """

    def load(self) -> str:
        """
        Extract and format in one call.

        Returns:
            Injection-ready string
        """
        return self.format(self.extract())


# Extraction functions (module-level for testability)
def extract_blockquote(content: str, section: str) -> str:
    """Extract first `> ` block from section."""

def extract_first_paragraph(content: str, section: str) -> str:
    """Extract text until first blank line after section heading."""

def extract_all_h3(content: str, section: str) -> List[str]:
    """Extract all ### headings with their first line."""

def extract_numbered_list(content: str, section: str) -> List[str]:
    """Extract all 1. 2. 3. items."""

def extract_bulleted_list(content: str, section: str) -> List[str]:
    """Extract all - items."""

def extract_frontmatter(content: str, field: str) -> Any:
    """Extract YAML frontmatter field value."""

def extract_code_block(content: str, section: str) -> str:
    """Extract first fenced code block."""

def extract_full_section(content: str, section: str) -> str:
    """Extract everything under heading until next same-level heading."""
```

### Call Chain Context

```
just coldstart
    |
    +-> cli.py context-load
    |       |
    |       +-> ContextLoader.load_identity()
    |               |
    |               +-> Loader(identity.yaml).load()  # <-- NEW
    |                       Returns: str (injection-ready content)
    |
    +-> print(content)  # Agent receives extracted content
```

### Behavior Logic

```
Config YAML → Loader.__init__()
                    |
                    +-> parse config
                    |
              Loader.extract()
                    |
                    +-> for each extraction in config:
                    |       |
                    |       +-> read source file
                    |       +-> find section
                    |       +-> call extraction function by type
                    |       +-> store result
                    |
              Loader.format(extracted)
                    |
                    +-> apply output template with {placeholders}
                    |
                    +-> return formatted string
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Module-level extraction functions | Functions outside class | Testable independently, class orchestrates |
| Regex-based extraction | stdlib `re` module | No external deps, sufficient for markdown patterns |
| Section-scoped extraction | Find section, then extract within | Prevents cross-section extraction errors |
| Template-based formatting | `str.format()` with config template | Simple, readable, no Jinja2 dependency |
| Graceful missing section | Return empty string | Loader shouldn't crash on missing optional content |
| Base path from config | `base_path` field in config | Allows relative paths in extraction definitions |

### Input/Output Examples

**Real Example with L0-telos.md:**

```yaml
# identity.yaml config
base_path: .claude/haios/manifesto
extract:
  mission:
    file: L0-telos.md
    section: "## The Prime Directive"
    type: blockquote
output:
  template: |
    PRIME DIRECTIVE: {mission}
```

**Input (L0-telos.md lines 79-81):**
```markdown
## The Prime Directive

> "The system's success is not measured in lines of code, but in its ability to reduce the Operator's cognitive load..."
```

**Output:**
```
PRIME DIRECTIVE: "The system's success is not measured in lines of code, but in its ability to reduce the Operator's cognitive load..."
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Section not found | Return empty string, log warning | Test with missing section |
| File not found | Raise FileNotFoundError | Test with bad path |
| Empty extraction | Return empty string | Test with empty section |
| Nested blockquotes | Extract outermost only | Test 1 |
| Multi-line blockquote | Join with spaces | Test 1 |
| Frontmatter missing field | Return None | Test 6 |

### Open Questions

**Q: Should extraction functions be class methods or module functions?**

Module functions - allows direct testing without Loader instantiation, class orchestrates.

**Q: How to handle encoding?**

Always UTF-8, same as sibling modules.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | - | - | No operator decisions required - spec is clear |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_loader.py`
- [ ] Add all 10 tests from Tests First section
- [ ] Verify all tests fail (red) - module doesn't exist yet

### Step 2: Create Loader Module Skeleton
- [ ] Create `.claude/haios/lib/loader.py` with class and function stubs
- [ ] Add docstrings per signatures above
- [ ] Tests still fail (stubs raise NotImplementedError)

### Step 3: Implement Extraction Functions
- [ ] Implement `extract_frontmatter()` - Tests 6 pass
- [ ] Implement `extract_blockquote()` - Test 1 passes
- [ ] Implement `extract_first_paragraph()` - Test 2 passes
- [ ] Implement `extract_all_h3()` - Test 3 passes
- [ ] Implement `extract_numbered_list()` - Test 4 passes
- [ ] Implement `extract_bulleted_list()` - Test 5 passes
- [ ] Implement `extract_code_block()` - Test 7 passes
- [ ] Implement `extract_full_section()` - Test 8 passes

### Step 4: Implement Loader Class
- [ ] Implement `Loader.__init__()` - config parsing
- [ ] Implement `Loader.extract()` - orchestrate extraction functions
- [ ] Implement `Loader.format()` - template substitution, Test 9 passes
- [ ] Implement `Loader.load()` - Test 10 passes

### Step 5: Create Example Config
- [ ] Create `.claude/haios/config/loaders/` directory
- [ ] Create `example.yaml` with L0-telos.md extraction
- [ ] Verify integration test works with real file

### Step 6: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/lib/README.md` with loader.py entry
- [ ] **MUST:** Create `.claude/haios/config/loaders/README.md`

### Step 7: Verification
- [ ] All 10 tests pass
- [ ] Run full test suite (no regressions)
- [ ] Verify example config extracts real content from L0-telos.md

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Regex edge cases in markdown parsing | Medium | Comprehensive test suite with real markdown files; edge case tests |
| Import path confusion (two lib dirs) | Medium | Document in README; obs-219-001 tracks migration |
| Extraction DSL too limited | Low | 8 types cover spec; extensible design allows adding types |
| Performance on large files | Low | Not a concern for config files (<500 lines); defer optimization |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-005/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| `.claude/haios/lib/loader.py` with extract/format/load methods | [ ] | Read file, verify class and methods exist |
| 8 extraction types implemented | [ ] | Tests 1-8 pass |
| Output template system | [ ] | Test 9 passes |
| Unit tests in `tests/test_loader.py` | [ ] | All 10 tests pass |
| Example config in `.claude/haios/config/loaders/example.yaml` | [ ] | File exists, integration test passes |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/loader.py` | Loader class with extract/format/load, 8 extraction functions | [ ] | |
| `tests/test_loader.py` | 10 tests covering all extraction types | [ ] | |
| `.claude/haios/config/loaders/example.yaml` | Working example extracting from L0-telos.md | [ ] | |
| `.claude/haios/lib/README.md` | **MUST:** Documents loader.py | [ ] | New directory |
| `.claude/haios/config/loaders/README.md` | **MUST:** Documents config format | [ ] | New directory |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest [test_file] -v
# Expected: X tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- @.claude/haios/epochs/E2_3/arcs/configuration/CH-003-loader-base.md (chapter spec)
- @.claude/haios/epochs/E2_3/arcs/configuration/ARC.md (arc context with extraction DSL)
- @.claude/haios/manifesto/L4-implementation.md (Module-First principle)
- @.claude/haios/epochs/E2_3/observations/obs-219-001.md (.claude/lib migration observation)
- @.claude/lib/config.py (sibling pattern reference)
- Session 218 checkpoint (memory_refs: 82199-82229 - Module-First principle)

---
