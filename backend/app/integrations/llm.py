"""Mistral chat wrapper (stdlib). Returns None without a key / on failure. Records cost+latency metrics."""
import json, os, time, urllib.request

METRICS = {"calls": 0, "failures": 0, "total_ms": 0, "prompt_tokens": 0, "completion_tokens": 0}

def available() -> bool:
    return bool(os.getenv("MISTRAL_API_KEY"))

def chat(system: str, user: str, temperature: float = 0.2) -> str | None:
    key = os.getenv("MISTRAL_API_KEY")
    if not key: return None
    body = json.dumps({"model": os.getenv("MISTRAL_MODEL", "mistral-small-latest"), "temperature": temperature,
                       "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request("https://api.mistral.ai/v1/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    t0 = time.time(); METRICS["calls"] += 1
    try:
        with urllib.request.urlopen(req, timeout=30) as r: d = json.load(r)
        u = d.get("usage", {})
        METRICS["prompt_tokens"] += u.get("prompt_tokens", 0); METRICS["completion_tokens"] += u.get("completion_tokens", 0)
        return d["choices"][0]["message"]["content"].strip()
    except Exception:
        METRICS["failures"] += 1; return None
    finally: METRICS["total_ms"] += int((time.time() - t0) * 1000)
