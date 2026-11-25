"""Deterministic, explainable scoring. Weights are initial proposals, not validated.
Exact skill = full credit; related skill (RELATED map) = half credit."""
from .skills import RELATED

WEIGHTS = {"technical": 35, "projects": 25, "experience": 15, "education": 10, "preferred": 15}

def _credit(skill, pool):
    if skill in pool: return 1.0, None
    via = [r for r in RELATED.get(skill, []) if r in pool]
    return (0.5, via[0]) if via else (0.0, None)

def _avg(skills, pool):
    return 1.0 if not skills else sum(_credit(s, pool)[0] for s in skills) / len(skills)

def score(profile: dict, job: dict, weights: dict = WEIGHTS) -> dict:
    src = {s["name"]: s["sources"] for s in profile["skills"]}
    have = set(src)
    proj = {t for p in profile["projects"] for t in p["technologies"]}
    req, pref = job["required_skills"], job["preferred_skills"]
    exp = 1.0 if profile["experience"] else (0.5 if profile["projects"] else 0.0)
    if job.get("min_years", 0) >= 2 and not profile["experience"]: exp = min(exp, 0.25)
    if not job["requires_degree"] or profile.get("degree"): edu = 1.0
    else: edu = 0.5 if profile["education"] else 0.0
    dims = {"technical": _avg(req, have), "projects": _avg(req, proj), "experience": exp,
            "education": edu, "preferred": _avg(pref, have)}
    total = sum(dims[k] * weights[k] for k in weights) / sum(weights.values()) * 100

    gap, partial = [], []
    for kind, skills in (("required", req), ("preferred", pref)):
        for s in skills:
            c, via = _credit(s, have)
            if c == 1:
                ev = "Found in " + ", ".join(src[s]) + ("; shown in a project" if s in proj else "; not shown in any project")
                st = "matched"
            elif c:
                ev, st = f"Related skill {via} found; {s} itself is not evidenced", "related"
                partial.append({"skill": s, "via": via})
            else: ev, st = "Not found in your resume", "missing"
            gap.append({"skill": s, "kind": kind, "status": st, "evidence": ev})
    return {
        "total": round(total), "dimensions": {k: round(v * 100) for k, v in dims.items()}, "weights": weights,
        "matched": sorted(have & set(req + pref)),
        "partial": partial,
        "missing_required": sorted(s for s in req if _credit(s, have)[0] == 0),
        "missing_preferred": sorted(s for s in pref if _credit(s, have)[0] == 0),
        "not_evidenced_in_projects": sorted((have & set(req)) - proj),
        "gap_report": gap,
        "disclaimer": "Compatibility estimate, not a hiring probability.",
    }
