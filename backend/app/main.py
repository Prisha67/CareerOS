import os, time, uuid
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError: pass
from fastapi import Depends, FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, model_validator
from .core.auth import authenticate, current_uid, uid_dep
from .integrations import llm
from .agents import interview as iv
from .services.tracker import STAGES, analytics
from .services import storage
from .services.resume_parser import extract_text, parse_resume, validate
from .services.skills import find_skills, normalize
from .graphs.analysis_graph import build_graph
from .agents import documents, roadmap as road
from .services.scoring_engine import score

app = FastAPI(title="CareerOS", dependencies=[Depends(authenticate)])
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")], allow_methods=["*"], allow_headers=["*"])
graph = build_graph()
DB = storage.load()

class Owned(BaseModel):
    user_id: str = "demo"
    @model_validator(mode="after")
    def _own(self):
        if current_uid.get(): self.user_id = current_uid.get()
        return self

class MatchReq(Owned):
    user_id: str = "demo"
    job_description: str

class ProfileEdit(BaseModel):
    name: str = ""; email: str = ""; degree: str = ""; branch: str = ""; education: str = ""
    skills: list[str] = []; projects: list[str] = []; experience: list[str] = []; certifications: list[str] = []

@app.get("/health")
def health(): return {"status": "ok"}

@app.post("/resume/upload")
async def upload(user_id: str = Depends(uid_dep), file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > 5_000_000: raise HTTPException(413, "File too large (max 5 MB)")
    if not file.filename.lower().endswith((".pdf", ".docx", ".txt")): raise HTTPException(415, "Use a PDF, DOCX or TXT file")
    text = extract_text(file.filename, data)
    if not text.strip(): raise HTTPException(422, "Could not read any text from this file. Is it a scanned PDF?")
    DB["profiles"][user_id] = parse_resume(text); storage.save(DB)
    return DB["profiles"][user_id]

@app.get("/profile/me")
def profile(user_id: str = Depends(uid_dep)):
    if user_id not in DB["profiles"]: raise HTTPException(404, "Upload a resume first")
    return DB["profiles"][user_id]

@app.put("/profile/me")
def edit_profile(e: ProfileEdit, user_id: str = Depends(uid_dep)):
    old = {s["name"]: s["sources"] for s in DB["profiles"].get(user_id, {}).get("skills", [])}
    names = sorted({normalize(s) for s in e.skills if s.strip()})
    p = {**e.model_dump(exclude={"skills", "projects"}),
         "skills": [{"name": n, "sources": old.get(n, ["manual"])} for n in names],
         "projects": [{"text": t, "technologies": sorted(find_skills(t))} for t in e.projects if t.strip()]}
    p["warnings"] = validate(p)
    DB["profiles"][user_id] = p; storage.save(DB)
    return p

@app.post("/applications/match")
def match(r: MatchReq):
    if r.user_id not in DB["profiles"]: raise HTTPException(404, "Upload a resume first")
    if len(r.job_description.strip()) < 20: raise HTTPException(422, "Job description is too short")
    out = graph.invoke({"candidate_profile": DB["profiles"][r.user_id], "job_description": r.job_description})
    if out.get("status") == "needs_correction": raise HTTPException(409, " ".join(out["profile_issues"]))
    aid = uuid.uuid4().hex
    out.update(baseline_total=out["match"]["total"], user_id=r.user_id, created_at=time.time())
    DB["analyses"][aid] = out; storage.save(DB)
    return {"id": aid, **out}

@app.get("/analysis/{aid}")
def analysis(aid: str, user_id: str = Depends(uid_dep)):
    if aid not in DB["analyses"] or DB["analyses"][aid].get("user_id", user_id) != user_id: raise HTTPException(404, "Analysis not found")
    return DB["analyses"][aid]

@app.get("/analyses")
def analyses():
    return [{"id": k, "job_title": v["job_requirements"]["job_title"], "total": v["match"]["total"]} for k, v in DB["analyses"].items()]


# ---- Phase 5: drafts (human approval), roadmap, rescoring ----
def _ctx(user_id, aid):
    if user_id not in DB["profiles"]: raise HTTPException(404, "Upload a resume first")
    if DB["analyses"].get(aid, {}).get("user_id", user_id) != user_id or aid not in DB["analyses"]: raise HTTPException(404, "Analysis not found")
    return DB["profiles"][user_id], DB["analyses"][aid]["job_requirements"]

class DocReq(Owned):
    user_id: str = "demo"; analysis_id: str; question: str = ""

def _make(kind, r: DocReq):
    p, j = _ctx(r.user_id, r.analysis_id)
    d = {"id": uuid.uuid4().hex, "user_id": r.user_id, "analysis_id": r.analysis_id, **documents.generate(kind, p, j, r.question)}
    DB["documents"][d["id"]] = d; storage.save(DB); return d

@app.post("/resume/tailor")
def tailor(r: DocReq): return _make("resume", r)
@app.post("/documents/cover-letter")
def cover(r: DocReq): return _make("cover_letter", r)
@app.post("/documents/answer")
def answer(r: DocReq):
    if not r.question.strip(): raise HTTPException(422, "Enter the application question")
    return _make("answer", r)

class DocEdit(BaseModel):
    text: str | None = None; approved: bool | None = None

@app.patch("/documents/{did}")
def edit_doc(did: str, e: DocEdit):
    d = DB["documents"].get(did)
    if not d: raise HTTPException(404, "Document not found")
    if e.text is not None: d["text"] = e.text; d["status"] = "pending_approval"   # edits need re-approval
    if e.approved is not None: d["status"] = "approved" if e.approved else "pending_approval"
    storage.save(DB); return d

@app.get("/documents")
def docs(analysis_id: str = ""): return [d for d in DB["documents"].values() if not analysis_id or d["analysis_id"] == analysis_id]

@app.post("/roadmap/generate")
def gen_roadmap(r: DocReq):
    p, _ = _ctx(r.user_id, r.analysis_id)
    ms = road.build(DB["analyses"][r.analysis_id]["match"], p)
    rm = {"id": uuid.uuid4().hex, "user_id": r.user_id, "analysis_id": r.analysis_id, "milestones": ms}
    DB["roadmaps"][rm["id"]] = rm; storage.save(DB); return rm

@app.get("/roadmap")
def get_roadmap(analysis_id: str):
    return next((r for r in DB["roadmaps"].values() if r["analysis_id"] == analysis_id), None)

class Done(Owned):
    done: bool; user_id: str = "demo"

@app.patch("/roadmap/{rid}/milestones/{mid}")
def milestone(rid: str, mid: str, b: Done):
    rm = DB["roadmaps"].get(rid); m = next((x for x in (rm or {}).get("milestones", []) if x["id"] == mid), None)
    if not m: raise HTTPException(404, "Milestone not found")
    m["done"] = b.done
    skills = DB["profiles"][b.user_id]["skills"]
    if b.done and not any(s["name"] == m["skill"] for s in skills): skills.append({"name": m["skill"], "sources": ["roadmap"]})
    if not b.done: skills[:] = [s for s in skills if not (s["name"] == m["skill"] and s["sources"] == ["roadmap"])]
    storage.save(DB); return rm

@app.post("/analysis/{aid}/rescore")
def rescore(aid: str, user_id: str = Depends(uid_dep)):
    p, j = _ctx(user_id, aid); a = DB["analyses"][aid]
    a["match"] = score(p, j); storage.save(DB)
    return {"before": a.get("baseline_total"), "after": a["match"]["total"], "match": a["match"]}


# ---- Phase 6: interviews, applications, analytics ----
class IvStart(Owned): analysis_id: str
class IvAnswer(Owned): interview_id: str; question_id: str; answer: str

@app.post("/interviews/start")
def iv_start(r: IvStart):
    p, j = _ctx(r.user_id, r.analysis_id)
    i = {"id": uuid.uuid4().hex, "user_id": r.user_id, "analysis_id": r.analysis_id, "questions": iv.questions(p, j), "answers": {}, "created_at": time.time()}
    DB["interviews"][i["id"]] = i; storage.save(DB); return i

@app.post("/interviews/answer")
def iv_answer(r: IvAnswer):
    i = DB["interviews"].get(r.interview_id)
    if not i or i["user_id"] != r.user_id: raise HTTPException(404, "Interview not found")
    q = next((x for x in i["questions"] if x["id"] == r.question_id), None)
    if not q: raise HTTPException(404, "Question not found")
    if len(r.answer.strip()) < 5: raise HTTPException(422, "Write an answer first")
    i["answers"][q["id"]] = {"answer": r.answer, **iv.evaluate(q, r.answer)}; storage.save(DB)
    done = len(i["answers"]) == len(i["questions"]); sc = [a["score"] for a in i["answers"].values()]
    return {"evaluation": i["answers"][q["id"]], "complete": done, "average": round(sum(sc) / len(sc), 1)}

@app.get("/interviews")
def iv_list(user_id: str = Depends(uid_dep)): return [i for i in DB["interviews"].values() if i["user_id"] == user_id]

class AppIn(Owned): company: str; role: str; analysis_id: str = ""
class AppPatch(Owned): status: str

@app.post("/applications")
def app_add(a: AppIn):
    if not a.company.strip() or not a.role.strip(): raise HTTPException(422, "Company and role are required")
    st = "analysed" if a.analysis_id else "saved"
    rec = {"id": uuid.uuid4().hex, "user_id": a.user_id, "company": a.company, "role": a.role, "analysis_id": a.analysis_id, "status": st,
           "history": [{"status": st, "at": time.time()}]}
    DB["applications"][rec["id"]] = rec; storage.save(DB); return rec

@app.get("/applications")
def app_list(user_id: str = Depends(uid_dep)):
    return [{**a, "match": DB["analyses"].get(a["analysis_id"], {}).get("match", {}).get("total")} for a in DB["applications"].values() if a["user_id"] == user_id]

@app.patch("/applications/{aid}")
def app_patch(aid: str, b: AppPatch):
    a = DB["applications"].get(aid)
    if not a or a["user_id"] != b.user_id: raise HTTPException(404, "Application not found")
    if b.status not in STAGES: raise HTTPException(422, "Unknown status")
    a["status"] = b.status; a["history"].append({"status": b.status, "at": time.time()}); storage.save(DB); return a

@app.get("/analytics")
def get_analytics(user_id: str = Depends(uid_dep)): return analytics(DB, user_id)

# ---- Phase 7: privacy + monitoring ----
@app.delete("/profile/me")
def delete_my_data(user_id: str = Depends(uid_dep)):
    DB["profiles"].pop(user_id, None)
    for coll in ("analyses", "documents", "roadmaps", "interviews", "applications"):
        DB[coll] = {k: v for k, v in DB[coll].items() if v.get("user_id", user_id) != user_id}
    storage.save(DB); return {"deleted": True}

@app.get("/metrics")
def metrics(): return {**llm.METRICS, "avg_ms": llm.METRICS["total_ms"] // max(llm.METRICS["calls"], 1)}
