"""FastAPI application entry point for the Coplur Lead Finder backend."""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import leads

app = FastAPI(
    title="Coplur Lead Finder API",
    description="Lightweight API for discovering and exporting potential Coplur customers.",
    version="1.0.0",
)

allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leads.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
