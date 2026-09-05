"""Pydantic models representing a lead / potential Coplur customer."""
from pydantic import BaseModel


class Lead(BaseModel):
    organization_name: str
    website: str | None = None
    industry: str | None = None
    organization_type: str | None = None

    city: str | None = None
    state: str | None = None
    country: str | None = None

    contact_name: str | None = None
    designation: str | None = None
    department: str | None = None

    business_email: str | None = None
    business_phone: str | None = None

    linkedin_url: str | None = None
    organization_linkedin: str | None = None

    source_url: str | None = None

    relevance_score: int = 0
    relevance_reason: str | None = None
