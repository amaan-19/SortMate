import os
import json
import logging
from pathlib import Path

logger = logging.getLogger('sortmate')

DEFAULT_CONFIG = {
    "sorting_methods": ["date", "sender"],
    "ignore_labels": ["SPAM", "TRASH"],
    "custom_rules": [],
    "max_emails_per_batch": 100
}

CONFIG_PATH = os.path.expanduser("~/.config/SortMate/config.json")

def load_config():
    """Load configuration from file or create default."""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {CONFIG_PATH}")
                return config
        else:
            # Create default config
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            logger.info(f"Created default configuration at {CONFIG_PATH}")
            return DEFAULT_CONFIG
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return DEFAULT_CONFIG