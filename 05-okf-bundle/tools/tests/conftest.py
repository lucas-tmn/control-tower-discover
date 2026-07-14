import sys
import re
import shutil
from pathlib import Path

import pytest

# Add tools/ to sys.path so tests can import document, build_index, build_viewer directly.
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def tmp_path(request):
    """Workspace-local replacement for pytest's tmp_path on sandboxed Windows.

    Pytest's built-in temp factory creates directories with permissions that the
    managed sandbox cannot reliably re-open. These tests only need an isolated
    scratch directory, so create one with normal workspace permissions instead.
    """
    root = Path(__file__).resolve().parents[2] / ".pytest_tmp"
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid)[:120]
    path = root / name
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
