# generated: 2026-01-21
# System Auto: last updated on: 2026-01-21T21:00:36
# Loader Configurations

YAML configuration files for the Loader extraction system (WORK-005).

## Purpose

Loader configs define what content to extract from structured markdown files
and how to format it for injection into agent context. This enables
token-efficient context loading during coldstart and other operations.

## Config Structure

```yaml
# Base path for source files (relative to project root)
base_path: .claude/haios/manifesto

# Extractions to perform
extract:
  extraction_name:
    file: source_file.md
    section: "## Section Heading"  # Optional for frontmatter
    type: blockquote              # Extraction type
    field: field_name             # For frontmatter type only

# Output formatting
output:
  template: |
    Label: {extraction_name}
  list_separator: "\n- "          # For list types
```

## Extraction Types

| Type | Description | Requires Section |
|------|-------------|------------------|
| `blockquote` | First `> ` block in section | Yes |
| `first_paragraph` | Text until first blank line | Yes |
| `all_h3` | All `### ` headings with first line | Yes |
| `numbered_list` | All `1. ` items | Yes |
| `bulleted_list` | All `- ` or `* ` items | Yes |
| `frontmatter` | YAML frontmatter field | No (uses `field`) |
| `code_block` | First fenced code block | Yes |
| `full_section` | Everything under heading | Yes |

## Files

| File | Purpose |
|------|---------|
| `example.yaml` | Example extracting from L0-telos.md and L1-principal.md |
| `identity.yaml` | (Future) Identity loader for coldstart |
| `session.yaml` | (Future) Session context loader |
| `work.yaml` | (Future) Work queue loader |

## Usage

```python
from pathlib import Path
import sys

# Add haios lib to path
haios_lib = Path('.claude/haios/lib')
sys.path.insert(0, str(haios_lib))

from loader import Loader

loader = Loader(Path('.claude/haios/config/loaders/example.yaml'))
content = loader.load()
print(content)
```

## Related

- `.claude/haios/lib/loader.py` - Loader implementation
- `tests/test_loader.py` - Unit tests
- CH-003 Loader Base chapter spec
