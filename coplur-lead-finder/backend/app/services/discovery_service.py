"""Orchestrates the end-to-end lead discovery workflow.

Ties together search query generation, the search provider, website
analysis, contact extraction and lead qualification, and produces a list of
:class:`Lead` objects. Any failure for an individual organization is caught
and skipped so partial results are always returned.
"""
import asyncio
import os
from typing import Any
from urllib.parse import urlparse

from app.models.lead import Lead
from app.models.search import SearchRequest
from app.providers.ai_provider import get_ai_provider
from app.providers.search_provider import get_search_provider
from app.services.qualification_service import qualify_lead
from app.services.website_analyzer import analyze_website
from app.utils.domain_utils import normalize_domain
from app.utils.text_cleaner import clean_text

DEFAULT_QUERY_COUNT = int(os.getenv("DEFAULT_QUERY_COUNT", "5"))


def generate_search_queries(request: SearchRequest, query_count: int = DEFAULT_QUERY_COUNT) -> list[str]:
    """Build a handful of targeted search queries from the request criteria."""
    segment = request.target_segment or "organizations"
    location = request.location or request.country or ""
    keyword_str = " ".join(request.keywords[:3])
    role_str = request.roles[0] if request.roles else ""

    candidates = [
        f"{segment} in {location} placement officer".strip(),
        f"site:.edu.in training placement officer {segment}".strip(),
        f"{segment} placement cell contact {location}".strip(),
        f"{segment} training and placement email {location}".strip(),
        f"head of placement {segment} {keyword_str}".strip(),
        f"{role_str} {segment} {location} {keyword_str}".strip(),
    ]
    # De-duplicate while preserving order, then trim to the configured count.
    seen: set[str] = set()
    queries: list[str] = []
    for query in candidates:
        cleaned = clean_text(query)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            queries.append(cleaned)
    return queries[:query_count]


def _extract_domain_from_result(result: dict[str, Any]) -> str:
    org = result.get("organization") or {}
    if org.get("domain"):
        return normalize_domain(org["domain"])
    url = result.get("url") or ""
    return normalize_domain(urlparse(url).netloc or url)


async def _build_lead(
    result: dict[str, Any],
    request: SearchRequest,
    ai_provider,
) -> Lead | None:
    org = result.get("organization") or {}
    domain = _extract_domain_from_result(result)
    if not domain:
        return None

    analysis = await analyze_website(domain)

    organization_data = {
        "description": result.get("snippet", ""),
        "website_text": analysis["text"],
        "industry": org.get("industry") or request.industry,
        "target_industry": request.industry,
        "location": ", ".join(filter(None, [org.get("city"), org.get("state"), org.get("country")])),
        "target_location": request.location,
        "keywords": request.keywords,
        "target_segment": request.target_segment,
        "has_contact_info": bool(analysis["emails"] or analysis["phones"]),
    }

    qualification = await qualify_lead(organization_data, ai_provider)
    if qualification["relevance_score"] < request.min_relevance_score:
        return None

    contact_name = None
    designation = None
    if org.get("sample_decision_maker") and request.roles:
        contact_name = org["sample_decision_maker"].get("name")
        designation = request.roles[0]

    return Lead(
        organization_name=org.get("name") or result.get("title") or domain,
        website=f"https://{domain}",
        industry=org.get("industry") or request.industry,
        organization_type=org.get("type"),
        city=org.get("city"),
        state=org.get("state"),
        country=org.get("country") or request.country,
        contact_name=contact_name,
        designation=designation,
        department=None,
        business_email=analysis["emails"][0] if analysis["emails"] else None,
        business_phone=analysis["phones"][0] if analysis["phones"] else None,
        linkedin_url=None,
        organization_linkedin=analysis.get("organization_linkedin"),
        source_url=analysis.get("source_url") or result.get("url"),
        relevance_score=qualification["relevance_score"],
        relevance_reason=qualification["reason"],
    )


async def discover_leads(request: SearchRequest) -> list[Lead]:
    """Run the full discovery pipeline and return qualified, deduplicated
    leads (deduplication itself happens in the router so it can be reused
    for both freshly-discovered and previously-exported leads).
    """
    search_provider = get_search_provider()
    ai_provider = get_ai_provider()

    queries = generate_search_queries(request)
    # Spread the requested limit across queries (with a small buffer to
    # account for duplicates/qualification filtering) so we don't
    # fetch/crawl/qualify many times more organizations than needed.
    PER_QUERY_BUFFER = 2
    per_query_limit = max(1, -(-request.limit // max(len(queries), 1)) + PER_QUERY_BUFFER)
    all_results: list[dict[str, Any]] = []
    for query in queries:
        try:
            results = await search_provider.search(query, limit=per_query_limit)
            all_results.extend(results)
        except Exception:
            continue  # A failing query should not abort the whole search.

    # De-duplicate raw results by domain before doing expensive work.
    seen_domains: set[str] = set()
    unique_results: list[dict[str, Any]] = []
    for result in all_results:
        domain = _extract_domain_from_result(result)
        if domain and domain not in seen_domains:
            seen_domains.add(domain)
            unique_results.append(result)

    tasks = [_build_lead(result, request, ai_provider) for result in unique_results]
    leads_or_none = await asyncio.gather(*tasks, return_exceptions=True)

    leads: list[Lead] = []
    for item in leads_or_none:
        if isinstance(item, Lead):
            leads.append(item)
        # Exceptions and ``None`` results are silently skipped so a single
        # failing organization never aborts the overall search.

    leads.sort(key=lambda lead: lead.relevance_score, reverse=True)
    return leads[: request.limit]
