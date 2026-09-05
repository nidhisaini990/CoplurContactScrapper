"""AI provider implementations used for lead qualification.

The AI integration is optional. When ``USE_AI`` is falsy (the default) the
application relies entirely on the rule-based qualification service instead
of calling any of these providers.
"""
import json
import os
from typing import Any

import httpx

from app.providers.base import BaseAIProvider


class MockAIProvider(BaseAIProvider):
    """Deterministic AI provider used for local development/testing.

    It performs a lightweight keyword-overlap heuristic so results stay
    stable without requiring any external API calls.
    """

    async def qualify_lead(self, organization_data: dict[str, Any]) -> dict[str, Any]:
        description = (organization_data.get("description") or "").lower()
        keywords = [k.lower() for k in organization_data.get("keywords", [])]
        target_segment = (organization_data.get("target_segment") or "").lower()

        matches = sum(1 for kw in keywords if kw and kw in description)
        score = 50
        if matches:
            score += min(matches * 12, 36)
        if target_segment and target_segment.split()[0] in description:
            score += 10
        score = min(score, 100)

        reason = (
            f"Organization profile matches {matches} target keyword(s) and "
            f"aligns with the '{organization_data.get('target_segment', 'target')}' segment."
            if matches
            else "Organization profile has limited overlap with the requested keywords."
        )
        return {
            "is_relevant": score >= 60,
            "relevance_score": score,
            "reason": reason,
        }


class OpenAIProvider(BaseAIProvider):
    """AI provider backed by the OpenAI Chat Completions API."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini") -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

    async def qualify_lead(self, organization_data: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            # AI is optional; caller should fall back to rule-based scoring.
            return {"is_relevant": False, "relevance_score": 0, "reason": "AI provider not configured."}

        prompt = (
            "You qualify potential B2B leads for Coplur, an assessment and "
            "interview-practice platform. Given the organization data below, "
            "return strict JSON with keys is_relevant (bool), "
            "relevance_score (0-100 int) and reason (short string).\n\n"
            f"Organization data: {json.dumps(organization_data)}"
        )
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": "Bearer " + self.api_key},
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0,
                    },
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception:
            # Never let AI failures break the search; fall back gracefully.
            return {"is_relevant": False, "relevance_score": 0, "reason": "AI qualification failed."}


def get_ai_provider() -> BaseAIProvider | None:
    """Returns the configured AI provider, or ``None`` if AI is disabled."""
    use_ai = os.getenv("USE_AI", "false").strip().lower() in {"1", "true", "yes"}
    if not use_ai:
        return None
    if os.getenv("OPENAI_API_KEY"):
        return OpenAIProvider()
    return MockAIProvider()
