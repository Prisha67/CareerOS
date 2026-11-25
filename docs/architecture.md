# Architecture
Next.js (Vercel) -> FastAPI (Render) -> LangGraph flows -> deterministic services + Mistral (optional).
- **Deterministic:** parsers, taxonomy, scoring, roadmap, interview rubric, analytics.
- **LLM (optional, guarded):** recommendations, bullet rewrites, cover letters, answers, interview coach note. Output passes `services/guard.py`; unsupported claims trigger a template fallback.
- **Human approval:** drafts are `pending_approval` until the user approves; edits reset approval. Nothing is auto-submitted.
- **Auth:** Firebase ID tokens (`AUTH_REQUIRED=true`); the verified uid overrides any client-supplied user_id.
- **Storage:** JSON file (`backend/data/store.json`). Replace `services/storage.py` with Firestore for production.
- **Semantic evidence:** Mistral embeddings + local cosine (`services/semantic.py`), informational only. `integrations/pinecone_store.py` is an unwired adapter.
