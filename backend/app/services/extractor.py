"""Document extraction service with configurable providers.

This module provides the main interface for document extraction, supporting
multiple providers:
    - anthropic: Claude API with vision capabilities (original)
    - ollama_vision: Ollama with vision models (LLaVA, Qwen-VL)
    - ollama_ocr: OCR + Ollama text models (NuMarkdown, etc.)

Configure the provider via the EXTRACTION_PROVIDER environment variable.
"""

import io
from pathlib import Path
from PIL import Image
from pdf2image import convert_from_bytes

from app.schemas.documents import PassportData, G28Data
from app.services.extractors import get_extractor


def load_file_as_images(file_content: bytes, filename: str) -> list[Image.Image]:
    """Load a file (PDF or image) and return list of PIL Images."""
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        # Convert PDF pages to images
        images = convert_from_bytes(file_content, dpi=200)
        return images
    elif suffix in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
        # Load image directly
        image = Image.open(io.BytesIO(file_content))
        return [image]
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


async def extract_passport(file_content: bytes, filename: str) -> PassportData:
    """Extract data from passport document.

    Uses the configured extraction provider to process the document.
    """
    images = load_file_as_images(file_content, filename)
    extractor = get_extractor()
    return await extractor.extract_passport(images)


async def extract_g28(file_content: bytes, filename: str) -> G28Data:
    """Extract data from G-28 form.

    Uses the configured extraction provider to process the document.
    """
    images = load_file_as_images(file_content, filename)
    extractor = get_extractor()
    return await extractor.extract_g28(images)
