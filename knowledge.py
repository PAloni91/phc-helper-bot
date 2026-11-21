"""Tiny keyword-based retrieval over the markdown files in ./knowledge.

Each paragraph (separated by a blank line) is one chunk. For a question we
score chunks by how many of the question's words they contain and return the
best few. This is deliberately simple: no extra services, easy to explain.
"""
import re
from pathlib import Path
from typing import List

STOPWORDS = {
    "the", "a", "an", "is", "are", "i", "my", "me", "to", "of", "and", "or",
    "in", "on", "for", "with", "what", "how", "do", "does", "can", "should",
    "it", "this", "that", "have", "has", "at", "be", "you", "your",
}


def tokenize(text: str) -> List[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def load_chunks(folder: str = "knowledge") -> List[str]:
    chunks: List[str] = []
    for path in sorted(Path(folder).glob("*.md")):
        for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8")):
            block = block.strip()
            if block and not block.startswith("<!--"):
                chunks.append(block)
    return chunks


def top_chunks(question: str, chunks: List[str], k: int = 3) -> List[str]:
    q_words = set(tokenize(question))
    if not q_words:
        return []
    scored = []
    for chunk in chunks:
        overlap = len(q_words & set(tokenize(chunk)))
        if overlap:
            scored.append((overlap, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:k]]
