"""Learning Agent: deterministic roadmap from the skill-gap report."""
HINTS = {"PyTorch": ("Build and train a small neural network", "Re-implement an existing project in PyTorch"),
         "NLP": ("Tokenise and classify a text dataset", "Build a small text-classification app"),
         "Machine Learning": ("Train and evaluate a model with cross-validation", "Publish an end-to-end ML project"),
         "SQL": ("Write joins, aggregates and subqueries", "Analyse a dataset using only SQL"),
         "Data Preprocessing": ("Clean and transform a messy dataset", "Document a preprocessing pipeline")}

def build(match: dict, profile: dict) -> list[dict]:
    have = {s["name"] for s in profile["skills"]}
    order = {("required", "missing"): 0, ("required", "related"): 1, ("preferred", "missing"): 2, ("preferred", "related"): 3}
    gaps = sorted((g for g in match["gap_report"] if g["status"] != "matched"), key=lambda g: order[(g["kind"], g["status"])])
    via = {x["skill"]: x["via"] for x in match.get("partial", [])}
    out = []
    for i, g in enumerate(gaps, 1):
        s = g["skill"]; ex, pr = HINTS.get(s, (f"Complete a tutorial and a small exercise in {s}", f"Add {s} to a portfolio project"))
        out.append({"id": f"m{i}", "priority": i, "skill": s, "kind": g["kind"], "objective": f"{s} fundamentals", "exercise": ex, "project": pr,
                    "prerequisites": [f"Builds on your {via[s]}"] if s in via else [], "resources": [f"Official {s} documentation"], "done": False})
    return out
