import json
from typing import TypedDict
from ..integrations import llm
from ..services.guard import grounded
from ..services.job_parser import parse_job
from ..services.scoring_engine import score
from ..services.explain import explain
from ..services import semantic
from .flow import END, compile_flow

class CareerState(TypedDict, total=False):
    candidate_profile: dict; job_description: str; profile_issues: list; status: str
    job_requirements: dict; match: dict; recommendations: list; llm_used: bool

def validate_node(s):  # Profile agent checkpoint
    issues = [] if s["candidate_profile"]["skills"] else ["No skills in profile. Add skills before analysing."]
    return {"profile_issues": issues, "status": "needs_correction" if issues else "ok"}

def job_node(s): return {"job_requirements": parse_job(s["job_description"])}   # Job agent
def match_node(s):
    m = score(s["candidate_profile"], s["job_requirements"])
    m["semantic_hints"] = semantic.hints([g["skill"] for g in m["gap_report"] if g["status"] != "matched"], s["candidate_profile"])
    return {"match": m}  # Matching agent (deterministic)

SYS = ("You are a career advisor. Using ONLY the facts given, write 3-6 short actionable recommendations, one per line. "
       "Never claim the candidate has a skill that is not listed as matched or related. No new numbers.")

def explain_node(s):
    base = explain(s["match"], s["job_requirements"])
    facts = json.dumps({"match": s["match"], "job": s["job_requirements"]})
    text = llm.chat(SYS, facts)
    if text:
        lines = [l.lstrip("-•*0123456789. ").strip() for l in text.splitlines() if l.strip()]
        have = {x["name"] for x in s["candidate_profile"]["skills"]}
        ok, _ = grounded(" ".join(lines), facts, have | set(s["job_requirements"]["required_skills"]) | set(s["job_requirements"]["preferred_skills"]))
        if ok and lines: return {"recommendations": lines, "llm_used": True}
    return {"recommendations": base, "llm_used": False}

def build_graph():
    return compile_flow({"validate": validate_node, "job": job_node, "match": match_node, "explain": explain_node},
                        "validate", {"validate": lambda s: END if s["status"] != "ok" else "job",
                                     "job": "match", "match": "explain", "explain": END}, CareerState)
