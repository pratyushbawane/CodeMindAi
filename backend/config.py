"""
Application configuration.
All values are loaded from environment variables (or a .env file).
The application will refuse to start if required secrets are missing.
"""
from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Required secrets (no defaults — fail fast if absent) ---
    mongodb_uri: str
    openai_api_key: str

    # --- LLM / Embedding ---
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # --- Sandbox / storage ---
    sandbox_base_path: str = "/tmp/codemind"
    vector_store_path: str = "./data/chroma"

    # --- CORS ---
    cors_origins: str = "http://localhost:5173"

    # --- Safety limits ---
    max_zip_size_mb: int = 50
    max_files_per_project: int = 5000
    max_file_size_kb: int = 500

    @field_validator("mongodb_uri")
    @classmethod
    def mongodb_uri_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(
                "\n\n  MONGODB_URI is not set.\n"
                "  Copy .env.example to .env and fill in your MongoDB Atlas connection string.\n"
            )
        return v

    @field_validator("openai_api_key")
    @classmethod
    def openai_key_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(
                "\n\n  OPENAI_API_KEY is not set.\n"
                "  Copy .env.example to .env and fill in your OpenAI API key.\n"
            )
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def max_zip_size_bytes(self) -> int:
        return self.max_zip_size_mb * 1024 * 1024

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_kb * 1024


# Single shared instance — imported everywhere as `from config import settings`
settings = Settings()
