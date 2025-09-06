from __future__ import annotations

import sys
from pathlib import Path


def _ensure_project_root_on_path() -> None:
    # Add repository root to sys.path so that `import src...` works when running pytest
    repo_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(repo_root))


_ensure_project_root_on_path()

