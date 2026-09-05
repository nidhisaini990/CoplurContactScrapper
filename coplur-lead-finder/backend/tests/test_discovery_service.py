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


async def test_discover_leads_require_contact_info_filters_out_leads_without_contact(monkeypatch):
    import app.services.discovery_service as discovery_service

    monkeypatch.setenv("SEARCH_PROVIDER", "mock")
    monkeypatch.setenv("USE_AI", "false")

    async def fake_analyze_website(domain):
        # Only "give" contact info to one specific domain so we can verify
        # the rest are filtered out when `require_contact_info` is set.
        if domain == "iitd.ac.in":
            return {
                "text": "",
                "emails": ["placements@iitd.ac.in"],
                "phones": [],
                "organization_linkedin": None,
                "source_url": None,
            }
        return {
            "text": "",
            "emails": [],
            "phones": [],
            "organization_linkedin": None,
            "source_url": None,
        }

    monkeypatch.setattr(discovery_service, "analyze_website", fake_analyze_website)

    request = _make_request(limit=50, min_relevance_score=0, require_contact_info=True)
    leads = await discovery_service.discover_leads(request)

    assert len(leads) > 0
    assert all(lead.business_email or lead.business_phone for lead in leads)
