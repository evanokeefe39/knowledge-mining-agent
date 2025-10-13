"""
Configuration module for the knowledge mining agent.

Parses config.yaml and expands environment variables using Pydantic for validation.
"""

import os
import re
from pathlib import Path
from typing import Any
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    verbose: bool = False
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7


class DatabaseConfig(BaseModel):
    default_schema: str = "dw"
    host: str
    user: str
    password: str
    name: str
    port: int


class VectorStoreConfig(BaseModel):
    table: str = "hormozi_transcripts"


class OpenAIConfig(BaseModel):
    api_key: str


class Config(BaseModel):
    agent: AgentConfig
    database: DatabaseConfig
    vector_store: VectorStoreConfig
    openai: OpenAIConfig


def _expand_variables(data: Any) -> Any:
    """Recursively expand ${VAR} variables in data."""
    if isinstance(data, dict):
        return {k: _expand_variables(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_expand_variables(item) for item in data]
    elif isinstance(data, str):
        return _expand_string(data)
    else:
        return data


def _expand_string(value: str) -> str:
    """Expand ${VAR} in string using environment variables."""
    def replacer(match):
        var_name = match.group(1)
        return os.environ.get(var_name, match.group(0))  # Leave unresolved if not found

    return re.sub(r'\$\{([^}]+)\}', replacer, value)


def load_config() -> Config:
    """Load and validate configuration from config.yaml."""
    load_dotenv()

    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"config.yaml not found at {config_path}")

    with open(config_path, 'r') as f:
        yaml_config = yaml.safe_load(f) or {}

    # Expand variables in yaml
    expanded_config = _expand_variables(yaml_config)

    return Config(**expanded_config)


# Global config instance
settings = load_config()