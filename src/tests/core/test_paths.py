from __future__ import annotations

# ANNOTATION_BLOCK_START
{
  "artifact_annotation_header": {
    "artifact_id_of_host": "test_core_paths_py_g150",
    "g_annotation_created": 150,
    "version_tag_of_host_at_annotation": "1.0.0"
  },
  "payload": {
    "description": "Unit tests for the core.paths module, specifically validating the safe_join security function.",
    "artifact_type": "TEST_SCRIPT_PYTHON_PYTEST",
    "purpose_statement": "To provide verifiable evidence that the path sandboxing primitive correctly prevents path traversal attacks.",
    "internal_dependencies": ["core_paths_py_g148", "core_exceptions_py_g137"],
    "linked_issue_ids": ["issue_00121"]
  }
}
# ANNOTATION_BLOCK_END

"""Comprehensive tests for core.paths.safe_join

These tests cover:
1. Happy‑path joins within the sandbox.
2. Rejection of path‑traversal attempts and absolute outsider paths.
3. Symlink‑escape protection.
4. Windows‑specific absolute path rejection (skipped on non‑Windows platforms).
5. Validation that the sandbox root itself must be absolute.

Running the suite:
$ pytest tests/core/test_paths.py
"""

import os
import pathlib
import sys
from typing import Iterable

import pytest

# Import the unit under test *directly* to avoid NameError during CI collection
from core.paths import safe_join
from core.exceptions import PathEscapeError
from pathlib import Path

###############################################################################
# Fixtures
###############################################################################

@pytest.fixture()
def sandbox(tmp_path: pathlib.Path) -> pathlib.Path:
    """Return a temporary sandbox root as an **absolute** path."""
    root = tmp_path / "workspace"
    root.mkdir()
    return root.resolve()

###############################################################################
# Helper data
###############################################################################

# Path fragments that SHOULD be accepted when joined onto the sandbox
_VALID_PARTS: tuple[str | os.PathLike[str], ...] = (
    "subdir",  # simple relative segment
    "subdir/child",  # nested relative
    pathlib.Path("nested") / "grandchild",  # mixed Path objects
)

# Malicious / invalid fragments that MUST be rejected with PathEscapeError
_INVALID_PARTS: tuple[str | os.PathLike[str], ...] = (
    "../outside.txt",  # parent traversal
    "../../etc/passwd",  # deep traversal
    "/etc/passwd",  # absolute outsider
    "dir/../../../../etc/passwd",  # embedded traversal
)

# Windows absolute outsider (e.g. on POSIX this still must fail but we test only on Windows)
_WINDOWS_OUTSIDER = r"C:\\Windows\\System32"

###############################################################################
# Tests – positive cases
###############################################################################

def test_safe_join_happy_paths(sandbox: pathlib.Path) -> None:
    """safe_join should resolve to a path under root for valid relative parts."""
    for part in _VALID_PARTS:
        result = safe_join(sandbox, part)
        assert sandbox == result or sandbox in result.parents, (
            f"{result} should lie within sandbox {sandbox}"
        )
        # Path objects only
        assert isinstance(result, pathlib.Path)

###############################################################################
# Tests – traversal & outsider rejection
###############################################################################

@pytest.mark.parametrize("malicious", _INVALID_PARTS)
def test_safe_join_prevents_path_traversal(sandbox: pathlib.Path, malicious: str) -> None:
    """Any attempt to escape the sandbox via traversal or absolute path throws."""
    with pytest.raises(PathEscapeError):
        _ = safe_join(sandbox, malicious)

# Windows‑specific absolute outsider path (skipped on non‑Windows)
@pytest.mark.skipif(sys.platform != "win32", reason="Windows‑specific path escape test")
def test_safe_join_rejects_windows_absolute(sandbox: pathlib.Path) -> None:
    with pytest.raises(PathEscapeError):
        _ = safe_join(sandbox, _WINDOWS_OUTSIDER)

###############################################################################
# Tests – symlink escape scenarios
###############################################################################

def test_safe_join_rejects_symlink_escape(tmp_path: pathlib.Path, sandbox: pathlib.Path) -> None:
    """A symlink that *points outside* the sandbox must be treated as an escape."""
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()

    # Create a symlink inside the sandbox pointing to the outside directory
    link_inside = sandbox / "link_out"
    link_inside.symlink_to(outside_dir, target_is_directory=True)

    with pytest.raises(PathEscapeError):
        safe_join(sandbox, "link_out/escaped.txt")

###############################################################################
# Tests – sandbox root validation
###############################################################################

def test_safe_join_requires_absolute_sandbox_root(tmp_path: pathlib.Path) -> None:
    """Passing a non‑absolute root should raise PathEscapeError or ValueError."""
    # Intentionally make a *relative* root path
    relative_root = pathlib.Path("relative_root")
    with pytest.raises((PathEscapeError, ValueError)):
        safe_join(relative_root, "child.txt")

    """The function must reject a relative path for the sandbox root."""
    relative_sandbox = Path("./relative_dir")
    with pytest.raises(ValueError, match="Sandbox root must be an absolute path."):
        safe_join(relative_sandbox, "file.txt")