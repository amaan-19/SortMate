"""
Configuration management for SortMate.

This module provides configuration loading and management functionality
that can be used throughout the application.
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger('sortmate.config')

DEFAULT_CONFIG = {
    "sorting_methods": ["date"],  # Start with just date by default
    "ignore_labels": ["SPAM", "TRASH"],
    "custom_rules": [],
    "max_emails_per_batch": 100,
    "categorization_options": {
        "date": True,
        "sender": {"enabled": False, "type": "domain"},
        "keywords": {"enabled": False, "keywords": None}
    }
}

CONFIG_PATH = os.path.expanduser("~/.config/SortMate/config.json")

def load_config():
    """Load configuration from file or create default."""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged_config = {**DEFAULT_CONFIG, **config}
                logger.info(f"Loaded configuration from {CONFIG_PATH}")
                return merged_config
        else:
            # Create default config
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            logger.info(f"Created default configuration at {CONFIG_PATH}")
            return DEFAULT_CONFIG
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        logger.info("Using default configuration")
        return DEFAULT_CONFIG

def save_config(config):
    """Save configuration to file."""
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Configuration saved to {CONFIG_PATH}")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return False