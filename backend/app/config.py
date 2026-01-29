import os
from enum import Enum
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class ExtractionProvider(str, Enum):
    """Supported extraction providers."""
    ANTHROPIC = "anthropic"           # Claude API (vision)
    OLLAMA_VISION = "ollama_vision"   # Ollama with vision models (LLaVA, Qwen-VL)
    OLLAMA_OCR = "ollama_ocr"         # OCR + Ollama text models (NuMarkdown, etc.)


class Settings(BaseSettings):
    # Extraction provider configuration
    extraction_provider: ExtractionProvider = ExtractionProvider.ANTHROPIC

    # Anthropic settings
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # Ollama settings
    ollama_base_url: str = "http://localhost:11434"
    ollama_text_model: str = "numind/numarkdown-8b-thinking"  # For OCR + text extraction
    ollama_vision_model: str = "llava:13b"  # For vision-based extraction
    ollama_timeout: int = 120  # Timeout in seconds for Ollama requests

    # OCR settings (for OLLAMA_OCR provider)
    ocr_engine: str = "easyocr"  # Options: easyocr, tesseract
    ocr_languages: str = "en"  # Comma-separated language codes

    # Application settings
    form_url: str = "https://mendrika-alma.github.io/form-submission/"
    upload_dir: str = "uploads"
    screenshot_dir: str = "screenshots"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
