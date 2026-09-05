"""API routes for lead search and CSV export."""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.search import ExportRequest, SearchRequest, SearchResponse
from app.services.csv_service import leads_to_csv
from app.services.deduplication_service import deduplicate_leads
from app.services.discovery_service import discover_leads

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.post("/search", response_model=SearchResponse)
async def search_leads(request: SearchRequest) -> SearchResponse:
    leads = await discover_leads(request)
    leads = deduplicate_leads(leads)
    leads.sort(key=lambda lead: lead.relevance_score, reverse=True)
    return SearchResponse(total=len(leads), leads=leads)


@router.post("/export")
async def export_leads(request: ExportRequest) -> StreamingResponse:
    csv_content = leads_to_csv(request.leads)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=coplur_leads.csv"},
    )
