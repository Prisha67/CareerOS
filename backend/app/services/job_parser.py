import re
from .skills import find_skills

PREF = re.compile(r"preferred|nice to have|bonus|good to have", re.I)
REQ = re.compile(r"^\s*(requirements?|qualifications?|what we.re looking for|must have)\b", re.I)
RESP = re.compile(r"^\s*(responsibilities|what you.ll do|key duties)\b", re.I)

def parse_job(text: str) -> dict:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    req, pref, resp, mode = set(), set(), [], "req"
    for l in lines:
        header_like = len(l) < 70
        if PREF.search(l) and header_like: mode = "pref"
        elif REQ.match(l): mode = "req"
        elif RESP.match(l): mode = "resp"; continue
        elif mode == "resp": resp.append(l.lstrip("-•* "))
        target = pref if (mode == "pref" or PREF.search(l)) else req
        target.update(find_skills(l))
    pref -= req
    yrs = re.search(r"(\d+)\+?\s*(?:years|yrs)", text, re.I)
    comp = re.search(r"company\s*:\s*(.+)", text, re.I)
    return {"job_title": lines[0] if lines else "", "company": comp.group(1).strip() if comp else "",
            "required_skills": sorted(req), "preferred_skills": sorted(pref),
            "min_years": int(yrs.group(1)) if yrs else 0, "responsibilities": resp,
            "requires_degree": bool(re.search(r"b\.?tech|bachelor|degree|computer science", text, re.I))}
