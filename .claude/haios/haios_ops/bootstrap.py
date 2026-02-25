# generated: 2026-02-25
"""
Bootstrap module for haios_ops MCP server.

Sets up dual sys.path so modules/ and lib/ are importable
from the server location inside .claude/haios/haios_ops/.

Pattern from .claude/haios/modules/cli.py:19-26.
"""
import sys
from pathlib import Path


def setup_paths() -> None:
    """Insert modules/ and lib/ dirs into sys.path.

    Anchored from this file's location:
      haios_ops/bootstrap.py
        -> haios_ops/ (package dir)
        -> haios/ (parent = .claude/haios/)
        -> modules/ (.claude/haios/modules/)
        -> lib/     (.claude/haios/lib/)

    Idempotent — only inserts if not already present.
    """
    haios_dir = Path(__file__).parent.parent  # .claude/haios/
    modules_dir = haios_dir / "modules"
    lib_dir = haios_dir / "lib"

    for p in (str(modules_dir), str(lib_dir)):
        if p not in sys.path:
            sys.path.insert(0, p)


# Run at import time so that `from . import bootstrap` in mcp_server.py
# is sufficient to prepare the path.
setup_paths()
