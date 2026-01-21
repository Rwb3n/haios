# generated: 2026-01-21
# System Auto: last updated on: 2026-01-21T22:21:25
"""
Config-driven content extractor for structured markdown files.

WORK-005: Implement Loader Base for Configuration Arc
CH-003: Loader Base chapter

Implements the extraction DSL for the Configuration arc, enabling
selective content extraction from markdown files based on YAML config.

Usage:
    from haios.lib.loader import Loader

    loader = Loader(Path("config/loaders/identity.yaml"))
    content = loader.load()  # Returns injection-ready string

Extraction Types:
    - blockquote: First `> ` block in section
    - first_paragraph: Text until first blank line
    - all_h3: All `### ` headings with first line
    - numbered_list: All `1. ` items
    - bulleted_list: All `- ` or `* ` items
    - frontmatter: YAML frontmatter field
    - code_block: First fenced code block
    - full_section: Everything under heading until next same-level
"""
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import re
import yaml
import logging

logger = logging.getLogger(__name__)

# Project root is 4 levels up from .claude/haios/lib/
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


# =============================================================================
# Extraction Functions (module-level for testability)
# =============================================================================

def _find_section(content: str, section_heading: str) -> Optional[str]:
    """
    Find content under a section heading.

    Args:
        content: Full markdown content
        section_heading: Heading to find (e.g., "## The Mission")

    Returns:
        Content from heading to next same-level heading, or None if not found
    """
    # Escape special regex characters in heading
    escaped_heading = re.escape(section_heading)
    # Determine heading level (count #)
    level = len(section_heading) - len(section_heading.lstrip('#'))

    # Pattern: heading followed by content until next same-level heading or EOF
    pattern = rf'^{escaped_heading}\s*$\n(.*?)(?=^{"#" * level} |\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

    if match:
        return match.group(1)
    return None


def extract_blockquote(content: str, section: str) -> str:
    """
    Extract first `> ` block from section.

    Args:
        content: Full markdown content
        section: Section heading (e.g., "## The Mission")

    Returns:
        Blockquote text (without `> ` prefix), or empty string if not found
    """
    section_content = _find_section(content, section)
    if not section_content:
        return ""

    # Find blockquote lines (starting with >)
    lines = section_content.split('\n')
    quote_lines = []
    in_quote = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('>'):
            in_quote = True
            # Remove > prefix and optional space
            quote_text = stripped[1:].lstrip(' ')
            # Handle nested quotes - just keep the outermost
            if quote_text.startswith('>'):
                # Nested quote - include as-is for now
                quote_lines.append(quote_text)
            else:
                quote_lines.append(quote_text)
        elif in_quote and stripped == '':
            # Blank line might end quote or be part of multi-paragraph quote
            # For simplicity, end quote on blank line
            break
        elif in_quote:
            # Non-quote line ends the block
            break

    return ' '.join(quote_lines).strip()


def extract_first_paragraph(content: str, section: str) -> str:
    """
    Extract text until first blank line after section heading.

    Args:
        content: Full markdown content
        section: Section heading

    Returns:
        First paragraph text, or empty string if not found
    """
    section_content = _find_section(content, section)
    if not section_content:
        return ""

    # Split into lines and find first non-empty paragraph
    lines = section_content.split('\n')
    paragraph_lines = []
    started = False

    for line in lines:
        stripped = line.strip()
        if stripped and not started:
            started = True
            paragraph_lines.append(stripped)
        elif started and stripped:
            paragraph_lines.append(stripped)
        elif started and not stripped:
            # Blank line ends paragraph
            break

    return ' '.join(paragraph_lines)


def extract_all_h3(content: str, section: str) -> List[str]:
    """
    Extract all ### headings with their first line of content.

    Args:
        content: Full markdown content
        section: Parent section heading (e.g., "## Principles")

    Returns:
        List of strings, each containing H3 heading and first content line
    """
    section_content = _find_section(content, section)
    if not section_content:
        return []

    results = []
    lines = section_content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('### '):
            heading = line.strip()[4:].strip()  # Remove "### " prefix
            # Find first non-empty content line after heading
            first_line = ""
            j = i + 1
            while j < len(lines):
                content_line = lines[j].strip()
                if content_line and not content_line.startswith('#'):
                    first_line = content_line
                    break
                elif content_line.startswith('#'):
                    # Next heading - stop
                    break
                j += 1
            results.append(f"{heading}\n{first_line}" if first_line else heading)
        i += 1

    return results


def extract_numbered_list(content: str, section: str) -> List[str]:
    """
    Extract all numbered list items (1. 2. 3. etc.).

    Args:
        content: Full markdown content
        section: Section heading

    Returns:
        List of item texts (without number prefix)
    """
    section_content = _find_section(content, section)
    if not section_content:
        return []

    # Match lines starting with number and period
    pattern = r'^\d+\.\s+(.+)$'
    matches = re.findall(pattern, section_content, re.MULTILINE)
    return matches


def extract_bulleted_list(content: str, section: str) -> List[str]:
    """
    Extract all bulleted list items (- or *).

    Args:
        content: Full markdown content
        section: Section heading

    Returns:
        List of item texts (without bullet prefix)
    """
    section_content = _find_section(content, section)
    if not section_content:
        return []

    # Match lines starting with - or *
    pattern = r'^[-*]\s+(.+)$'
    matches = re.findall(pattern, section_content, re.MULTILINE)
    return matches


def extract_frontmatter(content: str, field: str) -> Optional[Any]:
    """
    Extract YAML frontmatter field value.

    Args:
        content: Full markdown content (must start with ---)
        field: Field name to extract

    Returns:
        Field value, or None if not found
    """
    # Check for frontmatter
    if not content.strip().startswith('---'):
        return None

    # Extract frontmatter block
    pattern = r'^---\s*\n(.*?)\n---'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return None

    try:
        frontmatter = yaml.safe_load(match.group(1))
        if isinstance(frontmatter, dict):
            return frontmatter.get(field)
    except yaml.YAMLError:
        logger.warning(f"Failed to parse frontmatter")
        return None

    return None


def extract_code_block(content: str, section: str) -> str:
    """
    Extract first fenced code block content.

    Args:
        content: Full markdown content
        section: Section heading

    Returns:
        Code block content (without fence markers or language tag)
    """
    section_content = _find_section(content, section)
    if not section_content:
        return ""

    # Match fenced code block (``` with optional language)
    pattern = r'```\w*\n(.*?)```'
    match = re.search(pattern, section_content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def extract_full_section(content: str, section: str) -> str:
    """
    Extract everything under heading until next same-level heading.

    Args:
        content: Full markdown content
        section: Section heading

    Returns:
        Full section content, or empty string if not found
    """
    result = _find_section(content, section)
    return result.strip() if result else ""


# =============================================================================
# Loader Class
# =============================================================================

class Loader:
    """
    Config-driven content extractor for structured markdown files.

    Implements CH-003 extraction DSL for the Configuration arc.

    Usage:
        loader = Loader(Path("config/loaders/identity.yaml"))
        content = loader.load()  # Returns injection-ready string
    """

    # Map extraction type names to functions
    EXTRACTORS = {
        'blockquote': extract_blockquote,
        'first_paragraph': extract_first_paragraph,
        'all_h3': extract_all_h3,
        'numbered_list': extract_numbered_list,
        'bulleted_list': extract_bulleted_list,
        'frontmatter': extract_frontmatter,
        'code_block': extract_code_block,
        'full_section': extract_full_section,
    }

    def __init__(self, config_path: Path):
        """
        Initialize loader with config file.

        Args:
            config_path: Path to YAML config defining extractions

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config is invalid YAML
        """
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # Resolve base_path relative to project root or config location
        base_path = self.config.get('base_path', '.')
        if base_path == '.':
            self.base_path = self.config_path.parent
        else:
            # If absolute, use as-is; otherwise relative to project root
            base = Path(base_path)
            if base.is_absolute():
                self.base_path = base
            else:
                self.base_path = PROJECT_ROOT / base_path

    def extract(self) -> Dict[str, Any]:
        """
        Extract all values defined in config.

        Returns:
            Dict mapping extraction names to extracted values
        """
        extractions = self.config.get('extract', {})
        results = {}

        for name, spec in extractions.items():
            try:
                value = self._extract_one(name, spec)
                results[name] = value
            except Exception as e:
                logger.warning(f"Extraction '{name}' failed: {e}")
                results[name] = "" if spec.get('type') != 'frontmatter' else None

        return results

    def _extract_one(self, name: str, spec: Dict[str, Any]) -> Any:
        """
        Perform a single extraction.

        Args:
            name: Extraction name (for logging)
            spec: Extraction specification dict

        Returns:
            Extracted value
        """
        extract_type = spec.get('type', 'full_section')
        extractor = self.EXTRACTORS.get(extract_type)

        if not extractor:
            logger.warning(f"Unknown extraction type: {extract_type}")
            return ""

        # Handle frontmatter specially (doesn't need section)
        if extract_type == 'frontmatter':
            file_path = self.base_path / spec.get('file', '')
            if not file_path.exists():
                logger.warning(f"Source file not found: {file_path}")
                return None
            content = file_path.read_text(encoding='utf-8')
            return extractor(content, spec.get('field', ''))

        # Other types need file and section
        file_path = self.base_path / spec.get('file', '')
        if not file_path.exists():
            logger.warning(f"Source file not found: {file_path}")
            return "" if extract_type != 'all_h3' else []

        content = file_path.read_text(encoding='utf-8')
        section = spec.get('section', '')

        return extractor(content, section)

    def format(self, extracted: Dict[str, Any]) -> str:
        """
        Format extracted values using output template.

        Args:
            extracted: Dict from extract()

        Returns:
            Formatted string ready for injection
        """
        output_config = self.config.get('output', {})
        template = output_config.get('template', '')
        list_separator = output_config.get('list_separator', '\n')

        if not template:
            # No template - just dump values
            return '\n'.join(f"{k}: {v}" for k, v in extracted.items())

        # Process extracted values for template
        format_values = {}
        for key, value in extracted.items():
            if isinstance(value, list):
                format_values[key] = list_separator.join(str(v) for v in value)
            else:
                format_values[key] = value if value is not None else ""

        # Apply template
        try:
            return template.format(**format_values)
        except KeyError as e:
            logger.warning(f"Template placeholder not found in extracted values: {e}")
            # Return template with missing values as empty
            result = template
            for key, value in format_values.items():
                result = result.replace(f'{{{key}}}', str(value))
            return result

    def load(self) -> str:
        """
        Extract and format in one call.

        Returns:
            Injection-ready string
        """
        return self.format(self.extract())
