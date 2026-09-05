# Coplur Lead Finder

A lightweight, database-free web application that helps Coplur discover
potential B2B customers and export publicly available business contact
information to CSV.

## 1. Project Overview

Coplur Lead Finder lets a user describe a target segment (engineering
colleges, universities, companies, etc.), keywords and decision-maker roles,
then automatically:

1. Generates targeted search queries.
2. Discovers candidate organizations via a pluggable search provider.
3. Analyzes a small, bounded set of public pages per organization (contact,
   about, placement/career pages).
4. Extracts publicly available business emails and phone numbers.
5. Qualifies each lead with a rule-based scorer (or an optional AI provider).
6. Deduplicates results by domain/organization name.
7. Displays results in a sortable, filterable table.
8. Exports the selected leads to a CSV file.

The app is intentionally lightweight: **no database, no background workers,
no Docker requirement, no browser automation**. Results are held in memory
for the current request/session only.

## 2. Features

- Modular provider architecture for search and AI qualification.
- Works fully offline in **mock mode** (default) — no API keys required.
- Optional AI-powered lead qualification (falls back to rule-based scoring
  automatically when disabled or unavailable).
- Conservative, safe contact extraction (regex-based emails/phones).
- Deduplication by normalized domain and organization name.
- CSV export with formula-injection sanitization, UTF-8 + BOM for Excel.
- Graceful error handling — a single failing website never aborts a search.

## 3. Architecture

```text
coplur-lead-finder/
├── frontend/   React + Vite + TypeScript dashboard
└── backend/    FastAPI service
    ├── models/       Pydantic data models (Lead, Search request/response)
    ├── routers/       /api/leads/search, /api/leads/export
    ├── services/      discovery, website analysis, contact extraction,
    │                  qualification, deduplication, CSV export
    ├── providers/     Search provider + AI provider abstractions
    └── utils/         domain normalization, text cleaning helpers
```

## 4. Installation

### Backend setup

```bash
cd coplur-lead-finder/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`.

### Frontend setup

```bash
cd coplur-lead-finder/frontend
npm install
cp .env.example .env
npm run dev
```

The dashboard is available at `http://localhost:5173`.

## 5. Environment Configuration

Backend `.env` (see `backend/.env.example`):

```env
SEARCH_PROVIDER=mock

SERPER_API_KEY=
TAVILY_API_KEY=

USE_AI=false
OPENAI_API_KEY=

MAX_PAGES_PER_DOMAIN=5
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=10

DEFAULT_MIN_RELEVANCE_SCORE=60
```

Frontend `.env` (see `frontend/.env.example`):

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 6. Running in Mock Mode

By default `SEARCH_PROVIDER=mock` and `USE_AI=false`, so the application
runs end-to-end without any external API keys, returning realistic sample
Coplur customer data (engineering colleges, universities, skill development
organizations, companies, etc.).

## 7. Running with a Real Search Provider

Set `SEARCH_PROVIDER` to one of `serper`, `tavily`, `bing`, or `google`, and
populate the matching API key(s) in `.env`. The corresponding provider class
lives in `backend/app/providers/search_provider.py`.

## 8. Running with AI Qualification

Set `USE_AI=true`. If `OPENAI_API_KEY` is present, the `OpenAIProvider` is
used; otherwise a deterministic `MockAIProvider` is used so AI mode can still
be exercised locally without a key. AI failures always fall back to the
rule-based qualification service — the search never crashes because of AI.

## 9. API Examples

### Search leads

```http
POST /api/leads/search
Content-Type: application/json

{
  "target_segment": "Engineering Colleges",
  "industry": "Education",
  "location": "India",
  "keywords": ["placement", "employability", "coding assessment"],
  "roles": ["Training and Placement Officer", "Placement Director"],
  "limit": 50,
  "min_relevance_score": 60
}
```

### Export CSV

```http
POST /api/leads/export
Content-Type: application/json

{ "leads": [] }
```

### Health check

```http
GET /health
```

## 10. CSV Export

`POST /api/leads/export` returns a downloadable, UTF-8 (with BOM for Excel
compatibility) CSV containing only the fields the user selected in the UI.
Fields starting with `=`, `+`, `-`, or `@` are prefixed with a leading quote
to prevent spreadsheet formula injection.

## 11. Limitations

- The mock search provider returns a small, fixed set of sample
  organizations — real search providers require your own API keys.
- Contact extraction only reads a handful of well-known page paths per
  domain (max 5 by default) and never crawls an entire site.
- No data is fabricated: if a field cannot be verified from a public page,
  it is left empty.
- Results are held in memory only; refreshing the page clears them. Export
  to CSV before refreshing if you want to keep results.
