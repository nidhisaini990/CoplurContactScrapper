"""Deduplicates leads by normalized website domain and organization name."""
from app.models.lead import Lead
from app.utils.domain_utils import normalize_domain


def _completeness_score(lead: Lead) -> int:
    """Count how many optional contact-related fields are populated."""
    fields = [
        lead.contact_name,
        lead.designation,
        lead.department,
        lead.business_email,
        lead.business_phone,
        lead.linkedin_url,
        lead.organization_linkedin,
    ]
    return sum(1 for f in fields if f)


def _is_better(candidate: Lead, existing: Lead) -> bool:
    if candidate.relevance_score != existing.relevance_score:
        return candidate.relevance_score > existing.relevance_score
    return _completeness_score(candidate) > _completeness_score(existing)


def deduplicate_leads(leads: list[Lead]) -> list[Lead]:
    """Remove duplicate leads, keyed by normalized domain or org name.

    When duplicates are found, keeps the lead with the higher relevance
    score, breaking ties by contact-information completeness.
    """
    best_by_key: dict[str, Lead] = {}
    order: list[str] = []

    for lead in leads:
        domain = normalize_domain(lead.website)
        key = domain or f"name:{lead.organization_name.strip().lower()}"

        if key not in best_by_key:
            best_by_key[key] = lead
            order.append(key)
        elif _is_better(lead, best_by_key[key]):
            best_by_key[key] = lead

    return [best_by_key[key] for key in order]
