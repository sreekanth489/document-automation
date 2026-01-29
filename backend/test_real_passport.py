"""Test with real passport file."""
import asyncio
import httpx
from pathlib import Path


async def test_real_passport():
    passport_path = Path("/Users/sreekanthkeerthipati/Downloads/Anshi_Passport (1).pdf")

    if not passport_path.exists():
        print(f"File not found: {passport_path}")
        return

    print(f"Testing with: {passport_path.name}")
    print("-" * 50)

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Upload and extract
        print("Uploading and extracting data...")
        with open(passport_path, "rb") as f:
            files = {"passport": (passport_path.name, f, "application/pdf")}
            response = await client.post(
                "http://localhost:8000/api/upload",
                files=files
            )

        if response.status_code != 200:
            print(f"Upload failed: {response.status_code}")
            print(response.text)
            return

        data = response.json()
        print("\nExtracted Passport Data:")
        print("-" * 50)

        passport = data.get("passport", {})
        for key, value in passport.items():
            if value:
                print(f"  {key}: {value}")

        # Fill the form
        print("\n" + "-" * 50)
        print("Filling form...")

        fill_response = await client.post(
            "http://localhost:8000/api/fill-form",
            json={
                "session_id": data["session_id"],
                "passport": passport,
                "g28": None,
                "headless": False  # Show browser
            }
        )

        if fill_response.status_code == 200:
            result = fill_response.json()
            print(f"\nSuccess: {result['success']}")
            print(f"Message: {result['message']}")
            if result.get('screenshot_path'):
                print(f"Screenshot: {result['screenshot_path']}")
        else:
            print(f"Fill failed: {fill_response.status_code}")
            print(fill_response.text)


if __name__ == "__main__":
    asyncio.run(test_real_passport())
