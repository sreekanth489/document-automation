import uuid
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import get_settings
from app.schemas.documents import ExtractedData, PassportData, G28Data
from app.services.extractor import extract_passport, extract_g28


router = APIRouter(prefix="/api", tags=["upload"])

# In-memory storage for extracted data (use Redis/DB in production)
extracted_data_store: dict[str, ExtractedData] = {}


@router.post("/upload", response_model=ExtractedData)
async def upload_documents(
    passport: Optional[UploadFile] = File(None),
    g28: Optional[UploadFile] = File(None)
):
    """
    Upload passport and/or G-28 documents for data extraction.

    Accepts PDF or image files (JPEG, PNG).
    Returns extracted data from the documents.
    """
    if not passport and not g28:
        raise HTTPException(
            status_code=400,
            detail="At least one document (passport or g28) must be provided"
        )

    session_id = str(uuid.uuid4())
    passport_data = None
    g28_data = None

    # Process passport
    if passport:
        if not passport.filename:
            raise HTTPException(status_code=400, detail="Passport file has no filename")

        allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png"}
        ext = Path(passport.filename).suffix.lower()
        if ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Passport file type not supported. Allowed: {allowed_extensions}"
            )

        content = await passport.read()
        passport_data = await extract_passport(content, passport.filename)

    # Process G-28
    if g28:
        if not g28.filename:
            raise HTTPException(status_code=400, detail="G-28 file has no filename")

        allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png"}
        ext = Path(g28.filename).suffix.lower()
        if ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"G-28 file type not supported. Allowed: {allowed_extensions}"
            )

        content = await g28.read()
        g28_data = await extract_g28(content, g28.filename)

    # Store extracted data
    result = ExtractedData(
        session_id=session_id,
        passport=passport_data,
        g28=g28_data
    )
    extracted_data_store[session_id] = result

    return result


@router.get("/extract/{session_id}", response_model=ExtractedData)
async def get_extracted_data(session_id: str):
    """Retrieve previously extracted data by session ID."""
    if session_id not in extracted_data_store:
        raise HTTPException(status_code=404, detail="Session not found")
    return extracted_data_store[session_id]
