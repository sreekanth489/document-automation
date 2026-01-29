"""Test script to verify form filling with sample data."""
import asyncio
import httpx

# Sample extracted data for testing
TEST_DATA = {
    "session_id": "test-session-001",
    "passport": {
        "last_name": "SMITH",
        "first_name": "JOHN",
        "middle_name": "WILLIAM",
        "passport_number": "AB1234567",
        "country_of_issue": "United States",
        "nationality": "American",
        "date_of_birth": "1985-03-15",
        "place_of_birth": "New York",
        "sex": "M",
        "date_of_issue": "2020-01-10",
        "date_of_expiration": "2030-01-09"
    },
    "g28": {
        "attorney_family_name": "JOHNSON",
        "attorney_given_name": "EMILY",
        "attorney_middle_name": "R",
        "street_address": "123 Legal Street",
        "city": "Los Angeles",
        "state": "CA",
        "zip_code": "90001",
        "country": "United States",
        "daytime_phone": "213-555-0100",
        "mobile_phone": "213-555-0101",
        "email": "emily.johnson@lawfirm.com",
        "licensing_authority": "State Bar of California",
        "bar_number": "123456",
        "law_firm_name": "Johnson & Associates"
    },
    "headless": False  # Set to False to see the browser
}


async def test_form_fill():
    """Test the form filling endpoint."""
    print("Testing form fill endpoint...")
    print("-" * 50)

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "http://localhost:8000/api/fill-form",
            json=TEST_DATA
        )

        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            if result.get('screenshot_path'):
                print(f"Screenshot: {result['screenshot_path']}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)


if __name__ == "__main__":
    asyncio.run(test_form_fill())
