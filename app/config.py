"""Settings. Defaults select local/stub providers so the app runs with no keys.

Flip provider selectors (and supply keys) to swap in Docling / Claude / Tavily /
Supabase — no code change beyond the provider factory (see app/providers/factory.py).
"""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BPA_", env_file=".env", extra="ignore")

    # provider selectors
    parser: str = "pypdf"          # pypdf | docling
    retriever: str = "local"       # local | pgvector
    inference: str = "stub"        # stub | anthropic
    research: str = "stub"         # stub | tavily
    repository: str = "memory"     # memory | supabase

    # credentials (unused by stubs)
    anthropic_api_key: str | None = None
    tavily_api_key: str | None = None
    supabase_url: str | None = None
    supabase_key: str | None = None

    # defaults
    default_retention: str = "persist"   # persist | ephemeral
    preread_max_items: int = 5


settings = Settings()
