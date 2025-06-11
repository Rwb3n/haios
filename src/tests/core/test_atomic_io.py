# ANNOTATION_BLOCK_START
{
  "artifact_annotation_header": {
    "artifact_id_of_host": "test_core_atomic_io_py_g144",
    "g_annotation_created": 144,
    "version_tag_of_host_at_annotation": "1.0.0"
  },
  "payload": {
    "description": "Unit tests for the core.atomic_io module. Validates the correctness of atomic_write and the concurrency safety of file_lock.",
    "artifact_type": "TEST_SCRIPT_PYTHON_PYTEST",
    "purpose_statement": "To provide verifiable evidence that the data safety primitives prevent data loss and race conditions.",
    "internal_dependencies": ["core_atomic_io_py_g139"],
    "linked_issue_ids": ["issue_00121"]
  }
}
# ANNOTATION_BLOCK_END
"""tests.core.test_atomic_io
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Tests for the data safety primitives in core.atomic_io.
"""
import multiprocessing
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from core import atomic_io
from core.exceptions import AtomicWriteError, WriteConflictError

# --- Test atomic_write ---

def test_atomic_write_creates_file_with_correct_content(tmp_path: Path):
    """Happy path: atomic_write should create a file with the expected data."""
    test_file = tmp_path / "test.txt"
    test_data = "hello world"
    atomic_io.atomic_write(test_file, test_data)

    assert test_file.exists()
    assert test_file.read_text(encoding="utf-8") == test_data

def test_atomic_write_overwrites_existing_file(tmp_path: Path):
    """atomic_write should correctly replace an existing file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("initial content")

    new_data = "final content"
    atomic_io.atomic_write(test_file, new_data)

    assert test_file.read_text(encoding="utf-8") == new_data

@patch("os.replace")
def test_atomic_write_cleans_up_temp_file_on_failure(mock_replace, tmp_path: Path):
    """If os.replace fails, the temporary file should be removed."""
    mock_replace.side_effect = OSError("Disk full")
    test_file = tmp_path / "test.txt"
    test_data = "some data"

    with pytest.raises(AtomicWriteError):
        atomic_io.atomic_write(test_file, test_data)

    # Check that no stray temporary files are left in the directory
    temp_files = list(tmp_path.glob(".*"))
    assert not temp_files

# --- Test file_lock ---

def lock_file_exclusively(path: Path, queue: multiprocessing.Queue):
    """Target function for a separate process to acquire a lock."""
    try:
        with atomic_io.file_lock(path):
            # Signal that the lock was acquired
            queue.put("LOCKED")
            # Hold the lock for a short time to allow the main process to try
            multiprocessing.Event().wait(0.2)
        queue.put("RELEASED")
    except WriteConflictError:
        queue.put("CONFLICT")
    except Exception as e:
        queue.put(f"ERROR: {e}")

def test_file_lock_prevents_concurrent_exclusive_writes(tmp_path: Path):
    """A second process must not be able to acquire an exclusive lock."""
    test_file = tmp_path / "lock_test.txt"
    queue = multiprocessing.Queue()

    # Process 1 acquires the lock
    p1 = multiprocessing.Process(target=lock_file_exclusively, args=(test_file, queue))
    p1.start()

    # Wait until Process 1 confirms it has the lock
    assert queue.get(timeout=2) == "LOCKED"

    # Now, the main process (acting as Process 2) tries to acquire the lock
    with pytest.raises(WriteConflictError):
        with atomic_io.file_lock(test_file):
            # This code should not be reached
            pytest.fail("Second process was able to acquire exclusive lock.")

    # Wait for Process 1 to finish and release the lock
    assert queue.get(timeout=2) == "RELEASED"
    p1.join()

def test_file_lock_allows_concurrent_shared_reads(tmp_path: Path):
    """Multiple processes should be able to acquire shared locks concurrently."""
    test_file = tmp_path / "shared_lock_test.txt"
    test_file.write_text("data")

    # Both contexts should be able to acquire the shared lock without raising
    try:
        with atomic_io.file_lock(test_file, shared=True):
            with atomic_io.file_lock(test_file, shared=True):
                assert test_file.read_text() == "data"
    except WriteConflictError:
        pytest.fail("Could not acquire concurrent shared locks.")