from app.services.resume_parser import parse_resume
from app.graphs.analysis_graph import build_graph

RESUME = """Skills
Python, SQL, TensorFlow
Projects
Image Classification using CNN and TensorFlow in Python
Education
B.Tech Computer Science
"""
JD = """Machine Learning Intern
Requirements: Python, machine learning, SQL, data preprocessing
Preferred skills: PyTorch, NLP
"""

def test_end_to_end():
    out = build_graph().invoke({"candidate_profile": parse_resume(RESUME), "job_description": JD})
    m = out["match"]
    assert "Python" in m["matched"]
    assert any(x["skill"] == "Machine Learning" for x in m["partial"])  # related via TensorFlow/CNN
    assert {x["skill"] for x in m["partial"]} >= {"PyTorch", "NLP"}  # related via TensorFlow / Deep Learning
    assert 0 <= m["total"] <= 100

if __name__ == "__main__":
    test_end_to_end(); print("OK")
