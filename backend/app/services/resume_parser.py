import io, re
from .skills import find_skills

HEAD = re.compile(r"^\s*(skills|projects?|experience|work experience|internships?|education|certifications?)\s*:?\s*$", re.I)

def _canon(k: str) -> str:
    if k.startswith("project"): return "projects"
    if k in ("experience", "work experience") or k.startswith("intern"): return "experience"
    if k.startswith("certif"): return "certification"
    return k

def extract_text(filename: str, data: bytes) -> str:
    n = filename.lower()
    if n.endswith(".pdf"):
        from pypdf import PdfReader
        return "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages)
    if n.endswith(".docx"):
        import docx
        return "\n".join(p.text for p in docx.Document(io.BytesIO(data)).paragraphs)
    return data.decode("utf-8", errors="ignore")

def split_sections(text: str) -> dict[str, list[str]]:
    sec, cur = {}, "header"
    for line in text.splitlines():
        m = HEAD.match(line)
        if m:
            cur = _canon(m.group(1).lower()); sec.setdefault(cur, [])
        elif line.strip():
            sec.setdefault(cur, []).append(line.strip())
    return sec

DEGREE = re.compile(r"\b(b\.?\s?tech|b\.?e\.?|b\.?sc|bca|m\.?\s?tech|m\.?sc|mca|mba|bachelor[^,\n]*|master[^,\n]*)", re.I)
BRANCH = re.compile(r"computer science|information technology|electronics|electrical|mechanical|civil|data science|artificial intelligence", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")

def validate(p: dict) -> list[str]:
    w = []
    if not p["skills"]: w.append("No known skills detected. Add a Skills section.")
    if not p["projects"]: w.append("No projects found. Add a Projects section.")
    if not p["education"]: w.append("No education found.")
    if not p["email"]: w.append("No email found.")
    return w

def parse_resume(text: str) -> dict:
    sec = split_sections(text)
    skills: dict[str, set] = {}
    for name, lines in sec.items():
        for s in find_skills("\n".join(lines)):
            skills.setdefault(s, set()).add(name)  # source reference per skill
    projects = [{"text": l, "technologies": sorted(find_skills(l))} for l in sec.get("projects", [])]
    edu = " ".join(sec.get("education", []))
    head = sec.get("header", [])
    d, b, e = DEGREE.search(edu or text), BRANCH.search(edu or text), EMAIL.search(text)
    prof = {
        "name": head[0] if head and "@" not in head[0] and len(head[0]) < 50 else "",
        "email": e.group(0) if e else "",
        "degree": d.group(0).strip() if d else "", "branch": b.group(0).title() if b else "",
        "skills": [{"name": k, "sources": sorted(v)} for k, v in sorted(skills.items())],
        "projects": projects,
        "experience": sec.get("experience", []),
        "education": edu,
        "certifications": sec.get("certification", []),
    }
    prof["warnings"] = validate(prof)
    return prof
