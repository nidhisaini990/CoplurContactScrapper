import os

from app.models.search import SearchRequest
from app.providers.search_provider import (
    BingProvider,
    GoogleCustomSearchProvider,
    MockSearchProvider,
    SerperProvider,
    TavilyProvider,
    get_search_provider,
)


def test_get_search_provider_defaults_to_mock(monkeypatch):
    monkeypatch.delenv("SEARCH_PROVIDER", raising=False)
    assert isinstance(get_search_provider(), MockSearchProvider)


def test_get_search_provider_falls_back_for_unknown_value(monkeypatch):
    monkeypatch.setenv("SEARCH_PROVIDER", "not-a-real-provider")
    assert isinstance(get_search_provider(), MockSearchProvider)


def test_get_search_provider_maps_known_names(monkeypatch):
    cases = {
        "serper": SerperProvider,
        "tavily": TavilyProvider,
        "bing": BingProvider,
        "google": GoogleCustomSearchProvider,
    }
    for name, expected_cls in cases.items():
        monkeypatch.setenv("SEARCH_PROVIDER", name)
        assert isinstance(get_search_provider(), expected_cls)


async def test_mock_search_provider_returns_results():
    provider = MockSearchProvider()
    results = await provider.search("engineering colleges in India placement officer", limit=3)
    assert len(results) == 3
    for result in results:
        assert "title" in result
        assert "url" in result
        assert "organization" in result


async def test_placeholder_providers_return_empty_without_api_key(monkeypatch):
    for env_var in ("SERPER_API_KEY", "TAVILY_API_KEY", "BING_API_KEY", "GOOGLE_API_KEY", "GOOGLE_CX"):
        monkeypatch.delenv(env_var, raising=False)

    assert await SerperProvider().search("query") == []
    assert await TavilyProvider().search("query") == []
    assert await BingProvider().search("query") == []
    assert await GoogleCustomSearchProvider().search("query") == []
