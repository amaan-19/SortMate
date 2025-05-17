"""
Development script for running SortMate.

This script provides an easy way to run SortMate during development
without needing to install the package.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sortmate.cli import main

if __name__ == "__main__":
    sys.exit(main())