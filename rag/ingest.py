"""
Simple curriculum ingestion script.

Walks `knowledge/` for markdown files, splits by paragraphs, and upserts
into Chroma via `services.rag.chroma_service.ChromaService`.

Run as: `python -m rag.ingest` or `python rag/ingest.py` (ensuring project root on PYTHONPATH).
"""

import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.rag.chroma_service import ChromaService


def chunk_text(text: str, max_chars: int = 1000) -> List[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) + 2 <= max_chars:
            current = (current + "\n\n" + p).strip() if current else p
        else:
            if current:
                chunks.append(current)
            current = p
    if current:
        chunks.append(current)
    return chunks


def ingest(knowledge_dir: str = "knowledge", collection: str = "curriculum"):
    service = ChromaService()
    service.create_collection(collection)

    base = Path(knowledge_dir)
    docs = []
    for md in base.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        chunks = chunk_text(text)
        for i, c in enumerate(chunks):
            docs.append({"id": f"{md.stem}-{i}", "text": c, "metadata": {"source": str(md)}})

    if docs:
        service.upsert_documents(collection, docs)
        print(f"Ingested {len(docs)} document chunks into collection '{collection}'")
    else:
        print("No documents found to ingest.")


if __name__ == "__main__":
    ingest()
