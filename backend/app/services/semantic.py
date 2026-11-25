"""Semantic evidence via Mistral embeddings + local cosine. Returns [] when no key. Informational only (never changes the score)."""
import json, math, os, urllib.request
_cache: dict[str, list[float]] = {}

def embed(texts: list[str]):
    key = os.getenv("MISTRAL_API_KEY")
    if not key: return None
    need = [t for t in dict.fromkeys(texts) if t not in _cache]
    if need:
        req = urllib.request.Request("https://api.mistral.ai/v1/embeddings", headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                                     data=json.dumps({"model": "mistral-embed", "input": need}).encode())
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                for t, d in zip(need, json.load(r)["data"]): _cache[t] = d["embedding"]
        except Exception: return None
    return [_cache[t] for t in texts]

def cosine(a, b):
    n = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / n if n else 0.0

def hints(skills: list[str], profile: dict, threshold: float = 0.7) -> list[dict]:
    texts = [p["text"] for p in profile["projects"]] + profile["experience"]
    if not skills or not texts: return []
    vs = embed(skills + texts)
    if not vs: return []
    sv, tv, out = vs[:len(skills)], vs[len(skills):], []
    for s, v in zip(skills, sv):
        sim, t = max((cosine(v, w), t) for w, t in zip(tv, texts))
        if sim >= threshold: out.append({"skill": s, "evidence": t, "similarity": round(sim, 2)})
    return out
