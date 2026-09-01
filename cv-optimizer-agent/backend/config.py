"""
Configuration — all settings loaded from .env
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    LLM_MODEL: str = "gemini-1.5-flash"
    MAX_CV_LENGTH: int = 9000           # max characters sent to LLM
    LANGUAGE_TOOL_ENABLED: bool = True  # toggle grammar baseline on/off

    class Config:
        env_file = ".env"

settings = Settings()
