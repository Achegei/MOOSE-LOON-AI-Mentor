"""Tests for mentor chat performance modes."""

from backend.chat import CHAT_MODES, build_quick_fallback
from services.chat_cache import build_cache_key


def test_quick_mode_is_smaller_than_deep_mode() -> None:
    """Quick mode should use fewer chunks and fewer output tokens."""
    assert CHAT_MODES["quick"]["rag_k"] == 1
    assert CHAT_MODES["quick"]["max_tokens"] == 450
    assert CHAT_MODES["quick"]["timeout_seconds"] == 8
    assert CHAT_MODES["deep"]["rag_k"] == 5
    assert CHAT_MODES["deep"]["max_tokens"] == 1800
    assert CHAT_MODES["quick"]["max_tokens"] < CHAT_MODES["deep"]["max_tokens"]


def test_cache_key_changes_by_mode_and_context() -> None:
    """Cache identity should include mode and retrieved context."""
    quick_key, _ = build_cache_key("What is RAG?", "quick", "context-a")
    deep_key, _ = build_cache_key("What is RAG?", "deep", "context-a")
    context_key, _ = build_cache_key("What is RAG?", "quick", "context-b")

    assert quick_key != deep_key
    assert quick_key != context_key


def test_quick_fallback_uses_curriculum_context() -> None:
    """Timeout fallback should still give a useful curriculum-grounded answer."""
    reply = build_quick_fallback(
        "What is RAG?",
        "Source: knowledge/rag.md\nRAG retrieves relevant curriculum before generating an answer.",
    )

    assert "Quick answer" in reply
    assert "RAG retrieves relevant curriculum" in reply
