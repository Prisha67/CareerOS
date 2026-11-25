"""Phase 1 smoke test: python scripts/check_phase1.py  (backend on :8000, frontend on :3000)"""
import json, sys, urllib.request, urllib.error, pathlib
B, F = "http://localhost:8000", "http://localhost:3000"
SAMPLES = pathlib.Path(__file__).resolve().parents[1] / "docs" / "samples"
fails = 0

def check(name, fn):
    global fails
    try: print("PASS", name, "-", fn() or "")
    except Exception as e: fails += 1; print("FAIL", name, "-", e)

def req(url, method="GET", data=None, headers=None):
    r = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    return urllib.request.urlopen(r, timeout=10)

def backend(): return req(B + "/health").status
def cors():
    h = req(B + "/resume/upload", "OPTIONS", headers={"Origin": F, "Access-Control-Request-Method": "POST"}).headers
    assert h.get("access-control-allow-origin") == F, "CORS header missing"
def upload():
    body, bd = (SAMPLES / "resume.txt").read_bytes(), "----x"
    data = (f'--{bd}\r\nContent-Disposition: form-data; name="file"; filename="resume.txt"\r\n\r\n').encode() + body + f"\r\n--{bd}--\r\n".encode()
    p = json.load(req(B + "/resume/upload", "POST", data, {"Content-Type": f"multipart/form-data; boundary={bd}"}))
    assert p["skills"], "no skills parsed"; return f'{len(p["skills"])} skills parsed'
def match():
    d = json.dumps({"job_description": (SAMPLES / "job.txt").read_text()}).encode()
    m = json.load(req(B + "/applications/match", "POST", d, {"Content-Type": "application/json"}))
    return f'score {m["match"]["total"]}'
def frontend():
    for path in ("/dashboard", "/dashboard/resume", "/dashboard/job-analysis"): assert req(F + path).status == 200, path

for n, f in [("backend running", backend), ("CORS for frontend", cors), ("resume upload", upload),
             ("job match", match), ("frontend pages load", frontend)]: check(n, f)
sys.exit(1 if fails else 0)
