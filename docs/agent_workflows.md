# Agent workflows
**Analysis graph:** validate (profile agent) -> [no skills: stop, 409] -> job parse -> match (scoring engine + semantic hints) -> explain (LLM or template).
**Document graph:** select evidence -> draft -> check (guard) -> [unsupported claims: template fallback] -> pending approval.
**Interview:** questions from job+projects -> rubric evaluation per answer -> average score.
