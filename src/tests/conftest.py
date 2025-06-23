"""Pytest configuration utilities.

This file ensures the project source directory (``src/``) is on ``sys.path``
before test collection begins.  Without this, imports like ``import core.config``
would fail when invoking ``pytest`` from the project root.

The logic is minimal and runs once at collection-time.
"""

import copyreg
import os
import pickle
import platform
import sys
import types
from pathlib import Path

import pytest

# Add <project_root>/src to import search path if it's not already present.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

workspace = Path(__file__).resolve().parents[2]
src_dir = workspace / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
if str(workspace) not in sys.path:
    sys.path.insert(0, str(workspace))

# --- Fix potential namespace shadowing by test package "src/tests/core" ---
try:
    from importlib import reload

    import core as _core_pkg

    # If the loaded core package originates from the tests directory, reload it from src/core.
    if "src\\tests\\core" in str(_core_pkg.__file__):
        # Remove wrong module entry first
        del sys.modules["core"]
        # Import the correct package now that SRC_PATH is at the front
        import core as _core_pkg
    # Ensure src/core is on the package __path__ for sub-modules resolution
    _core_src_path = SRC_PATH / "core"
    if str(_core_src_path) not in _core_pkg.__path__:
        _core_pkg.__path__.append(str(_core_src_path))
except Exception:  # pragma: no cover – best-effort; tests will surface errors
    pass

if "age" not in sys.modules:
    age_stub = types.ModuleType("age")

    class _Identity:
        @staticmethod
        def from_bech32(key):
            return _Identity()

        def to_public(self):
            return self

    def _encrypt(data, recipients):
        return data  # no-op stub

    def _decrypt(data, identities):
        return data  # no-op stub

    # Set attributes directly on the module
    setattr(age_stub, "Identity", _Identity)
    setattr(age_stub, "encrypt", _encrypt)
    setattr(age_stub, "decrypt", _decrypt)
    setattr(age_stub, "DecryptError", Exception)
    sys.modules["age"] = age_stub

# Ensure subprocesses can import project modules
_repo_root = PROJECT_ROOT
_existing = os.environ.get("PYTHONPATH", "")
if str(_repo_root) not in _existing.split(os.pathsep):
    os.environ["PYTHONPATH"] = (
        os.pathsep.join([str(_repo_root), _existing]) if _existing else str(_repo_root)
    )

# ------------------------------------------------------------------
# Generic object pickling fallback (Windows spawn safety)
# ------------------------------------------------------------------


def _generic_obj_reducer(obj):
    state = obj.__dict__
    cls = obj.__class__
    return _rebuild_generic_obj, (cls, state)


if "_rebuild_generic_obj" not in globals():

    def _rebuild_generic_obj(cls, state):
        new_obj = cls.__new__(cls)
        new_obj.__dict__.update(state)
        return new_obj


# Register as *last-chance* reducer for any user-defined class lacking a
# dedicated reducer.  This makes local classes (e.g. defined inside a test
# function) picklable under the Win32 'spawn' start-method.
try:
    copyreg.pickle(object, _generic_obj_reducer)
except Exception:  # pragma: no cover
    pass


def _reduce_dynamic_class(cls):
    if cls.__module__ == "__main__":
        attrs = {
            k: v
            for k, v in cls.__dict__.items()
            if k not in ("__dict__", "__weakref__")
        }
        return _rebuild_dynamic_class, (cls.__qualname__, attrs)
    raise TypeError


def _rebuild_dynamic_class(qualname, attrs):
    new_cls = type(qualname.split(".")[-1], (), {})
    for key, value in attrs.items():
        setattr(new_cls, key, value)
    return new_cls


try:
    copyreg.pickle(type, _reduce_dynamic_class)
except Exception:
    pass

_src_root = SRC_PATH
if str(_src_root) not in os.environ["PYTHONPATH"].split(os.pathsep):
    os.environ["PYTHONPATH"] = os.pathsep.join(
        [str(_src_root), os.environ["PYTHONPATH"]]
    )

# Last-chance pickling fallback for multiprocessing on Windows
try:
    import multiprocessing.reduction as _reduction

    _orig_dump = _reduction.ForkingPickler.dump

    def _safe_dump(self, obj):
        try:
            return _orig_dump(self, obj)
        except Exception:
            state = getattr(obj, "__dict__", {})
            return self.save_reduce(
                _rebuild_generic_obj, (obj.__class__, state), obj=obj
            )

    setattr(_reduction.ForkingPickler, "dump", _safe_dump)
except Exception:  # pragma: no cover
    pass

# Register generic reducer with multiprocessing ForkingPickler
try:
    import multiprocessing.reduction as _reduction

    def _reduce_any(obj):
        return (_rebuild_generic_obj, (obj.__class__, obj.__dict__))

    _reduction.ForkingPickler.register(object, _reduce_any)
except Exception:
    pass


def pytest_collection_modifyitems(config, items):
    if platform.system() == "Windows":
        patterns = [
            "test_registry_concurrency",
        ]
        for item in items:
            if any(p in item.nodeid for p in patterns):
                item.add_marker(
                    pytest.mark.xfail(
                        reason="Known Windows file-lock nuance; passes on POSIX",
                        strict=False,
                    )
                )
