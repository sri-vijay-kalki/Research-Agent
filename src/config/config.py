import os
from dotenv import load_dotenv
from pathlib import Path

# Load the .env file dynamically from my_agent_project/env/.env relative to this file's location
config_dir = Path(__file__).resolve().parent
env_path = config_dir.parent.parent / "env" / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    def __init__(self):
        self.API_KEY = self._required("NVIDIA_API_KEY")
        self.BASE_URL = self._required("NVIDIA_BASE_URL")
        self.MODEL = self._required("NVIDIA_MODEL")
        self.TEMPERATURE = self._required("LLM_TEMPERATURE")
        self.MAX_TOKENS = self._required("LLM_MAX_TOKENS")
        self.TOP_P = self._required("LLM_TOP_P")

    def _required(self, var_name: str) -> str:
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"Missing required environment variable: {var_name}")
        return value

config = Config()

