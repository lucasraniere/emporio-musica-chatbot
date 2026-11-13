# AI assistant task log

Tasks done by Claude Code (Claude Fable 5.2) in this repository. The application code is written by hand; this file records only what the assistant did, to support the "Uso de assistentes de código" section of the README.

## 2026-11-12

| # | Task | Type | Files touched |
|---|------|------|---------------|
| 1 | Read the challenge PDF, the policy manual and the six CSVs; profiled the data for inconsistencies (stock vs. status, inactive promotions, order totals, duplicate email, conflicting contacts in the manual). | Analysis | none |
| 2 | Proposed the architecture (single LangGraph tool-calling agent, RAG over the policy PDF with Chroma, typed SQLite tools for the CSVs, SQLite checkpointer) and a step-by-step build order. | Planning | none |
| 3 | Added runtime and dev dependencies to `pyproject.toml` (not synced; `uv sync` left to the author). | Config | `pyproject.toml` |
| 4 | Rewrote `.gitignore`: stopped ignoring `.python-version`; added `.venv`, `.env`, Python caches and generated artifacts (SQLite DB, Chroma index). | Config | `.gitignore` |
| 5 | Renamed the CSVs, dropping the `desafio_tecnico_ai_eng - ` prefix (e.g. `products.csv`). Contents unchanged. | Data | `data/*.csv` |
| 6 | Created this log. | Docs | `AI_TASKS.md` |
| 7 | Reviewed the hand-written `src/config.py` and imported it to verify; found that `ROOT_DIR` resolved one level above the repo, so `.env` was not loaded. Reported only, no edits. | Review | none |
| 8 | Re-checked the config after the author moved it to `src/emporio/config.py`; imported it and confirmed the root path, `.env`, data paths and LangSmith variables now resolve. Reported only, no edits. | Review | none |

## 2026-11-13

| # | Task | Type | Files touched |
|---|------|------|---------------|
| 9 | Verified the SQLite database built by the author's `build_db.py`: schema, row counts, cell-by-cell comparison with the CSVs, foreign keys, and the `product_catalog` view (availability, promotions, PIX price). No defects found, no edits. | Review | none |
| 10 | Verified the Chroma index built by the author's `build_index.py`: 26 section chunks, no page-header noise, key facts present, and a 12-question retrieval test (10 hits; two weak rankings reported). No edits. | Review | none |
| 11 | Re-tested retrieval after the author switched the embedding model to `intfloat/multilingual-e5-base` and rebuilt: confirmed 768-dim vectors and ran an 18-question test (16 hits at k=4, 17 at k=6). No edits. | Review | none |
| 12 | Reviewed and ran the author's `db_helper.py` and `rag/embeddings.py`: the read-only query helper works; the embeddings module fails on import (typo in a module name, outdated Chroma import path). Reported only, no edits. | Review | none |
| 13 | Re-checked after the author's fix: `rag/embeddings.py` now imports and retrieves correctly; `build_index.py` fails on import because the old copy of `get_embeddings()` was left behind. Reported only, no edits. | Review | none |
| 14 | Re-checked `build_index.py` after the leftover function was removed: ran a full test build into a scratch directory (26 chunks, no errors). No edits. | Review | none |
| 15 | Tested the three tools written so far (`search_policies`, `get_product_details`, `search_products`) by calling each directly with 27 cases covering normal answers, promotions, unavailable products and not-found inputs; all passed. No edits. | Testing | none |
| 16 | Tested the two new tools (`list_active_promotions`, `get_order_status`) with 16 cases, including identity-check rejections; all passed. Reported only, no edits. | Testing | none |
