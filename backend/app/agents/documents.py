"""Resume Agent: tailored resume, cover letter, application answers. Always drafts, never final."""
import json
from typing import TypedDict
from ..integrations import llm
from ..services.guard import grounded
from ..services.skills import RELATED, find_skills
from ..graphs.flow import END, compile_flow

class DocState(TypedDict, total=False):
    kind: str; profile: dict; job: dict; question: str; evidence: dict
    text: str; used_llm: bool; issues: list; notes: list

RULES = ("Use ONLY facts in the JSON. Do not invent skills, employers, certifications, achievements or numbers. "
         "Do not claim skills the candidate lacks. Keep it honest and concise.")

def select_node(s):
    p, j = s["profile"], s["job"]
    want = set(j["required_skills"]) | set(j["preferred_skills"])
    near = {r for w in want for r in RELATED.get(w, [])}
    rel = lambda pr: len(set(pr["technologies"]) & want) + 0.5 * len(set(pr["technologies"]) & near)
    projects = sorted(p["projects"], key=rel, reverse=True)[:3]
    skills = sorted([x["name"] for x in p["skills"]], key=lambda n: (n not in want, n))
    return {"evidence": {"projects": [x["text"] for x in projects], "skills": skills, "matched": [n for n in skills if n in want]}}

def _resume(s, rewrite):
    p, ev = s["profile"], s["evidence"]
    out = [p.get("name") or "Candidate", p.get("email", ""), "", "SKILLS", ", ".join(ev["skills"]), "", "PROJECTS"]
    out += [f"- {rewrite(b)}" for b in ev["projects"]]
    if p["experience"]: out += ["", "EXPERIENCE"] + [f"- {e}" for e in p["experience"]]
    out += ["", "EDUCATION", p["education"] or " ".join(x for x in (p.get("degree"), p.get("branch")) if x)]
    if p["certifications"]: out += ["", "CERTIFICATIONS"] + [f"- {c}" for c in p["certifications"]]
    return "\n".join(out)

def _rewrite_bullet(s):
    j = s["job"]
    def rw(b):
        t = llm.chat(f"Rewrite this resume bullet to emphasise relevance to a {j['job_title']} role. {RULES} Return one line only.", json.dumps({"bullet": b}))
        return t if t and grounded(t, b, find_skills(b))[0] else b
    return rw

def _cover_template(s):
    ev, j, p = s["evidence"], s["job"], s["profile"]
    at = f" at {j['company']}" if j.get("company") else ""
    lines = [f"Dear Hiring Manager,", "", f"I am applying for the {j['job_title']} position{at}."]
    if ev["matched"]: lines.append(f"My background includes {', '.join(ev['matched'])}.")
    if ev["projects"]: lines.append(f"One relevant project: {ev['projects'][0]}.")
    if p.get("degree") or p.get("branch"): lines.append(f"I am studying {' '.join(x for x in (p.get('degree'), p.get('branch')) if x)}.")
    return "\n".join(lines + ["", "I would welcome the chance to discuss how I can contribute.", "", "Sincerely,", p.get("name") or ""])

def _answer_template(s):
    ev = s["evidence"]
    pts = [f"- Relevant project: {ev['projects'][0]}"] if ev["projects"] else []
    if ev["matched"]: pts.append(f"- Relevant skills: {', '.join(ev['matched'])}")
    return f"Question: {s['question']}\n\nOutline (expand in your own words):\n" + "\n".join(pts or ["- Add a project or experience that fits this question."])

def draft_node(s):
    k = s["kind"]
    if k == "resume": return {"text": _resume(s, _rewrite_bullet(s)), "used_llm": llm.available() if hasattr(llm, "available") else False}
    facts = json.dumps({"candidate": {"name": s["profile"].get("name"), "skills": s["evidence"]["skills"], "projects": s["evidence"]["projects"],
                                      "education": s["profile"]["education"], "experience": s["profile"]["experience"]},
                        "job": {"title": s["job"]["job_title"], "company": s["job"].get("company")}, "question": s.get("question", "")})
    ask = "Write a cover letter (under 200 words)." if k == "cover_letter" else f"Draft an answer (under 150 words) to: {s['question']}"
    t = llm.chat(f"{ask} {RULES}", facts)
    if t: return {"text": t, "used_llm": True}
    return {"text": (_cover_template if k == "cover_letter" else _answer_template)(s), "used_llm": False}

def check_node(s):
    src = json.dumps(s["profile"]) + s.get("question", "")
    return {"issues": grounded(s["text"], src, {x["name"] for x in s["profile"]["skills"]})[1]}

def fallback_node(s):
    t = _resume(s, lambda b: b) if s["kind"] == "resume" else (_cover_template if s["kind"] == "cover_letter" else _answer_template)(s)
    return {"text": t, "used_llm": False, "notes": [f"AI draft rejected: it added unsupported claims ({', '.join(s['issues'])}). Showing a template instead."]}

_flow = compile_flow({"select": select_node, "draft": draft_node, "check": check_node, "fallback": fallback_node}, "select",
                     {"select": "draft", "draft": "check", "check": lambda s: "fallback" if s["issues"] else END, "fallback": END}, DocState)

def generate(kind: str, profile: dict, job: dict, question: str = "") -> dict:
    o = _flow.invoke({"kind": kind, "profile": profile, "job": job, "question": question, "notes": []})
    return {"type": kind, "title": {"resume": "Tailored resume", "cover_letter": "Cover letter", "answer": "Application answer"}[kind],
            "text": o["text"], "used_llm": o["used_llm"], "notes": o.get("notes", []), "status": "pending_approval"}
