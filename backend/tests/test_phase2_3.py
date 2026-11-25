from app.services.resume_parser import parse_resume
from app.services.job_parser import parse_job
from app.services.scoring_engine import score
import pathlib
S = pathlib.Path(__file__).resolve().parents[2] / "docs" / "samples"
R, J = (S / "resume.txt").read_text(), (S / "job.txt").read_text()

def test_resume_fields():
    p = parse_resume(R)
    assert p["name"] == "Asha Rao" and p["email"] == "asha@example.com"
    assert "tech" in p["degree"].lower() and p["branch"] == "Computer Science"
    assert {"Python", "SQL", "TensorFlow", "React", "FastAPI"} <= {s["name"] for s in p["skills"]}
    assert p["certifications"] and p["warnings"] == []

def test_validation_warnings():
    assert parse_resume("hello")["warnings"]

def test_job_fields():
    j = parse_job(J)
    assert j["company"] == "Example Technologies"
    assert set(j["required_skills"]) == {"Python", "Machine Learning", "SQL", "Data Preprocessing"}
    assert set(j["preferred_skills"]) == {"PyTorch", "NLP"}
    assert j["responsibilities"] == ["Develop ML models", "Process datasets"]

def test_related_credit_and_gap_report():
    m = score(parse_resume(R), parse_job(J))
    assert {"skill": "PyTorch", "via": "TensorFlow"} in m["partial"]   # semantic partial match
    st = {g["skill"]: g["status"] for g in m["gap_report"]}
    assert st["Python"] == "matched" and st["PyTorch"] == "related" and st["Data Preprocessing"] == "missing"
    assert 0 < m["total"] < 100

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"): f(); print("ok", n)
