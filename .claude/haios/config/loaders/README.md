# generated: 2026-01-21
# System Auto: last updated on: 2026-01-22T22:43:26
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

| File | Purpose | Status |
|------|---------|--------|
| `example.yaml` | Example extracting from L0-telos.md and L1-principal.md | Reference |
| `identity.yaml` | Identity loader for coldstart - extracts L0-L4 essence | **Implemented (WORK-007)** |
| `session.yaml` | Session context loader (checkpoint, memory) | Planned (CH-005) |
| `work.yaml` | Work queue loader | Planned (CH-006) |

## Integration with ContextLoader (WORK-008, WORK-009)

Loaders are invoked by `ContextLoader` based on role configuration in `haios.yaml`:

```yaml
# .claude/haios/config/haios.yaml
context:
  roles:
    main:
      loaders: [identity]  # Which loaders to run for this role
    builder:
      loaders: [identity]
  loader_registry:
    identity:
      module: identity_loader
      class: IdentityLoader
```

### Call Chain

```
just coldstart
  → cli.py context-load
    → ContextLoader.load_context(role="main")
      → For each loader in roles[role].loaders:
          → LoaderClass().load()
      → Returns GroundedContext with loaded_context dict
```

### Adding a New Loader

1. Create `loaders/{name}.yaml` with extraction rules
2. Create `.claude/haios/lib/{name}_loader.py` implementing `load() -> str`
3. Register in `haios.yaml` under `context.loader_registry`
4. Add to appropriate roles under `context.roles`

No code changes to ContextLoader required - fully config-driven.

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
