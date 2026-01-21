# generated: 2026-01-21
# System Auto: last updated on: 2026-01-21T20:58:07
"""
Tests for the Loader extraction DSL module.

WORK-005: Implement Loader Base for Configuration Arc
CH-003: Loader Base chapter

Tests extraction functions and Loader class for config-driven
content extraction from structured markdown files.
"""
import pytest
from pathlib import Path
import tempfile
import os

# Import from the haios lib directory
import sys
from pathlib import Path

# Add the haios lib directory to path for imports
haios_lib = Path(__file__).parent.parent / ".claude" / "haios" / "lib"
sys.path.insert(0, str(haios_lib))

from loader import (
    Loader,
    extract_blockquote,
    extract_first_paragraph,
    extract_all_h3,
    extract_numbered_list,
    extract_bulleted_list,
    extract_frontmatter,
    extract_code_block,
    extract_full_section,
)


# =============================================================================
# Test 1: Extract Blockquote
# =============================================================================
def test_extract_blockquote():
    """Extract first blockquote from a section."""
    md_content = """
## The Prime Directive

> The system's success is measured by its ability to reduce cognitive load.

Other text here.
"""
    result = extract_blockquote(md_content, "## The Prime Directive")
    assert result == "The system's success is measured by its ability to reduce cognitive load."


def test_extract_blockquote_multiline():
    """Extract multi-line blockquote (joined with spaces)."""
    md_content = """
## Quote Section

> This is line one
> and this is line two
> and line three.

After quote.
"""
    result = extract_blockquote(md_content, "## Quote Section")
    assert "line one" in result
    assert "line two" in result
    assert "line three" in result


def test_extract_blockquote_missing_section():
    """Return empty string when section not found."""
    md_content = """
## Other Section

> Some quote.
"""
    result = extract_blockquote(md_content, "## Missing Section")
    assert result == ""


# =============================================================================
# Test 2: Extract First Paragraph
# =============================================================================
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


def test_extract_first_paragraph_single_line():
    """Extract single-line paragraph."""
    md_content = """
## Section

Single line paragraph.

More content.
"""
    result = extract_first_paragraph(md_content, "## Section")
    assert result.strip() == "Single line paragraph."


# =============================================================================
# Test 3: Extract All H3 Headings
# =============================================================================
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
    assert "Context Must Persist" in result[1]


def test_extract_all_h3_with_content():
    """H3 extraction includes heading and first content line."""
    md_content = """
## Features

### Feature A
This is feature A description.

More about A.

### Feature B
Feature B is different.
"""
    result = extract_all_h3(md_content, "## Features")
    assert len(result) == 2
    # Each result should include heading and first line
    assert "Feature A" in result[0]
    assert "feature A description" in result[0]


# =============================================================================
# Test 4: Extract Numbered List
# =============================================================================
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
    assert "First step" in result[0]
    assert "Second step" in result[1]
    assert "Third step" in result[2]


def test_extract_numbered_list_mixed_numbers():
    """Extract numbered items regardless of actual number."""
    md_content = """
## Items

1. Item one
5. Item five (numbered as 5)
10. Item ten
"""
    result = extract_numbered_list(md_content, "## Items")
    assert len(result) == 3


# =============================================================================
# Test 5: Extract Bulleted List
# =============================================================================
def test_extract_bulleted_list():
    """Extract all - items."""
    md_content = """
## Features

- Feature one
- Feature two
"""
    result = extract_bulleted_list(md_content, "## Features")
    assert len(result) == 2
    assert "Feature one" in result[0]
    assert "Feature two" in result[1]


def test_extract_bulleted_list_with_asterisks():
    """Also extract * items as bullets."""
    md_content = """
## Items

* Item with asterisk
- Item with dash
* Another asterisk
"""
    result = extract_bulleted_list(md_content, "## Items")
    assert len(result) == 3


# =============================================================================
# Test 6: Extract Frontmatter Field
# =============================================================================
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


def test_extract_frontmatter_missing_field():
    """Return None for missing frontmatter field."""
    md_content = """---
title: Test Document
---
# Content
"""
    result = extract_frontmatter(md_content, "missing_field")
    assert result is None


def test_extract_frontmatter_no_frontmatter():
    """Return None when no frontmatter exists."""
    md_content = """# No Frontmatter

Just content.
"""
    result = extract_frontmatter(md_content, "status")
    assert result is None


# =============================================================================
# Test 7: Extract Code Block
# =============================================================================
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
    assert 'print("world")' in result


def test_extract_code_block_with_language():
    """Code block extraction preserves content, not language tag."""
    md_content = """
## Code

```javascript
const x = 1;
```
"""
    result = extract_code_block(md_content, "## Code")
    assert "const x = 1" in result
    # Language tag should NOT be in the result
    assert "javascript" not in result


# =============================================================================
# Test 8: Extract Full Section
# =============================================================================
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
    assert "More content" in result
    assert "Different content" not in result


def test_extract_full_section_with_subsections():
    """Full section includes subsections."""
    md_content = """
## Main Section

Intro text.

### Subsection A

Content A.

### Subsection B

Content B.

## Next Main Section

Other content.
"""
    result = extract_full_section(md_content, "## Main Section")
    assert "Intro text" in result
    assert "Subsection A" in result
    assert "Content A" in result
    assert "Subsection B" in result
    assert "Other content" not in result


# =============================================================================
# Test 9: Loader Format Template
# =============================================================================
def test_loader_format():
    """Format extracted values into template."""
    # Create temp config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
base_path: .
extract: {}
output:
  template: |
    Mission: {mission}
    Principles: {principles}
""")
        config_path = Path(f.name)

    try:
        loader = Loader(config_path)
        extracted = {"mission": "Test mission", "principles": "P1, P2"}
        result = loader.format(extracted)
        assert "Mission: Test mission" in result
        assert "Principles: P1, P2" in result
    finally:
        os.unlink(config_path)


def test_loader_format_list_values():
    """Format handles list values."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
base_path: .
extract: {}
output:
  template: |
    Items: {items}
  list_separator: ", "
""")
        config_path = Path(f.name)

    try:
        loader = Loader(config_path)
        extracted = {"items": ["A", "B", "C"]}
        result = loader.format(extracted)
        assert "Items:" in result
        # List should be joined
        assert "A" in result
        assert "B" in result
    finally:
        os.unlink(config_path)


# =============================================================================
# Test 10: Loader Integration
# =============================================================================
def test_loader_load():
    """Full load() integration test with real-ish content."""
    # Create temp directory with config and source file
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create source markdown file
        source_file = tmpdir / "source.md"
        source_file.write_text("""---
title: Test Source
status: active
---
# Test Source

## The Mission

> This is the mission statement.

## Features

- Feature A
- Feature B
""", encoding='utf-8')

        # Create config file
        config_file = tmpdir / "config.yaml"
        config_file.write_text(f"""
base_path: {tmpdir}
extract:
  mission:
    file: source.md
    section: "## The Mission"
    type: blockquote
  features:
    file: source.md
    section: "## Features"
    type: bulleted_list
  status:
    file: source.md
    type: frontmatter
    field: status
output:
  template: |
    MISSION: {{mission}}
    STATUS: {{status}}
    FEATURES: {{features}}
""", encoding='utf-8')

        loader = Loader(config_file)
        result = loader.load()

        assert isinstance(result, str)
        assert len(result) > 0
        assert "MISSION:" in result
        assert "mission statement" in result
        assert "STATUS:" in result
        assert "active" in result
        assert "FEATURES:" in result


def test_loader_load_missing_file():
    """Loader handles missing source file gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        config_file = tmpdir / "config.yaml"
        config_file.write_text(f"""
base_path: {tmpdir}
extract:
  content:
    file: nonexistent.md
    section: "## Section"
    type: blockquote
output:
  template: "Content: {{content}}"
""", encoding='utf-8')

        loader = Loader(config_file)
        # Should not raise, but return empty for missing file
        result = loader.load()
        assert isinstance(result, str)


# =============================================================================
# Edge Cases
# =============================================================================
def test_extract_blockquote_nested():
    """Handle nested blockquotes - extract outermost."""
    md_content = """
## Nested

> Outer quote
> > Inner quote
> Back to outer
"""
    result = extract_blockquote(md_content, "## Nested")
    assert "Outer quote" in result


def test_section_at_end_of_file():
    """Extract section that goes to end of file."""
    md_content = """
## First Section

Some content.

## Last Section

Final content here.
No more sections after.
"""
    result = extract_full_section(md_content, "## Last Section")
    assert "Final content here" in result
    assert "No more sections after" in result
