"""
MongoDB connection via Motor (async driver).
Call get_database() to obtain the database instance.
"""
from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri)
    return _client


async def get_database() -> AsyncIOMotorDatabase:
    return get_client().get_default_database()


async def ping_database() -> None:
    """Raise if the database is unreachable. Called at startup."""
    client = get_client()
    await client.admin.command("ping")


async def close_database() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
