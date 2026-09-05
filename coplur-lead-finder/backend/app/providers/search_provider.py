"""Search provider implementations.

``get_search_provider`` returns the provider configured via the
``SEARCH_PROVIDER`` environment variable. Defaults to the mock provider so
the application works fully offline without any API keys.
"""
import os
import random
from typing import Any

import httpx

from app.providers.base import SearchProvider

# Realistic sample organizations used by the mock provider so the app can be
# exercised end-to-end without any external API keys.
_MOCK_ORGANIZATIONS: list[dict[str, Any]] = [
    {
        "name": "Vellore Institute of Engineering",
        "domain": "vie.ac.in",
        "type": "Engineering College",
        "industry": "Education",
        "city": "Vellore",
        "state": "Tamil Nadu",
        "country": "India",
        "description": (
            "Autonomous engineering college with an active training and "
            "placement cell focused on employability and coding assessments."
        ),
        "sample_decision_maker": {"name": "Anita Sharma"},
    },
    {
        "name": "Deccan University of Technology",
        "domain": "deccanuniv.edu.in",
        "type": "University",
        "industry": "Education",
        "city": "Hyderabad",
        "state": "Telangana",
        "country": "India",
        "description": (
            "State university offering technical programs, with a corporate "
            "relations office driving campus hiring and placement drives."
        ),
        "sample_decision_maker": {"name": "Ravi Kumar"},
    },
    {
        "name": "Nexora Softworks Pvt Ltd",
        "domain": "nexorasoft.com",
        "type": "Company",
        "industry": "Information Technology",
        "city": "Bengaluru",
        "state": "Karnataka",
        "country": "India",
        "description": (
            "IT services company running large scale campus hiring and "
            "technical interview evaluation programs for engineering talent."
        ),
        "sample_decision_maker": {"name": "Priya Nair"},
    },
    {
        "name": "Bright Future Skill Academy",
        "domain": "brightfutureskills.in",
        "type": "Skill Development Organization",
        "industry": "Education",
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "description": (
            "Skill development and training institute preparing students for "
            "industry readiness through practice assessments and mock "
            "interviews."
        ),
        "sample_decision_maker": {"name": "Suresh Iyer"},
    },
    {
        "name": "Coastal Institute of Technology",
        "domain": "coastaltech.ac.in",
        "type": "Technical Institute",
        "industry": "Education",
        "city": "Kochi",
        "state": "Kerala",
        "country": "India",
        "description": (
            "Technical institute with a dedicated placement director and "
            "career services team supporting employability initiatives."
        ),
        "sample_decision_maker": {"name": "Meera Pillai"},
    },
    {
        "name": "Vertex Talent Solutions",
        "domain": "vertextalent.com",
        "type": "Company",
        "industry": "Recruitment",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "country": "India",
        "description": (
            "Recruitment automation company that evaluates candidate skill "
            "assessments for enterprise hiring managers."
        ),
        "sample_decision_maker": {"name": "Arjun Menon"},
    },
]


class MockSearchProvider(SearchProvider):
    """Returns deterministic, realistic sample results without any network
    access so the application can run end-to-end with ``SEARCH_PROVIDER=mock``.
    """

    async def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        organizations = list(_MOCK_ORGANIZATIONS)
        random.Random(query).shuffle(organizations)
        for org in organizations[:limit]:
            results.append(
                {
                    "title": org["name"],
                    "url": f"https://{org['domain']}/placement",
                    "snippet": org["description"],
                    "organization": org,
                }
            )
        return results


class SerperProvider(SearchProvider):
    """Placeholder implementation for https://serper.dev search API."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("SERPER_API_KEY")

    async def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        if not self.api_key:
            return []
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": self.api_key, "Content-Type": "application/json"},
                json={"q": query, "num": limit},
            )
            response.raise_for_status()
            data = response.json()
        results = []
        for item in data.get("organic", [])[:limit]:
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                }
            )
        return results


class TavilyProvider(SearchProvider):
    """Placeholder implementation for the Tavily search API."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")

    async def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        if not self.api_key:
            return []
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={"api_key": self.api_key, "query": query, "max_results": limit},
            )
            response.raise_for_status()
            data = response.json()
        results = []
        for item in data.get("results", [])[:limit]:
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", ""),
                }
            )
        return results


class BingProvider(SearchProvider):
    """Placeholder implementation for the Bing Web Search API."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("BING_API_KEY")

    async def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        if not self.api_key:
            return []
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://api.bing.microsoft.com/v7.0/search",
                headers={"Ocp-Apim-Subscription-Key": self.api_key},
                params={"q": query, "count": limit},
            )
            response.raise_for_status()
            data = response.json()
        results = []
        for item in data.get("webPages", {}).get("value", [])[:limit]:
            results.append(
                {
                    "title": item.get("name", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("snippet", ""),
                }
            )
        return results


class GoogleCustomSearchProvider(SearchProvider):
    """Placeholder implementation for Google Programmable Search Engine."""

    def __init__(self, api_key: str | None = None, cx: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.cx = cx or os.getenv("GOOGLE_CX")

    async def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        if not self.api_key or not self.cx:
            return []
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": self.api_key,
                    "cx": self.cx,
                    "q": query,
                    "num": min(limit, 10),
                },
            )
            response.raise_for_status()
            data = response.json()
        results = []
        for item in data.get("items", [])[:limit]:
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                }
            )
        return results


def get_search_provider() -> SearchProvider:
    """Factory that returns the configured search provider.

    Falls back to :class:`MockSearchProvider` for any unknown/missing value,
    so the application always runs without external API keys.
    """
    provider_name = os.getenv("SEARCH_PROVIDER", "mock").strip().lower()
    providers = {
        "mock": MockSearchProvider,
        "serper": SerperProvider,
        "tavily": TavilyProvider,
        "bing": BingProvider,
        "google": GoogleCustomSearchProvider,
    }
    provider_cls = providers.get(provider_name, MockSearchProvider)
    return provider_cls()
