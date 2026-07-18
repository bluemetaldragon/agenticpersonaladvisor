"""TR-PRE: pre-read generation."""
from __future__ import annotations

from app.domain import Committee, DirectorProfile, RetentionMode
from app.engine.engine import BoardPrepEngine
from tests.conftest import make_providers, SpyResearch


def _run(pdf, committee):
    providers = make_providers()
    engine = BoardPrepEngine(providers)
    profile = DirectorProfile(committee=committee)
    return engine.ingest_and_preread(pdf, "Q3 board pack", profile, RetentionMode.PERSIST)


def test_emphasis_by_committee(synthetic_pdf):  # TR-PRE-1
    _, risk_preread = _run(synthetic_pdf, Committee.RISK)
    assert risk_preread.items[0].heading in {"Capital Adequacy", "Credit Risk"}

    _, audit_preread = _run(synthetic_pdf, Committee.AUDIT)
    assert audit_preread.items[0].heading in {"Audit And Controls", "Credit Risk"}


def test_items_addressable(synthetic_pdf):  # TR-PRE-3
    _, preread = _run(synthetic_pdf, Committee.RISK)
    refs = [i.item_ref for i in preread.items]
    assert len(refs) == len(set(refs))
    assert all(i.source_section_ref for i in preread.items)


def test_preread_makes_no_external_calls(synthetic_pdf):  # TR-PRE-2
    spy = SpyResearch()
    providers = make_providers(research=spy)
    engine = BoardPrepEngine(providers)
    engine.ingest_and_preread(
        synthetic_pdf, "Q3", DirectorProfile(committee=Committee.RISK),
        RetentionMode.PERSIST,
    )
    assert spy.calls == []
