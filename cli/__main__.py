"""
Entry point for running the CLI module with python -m cli
"""

from .cli import main
import sys

if __name__ == "__main__":
    sys.exit(main())
