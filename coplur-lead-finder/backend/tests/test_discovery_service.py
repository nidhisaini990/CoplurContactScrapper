from app.models.search import SearchRequest
from app.services.discovery_service import (
    _extract_domain_from_result,
    discover_leads,
    generate_search_queries,
)


def _make_request(**overrides):
    defaults = dict(
        target_segment="Engineering Colleges",
        industry="Education",
        location="India",
        keywords=["placement", "employability"],
        roles=["Training and Placement Officer"],
        limit=10,
        min_relevance_score=0,
    )
    defaults.update(overrides)
    return SearchRequest(**defaults)


def test_generate_search_queries_respects_query_count():
    request = _make_request()
    queries = generate_search_queries(request, query_count=3)
    assert len(queries) == 3
    assert all(isinstance(q, str) and q for q in queries)


def test_generate_search_queries_includes_segment_and_location():
    request = _make_request()
    queries = generate_search_queries(request)
    assert any("Engineering Colleges" in q for q in queries)
    assert any("India" in q for q in queries)


def test_extract_domain_from_result_prefers_organization_domain():
    result = {"organization": {"domain": "https://www.example.com/"}, "url": "https://other.com"}
    assert _extract_domain_from_result(result) == "example.com"


def test_extract_domain_from_result_falls_back_to_url():
    result = {"url": "https://sub.example.org/page"}
    assert _extract_domain_from_result(result) == "sub.example.org"


async def test_discover_leads_returns_sorted_results_within_limit(monkeypatch):
    monkeypatch.setenv("SEARCH_PROVIDER", "mock")
    monkeypatch.setenv("USE_AI", "false")
    request = _make_request(limit=3, min_relevance_score=0)
    leads = await discover_leads(request)
    assert len(leads) <= request.limit
    scores = [lead.relevance_score for lead in leads]
    assert scores == sorted(scores, reverse=True)


async def test_discover_leads_filters_by_min_relevance_score(monkeypatch):
    monkeypatch.setenv("SEARCH_PROVIDER", "mock")
    monkeypatch.setenv("USE_AI", "false")
    request = _make_request(min_relevance_score=100)
    leads = await discover_leads(request)
    assert leads == []
