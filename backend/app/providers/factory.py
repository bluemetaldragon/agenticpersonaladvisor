"""The single place providers are chosen. Swapping to prod is editing this file + creds."""
from __future__ import annotations
from dataclasses import dataclass

from app.config import Settings, settings as default_settings
from app.interfaces import (
    Inference, PackParser, Repository, ResearchProvider, Retriever, QueryFirewall,
)
from app.providers.firewall import LlmQueryFirewall
from app.providers.inference import DeepSeekInference, StubInference
from app.providers.parser_pypdf import PyPdfParser
from app.providers.repo_memory import InMemoryRepository
from app.providers.research_stub import StubResearch
from app.providers.retriever_local import LocalRetriever


@dataclass
class Providers:
    parser: PackParser
    retriever: Retriever
    inference: Inference
    firewall: QueryFirewall
    research: ResearchProvider
    repository: Repository


def build_providers(cfg: Settings | None = None) -> Providers:
    cfg = cfg or default_settings

    if cfg.parser == "pypdf":
        parser: PackParser = PyPdfParser()
    else:  # pragma: no cover - prod swap
        from app.providers.parser_docling import DoclingParser  # noqa
        parser = DoclingParser()

    retriever: Retriever = LocalRetriever()  # pgvector swap: retriever_pgvector

    if cfg.inference == "deepseek" and cfg.deepseek_api_key:
        inference: Inference = DeepSeekInference(
            cfg.deepseek_api_key, model=cfg.deepseek_model, base_url=cfg.deepseek_base_url)
    else:
        inference = StubInference()

    firewall: QueryFirewall = LlmQueryFirewall(inference)

    if cfg.research == "tavily" and cfg.tavily_api_key:  # pragma: no cover - prod swap
        from app.providers.research_tavily import TavilyResearch
        research: ResearchProvider = TavilyResearch(cfg.tavily_api_key)
    else:
        research = StubResearch()

    if cfg.repository == "supabase" and cfg.supabase_url and cfg.supabase_key:
        from app.providers.repo_supabase import SupabaseRepository
        repository: Repository = SupabaseRepository(cfg.supabase_url, cfg.supabase_key)
    else:
        repository = InMemoryRepository()

    return Providers(parser=parser, retriever=retriever, inference=inference,
                     firewall=firewall, research=research, repository=repository)