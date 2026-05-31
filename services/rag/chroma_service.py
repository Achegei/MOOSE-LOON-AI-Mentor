"""Chroma DB wrapper service for curriculum-first RAG operations."""

import hashlib
import logging
from pathlib import Path
from typing import Dict, Iterable, List

logger = logging.getLogger(__name__)


try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except Exception:
    chromadb = None
    CHROMADB_AVAILABLE = False


class DeterministicEmbeddingFunction:
    """Local embedding function that avoids external model downloads."""

    dimensions = 32

    @staticmethod
    def name() -> str:
        """Return Chroma embedding function name."""
        return "moose_loon_hash_embedding"

    @staticmethod
    def default_space() -> str:
        """Return the default distance space."""
        return "cosine"

    @staticmethod
    def supported_spaces() -> List[str]:
        """Return supported distance spaces."""
        return ["cosine", "l2", "ip"]

    def get_config(self) -> Dict:
        """Return serializable embedding configuration."""
        return {"dimensions": self.dimensions}

    @staticmethod
    def validate_config(config: Dict) -> None:
        """Validate embedding configuration."""
        if "dimensions" in config and int(config["dimensions"]) <= 0:
            raise ValueError("dimensions must be positive")

    @staticmethod
    def validate_config_update(old_config: Dict, new_config: Dict) -> None:
        """Validate embedding configuration updates."""
        if old_config.get("dimensions") != new_config.get("dimensions"):
            raise ValueError("embedding dimensions cannot be changed")

    @staticmethod
    def build_from_config(config: Dict) -> "DeterministicEmbeddingFunction":
        """Build an embedding function from persisted config."""
        return DeterministicEmbeddingFunction()

    def __call__(self, input: Iterable[str]) -> List[List[float]]:
        """Embed documents using hashed term counts."""
        return [self._embed(text) for text in input]

    def embed_query(self, input: Iterable[str]) -> List[List[float]]:
        """Embed query text for Chroma."""
        return self(input)

    def _embed(self, text: str) -> List[float]:
        vector = [0.0] * self.dimensions
        tokens = [
            token.strip(".,?!:;()[]{}").lower()
            for token in text.split()
            if token.strip(".,?!:;()[]{}")
        ]
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            vector[digest[0] % self.dimensions] += 1.0
        total = sum(vector) or 1.0
        return [value / total for value in vector]


class ChromaService:
    """Small retrieval wrapper with a markdown fallback for local development."""

    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = persist_directory
        self.embedding_function = DeterministicEmbeddingFunction()
        if CHROMADB_AVAILABLE:
            if hasattr(chromadb, "PersistentClient"):
                self.client = chromadb.PersistentClient(path=persist_directory)
            else:
                self.client = chromadb.Client(
                    ChromaSettings(
                        chroma_db_impl="duckdb+parquet",
                        persist_directory=persist_directory,
                    )
                )
        else:
            self._store = []  # list of (id, text, metadata, embedding)

    def create_collection(self, name: str):
        if CHROMADB_AVAILABLE:
            return self._get_or_create_collection(name)
        return True

    def upsert_documents(self, collection_name: str, documents: List[Dict]):
        """Upsert documents: each doc should be {'id': str, 'text': str, 'metadata': {}}"""
        if CHROMADB_AVAILABLE:
            col = self._get_or_create_collection(collection_name)
            ids = [d["id"] for d in documents]
            metadatas = [d.get("metadata", {}) for d in documents]
            texts = [d["text"] for d in documents]
            if hasattr(col, "upsert"):
                col.upsert(ids=ids, metadatas=metadatas, documents=texts)
            else:
                col.add(ids=ids, metadatas=metadatas, documents=texts)
            if hasattr(self.client, "persist"):
                self.client.persist()
            return True
        # naive in-memory store
        for d in documents:
            self._store.append((d["id"], d["text"], d.get("metadata", {})))
        return True

    def query(self, collection_name: str, query_text: str, k: int = 4):
        if CHROMADB_AVAILABLE:
            try:
                col = self.client.get_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function,
                )
                return col.query(query_texts=[query_text], n_results=k)
            except Exception:
                logger.exception("Chroma query failed; using markdown fallback")
                return self._query_markdown_fallback(query_text, k)
        if not self._store:
            return self._query_markdown_fallback(query_text, k)
        # naive text-similarity by substring matching and length heuristic
        scores = []
        for id_, text, meta in self._store:
            score = 0
            if query_text.lower() in text.lower():
                score += 10
            score += max(0, 1.0 - abs(len(text) - len(query_text)) / max(1, len(query_text)))
            scores.append((score, id_, text, meta))
        scores.sort(reverse=True)
        return [{"id": s[1], "text": s[2], "metadata": s[3], "score": s[0]} for s in scores[:k]]

    def _query_markdown_fallback(self, query_text: str, k: int) -> List[Dict]:
        """Rank local knowledge markdown chunks when Chroma is unavailable."""
        query_terms = {
            term.strip(".,?!:;()[]{}").lower()
            for term in query_text.split()
            if len(term.strip(".,?!:;()[]{}")) > 2
        }
        base = Path("knowledge")
        scored: list[tuple[int, str, str, Dict]] = []

        for markdown_file in base.rglob("*.md"):
            text = markdown_file.read_text(encoding="utf-8")
            chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
            for index, chunk in enumerate(chunks):
                lower_chunk = chunk.lower()
                score = sum(1 for term in query_terms if term in lower_chunk)
                if score:
                    scored.append(
                        (
                            score,
                            f"{markdown_file.stem}-{index}",
                            chunk,
                            {"source": str(markdown_file)},
                        )
                    )

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            {"id": item_id, "text": text, "metadata": metadata, "score": score}
            for score, item_id, text, metadata in scored[:k]
        ]

    def _get_or_create_collection(self, name: str):
        """Get a collection, replacing incompatible local embedding config."""
        try:
            return self.client.get_or_create_collection(
                name=name,
                embedding_function=self.embedding_function,
            )
        except ValueError as exc:
            if "Embedding function conflict" not in str(exc):
                raise
            logger.warning("Replacing incompatible Chroma collection '%s'", name)
            self.client.delete_collection(name=name)
            return self.client.get_or_create_collection(
                name=name,
                embedding_function=self.embedding_function,
            )
