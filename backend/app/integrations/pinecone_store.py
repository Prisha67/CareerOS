"""Pinecone adapter (not wired by default; local cosine in semantic.py is used). Needs PINECONE_API_KEY, PINECONE_INDEX."""
import os

def _index():
    from pinecone import Pinecone
    return Pinecone(api_key=os.environ["PINECONE_API_KEY"]).Index(os.environ["PINECONE_INDEX"])

def upsert(user_id: str, items: list[tuple[str, list[float], dict]]):
    _index().upsert(vectors=[{"id": i, "values": v, "metadata": {**m, "user_id": user_id}} for i, v, m in items], namespace=user_id)

def query(user_id: str, vector: list[float], k: int = 5):
    return _index().query(vector=vector, top_k=k, namespace=user_id, include_metadata=True).matches
