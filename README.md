# CareerOS (MVP backend)
Resume -> structured profile -> job parse -> explainable match -> skill gaps.

    cd backend && pip install -r requirements.txt
    pytest
    uvicorn app.main:app --reload   # interactive docs at /docs

Scoring is deterministic (`services/scoring_engine.py`); the LLM is only for explanations (`services/explain.py`).
Next: Next.js frontend, Firebase persistence, Pinecone semantic matching, Mistral explanations, resume tailoring.

## Frontend
    cd frontend && cp .env.example .env.local && npm install && npm run dev   # http://localhost:3000
Run the backend on port 8000 first. Pages: /dashboard, /dashboard/resume, /dashboard/job-analysis.

## Deploy
Backend: Render (`render.yaml`, Docker). Set AUTH_REQUIRED=true, FRONTEND_ORIGIN, MISTRAL_API_KEY, FIREBASE_CREDENTIALS (service-account JSON; mount as a secret file).
Frontend: Vercel, root `frontend`, set NEXT_PUBLIC_API_URL and NEXT_PUBLIC_FIREBASE_*.
Quality: `cd backend && pytest && python -m eval.evaluate`. See `docs/`.
