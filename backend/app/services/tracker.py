STAGES = ["saved", "analysed", "ready", "applied", "assessment", "interview", "offer", "rejected", "withdrawn"]
_PAST_APPLIED = {"applied", "assessment", "interview", "offer", "rejected", "withdrawn"}

def analytics(db: dict, uid: str) -> dict:
    mine = lambda coll: [v for v in db[coll].values() if v.get("user_id", uid) == uid]
    apps, ans, ivs, rms = mine("applications"), sorted(mine("analyses"), key=lambda a: a.get("created_at", 0)), mine("interviews"), mine("roadmaps")
    reached = lambda st: sum(1 for a in apps if any(h["status"] == st for h in a["history"]))
    applied = sum(1 for a in apps if a["status"] in _PAST_APPLIED or reached("applied"))
    rate = lambda n, d: round(100 * n / d) if d else None
    gaps: dict[str, int] = {}
    for a in ans:
        for s in a["match"]["missing_required"] + a["match"]["missing_preferred"]: gaps[s] = gaps.get(s, 0) + 1
    scores = [x["score"] for i in ivs for x in i["answers"].values()]
    ms = [m for r in rms for m in r["milestones"]]
    return {"jobs_analysed": len(ans), "applications": len(apps), "applied": reached("applied"),
            "by_stage": {s: sum(1 for a in apps if a["status"] == s) for s in STAGES},
            "interview_rate": rate(reached("interview"), reached("applied")), "offer_rate": rate(reached("offer"), reached("applied")),
            "top_missing_skills": sorted(gaps.items(), key=lambda x: -x[1])[:5],
            "match_trend": [a["match"]["total"] for a in ans], "interview_avg": round(sum(scores) / len(scores), 1) if scores else None,
            "roadmap_progress": {"done": sum(m["done"] for m in ms), "total": len(ms)}}
