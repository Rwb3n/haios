from __future__ import annotations

# ANNOTATION_BLOCK_START
{
  "artifact_annotation_header": {
    "artifact_id_of_host": "core_paths_py_g148",
    "g_annotation_created": 148,
    "version_tag_of_host_at_annotation": "1.0.0"
  },
  "payload": {
    "description": "Provides path manipulation utilities with a focus on security, including a sandboxed path joining function.",
    "artifact_type": "CORE_MODULE_PYTHON",
    "purpose_statement": "To prevent path traversal vulnerabilities by ensuring all file system access remains within designated project boundaries.",
    "authors_and_contributors": [{"g_contribution": 148, "identifier": "Cody"}],
    "internal_dependencies": ["core_exceptions_py_g137"],
    "linked_issue_ids": ["issue_00121"]
  }
}
# ANNOTATION_BLOCK_END
"""core.paths
~~~~~~~~~~~~~~
Security-hardened path manipulation utilities.
"""
import os
from pathlib import Path
from contextlib import contextmanager

from .exceptions import PathEscapeError


def safe_join(sandbox_root: Path, untrusted_subpath: str | Path) -> Path:
    """
    Safely joins an untrusted subpath to a sandbox root directory.

    It resolves the final path and strictly enforces that the resulting path
    is within the `sandbox_root`.

    Args:
        sandbox_root: The absolute, resolved path to the trusted root
                      directory that should not be escaped.
        untrusted_subpath: A relative path provided by an external source
                           (e.g., from a plan file).

    Returns:
        The resolved, absolute path if it is safe.

    Raises:
        PathEscapeError: If the resulting path is outside the sandbox_root.
        ValueError: If the sandbox_root is not an absolute path.
    """
    if not sandbox_root.is_absolute():
        raise ValueError("Sandbox root must be an absolute path.")

    # Join the untrusted path to the root.
    # Note: `Path` handles removing leading slashes from `untrusted_subpath`,
    # preventing trivial escapes like `/etc/passwd`.
    candidate_path = sandbox_root / untrusted_subpath

    # Resolve the path to get its canonical absolute form, collapsing `..`
    resolved_path = candidate_path.resolve()

    # The core security check: is the resolved path still inside the root?
    try:
        resolved_path.relative_to(sandbox_root)
        # If relative_to() succeeds, the path is safe.
        return resolved_path
    except ValueError as e:
        # ValueError is raised if the path is not a subpath of the root.
        raise PathEscapeError(
            f"Path traversal detected. Attempted to access '{resolved_path}' "
            f"which is outside the sandbox '{sandbox_root}'."
        ) from e

@contextmanager
def chroot(path: Path):
    """A context manager that temporarily changes the root directory."""
    original_root = os.open("/", os.O_RDONLY)
    try:
        os.chroot(path)
        os.chdir("/")
        yield
    finally:
        os.fchdir(original_root)
        os.chroot(".")
        os.close(original_root)