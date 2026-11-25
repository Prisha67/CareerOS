"""Run: python -m eval.evaluate  -> precision/recall/F1 of skill + requirement extraction vs hand annotations. Add cases to cases.json."""
import json, pathlib
from app.services.job_parser import parse_job
from app.services.resume_parser import parse_resume

def prf(pred, gold):
    pred, gold = set(pred), set(gold); tp = len(pred & gold)
    p, r = tp / len(pred) if pred else 0, tp / len(gold) if gold else 0
    return round(p, 2), round(r, 2), round(2 * p * r / (p + r), 2) if p + r else 0

def run():
    rows = []
    for c in json.loads((pathlib.Path(__file__).parent / "cases.json").read_text()):
        j = parse_job(c["job"])
        rows.append((c["name"], prf([s["name"] for s in parse_resume(c["resume"])["skills"]], c["resume_skills"]),
                     prf(j["required_skills"], c["required"]), prf(j["preferred_skills"], c["preferred"])))
    return rows

if __name__ == "__main__":
    print("case | resume skills P/R/F1 | job required P/R/F1 | job preferred P/R/F1")
    for r in run(): print(*r, sep=" | ")
