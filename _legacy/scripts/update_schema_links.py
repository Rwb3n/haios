"""update_schema_links.py
One-off migration script to update references from the old schema folder
(`docs/schema`) to the new location (`docs/schema`).

Usage (from project root):
    python scripts/update_schema_links.py

The script walks selected text-based files across the repository and
updates occurrences in-place, emitting a summary of touched files.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

# Ordered list so the variant with trailing slash is processed first.
REPLACEMENTS: list[tuple[str, str]] = [
    ("docs/schema/", "docs/schema/"),
    ("docs/schema", "docs/schema"),
]

# File extensions considered text sources to update. Extend as needed.
TEXT_EXTENSIONS: set[str] = {
    "md",
    "py",
    "txt",
    "yml",
    "yaml",
    "toml",
    "cfg",
    "ini",
    "sh",
    "ps1",
    "json",
}
# Filenames without extension that should also be inspected (e.g., Makefile)
TEXT_FILENAMES: set[str] = {"Makefile", "makefile"}


def iter_target_files() -> Iterable[Path]:
    """Yield repo files likely to be text sources worth scanning."""
    for path in Path(".").rglob("*"):
        if path.is_dir():
            continue
        if path.name in TEXT_FILENAMES or path.suffix.lstrip(".") in TEXT_EXTENSIONS:
            yield path


def main() -> None:
    changed_files: list[Path] = []

    for filepath in iter_target_files():
        try:
            content = filepath.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Skip non-UTF-8 or binary-like files.
            continue
        original = content
        for old, new in REPLACEMENTS:
            content = re.sub(re.escape(old), new, content)
        if content != original:
            filepath.write_text(content, encoding="utf-8")
            changed_files.append(filepath)

    print(f"Updated {len(changed_files)} file(s).")
    for f in changed_files:
        print(f" - {f.as_posix()}")


if __name__ == "__main__":
    main() 