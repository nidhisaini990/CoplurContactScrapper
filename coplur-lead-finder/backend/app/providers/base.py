"""Base provider interfaces used across the application.

Providers are intentionally small abstractions so that real implementations
(search engines, AI models) can be swapped in without touching the rest of
the codebase.
"""
from abc import ABC, abstractmethod
from typing import Any


class SearchProvider(ABC):
    """Abstract interface for a search provider."""

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Run a search query and return a list of results.

        Each result should be a dict with at least ``title``, ``url`` and
        ``snippet`` keys.
        """
        raise NotImplementedError


class BaseAIProvider(ABC):
    """Abstract interface for an AI qualification provider."""

    @abstractmethod
    async def qualify_lead(self, organization_data: dict[str, Any]) -> dict[str, Any]:
        """Qualify a lead and return a dict with ``is_relevant``,
        ``relevance_score`` and ``reason`` keys.
        """
        raise NotImplementedError
