"""Document extraction providers factory."""

from app.config import get_settings, ExtractionProvider
from app.services.extractors.base import BaseExtractor


def get_extractor() -> BaseExtractor:
    """Factory function to get the configured document extractor.

    Returns the appropriate extractor based on the EXTRACTION_PROVIDER setting.
    """
    settings = get_settings()
    provider = settings.extraction_provider

    if provider == ExtractionProvider.ANTHROPIC:
        from app.services.extractors.anthropic_extractor import AnthropicExtractor
        return AnthropicExtractor()

    elif provider == ExtractionProvider.OLLAMA_VISION:
        from app.services.extractors.ollama_vision_extractor import OllamaVisionExtractor
        return OllamaVisionExtractor()

    elif provider == ExtractionProvider.OLLAMA_OCR:
        from app.services.extractors.ollama_ocr_extractor import OllamaOCRExtractor
        return OllamaOCRExtractor()

    else:
        raise ValueError(f"Unknown extraction provider: {provider}")


async def check_provider_availability() -> dict:
    """Check the availability of the configured provider.

    Returns a dict with:
        - available: bool
        - provider: str
        - message: str
    """
    settings = get_settings()
    provider = settings.extraction_provider

    if provider == ExtractionProvider.ANTHROPIC:
        available = bool(settings.anthropic_api_key)
        return {
            "available": available,
            "provider": "anthropic",
            "message": "Anthropic API key configured" if available else "Missing ANTHROPIC_API_KEY"
        }

    elif provider == ExtractionProvider.OLLAMA_VISION:
        from app.services.extractors.ollama_vision_extractor import check_ollama_vision_availability
        available = await check_ollama_vision_availability(
            settings.ollama_base_url,
            settings.ollama_vision_model
        )
        return {
            "available": available,
            "provider": "ollama_vision",
            "message": f"Model {settings.ollama_vision_model} available" if available
                      else f"Ollama not running or model {settings.ollama_vision_model} not found"
        }

    elif provider == ExtractionProvider.OLLAMA_OCR:
        from app.services.extractors.ollama_ocr_extractor import check_ollama_text_availability
        available = await check_ollama_text_availability(
            settings.ollama_base_url,
            settings.ollama_text_model
        )
        return {
            "available": available,
            "provider": "ollama_ocr",
            "message": f"Model {settings.ollama_text_model} available" if available
                      else f"Ollama not running or model {settings.ollama_text_model} not found"
        }

    return {
        "available": False,
        "provider": str(provider),
        "message": "Unknown provider"
    }


__all__ = [
    "BaseExtractor",
    "get_extractor",
    "check_provider_availability",
    "ExtractionProvider",
]
