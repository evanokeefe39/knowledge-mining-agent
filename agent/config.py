import os
import yaml
from dotenv import load_dotenv

load_dotenv()

def get_config():
    """
    Return configuration settings by parsing config.yaml and .env.
    Secrets from .env are obfuscated.
    """
    # Load config.yaml
    with open('config.yaml', 'r') as f:
        yaml_config = yaml.safe_load(f)

    # Combine with env vars
    config = {
        "verbose": os.getenv("AGENT_VERBOSE", str(yaml_config.get('agent', {}).get('verbose', True))).lower() == "true",
        "model_name": os.getenv("MODEL_NAME", yaml_config.get('agent', {}).get('model_name', "gpt-3.5-turbo")),
        "temperature": float(os.getenv("TEMPERATURE", str(yaml_config.get('agent', {}).get('temperature', 0.7)))),
        "db_user": os.getenv("DB_USER", "***"),
        "db_password": os.getenv("DB_PASSWORD", "***"),
        "db_host": os.getenv("DB_HOST", "***"),
        "db_port": os.getenv("DB_PORT", "***"),
        "db_name": os.getenv("DB_NAME", "***"),
        "openai_api_key": os.getenv("OPENAI_API_KEY", "***"),
        "langextract_api_key": os.getenv("LANGEXTRACT_API_KEY", "***"),
        "youtube_api_key": os.getenv("YOUTUBE_API_KEY", "***"),
        "google_api_key": os.getenv("GOOGLE_API_KEY", "***"),
        "database_schema": yaml_config.get('database', {}).get('schema', 'dw'),
    }
    return config