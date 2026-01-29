"""Test script for extraction providers."""

import asyncio
import os
from PIL import Image, ImageDraw, ImageFont

# Set provider before importing app modules
# Options: anthropic, ollama_vision, ollama_ocr


def create_test_passport_image() -> Image.Image:
    """Create a simple test image that looks like a passport."""
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)

    # Add passport-like text
    text_lines = [
        "PASSPORT",
        "",
        "Surname: SMITH",
        "Given Names: JOHN WILLIAM",
        "Nationality: UNITED STATES",
        "Date of Birth: 15 MAR 1985",
        "Sex: M",
        "Place of Birth: NEW YORK",
        "Date of Issue: 01 JAN 2020",
        "Date of Expiry: 01 JAN 2030",
        "Passport No: AB1234567",
        "",
        "P<USASMITH<<JOHN<WILLIAM<<<<<<<<<<<<<<<<<<<<<",
        "AB12345671USA8503151M3001019<<<<<<<<<<<<<<00",
    ]

    y_position = 20
    for line in text_lines:
        draw.text((20, y_position), line, fill='black')
        y_position += 25

    return img


async def test_anthropic_provider():
    """Test Anthropic provider."""
    print("\n=== Testing Anthropic Provider ===")
    os.environ['EXTRACTION_PROVIDER'] = 'anthropic'

    # Clear cached settings
    from app.config import get_settings
    get_settings.cache_clear()

    from app.services.extractors import get_extractor, check_provider_availability

    status = await check_provider_availability()
    print(f"Provider status: {status}")

    if not status['available']:
        print("Anthropic not available, skipping test")
        return

    extractor = get_extractor()
    print(f"Extractor type: {type(extractor).__name__}")

    # Test extraction
    img = create_test_passport_image()
    try:
        result = await extractor.extract_passport([img])
        print(f"Extraction result: {result}")
    except Exception as e:
        print(f"Extraction error: {e}")


async def test_ollama_vision_provider():
    """Test Ollama Vision provider."""
    print("\n=== Testing Ollama Vision Provider ===")
    os.environ['EXTRACTION_PROVIDER'] = 'ollama_vision'

    from app.config import get_settings
    get_settings.cache_clear()

    from app.services.extractors import get_extractor, check_provider_availability

    status = await check_provider_availability()
    print(f"Provider status: {status}")

    if not status['available']:
        print("Ollama Vision not available, skipping test")
        return

    extractor = get_extractor()
    print(f"Extractor type: {type(extractor).__name__}")

    img = create_test_passport_image()
    try:
        result = await extractor.extract_passport([img])
        print(f"Extraction result: {result}")
    except Exception as e:
        print(f"Extraction error: {e}")


async def test_ollama_ocr_provider():
    """Test Ollama OCR provider."""
    print("\n=== Testing Ollama OCR Provider ===")
    os.environ['EXTRACTION_PROVIDER'] = 'ollama_ocr'

    from app.config import get_settings
    get_settings.cache_clear()

    from app.services.extractors import get_extractor, check_provider_availability

    status = await check_provider_availability()
    print(f"Provider status: {status}")

    if not status['available']:
        print("Ollama OCR not available, skipping extraction test")
        # But we can still test OCR
        print("\nTesting OCR only...")
        from app.services.extractors.ollama_ocr_extractor import perform_ocr
        img = create_test_passport_image()
        ocr_text = perform_ocr(img, 'easyocr', 'en')
        print(f"OCR extracted text:\n{ocr_text}")
        return

    extractor = get_extractor()
    print(f"Extractor type: {type(extractor).__name__}")

    img = create_test_passport_image()
    try:
        result = await extractor.extract_passport([img])
        print(f"Extraction result: {result}")
    except Exception as e:
        print(f"Extraction error: {e}")


async def test_ocr_only():
    """Test OCR functionality without LLM."""
    print("\n=== Testing OCR Only ===")
    from app.services.extractors.ollama_ocr_extractor import perform_ocr

    img = create_test_passport_image()

    print("Testing EasyOCR...")
    try:
        ocr_text = perform_ocr(img, 'easyocr', 'en')
        print(f"EasyOCR extracted text:\n{ocr_text}")
    except Exception as e:
        print(f"EasyOCR error: {e}")


async def main():
    """Run all provider tests."""
    print("=" * 60)
    print("Document Extraction Provider Tests")
    print("=" * 60)

    # Test OCR first (no external dependencies)
    await test_ocr_only()

    # Test each provider
    await test_anthropic_provider()
    await test_ollama_vision_provider()
    await test_ollama_ocr_provider()

    print("\n" + "=" * 60)
    print("Tests complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
