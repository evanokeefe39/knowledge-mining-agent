"""
Configuration module for the knowledge mining agent.

Parses config.yaml and .env files to provide centralized configuration.
Supports dynamic variable expansion and secret obfuscation.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dotenv import load_dotenv


class Config:
    """Configuration manager with dynamic expansion and secret obfuscation."""

    # Keys that contain sensitive information
    SECRET_KEYS = {
        'password', 'secret', 'key', 'token', 'api_key',
        'db_password', 'openai_api_key'
    }

    def __init__(self):
        """Initialize configuration from files."""
        load_dotenv()

        self._config = {}

        # Load config.yaml with expansion
        config_path = Path(__file__).parent / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                yaml_config = yaml.safe_load(f) or {}
                # Expand variables in yaml
                yaml_config = self._expand_variables(yaml_config)
                self._config.update(yaml_config)

        # Override with environment variables (already expanded by dotenv)
        for key, value in os.environ.items():
            self._config[key] = value

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

    def get_obfuscated(self, key: str, default: Any = None) -> Any:
        """Get configuration value with secrets obfuscated for logging.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Obfuscated configuration value
        """
        value = self.get(key, default)
        if isinstance(value, str) and any(secret in key.lower() for secret in self.SECRET_KEYS):
            if len(value) > 8:
                return value[:4] + '*' * (len(value) - 8) + value[-4:]
            else:
                return '*' * len(value)
        return value

    def log_safe_config(self) -> Dict[str, Any]:
        """Return configuration dict with secrets obfuscated for logging."""
        return {k: self.get_obfuscated(k) for k in self._config.keys()}


# Global config instance
config = Config()