"""
Configuration module for the knowledge mining agent.

Parses config.yaml and .env files to provide centralized configuration.
"""

import os
from pathlib import Path
from typing import Any, Dict
import yaml
from dotenv import load_dotenv


class Config:
    """Configuration manager."""

    def __init__(self):
        """Initialize configuration from files."""
        load_dotenv()

        self._config = {}

        # Load config.yaml
        config_path = Path(__file__).parent / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                self._config.update(yaml.safe_load(f) or {})

        # Override with environment variables
        for key, value in os.environ.items():
            self._config[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self._config.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Get configuration value with dict-like access."""
        return self._config[key]

    def __contains__(self, key: str) -> bool:
        """Check if key exists."""
        return key in self._config


# Global config instance
config = Config()