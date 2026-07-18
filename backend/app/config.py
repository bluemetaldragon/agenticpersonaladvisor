"""Settings. Defaults select local/stub providers so the app runs with no keys."""
from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BPA_", env_file=".env", extra="ignore")

    parser: str = "pypdf"          # pypdf | docling
    retriever: str = "local"       # local | pgvector
    inference: str = "stub"        # stub | deepseek
    research: str = "stub"         # stub | tavily
    repository: str = "memory"     # memory | supabase

    deepseek_api_key: str | None = None
    deepseek_model: str = "deepseek-v4-flash"
    deepseek_base_url: str = "https://api.deepseek.com"
    tavily_api_key: str | None = None
    supabase_url: str | None = None
    supabase_key: str | None = None

    default_retention: str = "persist"
    preread_max_items: int = 5
    challenge_max_items: int = 5
    job_poll_seconds: float = 10.0       # SSE progress poll interval (M11)
    cors_origins: str = "http://localhost:3000"  # Next.js dev origin(s), comma-sep


settings = Settings()