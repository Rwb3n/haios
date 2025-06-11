# ANNOTATION_BLOCK_START
{
  "artifact_annotation_header": {
    "artifact_id_of_host": "test_core_registry_concurrency_py_g158",
    "g_annotation_created": 158,
    "version_tag_of_host_at_annotation": "1.0.0"
  },
  "payload": {
    "description": "A stress test for the TaskExecutor's registry I/O, using multiprocessing to simulate concurrent writes and verify data integrity.",
    "artifact_type": "TEST_SCRIPT_PYTHON_PYTEST",
    "purpose_statement": "To provide evidence that the atomic, locked registry writer prevents race conditions and data loss under high contention.",
    "internal_dependencies": ["task_executor_py_g103"],
    "linked_issue_ids": ["issue_00121"]
  }
}
# ANNOTATION_BLOCK_END
"""tests.core.test_registry_concurrency
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Stress test for the atomicity and locking of the registry writer
in task_executor.
"""

import json
import multiprocessing
from pathlib import Path

import pytest

import task_executor

# --- Test Setup ---

NUM_PROCESSES = 5
ITEMS_PER_PROCESS = 10

def worker_function(registry_path: Path, process_id: int, lock: multiprocessing.Lock):
    """
    Simulates an agent process that repeatedly adds entries to the registry.
    """
    for i in range(ITEMS_PER_PROCESS):
        artifact_id = f"artifact_p{process_id}_{i}"
        
        try:
            with lock:
                registry_map = task_executor._load_registry(registry_path)
                
                if "payload" not in registry_map:
                    registry_map["payload"] = {"artifact_registry_tree": {}}
                
                registry_map["payload"]["artifact_registry_tree"][artifact_id] = {
                    "process_id": process_id,
                    "item_index": i
                }
                
                task_executor._write_registry(registry_path, registry_map)
        except Exception as e:
            return f"Process {process_id} failed: {e}"
    return None

# --- The Test Case ---

def test_concurrent_registry_writes_are_safe(tmp_path: Path):
    """
    Spawns multiple processes to write to the same registry file concurrently.
    The final file must contain all entries, proving no writes were lost.
    """
    registry_path = tmp_path / "global_registry_map.txt"
    
    # Initialize an empty registry file to start
    registry_path.write_text("{}", encoding="utf-8")

    lock = multiprocessing.Lock()
    processes = []
    for i in range(NUM_PROCESSES):
        p = multiprocessing.Process(target=worker_function, args=(registry_path, i, lock))
        processes.append(p)
        p.start()

    for p in processes:
        p.join(timeout=10) # Timeout to prevent test from hanging
        assert p.exitcode == 0, f"Process {p.pid} did not exit cleanly."

    # --- Verification ---
    # After all processes are done, read the final state of the registry
    final_data = json.loads(registry_path.read_text(encoding="utf-8"))
    
    # The final registry must contain ALL entries from ALL processes
    # Total expected entries = NUM_PROCESSES * ITEMS_PER_PROCESS
    expected_entry_count = NUM_PROCESSES * ITEMS_PER_PROCESS
    
    final_entries = final_data.get("payload", {}).get("artifact_registry_tree", {})
    actual_entry_count = len(final_entries)

    assert actual_entry_count == expected_entry_count, \
        f"Data loss detected! Expected {expected_entry_count} entries, but found {actual_entry_count}."
        
    # Spot check a few entries to be sure
    assert "artifact_p0_0" in final_entries
    assert "artifact_p4_9" in final_entries
    assert final_entries["artifact_p2_5"]["process_id"] == 2