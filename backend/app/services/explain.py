def explain(result: dict, job: dict) -> list[str]:
    """Template explanation. To use Mistral, call it here passing ONLY `result`
    (facts) and instruct it not to add any claims."""
    out = []
    if result["matched"]:
        out.append("Evidenced skills relevant to this role: " + ", ".join(result["matched"]) + ".")
    for x in result.get("partial", []):
        out.append(f"{x['skill']}: you have related experience ({x['via']}). Show {x['skill']} directly to get full credit.")
    for s in result["missing_required"]:
        out.append(f"Required skill not evidenced in your resume: {s}. (You may have it - if so, add proof.)")
    for s in result["missing_preferred"]:
        out.append(f"Preferred skill not evidenced: {s}. Learning it would raise your match.")
    for s in result["not_evidenced_in_projects"]:
        out.append(f"{s} is listed but not shown in any project; add a project bullet demonstrating it.")
    return out
