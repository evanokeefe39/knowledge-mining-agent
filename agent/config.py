import os
from dotenv import load_dotenv

load_dotenv()

def get_config():
    """
    Return configuration settings for the agent.
    """
    config = {
        "verbose": os.getenv("AGENT_VERBOSE", "true").lower() == "true",
        "model_name": os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
        "temperature": float(os.getenv("TEMPERATURE", "0.7")),
        # Add more config options as needed
    }
    return config