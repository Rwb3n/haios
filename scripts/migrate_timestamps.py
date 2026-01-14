# generated: 2025-12-21
# System Auto: last updated on: 2025-12-21T19:01:07
#!/usr/bin/env python3
"""Migrate legacy timestamp format to YAML frontmatter fields.

E2-126: Fix files with broken timestamp format from legacy PostToolUse.ps1.

The legacy format has timestamps as comments BEFORE the YAML frontmatter:
    # generated: 2025-12-15
    # System Auto: last updated on: 2025-12-20 14:30:00
    ---
    template: checkpoint
    ---

The correct format has timestamps AS YAML FIELDS inside frontmatter:
    ---
    template: checkpoint
    generated: 2025-12-15
    last_updated: 2025-12-20T14:30:00
    ---

Usage:
    python scripts/migrate_timestamps.py --dry-run  # Preview changes
    python scripts/migrate_timestamps.py            # Apply changes
"""

import re
import sys
from pathlib import Path


def normalize_timestamp(ts: str) -> str:
    """Normalize timestamp to ISO format."""
    # Handle "2025-12-20 14:30:00" -> "2025-12-20T14:30:00"
    ts = ts.strip()
    if ' ' in ts and 'T' not in ts:
        return ts.replace(' ', 'T')
    return ts


def migrate_file_content(content: str) -> tuple[str, bool]:
    """
    Convert legacy timestamp comments to YAML frontmatter fields.

    Returns:
        Tuple of (new_content, was_modified)
    """
    # Handle BOM
    had_bom = content.startswith('\ufeff')
    if had_bom:
        content = content[1:]

    lines = content.split('\n')

    # Extract legacy timestamps from beginning of file
    generated_date = None
    last_updated = None
    content_start = 0

    for i, line in enumerate(lines):
        # Strip BOM from line (can appear after legacy timestamps)
        clean_line = line.lstrip('\ufeff')
        if match := re.match(r'^#\s*generated:\s*(\d{4}-\d{2}-\d{2})', clean_line):
            generated_date = match.group(1)
            content_start = i + 1
        elif match := re.match(r'^#\s*System Auto:.*last updated on:\s*(.+)', clean_line):
            timestamp_str = match.group(1).strip()
            last_updated = normalize_timestamp(timestamp_str)
            content_start = i + 1
        elif clean_line.strip() == '---':
            # Hit the YAML frontmatter start
            break
        elif clean_line.strip() and not clean_line.startswith('#'):
            # Non-comment, non-empty line before --- means no frontmatter
            break

    # If no legacy timestamps found, return unchanged
    if generated_date is None and last_updated is None:
        return content, False

    # Find YAML frontmatter
    remaining_lines = lines[content_start:]
    remaining = '\n'.join(remaining_lines)

    # Strip BOM from remaining content
    remaining = remaining.lstrip('\ufeff')

    if not remaining.strip().startswith('---'):
        # No frontmatter to update
        return content, False

    # Parse frontmatter
    yaml_match = re.match(r'^---\s*\n(.*?)\n---', remaining, re.DOTALL)
    if not yaml_match:
        return content, False

    yaml_content = yaml_match.group(1)
    after_frontmatter = remaining[yaml_match.end():]

    # Parse existing YAML fields
    yaml_lines = yaml_content.split('\n')

    # Check if timestamps already exist in YAML
    has_generated = any(line.strip().startswith('generated:') for line in yaml_lines)
    has_last_updated = any(line.strip().startswith('last_updated:') for line in yaml_lines)

    # If both already exist, nothing to migrate
    if has_generated and has_last_updated:
        # But we still need to remove the legacy comments if they exist
        if content_start > 0:
            # Remove legacy comment lines, keep YAML
            new_content = remaining
            return new_content, True
        return content, False

    # Add timestamps to YAML if not already present
    if not has_generated and generated_date:
        yaml_lines.append(f'generated: {generated_date}')
    if not has_last_updated and last_updated:
        yaml_lines.append(f'last_updated: {last_updated}')

    # Rebuild file without legacy comments
    new_yaml = '\n'.join(yaml_lines)
    new_content = f'---\n{new_yaml}\n---{after_frontmatter}'

    return new_content, True


def find_files_to_migrate(root: Path) -> list[Path]:
    """Find all markdown files with legacy timestamp format."""
    files = []

    # Search patterns
    patterns = [
        root / 'docs' / '**' / '*.md',
        root / '.claude' / '**' / '*.md',
        root / 'CLAUDE.md',
    ]

    for pattern in patterns:
        for file in root.glob(str(pattern.relative_to(root))):
            if file.is_file():
                try:
                    content = file.read_text(encoding='utf-8', errors='ignore')
                    # Check if file starts with legacy format
                    if content.lstrip('\ufeff').startswith('# generated:'):
                        files.append(file)
                except Exception:
                    pass

    return sorted(set(files))


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Migrate legacy timestamps to YAML frontmatter')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    args = parser.parse_args()

    # Find project root
    script_dir = Path(__file__).parent
    root = script_dir.parent

    # Find files to migrate
    files = find_files_to_migrate(root)
    print(f"Found {len(files)} files with legacy timestamp format")

    if not files:
        print("Nothing to migrate!")
        return 0

    migrated = 0
    errors = 0

    for file in files:
        try:
            content = file.read_text(encoding='utf-8', errors='ignore')
            new_content, was_modified = migrate_file_content(content)

            if was_modified:
                if args.dry_run:
                    print(f"  [DRY-RUN] Would migrate: {file.relative_to(root)}")
                else:
                    file.write_text(new_content, encoding='utf-8')
                    print(f"  [MIGRATED] {file.relative_to(root)}")
                migrated += 1
        except Exception as e:
            print(f"  [ERROR] {file.relative_to(root)}: {e}")
            errors += 1

    print(f"\nSummary: {migrated} migrated, {errors} errors")

    if args.dry_run:
        print("\nRun without --dry-run to apply changes")

    return 0 if errors == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
