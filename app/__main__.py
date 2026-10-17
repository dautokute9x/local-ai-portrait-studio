"""Allow `python -m app`."""

import sys

from app.main import run

if __name__ == "__main__":
    sys.exit(run())
