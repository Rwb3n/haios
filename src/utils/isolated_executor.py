from __future__ import annotations

# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "utils_isolated_executor_py_g237",
        "g_annotation_created": 237,
        "version_tag_of_host_at_annotation": "1.0.0",
    },
    "payload": {
        "description": "A utility for running tasks in an isolated process.",
        "artifact_type": "UTILITY_MODULE_PYTHON",
        "status_in_lifecycle": "PROPOSED",
        "purpose_statement": "To provide a cross-platform mechanism for process isolation, as per ADR-OS-018.",
        "authors_and_contributors": [{"g_contribution": 237, "identifier": "Roo"}],
        "internal_dependencies": ["core.config", "core.exceptions", "task_executor"],
        "external_dependencies": [
            {"name": "psutil", "version_constraint": ">=5.9.0,<6.0.0"}
        ],
        "linked_issue_ids": ["issue_C3_roadmap"],
    },
}
# ANNOTATION_BLOCK_END

import multiprocessing
import os
import time
from pathlib import Path

import psutil

from core.config import Config
from core.exceptions import PathEscapeError
from task_executor import execute_task


def _isolated_task_wrapper(task, config, state_manager, secrets, result_queue):
    """A wrapper function to run a task in a separate process."""
    try:
        # This is a simplified check. A more robust implementation would
        # use a security manager to intercept all file system calls.
        if os.getcwd() != str(config.paths.project_workspace):
            raise PathEscapeError("Task attempted to change working directory.")

        result = execute_task(task, config, state_manager, secrets)
        result_queue.put(result)
    except Exception as e:
        result_queue.put(e)


class IsolatedTaskExecutor:
    """Runs a task in an isolated process and monitors its file access."""

    def __init__(self, config: Config):
        self.config = config

    def execute(self, task, state_manager, secrets) -> bool:
        """Executes a task in an isolated process."""
        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=_isolated_task_wrapper,
            args=(task, self.config, state_manager, secrets, result_queue),
        )
        process.start()

        # Monitor the process
        p = psutil.Process(process.pid)
        while process.is_alive():
            try:
                for f in p.open_files():
                    if not Path(f.path).is_relative_to(self.config.project_root):
                        p.terminate()
                        raise PathEscapeError(
                            f"Task attempted to access file outside of project root: {f.path}"
                        )
            except psutil.NoSuchProcess:
                break
            time.sleep(0.1)

        process.join()
        result = result_queue.get()

        if isinstance(result, Exception):
            raise result

        return result
