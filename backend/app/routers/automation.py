from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.schemas.documents import FormFillRequest, FormFillResponse
from app.services.form_filler import fill_form


router = APIRouter(prefix="/api", tags=["automation"])


@router.post("/fill-form", response_model=FormFillResponse)
async def fill_form_endpoint(request: FormFillRequest):
    """
    Fill the target form with extracted data using browser automation.

    Takes passport and/or G-28 data and uses Playwright to:
    - Navigate to the form URL
    - Fill in the fields with the provided data
    - Take a screenshot of the filled form

    Does NOT submit the form.
    """
    result = await fill_form(
        passport=request.passport,
        g28=request.g28,
        session_id=request.session_id,
        headless=request.headless
    )

    if not result.success:
        raise HTTPException(status_code=500, detail=result.message)

    return result


@router.get("/screenshot/{filename}")
async def get_screenshot(filename: str):
    """Retrieve a form screenshot by filename."""
    screenshot_path = Path("screenshots") / filename

    if not screenshot_path.exists():
        raise HTTPException(status_code=404, detail="Screenshot not found")

    return FileResponse(
        path=screenshot_path,
        media_type="image/png",
        filename=filename
    )
