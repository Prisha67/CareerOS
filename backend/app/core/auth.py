"""Optional Firebase ID-token auth. AUTH_REQUIRED=true enforces it; otherwise demo mode (user 'demo')."""
import os
from contextvars import ContextVar
from fastapi import HTTPException, Request

current_uid: ContextVar = ContextVar("uid", default=None)
OPEN = ("/health", "/docs", "/openapi.json")

def verify(token: str) -> str:
    import firebase_admin
    from firebase_admin import auth, credentials
    if not firebase_admin._apps:
        path = os.getenv("FIREBASE_CREDENTIALS")
        firebase_admin.initialize_app(credentials.Certificate(path) if path else None)
    return auth.verify_id_token(token)["uid"]

async def authenticate(request: Request):
    if os.getenv("AUTH_REQUIRED", "false").lower() != "true" or request.method == "OPTIONS" or request.url.path in OPEN: return
    h = request.headers.get("authorization", "")
    if not h.startswith("Bearer "): raise HTTPException(401, "Sign in required")
    try: current_uid.set(verify(h[7:]))
    except Exception: raise HTTPException(401, "Invalid or expired sign-in")

def uid_dep(user_id: str = "demo") -> str:
    return current_uid.get() or user_id
