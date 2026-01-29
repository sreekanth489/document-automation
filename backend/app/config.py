import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    form_url: str = "https://mendrika-alma.github.io/form-submission/"
    upload_dir: str = "uploads"
    screenshot_dir: str = "screenshots"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
