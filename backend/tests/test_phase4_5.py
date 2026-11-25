from app.agents import documents, roadmap
from app.graphs.analysis_graph import build_graph
from app.integrations import llm
from app.services.guard import grounded
from app.services.job_parser import parse_job
from app.services.resume_parser import parse_resume
from app.services.scoring_engine import score
from tests.test_phase2_3 import R, J
P, JOB = parse_resume(R), parse_job(J)

def test_guard():
    assert not grounded("Built with PyTorch, 95% accuracy", "Used TensorFlow", {"TensorFlow"})[0]
    assert grounded("Used TensorFlow", "Used TensorFlow", {"TensorFlow"})[0]

def test_conditional_flow_stops_on_empty_profile():
    o = build_graph().invoke({"candidate_profile": parse_resume("hello"), "job_description": J})
    assert o["status"] == "needs_correction" and "match" not in o

def test_documents_without_llm():
    for k in ("resume", "cover_letter"):
        d = documents.generate(k, P, JOB)
        assert d["status"] == "pending_approval" and not d["used_llm"] and "Asha" in d["text"]
    assert "Outline" in documents.generate("answer", P, JOB, "Why us?")["text"]

def test_hallucinating_llm_is_rejected():
    orig = llm.chat; llm.chat = lambda s, u, t=0.2: "I am an expert in PyTorch and NLP with 5 years at Google."
    try:
        d = documents.generate("cover_letter", P, JOB)
        assert "Google" not in d["text"] or d["notes"]
        assert d["notes"] and not d["used_llm"] and "PyTorch" not in d["text"]
    finally: llm.chat = orig

def test_roadmap_order_and_rescore():
    m = score(P, JOB); ms = roadmap.build(m, P)
    assert ms[0]["skill"] == "Data Preprocessing" and ms[0]["kind"] == "required"
    P2 = {**P, "skills": P["skills"] + [{"name": "Data Preprocessing", "sources": ["roadmap"]}]}
    assert score(P2, JOB)["total"] > m["total"]

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"): f(); print("ok", n)
