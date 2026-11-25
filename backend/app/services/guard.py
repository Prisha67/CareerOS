"""Evidence guard: generated text may not introduce skills or numbers absent from the user's facts."""
import re
from .skills import find_skills

NUM = re.compile(r"\d+(?:\.\d+)?%?")

def grounded(text: str, source_text: str, allowed_skills: set[str]) -> tuple[bool, list[str]]:
    bad = sorted(find_skills(text) - allowed_skills) + sorted(set(NUM.findall(text)) - set(NUM.findall(source_text)))
    return (not bad, bad)
