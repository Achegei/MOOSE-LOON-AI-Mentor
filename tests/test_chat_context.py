"""Tests for curriculum context building."""

from backend import chat


def test_build_curriculum_context_formats_list_results(monkeypatch) -> None:
    """List-style retrieval results should become source-labelled context."""

    class FakeChromaService:
        def __init__(self, persist_directory: str):
            self.persist_directory = persist_directory

        def query(self, collection_name: str, query_text: str, k: int = 4):
            return [
                {
                    "text": "Prompt engineering uses role, task, context, and output format.",
                    "metadata": {"source": "knowledge/prompt_engineering.md"},
                }
            ]

    monkeypatch.setattr(chat, "ChromaService", FakeChromaService)

    context = chat.build_curriculum_context("prompt engineering")

    assert context is not None
    assert "knowledge/prompt_engineering.md" in context
    assert "Prompt engineering" in context


def test_build_curriculum_context_returns_none_on_retrieval_failure(monkeypatch) -> None:
    """Chat should degrade gracefully when retrieval fails."""

    class BrokenChromaService:
        def __init__(self, persist_directory: str):
            self.persist_directory = persist_directory

        def query(self, collection_name: str, query_text: str, k: int = 4):
            raise RuntimeError("collection missing")

    monkeypatch.setattr(chat, "ChromaService", BrokenChromaService)

    assert chat.build_curriculum_context("agents") is None
