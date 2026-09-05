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
        "sample_email": "placements@vie.ac.in",
        "sample_phone": "+91-11-20000000",
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
        "sample_email": "placements@deccanuniv.edu.in",
        "sample_phone": "+91-22-20000137",
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
        "sample_email": "placements@nexorasoft.com",
        "sample_phone": "+91-33-20000274",
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
        "sample_email": "placements@brightfutureskills.in",
        "sample_phone": "+91-44-20000411",
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
        "sample_email": "placements@coastaltech.ac.in",
        "sample_phone": "+91-40-20000548",
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
        "sample_email": "placements@vertextalent.com",
        "sample_phone": "+91-20-20000685",
    },
    {
        "name": "Indian Institute of Technology Delhi",
        "domain": "iitd.ac.in",
        "type": "Engineering College",
        "industry": "Education",
        "city": "New Delhi",
        "state": "Delhi",
        "country": "India",
        "description": (
            "Premier engineering institute with a training and placement "
            "office coordinating recruitment and internship drives."
        ),
        "sample_decision_maker": {"name": "Rajesh Verma"},
        "sample_email": "placements@iitd.ac.in",
        "sample_phone": "+91-80-20000822",
    },
    {
        "name": "National Institute of Technology Warangal",
        "domain": "nitw.ac.in",
        "type": "Engineering College",
        "industry": "Education",
        "city": "Warangal",
        "state": "Telangana",
        "country": "India",
        "description": (
            "Autonomous institute of national importance with a dedicated "
            "training and placement cell for employability initiatives."
        ),
        "sample_decision_maker": {"name": "Kavitha Reddy"},
        "sample_email": "placements@nitw.ac.in",
        "sample_phone": "+91-79-20000959",
    },
    {
        "name": "Anna University",
        "domain": "annauniv.edu",
        "type": "University",
        "industry": "Education",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "country": "India",
        "description": (
            "State technical university running centralized placement and "
            "career services for affiliated engineering colleges."
        ),
        "sample_decision_maker": {"name": "Karthik Subramaniam"},
        "sample_email": "placements@annauniv.edu",
        "sample_phone": "+91-141-20001096",
    },
    {
        "name": "Pune Institute of Computer Technology",
        "domain": "pict.edu",
        "type": "Engineering College",
        "industry": "Education",
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "description": (
            "Autonomous engineering college with an active training and "
            "placement cell focused on coding assessments and hiring drives."
        ),
        "sample_decision_maker": {"name": "Sneha Kulkarni"},
        "sample_email": "placements@pict.edu",
        "sample_phone": "+91-281-20001233",
    },
    {
        "name": "Jadavpur University",
        "domain": "jadavpuruniversity.in",
        "type": "University",
        "industry": "Education",
        "city": "Kolkata",
        "state": "West Bengal",
        "country": "India",
        "description": (
            "State university with an established career services office "
            "supporting campus placements and industry tie-ups."
        ),
        "sample_decision_maker": {"name": "Debjani Sen"},
        "sample_email": "placements@jadavpuruniversity.in",
        "sample_phone": "+91-422-20001370",
    },
    {
        "name": "PSG College of Technology",
        "domain": "psgtech.edu",
        "type": "Engineering College",
        "industry": "Education",
        "city": "Coimbatore",
        "state": "Tamil Nadu",
        "country": "India",
        "description": (
            "Autonomous engineering college with a training and placement "
            "cell driving employability and industry-readiness programs."
        ),
        "sample_decision_maker": {"name": "Lakshmi Narayanan"},
        "sample_email": "placements@psgtech.edu",
        "sample_phone": "+91-471-20001507",
    },
    {
        "name": "Malaviya National Institute of Technology Jaipur",
        "domain": "mnit.ac.in",
        "type": "Engineering College",
        "industry": "Education",
        "city": "Jaipur",
        "state": "Rajasthan",
        "country": "India",
        "description": (
            "Institute of national importance with a training and placement "
            "office coordinating campus hiring and internships."
        ),
        "sample_decision_maker": {"name": "Vikram Singh"},
        "sample_email": "placements@mnit.ac.in",
        "sample_phone": "+91-11-20001644",
    },
    {
        "name": "Birla Institute of Technology and Science Pilani",
        "domain": "bits-pilani.ac.in",
        "type": "University",
        "industry": "Education",
        "city": "Pilani",
        "state": "Rajasthan",
        "country": "India",
        "description": (
            "Deemed university with a dedicated career development centre "
            "focused on placement and internship support for students."
        ),
        "sample_decision_maker": {"name": "Anjali Bhatia"},
        "sample_email": "placements@bits-pilani.ac.in",
        "sample_phone": "+91-22-20001781",
    },
    {
        "name": "Manipal Institute of Technology",
        "domain": "manipal.edu",
        "type": "Engineering College",
        "industry": "Education",
        "city": "Manipal",
        "state": "Karnataka",
        "country": "India",
        "description": (
            "Constituent institute of a deemed university with a placement "
            "cell organizing recruitment and career fairs."
        ),
        "sample_decision_maker": {"name": "Nikhil Shetty"},
        "sample_email": "placements@manipal.edu",
        "sample_phone": "+91-33-20001918",
    },
    {
        "name": "SRM Institute of Science and Technology",
        "domain": "srmist.edu.in",
        "type": "University",
        "industry": "Education",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "country": "India",
        "description": (
            "Deemed university with a large training and placement "
            "department supporting employability across engineering programs."
        ),
        "sample_decision_maker": {"name": "Divya Ramakrishnan"},
        "sample_email": "placements@srmist.edu.in",
        "sample_phone": "+91-44-20002055",
    },
    {
        "name": "Lovely Professional University",
        "domain": "lpu.in",
        "type": "University",
        "industry": "Education",
        "city": "Jalandhar",
        "state": "Punjab",
        "country": "India",
        "description": (
            "Private university with a dedicated placement office running "
            "industry-readiness and coding assessment programs."
        ),
        "sample_decision_maker": {"name": "Harpreet Kaur"},
        "sample_email": "placements@lpu.in",
        "sample_phone": "+91-40-20002192",
    },
    {
        "name": "Amity University Noida",
        "domain": "amity.edu",
        "type": "University",
        "industry": "Education",
        "city": "Noida",
        "state": "Uttar Pradesh",
        "country": "India",
        "description": (
            "Private university with a training and placement cell managing "
            "campus recruitment and employability initiatives."
        ),
        "sample_decision_maker": {"name": "Rohit Malhotra"},
        "sample_email": "placements@amity.edu",
        "sample_phone": "+91-20-20002329",
    },
    {
        "name": "Guru Gobind Singh Indraprastha University",
        "domain": "ipu.ac.in",
        "type": "University",
        "industry": "Education",
        "city": "New Delhi",
        "state": "Delhi",
        "country": "India",
        "description": (
            "State university coordinating training and placement activities "
            "for affiliated engineering colleges."
        ),
        "sample_decision_maker": {"name": "Neha Gupta"},
        "sample_email": "placements@ipu.ac.in",
        "sample_phone": "+91-80-20002466",
    },
    {
        "name": "College of Engineering Pune",
        "domain": "coep.org.in",
        "type": "Engineering College",
        "industry": "Education",
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "description": (
            "Autonomous engineering college with a training and placement "
            "office focused on industry hiring and skill assessments."
        ),
        "sample_decision_maker": {"name": "Mahesh Joshi"},
        "sample_email": "placements@coep.org.in",
        "sample_phone": "+91-79-20002603",
    },
    {
        "name": "Vishwakarma Institute of Technology",
        "domain": "vit.edu",
        "type": "Engineering College",
        "industry": "Education",
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "description": (
            "Autonomous institute with an active placement cell coordinating "
            "employability and coding assessment drives."
        ),
        "sample_decision_maker": {"name": "Snehal Deshmukh"},
        "sample_email": "placements@vit.edu",
        "sample_phone": "+91-141-20002740",
    },
    {
        "name": "Sardar Vallabhbhai National Institute of Technology",
        "domain": "svnit.ac.in",
        "type": "Engineering College",
        "industry": "Education",
        "city": "Surat",
        "state": "Gujarat",
        "country": "India",
        "description": (
            "Institute of national importance with a training and placement "
            "cell driving campus hiring initiatives."
        ),
        "sample_decision_maker": {"name": "Bhavesh Patel"},
        "sample_email": "placements@svnit.ac.in",
        "sample_phone": "+91-281-20002877",
    },
    {
        "name": "Chandigarh University",
        "domain": "cuchd.in",
        "type": "University",
        "industry": "Education",
        "city": "Mohali",
        "state": "Punjab",
        "country": "India",
        "description": (
            "Private university with a dedicated placement office running "
            "employability and industry readiness programs."
        ),
        "sample_decision_maker": {"name": "Simran Kaur"},
        "sample_email": "placements@cuchd.in",
        "sample_phone": "+91-422-20003014",
    },
    {
        "name": "Delhi Technological University",
        "domain": "dtu.ac.in",
        "type": "Engineering College",
        "industry": "Education",
        "city": "New Delhi",
        "state": "Delhi",
        "country": "India",
        "description": (
            "State university with a training and placement cell "
            "coordinating recruitment and internship drives."
        ),
        "sample_decision_maker": {"name": "Ankit Sharma"},
        "sample_email": "placements@dtu.ac.in",
        "sample_phone": "+91-471-20003151",
    },
    {
        "name": "Jawaharlal Nehru Technological University Hyderabad",
        "domain": "jntuh.ac.in",
        "type": "University",
        "industry": "Education",
        "city": "Hyderabad",
        "state": "Telangana",
        "country": "India",
        "description": (
            "State technical university coordinating placement activities "
            "for affiliated engineering colleges across the state."
        ),
        "sample_decision_maker": {"name": "Srinivas Rao"},
        "sample_email": "placements@jntuh.ac.in",
        "sample_phone": "+91-11-20003288",
    },
    {
        "name": "Bhartiya Skill Development University",
        "domain": "bsdu.org.in",
        "type": "Skill Development Organization",
        "industry": "Education",
        "city": "Jaipur",
        "state": "Rajasthan",
        "country": "India",
        "description": (
            "Skill development university offering vocational training and "
            "employability programs backed by an industry placement cell."
        ),
        "sample_decision_maker": {"name": "Deepak Choudhary"},
        "sample_email": "placements@bsdu.org.in",
        "sample_phone": "+91-141-20003425",
    },
    {
        "name": "National Skill Training Institute",
        "domain": "nsti.gov.in",
        "type": "Skill Development Organization",
        "industry": "Education",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "country": "India",
        "description": (
            "Government-run vocational training institute with a placement "
            "cell coordinating apprenticeships and industry hiring."
        ),
        "sample_decision_maker": {"name": "Geetha Krishnan"},
        "sample_email": "placements@nsti.gov.in",
        "sample_phone": "+91-44-20003562",
    },
    {
        "name": "National Institute for Entrepreneurship and Small Business Development",
        "domain": "niesbud.nic.in",
        "type": "Professional Training Institute",
        "industry": "Education",
        "city": "New Delhi",
        "state": "Delhi",
        "country": "India",
        "description": (
            "Professional training institute running entrepreneurship and "
            "skill-building programs with a career services office."
        ),
        "sample_decision_maker": {"name": "Manoj Tiwari"},
        "sample_email": "placements@niesbud.nic.in",
        "sample_phone": "+91-11-20003699",
    },
    {
        "name": "Institute of Chartered Financial Analysts of India",
        "domain": "icfai.org",
        "type": "Professional Training Institute",
        "industry": "Education",
        "city": "Hyderabad",
        "state": "Telangana",
        "country": "India",
        "description": (
            "Professional training and certification institute with a "
            "career services office supporting placement drives."
        ),
        "sample_decision_maker": {"name": "Ramesh Chandra"},
        "sample_email": "placements@icfai.org",
        "sample_phone": "+91-40-20003836",
    },
    {
        "name": "Byju's Learning Solutions",
        "domain": "byjuslearning.example.com",
        "type": "EdTech Organization",
        "industry": "Education Technology",
        "city": "Bengaluru",
        "state": "Karnataka",
        "country": "India",
        "description": (
            "EdTech organization running large-scale campus hiring and "
            "technical assessment programs for content and engineering roles."
        ),
        "sample_decision_maker": {"name": "Aditi Rao"},
        "sample_email": "careers@byjuslearning.example.com",
        "sample_phone": "+91-80-20003973",
    },
    {
        "name": "Vedantu Innovations",
        "domain": "vedantuinnovations.example.com",
        "type": "EdTech Organization",
        "industry": "Education Technology",
        "city": "Bengaluru",
        "state": "Karnataka",
        "country": "India",
        "description": (
            "EdTech company with a dedicated talent acquisition team hiring "
            "for coding assessment and content development roles."
        ),
        "sample_decision_maker": {"name": "Kunal Bhatia"},
        "sample_email": "careers@vedantuinnovations.example.com",
        "sample_phone": "+91-80-20004110",
    },
    {
        "name": "Coastal Institute of Technical Education",
        "domain": "coastaltechedu.ac.in",
        "type": "Technical Institute",
        "industry": "Education",
        "city": "Visakhapatnam",
        "state": "Andhra Pradesh",
        "country": "India",
        "description": (
            "Technical institute with a placement director and career "
            "services team supporting employability initiatives."
        ),
        "sample_decision_maker": {"name": "Satya Prakash"},
        "sample_email": "placements@coastaltechedu.ac.in",
        "sample_phone": "+91-79-20004247",
    },
    {
        "name": "Northern Institute of Polytechnic",
        "domain": "nipolytechnic.ac.in",
        "type": "Technical Institute",
        "industry": "Education",
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "country": "India",
        "description": (
            "Polytechnic institute with a training and placement wing "
            "supporting industry-readiness assessments for diploma students."
        ),
        "sample_decision_maker": {"name": "Alok Mishra"},
        "sample_email": "placements@nipolytechnic.ac.in",
        "sample_phone": "+91-522-20004384",
    },
    {
        "name": "Aarohi Technologies Pvt Ltd",
        "domain": "aarohitech.example.com",
        "type": "Company",
        "industry": "Information Technology",
        "city": "Hyderabad",
        "state": "Telangana",
        "country": "India",
        "description": (
            "IT services company running campus hiring and technical "
            "interview evaluation programs for engineering talent."
        ),
        "sample_decision_maker": {"name": "Farah Sheikh"},
        "sample_email": "careers@aarohitech.example.com",
        "sample_phone": "+91-40-20004521",
    },
    {
        "name": "Zenith Workforce Solutions",
        "domain": "zenithworkforce.example.com",
        "type": "Company",
        "industry": "Recruitment",
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India",
        "description": (
            "Workforce staffing company evaluating candidate skill "
            "assessments for enterprise hiring managers."
        ),
        "sample_decision_maker": {"name": "Vivaan Kapoor"},
        "sample_email": "careers@zenithworkforce.example.com",
        "sample_phone": "+91-22-20004658",
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
