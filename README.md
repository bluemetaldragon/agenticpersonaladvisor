# Board-Prep Agent — backend

Phase 0 foundation + Slice 1 vertical (ingestion → retrieval → pre-read), built on
the architecture and requirements spec (v1.2). LangGraph agent core, FastAPI shell,
every external dependency behind a swappable interface (NFR-2).

## Run

```bash
cd backend
pip install -r requirements.txt
pytest -q                       # gating suite (9 tests)
uvicorn app.main:app --reload   # API on :8000, /health to check providers
```

No keys needed — it runs on local/stub providers by default.

## What's real vs stubbed

| Concern | Now (runs here) | Prod swap (one file) |
|---|---|---|
| Parser (M3) | PyPDF + heading heuristic | Docling (local, table-aware) |
| Retriever (M4) | keyword scoring, in-memory | local embedder + pgvector |
| Inference | deterministic `StubInference` | Claude via Anthropic API |
| Research (M8) | `StubResearch` | Tavily |
| Repository (M9) | in-memory | Supabase (Postgres + pgvector + Storage) |

Swap point is `app/providers/factory.py` plus credentials in `.env` (`BPA_` prefix).
Nothing in `engine/` or the API changes.

## Layout

```
app/
  domain.py            # entities (spec §7)
  interfaces.py        # provider Protocols, tagged by module (NFR-2)
  config.py            # settings; provider selectors default to stub/local
  engine/
    state.py           # LangGraph state
    nodes.py           # ingest (idempotent) + profile-shaped pre-read
    graph.py           # START -> ingest -> preread -> END
    engine.py          # facade used by the API
  providers/
    parser_pypdf.py  retriever_local.py  inference.py
    firewall.py      research_stub.py    repo_memory.py
    factory.py         # the single swap point
  main.py              # FastAPI routes
tests/
  conftest.py          # synthetic pack + canary tokens
  test_ingestion.py    # TR-IN
  test_preread.py      # TR-PRE
  test_invariant.py    # TR-INV (INV-1)
```

## Confidentiality invariant (INV-1)

The wall is structural, not conventional:

- `build_search_intent(question, chunks)` derives the search intent from the
  question **only**; retrieved chunks inform later analysis but are never used to
  build the query. The firewall is simply never handed pack content.
- `LlmQueryFirewall.formulate` produces the query and applies a defensive scrub.
- `tests/test_invariant.py` seeds canary tokens into the pack and asserts none ever
  appear in a query — including when a canary-bearing chunk sits in reasoning
  context (`test_intent_excludes_chunk_content`). These tests are gating.

## Status against slice exit criteria

Slice 1 target — `TR-IN`, `TR-PR`(partial), `TR-PRE`, embedding-egress — green.
Next: Slice 2 (challenge sheet), then Slice 3 (deep-dive + firewall + research),
which cannot close until the full `TR-FW` / `TR-INV` suite is green against real
inference.
