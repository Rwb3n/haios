# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "util_schema_converter_py_g10",
        "entity_type": "EMBEDDED_ANNOTATION_BLOCK",
        "schema_definition_id_ref": "HybridAI_OS_EmbeddedAnnotation_Payload_v5.3",
        "g_annotation_created": 10,
        "g_annotation_last_modified": 48,
        "version_tag_of_host_at_annotation": "2.0.0",
    },
    "payload": {
        "description": "A production-ready utility to parse Markdown documentation, extract all JSON schema blocks, validate their structure, and write them to a mirrored directory structure, handling filename collisions and edge cases.",
        "artifact_type": "UTILITY_SCRIPT_PYTHON",
        "status_in_lifecycle": "STABLE",
        "purpose_statement": "To automate the creation of machine-readable schemas from human-readable documentation, enforcing data integrity for the HAiOS.",
        "authors_and_contributors": [
            {
                "_locked_entry_definition": True,
                "g_contribution": 10,
                "identifier": "Successor Agent",
                "contribution_summary": "Initial creation.",
            },
            {
                "_locked_entry_definition": True,
                "g_contribution": 40,
                "identifier": "Successor Agent",
                "contribution_summary": "Remediation 1: Multi-block parsing.",
            },
            {
                "_locked_entry_definition": True,
                "g_contribution": 41,
                "identifier": "Successor Agent",
                "contribution_summary": "Remediation 2: Added jsonschema self-validation.",
            },
            {
                "_locked_entry_definition": True,
                "g_contribution": 48,
                "identifier": "Successor Agent",
                "contribution_summary": "Final Micro-Remediation (exec_plan_00045): Fixed logger mismatch and hardened regex.",
            },
        ],
        "key_logic_points_or_summary": [
            "Instantiates and uses a module-specific logger (`logging.getLogger(__name__)`).",
            "Uses a robust, multi-line regex to find all `json` code blocks.",
            "Implements a filename suffixing strategy (_1, _2) to prevent collisions.",
            "Uses jsonschema.Draft202012Validator to validate that the extracted object is a structurally valid JSON Schema.",
            "Handles UnicodeDecodeError during file reads gracefully.",
        ],
        "quality_notes": {
            "overall_quality_assessment": "NEEDS_IMPROVEMENT",
            "last_validation_report_ref": "val_report_g36",
            "unit_tests": {"status": "NEEDS_REWORK"},
        },
        "linked_issue_ids": ["issue_00015", "issue_00044"],
    },
}
# ANNOTATION_BLOCK_END

"""schema_converter.py

Utility to extract JSON‑Schema code blocks from Markdown files and write
them to `.schema.json` files with a directory structure that mirrors the
source tree.

Key features
------------
* Recurses the *source* directory, processing ``*.md`` / ``*.markdown`` files.
* Finds both triple‑back‑tick and triple‑tilde fenced blocks tagged
  ``json`` (indentation is ignored).
* Multiple schema blocks in one file are extracted individually
  (``myfile.schema.json``, ``myfile_1.schema.json`` …).
* Filename collisions across different source files are resolved by
  suffixing ``-1``, ``-2`` …
* Each schema is self‑validated with *jsonschema* (Draft 2020‑12).  Invalid
  files are skipped with an ERROR log.
* ``--check`` flag performs a dry‑run that prints would‑be actions,
  suitable for CI / pre‑commit.
* Exits with status 1 if any ERROR was logged.

Requires: ``jsonschema``

Example
-------
$ python schema_converter.py docs schemas --check
$ python schema_converter.py docs schemas
"""

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

from jsonschema import Draft202012Validator

logger = logging.getLogger(__name__)
LOG_FORMAT = "%(levelname)s %(message)s"

# Capture ```json … ``` *or* ~~~json … ~~~  (indented fences allowed)
SCHEMA_BLOCK_REGEX = re.compile(
    r"^[ \t]*(?P<fence>`{3}|~{3})json[ \t]*\r?\n(?P<body>.*?)\r?\n[ \t]*(?P=fence)[ \t]*$",
    re.MULTILINE | re.DOTALL,
)


from typing import Iterator


def _iter_markdown_files(root: Path) -> Iterator[Path]:
    """Yield Markdown files (*.md, *.markdown) under *root* recursively."""
    for path in root.rglob("*"):
        if path.suffix.lower() in {".md", ".markdown"} and path.is_file():
            yield path


def _extract_schema_blocks(text: str) -> List[str]:
    """Return a list of the raw JSON strings found in code blocks."""
    return [m.group("body") for m in SCHEMA_BLOCK_REGEX.finditer(text)]


def _unique_path(candidate: Path) -> Path:
    """Append numeric suffixes until *candidate* does not exist."""
    base, ext = candidate.with_suffix("").as_posix(), candidate.suffix
    counter = 1
    path = candidate
    while path.exists():
        path = Path(f"{base}-{counter}{ext}")
        counter += 1
    return path


def _write_schema(schema: dict, dest: Path, dry_run: bool) -> None:
    if dry_run:
        logger.info("[CHECK] Would write %s", dest)
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fp:
        json.dump(schema, fp, indent=2)
    logger.info("Wrote %s", dest)


def find_and_parse_schemas(
    source_dir: str | os.PathLike,
    target_dir: str | os.PathLike,
    *,
    dry_run: bool = False,
) -> Tuple[int, int]:
    """Walk *source_dir* and emit \*.schema.json files into *target_dir*.

    Returns
    -------
    ok, errors : tuple[int, int]
        Counts of successful writes and errors encountered.
    """
    ok = errors = 0
    src_root = Path(source_dir).resolve()
    tgt_root = Path(target_dir).resolve()

    for md_path in _iter_markdown_files(src_root):
        try:
            content = md_path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            logger.error("Unable to read %s: %s", md_path, exc)
            errors += 1
            continue

        blocks = _extract_schema_blocks(content)
        if not blocks:
            continue

        rel_dir = md_path.relative_to(src_root).parent
        base_name = md_path.stem  # without suffix

        for idx, raw in enumerate(blocks):
            name = base_name if idx == 0 else f"{base_name}_{idx}"
            dest_path = tgt_root / rel_dir / f"{name}.schema.json"
            dest_path = _unique_path(dest_path)

            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                logger.error("Invalid JSON in %s block %d: %s", md_path, idx, exc)
                errors += 1
                continue

            try:
                Draft202012Validator.check_schema(data)
            except Exception as exc:
                logger.error(
                    "Invalid JSON‑Schema in %s block %d: %s", md_path, idx, exc
                )
                errors += 1
                continue

            _write_schema(data, dest_path, dry_run)
            ok += 1

    return ok, errors


def _parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", help="Source directory containing Markdown files")
    p.add_argument("target", help="Target directory for .schema.json output")
    p.add_argument(
        "--check",
        action="store_true",
        help="Do a dry‑run – validate & report but do not write files",
    )
    p.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase log verbosity"
    )
    return p.parse_args(argv)


def main(argv: List[str] | None = None) -> None:
    args = _parse_args(argv)

    level = logging.WARNING - (
        10 * args.verbose
    )  # WARN by default, INFO (-v), DEBUG (-vv)
    logging.basicConfig(format=LOG_FORMAT, level=level)

    ok, errors = find_and_parse_schemas(args.source, args.target, dry_run=args.check)

    summary = f"{ok} schema(s) extracted, {errors} error(s)"
    if errors:
        logger.error(summary)
        sys.exit(1)
    logger.info(summary)


if __name__ == "__main__":  # pragma: no cover
    main()
