import os
import sys
from pathlib import Path

# Run Qt without a visible window (works on Windows, Linux and CI).
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Make `import app` work when pytest is run from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
