"""
FastAPI application entry point.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import close_database, ping_database
from routers import ai, analysis, ingest, projects

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CodeMind AI",
    description="AI-powered codebase understanding platform",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(projects.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(ai.router, prefix="/api")


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup() -> None:
    logger.info("Starting CodeMind AI v%s", app.version)
    try:
        await ping_database()
        logger.info("MongoDB connection verified.")
    except Exception as exc:
        logger.error(
            "\n\n  WARNING: Could not connect to MongoDB: %s\n"
            "  The server will start but all database operations will fail.\n"
            "  Set MONGODB_URI in your .env file to a valid connection string.\n",
            exc,
        )


@app.on_event("shutdown")
async def shutdown() -> None:
    await close_database()
    logger.info("MongoDB connection closed.")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/api/health", tags=["Meta"])
async def health() -> dict:
    return {"status": "ok", "version": app.version}
