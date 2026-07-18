"""TR-IN: ingestion & retrieval."""
from __future__ import annotations

from tests.conftest import CANARIES


def test_parse_sections(synthetic_pdf, providers):  # TR-IN-1
    pack = providers.parser.parse(synthetic_pdf, "Q3 board pack")
    titles = {s.title for s in pack.sections}
    assert "Capital Adequacy" in titles
    assert "Credit Risk" in titles
    # a canary is present in the pack (so later we can prove it never leaks)
    all_text = " ".join(s.text for s in pack.sections)
    assert any(c in all_text for c in CANARIES)


def test_index_and_retrieve(synthetic_pdf, providers):  # TR-IN-2 / TR-IN-3
    pack = providers.parser.parse(synthetic_pdf, "Q3 board pack")
    chunks = providers.retriever.index(pack)
    assert len(chunks) > 0
    hits = providers.retriever.retrieve(pack.id, "credit provisions lending", k=3)
    assert hits, "expected a relevant chunk"
    assert any("credit" in h.chunk_text.lower() for h in hits)


def test_drop_clears_index(synthetic_pdf, providers):  # supports TR-INV-5 / TR-RT-2
    pack = providers.parser.parse(synthetic_pdf, "Q3 board pack")
    providers.retriever.index(pack)
    providers.retriever.drop(pack.id)
    assert providers.retriever.retrieve(pack.id, "credit", k=3) == []
