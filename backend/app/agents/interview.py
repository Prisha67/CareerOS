"""Interview Agent: question generation + rubric evaluation (deterministic; LLM adds an optional coach note)."""
import re
from ..integrations import llm

KEY = {"Python": ["list", "function", "library", "class", "script"], "SQL": ["join", "select", "index", "table", "query"],
       "Machine Learning": ["train", "test", "overfit", "model", "feature"], "Deep Learning": ["layer", "gradient", "neural", "convolution", "loss"],
       "NLP": ["token", "text", "embedding", "transformer", "corpus"], "PyTorch": ["tensor", "autograd", "module", "gpu"],
       "TensorFlow": ["tensor", "keras", "layer", "graph"], "Data Preprocessing": ["missing", "normalize", "clean", "outlier", "scale"]}
STAR = {"situation": ["situation", "when", "context"], "task": ["task", "goal", "needed to", "responsib"],
        "action": ["i built", "i decided", "i implemented", "i wrote", "action", "i "], "result": ["result", "outcome", "improved", "reduced", "learned", "achieved"]}

def questions(profile: dict, job: dict) -> list[dict]:
    qs = [{"category": "Technical", "text": f"Explain {s} and how you would apply it in this role.", "expect": KEY.get(s, [s.lower(), "example", "used"])}
          for s in (job["required_skills"] or [])[:3]]
    if profile["projects"]:
        p = profile["projects"][0]
        qs.append({"category": "Project", "text": f"Walk me through this project: {p['text']}", "expect": [t.lower() for t in p["technologies"]] + ["why", "result"]})
    qs.append({"category": "Behavioural", "text": "Describe a challenging situation in a project and how you handled it.", "expect": []})
    qs.append({"category": "HR", "text": f"Why do you want this {job['job_title']} role?", "expect": ["learn", "team", "role", "contribute"]})
    return [{"id": f"q{i}", **q} for i, q in enumerate(qs, 1)]

def evaluate(q: dict, answer: str) -> dict:
    a = answer.lower(); words = len(answer.split())
    sents = [x for x in re.split(r"[.!?]+", answer) if x.strip()]
    avg = words / max(len(sents), 1)
    clarity = 1.0 if 6 <= avg <= 30 else 0.6
    depth = min(words / 80, 1.0)
    hits = [k for k in q["expect"] if k in a]
    cov = len(hits) / len(q["expect"]) if q["expect"] else 0.0
    star_hit = {k: any(w in a for w in v) for k, v in STAR.items()}
    structure = sum(star_hit.values()) / 4
    if q["category"] == "Behavioural": total = 0.5 * structure + 0.25 * depth + 0.25 * clarity
    else: total = 0.45 * cov + 0.3 * depth + 0.25 * clarity
    strengths, improve = [], []
    if cov >= 0.6 or (q["category"] == "Behavioural" and structure >= 0.75): strengths.append("Covers the key ideas for this question.")
    if depth >= 0.75: strengths.append("Good level of detail.")
    if clarity == 1.0 and words >= 20: strengths.append("Clear sentence length and flow.")
    if q["category"] == "Behavioural":
        miss = [k for k, v in star_hit.items() if not v]
        if miss: improve.append("Use the STAR structure. Missing: " + ", ".join(miss) + ".")
    elif q["expect"] and cov < 0.6: improve.append("Consider mentioning: " + ", ".join(k for k in q["expect"] if k not in hits) + ".")
    if words < 40: improve.append("Add more detail and one concrete example.")
    if clarity < 1.0: improve.append("Use shorter, clearer sentences.")
    note = llm.chat("You are an interviewer. Give two sentences of feedback on this answer. Do not add facts about the candidate.", f"Q: {q['text']}\nA: {answer}")
    return {"score": round(total * 10, 1), "dimensions": {"coverage": round(cov * 100), "depth": round(depth * 100), "clarity": round(clarity * 100),
            "structure": round(structure * 100)}, "strengths": strengths, "improve": improve, "coach_note": note}
