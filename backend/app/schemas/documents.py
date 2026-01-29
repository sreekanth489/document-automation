from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class PassportData(BaseModel):
    """Extracted data from passport document."""
    last_name: Optional[str] = Field(None, description="Family name / surname")
    first_name: Optional[str] = Field(None, description="Given name(s)")
    middle_name: Optional[str] = Field(None, description="Middle name(s)")
    passport_number: Optional[str] = Field(None, description="Passport number")
    country_of_issue: Optional[str] = Field(None, description="Country that issued the passport")
    nationality: Optional[str] = Field(None, description="Nationality of holder")
    date_of_birth: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD)")
    place_of_birth: Optional[str] = Field(None, description="Place of birth")
    sex: Optional[str] = Field(None, description="Sex (M, F, or X)")
    date_of_issue: Optional[str] = Field(None, description="Passport issue date (YYYY-MM-DD)")
    date_of_expiration: Optional[str] = Field(None, description="Passport expiry date (YYYY-MM-DD)")


class G28Data(BaseModel):
    """Extracted data from G-28 form (Attorney information)."""
    # Part 1: Attorney/Representative Information
    attorney_family_name: Optional[str] = Field(None, description="Attorney's family name")
    attorney_given_name: Optional[str] = Field(None, description="Attorney's given name")
    attorney_middle_name: Optional[str] = Field(None, description="Attorney's middle name")
    street_address: Optional[str] = Field(None, description="Street number and name")
    apt_ste_flr: Optional[str] = Field(None, description="Apartment/Suite/Floor type")
    apt_ste_flr_number: Optional[str] = Field(None, description="Apartment/Suite/Floor number")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State (2-letter code)")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    country: Optional[str] = Field(None, description="Country")
    daytime_phone: Optional[str] = Field(None, description="Daytime telephone number")
    mobile_phone: Optional[str] = Field(None, description="Mobile telephone number")
    email: Optional[str] = Field(None, description="Email address")

    # Part 2: Eligibility Information
    licensing_authority: Optional[str] = Field(None, description="Licensing authority")
    bar_number: Optional[str] = Field(None, description="Bar number")
    law_firm_name: Optional[str] = Field(None, description="Law firm or organization name")


class ExtractedData(BaseModel):
    """Combined extracted data from all documents."""
    session_id: str
    passport: Optional[PassportData] = None
    g28: Optional[G28Data] = None


class FormFillRequest(BaseModel):
    """Request to fill the form with extracted data."""
    session_id: str
    passport: Optional[PassportData] = None
    g28: Optional[G28Data] = None
    headless: bool = Field(True, description="Run browser in headless mode")


class FormFillResponse(BaseModel):
    """Response after form filling."""
    success: bool
    message: str
    screenshot_path: Optional[str] = None
