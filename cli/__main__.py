"""
Entry point for running the CLI module with python -m cli
"""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
