"""Fetches a small, bounded set of likely-relevant pages for an organization
and extracts text content + public contact information.

Crawling is intentionally shallow: only a handful of well-known paths are
checked per domain, requests are time-boxed, and overall concurrency is
capped so the tool stays lightweight.
"""
import asyncio
import os
import re
from typing import Any

import httpx
from bs4 import BeautifulSoup

from app.services.contact_extractor import extract_contact_info
from app.utils.domain_utils import build_page_url
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

_LINKEDIN_RE = re.compile(r"https?://(?:www\.)?linkedin\.com/[\w\-/%.]+", re.IGNORECASE)

_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


async def _fetch_page(client: httpx.AsyncClient, url: str) -> str | None:
    try:
        async with _semaphore:
            response = await client.get(url, timeout=REQUEST_TIMEOUT, follow_redirects=True)
        if response.status_code >= 400:
            return None
        return response.text
    except (httpx.HTTPError, httpx.TimeoutException):
        return None


async def analyze_website(domain: str) -> dict[str, Any]:
    """Crawl up to ``MAX_PAGES_PER_DOMAIN`` likely pages on a domain and
    return aggregated text plus extracted public contact details.

    Never raises: any network/parsing failure for a page is skipped so a
    single bad website cannot break the overall search.
    """
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
