"""Base extractor interface for document extraction."""

from abc import ABC, abstractmethod
from typing import Any
from PIL import Image

from app.schemas.documents import PassportData, G28Data


# Extraction prompts - shared across all providers
PASSPORT_EXTRACTION_PROMPT = """Analyze this passport information and extract the following data.
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


G28_EXTRACTION_PROMPT = """Analyze this G-28 form information and extract attorney/representative information.
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


# For OCR-based extraction, we need different prompts that work with text input
PASSPORT_OCR_PROMPT = """The following is OCR-extracted text from a passport document.
Parse this text and extract the following information.
Return ONLY a valid JSON object with these exact keys (use null for missing values):

{
  "last_name": "Family name/surname",
  "first_name": "Given name(s)",
  "middle_name": "Middle name(s) if present",
  "passport_number": "Passport number",
  "country_of_issue": "Full country name that issued the passport",
  "nationality": "Nationality",
  "date_of_birth": "YYYY-MM-DD format",
  "place_of_birth": "Place of birth",
  "sex": "M, F, or X",
  "date_of_issue": "YYYY-MM-DD format",
  "date_of_expiration": "YYYY-MM-DD format"
}

The text may include MRZ (machine readable zone) data with format like:
P<COUNTRYNAME<<GIVEN<NAMES
followed by passport number and dates.

For dates, convert to YYYY-MM-DD format. Handle various date formats like DD/MM/YYYY, MM-DD-YYYY, etc.
Return ONLY the JSON, no other text.

OCR TEXT:
"""


G28_OCR_PROMPT = """The following is OCR-extracted text from a G-28 immigration form.
Parse this text and extract the attorney/representative information.
Return ONLY a valid JSON object with these exact keys (use null for missing values):

{
  "attorney_family_name": "Attorney's last/family name",
  "attorney_given_name": "Attorney's first/given name",
  "attorney_middle_name": "Attorney's middle name if present",
  "street_address": "Street number and name",
  "apt_ste_flr": "Type: Apt, Ste, or Flr",
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

Return ONLY the JSON, no other text.

OCR TEXT:
"""


class BaseExtractor(ABC):
    """Base class for document extractors."""

    @abstractmethod
    async def extract_passport(
        self, images: list[Image.Image]
    ) -> PassportData:
        """Extract passport data from images."""
        pass

    @abstractmethod
    async def extract_g28(
        self, images: list[Image.Image]
    ) -> G28Data:
        """Extract G-28 form data from images."""
        pass

    @staticmethod
    def parse_json_response(response_text: str) -> dict:
        """Parse JSON from model response, handling markdown code blocks."""
        import json

        text = response_text.strip()

        # Handle markdown code blocks
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first line (```json or ```) and last line (```)
            text = "\n".join(lines[1:-1])

        # Try to find JSON object in the text
        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1

        if start_idx != -1 and end_idx > start_idx:
            text = text[start_idx:end_idx]

        return json.loads(text)
