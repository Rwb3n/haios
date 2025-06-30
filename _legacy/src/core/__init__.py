# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "core_init_py_g136",
        "g_annotation_created": 136,
        "version_tag_of_host_at_annotation": "1.0.0",
    },
    "payload": {
        "description": "Initializes the 'core' module as a Python package.",
        "artifact_type": "CORE_MODULE_PYTHON",
    },
}
# ANNOTATION_BLOCK_END

# Expose key sub-modules at the package root for convenient imports, e.g.::
#     from core import atomic_io, paths
# This is especially helpful for legacy tests that expect these symbols on the
# top-level package (see tests under ``src/tests/core``).

from importlib import import_module as _imp

for _name in ("atomic_io", "paths", "config", "config_loader", "exceptions", "planner"):
    globals()[_name] = _imp(f"{__name__}.{_name}")

del _imp, _name

__all__ = [
    "atomic_io",
    "paths",
    "config",
    "config_loader",
    "exceptions",
    "planner",
]
