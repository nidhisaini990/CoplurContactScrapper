"""Lightweight, safe extraction of business emails and phone numbers from
publicly available webpage text.
"""
import re

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# Conservative phone pattern: requires at least 9 digits total, allows
# common separators. Avoids matching arbitrary numeric noise.
PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?){2,4}\d{3,4}"
)

_GENERIC_EMAIL_PREFIXES = {"noreply", "no-reply", "donotreply"}


def extract_emails(text: str) -> list[str]:
    """Return unique, likely-valid business email addresses found in text."""
    found = EMAIL_PATTERN.findall(text or "")
    emails: list[str] = []
    seen = set()
    for email in found:
        lower = email.lower()
        prefix = lower.split("@", 1)[0]
        if prefix in _GENERIC_EMAIL_PREFIXES:
            continue
        if lower not in seen:
            seen.add(lower)
            emails.append(email)
    return emails


def extract_phones(text: str) -> list[str]:
    """Return unique candidate phone numbers found in text.

    The pattern is intentionally conservative to avoid false positives from
    dates, prices, or unrelated numeric strings.
    """
    candidates = PHONE_PATTERN.findall(text or "")
    phones: list[str] = []
    seen = set()
    for candidate in candidates:
        digits = re.sub(r"\D", "", candidate)
        if len(digits) < 9 or len(digits) > 15:
            continue
        cleaned = candidate.strip()
        if cleaned not in seen:
            seen.add(cleaned)
            phones.append(cleaned)
    return phones


def extract_contact_info(text: str) -> dict[str, list[str]]:
    """Extract both emails and phone numbers from a page's text content."""
    return {
        "emails": extract_emails(text),
        "phones": extract_phones(text),
    }
