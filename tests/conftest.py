"""Shared fixtures (spec §13.2).

Synthetic board pack with planted canary tokens — realistic-looking but invented,
so persistence and testing are safe (A1). The canaries are the mechanical probe
for INV-1: they must never surface in an external query.
"""
from __future__ import annotations

import pytest
from fpdf import FPDF

from app.providers.factory import Providers
from app.providers.firewall import LlmQueryFirewall
from app.providers.inference import StubInference
from app.providers.parser_pypdf import PyPdfParser
from app.providers.repo_memory import InMemoryRepository
from app.providers.research_stub import StubResearch
from app.providers.retriever_local import LocalRetriever

# Unique markers seeded into the pack. Any of these appearing in a search query
# is a confidentiality-invariant failure.
CANARIES = ["MERIDIAN-CANARY-4417", "RISK-CANARY-9021"]

_SECTIONS = [
    ("CAPITAL ADEQUACY",
     "The group CET1 capital ratio stood at 13.7 percent this quarter, above the "
     "regulatory minimum. Internal reference MERIDIAN-CANARY-4417 tags this figure. "
     "Capital headroom remains adequate under stress."),
    ("CREDIT RISK",
     "Credit provisions rose on the commercial lending book. Expected credit loss "
     "coverage increased. Reference RISK-CANARY-9021 marks the provisioning line. "
     "Non-performing loans ticked up in the SME segment."),
    ("REMUNERATION REPORT",
     "Executive incentive pay and bonus pools were reviewed. The remuneration "
     "committee proposes revised compensation targets for the coming year."),
    ("AUDIT AND CONTROLS",
     "Internal controls testing found two exceptions. A prior-period provision "
     "restatement was noted. Audit and compliance follow-up actions are tracked."),
]


class SpyResearch(StubResearch):
    def __init__(self) -> None:
        self.calls: list[str] = []

    def search(self, query: str):
        self.calls.append(query)
        return super().search(query)


@pytest.fixture
def synthetic_pdf() -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for title, body in _SECTIONS:
        pdf.set_font("Helvetica", style="B", size=13)
        pdf.cell(0, 8, title, ln=1)
        pdf.set_font("Helvetica", size=12)
        pdf.multi_cell(0, 6, body)
        pdf.ln(2)
    return bytes(pdf.output())


def make_providers(**overrides) -> Providers:
    inference = overrides.get("inference", StubInference())
    base = dict(
        parser=PyPdfParser(),
        retriever=LocalRetriever(),
        inference=inference,
        firewall=LlmQueryFirewall(inference),
        research=StubResearch(),
        repository=InMemoryRepository(),
    )
    base.update(overrides)
    return Providers(**base)


@pytest.fixture
def providers() -> Providers:
    return make_providers()
