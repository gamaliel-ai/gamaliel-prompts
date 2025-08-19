"""
Gamaliel Prompts CLI Tool

A simplified reference implementation for testing and validating changes to prompts
in the gamaliel-prompts submodule.
"""

__version__ = "0.1.0"
__author__ = "Gamaliel Team"

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, continue without it
    pass

# Don't import main here to avoid circular imports
# from .cli import main

# __all__ = ["main"]
