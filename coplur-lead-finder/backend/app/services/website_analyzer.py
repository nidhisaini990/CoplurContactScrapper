"""Fetches a small, bounded set of likely-relevant pages for an organization
and extracts text content + public contact information.

Crawling is intentionally shallow: only a handful of well-known paths are
checked per domain, requests are time-boxed, and overall concurrency is
capped so the tool stays lightweight.
"""
import asyncio
import ipaddress
import os
import re
import socket
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.services.contact_extractor import extract_contact_info
from app.utils.domain_utils import build_page_url, normalize_domain
from app.utils.text_cleaner import clean_text

# Likely-relevant paths to check for both academic institutions and
# companies. Kept short and generic on purpose.
CANDIDATE_PATHS = [
    "/",
    "/contact",
    "/about",
    "/placement",
    "/training-and-placement",
    "/career",
    "/careers",
    "/team",
]

MAX_PAGES_PER_DOMAIN = int(os.getenv("MAX_PAGES_PER_DOMAIN", "5"))
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10"))
MAX_REDIRECTS = 3

_LINKEDIN_RE = re.compile(r"https?://(?:www\.)?linkedin\.com/[\w\-/%.]+", re.IGNORECASE)

_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


async def _resolve_public_ip(host: str) -> str | None:
    """Resolve ``host`` and return a single public, routable IP address to
    pin the connection to, or ``None`` if the host is missing, unresolvable,
    or resolves to any private/internal address.

    This guards against SSRF: without it, a malicious/misleading search
    result domain could point at internal infrastructure (loopback,
    link-local, private ranges, or cloud metadata endpoints like
    169.254.169.254) and trick the server into fetching it. Pinning the
    connection to the specific IP we validated (instead of re-resolving the
    hostname when the request is actually sent) also closes the
    TOCTOU/DNS-rebinding gap where a hostname could resolve to a different,
    private address between validation and the actual connection.
    """
    if not host:
        return None
    try:
        loop = asyncio.get_running_loop()
        infos = await loop.run_in_executor(None, socket.getaddrinfo, host, None)
    except (socket.gaierror, UnicodeError):
        return None

    if not infos:
        return None

    addresses: list[str] = []
    for info in infos:
        address = info[4][0]
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            return None
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            return None
        addresses.append(address)
    return addresses[0] if addresses else None


def _with_pinned_host(url: str, ip: str) -> str:
    """Rewrite ``url`` so its network location points directly at ``ip``,
    keeping the original scheme, port and path intact.
    """
    parsed = urlparse(url)
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    netloc_host = f"[{ip}]" if ":" in ip else ip
    return parsed._replace(netloc=f"{netloc_host}:{port}").geturl()


async def _fetch_page(client: httpx.AsyncClient, url: str) -> str | None:
    """Fetch ``url``, manually validating and pinning the host of every
    redirect hop so a same-domain redirect (or DNS rebinding) cannot be used
    to reach internal infrastructure.
    """
    current_url = url  # Logical URL (real hostname), used for redirect resolution.
    try:
        for _ in range(MAX_REDIRECTS + 1):
            host = urlparse(current_url).hostname or ""
            ip = await _resolve_public_ip(host)
            if not ip:
                return None
            pinned_url = _with_pinned_host(current_url, ip)
            async with _semaphore:
                response = await client.get(
                    pinned_url,
                    timeout=REQUEST_TIMEOUT,
                    follow_redirects=False,
                    headers={"Host": host},
                    extensions={"sni_hostname": host},
                )
            if response.is_redirect:
                next_url = response.headers.get("location")
                if not next_url:
                    return None
                current_url = str(httpx.URL(current_url).join(next_url))
                continue
            if response.status_code >= 400:
                return None
            return response.text
        return None
    except (httpx.HTTPError, httpx.TimeoutException):
        return None


async def analyze_website(domain: str) -> dict[str, Any]:
    """Crawl up to ``MAX_PAGES_PER_DOMAIN`` likely pages on a domain and
    return aggregated text plus extracted public contact details.

    Never raises: any network/parsing failure for a page is skipped so a
    single bad website cannot break the overall search.
    """
    domain = normalize_domain(domain)
    if not domain or not await _resolve_public_ip(domain):
        return {
            "text": "",
            "emails": [],
            "phones": [],
            "organization_linkedin": None,
            "source_url": None,
        }

    paths = CANDIDATE_PATHS[:MAX_PAGES_PER_DOMAIN]
    aggregated_text = ""
    linkedin_urls: set[str] = set()
    fetched_urls: list[str] = []

    headers = {"User-Agent": "CoplurLeadFinder/1.0 (+https://coplur.example)"}
    async with httpx.AsyncClient(headers=headers) as client:
        tasks = [
            _fetch_page(client, build_page_url(domain, path)) for path in paths
        ]
        pages = await asyncio.gather(*tasks, return_exceptions=False)

    for path, html in zip(paths, pages):
        if not html:
            continue
        fetched_urls.append(build_page_url(domain, path))
        try:
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator=" ")
        except Exception:
            continue
        aggregated_text += f" {clean_text(text)}"
        for match in _LINKEDIN_RE.findall(html):
            if "/company/" in match.lower():
                linkedin_urls.add(match)

    contact_info = extract_contact_info(aggregated_text)
    organization_linkedin = next(
        (url for url in linkedin_urls if "/company/" in url.lower()), None
    )

    return {
        "text": aggregated_text.strip(),
        "emails": contact_info["emails"],
        "phones": contact_info["phones"],
        "organization_linkedin": organization_linkedin,
        "source_url": fetched_urls[0] if fetched_urls else None,
    }
