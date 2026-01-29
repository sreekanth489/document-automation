"""OCR + Ollama Text LLM extractor for document extraction."""

import httpx
import numpy as np
from PIL import Image
from typing import Optional

from app.config import get_settings
from app.schemas.documents import PassportData, G28Data
from app.services.extractors.base import (
    BaseExtractor,
    PASSPORT_OCR_PROMPT,
    G28_OCR_PROMPT,
)


# Lazy-loaded OCR engines
_easyocr_reader: Optional[object] = None


def get_easyocr_reader(languages: list[str]):
    """Get or create EasyOCR reader (singleton pattern for efficiency)."""
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr
        _easyocr_reader = easyocr.Reader(languages, gpu=True)
    return _easyocr_reader


def perform_ocr_easyocr(image: Image.Image, languages: list[str]) -> str:
    """Perform OCR using EasyOCR."""
    reader = get_easyocr_reader(languages)
    # Convert PIL Image to numpy array
    img_array = np.array(image)
    results = reader.readtext(img_array)
    # Extract text from results (each result is [bbox, text, confidence])
    texts = [result[1] for result in results]
    return "\n".join(texts)


def perform_ocr_tesseract(image: Image.Image, languages: str) -> str:
    """Perform OCR using Tesseract."""
    import pytesseract
    # Tesseract uses '+' to separate languages, e.g., 'eng+fra'
    lang_str = languages.replace(",", "+")
    return pytesseract.image_to_string(image, lang=lang_str)


def perform_ocr(image: Image.Image, engine: str, languages: str) -> str:
    """Perform OCR on image using specified engine."""
    lang_list = [lang.strip() for lang in languages.split(",")]

    if engine == "easyocr":
        return perform_ocr_easyocr(image, lang_list)
    elif engine == "tesseract":
        return perform_ocr_tesseract(image, languages)
    else:
        raise ValueError(f"Unknown OCR engine: {engine}")


class OllamaOCRExtractor(BaseExtractor):
    """Document extractor using OCR + Ollama text models (NuMarkdown, etc.)."""

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_text_model
        self.timeout = settings.ollama_timeout
        self.ocr_engine = settings.ocr_engine
        self.ocr_languages = settings.ocr_languages

    def _extract_text_from_images(self, images: list[Image.Image]) -> str:
        """Extract text from all images using OCR."""
        all_text = []
        for i, image in enumerate(images):
            # Convert to RGB if necessary
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            text = perform_ocr(image, self.ocr_engine, self.ocr_languages)
            if len(images) > 1:
                all_text.append(f"--- Page {i + 1} ---\n{text}")
            else:
                all_text.append(text)

        return "\n\n".join(all_text)

    async def _call_ollama_text(self, prompt: str) -> dict:
        """Send text prompt to Ollama API and get structured response."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for more deterministic output
            }
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            result = response.json()

        response_text = result.get("response", "")
        return self.parse_json_response(response_text)

    async def extract_passport(self, images: list[Image.Image]) -> PassportData:
        """Extract passport data from images using OCR + text LLM."""
        # Step 1: Extract text using OCR
        ocr_text = self._extract_text_from_images(images)

        # Step 2: Use LLM to structure the extracted text
        full_prompt = PASSPORT_OCR_PROMPT + ocr_text
        data = await self._call_ollama_text(full_prompt)

        return PassportData(**data)

    async def extract_g28(self, images: list[Image.Image]) -> G28Data:
        """Extract G-28 form data from images using OCR + text LLM."""
        # Step 1: Extract text using OCR
        ocr_text = self._extract_text_from_images(images)

        # Step 2: Use LLM to structure the extracted text
        full_prompt = G28_OCR_PROMPT + ocr_text
        data = await self._call_ollama_text(full_prompt)

        return G28Data(**data)


async def check_ollama_text_availability(base_url: str, model: str) -> bool:
    """Check if Ollama is running and the text model is available."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{base_url}/api/tags")
            if response.status_code != 200:
                return False

            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]

            model_base = model.split(":")[0]
            return any(
                m == model or m.startswith(f"{model_base}:")
                for m in model_names
            )
    except Exception:
        return False
