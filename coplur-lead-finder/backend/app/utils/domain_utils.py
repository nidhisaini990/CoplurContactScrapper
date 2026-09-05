"""Helpers for normalizing and comparing domains/URLs."""
from urllib.parse import urlparse


def normalize_domain(url_or_domain: str | None) -> str:
    """Normalize a URL or domain into a bare lowercase domain.

    Examples
    --------
    ``https://www.example.com/`` -> ``example.com``
    ``example.com`` -> ``example.com``
    """
    if not url_or_domain:
        return ""
    value = url_or_domain.strip().lower()
    if "://" not in value:
        value = f"https://{value}"
    parsed = urlparse(value)
    host = parsed.netloc or parsed.path
    host = host.split(":")[0]
    if host.startswith("www."):
        host = host[len("www.") :]
    return host.rstrip("/")


def build_page_url(domain: str, path: str) -> str:
    """Build a full HTTPS URL for a domain + path combination."""
    domain = normalize_domain(domain)
    path = path if path.startswith("/") else f"/{path}"
    return f"https://{domain}{path}"
