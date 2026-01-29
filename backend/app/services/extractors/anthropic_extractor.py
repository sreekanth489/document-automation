"""Anthropic Claude API extractor for document extraction."""

import base64
import io
from PIL import Image
import anthropic

from app.config import get_settings
from app.schemas.documents import PassportData, G28Data
from app.services.extractors.base import (
    BaseExtractor,
    PASSPORT_EXTRACTION_PROMPT,
    G28_EXTRACTION_PROMPT,
)


class AnthropicExtractor(BaseExtractor):
    """Document extractor using Anthropic Claude API with vision."""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.anthropic_api_key
        self.model = settings.anthropic_model

        if not self.api_key:
            raise ValueError(
                "Anthropic API key not configured. "
                "Set ANTHROPIC_API_KEY in your .env file."
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def _image_to_base64(self, image: Image.Image, format: str = "JPEG") -> str:
        """Convert PIL Image to base64 string."""
        # Convert to RGB if necessary (for PNG with transparency)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        buffer = io.BytesIO()
        image.save(buffer, format=format)
        return base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

    def _build_image_content(self, images: list[Image.Image]) -> list[dict]:
        """Build content array with images for Claude API."""
        content = []
        for img in images:
            b64_data = self._image_to_base64(img)
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": b64_data
                }
            })
        return content

    def _call_claude(self, images: list[Image.Image], prompt: str) -> dict:
        """Send images and prompt to Claude API and get structured response."""
        content = self._build_image_content(images)
        content.append({"type": "text", "text": prompt})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": content}]
        )

        response_text = response.content[0].text
        return self.parse_json_response(response_text)

    async def extract_passport(self, images: list[Image.Image]) -> PassportData:
        """Extract passport data from images using Claude vision."""
        data = self._call_claude(images, PASSPORT_EXTRACTION_PROMPT)
        return PassportData(**data)

    async def extract_g28(self, images: list[Image.Image]) -> G28Data:
        """Extract G-28 form data from images using Claude vision."""
        data = self._call_claude(images, G28_EXTRACTION_PROMPT)
        return G28Data(**data)
