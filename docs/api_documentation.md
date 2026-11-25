# API (interactive docs at /docs)
Resume: POST /resume/upload, GET|PUT|DELETE /profile/me. Analysis: POST /applications/match, GET /analysis/{id}, GET /analyses, POST /analysis/{id}/rescore.
Drafts: POST /resume/tailor, /documents/cover-letter, /documents/answer; PATCH /documents/{id}; GET /documents.
Roadmap: POST /roadmap/generate, GET /roadmap, PATCH /roadmap/{id}/milestones/{mid}.
Interview: POST /interviews/start, /interviews/answer; GET /interviews.
Tracker: GET|POST /applications, PATCH /applications/{id}; GET /analytics. Ops: GET /health, /metrics.
