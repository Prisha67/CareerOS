"""JSON-file persistence so data survives restarts. Swap for Firestore later."""
import json, pathlib
FILE = pathlib.Path(__file__).resolve().parents[2] / "data" / "store.json"

def load() -> dict:
    try: db = json.loads(FILE.read_text())
    except Exception: db = {}
    for k in ("profiles", "analyses", "documents", "roadmaps", "interviews", "applications"): db.setdefault(k, {})
    return db

def save(db: dict) -> None:
    FILE.parent.mkdir(exist_ok=True); FILE.write_text(json.dumps(db, indent=1))
