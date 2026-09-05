from app.services.contact_extractor import extract_emails, extract_phones
from app.services.deduplication_service import deduplicate_leads
from app.services.qualification_service import rule_based_score
from app.utils.domain_utils import normalize_domain
from app.models.lead import Lead


def test_normalize_domain_strips_scheme_and_www():
    assert normalize_domain("https://www.example.com/") == "example.com"
    assert normalize_domain("example.com") == "example.com"
    assert normalize_domain(None) == ""


def test_extract_emails_filters_generic_addresses():
    text = "Contact us at placement@college.edu.in or noreply@college.edu.in"
    emails = extract_emails(text)
    assert emails == ["placement@college.edu.in"]


def test_extract_phones_conservative():
    text = "Call us at +91 98765 43210 or visit in 2024."
    phones = extract_phones(text)
    assert any("98765" in p for p in phones)


def test_rule_based_score_within_bounds():
    result = rule_based_score(
        keywords=["placement"],
        industry="Education",
        target_industry="Education",
        location="India",
        target_location="India",
        website_text="Our placement and training cell supports careers.",
        has_contact_info=True,
    )
    assert 0 <= result["relevance_score"] <= 100
    assert result["is_relevant"] is True


def test_deduplicate_leads_keeps_higher_score():
    lead_a = Lead(organization_name="Acme College", website="https://www.acme.edu", relevance_score=50)
    lead_b = Lead(organization_name="Acme College", website="https://acme.edu/", relevance_score=80)
    deduped = deduplicate_leads([lead_a, lead_b])
    assert len(deduped) == 1
    assert deduped[0].relevance_score == 80
