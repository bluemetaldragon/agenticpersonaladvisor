"""The single place providers are chosen. Swapping to prod is editing this file
plus supplying credentials — nothing in engine/ or the API changes.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings, settings as default_settings
from app.interfaces import (
    Inference,
    PackParser,
    Repository,
    ResearchProvider,
    Retriever,
    QueryFirewall,
)
from app.providers.firewall import LlmQueryFirewall
from app.providers.inference import AnthropicInference, StubInference
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

    if cfg.inference == "anthropic" and cfg.anthropic_api_key:
        inference: Inference = AnthropicInference(cfg.anthropic_api_key)
    else:
        inference = StubInference()

    firewall: QueryFirewall = LlmQueryFirewall(inference)
    research: ResearchProvider = StubResearch()  # tavily swap: research_tavily
    repository: Repository = InMemoryRepository()  # supabase swap: repo_supabase

    return Providers(
        parser=parser,
        retriever=retriever,
        inference=inference,
        firewall=firewall,
        research=research,
        repository=repository,
    )
