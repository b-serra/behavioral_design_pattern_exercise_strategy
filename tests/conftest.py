import sys
from pathlib import Path

# Ensure project root is on sys.path so tests can import top-level packages like
# `domain`, `application`, and `presentation` when pytest changes the import context.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
