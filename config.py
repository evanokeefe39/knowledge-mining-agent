"""
Configuration module for the knowledge mining agent.

Parses config.yaml and expands environment variables.
"""

import os
import re
from pathlib import Path
from typing import Any
import yaml
from dotenv import load_dotenv


class Config:
    """Simple configuration manager that parses YAML and expands env vars."""

    def __init__(self):
        """Initialize configuration from config.yaml."""
        load_dotenv()

        self._config = {}

        # Load config.yaml with expansion
        config_path = Path(__file__).parent / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                yaml_config = yaml.safe_load(f) or {}
                # Expand variables in yaml
                self._config = self._expand_variables(yaml_config)

    def _expand_variables(self, data: Any) -> Any:
        """Recursively expand ${VAR} variables in data."""
        if isinstance(data, dict):
            return {k: self._expand_variables(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._expand_variables(item) for item in data]
        elif isinstance(data, str):
            return self._expand_string(data)
        else:
            return data

    def _expand_string(self, value: str) -> str:
        """Expand ${VAR} in string using environment variables."""
        def replacer(match):
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))  # Leave unresolved if not found

        return re.sub(r'\$\{([^}]+)\}', replacer, value)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Get configuration value with dict-like access."""
        return self._config[key]

    def __contains__(self, key: str) -> bool:
        """Check if key exists."""
        return key in self._config


# Global config instance
config = Config()