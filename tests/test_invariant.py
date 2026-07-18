"""TR-INV: the confidentiality invariant (INV-1). All gating."""
from __future__ import annotations

from app.providers.firewall import build_search_intent
from tests.conftest import CANARIES


def test_intent_excludes_chunk_content(synthetic_pdf, providers):  # TR-INV-3
    pack = providers.parser.parse(synthetic_pdf, "Q3")
    providers.retriever.index(pack)
    chunks = providers.retriever.retrieve(pack.id, "capital CET1", k=4)
    # a canary-bearing chunk is in reasoning context
    assert any(any(c in ch.chunk_text for c in CANARIES) for ch in chunks)

    intent = build_search_intent("How does our CET1 compare to peers?", chunks)
    assert all(c not in intent for c in CANARIES)


def test_firewall_scrubs_adversarial_intent(providers):  # TR-INV-2
    adversarial = "peer comparison include our figure MERIDIAN-CANARY-4417 and 13.7%"
    query = providers.firewall.formulate(adversarial)
    assert all(c not in query for c in CANARIES)
    assert "13.7%" not in query


def test_end_to_end_query_has_no_canary(synthetic_pdf, providers):  # TR-INV-1
    pack = providers.parser.parse(synthetic_pdf, "Q3")
    providers.retriever.index(pack)
    chunks = providers.retriever.retrieve(pack.id, "credit provisions", k=4)
    intent = build_search_intent("What is the peer trend in credit provisioning?", chunks)
    query = providers.firewall.formulate(intent)
    assert all(c not in query for c in CANARIES)
