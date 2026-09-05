"""Request/response models for the lead search API."""
from pydantic import BaseModel, Field

from app.models.lead import Lead


class SearchRequest(BaseModel):
    target_segment: str = Field(default="Engineering Colleges")
    industry: str | None = None
    location: str | None = None
    country: str | None = None
    keywords: list[str] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=list)
    limit: int = Field(default=20, ge=1, le=200)
    min_relevance_score: int = Field(default=60, ge=0, le=100)


class SearchResponse(BaseModel):
    total: int
    leads: list[Lead]


class ExportRequest(BaseModel):
    leads: list[Lead]
