from app.agents import interview as iv
from app.services import semantic
from app.services.tracker import analytics
from app.integrations import llm
from app.services.job_parser import parse_job
from app.services.resume_parser import parse_resume
from tests.test_phase2_3 import R, J
from eval.evaluate import run
P, JOB = parse_resume(R), parse_job(J)

def test_questions_cover_categories():
    cats = {q["category"] for q in iv.questions(P, JOB)}
    assert {"Technical", "Project", "Behavioural", "HR"} <= cats

def test_evaluation_rewards_good_answers():
    q = iv.questions(P, JOB)[0]
    good = iv.evaluate(q, "I use Python lists and functions to write scripts and a small library for data tasks. For example, I wrote a class that cleans a table and tests it. It reduced errors.")
    bad = iv.evaluate(q, "I know it")
    assert good["score"] > bad["score"] and bad["improve"]

def test_star_feedback():
    q = next(x for x in iv.questions(P, JOB) if x["category"] == "Behavioural")
    assert "STAR" in " ".join(iv.evaluate(q, "It was hard but fine.")["improve"])

def test_analytics():
    db = {"analyses": {"a": {"user_id": "u", "created_at": 1, "match": {"total": 60, "missing_required": ["SQL"], "missing_preferred": []}}},
          "applications": {"x": {"user_id": "u", "status": "interview", "history": [{"status": "saved"}, {"status": "applied"}, {"status": "interview"}]}},
          "interviews": {"i": {"user_id": "u", "answers": {"q1": {"score": 7.0}}}}, "roadmaps": {}}
    a = analytics(db, "u")
    assert a["interview_rate"] == 100 and a["top_missing_skills"] == [("SQL", 1)] and a["interview_avg"] == 7.0

def test_semantic_cosine_and_no_key(monkeypatch=None):
    assert abs(semantic.cosine([1, 0], [1, 0]) - 1) < 1e-9 and semantic.cosine([1, 0], [0, 1]) == 0
    assert semantic.hints(["NLP"], P) == []   # no key -> no hints

def test_metrics_exist(): assert {"calls", "failures", "total_ms"} <= set(llm.METRICS)

def test_eval_harness():
    assert all(r[1][2] >= 0.8 for r in run())

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"): f(); print("ok", n)
