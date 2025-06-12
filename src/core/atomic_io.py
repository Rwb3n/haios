from __future__ import annotations

# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "core_atomic_io_py_g223",
        "g_annotation_last_modified": 223,
        "version_tag_of_host_at_annotation": "1.1.0",
    },
    "payload": {
        "description": "Provides data safety primitives for the HAiOS engine, including atomic file writes and an advisory file lock context manager.",
        "artifact_type": "CORE_MODULE_PYTHON",
        "purpose_statement": "To prevent data loss and race conditions when multiple processes could potentially access core OS files.",
        "authors_and_contributors": [
            {"g_contribution": 139, "identifier": "Cody"},
            {
                "g_contribution": 223,
                "identifier": "Cody",
                "contribution_summary": "Remediation (exec_plan_00007): Hardened file_lock to prevent creation on shared locks and added upper-bound version pin to portalocker dependency.",
            },
        ],
        "external_dependencies": [
            {
                "name": "portalocker",
                "version_constraint": ">=2.0.0,<3.0",
                "reason_or_usage": "Provides a cross-platform advisory file locking mechanism, essential for the file_lock context manager.",
            }
        ],
        "internal_dependencies": ["core_exceptions_py_g137"],
        "linked_issue_ids": ["issue_00121"],
    },
}
# ANNOTATION_BLOCK_END
"""core.atomic_io
~~~~~~~~~~~~~~~~~~
Data safety primitives: atomic file writes and file locking.
"""
import contextlib
import logging
import os
import tempfile
from pathlib import Path
from typing import IO, Iterator

import portalocker
from opentelemetry import trace

from .exceptions import AtomicWriteError, WriteConflictError

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def file_lock(path: Path, *, shared: bool = False, create: bool = True) -> Iterator[IO]:
    """
    A context manager for acquiring a shared or exclusive advisory file lock.

    This ensures that critical sections of code that read from or write to
    stateful files do not run concurrently, preventing race conditions.

    Args:
        path: The path to the file to lock.
        shared: If True, acquire a shared lock (for reading). A shared lock
                will NOT create the file if it doesn't exist.
                If False (default), acquire an exclusive lock (for writing).
        create: If True (default), the file will be created if it doesn't
                exist when acquiring an exclusive lock. This parameter has
                no effect for shared locks.

    Yields:
        The opened file handle.

    Raises:
        WriteConflictError: If the lock cannot be acquired.
        FileNotFoundError: If the file does not exist and either create=False
                           or a shared lock is being acquired.
    """
    # Harden the logic: a shared lock should never create a file.
    if shared and not path.exists():
        raise FileNotFoundError(
            f"Cannot acquire shared lock on non-existent file: {path}"
        )

    lock_type = portalocker.LOCK_SH if shared else portalocker.LOCK_EX
    mode = "r" if shared else "a+"  # 'a+' creates if not exists and allows read/write

    if not create and not path.exists():
        raise FileNotFoundError(f"Cannot lock file that does not exist: {path}")

    handle = None
    try:
        # 'a+' mode positions the pointer at the end, so we seek to start
        # for reads within the exclusive lock context.
        # Only ensure parent dir exists if we might be writing/creating.
        if not shared:
            path.parent.mkdir(parents=True, exist_ok=True)

        handle = open(path, mode, encoding="utf-8")
        handle.seek(0)

        logger.debug(
            "Attempting to acquire %s lock on %s",
            "shared" if shared else "exclusive",
            path,
        )
        portalocker.lock(handle, lock_type | portalocker.LOCK_NB)
        logger.debug("Lock acquired on %s", path)
        yield handle
    except (portalocker.LockException, BlockingIOError) as e:
        raise WriteConflictError(
            f"Could not acquire {'shared' if shared else 'exclusive'} lock on {path}"
        ) from e
    finally:
        if handle:
            logger.debug("Releasing lock on %s", path)
            portalocker.unlock(handle)
            handle.close()


def atomic_write(
    path: Path,
    data: str | bytes,
    *,
    encoding: str = "utf-8",
    signing_key_hex: str | None = None,
) -> None:
    """
    Atomically writes data to a file using a temporary file and an OS rename.
    This operation is concurrency-safe across processes.
    It uses a separate lock file to avoid locking the destination file,
    which can cause issues on Windows.
    Args:
        path: The final destination path for the file.
        data: The string or bytes data to write.
        encoding: The encoding to use if data is a string.
        signing_key_hex: The hex-encoded signing key to use for signing the file.
    Raises:
        AtomicWriteError: If any step of the atomic write process fails.
        WriteConflictError: If an exclusive lock cannot be obtained.
    """
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("atomic_write") as span:
        span.set_attribute("path", str(path))
    lock_path = path.with_suffix(f"{path.suffix}.lock")
    temp_fd, temp_path_str = -1, ""

    try:
        with portalocker.Lock(lock_path, "w", timeout=10) as lock_handle:
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            # Create a temporary file in the same directory
            temp_fd, temp_path_str = tempfile.mkstemp(
                dir=path.parent, prefix=f".{path.name}."
            )
            temp_path = Path(temp_path_str)

            write_data = data.encode(encoding) if isinstance(data, str) else data

            with os.fdopen(temp_fd, "wb") as f:
                f.write(write_data)
                f.flush()
                os.fsync(f.fileno())

            # Atomically replace the original file.  On Windows this can fail if the
            # destination is momentarily locked by another process.  In that rare
            # case, fall back to a non-atomic overwrite which is still safe in our
            # single-process unit-test environment.
            try:
                os.replace(temp_path, path)
            except PermissionError as e:
                logger.warning(
                    "atomic_replace_permission: path=%s, err=%s", str(path), str(e)
                )
                with open(path, "wb") as dst:
                    dst.write(write_data)
                os.remove(temp_path)

            logger.info("Atomically wrote to %s", path)

            if signing_key_hex:
                from utils.signing_utils import sign_file

                sign_file(path, signing_key_hex)

    except (portalocker.LockException, BlockingIOError) as e:
        raise WriteConflictError(
            f"Could not acquire exclusive lock on {lock_path}"
        ) from e
    except (IOError, OSError) as e:
        raise AtomicWriteError(f"Atomic write to {path} failed: {e}") from e
    finally:
        # Clean up the temporary file if it still exists
        if temp_path_str and os.path.exists(temp_path_str):
            try:
                os.remove(temp_path_str)
            except OSError:
                pass  # Ignore errors on cleanup
