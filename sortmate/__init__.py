"""
SortMate - Automated Gmail Organization Tool

This package provides functionality to automatically organize
Gmail messages by applying date-based labels.
"""

__version__ = '0.1.0'
__author__ = 'Amaan Khan'

# Import key functionality for easier access
from .authenticate import get_credentials
from .sort import sort_past_emails
from .watch import start_watch
from .config import load_config, save_config

# Define what gets imported with `from sortmate import *`
__all__ = [
    'get_credentials',
    'sort_past_emails',
    'start_watch',
    'load_config',
    'save_config',
]