"""Ollama Vision LLM extractor for document extraction."""

import base64
import io
import httpx
from PIL import Image

from app.config import get_settings
from app.schemas.documents import PassportData, G28Data
from app.services.extractors.base import (
    BaseExtractor,
    PASSPORT_EXTRACTION_PROMPT,
    G28_EXTRACTION_PROMPT,
)


class OllamaVisionExtractor(BaseExtractor):
    """Document extractor using Ollama with vision-capable models (LLaVA, Qwen-VL, etc.)."""

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_vision_model
        self.timeout = settings.ollama_timeout

    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        # Convert to RGB if necessary
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        return base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

    async def _call_ollama(self, images: list[Image.Image], prompt: str) -> dict:
        """Send images and prompt to Ollama API and get structured response."""
        # Convert images to base64
        image_data = [self._image_to_base64(img) for img in images]

        # Ollama API expects images in the 'images' field for vision models
        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": image_data,
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
        """Extract passport data from images using Ollama vision model."""
        data = await self._call_ollama(images, PASSPORT_EXTRACTION_PROMPT)
        return PassportData(**data)

    async def extract_g28(self, images: list[Image.Image]) -> G28Data:
        """Extract G-28 form data from images using Ollama vision model."""
        data = await self._call_ollama(images, G28_EXTRACTION_PROMPT)
        return G28Data(**data)


async def check_ollama_vision_availability(base_url: str, model: str) -> bool:
    """Check if Ollama is running and the vision model is available."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Check if Ollama is running
            response = await client.get(f"{base_url}/api/tags")
            if response.status_code != 200:
                return False

            # Check if the model is available
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]

            # Check for exact match or prefix match (e.g., "llava" matches "llava:13b")
            model_base = model.split(":")[0]
            return any(
                m == model or m.startswith(f"{model_base}:")
                for m in model_names
            )
    except Exception:
        return False
