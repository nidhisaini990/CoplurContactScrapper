"""Rule-based lead qualification, with an optional AI qualification path.

The rule-based scorer is always available as a fallback so the application
works fully without any AI provider configured.
"""
from typing import Any

from app.providers.base import BaseAIProvider

_ROLE_OR_PAGE_HINTS = (
    "placement",
    "training",
    "career",
    "recruit",
    "talent",
    "hr",
    "hiring",
)

_MAX_SCORE = 100


def rule_based_score(
    *,
    keywords: list[str],
    industry: str | None,
    target_industry: str | None,
    location: str | None,
    target_location: str | None,
    website_text: str,
    has_contact_info: bool,
) -> dict[str, Any]:
    """Compute a 0-100 relevance score using simple, explainable rules."""
    score = 0
    reasons: list[str] = []
    text = (website_text or "").lower()

    keyword_matches = [kw for kw in keywords if kw and kw.lower() in text]
    if keyword_matches:
        score += 25
        reasons.append(f"matches keywords: {', '.join(keyword_matches)}")

    if industry and target_industry and industry.lower() == target_industry.lower():
        score += 20
        reasons.append(f"industry matches '{target_industry}'")

    if any(hint in text for hint in _ROLE_OR_PAGE_HINTS):
        score += 20
        reasons.append("website references placement/training/careers content")

    if has_contact_info:
        score += 10
        reasons.append("public contact information available")

    if location and target_location and target_location.lower() in location.lower():
        score += 10
        reasons.append(f"location matches '{target_location}'")

    score = min(score, _MAX_SCORE)
    reason = (
        "; ".join(reasons).capitalize()
        if reasons
        else "No strong signals found matching the target criteria."
    )
    return {
        "is_relevant": score >= 60,
        "relevance_score": score,
        "reason": reason,
    }


async def qualify_lead(
    organization_data: dict[str, Any],
    ai_provider: BaseAIProvider | None = None,
) -> dict[str, Any]:
    """Qualify a lead using AI when available, otherwise fall back to the
    rule-based scorer. Never raises: AI failures fall back automatically.
    """
    if ai_provider is not None:
        try:
            result = await ai_provider.qualify_lead(organization_data)
            if result and result.get("relevance_score", 0) > 0:
                return result
        except Exception:
            pass  # Fall through to rule-based scoring.

    return rule_based_score(
        keywords=organization_data.get("keywords", []),
        industry=organization_data.get("industry"),
        target_industry=organization_data.get("target_industry"),
        location=organization_data.get("location"),
        target_location=organization_data.get("target_location"),
        website_text=organization_data.get("description", "")
        + " "
        + organization_data.get("website_text", ""),
        has_contact_info=organization_data.get("has_contact_info", False),
    )
