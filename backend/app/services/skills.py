"""Skill taxonomy + deterministic normalization. Extend TAXONOMY freely."""
import re

TAXONOMY = {
    "Python": ["python"], "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning", "cnn", "neural network"],
    "TensorFlow": ["tensorflow"], "PyTorch": ["pytorch"],
    "NLP": ["nlp", "natural language processing", "transformer", "text classification"],
    "SQL": ["sql", "mysql", "postgresql"], "Data Preprocessing": ["data preprocessing", "data cleaning", "preprocessing"],
    "Java": ["java"], "C++": ["c++"], "JavaScript": ["javascript", "js"], "TypeScript": ["typescript"],
    "React": ["react", "next.js"], "FastAPI": ["fastapi"], "Docker": ["docker"], "Git": ["git", "github"],
    "Model Deployment": ["model deployment", "mlops", "deployed model"],
}
_PATTERNS = {
    c: re.compile(r"(?<![\w+#])(?:%s)(?![\w+#])" % "|".join(re.escape(a) for a in al), re.I)
    for c, al in TAXONOMY.items()
}

def find_skills(text: str) -> set[str]:
    return {c for c, p in _PATTERNS.items() if p.search(text or "")}

# Semantic-ish relatedness (partial credit). Replace/augment with embeddings (Pinecone) later.
RELATED = {
    "PyTorch": ["TensorFlow", "Deep Learning"], "TensorFlow": ["PyTorch", "Deep Learning"],
    "Deep Learning": ["PyTorch", "TensorFlow"], "NLP": ["Deep Learning"],
    "Machine Learning": ["Deep Learning", "TensorFlow", "PyTorch"],
    "Model Deployment": ["Docker", "FastAPI"], "JavaScript": ["TypeScript"],
    "TypeScript": ["JavaScript"], "React": ["JavaScript", "TypeScript"],
}

def normalize(name: str) -> str:
    f = find_skills(name)
    return next(iter(f)) if len(f) == 1 else name.strip()
