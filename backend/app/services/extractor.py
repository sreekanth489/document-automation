import base64
import json
import io
from pathlib import Path
from typing import Optional

import anthropic
from PIL import Image
from pdf2image import convert_from_bytes

from app.config import get_settings
from app.schemas.documents import PassportData, G28Data


PASSPORT_EXTRACTION_PROMPT = """Analyze this passport image and extract the following information.
Return ONLY a valid JSON object with these exact keys (use null for missing values):

{
  "last_name": "Family name/surname exactly as shown",
  "first_name": "Given name(s) exactly as shown",
  "middle_name": "Middle name(s) if present",
  "passport_number": "Passport number",
  "country_of_issue": "Full country name that issued the passport",
  "nationality": "Nationality as shown",
  "date_of_birth": "YYYY-MM-DD format",
  "place_of_birth": "Place of birth as shown",
  "sex": "M, F, or X",
  "date_of_issue": "YYYY-MM-DD format",
  "date_of_expiration": "YYYY-MM-DD format"
}

Extract from both the visual fields AND the MRZ (machine readable zone) at the bottom if present.
For dates, convert to YYYY-MM-DD format.
Return ONLY the JSON, no other text."""


G28_EXTRACTION_PROMPT = """Analyze this G-28 form image and extract attorney/representative information.
Return ONLY a valid JSON object with these exact keys (use null for missing values):

{
  "attorney_family_name": "Attorney's last/family name",
  "attorney_given_name": "Attorney's first/given name",
  "attorney_middle_name": "Attorney's middle name if present",
  "street_address": "Street number and name",
  "apt_ste_flr": "Type: Apt, Ste, or Flr if checked",
  "apt_ste_flr_number": "Unit number if present",
  "city": "City name",
  "state": "State as 2-letter code (e.g., CA, NY)",
  "zip_code": "ZIP code",
  "country": "Country name",
  "daytime_phone": "Daytime phone number",
  "mobile_phone": "Mobile phone number",
  "email": "Email address",
  "licensing_authority": "Licensing authority/jurisdiction",
  "bar_number": "Bar number or registration number",
  "law_firm_name": "Law firm or organization name"
}

Return ONLY the JSON, no other text."""


def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """Convert PIL Image to base64 string."""
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    return base64.standard_b64encode(buffer.getvalue()).decode("utf-8")


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


def extract_with_claude(
    images: list[Image.Image],
    prompt: str,
    api_key: str
) -> dict:
    """Send images to Claude API and extract structured data."""
    client = anthropic.Anthropic(api_key=api_key)

    # Build content with all images
    content = []
    for img in images:
        # Convert to RGB if necessary (for PNG with transparency)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        b64_data = image_to_base64(img, "JPEG")
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": b64_data
            }
        })

    content.append({"type": "text", "text": prompt})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": content}]
    )

    # Parse JSON from response
    response_text = response.content[0].text.strip()

    # Handle potential markdown code blocks
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    return json.loads(response_text)


async def extract_passport(file_content: bytes, filename: str) -> PassportData:
    """Extract data from passport document."""
    settings = get_settings()
    images = load_file_as_images(file_content, filename)
    data = extract_with_claude(images, PASSPORT_EXTRACTION_PROMPT, settings.anthropic_api_key)
    return PassportData(**data)


async def extract_g28(file_content: bytes, filename: str) -> G28Data:
    """Extract data from G-28 form."""
    settings = get_settings()
    images = load_file_as_images(file_content, filename)
    data = extract_with_claude(images, G28_EXTRACTION_PROMPT, settings.anthropic_api_key)
    return G28Data(**data)
